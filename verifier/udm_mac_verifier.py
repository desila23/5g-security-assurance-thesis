from nfs.udm.UDMClient import extract_autn_data
from scasutils.crypto.milenage import Milenage

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