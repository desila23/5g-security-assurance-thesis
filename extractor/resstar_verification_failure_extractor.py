import hashlib

from datetime import datetime, timezone
from pathlib import Path

from utils.tshark_utils import (
    calculate_sha256, 
    get_tshark_version, 
    run_tshark, 
    extract_tcp_json_messages, 
    compact_tcp_json_message
)

from utils.json_utils import save_json

import utils.extractor_utils as extractor_utils


BASE_DIR = Path(__file__).resolve().parent.parent


# -- NAS MESSAGE TYPES --
REGISTRATION_REQUEST = "0x41"
AUTHENTICATION_REQUEST = "0x56"
AUTHENTICATION_RESPONSE = "0x57"
AUTHENTICATION_REJECT = "0x58"
IDENTITY_REQUEST = "0x5b"
IDENTITY_RESPONSE = "0x5c"

IDENTITY_TYPES = {
    1: "SUCI",
    2: "5G_GUTI"
}



# -- NAS EXTRACTION --
def extract_nas_messages(pcap_file):
    fields = [
        "frame.number",
        "frame.time_relative",
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "nas_5gs.mm.message_type",
        "nas_5gs.mm.type_id",
        "gsm_a.dtap.rand",
        "gsm_a.dtap.autn",
        "nas_eps.emm.res"
    ]

    rows = run_tshark(
        pcap_file,
        "nas_5gs.mm.message_type",
        fields
    )

    messages = []

    for row in rows:
        identity_type_raw = row["nas_5gs.mm.type_id"]
        identity_type = int(identity_type_raw) if identity_type_raw else None

        messages.append({
            "frame": int(row["frame.number"]),
            "timestamp_relative": float(row["frame.time_relative"]),
            "timestamp_epoch": float(row["frame.time_epoch"]),
            "ip_src": row["ip.src"],
            "ip_dst": row["ip.dst"],
            "message_type": row["nas_5gs.mm.message_type"],
            "identity_type": identity_type,
            "rand": row["gsm_a.dtap.rand"] or None,
            "autn": row["gsm_a.dtap.autn"] or None,
            "res_star": row["nas_eps.emm.res"] or None
        })

    return messages    


# -- NAS CORRELATION --
def find_message(messages, message_type, before_time=None):
    candidates = [
        message
        for message in messages
        if (
            message["message_type"] == message_type
            and (
                before_time is None 
                or message["timestamp_relative"] < before_time
            )
        )
    ]

    if not candidates:
        raise RuntimeError(
            f"No message found with type {message_type}"
        )

    return max(
        candidates,
        key=lambda message: message["timestamp_relative"]
    )


def find_message_between(messages, message_type, start_time, end_time, required=False):
    candidates = [
        message
        for message in messages
        if (
            message["message_type"] == message_type
            and start_time < message["timestamp_relative"] < end_time
        )
    ]

    if not candidates:
        if required:
            raise RuntimeError(
                f"No message found with type {message_type} between {start_time} and {end_time}"
            )

        return None

    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one message with type {message_type} between {start_time} and {end_time}, found {len(candidates)}"
        )


    return candidates[0]



# -- SBI / AUSF CORRELATION -- 
def find_authentication_vector(messages, rand, autn):
    candidates = []

    for message in messages:
        body = message["body"]
        auth_data = body.get("5gAuthData")

        if not isinstance(auth_data, dict):
            continue

        if auth_data.get("rand") == rand and auth_data.get("autn") == autn:
            candidates.append(message)


    if not candidates:
        raise RuntimeError(
            "No authentication vector matched RAND and AUTN"
        )

    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one matching authentication vector, found {len(candidates)}"
        )

    return candidates[0]



def find_res_star_message(messages, res_star, after_time):
    candidates = [
        message
        for message in messages
        if (
            message["body"].get("resStar") == res_star
            and message["timestamp_relative"] > after_time
        )
    ]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda message: message["timestamp_relative"]
    )


def find_auth_result_message(messages, after_time):
    candidates = [
        message
        for message in messages
        if (
            "authResult" in message["body"]
            and message["timestamp_relative"] > after_time
        )
    ]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda message: message["timestamp_relative"]
    )


# Calcolo HRES*
def calculate_hres_star(rand, res_star):
    data = bytes.fromhex(rand + res_star)
    digest = hashlib.sha256(data).digest()

    return digest[16:].hex()







# -- Normalizzazione --
def identity_name(identity_type):
    if identity_type is None:
        return None

    return IDENTITY_TYPES.get(
        identity_type,
        f"UNKNOWN_{identity_type}"
    )


def compact_nas_message(message):
    if message is None:
        return None

    return {
        "frame": message["frame"],
        "timestamp_relative": message["timestamp_relative"],
        "timestamp_epoch": message["timestamp_epoch"],
        "ip_src": message["ip_src"],
        "ip_dst": message["ip_dst"]
    }



