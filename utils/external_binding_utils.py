from pathlib import Path

from utils.json_utils import load_json
from verifier.binding_verifier import get_nested_value


def load_external_bindings(base_dir: Path, config: dict | None) -> dict:
    """
    Carica binding esterni dichiarati nella configurazione del test.

    Esempio:

        "expected": {
            "source": "subscriber.json",
            "fields": {
                "supi": {
                    "path": "supi",
                    "prefix": "imsi-"
                }
            }
        }

    Produce:

        {
            "expected": {
                "supi": "imsi-001010000000001"
            }
        }
    """

    if not config:
        return {}

    bindings = {}

    for alias, binding_config in config.items():
        source_path = (
            base_dir / binding_config["source"]
        )

        source_data = load_json(source_path)

        values = {}

        for target_field, field_config in (
            binding_config.get("fields", {}).items()
        ):
            if isinstance(field_config, str):
                source_field = field_config
                prefix = ""

            else:
                source_field = field_config["path"]
                prefix = field_config.get("prefix", "")

            value = get_nested_value(
                source_data,
                source_field,
            )

            if prefix:
                value = f"{prefix}{value}"

            values[target_field] = value

        bindings[alias] = values

    return bindings