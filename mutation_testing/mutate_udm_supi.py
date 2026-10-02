import argparse
import hashlib

from pathlib import Path

from utils.json_utils import load_json
from utils.http2_mutation_utils import replace_http2_body_value



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    report_path = args.report.resolve()
    output = args.output.resolve()

    if not source.is_file():
        parser.error(f"Cattura non trovata: {source}")
    if not report_path.is_file():
        parser.error(f"Report non trovata: {report_path}")
    if source == output:
        parser.error("Sorgente e output devono essere diversi")
    if output.exists() and not args.overwrite:
        parser.error(f"Il file di output esiste già: {output}")

    report = load_json(report_path)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    if report["source"]["sha256"] != source_hash:
        parser.error("Il report non corrisponde alla cattura sorgente")


    bindings = (
        report
        .get("evidence", {})
        .get("bindings", {})
    )

    response = bindings.get("response")
    expected = bindings.get("expected")

    if response is None:
        raise RuntimeError(
            "Binding 'response' non trovato nel report"
        )

    if expected is None:
        raise RuntimeError(
            "Binding esterno 'expected' non trovato nel report"
        )

    old = (
        response
        .get("fields", {})
        .get("body", {})
        .get("supi")
    )

    expected_supi = (
        expected
        .get("fields", {})
        .get("supi")
    )

    if old is None:
        raise RuntimeError(
            "SUPI della response non trovato nel report"
        )

    if expected_supi is None:
        raise RuntimeError(
            "SUPI atteso non trovato nel report"
        )

    if old != expected_supi:
        raise RuntimeError(
            "La cattura originale non ha il SUPI atteso"
        )

    if not old[-1].isdigit():
        raise RuntimeError(
            "Il SUPI non termina con una cifra"
        )

    new = old[:-1] + str((int(old[-1]) + 1) % 10)

    old_bytes = old.encode("ascii")
    new_bytes = new.encode("ascii")

    related_frames = response.get(
        "related_frames",
        [],
    )

    if not related_frames:
        raise RuntimeError(
            "Frame della response non disponibili nel report"
        )

    frame, offset = replace_http2_body_value(
        source,
        output,
        related_frames,
        old_bytes,
        new_bytes,
        port=args.port,
    )

    print(f"PCAP creato: {output}")
    print(
        f"Frame: {frame}, posizione: {offset}"
    )
    print(
        f"SUPI: {old} -> {new}"
    )


if __name__ == "__main__":
    main()