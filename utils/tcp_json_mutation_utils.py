import re

from scapy.all import IP, TCP, rdpcap, raw, wrpcap


def replace_tcp_json_value(source, output, frame, field, old, new):
    old_bytes = old.encode("ascii")
    new_bytes = new.encode("ascii")

    if not old_bytes or len(old_bytes) != len(new_bytes):
        raise ValueError("I valori devono avere la stessa lunghezza non nulla")

    if source.resolve() == output.resolve():
        raise ValueError("Sorgente e output devono essere diversi")

    packets = list(rdpcap(str(source)))

    if not 1 <= frame <= len(packets):
        raise RuntimeError(f"Frame inesistente: {frame}")

    original = packets[frame - 1]
    if IP not in original or TCP not in original:
        raise RuntimeError("Il frame selezionato non contiene IPv4/TCP")

    payload = raw(original[TCP].payload)
    packet_bytes = bytearray(raw(original))
    payload_offset = len(packet_bytes) - len(payload)

    if not payload or packet_bytes[payload_offset:] != payload:
        raise RuntimeError("Payload TCP non valido")

    pattern = re.compile(
        rb'"' + re.escape(field.encode("ascii"))
        + rb'"\s*:\s*"' + re.escape(old_bytes) + rb'"'
    )
    matches = list(pattern.finditer(payload))

    if len(matches) != 1:
        raise RuntimeError(
            f"Atteso un solo {field}={old} nel frame {frame}; "
            f"trovati {len(matches)}"
        )

    value_offset = matches[0].end() - len(old_bytes) - 1
    offset = payload_offset + value_offset
    packet_bytes[offset:offset + len(old_bytes)] = new_bytes

    modified = type(original)(bytes(packet_bytes))
    modified.time = original.time
    del modified[IP].chksum
    del modified[TCP].chksum

    packets[frame - 1] = modified
    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)

    return offset