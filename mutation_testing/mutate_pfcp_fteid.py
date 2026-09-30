import argparse
import subprocess
import hashlib

import xml.etree.ElementTree as ET

from pathlib import Path

from scapy.all import Ether, IP, UDP, rdpcap, raw, wrpcap

from utils.json_utils import load_json



FIELD_NAME = "pfcp.f_teid.teid"


def find_field_offset(source, frame_number, expected):
    result = subprocess.run(
        [
            "tshark", "-r", str(source),
            "-Y", f"frame.number == {frame_number}",
            "-T", "pdml",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    pdml = ET.fromstring(result.stdout)
    matches = [
        field
        for field in pdml.iter("field")
        if field.get("name") == FIELD_NAME
        and field.get("value", "").lower() == expected.hex()
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Atteso un solo {FIELD_NAME} con valore "
            f"{expected.hex()} nel frame {frame_number}; trovati {len(matches)}"
        )

    field = matches[0]
    offset = int(field.get("pos"))
    size = int(field.get("size"))

    if size != 4:
        raise RuntimeError(f"Dimensione inattesa del TEID: {size}")

    return offset



def choose_mutation(source, evidence):
    events = [
        event for event in evidence["events"]
        if event["type"] == "pfcp_session_establishment_response"
    ]

    for index, first in enumerate(events):
        for second in events[index + 1:]:
            if first["ip_src"] != second["ip_src"]:
                continue

            second_values = {
                (item["teid"], item["ipv4"])
                for item in second["f_teids"]
            }

            for old_item in second["f_teids"]:
                old = int(old_item["teid"], 16)

                # Il campo da modificare deve comparire una sola volta nel frame.
                try:
                    find_field_offset(
                        source, second["frame"], old.to_bytes(4, "big")
                    )
                except RuntimeError:
                    continue

                for new_item in first["f_teids"]:
                    new_value = (new_item["teid"], new_item["ipv4"])
                    if new_item["ipv4"] != old_item["ipv4"]:
                        continue
                    if new_value in second_values:
                        continue

                    new = int(new_item["teid"], 16)
                    return second["frame"], old, new

    raise RuntimeError("Nessuna coppia di F-TEID adatta alla mutazione")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--frame", type=int)
    parser.add_argument("--old", type=lambda value: int(value, 0))
    parser.add_argument("--new", type=lambda value: int(value, 0))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()

    if not source.is_file():
        parser.error(f"Cattura non trovata: {source}")
    if source == output:
        parser.error("Sorgente e output devono essere file diversi")
    if output.exists() and not output.is_file():
        parser.error(f"Il percorso di output non è un file: {output}")
    if output.exists() and not args.overwrite:
        parser.error(f"Il file di output esiste già: {output}")
    if args.evidence is not None:
        if any(value is not None for value in (args.frame, args.old, args.new)):
            parser.error("--evidence non può essere usato con --frame, --old o --new")

        evidence_path = args.evidence.resolve()
        if not evidence_path.is_file():
            parser.error(f"Evidenza non trovata: {evidence_path}")

        evidence = load_json(evidence_path)
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if evidence["source"]["sha256"] != source_hash:
            parser.error("L'evidenza non corrisponde alla cattura sorgente")

        args.frame, args.old, args.new = choose_mutation(source, evidence)
    elif any(value is None for value in (args.frame, args.old, args.new)):
        parser.error("Indica --evidence oppure tutti e tre: --frame, --old, --new")
    if args.frame < 1:
        parser.error("--frame deve essere almeno 1")
    if not (0 <= args.old <= 0xFFFFFFFF):
        parser.error("--old deve essere un TEID a 32 bit")
    if not (0 <= args.new <= 0xFFFFFFFF):
        parser.error("--new deve essere un TEID a 32 bit")
    if args.old == args.new:
        parser.error("--old e --new devono essere diversi")

    old_bytes = args.old.to_bytes(4, "big")
    new_bytes = args.new.to_bytes(4, "big")

    packets = list(rdpcap(str(source)))
    if args.frame > len(packets):
        raise RuntimeError(
            f"Il frame {args.frame} non esiste: la cattura ha {len(packets)} frame"
        )

    offset = find_field_offset(source, args.frame, old_bytes)
    index = args.frame - 1
    original = packets[index]
    packet_bytes = bytearray(raw(original))

    if packet_bytes[offset:offset + 4] != old_bytes:
        raise RuntimeError("I byte del pacchetto non coincidono con il campo PDML")

    if not isinstance(original, Ether) or IP not in original or UDP not in original:
        raise RuntimeError("Il frame selezionato non è Ethernet/IPv4/UDP")

    packet_bytes[offset:offset + 4] = new_bytes
    modified = Ether(bytes(packet_bytes))
    modified.time = original.time

    # Il payload UDP è cambiato: Scapy deve ricalcolare il checksum.
    del modified[IP].chksum
    del modified[UDP].chksum

    packets[index] = modified
    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)

    print(f"PCAP creato: {output}")
    print(f"Frame: {args.frame}, posizione: {offset}")
    print(f"TEID: 0x{args.old:08x} -> 0x{args.new:08x}")


if __name__ == "__main__":
    main()    