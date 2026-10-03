import argparse
from pathlib import Path

from utils.json_utils import load_json
from utils.tshark_utils import calculate_sha256


# NUOVA PIPELINE:
# Loader per i mutator basati sulla nuova architettura.
# Il report unificato viene utilizzato come sorgente dell'evidenza
# necessaria per individuare e validare la mutazione.
def load_sequence_mutation_context():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    report_path = args.report.resolve()
    output = args.output.resolve()

    if not source.is_file():
        parser.error(f"Cattura non trovata: {source}")
    if not report_path.is_file():
        parser.error(f"Evidenza non trovata: {report_path}")
    if source == output:
        parser.error("Sorgente e output devono essere diversi")
    if output.exists() and not args.overwrite:
        parser.error(f"Il file di output esiste già: {output}")

    report = load_json(report_path)

    report_hash = report["source"]["sha256"]
    source_hash = calculate_sha256(source)

    if report_hash != source_hash:
        parser.error(
            "Il report non corrisponde alla cattura sorgente"
        )

    return source, report, output