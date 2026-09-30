from decimal import Decimal

from scapy.all import rdpcap, wrpcap

from utils.evidence_utils import get_events_by_type
from utils.mutation_utils import load_mutation_context


TIMER_SECONDS = Decimal("15")
MARGIN_SECONDS = Decimal("5")


def apply_timing(packets, event):
    case = event["case"]

    if case == "A":
        start_frame = event["resynchronization_request"]["frame"]
        target_frame = event["ausf_authentication_response"]["frame"]
    elif case == "B":
        start_frame = event["synchronization_failure"]["frame"]
        target_frame = event["subsequent_authentication_request"]["frame"]
    else:
        raise RuntimeError(f"Caso AMF non supportato: {case}")

    if not (1 <= start_frame < target_frame <= len(packets)):
        raise RuntimeError("Frame temporali non validi nell'evidenza")

    start_time = Decimal(str(packets[start_frame - 1].time))
    target_time = Decimal(str(packets[target_frame - 1].time))
    original_interval = target_time - start_time

    if original_interval <= 0:
        raise RuntimeError("Intervallo temporale originale non valido")

    if case == "A":
        if original_interval >= TIMER_SECONDS:
            raise RuntimeError("Il caso A non rispetta già la soglia")

        new_interval = TIMER_SECONDS + MARGIN_SECONDS
        delay = new_interval - original_interval

        for packet in packets[start_frame:]:
            packet.time = Decimal(str(packet.time)) + delay

    else:
        if original_interval <= TIMER_SECONDS:
            raise RuntimeError("Il caso B non rispetta già la soglia")

        new_interval = TIMER_SECONDS - MARGIN_SECONDS
        factor = new_interval / original_interval

        for packet in packets[start_frame:target_frame]:
            old_time = Decimal(str(packet.time))
            packet.time = start_time + (old_time - start_time) * factor

        shift = new_interval - original_interval
        for packet in packets[target_frame:]:
            packet.time = Decimal(str(packet.time)) + shift

    return case, start_frame, target_frame, original_interval, new_interval


def main():
    source, evidence, output = load_mutation_context()

    event = get_events_by_type(
        evidence, "amf_sync_failure", require_single=True
    )
    packets = list(rdpcap(str(source)))

    case, start_frame, target_frame, before, after = apply_timing(
        packets, event
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)

    print(f"PCAP creato: {output}")
    print(f"Caso {case}: frame {start_frame} → {target_frame}")
    print(f"Intervallo: {before:.3f} s → {after:.3f} s")


if __name__ == "__main__":
    main()