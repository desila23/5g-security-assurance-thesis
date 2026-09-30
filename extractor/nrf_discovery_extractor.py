import json

from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from pathlib import Path


from utils.tshark_utils import run_tshark, get_tshark_version, calculate_sha256
from utils.http2_utils import decode_json_body
from utils.json_utils import save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent


def find_discovery_request(pcap_file):
    request_rows = run_tshark(  
        pcap_file,
        'http2.headers.path contains "nnrf-disc"',
        [
            "frame.number",
            "frame.time_relative",
            "frame.time_epoch",
            "tcp.stream",
            "http2.streamid",
            "http2.headers.method",
            "http2.headers.path"
        ],
        decode_as="tcp.port==7777,http2"
    )

    if not request_rows:
        raise RuntimeError(
            "NF Discovery request not found in PCAP"
        )


    matching_request = []

    for row in request_rows:
        request_path = row["http2.headers.path"]

        parsed_url = urlparse(request_path)
        query_params = parse_qs(parsed_url.query)

        requester_nf_type = query_params.get(
            "requester-nf-type",
            [None]
        )[0]

        target_nf_type = query_params.get(
            "target-nf-type",
            [None]
        )[0]

        requester_snssais_raw = query_params.get(
            "requester-snssais",
            [None]
        )[0]

        requester_snssais = []

        if requester_snssais_raw:
            try:
                requester_snssais = json.loads(
                    requester_snssais_raw
                )
            except json.JSONDecodeError:
                continue

        if (
            requester_nf_type == "AMF"
            and target_nf_type == "SMF"
            and requester_snssais
            and requester_snssais[0].get("sst") == 128
            and requester_snssais[0].get("sd") == "AAAAAA"
        ):
            matching_request.append(row)

    if not matching_request:
        raise RuntimeError(
            "Expected NF Discovery request for this test not found"
        )

    if len(matching_request) > 1:
        raise RuntimeError(
            "Multiple matching NF Discovery request found: "
            f"{len(matching_request)}"
        )

    return matching_request[0]



def parse_request_data(request_row):
    request_method = request_row["http2.headers.method"]
    request_path = request_row["http2.headers.path"]

    if not request_path:
        raise RuntimeError(
            "Request path not found in NF Discovery request"
        )


    parsed_url = urlparse(request_path)
    query_params = parse_qs(parsed_url.query)


    # TIPI
    requester_nf_type = query_params.get(
        "requester-nf-type", 
        [None]
    )[0]

    target_nf_type = query_params.get(
        "target-nf-type", 
        [None]
    )[0]


    # ID
    requester_nf_instance_id = query_params.get(
        "requester-nf-instance-id", 
        [None]
    )[0]

    target_nf_instance_id = query_params.get(
        "target-nf-instance-id", 
        [None]
    )[0]


    # SNSSAIs
    requester_snssais_raw = query_params.get(
        "requester-snssais",
        [None]
    )[0]


    if requester_snssais_raw:
        try:
            requester_snssais = json.loads(requester_snssais_raw)

        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Error parsing requester-snssais parameter: {e}"
            )
    else:
        requester_snssais = []



    tcp_stream = request_row["tcp.stream"]
    http2_stream_raw = request_row["http2.streamid"]

    # In alcuni casi TShark potrebbe restituire più valori.
    http2_stream = http2_stream_raw.split(",")[0] 


    return {
        "method": request_method,
        "path": parsed_url.path,
        "requester_nf_type": requester_nf_type,
        "requester_nf_instance_id": requester_nf_instance_id,
        "target_nf_type": target_nf_type,
        "target_nf_instance_id": target_nf_instance_id,
        "requester_snssais": requester_snssais,
        "tcp_stream": tcp_stream,
        "http2_stream": http2_stream
    }



def find_discovery_response(pcap_file, tcp_stream, http2_stream):
    response_filter = (
        f'tcp.stream == {tcp_stream} && '
        f'http2.streamid == {http2_stream} && '
        f'http2.headers.status'
    )


    response_rows = run_tshark(
        pcap_file,
        response_filter,
        [
            "frame.number",
            "frame.time_relative",
            "frame.time_epoch",
            "http2.headers.status"        
        ],
        decode_as="tcp.port==7777,http2"
    )

    if not response_rows:
        raise RuntimeError(
            "NF Discovery response not found in PCAP"
        )


    if len(response_rows) > 1:
        raise RuntimeError(
            "Multiple NF Discovery responses found: "
            f"{len(response_rows)}"
        )

    response_row = response_rows[0]

    status_raw = response_row["http2.headers.status"]

    if not status_raw:
        raise RuntimeError(
            "Status code not found in NF Discovery response"
        )

    return response_row, int(status_raw)



