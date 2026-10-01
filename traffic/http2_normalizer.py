import json
from collections import defaultdict
from typing import Any
from urllib.parse import parse_qs, urlsplit

from traffic.models import MessageEvent


def _first(value: Any) -> Any:
    """
    Restituisce il primo elemento se TShark ha prodotto una lista, altrimenti restituisce direttamente il valore.
    """

    if isinstance(value, list):
        return value[0] if value else None

    return value


def _http2_blocks(value: Any) -> list[dict]:
    if value is None:
        return []

    if isinstance(value, dict):
        return [value]

    if isinstance(value, list):
        return [
            item for item in value
            if isinstance(item, dict)
        ]

    return []


def _to_list(value: Any) -> list:
    """
    Normalizza un valore TShark in una lista.

    Esempi:
        "GET"        -> ["GET"]
        ["a", "b"]   -> ["a", "b"]
        None         -> []
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _extract_headers(http2: dict) -> dict[str, str]:
    """
    Ricostruisce gli header HTTP/2 usando le liste parallele header_name e header_value prodotte da TShark.
    """

    names = _to_list(http2.get("http2_http2_header_name"))

    values = _to_list(http2.get("http2_http2_header_value"))

    headers = {}

    for name, value in zip(names, values):
        if name == "<unknown>":
            continue

        headers[str(name)] = str(value)

    return headers


def _decode_body(body_bytes: bytes) -> Any:
    """
    Prova a interpretare il payload come UTF-8 e, se possibile, come JSON.

    Se non è JSON restituisce la stringa.
    Se non è UTF-8 restituisce i byte in formato esadecimale.
    """

    if not body_bytes:
        return None

    try:
        text = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return body_bytes.hex()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _parse_path(path: str | None) -> tuple[str | None, dict]:
    """
    Separa il path HTTP dai query parameters.

    Esempio:
        /nnrf-disc/v1/nf-instances?target-nf-type=SMF
    diventa:
        path = /nnrf-disc/v1/nf-instances
        query = {"target-nf-type": "SMF"}
    """

    if not path:
        return None, {}

    parsed = urlsplit(path)

    query = {
        key: values[0] if len(values) == 1 else values
        for key, values in parse_qs(parsed.query).items()
    }

    return parsed.path, query


def normalize_http2(packets: list[dict]) -> list[MessageEvent]:
    """
    Converte i packet record TShark HTTP/2 in eventi applicativi.

    Request headers, response headers e DATA appartenenti allo stesso HTTP/2 stream vengono correlati tramite:
        (tcp.stream, http2.streamid)
    """

    transactions = defaultdict(
        lambda: {
            "request": None,
            "response": None,
            "request_body": bytearray(),
            "response_body": bytearray(),
            "orphan_body": bytearray(),
            "orphan_frames": [],
            "orphan_metadata": None
        }
    )

    for packet in packets:
        layers = packet.get("layers", {})

        frame = layers.get("frame", {})
        ip = layers.get("ip", {})
        tcp = layers.get("tcp", {})
        http2_blocks = _http2_blocks(layers.get("http2"))

        if not http2_blocks:
            continue

        frame_number = int(frame["frame_frame_number"])
        timestamp = float(frame["frame_frame_time_epoch"])

        src = ip.get("ip_ip_src")
        dst = ip.get("ip_ip_dst")

        tcp_stream = _first(tcp.get("tcp_tcp_stream"))
        
        if tcp_stream is None:
            continue
        
        tcp_stream = int(tcp_stream)


        for http2 in http2_blocks:
            http2_stream_id = _first(http2.get("http2_http2_streamid"))

        if http2_stream_id is None:
            continue

        http2_stream_id = int(http2_stream_id)


        key = (tcp_stream, http2_stream_id)

        transaction = transactions[key]

        method = _first(http2.get("http2_http2_headers_method"))

        status = _first(http2.get("http2_http2_headers_status"))

        data_hex = _first(http2.get("http2_http2_data_data"))


        # -------------------------
        # HTTP/2 REQUEST
        # -------------------------

        if method is not None:
            raw_path = _first(http2.get("http2_http2_headers_path"))

            path, query = _parse_path(raw_path)

            event = MessageEvent(
                frame_number=frame_number,
                timestamp=timestamp,
                protocol="http2",
                kind="request",
                src=src,
                dst=dst,
                related_frames=[frame_number],
                correlation={
                    "tcp_stream": tcp_stream,
                    "http2_stream_id": http2_stream_id,
                },
                fields={
                    "method": method,
                    "path": path,
                    "raw_path": raw_path,
                    "query": query,
                    "headers": _extract_headers(http2),
                },
            )

            transaction["request"] = event

        # -------------------------
        # HTTP/2 RESPONSE
        # -------------------------

        if status is not None:
            event = MessageEvent(
                frame_number=frame_number,
                timestamp=timestamp,
                protocol="http2",
                kind="response",
                src=src,
                dst=dst,
                related_frames=[frame_number],
                correlation={
                    "tcp_stream": tcp_stream,
                    "http2_stream_id": http2_stream_id,
                },
                fields={
                    "status": int(status),
                    "headers": _extract_headers(http2),
                },
            )

            transaction["response"] = event

        # -------------------------
        # HTTP/2 DATA
        # -------------------------

        if data_hex:
            try:
                data = bytes.fromhex(data_hex.replace(":", ""))
            except ValueError:
                continue

            request = transaction["request"]
            response = transaction["response"]

            # Se la direzione è la stessa della request, il DATA appartiene al body della request.
            if (
                request is not None
                and src == request.src
                and dst == request.dst
            ):
                transaction["request_body"].extend(data)

                if frame_number not in request.related_frames:
                    request.related_frames.append(frame_number)

            # Se la direzione è inversa, appartiene alla response.
            elif (
                request is not None
                and src == request.dst
                and dst == request.src
            ):
                transaction["response_body"].extend(data)

                if response is not None:
                    if frame_number not in response.related_frames:
                        response.related_frames.append(frame_number)


            # Se ci sono dei frames senza correlazione non li scarto
            else:
                transaction["orphan_body"].extend(data)
                transaction["orphan_frames"].append(frame_number)

                if transaction["orphan_metadata"] is None:
                    transaction["orphan_metadata"] = {
                        "frame_number": frame_number,
                        "timestamp": timestamp,
                        "src": src,
                        "dst": dst,
                        "tcp_stream": tcp_stream,
                        "http2_stream_id": http2_stream_id,
                        "headers": _extract_headers(http2),
                    }

    events = []

    for transaction in transactions.values():
        request = transaction["request"]
        response = transaction["response"]

        if request is not None:
            body = _decode_body(bytes(transaction["request_body"]))

            if body is not None:
                request.fields["body"] = body

            events.append(request)

        if response is not None:
            body = _decode_body(bytes(transaction["response_body"]))

            if body is not None:
                response.fields["body"] = body

            events.append(response)


        orphan_body = bytes(transaction["orphan_body"])
        orphan_metadata = transaction["orphan_metadata"]

        if orphan_body and orphan_metadata is not None:
            body = _decode_body(orphan_body)

            event = MessageEvent(
                frame_number=orphan_metadata["frame_number"],
                timestamp=orphan_metadata["timestamp"],
                protocol="http2",
                kind="data",
                src=orphan_metadata["src"],
                dst=orphan_metadata["dst"],
                related_frames=transaction["orphan_frames"],
                correlation={
                    "tcp_stream": orphan_metadata["tcp_stream"],
                    "http2_stream_id": orphan_metadata["http2_stream_id"],
                },
                fields={
                    "headers": orphan_metadata["headers"],
                    "body": body,
                },
            )

            events.append(event)

    events.sort(
        key=lambda event: (
            event.timestamp,
            event.frame_number,
        )
    )

    return events