import json


def load_subscriber_config(subscriber_file):
    with open(subscriber_file, "r", encoding="utf-8") as f:
        subscriber = json.load(f)

    if "key" not in subscriber:
        raise RuntimeError(
            "KEY not found in SCAS subscriber configuration"
        )

    if "opc" not in subscriber:
        raise RuntimeError(
            "OPc not found in SCAS subscriber configuration"
        )

    return subscriber