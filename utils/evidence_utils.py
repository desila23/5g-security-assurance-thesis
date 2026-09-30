def get_events_by_type(evidence, event_type, require_single=False):
    events = [
        event
        for event in evidence["events"]
        if event["type"] == event_type
    ]

    if not events:
        raise RuntimeError(
            f"Event '{event_type}' not found in evidence"
        )

    if require_single:
        if len(events) > 1:
            raise RuntimeError(
                f"Multiple events of type '{event_type}' found: "
                f"{len(events)}"
            )

        return events[0]

    return events