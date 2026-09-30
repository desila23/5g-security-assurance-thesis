from pathlib import Path

from utils.evidence_utils import get_events_by_type
from utils.report_schema import normalize_report

import utils.reporter_utils as reporter_utils


BASE_DIR = Path(__file__).resolve().parent.parent



def get_frames_for_field(evidence, field_path):
    parts = field_path.split(".")

    event_type = parts[0]
    section = parts[1]

    event = get_events_by_type(
        evidence,
        event_type,
        require_single=True
    )

    if section not in ("request", "response"):
        raise RuntimeError(
            f"Unsupported section in field '{field_path}'"
        )

    section_data = event[section]
    remaining_path = parts[2:]

    # Dati contenuti nel body HTTP/2
    if "body" in remaining_path:
        return list(section_data["body_frames"])

    # La verifica MAC deriva da RAND e AUTN contenuti nel body della response
    if "mac_verification" in remaining_path:
        return list(section_data["body_frames"])

    # Status HTTP: l'evidenza è negli HEADERS della response
    if "status_code" in remaining_path:
        return [section_data["headers_frame"]]

    # Method e path sono negli HEADERS della request
    if "method" in remaining_path or "path" in remaining_path:
        return [section_data["headers_frame"]]

    return []


def build_report(test_id, case_id, context):
    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]


    initial_auth = get_events_by_type(
        evidence,
        "initial_auth",
        require_single=True
    )

    resynchronization = get_events_by_type(
        evidence,
        "resynchronization",
        require_single=True
    )

    criteria = []
    verification_results = []

    for index, (parsed_rule, verification_rule) in enumerate(
        zip(parsed_rules, verification["rules"]), start=1
    ):
        criterion_id = f"criterion_{index}"

        evidence_frames = get_frames_for_field(
            evidence,
            parsed_rule["field"]
        )

        expected_source_field = None

        if parsed_rule["expected"]["type"] == "field":
            expected_source_field = parsed_rule["expected"]["value"]

            expected_frames = get_frames_for_field(
                evidence,
                expected_source_field
            )

            evidence_frames.extend(expected_frames)

        evidence_frames = list(dict.fromkeys(evidence_frames))

        if expected_source_field:
            expected_description = expected_source_field
        else:
            expected_description = verification_rule["expected"]


        criteria.append({
            "id": criterion_id,

            "type": "comparison",

            "description": (
                f"Verification of "
                f"{parsed_rule['field']} "
                f"{parsed_rule['operator']} "
                f"{expected_description}"
            ),

            "specification": {
                "language": "DSL",

                "expression": reporter_utils.rule_to_expression(parsed_rule)
            }
        })

        verification_results.append({
                "criterion_id": criterion_id,

                "engine": "simple_verifier",

                "field": verification_rule["field"],            

                "operator": verification_rule["operator"],

                "expected": verification_rule["expected"],

                "observed": verification_rule["observed"],

                "expected_source_field": expected_source_field,

                "evidence_frames": evidence_frames,

                "verdict": verification_rule["verdict"]
            })


    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "source_test_name": "TC SYNCH FAIL HANDLING",

            "nf": "UDM",

            "description": "Verification of AKA resynchronization handling by the UDM"
        },

        "source": evidence["source"],

        "configuration": evidence["configuration"],

        "criteria": criteria,

        "verification": {
            "results": verification_results,

            "overall_verdict": verification["overall_verdict"]
        },

        "evidence": {
            "initial_auth": initial_auth,

            "resynchronization": resynchronization
        },

        "explanation": {
            "initial_auth_status": initial_auth["response"]["status_code"],

            "resynchronization_status": resynchronization["response"]["status_code"],

            "initial_rand": initial_auth["response"]["body"]["authenticationVector"]["rand"],

            "resynchronization_request_rand": resynchronization["request"]["body"]["resynchronizationInfo"]["rand"],

            "resynchronization_response_rand": resynchronization["response"]["body"]["authenticationVector"]["rand"],

            "initial_mac_valid": initial_auth["response"]["mac_verification"]["match"],

            "resynchronization_mac_valid": resynchronization["response"]["mac_verification"]["match"]
        },

        "verdict": verification["overall_verdict"]
    }


    failed_rules = [
        rule for rule in verification["rules"]
        if rule["verdict"] == "FAIL"
    ]

    if failed_rules:
        fields = ", ".join(rule["field"] for rule in failed_rules)
        summary = f"UDM resynchronization failed the following checks: {fields}."
    else:
        summary = (
            "UDM resynchronization passed all checks, including RAND "
            "correlation and both MAC verifications."
        )

    return normalize_report(report, summary)


def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR,
        "Generate UDM resynchronization report",
        build_report
    )

    observations = report["explanation"]["observations"]


    print()
    print("--- EVIDENCE REPORT ---")

    print(
        f"Test: "
        f"{report['test']['id']}"
    )

    print(
        f"Source SCAS test: "
        f"{report['test']['source_test_name']}"
    )

    print(
        f"NF: "
        f"{report['test']['nf']}"
    )

    print(
        f"Overall verdict: "
        f"{report['verdict']}"
    )

    print()
    print("Details:")

    print(
        f"- Initial auth status: "
        f"{observations['initial_auth_status']}"
    )

    print(
        f"- Resynchronization status: "
        f"{observations['resynchronization_status']}"
    )

    print(
        f"- Initial MAC valid: "
        f"{observations['initial_mac_valid']}"
    )

    print(
        f"- Resynchronization MAC valid: "
        f"{observations['resynchronization_mac_valid']}"
    )

    print(
        f"Report saved to: "
        f"{output_file}"
    )

    print("-----------------------")



if __name__ == "__main__":
    main()