import json
import subprocess
from pathlib import Path
from typing import Iterator


def iter_tshark_ek(
    pcap_file: str | Path,
    display_filter: str | None = None,
    decode_as: list[str] | None = None,
) -> Iterator[dict]:
    """
    Esegue TShark con output EK e restituisce, uno alla volta, i record dei pacchetti.

    Le righe di metadata {"index": ...} prodotte da -T ek vengono ignorate.
    """

    pcap_file = Path(pcap_file)

    if not pcap_file.exists():
        raise FileNotFoundError(f"PCAP non trovato: {pcap_file}")

    command = [
        "tshark",
        "-r",
        str(pcap_file),
    ]

    # Decode-as, ad esempio:
    # tcp.port==7777,http2
    for rule in decode_as or []:
        command.extend(["-d", rule])

    if display_filter:
        command.extend(["-Y", display_filter])

    command.extend(["-T", "ek"])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    assert process.stdout is not None

    for line in process.stdout:
        line = line.strip()

        if not line:
            continue

        record = json.loads(line)

        # -T ek alterna:
        #     {"index": {...}}
        #     {"timestamp": "...", "layers": {...}}
        # A noi interessano solo i packet record.
        if "layers" not in record:
            continue

        yield record

    stderr = process.stderr.read() if process.stderr else ""
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(
            f"TShark terminato con codice {return_code}:\n{stderr}"
        )


def load_tshark_ek(
    pcap_file: str | Path,
    display_filter: str | None = None,
    decode_as: list[str] | None = None,
) -> list[dict]:
    """
    Versione conveniente che carica tutti i packet record in memoria.
    """

    return list(
        iter_tshark_ek(
            pcap_file=pcap_file,
            display_filter=display_filter,
            decode_as=decode_as,
        )
    )