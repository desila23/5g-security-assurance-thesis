from decimal import Decimal

from scapy.all import rdpcap, wrpcap

from utils.mutation_utils import load_sequence_mutation_context


TIMER_SECONDS = Decimal("15")
MARGIN_SECONDS = Decimal("5")


def apply_timing(
    packets,
    case,
    start_frame,
    target_frame,
):
    if case not in {"A", "B"}:
        raise RuntimeError(
            f"Caso AMF non supportato: {case}"
        )

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
    source, report, output = (
        load_sequence_mutation_context()
    )

    case = report.get("configuration", {}).get("case")

    if case not in {"A", "B"}:
        raise RuntimeError(
            "Caso AMF non presente o non valido nel report"
        )

    bindings = report.get("evidence", {}).get("bindings", {})

    if case == "A":
        start_event = bindings.get("resync")
        target_event = bindings.get("new_vector")

        if start_event is None or target_event is None:
            raise RuntimeError(
                "Bindings resync/new_vector non trovati nel report AMF Case A"
            )

    else:
        start_event = bindings.get("sync_failure")
        target_event = bindings.get("subsequent_auth_request")

        if start_event is None or target_event is None:
            raise RuntimeError(
                "Bindings temporali del Case B non trovati nel report"
            )

    start_frame = start_event["frame"]
    target_frame = target_event["frame"]

    packets = list(
        rdpcap(str(source))
    )

    case, start_frame, target_frame, before, after = (
        apply_timing(packets, case, start_frame, target_frame)
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    wrpcap(
        str(output),
        packets,
    )

    print(f"PCAP creato: {output}")
    print(
        f"Caso {case}: "
        f"frame {start_frame} → {target_frame}"
    )
    print(
        f"Intervallo: "
        f"{before:.3f} s → {after:.3f} s"
    )


if __name__ == "__main__":
    main()