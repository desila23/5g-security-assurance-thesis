import argparse

from pathlib import Path

from utils.http2_mutation_utils import replace_http2_body_value
from utils.json_utils import load_json
from utils.tshark_utils import calculate_sha256


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--report",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--port",
        type=int,
        action="append",
        required=True
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--overwrite",
        action="store_true"
    )

    args = parser.parse_args()

    source = args.source.resolve()
    report_path = args.report.resolve()
    output = args.output.resolve()

    if not source.is_file():
        parser.error(
            f"Cattura non trovata: {source}"
        )

    if not report_path.is_file():
        parser.error(
            f"Report non trovato: {report_path}"
        )

    if source == output:
        parser.error(
            "Sorgente e output devono essere diversi"
        )

    if output.exists() and not args.overwrite:
        parser.error(
            f"Il file di output esiste già: {output}"
        )

    report = load_json(report_path)

    # --------------------------------------------------
    # Verifica coerenza report / PCAP
    # --------------------------------------------------

    if (
        report["source"]["sha256"]
        != calculate_sha256(source)
    ):
        parser.error(
            "Il report non corrisponde alla cattura sorgente"
        )

    # --------------------------------------------------
    # Binding generici
    # --------------------------------------------------

    bindings = report["evidence"]["bindings"]

    case_binding = bindings["case"]["fields"]

    case = case_binding["id"]
    failure_source = case_binding["failure_source"]

    # --------------------------------------------------
    # Local failure: A / B
    #
    # La baseline richiede:
    #
    #     HRES* != HXRES*
    #
    # Mutiamo HXRES* rendendolo uguale a HRES*.
    # --------------------------------------------------

    if failure_source == "local":

        vector = bindings["authentication_vector"]
        hres_star = bindings["hres_star"]

        old = vector["fields"]["hxres_star"]
        new = hres_star["fields"]["value"]

        body_frames = vector["related_frames"]

        field = "hxresStar"

        if old == new:
            raise RuntimeError(
                "HRES* e HXRES* coincidono già"
            )

    # --------------------------------------------------
    # AUSF failure: C / D
    #
    # La baseline richiede:
    #
    #     authResult == AUTHENTICATION_FAILURE
    #
    # Lo trasformiamo in AUTHENTICATION_SUCCESS.
    # --------------------------------------------------

    elif failure_source == "ausf":

        response = bindings[
            "ausf_confirmation_response"
        ]

        old = response["fields"]["auth_result"]
        new = "AUTHENTICATION_SUCCESS"

        body_frames = response["related_frames"]

        field = "authResult"

        if old != "AUTHENTICATION_FAILURE":
            raise RuntimeError(
                "authResult iniziale inatteso: "
                f"{old}"
            )

    else:
        raise RuntimeError(
            "Origine del fallimento non supportata: "
            f"{failure_source}"
        )

    # --------------------------------------------------
    # Controllo mutazione
    # --------------------------------------------------

    if len(old) != len(new):
        raise RuntimeError(
            f"La mutazione di {field} cambia "
            "la lunghezza del payload"
        )

    # --------------------------------------------------
    # Mutazione PCAP
    # --------------------------------------------------

    last_error = None

    for port in args.port:
        try:
            frame, offset = replace_http2_body_value(
                source,
                output,
                body_frames,
                old.encode("ascii"),
                new.encode("ascii"),
                port=port
            )
            break
        except RuntimeError as exc:
            last_error = exc

    else:
        raise RuntimeError(
            f"Impossibile trovare il valore nel body HTTP/2 usando le porte configurate: {args.port}"
        ) from last_error
    

    print(f"PCAP creato: {output}")
    print(
        f"Case {case}, frame {frame}, "
        f"posizione {offset}"
    )
    print(
        f"{field}: {old} -> {new}"
    )


if __name__ == "__main__":
    main()