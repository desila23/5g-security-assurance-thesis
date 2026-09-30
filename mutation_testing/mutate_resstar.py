from utils.evidence_utils import get_events_by_type
from utils.mutation_utils import load_mutation_context
from utils.tcp_json_mutation_utils import replace_tcp_json_value


def main():
    source, evidence, output = load_mutation_context()

    event = get_events_by_type(
        evidence,
        "resstar_verification_failure",
        require_single=True,
    )

    case = event["case"]
    failure_source = event["failure_source"]

    if failure_source == "local":
        vector = event["authentication_vector"]
        old = vector["hxres_star"]
        new = event["res_star_verification"]["hres_star"]
        frame = vector["frame"]
        field = "hxresStar"

        if old == new:
            raise RuntimeError("HRES* e HXRES* coincidono già")

    elif failure_source == "ausf":
        response = event["ausf_confirmation_response"]
        old = response["auth_result"]
        new = "AUTHENTICATION_SUCCESS"
        frame = response["frame"]
        field = "authResult"

        if old != "AUTHENTICATION_FAILURE":
            raise RuntimeError(f"authResult iniziale inatteso: {old}")

    else:
        raise RuntimeError(f"Origine del fallimento non supportata: {failure_source}")

    offset = replace_tcp_json_value(
        source, output, frame, field, old, new
    )

    print(f"PCAP creato: {output}")
    print(f"Caso {case}, frame {frame}, posizione {offset}")
    print(f"{field}: {old} -> {new}")


if __name__ == "__main__":
    main()