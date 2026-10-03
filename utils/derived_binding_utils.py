import hashlib

from traffic.models import MessageEvent

from verifier.binding_verifier import get_nested_value
from verifier.udm_mac_verifier import verify_auth_vector_mac


def get_binding_value(context, field_path: str):
    parts = field_path.split(".")

    alias = parts[0]

    if alias not in context.bindings:
        raise RuntimeError(
            f"Binding not found: {alias}"
        )

    binding = context.bindings[alias]

    remaining_path = ".".join(parts[1:])

    if not remaining_path:
        return binding

    if isinstance(binding, MessageEvent):
        return get_nested_value(
            binding.fields,
            remaining_path
        )

    if isinstance(binding, dict):
        return get_nested_value(
            binding,
            remaining_path
        )

    raise RuntimeError(
        f"Unsupported binding type for '{alias}': "
        f"{type(binding).__name__}"
    )



def calculare_hres_star(rand: str, res_star: str) -> str:
    data = bytes.fromhex(rand + res_star)
    digest = hashlib.sha256(data).digest()

    return digest[16:].hex()



def build_derived_bindings(context, config: dict | None) -> dict:
    if not config:
        return {}

    bindings = {}

    for alias, binding_config in config.items():
        binding_type = binding_config["type"]

        if binding_type == "udm_auth_vector_mac":
            auth_vector = get_binding_value(context, binding_config["auth_vector"])

            key = get_binding_value(context, binding_config["key"])

            opc = get_binding_value(context, binding_config["opc"])

            bindings[alias] = verify_auth_vector_mac(
                auth_vector,
                bytes.fromhex(key),
                bytes.fromhex(opc)
            )


        elif binding_type == "hres_star":
            rand = get_binding_value(context, binding_config["rand"])

            res_star = get_binding_value(context, binding_config["res_star"])

            bindings[alias] = {
                "value": calculare_hres_star(rand, res_star)
            }


        else:
            raise RuntimeError(
                f"Unsupported derived binding type: {binding_type}"
            )

    return bindings


