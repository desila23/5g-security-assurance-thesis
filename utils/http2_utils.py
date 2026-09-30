import json


def classify_transaction_frames(frames):
    request_headers = None
    response_headers = None

    request_body_frames = []
    response_body_frames = []

    request_end_stream_frames = []
    response_end_stream_frames = []

    for frame in frames:
        method = frame["http2.headers.method"]
        status = frame["http2.headers.status"]

        lengths_raw = frame["http2.length"]
        end_stream_raw = frame["http2.flags.end_stream"]

        lengths = []

        if lengths_raw:
            for value in lengths_raw.split(","):
                value = value.strip()

                if value.isdigit():
                    lengths.append(int(value))

        has_payload = any(length > 0 for length in lengths)

        is_end_stream = ("1" in end_stream_raw.split(","))


        # Classificazione del contenuto del frame
        if method:
            request_headers = frame

        elif status:
            response_headers = frame

        elif request_headers is not None and response_headers is None:
            if has_payload:
                request_body_frames.append(frame)

        elif response_headers is not None:
            if has_payload:
                response_body_frames.append(frame)


        # END_STREAM viene gestito indipendentemente
        if is_end_stream:
            if status:
                response_end_stream_frames.append(frame)

            elif response_headers is None:
                request_end_stream_frames.append(frame)

            else:
                response_end_stream_frames.append(frame)


    return {
        "request_headers": request_headers,
        "request_body_frames": request_body_frames,
        "request_end_stream_frames": request_end_stream_frames,

        "response_headers": response_headers,
        "response_body_frames": response_body_frames,
        "response_end_stream_frames": response_end_stream_frames
    }


def decode_json_body(body_frames):
    hex_payload = ""

    for frame in body_frames:
        data_hex = frame["http2.data.data"]

        if data_hex:
            hex_payload += data_hex.replace(":", "")

    if not hex_payload:
        raise RuntimeError(
            "No HTTP/2 payload found"
        )

    try:
        body_bytes = bytes.fromhex(hex_payload)

    except ValueError as e:
        raise RuntimeError(
            f"Invalid HTTP/2 payload: {e}"
        ) from e

    try:
        body_text = body_bytes.decode("utf-8")

    except UnicodeDecodeError as e:
        raise RuntimeError(
            f"Payload cannot be decoded as UTF-8: {e}"
        ) from e

    try:
        return json.loads(body_text)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Body is not valid JSON: {e}"
        ) from e