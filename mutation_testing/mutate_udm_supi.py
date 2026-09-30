import argparse
import hashlib

from pathlib import Path

from utils.json_utils import load_json
from utils.http2_mutation_utils import replace_http2_body_value



def main():
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
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

    if evidence["source"]["sha256"] != source_hash:
        parser.error("L'evidenza non corrisponde alla cattura sorgente")

    events = [
        event for event in evidence["events"]
        if event["type"] == "suci_deconcealment"
    ]
    if len(events) != 1:
        raise RuntimeError("Atteso un solo evento SUCI de-concealment")

    event = events[0]
    old = event["response"]["body"]["supi"]
    expected = event["test_input"]["original_supi"]

    if old != expected:
        raise RuntimeError("La cattura originale non ha il SUPI atteso")
    if not old[-1].isdigit():
        raise RuntimeError("Il SUPI non termina con una cifra")

    new = old[:-1] + str((int(old[-1]) + 1) % 10)
    old_bytes = old.encode("ascii")
    new_bytes = new.encode("ascii")

    frame, offset = replace_http2_body_value(
        source,
        output,
        event["response"]["body_frames"],
        old_bytes,
        new_bytes,
        port=7777
    )

    print(f"PCAP creato: {output}")
    print(f"Frame: {frame}, posizione: {offset}")
    print(f"SUPI: {old} -> {new}")


if __name__ == "__main__":
    main()