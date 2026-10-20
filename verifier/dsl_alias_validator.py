def collect_sequence_aliases(items: list[dict]) -> set[str]:
    """
    Raccoglie gli alias dichiarati nella SEQUENCE,
    inclusi quelli contenuti nei blocchi OPTIONAL.
    """
    aliases = set()

    for item in items:
        if item.get("operator") == "OPTIONAL":
            aliases.update(
                collect_sequence_aliases(item["items"])
            )
        else:
            aliases.add(item["alias"])

    return aliases


def collect_rule_field_paths(rules: list[dict]) -> list[str]:
    """
    Raccoglie tutti i riferimenti ai campi usati
    nei criteri statici, inclusi IF annidati
    e operandi a destra dei confronti.
    """
    paths = []

    for rule in rules:
        paths.append(rule["field"])

        expected = rule.get("expected")

        if isinstance(expected, dict):
            if expected.get("type") == "field":
                paths.append(expected["value"])

        if rule["operator"] == "IF":
            paths.extend(
                collect_rule_field_paths(rule["rules"])
            )

    return paths


def validate_rule_aliases(rules: list[dict], declared_aliases: set[str]) -> None:
    """
    Verifica che gli alias utilizzati dai criteri siano stati effettivamente dichiarati.
    """
    for field_path in collect_rule_field_paths(rules):

        parts = field_path.split(".")

        if len(parts) < 2:
            raise ValueError(
                f"Invalid DSL field path: '{field_path}'"
            )

        alias = parts[0]

        if alias not in declared_aliases:
            raise ValueError(
                f"Undeclared DSL alias '{alias}' "
                f"referenced by '{field_path}'"
            )