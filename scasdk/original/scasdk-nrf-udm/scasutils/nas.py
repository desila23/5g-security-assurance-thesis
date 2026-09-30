import pycrate_mobile.NAS as NAS


def get_naspdu(ngap_pdu):
    protocolIEs = ngap_pdu[1]["value"][1]["protocolIEs"]
    for ie in protocolIEs:
        if ie["id"] == 38:
            naspdu_bytes = ie["value"][1]
            m, err = NAS.parse_NAS5G(naspdu_bytes, inner=False)
            return m, err
    return None, 1

def set_naspdu(ngap_pdu, nas_bytes):
    protocolIEs = ngap_pdu[1]["value"][1]["protocolIEs"]
    for ie in protocolIEs:
        if ie["id"] == 38:
            ie["value"] = (ie["value"][0], nas_bytes)
            return 0
    return -1

def get_prot_nas(nas_dict):
    my_arr = nas_dict.get("5GMMSecProtNASMessage")
    for elem in my_arr:
        plain = elem.get("NASMessage")
        if plain:
            m, err = NAS.parse_NAS5G(NAS.unhexlify(plain))
            return m, err
    return None, 1

def set_prot_nas(nas_pdu, nas_bytes):
    nas_pdu[-1].set_val(nas_bytes)
    return nas_pdu
