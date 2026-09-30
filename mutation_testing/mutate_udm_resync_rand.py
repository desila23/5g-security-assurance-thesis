import argparse

from pathlib import Path

from utils.evidence_utils import get_events_by_type
from utils.http2_mutation_utils import replace_http2_body_value
from utils.json_utils import load_json
from utils.tshark_utils import calculate_sha256


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

    if evidence["source"]["sha256"] != calculate_sha256(source):
        parser.error("L'evidenza non corrisponde alla cattura sorgente")

    initial_auth = get_events_by_type(
        evidence, 
        "initial_auth", 
        require_single=True
    )

    resynchronization = get_events_by_type(
        evidence, 
        "resynchronization", 
        require_single=True
    )


    initial_rand = initial_auth["response"]["body"]["authenticationVector"]["rand"]
    old = resynchronization["request"]["body"]["resynchronizationInfo"]["rand"]

    if old != initial_rand:
        raise RuntimeError("Il RAND della cattura originale non coincide")

    if len(old) != 32 or any(
        character not in "0123456789abcdefABCDEF" for character in old
    ):
        raise RuntimeError("Il RAND non è un valore esadecimale a 128 bit")

    new = old[:-1] + format(int(old[-1], 16) ^ 1, "x")

    frame, offset = replace_http2_body_value(
        source,
        output,
        resynchronization["request"]["body_frames"],
        old.encode("ascii"),
        new.encode("ascii"),
        port=7777
    )

    print(f"PCAP creato: {output}")
    print(f"Frame: {frame}, posizione: {offset}")
    print(f"RAND: {old} -> {new}")


if __name__ == "__main__":
    main()