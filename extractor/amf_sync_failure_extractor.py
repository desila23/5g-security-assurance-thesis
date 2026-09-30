from datetime import datetime, timezone
from pathlib import Path

from utils.tshark_utils import calculate_sha256, get_tshark_version, run_tshark,extract_tcp_json_messages, compact_tcp_json_message
from utils.json_utils import save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# NAS MESSAGE TYPES
# ============================================================

REGISTRATION_REQUEST = "0x41"
AUTHENTICATION_REQUEST = "0x56"
AUTHENTICATION_RESPONSE = "0x57"
AUTHENTICATION_FAILURE = "0x59"
SECURITY_MODE_COMMAND = "0x5d"

SYNCH_FAILURE_CAUSE = 21


# ============================================================
# TSHARK - NAS EXTRACTION
# ============================================================

def extract_nas_messages(pcap_file):
    fields = [
        "frame.number",
        "frame.time_relative",
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "nas_5gs.mm.message_type",
        "nas_5gs.mm.5gmm_cause",
        "ngap.procedureCode",
        "ngap.NAS_PDU",
        "gsm_a.dtap.auts"
    ]

    rows = run_tshark(
        pcap_file,
        "nas_5gs.mm.message_type",
        fields
    )

    messages = []

    for row in rows:
        message_type = row["nas_5gs.mm.message_type"]

        cause_raw = row["nas_5gs.mm.5gmm_cause"]
        cause = int(cause_raw) if cause_raw else None

        procedure_code_raw = row["ngap.procedureCode"]
        procedure_code = int(procedure_code_raw) if procedure_code_raw else None

        messages.append({
            "frame": int(row["frame.number"]),
            "timestamp_relative": float(row["frame.time_relative"]),
            "timestamp_epoch": float(row["frame.time_epoch"]),
            "ip_src": row["ip.src"],
            "ip_dst": row["ip.dst"],
            "message_type": message_type,
            "cause": cause,
            "ngap_procedure_code": procedure_code,
            "nas_pdu": row["ngap.NAS_PDU"],
            "auts": row["gsm_a.dtap.auts"] or None
        })

    return messages


# ============================================================
# SBI / AUSF EXTRACTION
# ============================================================

def extract_resynchronization_requests(pcap_file):
    messages = extract_tcp_json_messages(
        pcap_file,
        'tcp contains "resynchronizationInfo"'
    )

    return [
        message
        for message in messages
        if "resynchronizationInfo" in message["body"]
    ]


def extract_authentication_vectors(pcap_file):
    messages = extract_tcp_json_messages(
        pcap_file,
        'tcp contains "authType"'
    )

    return [
        message
        for message in messages
        if message["body"].get("authType") == "5G_AKA"
    ]


# ============================================================
# SUPPORTS
# ============================================================

def find_message(
    messages,
    message_type,
    reference_time=None,
    cause=None,
    relation=None,
    required=True
):
    candidates = [
        message
        for message in messages
        if (
            message["message_type"] == message_type
            and (cause is None or message["cause"] == cause)
        )
    ]

    if reference_time is not None:
        if relation == "before":
            candidates = [
                message
                for message in candidates
                if message["timestamp_relative"] < reference_time
            ]

        elif relation == "after":
            candidates = [
                message
                for message in candidates
                if message["timestamp_relative"] > reference_time
            ]

    if not candidates:
        if required:
            raise RuntimeError(
                f"No message found: "
                f"type={message_type}, "
                f"cause={cause}, "
                f"relation={relation}"
            )

        return None

    if relation == "before":
        return max(
            candidates,
            key=lambda message: message["timestamp_relative"]
        )

    if relation == "after":
        return min(
            candidates,
            key=lambda message: message["timestamp_relative"]
        )

    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one message "
            f"type={message_type}, cause={cause}, "
            f"found: {len(candidates)}"
        )

    return candidates[0]


