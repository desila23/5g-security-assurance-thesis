import subprocess
import json

from datetime import datetime, timezone
from pathlib import Path

from verifier.udm_mac_verifier import verify_auth_vector_mac
from utils.tshark_utils import calculate_sha256, get_tshark_version
from utils.subscriber_utils import load_subscriber_config
from utils.json_utils import save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent


#==============================================
# FUNZIONI
#==============================================

def run_tshark(pcap_file, display_filter, fields):
    command = [
        "tshark",
        "-r", str(pcap_file),
        "-d", "tcp.port==7777,http2",
        "-Y", display_filter,
        "-T", "fields"
    ]

    for field in fields:
        command.extend(["-e", field])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout


def find_generate_auth_requests(pcap_file):
    output = run_tshark(
        pcap_file,
        'http2.headers.path contains "generate-auth-data"',
        [
            "frame.number",
            "frame.time_relative",
            "frame.time_epoch",
            "tcp.stream",
            "http2.streamid",
            "http2.headers.method",
            "http2.headers.path"
        ]
    )

    requests = []

    for line in output.strip().splitlines():
        columns = line.split("\t")

        if len(columns) < 7:
            continue

        frame_number = int(columns[0])
        timestamp_relative = float(columns[1])
        timestamp_epoch = float(columns[2])
        tcp_stream = int(columns[3])

        http2_stream_ids = columns[4].split(",")
        http2_stream_id = int(http2_stream_ids[0])

        method = columns[5]
        path = columns[6]

        requests.append({
            "headers_frame": frame_number,
            "timestamp_relative": timestamp_relative,
            "timestamp_epoch": timestamp_epoch,
            "tcp_stream": tcp_stream,
            "http2_stream_id": http2_stream_id,
            "method": method,
            "path": path
        })

    return requests



def get_transaction_frames(pcap_file, tcp_stream, http2_stream_id):
    output = run_tshark(
        pcap_file,
        f"tcp.stream == {tcp_stream} && http2.streamid == {http2_stream_id}",
        [
            "frame.number",
            "frame.time_relative",
            "frame.time_epoch",
            "http2.header.name",
            "http2.header.value",
            "http2.data.data",
            "http2.length",
            "http2.flags.end_stream"        
        ]
    )

    frames = []

    for line in output.strip().splitlines():
        columns = line.split("\t")

        while len(columns) < 8:
            columns.append("")

        frame_number = int(columns[0])
        timestamp_relative = float(columns[1])
        timestamp_epoch = float(columns[2])
        header_names = columns[3]
        data = columns[5]

        http2_lengths = [
            int(value)
            for value in columns[6].split(",")
            if value
        ]

        end_stream_values = [
            value
            for value in columns[7].split(",")
            if value
        ]

        end_stream = "1" in end_stream_values


        frames.append({
            "frame": frame_number,
            "timestamp_relative": timestamp_relative,
            "timestamp_epoch": timestamp_epoch,
            "header_names": header_names,
            "data": data,
            "http2_lengths": http2_lengths,
            "end_stream": end_stream
        })

    return frames


def classify_transaction_frames(frames):
    request_headers_frame = None
    request_body_frames = []
    request_end_stream_frame = None

    response_headers_frame = None
    response_body_frames = []
    response_end_stream_frame = None


    for frame in frames:
        header_names = frame["header_names"]
        http2_lengths = frame["http2_lengths"]
        end_stream = frame["end_stream"]

        if ":method" in header_names:
            request_headers_frame = frame["frame"]

        elif ":status" in header_names:
            response_headers_frame = frame["frame"]

        elif any(length > 0 for length in http2_lengths):
            if response_headers_frame is None:
                request_body_frames.append(frame["frame"])
            else:
                response_body_frames.append(frame["frame"])

        if end_stream:
            if response_headers_frame is None:
                request_end_stream_frame = frame["frame"]
            else:
                response_end_stream_frame = frame["frame"]

    return {
        "request_headers_frame": request_headers_frame,
        "request_body_frames": request_body_frames,
        "request_end_stream_frame": request_end_stream_frame,

        "response_headers_frame": response_headers_frame,
        "response_body_frames": response_body_frames,
        "response_end_stream_frame": response_end_stream_frame
    }


def decode_json_body(frames, body_frame_numbers):
    data_values = []

    for frame in frames:
        if frame["frame"] in body_frame_numbers:
            data = frame["data"]

            if data:
                data_values.append(data)

    if not data_values:
        raise RuntimeError(
            f"No HTTP/2 body found in frames {body_frame_numbers}"
        )

    hex_data = "".join(data_values)

    try:
        body_bytes = bytes.fromhex(hex_data)
    except ValueError as e:
        raise RuntimeError(
            f"HTTP/2 body is not valid HEX in frames {body_frame_numbers}"
        ) from e

    try:
        body_text = body_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise RuntimeError(
            f"HTTP/2 body cannot be decoded as UTF-8 in frames {body_frame_numbers}"
        ) from e

    try:
        return json.loads(body_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"HTTP/2 body is not valid JSON in frames {body_frame_numbers}"
        ) from e



