from utils.evidence_utils import get_events_by_type
from utils.http2_mutation_utils import replace_http2_body_value
from utils.mutation_utils import load_mutation_context


def apply_rand(source, evidence, output):
    event = get_events_by_type(
        evidence, "amf_sync_failure", require_single=True
    )

    initial_rand = event["initial_authentication_vector"]["rand"]
    request = event["resynchronization_request"]
    old = request["rand"]

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
        [request["frame"]],
        old.encode("ascii"),
        new.encode("ascii"),
        port=15001,
    )

    return frame, offset, old, new


def main():
    source, evidence, output = load_mutation_context()
    frame, offset, old, new = apply_rand(source, evidence, output)

    print(f"PCAP creato: {output}")
    print(f"Frame: {frame}, posizione: {offset}")
    print(f"RAND: {old} -> {new}")


if __name__ == "__main__":
    main()