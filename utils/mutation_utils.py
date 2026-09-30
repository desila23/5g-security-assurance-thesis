import argparse
from pathlib import Path

from utils.json_utils import load_json
from utils.tshark_utils import calculate_sha256


def load_mutation_context():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source = args.source.resolve()
    evidence_path = args.evidence.resolve()
    output = args.output.resolve()

    if not source.is_file():
        parser.error(f"Cattura non trovata: {source}")
    if not evidence_path.is_file():
        parser.error(f"Evidenza non trovata: {evidence_path}")
    if source == output:
        parser.error("Sorgente e output devono essere diversi")
    if output.exists() and not args.overwrite:
        parser.error(f"Il file di output esiste già: {output}")

    evidence = load_json(evidence_path)
    if evidence["source"]["sha256"] != calculate_sha256(source):
        parser.error("L'evidenza non corrisponde alla cattura sorgente")

    return source, evidence, output