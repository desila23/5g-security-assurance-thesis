import argparse
import subprocess
import sys

from contextlib import redirect_stdout
from io import StringIO

from pathlib import Path

from utils.verifier_utils import load_test_config
from utils.json_utils import load_json


BASE_DIR = Path(__file__).resolve().parent


def load_all_tests(filename):
    return load_json(BASE_DIR / "config" / filename)


def list_tests():
    tests = load_all_tests("tests.json")
    mutations = load_all_tests("mutation_tests.json")

    print("\nORIGINAL TEST\n")

    for index, (test_id, test_config) in enumerate(tests.items(), start=1):
        print(f"[{index}] {test_id}")

        cases = test_config.get("cases")
        if cases:
            for case_id in cases:
                print(
                    f"    Case {case_id}: python main.py "
                    f"--test {test_id} --case {case_id}"
                )
        else:
            print(f"    Run: python main.py --test {test_id}")

        print()

    print("MUTATED TEST\n")

    by_baseline = {}
    for mutation_id, mutation_config in mutations.items():
        baseline_id = mutation_config["baseline_test"]
        by_baseline.setdefault(baseline_id, []).append(
            (mutation_id, mutation_config)
        )

    index = 1
    for baseline_id in tests:
        entries = by_baseline.pop(baseline_id, [])
        if not entries:
            continue

        variants = {
            config["variant"]: config
            for _, config in entries
            if "variant" in config
        }
        if variants:
            print(f"[{index}] {baseline_id}")
            for variant in ("static", "temporal", "both"):
                if variant not in variants:
                    continue
                mutated_id = variants[variant]["mutated_test"]
                print(f"    {variant}: {mutated_id}")
                print(
                    f"        Run: python main.py --mutation "
                    f"{baseline_id} --variant {variant}"
                )
            print()
            index += 1
            continue

        for mutation_id, config in entries:
            print(f"[{index}] {config['mutated_test']}")
            cases = config["test_config"].get("cases")
            if cases:
                for case_id in cases:
                    print(
                        f"    Case {case_id}: python main.py "
                        f"--mutation {mutation_id} --case {case_id}"
                    )
            else:
                print(f"    Run: python main.py --mutation {mutation_id}")
            print()
            index += 1

    if by_baseline:
        raise RuntimeError(
            "Mutazioni con baseline assente da config/tests.json: "
            + ", ".join(by_baseline)
        )


def run_command(command, label, verbose=False):
    result = subprocess.run(
        command,
        cwd=BASE_DIR,
        capture_output=not verbose,
        text=True,
    )

    if result.returncode != 0:
        print(
            f"Errore durante {label} (codice {result.returncode})",
            file=sys.stderr,
        )
        if result.stdout:
            print(
                result.stdout,
                file=sys.stderr,
                end="" if result.stdout.endswith("\n") else "\n",
            )
        if result.stderr:
            print(
                result.stderr,
                file=sys.stderr,
                end="" if result.stderr.endswith("\n") else "\n",
            )
        raise subprocess.CalledProcessError(result.returncode, command)


def run_module(module_name, test_id=None, case_id=None, verbose=False):
    command = [
        sys.executable,
        "-m",
        module_name,
    ]

    if test_id is not None:
        command.extend(["--test", test_id])

    if case_id is not None:
        command.extend(["--case", case_id])

    if verbose:
        print(f"\n> Running {module_name}")

    run_command(command, module_name, verbose=verbose)


