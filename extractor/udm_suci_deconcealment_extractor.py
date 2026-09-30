import json

from datetime import datetime, timezone
from pathlib import Path

from utils.tshark_utils import calculate_sha256, get_tshark_version, run_tshark
from utils.http2_utils import classify_transaction_frames, decode_json_body
from utils.json_utils import load_json, save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent



def get_original_supi(subscriber_file):
    subscriber = load_json(subscriber_file)

    if "supi" not in subscriber:
        raise RuntimeError(
            "SUPI not found in subscriber configuration"
        )

    return f"imsi-{subscriber['supi']}"


def find_deconcealment_request(pcap_file):
    rows = run_tshark(
        pcap_file,
        'http2.headers.path contains "generate-auth-data" '
        '&& http2.headers.path contains "suci-"',
        [
            "frame.number",
            "frame.time_relative",
            "tcp.stream",
            "http2.streamid",
            "http2.headers.method",
            "http2.headers.path"
        ],
        decode_as="tcp.port==7777,http2"
    )

    if not rows:
        raise RuntimeError(
            "No SUCI generate-auth-data request found"
        )

    if len(rows) > 1:
        raise RuntimeError(
            "Multiple SUCI generate-auth-data requests found: " f"{len(rows)}"
        )

    return rows[0]


def extract_suci_from_path(path):
    marker = "/nudm-ueau/v1/"

    if marker not in path:
        raise RuntimeError(
            f"Unrecognized UDM path: {path}"
        )

    remainder = path.split(marker, 1)[1]

    suci = remainder.split("/", 1)[0]
    if not suci.startswith("suci-"):
        raise RuntimeError(
            f"Identifier in path is not a SUCI: {suci}"
        )

    return suci



def get_transaction_frames(pcap_file, tcp_stream, http2_stream):
    return run_tshark(
        pcap_file,
        f'tcp.stream == {tcp_stream} '
        f'&& http2.streamid == {http2_stream}',
        [
            "frame.number",
            "frame.time_relative",
            "http2.headers.method",
            "http2.headers.path",
            "http2.headers.status",
            "http2.length",
            "http2.flags.end_stream",
            "http2.data.data"
        ],
        decode_as="tcp.port==7777,http2"
    )


def build_suci_deconcealment_event(pcap_file, subscriber_file):
    # 1. Identificazione della transazione
    request = find_deconcealment_request(pcap_file)

    tcp_stream = request["tcp.stream"]
    http2_stream = request["http2.streamid"].split(",")[0]

    frames = get_transaction_frames(
        pcap_file,
        tcp_stream,
        http2_stream
    )


    # 2. Classificazione dei frame
    classified = classify_transaction_frames(frames)

    request_headers = classified["request_headers"]
    response_headers = classified["response_headers"]

    request_body_frames_raw = classified["request_body_frames"]
    response_body_frames_raw = classified["response_body_frames"]

    request_end_stream_frames_raw = classified["request_end_stream_frames"]
    response_end_stream_frames_raw = classified["response_end_stream_frames"]

    if request_headers is None:
        raise RuntimeError("Request headers not found")

    if response_headers is None:
        raise RuntimeError("Response headers not found")


    # 3. Decoding dei body
    request_body = decode_json_body(
        request_body_frames_raw
    )

    response_body = decode_json_body(
        response_body_frames_raw
    )

    if "supi" not in response_body:
        raise RuntimeError(
            "SUPI not found in UDM response"
        )


    # 4. Estrazione e normalizzazione dei valori
    request_path = request["http2.headers.path"]
    request_method = request["http2.headers.method"]

    suci = extract_suci_from_path(request_path)
    original_supi = get_original_supi(subscriber_file)

    status_raw = response_headers["http2.headers.status"]

    if not status_raw:
        raise RuntimeError(
            "HTTP status not found"
        )

    status_code = int(status_raw)

    request_headers_frame = int(
        request_headers["frame.number"]
    )

    request_body_frames = [
        int(frame["frame.number"])
        for frame in request_body_frames_raw
    ]

    request_end_stream_frames = [
        int(frame["frame.number"])
        for frame in request_end_stream_frames_raw
    ]

    response_headers_frame = int(
        response_headers["frame.number"]
    )

    response_body_frames = [
        int(frame["frame.number"])
        for frame in response_body_frames_raw
    ]

    response_end_stream_frames = [
        int(frame["frame.number"])
        for frame in response_end_stream_frames_raw
    ]


    # 5. Costruzione dell'evento
    event = {
        "type": "suci_deconcealment",

        "test_input": {
            "original_supi": original_supi
        },

        "request": {
            "headers_frame": request_headers_frame,
            "body_frames": request_body_frames,
            "end_stream_frames": request_end_stream_frames,
            "method": request_method,
            "path": request_path,
            "suci": suci,
            "body": request_body
        },

        "response": {
            "headers_frame": response_headers_frame,
            "body_frames": response_body_frames,
            "end_stream_frames": response_end_stream_frames,
            "status_code": status_code,
            "body": response_body
        }
    }

    return event



def build_evidence(pcap_file, subscriber_file):
    event = build_suci_deconcealment_event(pcap_file, subscriber_file)

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    tshark_version = get_tshark_version()

    sha256 = calculate_sha256(pcap_file)


    subscriber_sha256 = calculate_sha256(subscriber_file)

    subscriber_file_relative = str(subscriber_file.relative_to(BASE_DIR))


    evidence = {
        "schema_version": "1.0",

        "metadata": {
            "generated_at": generated_at,

            "tshark_version": tshark_version
        },

        "source": {
            "pcap_file": str(
                pcap_file.relative_to(BASE_DIR)
            ),

            "sha256": sha256
        },

        "configuration": {
            "subscriber_file": subscriber_file_relative,
            "subscriber_sha256": subscriber_sha256
        },

        "events": [
            event
        ]
    }

    return evidence        




def main():
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract UDM SUCI de-concealment evidence"
    )

    subscriber_file = BASE_DIR / context["config"]["subscriber_file"]
    evidence = build_evidence(context["pcap_file"], subscriber_file)


    output_file = context["output_file"]

    save_json(output_file, evidence)


    print(
        f"Evidence saved to: {output_file}"
    )


if __name__ == "__main__":
    main()