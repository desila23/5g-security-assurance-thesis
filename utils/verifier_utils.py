import json
import argparse


def merge_test_config(base, overrides):
    result = dict(base)

    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_test_config(result[key], value)
        else:
            result[key] = value

    return result



def parse_arguments(description):
    parser = argparse.ArgumentParser(
        description=description
    )

    parser.add_argument(
        "--test",
        required=True,
        help="Identifier of the test to verify"
    )

    parser.add_argument(
        "--case",
        help="Optional case identifier for multi-case tests"
    )

    return parser.parse_args()


def load_test_config(base_dir, test_id, case_id=None):
    config_file = base_dir / "config" / "tests.json"

    with open(config_file, "r", encoding="utf-8") as f:
        tests = json.load(f)

    if test_id in tests:
        test_config = tests[test_id]
    else:
        mutation_file = base_dir / "config" / "mutation_tests.json"

        with open(mutation_file, "r", encoding="utf-8") as f:
            mutations = json.load(f)

        matches = [
            mutation
            for mutation in mutations.values()
            if mutation.get("mutated_test") == test_id
        ]

        if len(matches) != 1:
            raise RuntimeError(
                f"Test '{test_id}' not found in test configurations"
            )

        mutation = matches[0]
        test_config = mutation["test_config"]

        if mutation.get("inherit_baseline_config", False):
            baseline_id = mutation["baseline_test"]
            if baseline_id not in tests:
                raise RuntimeError(
                    f"Baseline test '{baseline_id}' not found in config/tests.json"
                )
            test_config = merge_test_config(tests[baseline_id], test_config)


    cases = test_config.get("cases")

    # Test normale senza casi
    if cases is None:
        if case_id is not None:
            raise RuntimeError(
                f"Test '{test_id}' does not define cases"
            )            

        return test_config


    available_cases = ", ".join(cases.keys())

    # Test multi-case: --case obbligatorio
    if case_id is None:
        raise RuntimeError(
            f"Test '{test_id}' requires --case. Available cases: {available_cases}"
        )

    if case_id not in cases:
        raise RuntimeError(
            f"Case '{case_id}' not found for test '{test_id}'. Available cases: {available_cases}"
        )

    case_config = cases[case_id]

    # Proprietà comuni del test
    resolved_config = {
        key: value
        for key, value in test_config.items()
        if key != "cases"
    }

    # Le proprietà specifiche del caso sovrascrivono quelle comuni
    resolved_config.update(case_config)

    # Per far sapere a extractor/reporter il caso selezionato
    resolved_config["case"] = case_id

    return resolved_config