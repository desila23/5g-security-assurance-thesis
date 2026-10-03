from matcher.ast import Atom, Sequence
from matcher.thompson import ThompsonCompiler
from matcher.matcher import match_sequences
from traffic.models import MessageEvent


def event(frame_number: int, message_type: str) -> MessageEvent:
    return MessageEvent(
        frame_number=frame_number,
        timestamp=float(frame_number),
        protocol="nas-5gs",
        kind="message",
        message_type=message_type,
    )


def test_case_b():
    pattern = Sequence(
        items=[
            Atom(
                message_type="registration_request",
                alias="registration"
            ),
            Atom(
                message_type="identity_request",
                alias="identity_request"
            ),
            Atom(
                message_type="identity_response",
                alias="identity_response"
            ),
            Atom(
                message_type="authentication_request",
                alias="authentication_request"
            ),
            Atom(
                message_type="authentication_response",
                alias="authentication_response"
            ),
            Atom(
                message_type="authentication_reject",
                alias="authentication_reject"
            ),
        ]
    )

    nfa = ThompsonCompiler().compile(pattern)

    events = [
        # Tentativo precedente/incompleto
        event(800, "registration_request"),
        event(801, "authentication_request"),
        event(802, "authentication_response"),

        # Caso B corretto
        event(867, "registration_request"),
        event(868, "identity_request"),
        event(869, "identity_response"),
        event(905, "authentication_request"),
        event(906, "authentication_response"),
        event(907, "authentication_reject"),
    ]

    matches = match_sequences(nfa, events)

    print(f"Matches trovati: {len(matches)}")

    for i, match in enumerate(matches, start=1):
        print()
        print(f"Match {i}")
        print(f"  start_index: {match.start_index}")
        print(f"  end_index:   {match.end_index}")

        for alias, matched_event in match.bindings.items():
            print(
                f"  {alias}: "
                f"frame={matched_event.frame_number}, "
                f"type={matched_event.message_type}"
            )

    print()
    print("Match atteso:")
    print("  start_index = 3")
    print("  end_index   = 8")

    assert len(matches) == 1
    assert matches[0].start_index == 3
    assert matches[0].end_index == 8

    print()
    print("CASE B: PASS")


if __name__ == "__main__":
    test_case_b()

