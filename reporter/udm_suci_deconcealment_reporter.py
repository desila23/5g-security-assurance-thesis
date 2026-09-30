from pathlib import Path

import utils.reporter_utils as reporter_utils
from utils.report_schema import normalize_report


BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_TYPE = "suci_deconcealment"



def build_report(test_id, case_id, context):
    evidence = context["evidence"]
    verification = context["verification"]
    parsed_rules = context["rules"]
    event = context["event"]


    rule_1 = verification["rules"][0]
    rule_2 = verification["rules"][1]

    parsed_rule_1 = parsed_rules[0]
    parsed_rule_2 = parsed_rules[1]

    criterion_1_id = "criterion_1"
    criterion_2_id = "criterion_2"


    report = {
        "schema_version": "1.0",

        "metadata": evidence["metadata"],

        "test": {
            "id": test_id,

            "source_test_name": "TC_DE-CONCEAL_SUPI_from_SUCI_UDM",

            "scas_specification": "3GPP TS 33.514",

            "scas_clause": "4.2.1.1",

            "nf": "UDM",

            "description": "Verification of SUCI de-concealment by the UDM"
        },

        "source": evidence["source"],

        "configuration": evidence["configuration"],

        "criteria": [
            {
                "id": criterion_1_id,

                "type": "comparison",

                "description": "The UDM response to the generate-auth-data request must have HTTP status 200",

                "specification": {
                    "language": "DSL",

                    "expression": reporter_utils.rule_to_expression(parsed_rule_1)
                }
            },

            {
                "id": criterion_2_id,

                "type": "comparison",

                "description": "The SUPI returned by the UDM must match the original SUPI known to the tester",

                "specification": {
                    "language": "DSL",

                    "expression": reporter_utils.rule_to_expression(parsed_rule_2)
                }
            }
        ],

        "verification": {
            "results": [
                {
                    "criterion_id": criterion_1_id,

                    "engine": "simple_verifier",

                    "field": rule_1["field"],

                    "operator": rule_1["operator"],

                    "expected": rule_1["expected"],

                    "observed": rule_1["observed"],

                    "evidence_frames": [
                        event["response"]["headers_frame"]
                    ],

                    "verdict": rule_1["verdict"]
                },

                {
                    "criterion_id": criterion_2_id,

                    "engine": "simple_verifier",

                    "field": rule_2["field"],

                    "operator": rule_2["operator"],

                    "expected": rule_2["expected"],

                    "observed": rule_2["observed"],

                    "evidence_frames": event["response"]["body_frames"],

                    "verdict": rule_2["verdict"]
                }
            ],

            "overall_verdict": verification["overall_verdict"]
        },

        "evidence": {
            "type": EVENT_TYPE,

            "test_input": event["test_input"],

            "request": event["request"],

            "response": event["response"]
        },

        "explanation": {
            "expected_http_status": rule_1["expected"],

            "observed_http_status": rule_1["observed"],

            "original_supi": event["test_input"]["original_supi"],

            "returned_supi": event["response"]["body"]["supi"]
        },

        "verdict": verification["overall_verdict"]
    }


    original_supi = event["test_input"]["original_supi"]
    returned_supi = event["response"]["body"]["supi"]
    http_status = event["response"]["status_code"]
    summary = (
        f"UDM returned HTTP {http_status} and SUPI {returned_supi}; "
        f"expected HTTP {rule_1['expected']} and SUPI {original_supi}."
    )

    return normalize_report(report, summary)    



def main():
    report, output_file = reporter_utils.run_reporter(
        BASE_DIR,
        "Generate UDM SUCI de-concealment report",
        build_report,
        EVENT_TYPE,        
    )


    print()
    print("--- UDM SUCI EVIDENCE REPORT ---")

    print(
        f"Test: {report['test']['id']}"
    )

    print(
        f"Source SCAS test: {report['test']['source_test_name']}"
    )

    print(
        f"NF: {report['test']['nf']}"
    )

    print(
        f"Overall verdict: {report['verification']['overall_verdict']}"
    )

    print(
        f"Report saved to: {output_file}"
    )

    print("-----------------------")



if __name__ == "__main__":
    main()