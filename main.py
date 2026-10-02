import argparse
import subprocess
import sys

from contextlib import redirect_stdout
from io import StringIO

from pathlib import Path

from utils.verifier_utils import load_test_config
from utils.json_utils import load_json
from utils.external_binding_utils import load_external_bindings

from traffic.tshark_reader import load_tshark_ek
from traffic.http2_normalizer import normalize_http2
from traffic.nas_normalizer import normalize_nas_events
from traffic.resolvers.sbi_resolver import resolve_sbi_message_types
from traffic.pfcp_normalizer import normalize_pfcp_events

from pipeline.collect_pipeline import run_collect_verification

from dsl.parse_rule import get_mfotl_formula

from verifier.temporal_verifier import (
    generate_temporal_log_from_match,
    write_monpoly_formula,
    write_monpoly_log,
    run_monpoly,
    build_temporal_verification,
)

from pipeline.sequence_pipeline import run_sequence_verification

from reporter.generic_reporter import save_generic_report


BASE_DIR = Path(__file__).resolve().parent


def load_all_tests(filename):
    return load_json(BASE_DIR / "config" / filename)



def iter_mutation_scenarios(mutations):
    """
    Restituisce tutte le mutation in forma uniforme.

    Supporta:
        - formato legacy flat;
        - nuovo formato con variants.
    """

    for mutation_id, mutation_group in mutations.items():

        variants = mutation_group.get("variants")

        if variants is None:
            yield mutation_id, mutation_group
            continue

        common_config = {
            key: value
            for key, value in mutation_group.items()
            if key != "variants"
        }

        for variant, variant_config in variants.items():
            mutation = {
                **common_config,
                **variant_config,
                "variant": variant,
            }

            yield mutation_id, mutation


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

    for mutation_id, mutation_config in iter_mutation_scenarios(
        mutations
    ):
        baseline_id = mutation_config["baseline_test"]

        by_baseline.setdefault(
            baseline_id,
            []
        ).append(
            (mutation_id, mutation_config)
        )


    variant_order = {
        "static": 0,
        "temporal": 1,
        "both": 2,
        "fail": 3,
        "inconclusive": 4,
    }


    index = 1

    for baseline_id in tests:
        entries = by_baseline.pop(
            baseline_id,
            []
        )

        if not entries:
            continue

        entries.sort(
            key=lambda item: variant_order.get(
                item[1].get("variant"),
                99,
            )
        )

        variant_entries = [
            (mutation_id, config)
            for mutation_id, config in entries
            if config.get("variant") is not None
        ]

        non_variant_entries = [
            (mutation_id, config)
            for mutation_id, config in entries
            if config.get("variant") is None
        ]

        if variant_entries:
            print(f"[{index}] {baseline_id}")

            for _, config in variant_entries:
                variant = config["variant"]
                mutated_id = config["mutated_test"]

                print(
                    f"    {variant}: {mutated_id}"
                )

                print(
                    f"        Run: python main.py "
                    f"--mutation {baseline_id} "
                    f"--variant {variant}"
                )

            print()
            index += 1

        for mutation_id, config in non_variant_entries:
            print(
                f"[{index}] "
                f"{config['mutated_test']}"
            )

            cases = (
                config["test_config"].get("cases")
            )

            if cases:
                for case_id in cases:
                    print(
                        f"    Case {case_id}: "
                        f"python main.py "
                        f"--mutation {mutation_id} "
                        f"--case {case_id}"
                    )

            else:
                print(
                    f"    Run: python main.py "
                    f"--mutation {mutation_id}"
                )

            print()
            index += 1


    if by_baseline:
        raise RuntimeError(
            "Mutazioni con baseline assente "
            "da config/tests.json: "
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


# COMPATIBILITÀ LEGACY:
# Supporto temporaneo per i test non ancora migrati alla nuova pipeline basata su SEQUENCE. 
# Questo ramo verrà rimosso al termine della migrazione.
def run_pipeline(test_id, case_id=None, verbose=False, test_config=None):
    if test_config is None:
        test_config = load_test_config(BASE_DIR, test_id, case_id)

    pipeline_type = test_config.get("pipeline", "legacy")

    if pipeline_type == "sequence":
        return run_sequence_test(test_id, test_config, verbose)

    if pipeline_type == "collect":
        return run_collect_test(test_id, test_config, verbose)

    # COMPATIBILITÀ LEGACY:
    # Mantiene il flusso originale:
    #      extractor -> verifier -> temporal verifier -> reporter.
    # Serve solo per i test non ancora migrati alla nuova architettura e verrà rimosso al termine della migrazione.
    return run_legacy_pipeline(
        test_id,
        test_config,
        case_id,
        verbose
    )


def run_sequence_test(test_id, test_config, verbose=False):
    print(f"\nTest: {test_id}", flush=True)

    pcap_file = BASE_DIR / test_config["pcap"]
    rule_file = BASE_DIR / test_config["rules"]

    traffic_config = test_config.get(
        "traffic",
        {},
    )


    events = []

    traffic_sources = traffic_config.get("sources", [])

    for source in traffic_sources:
        source_type = source["type"]

        packets = load_tshark_ek(
            pcap_file,
            display_filter=source.get("display_filter"),
            decode_as=source.get("decode_as", []),
        )

        if source_type == "http2":
            source_events = normalize_http2(packets)

            source_events = resolve_sbi_message_types(source_events)

        elif source_type == "nas":
            source_events = normalize_nas_events(packets)

        else:
            raise ValueError(
                f"Unsupported traffic source type: {source_type}"
            )

        events.extend(source_events)


    events = [
        event for event in events
        if event.message_type is not None
    ]

    events.sort(
        key=lambda event: (
            event.timestamp,
            event.frame_number,
        )
    )

    correlation_mode = traffic_config.get(
        "correlation_mode",
        "grouped",
    )

    external_bindings = load_external_bindings(BASE_DIR, test_config.get("external_bindings"))

    result = run_sequence_verification(
        events,
        str(rule_file),
        correlation_mode=correlation_mode,
        external_bindings=external_bindings
    )


    #---------------------------------------
    # VERIFICA TEMPORALE    
    #---------------------------------------
    
    temporal_verification = None

    temporal_config = test_config.get("temporal")

    if temporal_config and result.match is not None:

        temporal_rule_file = BASE_DIR / test_config.get(
            "temporal_rules",
            test_config["rules"],
        )

        timer_duration_ms = temporal_config["timer"]["duration_ms"]

        event_mapping = temporal_config["event_mapping"]

        signature_file = (BASE_DIR / temporal_config["signature"])

        generated_formula_file = (BASE_DIR / temporal_config["generated_formula"])

        log_file = (BASE_DIR / temporal_config["log"])

        formula_template = get_mfotl_formula(
            temporal_rule_file,
            test_config["case"],
        )

        write_monpoly_formula(
            formula_template,
            generated_formula_file,
            timer_duration_ms,
        )

        log_content = generate_temporal_log_from_match(
            result.match,
            event_mapping,
        )

        write_monpoly_log(log_content, log_file)

        monpoly_output = run_monpoly(
            signature_file,
            generated_formula_file,
            log_file,
        )

        temporal_verification = build_temporal_verification(monpoly_output)


    # Combino il risultato statico con quello temporale
    if temporal_verification is not None:

        result.details["temporal"] = temporal_verification

        if temporal_verification["overall_verdict"] == "FAIL":
            result.verdict = "FAIL"


    report_file = BASE_DIR / test_config["report"]

    report = save_generic_report(
        test_id,
        test_config,
        result,
        report_file,
        BASE_DIR
    )


    static_verdict = (
        result.verification.get("overall_verdict")
        if result.verification
        else None
    )

    temporal_verdict = (
        temporal_verification.get("overall_verdict")
        if temporal_verification
        else None
    )

    print(f"  Static verdict:   {static_verdict or 'N/A'}")
    print(f"  Temporal verdict: {temporal_verdict or 'N/A'}")
    print(f"  Overall verdict:  {result.verdict}")
    print(f"  Report file:      {test_config['report']}")

    if verbose and result.match:
        print("  Bindings:")

        for alias, event in result.match.bindings.items():
            print(
                f"    {alias}: {event.message_type} (frame {event.frame_number})"
            )

    if verbose:
        print(
            f"  Details: {result.details}"
        )

        if result.verification:
            print(
                f"  Verification: {result.verification}"
            )

    return result, report


def run_collect_test(
    test_id,
    test_config,
    verbose=False
):
    print(f"\nTest: {test_id}", flush=True)

    pcap_file = BASE_DIR / test_config["pcap"]
    rule_file = BASE_DIR / test_config["rules"]

    traffic_config = test_config.get(
        "traffic",
        {},
    )

    events = []

    traffic_sources = traffic_config.get(
        "sources",
        []
    )

    for source in traffic_sources:
        source_type = source["type"]

        packets = load_tshark_ek(
            pcap_file,
            display_filter=source.get(
                "display_filter"
            ),
            decode_as=source.get(
                "decode_as",
                []
            ),
        )

        if source_type == "pfcp":
            source_events = normalize_pfcp_events(
                packets
            )

        else:
            raise ValueError(
                "Unsupported traffic source type "
                f"for collect pipeline: "
                f"{source_type}"
            )

        events.extend(source_events)

    events = [
        event for event in events
        if event.message_type is not None
    ]

    events.sort(
        key=lambda event: (
            event.timestamp,
            event.frame_number
        )
    )

    result = run_collect_verification(
        events,
        str(rule_file)
    )

    report_file = (
        BASE_DIR / test_config["report"]
    )

    save_generic_report(
        test_id,
        test_config,
        result,
        report_file,
        BASE_DIR
    )

    static_verdict = (
        result.verification.get(
            "overall_verdict"
        )
        if result.verification
        else None
    )

    print(
        "  Static verdict:   "
        f"{static_verdict or 'N/A'}"
    )

    print(
        "  Temporal verdict: N/A"
    )

    print(
        "  Overall verdict:  "
        f"{result.verdict}"
    )

    print(
        "  Report file:      "
        f"{test_config['report']}"
    )

    return result


def run_legacy_pipeline(
    test_id, 
    test_config,
    case_id=None, 
    verbose=False
):
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


def check_target_rule(
    test_id,
    config,
    target,
    expected_verdict,
):
    if config.get("pipeline") in {"sequence", "collect"}:
        report = load_json(BASE_DIR / config["report"])

        rules = []

        for result in report["verification"]["results"]:
            details = result.get(
                "details",
                result
            )

            rules.append({
                "field": details.get("field"),
                "operator": details.get("operator"),
                "verdict": result["verdict"]
            })

    # COMPATIBILITÀ LEGACY:
    # I test legacy salvano i risultati delle regole in un file di verifica separato. 
    # La nuova pipeline usa invece il report unificato.
    # Rimuovere questo ramo quando tutti i test useranno il nuovo formato.
    else:
        verification = load_json(BASE_DIR / config["output"])

        rules = list(
            iter_rule_results(
                verification["rules"]
            )
        )

    matches = [
        rule
        for rule in rules
        if rule["field"] == target["field"]
        and rule["operator"] == target["operator"]
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"{test_id}: attesa una sola regola bersaglio "
            f"{target['field']} {target['operator']}; "
            f"trovate {len(matches)}"
        )

    observed = matches[0]["verdict"]

    if observed != expected_verdict:
        raise RuntimeError(
            f"{test_id}: regola bersaglio attesa "
            f"{expected_verdict}, ottenuta {observed}"
        )


def check_expected_components(
    test_id,
    config,
    expected_components,
):
    if config.get("pipeline") in {"sequence", "collect"}:
        report = load_json(BASE_DIR / config["report"])

        static_results = [
            result for result in report["verification"]["results"]
            if result["engine"] == "binding_verifier"
        ]

        temporal_results = [
            result for result in report["verification"]["results"]
            if result["engine"] == "Monpoly"
        ]

        static_verdict = (
            "FAIL" if any(
                result["verdict"] == "FAIL"
                for result in static_results
            )
            else "PASS"
        )

        if temporal_results:
            temporal_verdict = (
                "FAIL" if any(
                    result["verdict"] == "FAIL"
                    for result in temporal_results
                )
                else "PASS"
            )
        else:
            temporal_verdict = None

        observed = {
            "static": static_verdict,
            "temporal": temporal_verdict,
        }

    # COMPATIBILITÀ LEGACY
    else:
        static_result = load_json(
            BASE_DIR / config["output"]
        )

        temporal_result = load_json(
            BASE_DIR
            / config["temporal"]["output"]
        )

        observed = {
            "static": static_result[
                "overall_verdict"
            ],
            "temporal": temporal_result[
                "overall_verdict"
            ],
        }

    if set(expected_components) != set(observed):
        raise RuntimeError(
            f"{test_id}: componenti attese non valide"
        )

    for component, expected_verdict in (
        expected_components.items()
    ):
        if observed[component] != expected_verdict:
            raise RuntimeError(
                f"{test_id}: {component} atteso "
                f"{expected_verdict}, "
                f"ottenuto {observed[component]}"
            )


# HELPERS PER RUN MUTATION
def get_source_sha256(config): 
    if config.get("pipeline") in {"sequence", "collect"}: 
        report = load_json(BASE_DIR / config["report"]) 
 
        return report["source"]["sha256"] 

    # COMPATIBILITÀ LEGACY:
    # I test legacy salvano l'hash SHA-256 della cattura in evidence.json.
    # La nuova pipeline lo salva direttamente nel report unificato.
    # Rimuovere questo ramo quando evidence.json non sarà più utilizzato.
    evidence = load_json(BASE_DIR / config["evidence"]) 
 
    return evidence["source"]["sha256"] 
 
def get_verdict(config): 
    report = load_json(BASE_DIR / config["report"]) 
 
    return report["verdict"]  

def run_pipeline_for_mutation(
        test_id,
        case_id,
        verbose,
        test_config=None
):
    if verbose:
        return run_pipeline(test_id, case_id, verbose, test_config)

    output = StringIO()

    with redirect_stdout(output):
        return run_pipeline(test_id, case_id, verbose, test_config)

def build_mutated_config(
    baseline_config,
    mutation,
    case_id=None,
):
    if not mutation.get("inherit_baseline_config"):
        return load_test_config(
            BASE_DIR,
            mutation["mutated_test"],
            case_id,
        )

    mutated_config = dict(baseline_config)

    test_config = mutation.get("test_config", {})

    # Override comuni
    for key, value in test_config.items():
        if key == "cases":
            continue

        mutated_config[key] = value

    # Eventuali override specifici per case
    cases = test_config.get("cases")

    if cases is not None:
        if case_id is None:
            raise RuntimeError(
                f"{mutation['mutated_test']}: "
                "case_id richiesto"
            )

        if case_id not in cases:
            raise RuntimeError(
                f"{mutation['mutated_test']}: "
                f"case '{case_id}' non configurato"
            )

        mutated_config.update(
            cases[case_id]
        )

    return mutated_config

def get_http2_decode_port(test_config: dict) -> int | None:
    traffic = test_config.get("traffic", {})

    for source in traffic.get("sources", []):
        if source.get("type") != "http2":
            continue

        for decode_as in source.get("decode_as", []):
            prefix = "tcp.port=="
            suffix = ",http2"

            if (
                decode_as.startswith(prefix)
                and decode_as.endswith(suffix)
            ):
                port_value = decode_as[
                    len(prefix):-len(suffix)
                ]

                try:
                    return int(port_value)
                except ValueError:
                    raise RuntimeError(
                        f"Porta HTTP/2 non valida in decode_as: {decode_as}"
                    )

    return None


def run_mutation(test_id, variant=None, case_id=None, verbose=False, baseline_already_run=False):
    mutations = load_all_tests("mutation_tests.json")

    mutation_group = mutations.get(test_id)

    if mutation_group is None:
        #
        # COMPATIBILITÀ CON IL FORMATO FLAT ATTUALE.
        #   Serve finché NRF, AMF e gli altri mutation test non saranno migrati alla struttura "variants".
        #
        matches = [
            config
            for config in mutations.values()
            if config["baseline_test"] == test_id
            and (
                variant is None
                or config.get("variant") == variant
            )
        ]

        if len(matches) != 1:
            if variant is None:
                raise RuntimeError(
                    f"Mutation test non configurato univocamente per {test_id}"
                )

            raise RuntimeError(
                f"Variante '{variant}' non disponibile per {test_id}"
            )

        mutation = matches[0]

    else:
        variants = mutation_group.get("variants")

        # NUOVO FORMATO:
        # test
        # └── variants
        #     ├── fail
        #     └── inconclusive

        if variants is not None:

            if variant is None:
                available = ", ".join(sorted(variants))

                raise RuntimeError(
                    f"{test_id} dispone di più varianti. "
                    f"Specificane una con --variant. "
                    f"Disponibili: {available}"
                )

            if variant not in variants:
                available = ", ".join(sorted(variants))

                raise RuntimeError(
                    f"Variante '{variant}' non disponibile per {test_id}. "
                    f"Disponibili: {available}"
                )

            common_config = {
                key: value
                for key, value in mutation_group.items()
                if key != "variants"
            }

            mutation = {
                **common_config,
                **variants[variant],
                "variant": variant,
            }

        #
        # FORMATO FLAT ANCORA PRESENTE
        #
        else:
            if (
                variant is not None
                and mutation_group.get("variant") != variant
            ):
                raise RuntimeError(
                    f"Variante '{variant}' non disponibile per {test_id}"
                )

            mutation = mutation_group


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

    mutated_config = build_mutated_config(baseline_config, mutation, case_id)


    if not baseline_already_run:
        run_pipeline_for_mutation(baseline_id, case_id, verbose)


    baseline_report = load_json(BASE_DIR / baseline_config["report"])
    baseline_sha256 = get_source_sha256(baseline_config)

    if baseline_report["verdict"] != expected["baseline"]:
        raise RuntimeError(
            f"{baseline_id}: atteso {expected['baseline']}, "
            f"ottenuto {baseline_report['verdict']}"
        )

    if target is not None:
        check_target_rule(
            baseline_id, baseline_config, target, target["baseline"]
        )

    mutation_command = [
        sys.executable,
        "-m",
        mutation["mutator"],
        "--source",
        str(BASE_DIR / baseline_config["pcap"]),
    ]

    if baseline_config.get("pipeline") in {"sequence", "collect"}:
        mutation_command.extend([
            "--report",
            str(BASE_DIR / baseline_config["report"]),
        ])

        mutator_option = mutation.get(
            "mutator_options",
            {}
        )

        if mutator_option.get("http2_port"):
            http2_port = get_http2_decode_port(baseline_config)

            if http2_port is None:
                raise RuntimeError(
                    f"{test_id}: il mutator richiede una porta HTTP/2, ma nessuna porta è configurata"
                )

            mutation_command.extend([
                "--port",
                str(http2_port)
            ])


    # COMPATIBILITÀ LEGACY:
    # I mutator legacy ricevono ancora evidence.json come sorgente dell'evidenza. 
    # I nuovi mutator usano direttamente il report unificato.
    # Rimuovere questo ramo dopo la migrazione dei mutator mantenuti.  
    else:
        mutation_command.extend([
            "--evidence",
            str(BASE_DIR / baseline_config["evidence"]),
        ])

    mutation_command.extend([
        "--output",
        str(BASE_DIR / mutated_config["pcap"]),
        "--overwrite",
    ])

    run_command(
        mutation_command,
        mutation["mutator"],
        verbose=verbose,
    )

    run_pipeline_for_mutation(mutated_id, case_id, verbose, mutated_config)


    mutated_report = load_json(BASE_DIR / mutated_config["report"])
    mutated_sha256 = get_source_sha256(mutated_config)

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

    if baseline_sha256 == mutated_sha256:
        raise RuntimeError("Il PCAP mutato coincide con la baseline")


    label = f"Mutation test: {test_id}"

    if case_id:
        label += f" - Case {case_id}"

    print(f"\n{label}")

    if variant:
        print(f"  Variant: {variant}")

    baseline_verdict = baseline_report["verdict"]
    mutated_verdict = mutated_report["verdict"]

    print()
    print("  Baseline")
    print(f"    Verdict: {baseline_verdict}")
    print(f"    Report:  {baseline_config['report']}")

    print()
    print("  Mutation")
    print(f"    Mutator: {mutation['mutator']}")
    print(f"    Report:  {mutated_config['report']}")
    print(f"    Verdict: {mutated_verdict}")

    if "expected_components" in mutation:
        components = mutation["expected_components"]

        print(
            f"    Static: {components['static']} "
            f"| Temporal: {components['temporal']}"
        )

    if target is not None:
        print()
        print("  Target rule")
        print(
            f"    {target['field']} "
            f"{target['operator']}"
        )
        print(
            f"    {target['baseline']} "
            f"-> {target['mutated']}"
        )

    print()
    print(
        f"  Expected transition: "
        f"{expected['baseline']} -> {expected['mutated']}"
    )

    print(
        f"  Observed transition: "
        f"{baseline_verdict} -> {mutated_verdict}"
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

    mutation_scenarios = list(
        iter_mutation_scenarios(
            mutations
        )
    )

    baseline_expected = {}

    for _, mutation in mutation_scenarios:
        test_id = mutation["baseline_test"]
        expected = (
            mutation["expected_verdicts"]["baseline"]
        )

        if (
            test_id in baseline_expected
            and baseline_expected[test_id]
            != expected
        ):
            raise RuntimeError(
                f"Conflicting baseline verdicts "
                f"for {test_id}"
            )

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
            for mutation_id, mutation in mutation_scenarios
            if mutation["baseline_test"] == test_id
        ]
        order = {
            "static": 0, 
            "temporal": 1, 
            "both": 2,
            "fail": 3,
            "inconclusive": 4
        }
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

                baseline_config = load_test_config(
                    BASE_DIR,
                    test_id,
                    case_id,
                )

                mutated_config = build_mutated_config(
                    baseline_config,
                    mutation,
                    case_id,
                )

                requested_id = (test_id if variant else mutation_id)

                ok = run_batch_item(
                    label,
                    mutation["expected_verdicts"]["mutated"],
                    mutated_config["report"],
                    lambda t=requested_id,
                        v=variant,
                        c=case_id: run_mutation(t, v, c, baseline_already_run=True),
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
        help=(
            "Mutation variant, e.g. static, temporal, both, " \
            "fail, inconclusive"
        )

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