from datetime import datetime, timezone
from pathlib import Path

from utils.tshark_utils import calculate_sha256, get_tshark_version, run_tshark
from utils.json_utils import save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent


PFCP_SESSION_ESTABLISHMENT_RESPONSE = 51



def parse_multi_value_field(value):
    if not value:
        return []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def deduplicate_f_teids(teids, ipv4_addresses):
    if len(teids) != len(ipv4_addresses):
        raise RuntimeError(
            "Mismatch between extracted F-TEIDs and IPv4 addresses: "
            f"{len(teids)} TEIDs, "
            f"{len(ipv4_addresses)} IPv4 addresses"
        )        

    result = []
    seen = set()

    for teid, ipv4 in zip(teids, ipv4_addresses):
        key = (teid, ipv4)

        if key in seen:
            continue

        seen.add(key)

        result.append({
            "teid": teid,
            "ipv4": ipv4
        })

    return result



def extract_session_establishment_responses(pcap_file):
    fields = [
        "frame.number",
        "frame.time_relative",
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "pfcp.msg_type",
        "pfcp.f_teid.teid",
        "pfcp.f_teid.ipv4_addr"
    ]

    rows = run_tshark(
        pcap_file,
        f"pfcp.msg_type == {PFCP_SESSION_ESTABLISHMENT_RESPONSE}",
        fields
    )

    if not rows:
        raise RuntimeError(
            "No PFCP Session Establishment Response found in PCAP"
        )

    return rows



def build_event(row):
    message_type_raw = row["pfcp.msg_type"]

    if not message_type_raw:
        raise RuntimeError(
            f"PFCP message type missing in frame {row['frame.number']}"
        )

    message_type = int(message_type_raw)

    if message_type != PFCP_SESSION_ESTABLISHMENT_RESPONSE:
        raise RuntimeError(
            f"Unexpected PFCP message type in frame "
            f"{row['frame.number']}: {message_type}"
        )


    teids = parse_multi_value_field(
        row["pfcp.f_teid.teid"]
    )

    ipv4_addresses = parse_multi_value_field(
        row["pfcp.f_teid.ipv4_addr"]
    )


    if not teids:
        raise RuntimeError(
            f"No F-TEID found in PFCP Session Establishment "
            f"Response frame {row['frame.number']}"
        )


    f_teids = deduplicate_f_teids(
        teids,
        ipv4_addresses
    )


    return {
        "type": "pfcp_session_establishment_response",

        "frame": int(
            row["frame.number"]
        ),

        "timestamp_relative": float(
            row["frame.time_relative"]
        ),

        "timestamp_epoch": float(
            row["frame.time_epoch"]
        ),

        "ip_src": row["ip.src"],

        "ip_dst": row["ip.dst"],

        "message_type": message_type,

        "f_teids": f_teids
    }




def build_evidence(pcap_file):
    rows = extract_session_establishment_responses(pcap_file)

    events = [
        build_event(row)
        for row in rows
    ]


    return {
        "schema_version": "1.0",

        "metadata": {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "tshark_version": get_tshark_version()
        },

        "source": {
            "pcap_file": str(
                pcap_file.relative_to(BASE_DIR)
            ),

            "sha256": calculate_sha256(
                pcap_file
            )
        },

        "events": events
    }



def main():
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract UPF TEID uniqueness evidence"
    )

    evidence = build_evidence(context["pcap_file"])


    output_file = context["output_file"]

    save_json(output_file, evidence)

    print(f"Evidence saved to: {output_file}")



if __name__ == "__main__":
    main()