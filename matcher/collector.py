from matcher.models import BindingContext
from traffic.models import MessageEvent


def collect_events(
        events: list[MessageEvent],
        message_type: str,
        alias: str
) -> BindingContext:
    
    matched_events = [
        event for event in events
        if event.message_type == message_type
    ]

    return BindingContext(
        bindings={
            alias: matched_events
        } 
    )