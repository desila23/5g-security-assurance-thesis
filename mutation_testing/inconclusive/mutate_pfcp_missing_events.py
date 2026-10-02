from scapy.all import rdpcap, wrpcap

from utils.mutation_utils import load_sequence_mutation_context

BINDING_ALIAS = "responses"


def get_target_frames(report):
    bindings = (
        report
        .get("evidence", {})
        .get("bindings", {})
    )

    events = bindings.get(BINDING_ALIAS, [])

    if not events:
        raise RuntimeError(
            f"Nessun evento trovato nel binding '{BINDING_ALIAS}'"
        )

    frames = {
        event["frame"] 
        for event in events
    }

    return frames


def main():
    source, report, output = load_sequence_mutation_context()

    target_frames = get_target_frames(report)

    packets = list(rdpcap(str(source)))


    # Creo un nuovo PCAP copiando tutti i pacchetti TRANNE quelli target
    mutated_packets = [
        packet for frame_number, packet in enumerate(
            packets,
            start=1
        )
        if frame_number not in target_frames
    ]

    # Se questo vale, sto restituendo praticamente il PCAP originale
    if len(mutated_packets) == len(packets):
        raise RuntimeError(
            "Nessun frame è stato rimosso"
        )

    # Se questo vale, non ho proprio il PCAP
    if not mutated_packets:
        raise RuntimeError(
            "La mutazione rimuoverebbe tutti i pacchetti"
        )


    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    wrpcap(
        str(output),
        mutated_packets
    )

    print(f"PCAP creato: {output}")
    print(
        "Frame rimossi: "
        + ", ".join(
            str(frame) for frame in sorted(target_frames)
        )
    )


if __name__ == "__main__":
    main()