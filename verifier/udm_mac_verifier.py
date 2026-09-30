import json
from pathlib import Path

from nfs.udm.UDMClient import extract_autn_data
from scasutils.crypto.milenage import Milenage

from utils.subscriber_utils import load_subscriber_config
from utils.evidence_utils import get_events_by_type
from utils.json_utils import load_json
from utils.verifier_utils import load_test_config, parse_arguments



BASE_DIR = Path(__file__).resolve().parent.parent



def verify_auth_vector_mac(auth_vector, key_bytes, opc_bytes):
    autn = bytes.fromhex(auth_vector["autn"])
    rand_bytes = bytes.fromhex(auth_vector["rand"])

    sqn_bytes, amf, received_mac = extract_autn_data(
        autn,
        key_bytes,
        rand_bytes,
        opc_bytes
    )

    computed_xmac, _ = Milenage.f1(
        key_bytes,
        sqn_bytes,
        rand_bytes,
        opc_bytes,
        amf
    )

    return {
        "received_mac": received_mac.hex(),
        "computed_xmac": computed_xmac.hex(),
        "match": received_mac == computed_xmac
    }



def main():
    args = parse_arguments("Verify UDM authentication vector MACs")
    config = load_test_config(BASE_DIR, args.test, args.case)

    evidence = load_json(BASE_DIR / config["evidence"])


    initial_auth = get_events_by_type(
        evidence,
        "initial_auth",
        require_single=True
    )

    initial_auth_vector = (
        initial_auth["response"]["body"]["authenticationVector"]
    )



    resynchronization = get_events_by_type(
        evidence,
        "resynchronization",
        require_single=True
    )

    resynchronization_vector = (
        resynchronization["response"]["body"]["authenticationVector"]
    )


    subscriber = load_subscriber_config(BASE_DIR / config["subscriber_file"])

    key_bytes = bytes.fromhex(
        subscriber["key"]
    )

    opc_bytes = bytes.fromhex(
        subscriber["opc"]
    )


    initial_result = verify_auth_vector_mac(
        initial_auth_vector,
        key_bytes,
        opc_bytes
    )

    resynchronization_result = verify_auth_vector_mac(
        resynchronization_vector,
        key_bytes,
        opc_bytes
    )



    print("\n--- INITIAL AUTH MAC ---")
    print(json.dumps(initial_result, indent=4))

    print("\n--- RESYNCHRONIZATION MAC ---")
    print(json.dumps(resynchronization_result, indent=4))



if __name__ == "__main__":
    main()