import subprocess
import xml.etree.ElementTree as ET

from scapy.all import IP, TCP, rdpcap, raw, wrpcap


def check_http2_body(source, frame, offset, length, port):
    result = subprocess.run(
        [
            "tshark",
            "-d", f"tcp.port=={port},http2",
            "-r", str(source),
            "-Y", f"frame.number == {frame}",
            "-T", "pdml",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    pdml = ET.fromstring(result.stdout)

    for field in pdml.iter("field"):
        if field.get("name") != "http2.data.data":
            continue

        pos = field.get("pos")
        size = field.get("size")
        if pos is None or size is None:
            continue

        start = int(pos)
        end = start + int(size)

        if start <= offset and offset + length <= end:
            return

    raise RuntimeError("Il valore non si trova nel body HTTP/2")


def replace_http2_body_value(source, output, body_frames, old_bytes, new_bytes, port):
    if not old_bytes or len(old_bytes) != len(new_bytes):
        raise ValueError("I valori devono avere la stessa lunghezza non nulla")

    if source.resolve() == output.resolve():
        raise ValueError("Sorgente e output devono essere diversi")

    packets = list(rdpcap(str(source)))
    matches = []

    for frame in body_frames:
        if frame < 1 or frame > len(packets):
            raise RuntimeError(f"Frame inesistente: {frame}")

        packet_bytes = raw(packets[frame - 1])
        count = packet_bytes.count(old_bytes)

        if count > 1:
            raise RuntimeError(
                f"Valore presente più volte nel frame {frame}"
            )
        if count == 1:
            matches.append((frame, packet_bytes.find(old_bytes)))

    if len(matches) != 1:
        raise RuntimeError(
            f"Atteso un solo frame contenente il valore; trovati {len(matches)}"
        )

    frame, offset = matches[0]
    check_http2_body(source, frame, offset, len(old_bytes), port)

    original = packets[frame - 1]
    if IP not in original or TCP not in original:
        raise RuntimeError("Il frame selezionato non è Ethernet/IPv4/TCP")

    packet_bytes = bytearray(raw(original))
    packet_bytes[offset:offset + len(old_bytes)] = new_bytes

    modified = type(original)(bytes(packet_bytes))
    modified.time = original.time

    del modified[IP].chksum
    del modified[TCP].chksum

    packets[frame - 1] = modified

    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)

    return frame, offset