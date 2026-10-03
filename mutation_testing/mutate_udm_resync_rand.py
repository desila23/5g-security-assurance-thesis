import argparse

from pathlib import Path

from utils.http2_mutation_utils import replace_http2_body_value
from utils.json_utils import load_json
from utils.tshark_utils import calculate_sha256


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--port", type=Path, required=True)
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

    # --------------------------------------------------
    # Verifica coerenza report / PCAP
    # --------------------------------------------------

    if report["source"]["sha256"] != calculate_sha256(source):
        parser.error("Il report non corrisponde alla cattura sorgente")

    # --------------------------------------------------
    # Binding generici
    # --------------------------------------------------

    bindings = report["evidence"]["bindings"]

    initial_response = bindings["initial_response"]
    resync_request = bindings["resync_request"]


    initial_rand = (
        initial_response["fields"]
        ["body"]
        ["authenticationVector"]
        ["rand"]
    )

    old = (
        resync_request["fields"]
        ["body"]
        ["resynchronizationInfo"]
        ["rand"]
    )


    # --------------------------------------------------
    # Controllo baseline
    # --------------------------------------------------

    if old != initial_rand:
        raise RuntimeError(
            "Il RAND della request di resynchronization "
            "non coincide con il RAND iniziale"
        )

    if len(old) != 32 or any(
        character not in "0123456789abcdefABCDEF"
        for character in old
    ):
        raise RuntimeError(
            "Il RAND non è un valore esadecimale a 128 bit"
        )


    # --------------------------------------------------
    # Mutazione deterministica
    # --------------------------------------------------

    new = (
        old[:-1]
        + format(
            int(old[-1], 16) ^ 1,
            "x"
        )
    )


    # --------------------------------------------------
    # Mutazione PCAP
    # --------------------------------------------------

    frame, offset = replace_http2_body_value(
        source,
        output,
        resync_request["related_frames"],
        old.encode("ascii"),
        new.encode("ascii"),
        port=args.port
    )


    print(f"PCAP creato: {output}")
    print(f"Frame: {frame}, posizione: {offset}")
    print(f"RAND: {old} -> {new}")


if __name__ == "__main__":
    main()