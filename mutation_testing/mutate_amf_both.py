from pathlib import Path
from tempfile import TemporaryDirectory

from scapy.all import rdpcap, wrpcap

from mutation_testing.mutate_amf_sync_rand import apply_rand
from mutation_testing.mutate_amf_timing import apply_timing
from utils.evidence_utils import get_events_by_type
from utils.mutation_utils import load_mutation_context


def main():
    source, evidence, output = load_mutation_context()
    event = get_events_by_type(
        evidence, 
        "amf_sync_failure", 
        require_single=True
    )


    with TemporaryDirectory() as directory:
        intermediate = Path(directory) / "rand_mutation.pcap"

        frame, offset, old, new = apply_rand(
            source, 
            evidence, 
            intermediate
        )

        packets = list(rdpcap(str(intermediate)))
        (
            case,
            start_frame,
            target_frame,
            original_interval,
            new_interval,
        ) = apply_timing(packets, event)

        output.parent.mkdir(parents=True, exist_ok=True)
        wrpcap(str(output), packets)

    print(f"PCAP creato: {output}")
    print(f"RAND nel frame {frame}, posizione {offset}: {old} -> {new}")
    print(
        f"Caso {case}, frame {start_frame} → {target_frame}: "
        f"{original_interval:.3f} s → {new_interval:.3f} s"
    )


if __name__ == "__main__":
    main()