def run_pipeline(test_id, case_id=None, verbose=False):
    test_config = load_test_config(BASE_DIR, test_id, case_id)

    test_label = test_id
    if case_id is not None:
        test_label += f" - Case {case_id}"

    print(f"\nTest: {test_label}", flush=True)

    extractor = test_config.get("extractor")
    if extractor:
        run_module(extractor, test_id, case_id, verbose)

    pre_verifiers = test_config.get("pre_verifiers", [])
    for verifier in pre_verifiers:
        run_module(verifier, test_id, case_id, verbose)

    verifier = test_config.get("verifier")
    if verifier:
        run_module(verifier, test_id, case_id, verbose)

    temporal_config = test_config.get("temporal")
    if temporal_config:
        temporal_verifier = temporal_config.get("verifier")
        if temporal_verifier:
            run_module(temporal_verifier, test_id, case_id, verbose)

    reporter = test_config.get("reporter")
    if reporter:
        run_module(reporter, test_id, case_id, verbose)

    verification = load_json(BASE_DIR / test_config["output"])
    report = load_json(BASE_DIR / test_config["report"])

    leaf_rules = [
        rule
        for rule in iter_rule_results(verification["rules"])
        if rule["operator"] != "IF"
    ]
    passed = sum(rule["verdict"] == "PASS" for rule in leaf_rules)
    failed = sum(rule["verdict"] == "FAIL" for rule in leaf_rules)


    print(f"  DSL: {verification['overall_verdict']} ({passed} PASS, {failed} FAIL)")
    if temporal_config:
        temporal = load_json(BASE_DIR / temporal_config["output"])
        print(f"  Temporal: {temporal['overall_verdict']}")
    print(f"  Overall verdict: {report['verdict']}")

    if report["verdict"] == "FAIL":
        print_failed_checks(report)

    print(f"  Report file: {test_config['report']}")



def iter_rule_results(rules):
    for rule in rules:
        yield rule
        yield from iter_rule_results(rule.get("rules", []))


def iter_failed_report_results(results):
    for entry in results:
        result = entry.get("result", entry)
        details = result.get("details", result)
        children = details.get("rules", [])
        if children:
            yield from iter_failed_report_results(children)
        elif result.get("verdict") == "FAIL":
            yield result


def format_frames(frames):
    if not frames:
        return ""
    return " | frames: " + ", ".join(str(frame) for frame in frames)


def print_failed_checks(report):
    results = list(iter_failed_report_results(
        report.get("verification", {}).get("results", [])
    ))
    criteria = {item["id"]: item for item in report.get("criteria", [])}

    print("  Failed checks:")
    if not results:
        print("    - See report for details")
        return

    for result in results:
        frames = format_frames(result.get("evidence_frames", []))
        details = result.get("details", result)

        if result.get("engine") == "Monpoly":
            criterion = criteria.get(result.get("criterion_id"), {})
            description = criterion.get("description", "Temporal criterion")
            timer = criterion.get("timer", {})
            interval = details.get("observed_interval_seconds")

            print(f"    - Temporal: {description}{frames}")
            if timer and interval is not None:
                print(
                    f"      {timer['name']}: {timer['duration_ms'] / 1000:g} s"
                    f" | observed interval: {interval:g} s"
                )
            continue

        field = details.get("field", "Unknown field")
        operator = details.get("operator", "?")
        print(f"    - {field} [{operator}]{frames if operator != 'UNIQUE' else ''}")

        if operator == "UNIQUE":
            for duplicate in details.get("duplicates", []):
                value = duplicate["value"]
                if isinstance(value, dict):
                    value = ", ".join(f"{key}={item}" for key, item in value.items())
                print(
                    f"      Duplicate: {value}"
                    f"{format_frames(duplicate['frames'])}"
                )
            continue

        expected_source = details.get("expected_source_field")
        expected_label = (
            f"Expected from {expected_source}"
            if expected_source else "Expected"
        )
        print(
            f"      Observed: {details.get('observed')}"
            f" | {expected_label}: {details.get('expected')}"
        )


def check_target_rule(test_id, config, target, expected_verdict):
    verification = load_json(BASE_DIR / config["output"])
    matches = [
        rule
        for rule in iter_rule_results(verification["rules"])
        if rule["field"] == target["field"]
        and rule["operator"] == target["operator"]
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"{test_id}: attesa una sola regola bersaglio "
            f"{target['field']} {target['operator']}; trovate {len(matches)}"
        )

    observed = matches[0]["verdict"]
    if observed != expected_verdict:
        raise RuntimeError(
            f"{test_id}: regola bersaglio attesa {expected_verdict}, "
            f"ottenuta {observed}"
        )


def check_expected_components(test_id, config, expected_components):
    static_result = load_json(BASE_DIR / config["output"])
    temporal_result = load_json(BASE_DIR / config["temporal"]["output"])

    observed = {
        "static": static_result["overall_verdict"],
        "temporal": temporal_result["overall_verdict"],
    }

    if set(expected_components) != set(observed):
        raise RuntimeError(f"{test_id}: componenti attese non valide")

    for component, expected_verdict in expected_components.items():
        if observed[component] != expected_verdict:
            raise RuntimeError(
                f"{test_id}: {component} atteso {expected_verdict}, "
                f"ottenuto {observed[component]}"
            )