# -- Costruzione evento --
def build_event(pcap_file, case, identity_path, failure_source):
    messages = extract_nas_messages(pcap_file)


    authentication_vectors = extract_tcp_json_messages(
        pcap_file,
        'tcp contains "authType"'
    )

    res_star_messages = extract_tcp_json_messages(
        pcap_file,
        'tcp contains "resStar"'
    )

    auth_result_messages = extract_tcp_json_messages(
        pcap_file,
        'tcp contains "authResult"'
    )


    # Parto da "Authentication Reject" e recupero i messaggi andando a ritroso
    authentication_reject = find_message(
        messages,
        AUTHENTICATION_REJECT
    )

    authentication_response = find_message(
        messages,
        AUTHENTICATION_RESPONSE,
        authentication_reject["timestamp_relative"]
    )

    authentication_request = find_message(
        messages,
        AUTHENTICATION_REQUEST,
        authentication_response["timestamp_relative"]
    )

    authentication_vector = find_authentication_vector(
        authentication_vectors,
        authentication_request["rand"],
        authentication_request["autn"]
    )


    # Questo serve per i casi C e D
    ausf_confirmation_request = find_res_star_message(
        res_star_messages,
        authentication_response["res_star"],
        authentication_response["timestamp_relative"]
    )

    ausf_confirmation_response = None
    if ausf_confirmation_request is not None:
        ausf_confirmation_response = find_auth_result_message(
            auth_result_messages,
            ausf_confirmation_request["timestamp_relative"]
        )


    auth_data = authentication_vector["body"]["5gAuthData"]
    hxres_star = auth_data["hxresStar"]

    hres_star = calculate_hres_star(
        authentication_request["rand"],
        authentication_response["res_star"]
    )


    registration_request = find_message(
        messages,
        REGISTRATION_REQUEST,
        authentication_request["timestamp_relative"]
    )

    registration_time = registration_request["timestamp_relative"]
    authentication_time = authentication_request["timestamp_relative"]

    identity_request = find_message_between(
        messages,
        IDENTITY_REQUEST,
        registration_time,
        authentication_time
    )

    identity_response = find_message_between(
        messages,
        IDENTITY_RESPONSE,
        registration_time,
        authentication_time
    )


    event = {
        "type": "resstar_verification_failure",
        "case": case,
        "identity_path": identity_path,
        "failure_source": failure_source,

        "registration_request": {
            **compact_nas_message(registration_request),
            "identity_type": identity_name(registration_request["identity_type"])
        },

        "authentication_request": {
            **compact_nas_message(authentication_request),
            "rand": authentication_request["rand"],
            "autn": authentication_request["autn"]
        },

        "authentication_response": {
            **compact_nas_message(authentication_response),
            "res_star": authentication_response["res_star"]
        },

        "authentication_vector": {
            **compact_tcp_json_message(authentication_vector),
            "rand": auth_data["rand"],
            "hxres_star": hxres_star,
            "autn": auth_data["autn"]
        },

        "res_star_verification": {
            "hres_star": hres_star,
            "hxres_star": hxres_star,
            "match": hres_star == hxres_star
        },
        

        "authentication_reject": {
            **compact_nas_message(authentication_reject),
            "present": True
        }
    }

    if identity_request is not None:
        event["identity_request"] = {
            **compact_nas_message(identity_request),
            "requested_identity": identity_name(identity_request["identity_type"])
        }

    if identity_response is not None:
        event["identity_response"] = {
            **compact_nas_message(identity_response),
            "identity_type": identity_name(identity_response["identity_type"])
        }

    if ausf_confirmation_request is not None:
        event["ausf_confirmation_request"] = {
            **compact_tcp_json_message(ausf_confirmation_request),
            "res_star": ausf_confirmation_request["body"]["resStar"]
        }

    if ausf_confirmation_response is not None:
        event["ausf_confirmation_response"] = {
            **compact_tcp_json_message(ausf_confirmation_response),
            "auth_result": ausf_confirmation_response["body"]["authResult"]
        }

    return event



# -- EVIDENCE --
def build_evidence(pcap_file, case, identity_path, failure_source):
    event = build_event(pcap_file, case, identity_path, failure_source)

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



# -- MAIN --
def main():
    context = extractor_utils.load_extractor_context(
        BASE_DIR,
        "Extract RES* verification failure evidence"
    )

    test_config = context["config"]

    evidence = build_evidence(
        context["pcap_file"],
        test_config["case"],
        test_config["identity_path"],
        test_config["failure_source"]
    )


    output_file = context["output_file"]

    save_json(output_file, evidence)


    print(f"Evidence saved to: {output_file}")



if __name__ == "__main__":
    main()