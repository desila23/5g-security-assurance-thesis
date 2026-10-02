from pathlib import Path

from utils.json_utils import save_json
from utils.report_schema import normalize_report
from utils.tshark_utils import calculate_sha256


def _event_to_evidence(event):
    return {
        "message_type": event.message_type,
        "frame": event.frame_number,
        "related_frames": event.related_frames,
        "timestamp": event.timestamp,
        "protocol": event.protocol,
        "kind": event.kind,
        "src": event.src,
        "dst": event.dst,
        "correlation": event.correlation,
        "fields": event.fields,
    }


def _get_binding_context(result):
    if getattr(result, "context", None) is not None:
        return result.context

    match = getattr(result, "match", None) 

    if match is not None:
        return match.to_binding_context()


def _build_evidence(result):
    context = _get_binding_context(result)

    if context is None:
        return {
            "bindings": {}
        }

    bindings = {}

    for alias, binding in context.bindings.items():
        if isinstance(binding, list):
            bindings[alias] = [
                _event_to_evidence(event)
                for event in binding
            ]
        else:
            bindings[alias] = _event_to_evidence(binding)

    return {
        "bindings": bindings
    }



def _frames_for_event(event):
    frames = [event.frame_number]

    for frame in event.related_frames:
        if frame not in frames:
            frames.append(frame)

    return frames


def _frames_for_field(result, field_path):
    if not field_path:
        return []

    context = _get_binding_context(result)

    if context is None:
        return []


    alias = field_path.split(".", 1)[0]

    binding = context.bindings.get(alias)

    if binding is None:
        return []

    if isinstance(binding, list):
        frames = []

        for event in binding:
            for frame in _frames_for_event(event):
                if frame not in frames:
                    frames.append(frame)

        return frames

    return _frames_for_event(binding)


def _build_verification_results(result, test_config):
    if not result.verification:
        return []

    verification_results = []

    for index, rule in enumerate(
        result.verification.get("rules", []),
        start=1,
    ):
        evidence_frames = []

        for frame in _frames_for_field(
            result,
            rule["field"],
        ):
            if frame not in evidence_frames:
                evidence_frames.append(frame)

        expected_field = rule.get("expected_field")

        if expected_field:
            for frame in _frames_for_field(
                result,
                expected_field,
            ):
                if frame not in evidence_frames:
                    evidence_frames.append(frame)

        
        verification_result = {
            "criterion_id": f"criterion_{index}",
            "engine": "binding_verifier",
            "verdict": rule["verdict"],
            "evidence_frames": sorted(evidence_frames),

            "field": rule["field"],
            "operator": rule["operator"],
            "expected": rule["expected"],
            "observed": rule["observed"],
        }

        if expected_field:
            verification_result["expected_field"] = expected_field

        if "duplicates" in rule:
            verification_result["duplicates"] = rule["duplicates"]

        verification_results.append(verification_result)


    #------------------------------------------------
    # Aggiungo MonPoly al report
    #------------------------------------------------

    temporal = result.details.get("temporal")

    if temporal is not None:

        temporal_frames = []

        temporal_config = test_config.get(
            "temporal",
            {}
        )

        event_mapping = temporal_config.get(
            "event_mapping",
            {}
        )

        if result.match is not None:

            for alias in event_mapping:
                event = result.match.bindings.get(alias)

                if event is None:
                    continue

                for frame in _frames_for_event(event):
                    if frame not in temporal_frames:
                        temporal_frames.append(frame)

        verification_results.append({
            "criterion_id": "temporal_1",
            "engine": temporal.get(
                "engine",
                "Monpoly",
            ),
            "verdict": temporal["overall_verdict"],
            "evidence_frames": sorted(temporal_frames),
            "verification_mode": temporal.get("verification_mode"),
            "violation_found": temporal.get("violation_found"),
            "monpoly_output": temporal.get("monpoly_output"),
        })

    return verification_results


def _build_criteria(result):
    if not result.verification:
        return []

    criteria = []

    for index, rule in enumerate(
        result.verification.get("rules", []),
        start=1,
    ):
        operator = rule["operator"]

        if operator == "UNIQUE":
            criterion_type = "uniqueness"
            description = (
                f"verify uniqueness of {rule['field']} across collected events"
            )
        else:
            criterion_type = "comparison"
            description = (
                f"Verify {rule['field']} "
                f"{operator} "
                f"{rule['expected']}"
            )

        criteria.append({
            "id": f"criterion_{index}",
            "type": criterion_type,
            "description": description,
        })


    temporal = result.details.get("temporal")

    if temporal is not None:
        criteria.append({
            "id": "temporal_1",
            "type": "temporal",
            "description": (
                "Verify temporal MFOTL criterion with MonPoly"
            )
        })

    return criteria


def build_generic_report(
    test_id,
    test_config,
    result,
    base_dir
):
    verification_results = (
        _build_verification_results(result, test_config)
    )

    criteria = _build_criteria(result)

    pcap_file = Path(base_dir) / test_config["pcap"]

    pcap_sha256 = calculate_sha256(pcap_file)

    report = {
        "schema_version": "1.0",

        "metadata": {
            "generator": "generic_verification_pipeline",
        },

        "test": {
            "id": test_id,
            "description": test_config.get(
                "description",
                "",
            ),
            "nf": test_config.get(
                "nf",
                "",
            ),
        },

        "source": {
            "pcap": test_config["pcap"],
            "sha256": pcap_sha256
        },

        "configuration": {
            "pipeline": test_config.get(
                "pipeline",
                "legacy"
            ),
            "case": test_config.get("case"),
            "rules": test_config["rules"],
            "traffic": test_config.get(
                "traffic",
                {},
            ),
        },

        "criteria": criteria,

        "verification": {
            "results": verification_results,
            "overall_verdict": result.verdict,
        },

        "evidence": _build_evidence(result),

        "explanation": {
            "reason": result.details.get("reason"),
            "message_type": result.details.get("message_type"),
            "alias": result.details.get("alias"),
            "matches_found": result.details.get("matches_found"),
            "collected_events": result.details.get("collected_events"),
        },

        "verdict": result.verdict,
    }

    if result.verdict == "INCONCLUSIVE":
        summary = result.details.get(
            "reason",
            "Verification was inconclusive",
        )
    else:
        summary = (
            f"Verification completed with verdict {result.verdict}"
        )

    return normalize_report(report, summary)


def save_generic_report(
    test_id,
    test_config,
    result,
    output_file,
    base_dir
):
    report = build_generic_report(
        test_id,
        test_config,
        result,
        base_dir
    )

    save_json(output_file, report)

    return report