def get_response_status(pcap_file, response_headers_frame):
    output = run_tshark(
        pcap_file,
        f"frame.number == {response_headers_frame}",
        [
            "http2.headers.status"
        ]
    )

    status = output.strip()

    if not status:
        raise RuntimeError(
            f"HTTP status not found in frame {response_headers_frame}"
        )

    return int(status)


def build_transaction_event(pcap_file, request, subscriber_key, subscriber_opc):
    frames = get_transaction_frames(
        pcap_file,
        request["tcp_stream"],
        request["http2_stream_id"]
    )

    classification = classify_transaction_frames(frames)

    request_body = decode_json_body(
        frames,
        classification["request_body_frames"]
    )

    response_body = decode_json_body(
        frames,
        classification["response_body_frames"]
    )


    auth_vector = response_body["authenticationVector"]


    mac_verification = verify_auth_vector_mac(
        auth_vector,
        subscriber_key,
        subscriber_opc
    )


    status_code = get_response_status(
        pcap_file,
        classification["response_headers_frame"]
    )


    if "resynchronizationInfo" in request_body:
        event_type = "resynchronization"
    else:
        event_type = "initial_auth"


    request_end_stream_frames = []
    if classification["request_end_stream_frame"] is not None:
        request_end_stream_frames.append(
            classification["request_end_stream_frame"]
        )


    response_end_stream_frames = []
    if classification["response_end_stream_frame"] is not None:
        response_end_stream_frames.append(
            classification["response_end_stream_frame"]
        )


    return {
        "type": event_type,

        "request": {
            "headers_frame": classification["request_headers_frame"],
            "body_frames": classification["request_body_frames"],
            "end_stream_frames": request_end_stream_frames,
            "timestamp_relative": request["timestamp_relative"],
            "timestamp_epoch": request["timestamp_epoch"],
            "tcp_stream": request["tcp_stream"],
            "http2_stream_id": request["http2_stream_id"],
            "method": request["method"],
            "path": request["path"],
            "body": request_body
        },

        "response": {
            "headers_frame": classification["response_headers_frame"],
            "body_frames": classification["response_body_frames"],
            "end_stream_frames": response_end_stream_frames,
            "status_code": status_code,
            "body": response_body,
            "mac_verification": mac_verification
        }
    }



def build_evidence(pcap_file, subscriber_file):
    requests = find_generate_auth_requests(pcap_file)

    subscriber_sha256 = calculate_sha256(subscriber_file)
    subscriber_relative = str(subscriber_file.relative_to(BASE_DIR))
    subscriber = load_subscriber_config(subscriber_file)

    subscriber_key = bytes.fromhex(
        subscriber["key"]
    )

    subscriber_opc = bytes.fromhex(
        subscriber["opc"]
    )


    events = []

    for request in requests:
        event = build_transaction_event(pcap_file, request, subscriber_key, subscriber_opc)
        events.append(event)

    initial_auth_events = [
        event 
        for event in events 
        if event["type"] == "initial_auth"
    ]

    resynchronization_events = [
        event
        for event in events
        if event["type"] == "resynchronization"
    ]

    if len(initial_auth_events) != 1:
        raise RuntimeError(
            "The test requires exactly one initial_auth event, "
            f"found: {len(initial_auth_events)}"
        )

    if len(resynchronization_events) != 1:
        raise RuntimeError(
            "The test requires exactly one resynchronization event, "
            f"found: {len(resynchronization_events)}"
        )


    evidence = {
        "schema_version": "1.0",

        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tshark_version": get_tshark_version()
        },

        "source": {
            "pcap_file": str(pcap_file.relative_to(BASE_DIR)),
            "sha256": calculate_sha256(pcap_file)
        },

        "configuration": {
            "subscriber_file": subscriber_relative,
            "subscriber_sha256": subscriber_sha256
        },

        "events": events
    }

    return evidence



def main():
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract UDM resynchronization evidence"
    )

    subscriber_file = BASE_DIR / context["config"]["subscriber_file"]
    
    evidence = build_evidence(context["pcap_file"], subscriber_file)

    output_file = context["output_file"]
    
    save_json(output_file, evidence)

    print(f"Evidence saved to: {output_file}")


if __name__ == "__main__":
    main()