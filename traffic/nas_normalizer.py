from typing import Any

from traffic.models import MessageEvent


REGISTRATION_REQUEST = "0x41"
AUTHENTICATION_REQUEST = "0x56"
AUTHENTICATION_RESPONSE = "0x57"
AUTHENTICATION_REJECT = "0x58"
AUTHENTICATION_FAILURE = "0x59"
IDENTITY_REQUEST = "0x5b"
IDENTITY_RESPONSE = "0x5c"


IDENTITY_TYPES = {
    1: "SUCI",
    2: "5G_GUTI",
}



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


def _identity_name(value) -> str | None:
    if value is None:
        return None

    try:
        identity_type = int(value)
    except (TypeError, ValueError):
        return None

    return IDENTITY_TYPES.get(
        identity_type,
        f"UNKNOWN_{identity_type}"
    )


def normalize_nas_events(rows: list[dict]) -> list[MessageEvent]:
    events = []

    supported_types = {
        REGISTRATION_REQUEST,
        AUTHENTICATION_REQUEST,
        AUTHENTICATION_RESPONSE,
        AUTHENTICATION_REJECT,
        AUTHENTICATION_FAILURE,
        IDENTITY_REQUEST,
        IDENTITY_RESPONSE,
    }

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

        if message_type not in supported_types:
            continue

        frame_number = frame.get("frame_frame_number")
        timestamp = frame.get("frame_frame_time_epoch")

        if frame_number is None or timestamp is None:
            continue

        fields = {}


        # --------------------------------------------------
        # Registration Request
        # --------------------------------------------------

        if message_type == REGISTRATION_REQUEST:
            semantic_type = "nas.registration_request"

            identity_type = nas_container.get("nas-5gs_nas_5gs_mm_type_id")

            identity_name = _identity_name(identity_type)

            if identity_name is not None:
                fields["identity_type"] = identity_name


        # --------------------------------------------------
        # Authentication Request
        # --------------------------------------------------

        elif message_type == AUTHENTICATION_REQUEST:
            semantic_type = "nas.authentication_request"

            rand = nas_container.get("gsm_a_dtap_gsm_a_dtap_rand")

            autn = nas_container.get("gsm_a_dtap_gsm_a_dtap_autn")

            if rand is not None:
                fields["rand"] = _normalize_hex(rand)

            if autn is not None:
                fields["autn"] = _normalize_hex(autn)


        # --------------------------------------------------
        # Authentication Response
        # --------------------------------------------------

        elif message_type == AUTHENTICATION_RESPONSE:
            semantic_type = "nas.authentication_response"

            res_star = nas_container.get("nas-eps_nas_eps_emm_res")

            if res_star is not None:
                fields["res_star"] = _normalize_hex(res_star)


        # --------------------------------------------------
        # Authentication Reject
        # --------------------------------------------------

        elif message_type == AUTHENTICATION_REJECT:
            semantic_type = "nas.authentication_reject"

            fields["present"] = True


        # --------------------------------------------------
        # Authentication Failure
        # --------------------------------------------------

        elif message_type == AUTHENTICATION_FAILURE:
            semantic_type = "nas.authentication_failure"

            cause = nas_container.get("nas-5gs_nas_5gs_mm_5gmm_cause")

            auts = nas_container.get("gsm_a_dtap_gsm_a_dtap_auts")

            if cause is not None:
                fields["cause"] = int(cause)

            if auts is not None:
                fields["auts"] = _normalize_hex(auts)


        # --------------------------------------------------
        # Identity Request
        # --------------------------------------------------

        elif message_type == IDENTITY_REQUEST:
            semantic_type = "nas.identity_request"

            identity_type = nas_container.get("nas-5gs_nas_5gs_mm_type_id")

            identity_name = _identity_name(identity_type)

            if identity_name is not None:
                fields["requested_identity"] = identity_name


        # --------------------------------------------------
        # Identity Response
        # --------------------------------------------------

        else:
            semantic_type = "nas.identity_response"

            identity_type = nas_container.get("nas-5gs_nas_5gs_mm_type_id")

            identity_name = _identity_name(identity_type)

            if identity_name is not None:
                fields["identity_type"] = identity_name

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