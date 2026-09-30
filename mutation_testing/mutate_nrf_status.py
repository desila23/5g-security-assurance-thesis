from scapy.all import IP, TCP, Raw, rdpcap, raw, wrpcap

from utils.evidence_utils import get_events_by_type
from utils.mutation_utils import load_mutation_context


OLD_STATUS = b"\x88"               # :status 200 nella tabella HPACK
NEW_STATUS = b"\x08\x03" + b"403"  # :status 403, valore letterale


def endpoints(packet):
    return (
        packet[IP].src,
        packet[TCP].sport,
        packet[IP].dst,
        packet[TCP].dport,
    )


def main():
    source, evidence, output = load_mutation_context()
    event = get_events_by_type(
        evidence, 
        "nrf_nf_discovery", 
        require_single=True
    )

    if event["response"]["status_code"] != 200:
        raise RuntimeError("La risposta originale non ha status 200")

    frame = event["response"]["frame"]
    packets = list(rdpcap(str(source)))

    if not 1 <= frame <= len(packets):
        raise RuntimeError(f"Frame inesistente: {frame}")

    response = packets[frame - 1]
    if IP not in response or TCP not in response:
        raise RuntimeError("La risposta non contiene IPv4/TCP")

    payload = raw(response[TCP].payload)
    if len(payload) < 13:
        raise RuntimeError("Frame HTTP/2 troppo corto")

    header_length = int.from_bytes(payload[:3], "big")
    stream_id = int.from_bytes(payload[5:9], "big") & 0x7FFFFFFF

    if payload[3] != 1 or payload[4] != 4:
        raise RuntimeError("Atteso un frame HTTP/2 HEADERS con END_HEADERS")
    if len(payload) != 9 + header_length:
        raise RuntimeError("Lunghezza del frame HTTP/2 inattesa")
    if stream_id != int(event["request"]["http2_stream_id"]):
        raise RuntimeError("Stream HTTP/2 diverso dall'evidenza")

    # Nella cattura: aggiornamento della tabella HPACK, poi :status 200.
    if payload[9:12] != b"\x3f\xe1\x1f" or payload[12:13] != OLD_STATUS:
        raise RuntimeError("Codifica HPACK inattesa: PCAP non compatibile")

    delta = len(NEW_STATUS) - len(OLD_STATUS)
    new_payload = (
        (header_length + delta).to_bytes(3, "big")
        + payload[3:12]
        + NEW_STATUS
        + payload[13:]
    )

    server = endpoints(response)
    client = (server[2], server[3], server[0], server[1])
    end_sequence = response[TCP].seq + len(payload)

    if end_sequence >= 2**32:
        raise RuntimeError("Questo flusso richiede la gestione del wrap TCP")


    original_bytes = raw(response)
    payload_offset = len(original_bytes) - len(payload)

    if original_bytes[payload_offset:] != payload:
        raise RuntimeError("Il payload TCP non coincide con il pacchetto")

    modified = type(response)(
        original_bytes[:payload_offset] + new_payload
    )
    modified[TCP].remove_payload()
    modified[TCP].add_payload(Raw(new_payload))
   
    modified.time = response.time
    modified[IP].len = response[IP].len + delta
    del modified[IP].chksum
    del modified[TCP].chksum

    if len(raw(modified)) != len(original_bytes) + delta:
        raise RuntimeError("Lunghezza del pacchetto modificato inattesa")

    packets[frame - 1] = modified


    adjusted_frames = []

    for number in range(frame + 1, len(packets) + 1):
        packet = packets[number - 1]
        if IP not in packet or TCP not in packet:
            continue

        flow = endpoints(packet)
        changed = False

        if flow == server and packet[TCP].seq >= end_sequence:
            packet[TCP].seq += delta
            changed = True

        if flow == client and packet[TCP].ack >= end_sequence:
            packet[TCP].ack += delta
            changed = True

        if changed:
            del packet[TCP].chksum
            adjusted_frames.append(number)

    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)

    print(f"PCAP creato: {output}")
    print(f"Frame {frame}: HTTP 200 -> 403")
    print(f"Frame TCP successivi aggiornati: {adjusted_frames}")


if __name__ == "__main__":
    main()