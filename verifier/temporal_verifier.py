import subprocess

from pathlib import Path

from utils.verifier_utils import parse_arguments, load_test_config
from utils.evidence_utils import get_events_by_type
from utils.json_utils import load_json, save_json
from dsl.parse_rule import get_mfotl_formula


# TEMPO
def seconds_to_milliseconds(timestamp):
    return round(timestamp * 1000)



# FORMULA MFOTL
def build_monpoly_formula(formula_template, timer_duration_ms):
    return formula_template.replace(
        "{TIMER_MS}", 
        str(timer_duration_ms)
    )


def write_monpoly_formula(formula_template, formula_output_file, timer_duration_ms):
        formula = build_monpoly_formula(formula_template, timer_duration_ms)

        formula_output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(formula_output_file, "w", encoding="utf-8") as f:
            f.write(formula + "\n")



# MONPOLY LOG
def add_log_event(events, timestamp, event_name):
    if timestamp is None:
        return

    events.append({
        "timestamp": seconds_to_milliseconds(timestamp),
        "event": event_name
    })


def generate_amf_sync_failure_log(evidence):
    event = get_events_by_type(
        evidence,
        "amf_sync_failure",
        require_single=True
    )

    log_events = []

    # SYNCHRONIZATION FAILURE
    sync_failure = event.get("synchronization_failure")

    if sync_failure is not None:
        add_log_event(
            log_events,
            sync_failure.get("timestamp_relative"),
            "SyncFailure()"
        )


    # RESYNCHRONIZATION REQUEST
    resync_request = event.get("resynchronization_request")

    if (
        resync_request is not None 
        and resync_request.get("present") is True
    ):
        add_log_event(
            log_events,
            resync_request.get("timestamp_relative"),
            "ResynchronizationRequest()"
        )


    # AUSF AUTHENTICATION RESPONSE
    ausf_response = event.get("ausf_authentication_response")

    if (
        ausf_response is not None
        and ausf_response.get("present") is True
    ):
        add_log_event(
            log_events,
            ausf_response.get("timestamp_relative"),
            "AusfAuthenticationResponse()"
        )


    # SUBSEQUENT AUTHENTICATION REQUEST
    auth_request = event.get("subsequent_authentication_request")

    if (
        auth_request is not None
        and auth_request.get("present") is True
    ):
        add_log_event(
            log_events,
            auth_request.get("timestamp_relative"),
            "AuthenticationRequest()"
        )


    # Ordino gli eventi temporalmente
    log_events.sort(key=lambda item: item["timestamp"])

    lines = [
        f"@{item['timestamp']} {item['event']}"
        for item in log_events
    ]

    return "\n".join(lines) + "\n"



def write_monpoly_log(log_content, log_file):
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_content)



# ESECUZIONE DI MONPOLY
def run_monpoly(signature_file, formula_file, log_file):
    command = [
        "monpoly",
        "-sig", str(signature_file),
        "-formula", str(formula_file),
        "-log", str(log_file),
        "-negate"        
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout.strip()


# VERIFICATION
def build_temporal_verification(monpoly_output):
    violation_found = bool(monpoly_output)

    return {
        "engine": "Monpoly",
        "verification_mode": "negated_policy",
        "violation_found": violation_found,
        "monpoly_output": monpoly_output,
        "overall_verdict": "FAIL" if violation_found else "PASS"        
    }



def main():
    args = parse_arguments(
        "Verify temporal MFOTL criteria using MonPoly"
    )

    BASE_DIR = Path(__file__).resolve().parent.parent

    test_config = load_test_config(BASE_DIR, args.test)

    if "temporal" not in test_config:
        raise RuntimeError(
            f"Test '{args.test}' has no temporal configuration"
        )

    temporal_config = test_config["temporal"]

    evidence_file = BASE_DIR / test_config["evidence"]
    signature_file = BASE_DIR / temporal_config["signature"]
    generated_formula_file = BASE_DIR / temporal_config["generated_formula"]
    log_file = BASE_DIR / temporal_config["log"]
    output_file = BASE_DIR / temporal_config["output"]

    timer_duration_ms = temporal_config["timer"]["duration_ms"]

    formula_template = get_mfotl_formula(
        BASE_DIR / test_config["rules"],
        test_config["case"]
    )

    # Genero formula MFOTL  
    write_monpoly_formula(
        formula_template, 
        generated_formula_file, 
        timer_duration_ms
    )


    evidence = load_json(evidence_file)

    # Genero log MONPOLY
    log_content = generate_amf_sync_failure_log(evidence)

    write_monpoly_log(log_content, log_file)


    # Eseguo MONPOLY
    monpoly_output = run_monpoly(
        signature_file,
        generated_formula_file,
        log_file
    )

    # Risultato
    verification = build_temporal_verification(monpoly_output)

    save_json(output_file, verification)


    print(
        f"Temporal verification saved to: {output_file}"
    )

    print(
        f"Overall verdict: {verification['overall_verdict']}"
    )


if __name__ == "__main__":
    main()