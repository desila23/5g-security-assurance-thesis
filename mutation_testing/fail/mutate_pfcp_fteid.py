import subprocess
import xml.etree.ElementTree as ET

from pathlib import Path

from scapy.all import Ether, IP, UDP, rdpcap, raw, wrpcap

from utils.mutation_utils import load_sequence_mutation_context



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



def choose_mutation(source, report):
    events = (
    report
        .get("evidence", {})
        .get("bindings", {})
        .get("responses", [])
    )

    if not events:
        raise RuntimeError(
            "Nessuna PFCP Session Establishment Response "
            "trovata nel report"
    )


    for index, first in enumerate(events):
        for second in events[index + 1:]:

            if first["src"] != second["src"]:
                continue

            first_f_teids = first["fields"]["f_teids"]
            second_f_teids = second["fields"]["f_teids"]

            second_values = {
                (item["teid"], item["ipv4"])
                for item in second_f_teids
            }

            for old_item in second_f_teids:
                old = int(
                    old_item["teid"],
                    16
                )

                try:
                    find_field_offset(
                        source,
                        second["frame"],
                        old.to_bytes(4, "big")
                    )

                except RuntimeError:
                    continue

                for new_item in first_f_teids:
                    new_value = (
                        new_item["teid"],
                        new_item["ipv4"]
                    )

                    if (
                        new_item["ipv4"]
                        != old_item["ipv4"]
                    ):
                        continue

                    if new_value in second_values:
                        continue

                    new = int(
                        new_item["teid"],
                        16
                    )

                    return (
                        second["frame"],
                        old,
                        new
                    )

    raise RuntimeError(
        "Nessuna coppia di F-TEID adatta alla mutazione"
    )



def main():
    source, report, output = (
        load_sequence_mutation_context()
    )

    frame, old, new = choose_mutation(
        source,
        report
    )

    old_bytes = old.to_bytes(
        4,
        "big"
    )

    new_bytes = new.to_bytes(
        4,
        "big"
    )

    packets = list(
        rdpcap(str(source))
    )

    if frame > len(packets):
        raise RuntimeError(
            f"Il frame {frame} non esiste: "
            f"la cattura ha {len(packets)} frame"
        )

    offset = find_field_offset(
        source,
        frame,
        old_bytes
    )

    index = frame - 1
    original = packets[index]

    packet_bytes = bytearray(
        raw(original)
    )

    if (
        packet_bytes[
            offset:offset + 4
        ]
        != old_bytes
    ):
        raise RuntimeError(
            "I byte del pacchetto non coincidono "
            "con il campo PDML"
        )

    if (
        not isinstance(original, Ether)
        or IP not in original
        or UDP not in original
    ):
        raise RuntimeError(
            "Il frame selezionato non è "
            "Ethernet/IPv4/UDP"
        )

    packet_bytes[
        offset:offset + 4
    ] = new_bytes

    modified = Ether(
        bytes(packet_bytes)
    )

    modified.time = original.time

    del modified[IP].chksum
    del modified[UDP].chksum

    packets[index] = modified

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    wrpcap(
        str(output),
        packets
    )

    print(
        f"PCAP creato: {output}"
    )

    print(
        f"Frame: {frame}, "
        f"posizione: {offset}"
    )

    print(
        f"TEID: "
        f"0x{old:08x} -> "
        f"0x{new:08x}"
    )


if __name__ == "__main__":
    main()    