from utils.http2_mutation_utils import replace_http2_body_value
from utils.mutation_utils import load_sequence_mutation_context


def apply_rand(source, report, output):
    bindings = (
        report.get("evidence", {}).get("bindings", {})
    )

    initial_vector = bindings.get("initial_vector")
    request = bindings.get("resync")

    if initial_vector is None or request is None:
        raise RuntimeError(
            "Bindings initial_vector/resync non trovati nel report"
        )

    initial_rand = initial_vector["fields"].get("rand")

    old = request["fields"].get("rand")

    if initial_rand is None or old is None:
        raise RuntimeError(
            "RAND non presente nei bindings AMF"
        )

    if old != initial_rand:
        raise RuntimeError(
            "Il RAND della cattura originale non coincide"
        )

    if len(old) != 32 or any(
        character not in "0123456789abcdefABCDEF"
        for character in old
    ):
        raise RuntimeError(
            "Il RAND non è un valore esadecimale a 128 bit"
        )

    new = (
        old[:-1] + format(
            int(old[-1], 16) ^ 1,
            "x",
        )
    )

    candidate_frames = []

    for frame in [
        request["frame"],
        *request.get("related_frames", []),
    ]:
        if frame not in candidate_frames:
            candidate_frames.append(frame)

    frame, offset = replace_http2_body_value(
        source,
        output,
        candidate_frames,
        old.encode("ascii"),
        new.encode("ascii"),
        port=15001,
    )

    return frame, offset, old, new


def main():
    source, report, output = (
        load_sequence_mutation_context()
    )

    frame, offset, old, new = apply_rand(
        source,
        report,
        output,
    )

    print(f"PCAP creato: {output}")
    print(
        f"Frame: {frame}, posizione: {offset}"
    )
    print(f"RAND: {old} -> {new}")


if __name__ == "__main__":
    main()