def find_json_message(
    messages,
    reference_time=None,
    relation=None,
    required=True
):
    candidates = list(messages)

    if reference_time is not None:
        if relation == "before":
            candidates = [
                message
                for message in candidates
                if message["timestamp_relative"] < reference_time
            ]

        elif relation == "after":
            candidates = [
                message
                for message in candidates
                if message["timestamp_relative"] > reference_time
            ]

    if not candidates:
        if required:
            raise RuntimeError(
                "No matching JSON/TCP message found"
            )

        return None

    if relation == "before":
        return max(
            candidates,
            key=lambda message: message["timestamp_relative"]
        )

    if relation == "after":
        return min(
            candidates,
            key=lambda message: message["timestamp_relative"]
        )

    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one JSON/TCP message, "
            f"found: {len(candidates)}"
        )

    return candidates[0]


# ============================================================
# NORMALIZATION
# ============================================================

def compact_message(message, include_nas_pdu=False):
    if message is None:
        return None

    result = {
        "frame": message["frame"],
        "timestamp_relative": message["timestamp_relative"],
        "timestamp_epoch": message["timestamp_epoch"],
        "ip_src": message["ip_src"],
        "ip_dst": message["ip_dst"],
        "message_type": message["message_type"],
        "ngap_procedure_code": message["ngap_procedure_code"]
    }

    if message["cause"] is not None:
        result["cause"] = message["cause"]

    if include_nas_pdu:
        result["nas_pdu"] = message["nas_pdu"]

    return result



# ============================================================
# EVENT BUILDING
# ============================================================