def run_mutation(test_id, variant=None, case_id=None, verbose=False, baseline_already_run=False):
    mutations = load_all_tests("mutation_tests.json")

    if variant is None:
        mutation = mutations.get(test_id)
    else:
        matches = [
            config
            for config in mutations.values()
            if config["baseline_test"] == test_id
            and config.get("variant") == variant
        ]

        if len(matches) != 1:
            raise RuntimeError(
                f"Variante '{variant}' non disponibile per {test_id}"
            )

        mutation = matches[0]

    if mutation is None:
        raise RuntimeError(f"Mutation test not configurated: {test_id}")

    baseline_id = mutation["baseline_test"]
    mutated_id = mutation["mutated_test"]
    expected = mutation["expected_verdicts"]

    target = mutation.get("target_rule")
    if "target_rules" in mutation:
        if case_id not in mutation["target_rules"]:
            raise RuntimeError(
                f"Regola bersaglio non configurata per il caso {case_id}"
            )
        target = mutation["target_rules"][case_id]

    baseline_config = load_test_config(BASE_DIR, baseline_id, case_id)
    mutated_config = load_test_config(BASE_DIR, mutated_id, case_id)

    if not baseline_already_run:
        run_pipeline(baseline_id, case_id, verbose)

    baseline_evidence = load_json(BASE_DIR / baseline_config["evidence"])
    baseline_report = load_json(BASE_DIR / baseline_config["report"])

    if baseline_report["verdict"] != expected["baseline"]:
        raise RuntimeError(
            f"{baseline_id}: atteso {expected['baseline']}, "
            f"ottenuto {baseline_report['verdict']}"
        )

    if target is not None:
        check_target_rule(
            baseline_id, baseline_config, target, target["baseline"]
        )

    print(f"\nMutator: {mutation['mutator']}", flush=True)
    run_command(
        [
            sys.executable,
            "-m",
            mutation["mutator"],
            "--source",
            str(BASE_DIR / baseline_config["pcap"]),
            "--evidence",
            str(BASE_DIR / baseline_config["evidence"]),
            "--output",
            str(BASE_DIR / mutated_config["pcap"]),
            "--overwrite",
        ],
        mutation["mutator"],
        verbose=verbose,
    )
    print(f"  Output PCAP: {mutated_config['pcap']}")

    run_pipeline(mutated_id, case_id, verbose)

    mutated_evidence = load_json(BASE_DIR / mutated_config["evidence"])
    mutated_report = load_json(BASE_DIR / mutated_config["report"])

    if mutated_report["verdict"] != expected["mutated"]:
        raise RuntimeError(
            f"{mutated_id}: atteso {expected['mutated']}, "
            f"ottenuto {mutated_report['verdict']}"
        )

    if target is not None:
        check_target_rule(
            mutated_id, mutated_config, target, target["mutated"]
        )

    if "expected_components" in mutation:
        check_expected_components(
            mutated_id,
            mutated_config,
            mutation["expected_components"],
        )

    if (
        baseline_evidence["source"]["sha256"]
        == mutated_evidence["source"]["sha256"]
    ):
        raise RuntimeError("Il PCAP mutato coincide con la baseline")

    label = f"Mutation test: {test_id}"
    if case_id:
        label += f" - Case {case_id}"
    print(f"\n{label}")

    if variant:
        print(f"  Variant: {variant}")

    print(
        f"  Verdict: {expected['baseline']} "
        f"-> {expected['mutated']}"
    )

    if target is not None:
        print(
            f"  Target rule: {target['field']} "
            f"({target['baseline']} -> {target['mutated']})"
        )

    if "expected_components" in mutation:
        components = mutation["expected_components"]
        print(
            f"  Static: {components['static']} "
            f"| Temporal: {components['temporal']}"
        )

    print("  Result: OK")


