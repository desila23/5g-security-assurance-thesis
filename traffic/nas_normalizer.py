from typing import Any

from traffic.models import MessageEvent


AUTHENTICATION_REQUEST = "0x56"
AUTHENTICATION_FAILURE = "0x59"


def _find_dict_with_key(data: Any, key: str) -> dict | None:
    if isinstance(data, dict):
        if key in data:
            return data

        for value in data.values():
            result = _find_dict_with_key(value, key)

            if result is not None:
                return result

    elif isinstance(data, list):
        for value in data:
            result = _find_dict_with_key(value, key)

            if result is not None:
                return result

    return None


def _normalize_hex(value: str | None) -> str | None:
    if value is None:
        return None

    return value.replace(":", "").lower()


def normalize_nas_events(rows: list[dict]) -> list[MessageEvent]:
    events = []

    for row in rows:
        layers = row.get("layers", {})

        frame = layers.get("frame", {})
        ip = layers.get("ip", {})

        nas_container = _find_dict_with_key(
            layers,
            "nas-5gs_nas_5gs_mm_message_type"
        )

        if nas_container is None:
            continue

        message_type = nas_container.get(
            "nas-5gs_nas_5gs_mm_message_type"
        )

        if message_type not in {
            AUTHENTICATION_REQUEST,
            AUTHENTICATION_FAILURE,
        }:
            continue

        frame_number = frame.get("frame_frame_number")
        timestamp = frame.get("frame_frame_time_epoch")

        if frame_number is None or timestamp is None:
            continue

        fields = {}

        if message_type == AUTHENTICATION_REQUEST:
            semantic_type = "nas.authentication_request"

            rand = nas_container.get(
                "gsm_a_dtap_gsm_a_dtap_rand"
            )

            if rand is not None:
                fields["rand"] = _normalize_hex(rand)

        else:
            semantic_type = "nas.authentication_failure"

            cause = nas_container.get(
                "nas-5gs_nas_5gs_mm_5gmm_cause"
            )

            auts = nas_container.get(
                "gsm_a_dtap_gsm_a_dtap_auts"
            )

            if cause is not None:
                fields["cause"] = int(cause)

            if auts is not None:
                fields["auts"] = _normalize_hex(auts)

        events.append(
            MessageEvent(
                frame_number=int(frame_number),
                timestamp=float(timestamp),
                protocol="nas_5gs",
                kind="message",
                src=ip.get("ip_ip_src"),
                dst=ip.get("ip_ip_dst"),
                message_type=semantic_type,
                fields=fields,
            )
        )

    events.sort(
        key=lambda event: (
            event.timestamp,
            event.frame_number
        )
    )

    return events