def find_discovery_body(pcap_file, tcp_stream, http2_stream):
    body_filter = (
        f'tcp.stream == {tcp_stream} && '
        f'http2.streamid == {http2_stream} && '
        f'http2.data.data'
    )


    body_rows = run_tshark(
        pcap_file,
        body_filter,
        [
            "frame.number",
            "frame.time_relative",
            "frame.time_epoch",
            "http2.data.data"
        ],
        decode_as="tcp.port==7777,http2"
    ) 

    if not body_rows:
        raise RuntimeError(
            "NF Discovery response body not found in PCAP"
        )


    body_json = decode_json_body(body_rows)

    body_frames = [
        int(row["frame.number"])
        for row in body_rows
    ]

    body_frame = body_frames[0]

    body_timestamp = float(body_rows[0]["frame.time_relative"])

    body_timestamp_epoch = float(body_rows[0]["frame.time_epoch"])


    return{
        "frame": body_frame,
        "frames": body_frames,
        "timestamp": body_timestamp,
        "timestamp_epoch": body_timestamp_epoch,
        "json": body_json
    }


def build_nrf_discovery_event(pcap_file):
    request_row = find_discovery_request(pcap_file)

    request_data = parse_request_data(request_row)

    tcp_stream = request_data["tcp_stream"]
    http2_stream = request_data["http2_stream"]

    response_row, status_code = find_discovery_response(
        pcap_file,
        tcp_stream, 
        http2_stream
    )

    body = find_discovery_body(pcap_file, tcp_stream, http2_stream)


    event = {
       "type": "nrf_nf_discovery",

       "request": {
           "frame": int(
                request_row["frame.number"]
            ),

            "timestamp": float(
                request_row["frame.time_relative"]
            ),

            "timestamp_epoch": float(
                request_row["frame.time_epoch"]
            ),

            "tcp_stream": int(
                tcp_stream
            ),

            "http2_stream_id": int(
                http2_stream
            ),

            "method": request_data["method"],

            "path": request_data["path"],

            "requester_nf_type":
                request_data["requester_nf_type"],

            "requester_nf_instance_id":
                request_data["requester_nf_instance_id"],

            "target_nf_type":
                request_data["target_nf_type"],

            "target_nf_instance_id":
                request_data["target_nf_instance_id"],

            "requester_snssais":
                request_data["requester_snssais"]
        },

        "response": {
            "frame": int(
                response_row["frame.number"]
            ),

            "timestamp": float(
                response_row["frame.time_relative"]
            ),

            "timestamp_epoch": float(
                response_row["frame.time_epoch"]
            ),

            "status_code": status_code
        },

        "body": body
    }

    return event



def build_evidence(pcap_file):
    event = build_nrf_discovery_event(pcap_file)

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    tshark_version = get_tshark_version()

    pcap_hash = calculate_sha256(
        pcap_file
    )

    evidence = {
        "schema_version": "1.0",

        "metadata": {
            "generated_at": generated_at,
            "tshark_version": tshark_version
        },

        "source": {
            "pcap_file": str(pcap_file.relative_to(BASE_DIR)),
            "sha256": pcap_hash
        },

        "events": [
            event
        ]
    }

    return evidence


def main(): 
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract NRF NF Discovery evidence"
    )

    evidence = build_evidence(context["pcap_file"])

    save_json(context["output_file"], evidence)


    output_file = context["output_file"]

    event = evidence["events"][0]


    print(f"Evidence saved to: {output_file}")


    print()
    print("--- NRF DISCOVERY EVIDENCE ---")

    print(
        f"Request frame: "
        f"{event['request']['frame']}"
    )

    print(
        f"Requester NF: "
        f"{event['request']['requester_nf_type']}"
    )

    print(
        f"Requester S-NSSAI: "
        f"{event['request']['requester_snssais']}"
    )

    print(
        f"Target NF: "
        f"{event['request']['target_nf_type']}"
    )

    print(
        f"Response frame: "
        f"{event['response']['frame']}"
    )

    print(
        f"HTTP status: "
        f"{event['response']['status_code']}"
    )

    print(
        f"Body frame: "
        f"{event['body']['frame']}"
    )

    print("------------------------------")


if __name__ == "__main__":
    main()