def build_event(pcap_file, case):
    # --------------------------------------------------------
    # NAS
    # --------------------------------------------------------

    messages = extract_nas_messages(pcap_file)

    sync_failure = find_message(
        messages,
        AUTHENTICATION_FAILURE,
        cause=SYNCH_FAILURE_CAUSE
    )

    sync_failure_time = sync_failure["timestamp_relative"]

    initial_auth_request = find_message(
        messages,
        AUTHENTICATION_REQUEST,
        reference_time=sync_failure_time,
        relation="before"
    )

    initial_registration = find_message(
        messages,
        REGISTRATION_REQUEST,
        reference_time=initial_auth_request["timestamp_relative"],
        relation="before",
        required=False
    )

    next_registration = find_message(
        messages,
        REGISTRATION_REQUEST,
        reference_time=sync_failure_time,
        relation="after",
        required=False
    )

    next_auth_request = find_message(
        messages,
        AUTHENTICATION_REQUEST,
        reference_time=sync_failure_time,
        relation="after",
        required=False
    )

    next_auth_response = None

    if next_auth_request is not None:
        next_auth_response = find_message(
            messages,
            AUTHENTICATION_RESPONSE,
            reference_time=next_auth_request["timestamp_relative"],
            relation="after",
            required=False
        )

    security_mode_command = None

    if next_auth_request is not None:
        security_mode_command = find_message(
            messages,
            SECURITY_MODE_COMMAND,
            reference_time=next_auth_request["timestamp_relative"],
            relation="after",
            required=False
        )


    # --------------------------------------------------------
    # AUTS FROM NAS
    # --------------------------------------------------------

    auts = sync_failure["auts"]

    auts_present = auts is not None

    synchronization_failure = compact_message(
        sync_failure,
        include_nas_pdu=True
    )

    synchronization_failure.update({
        "cause_name": "Synch failure",
        "auts_present": auts_present,
        "auts": auts
    })


    # --------------------------------------------------------
    # SBI / AUSF
    # --------------------------------------------------------

    auth_vectors = extract_authentication_vectors(
        pcap_file
    )

    initial_auth_vector = find_json_message(
        auth_vectors,
        reference_time=sync_failure_time,
        relation="before",
        required=False
    )

    resync_requests = extract_resynchronization_requests(
        pcap_file
    )

    resync_request = find_json_message(
        resync_requests,
        reference_time=sync_failure_time,
        relation="after",
        required=False
    )

    resync_request_time = None

    if resync_request is not None:
        resync_request_time = resync_request["timestamp_relative"]

    ausf_response = None

    if resync_request_time is not None:
        ausf_response = find_json_message(
            auth_vectors,
            reference_time=resync_request_time,
            relation="after",
            required=False
        )


    # --------------------------------------------------------
    # NORMALIZED SBI OBJECTS
    # --------------------------------------------------------

    initial_authentication_vector = compact_tcp_json_message(
        initial_auth_vector,
        data_key="5gAuthData",
        field_map={
            "auth_type": {
                "source": "body",
                "field": "authType"
            },
            "rand": {
                "source": "nested",
                "field": "rand"
            },
            "hxres_star": {
                "source": "nested",
                "field": "hxresStar"
            },
            "autn": {
                "source": "nested",
                "field": "autn"
            },
            "serving_network_name": {
                "source": "body",
                "field": "servingNetworkName"
            }
        }
    )

    resynchronization_request = compact_tcp_json_message(
        resync_request,
        data_key="resynchronizationInfo",
        field_map={
            "supi_or_suci": {
                "source": "body",
                "field": "supiOrSuci"
            },
            "serving_network_name": {
                "source": "body",
                "field": "servingNetworkName"
            },
            "rand": {
                "source": "nested",
                "field": "rand"
            },
            "auts": {
                "source": "nested",
                "field": "auts"
            }
        }
    )

    ausf_authentication_response = compact_tcp_json_message(
        ausf_response,
        data_key="5gAuthData",
        field_map={
            "auth_type": {
                "source": "body",
                "field": "authType"
            },
            "rand": {
                "source": "nested",
                "field": "rand"
            },
            "hxres_star": {
                "source": "nested",
                "field": "hxresStar"
            },
            "autn": {
                "source": "nested",
                "field": "autn"
            },
            "serving_network_name": {
                "source": "body",
                "field": "servingNetworkName"
            }
        }
    )


    # --------------------------------------------------------
    # TIMING
    # --------------------------------------------------------

    sync_to_next_auth = None

    if next_auth_request is not None:
        sync_to_next_auth = round(
            next_auth_request["timestamp_relative"] - sync_failure_time,
            6
        )

    sync_to_next_registration = None

    if next_registration is not None:
        sync_to_next_registration = (
            next_registration["timestamp_relative"]
            - sync_failure_time
        )

    resync_to_ausf_response = None

    if resync_request is not None and ausf_response is not None:
        resync_to_ausf_response = round(
            ausf_response["timestamp_relative"] - resync_request["timestamp_relative"],
            6
        )


    # --------------------------------------------------------
    # SUBSEQUENT AUTHENTICATION REQUEST
    # --------------------------------------------------------

    subsequent_authentication_request = {
        "present": next_auth_request is not None
    }

    if next_auth_request is not None:
        subsequent_authentication_request.update(
            compact_message(
                next_auth_request,
                include_nas_pdu=True
            )
        )


    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    return {
        "type": "amf_sync_failure",
        "case": case,

        "initial_registration": compact_message(
            initial_registration
        ),

        "initial_authentication_request": compact_message(
            initial_auth_request
        ),

        "initial_authentication_vector": initial_authentication_vector,

        "synchronization_failure": synchronization_failure,

        "resynchronization_request": resynchronization_request,

        "ausf_authentication_response": ausf_authentication_response,

        "subsequent_registration": compact_message(
            next_registration
        ),

        "subsequent_authentication_request": subsequent_authentication_request,

        "subsequent_authentication_response": compact_message(
            next_auth_response
        ),

        "security_mode_command": compact_message(
            security_mode_command
        ),

        "timing": {
            "sync_failure_to_next_registration_seconds": sync_to_next_registration,
            "sync_failure_to_next_authentication_request_seconds": sync_to_next_auth,
            "resynchronization_request_to_ausf_response_seconds": resync_to_ausf_response
        }
    }


# ============================================================
# EVIDENCE
# ============================================================

def build_evidence(pcap_file, case):
    event = build_event(
        pcap_file,
        case
    )

    return {
        "schema_version": "1.0",

        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tshark_version": get_tshark_version()
        },

        "source": {
            "pcap_file": str(pcap_file.relative_to(BASE_DIR)),
            "sha256": calculate_sha256(pcap_file)
        },

        "events": [
            event
        ]
    }


# ============================================================
# MAIN
# ============================================================

def main():
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract AMF synchronization failure evidence"
    )

    test_config = context["config"]
    pcap_file = context["pcap_file"]
    output_file = context["output_file"]

    case = test_config["case"]

    evidence = build_evidence(
        pcap_file,
        case
    )

    save_json(
        output_file,
        evidence
    )

    print(
        f"Evidence saved to: {output_file}"
    )


if __name__ == "__main__":
    main()