"""Shared structure for evidence reports."""


RESULT_FIELDS = ("criterion_id", "engine", "verdict", "evidence_frames")


def normalize_result(result):
    common = {field: result[field] for field in RESULT_FIELDS}
    details = {
        key: value
        for key, value in result.items()
        if key not in RESULT_FIELDS
    }

    if "rules" in details:
        details["rules"] = [
            {
                **entry,
                "result": normalize_result(entry["result"]),
            }
            for entry in details["rules"]
        ]

    return {**common, "details": details}


def normalize_report(report, summary):
    if report["schema_version"] != "1.0":
        raise ValueError("Atteso un report nel formato 1.0")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("La spiegazione del report non puo essere vuota")
    if report["verdict"] != report["verification"]["overall_verdict"]:
        raise ValueError("Il verdetto del report non coincide con la verifica")
    if not isinstance(report["explanation"], dict):
        raise ValueError("Le osservazioni devono essere un oggetto JSON")

    return {
        "schema_version": "2.0",
        "metadata": report["metadata"],
        "test": report["test"],
        "source": report["source"],
        "configuration": report.get("configuration", {}),
        "criteria": report["criteria"],
        "verification": {
            **report["verification"],
            "results": [
                normalize_result(result)
                for result in report["verification"]["results"]
            ],
        },
        "evidence": report["evidence"],
        "explanation": {
            "summary": summary,
            "observations": report["explanation"],
        },
        "verdict": report["verdict"],
    }