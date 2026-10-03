from lark import Lark, Transformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GRAMMAR_FILE = BASE_DIR / "grammar.lark"


class RuleTransformer(Transformer):

    def start(self, items):
        return items


    def FIELD(self, token):
        return str(token)

    def NAME(self, token):
        return str(token)

    def OP(self, token):
        return str(token)


    def VALUE(self, token):
        value = str(token)

        if value == "true":
            return True

        if value == "false":
            return False

        if value.isdigit():
            return int(value)

        return value


    def field_operand(self, items):
        return {
            "type": "field",
            "value": str(items[0])
        }


    def literal_operand(self, items):
        return {
            "type": "literal",
            "value": items[0]
        }


    def sequence_item(self, items):
        message_type, alias = items

        return {
            "message_type": str(message_type),
            "alias": str(alias)
        }

    def optional_block(self, items):
        return {
            "operator": "OPTIONAL",
            "items": items
        }

    def sequence_rule(self, items):
        return{
            "operator": "SEQUENCE",
            "items": items
        }


    def comparison_rule(self, items):
        field, operator, expected = items

        return {
            "field": str(field),
            "operator": str(operator),
            "expected": expected
        }

    def unique_rule(self, items):
        field = items[0]

        return {
            "field": str(field),
            "operator": "UNIQUE",
            "expected": None
        }

    def collect_rule(self, items):
        message_type, alias = items

        return {
            "operator": "COLLECT",
            "message_type": str(message_type),
            "alias": str(alias)
        }

    def if_rule(self, items):
        field = items[0]
        operator = items[1]
        expected = items[2]
        rules = items[3:]

        return {
            "field": str(field),
            "operator": "IF",
            "condition_operator": str(operator),
            "expected": expected,
            "rules": rules            
        }

    def MFOTL_BLOCK(self, token):
        return str(token)[3:-3].strip()

    def temporal_rule(self, items):
        case, formula = items
        if not formula:
            raise ValueError(f"Empty MFOTL formula for case {case}")

        return {
            "operator": "MFOTL",
            "case": str(case),
            "formula": formula
        }



def parse_policy(rule_file):
    with open(GRAMMAR_FILE, "r", encoding="utf-8") as f:
        grammar = f.read()

    with open(rule_file, "r", encoding="utf-8") as f:
        rule_text = f.read()

    parser = Lark(grammar, start="start")


    tree = parser.parse(rule_text)

    transformer = RuleTransformer()

    return transformer.transform(tree)


def parse_rule(rule_file):
    # Il verifier statico e i reporter ricevono solo le regole statiche
    return [
        rule for rule in parse_policy(rule_file)
        if rule["operator"] not in {
            "MFOTL", 
            "SEQUENCE",
            "COLLECT"
        }
    ]


def get_sequence(rule_file):
    sequences = [
        rule["items"] for rule in parse_policy(rule_file)
        if rule["operator"] == "SEQUENCE"
    ]

    if len(sequences) != 1:
        raise ValueError(
            f"Expected one SEQUENCE block; found {len(sequences)}"
        )

    return sequences[0]


def get_collect(rule_file):
    collects = [
        rule for rule in parse_policy(rule_file)
        if rule["operator"] == "COLLECT"
    ]

    if len(collects) != 1:
        raise ValueError(
            f"Expected one COLLECT declaration; found {len(collects)}"
        )

    return {
        "message_type": collects[0]["message_type"],
        "alias": collects[0]["alias"]        
    }        


def get_mfotl_formula(rule_file, case):
    formulas = [
        rule["formula"] for rule in parse_policy(rule_file)
        if rule["operator"] == "MFOTL" and rule["case"] == case
    ]

    if len(formulas) != 1:
        raise ValueError(
            f"Expected one MFOTL formula for case {case}; "
            f"found {len(formulas)}"
        )

    return formulas[0]