def run_batch_item(label, expected, report_file, action):
    output = StringIO()

    try:
        with redirect_stdout(output):
            action()

        observed = load_json(BASE_DIR / report_file)["verdict"]
        ok = observed == expected
        error = None
    except Exception as exc:
        observed = "ERROR"
        ok = False
        error = exc

    status = "OK" if ok else "ERROR"
    print(f"{label}: observed {observed} | expected {expected} | {status}")

    if not ok:
        print(output.getvalue(), end="")
        if error is not None:
            print(f"{type(error).__name__}: {error}", file=sys.stderr)

    return ok


def run_all():
    tests = load_all_tests("tests.json")
    mutations = load_all_tests("mutation_tests.json")

    baseline_expected = {}
    for mutation in mutations.values():
        test_id = mutation["baseline_test"]
        expected = mutation["expected_verdicts"]["baseline"]

        if test_id in baseline_expected and baseline_expected[test_id] != expected:
            raise RuntimeError(f"Conflicting baseline verdicts for {test_id}")

        baseline_expected[test_id] = expected

    missing = set(tests) - set(baseline_expected)
    if missing:
        raise RuntimeError(
            "Missing expected baseline verdict for: " + ", ".join(sorted(missing))
        )

    passed = 0
    total = 0
    successful_baselines = set()

    print("\nORIGINAL TESTS")

    for test_id, test_config in tests.items():
        cases = test_config.get("cases") or {None: None}

        for case_id in cases:
            config = load_test_config(BASE_DIR, test_id, case_id)
            label = test_id + (f" [case {case_id}]" if case_id else "")

            ok = run_batch_item(
                label,
                baseline_expected[test_id],
                config["report"],
                lambda t=test_id, c=case_id: run_pipeline(t, c),
            )

            total += 1
            passed += ok
            if ok:
                successful_baselines.add((test_id, case_id))

    print("\nMUTATION TESTS")

    for test_id in tests:
        entries = [
            (mutation_id, mutation)
            for mutation_id, mutation in mutations.items()
            if mutation["baseline_test"] == test_id
        ]
        order = {"static": 0, "temporal": 1, "both": 2}
        entries.sort(key=lambda item: order.get(item[1].get("variant"), 3))

        for mutation_id, mutation in entries:
            variant = mutation.get("variant")
            cases = mutation["test_config"].get("cases") or {None: None}

            for case_id in cases:
                label = mutation["mutated_test"]
                if case_id:
                    label += f" [case {case_id}]"

                total += 1
                if (test_id, case_id) not in successful_baselines:
                    print(f"{label}: SKIPPED | baseline did not match its expected verdict")
                    continue

                config = load_test_config(
                    BASE_DIR, mutation["mutated_test"], case_id
                )
                requested_id = test_id if variant else mutation_id

                ok = run_batch_item(
                    label,
                    mutation["expected_verdicts"]["mutated"],
                    config["report"],
                    lambda t=requested_id, v=variant, c=case_id: run_mutation(
                        t, v, c, baseline_already_run=True
                    ),
                )
                passed += ok

    print(f"\nCompleted: {passed}/{total} scenarios")

    if passed != total:
        raise SystemExit(1)



def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run the 5G Security Assurance verification pipeline"
    )

    selection = parser.add_mutually_exclusive_group()

    selection.add_argument(
        "--test",
        help="Identifier of the test to execute",
    )
    selection.add_argument(
        "--mutation",
        help="Run mutation testing for the specified test",
    )
    selection.add_argument(
        "--list",
        action="store_true",
        help="List available tests",
    )

    selection.add_argument(
        "--all",
        action="store_true",
        help="Run all original tests and mutation scenarios"
    )


    parser.add_argument(
        "--case",
        help="Optional case identifier for multi-case tests",
    )
    parser.add_argument(
        "--variant",
        choices=("static", "temporal", "both"),
        help="Mutation variant to run",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show the detailed output of extractors, verifiers and reporters",
    )

    args = parser.parse_args()

    if args.variant and not args.mutation:
        parser.error("--variant richiede --mutation")

    return args


def main():
    args = parse_arguments()

    if args.list:
        list_tests()
        return

    if args.all:
        run_all()
        return       

    if args.mutation:
        run_mutation(args.mutation, args.variant, args.case, args.verbose)
        return

    if args.test:
        run_pipeline(args.test, args.case, args.verbose)
        return

    list_tests()
    raise RuntimeError("Specify a test using --test or --mutation")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)