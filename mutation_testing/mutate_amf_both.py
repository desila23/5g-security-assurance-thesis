from pathlib import Path
from tempfile import TemporaryDirectory

from scapy.all import rdpcap, wrpcap

from mutation_testing.mutate_amf_sync_rand import apply_rand
from mutation_testing.mutate_amf_timing import apply_timing
from utils.mutation_utils import load_sequence_mutation_context


def main():
    source, report, output = (
        load_sequence_mutation_context()
    )

    configuration = report.get(
        "configuration",
        {}
    )

    case = configuration.get("case")

    if case not in {"A", "B"}:
        raise RuntimeError(
            "Caso AMF non presente o non valido nel report"
        )

    bindings = report.get("evidence", {}).get("bindings", {})

    if case == "A":
        start_event = bindings.get("resync")
        target_event = bindings.get("new_vector")

        if start_event is None or target_event is None:
            raise RuntimeError(
                "Bindings resync/new_vector non trovati "
                "nel report AMF Case A"
            )

    else:
        start_event = bindings.get("sync_failure")
        target_event = bindings.get("subsequent_auth_request")

        if start_event is None or target_event is None:
            raise RuntimeError(
                "Bindings temporali del Case B non trovati nel report"
            )

    start_frame = start_event["frame"]
    target_frame = target_event["frame"]

    with TemporaryDirectory() as directory:
        intermediate = Path(directory) / "rand_mutation.pcap"

        frame, offset, old, new = apply_rand(
            source,
            report,
            intermediate,
        )

        packets = list(
            rdpcap(str(intermediate))
        )

        case, start_frame, target_frame, original_interval, new_interval = (
            apply_timing(packets, case, start_frame, target_frame)
        )
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        wrpcap(
            str(output),
            packets,
        )

    print(f"PCAP creato: {output}")

    print(
        f"RAND nel frame {frame}, "
        f"posizione {offset}: "
        f"{old} -> {new}"
    )

    print(
        f"Caso {case}, "
        f"frame {start_frame} → {target_frame}: "
        f"{original_interval:.3f} s "
        f"→ {new_interval:.3f} s"
    )


if __name__ == "__main__":
    main()