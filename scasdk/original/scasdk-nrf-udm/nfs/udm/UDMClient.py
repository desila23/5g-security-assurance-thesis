#define PY_SSIZE_T_CLEAN
from robot.api import logger
from robot.api.deco import keyword
import httpx
import json
import jsonschema
from scasutils.crypto.milenage import Milenage
import scasutils.crypto.util as util
from binascii import unhexlify
from CryptoMobile import ECIES


CLIENT_SCHEMA = {
    "type": "object",
    "properties": {
        "mnc": {
            "type": "string",
            "pattern": "^\\d{2,3}$"
            },
        "mcc": {
            "type": "string",
            "pattern": "^\\d{3}$"
            },
        "ausfInstanceId": {
            "type": "string",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
            },
        "home_network_key": {
            "type": "string"
        },
        "protection_scheme": {
            "enum": ["A", "B"]
        },
        "key_id": {
            "type": "integer",
            "minimum": 0,
            "maximum": 256
        }
    },
    "required": ["mnc", "mcc", "ausfInstanceId"],
    "additionalProperties": True
}

SUBSCRIBER_SCHEMA = {
    "type": "object",
    "properties": {
        "suci": {
            "type": "string",
            "pattern": "^(imsi-[0-9]{5,15}|nai-.+|gli-.+|gci-.+|suci-(0-[0-9]{3}-[0-9]{2,3}|[1-7]-.+)-[0-9]{1,4}-(0-0-.*|[a-fA-F1-9]-([1-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])-[a-fA-F0-9]+)|.+)$"
            },
        "supi": {
            "type": "string",
            "pattern": "^[0-9]{5,15}$"
        },
        "key": {"type": "string"},
        "opc": {"type": "string"}, 
    },
    "required": ["suci", "key", "opc"],
    "additionalProperties": True
}

PROTECTIONSCHEMES = {'A': 1, 'B': 2}

ROBOT_AUTO_KEYWORDS = False

NUDM_UEAU = "nudm-ueau/v1"
GEN_AUTH_DATA = "security-information/generate-auth-data"



def get_sn_name(mnc, mcc):
    return f"5G:mnc{mnc}.mcc{mcc}.3gppnetwork.org"


def extract_autn_data(autn, sub_key, rand_bytes, opc_bytes):
    ak_xor_sqn = autn[:6]
    amf = autn[6:8]
    mac = autn[8:]

    _, ak = Milenage.f2_f5(sub_key, rand_bytes, opc_bytes)

    sqn_bytes = util.xor(ak, ak_xor_sqn)

    return sqn_bytes, amf, mac

def verify_mac(auth_vect:dict, key_bytes:bytes, opc_bytes:bytes)-> None:
    autn = bytes.fromhex(auth_vect["autn"])
    rand = auth_vect["rand"]
    rand_bytes = bytes.fromhex(rand)
    sqn_bytes, amf, mac = extract_autn_data(autn, key_bytes, rand_bytes, opc_bytes)
    xmac, _ = Milenage.f1(key_bytes, sqn_bytes, rand_bytes, opc_bytes, amf)
    if mac != xmac:
        raise Exception(f"MAC mismatch: xmac = {xmac.hex()} - mac = {mac.hex()}")


class UDMClient:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    config:dict|None

    def __init__(self, udm_url:str="", is_http2:bool=False) -> None:
        self.udm_url = udm_url
        self.is_http2 = is_http2
        self.config:dict|None = None
        self.subscriber = None


    def _gen_auth_data(self, supi_or_suci:str, resync_info:dict|None = None) -> dict: 
        url = f"{self.udm_url}/{NUDM_UEAU}/{supi_or_suci}/{GEN_AUTH_DATA}"

        
        with httpx.Client(http1=not self.is_http2, http2=self.is_http2, verify=False) as client:
            
            if self.config is None:
                raise Exception("Missing config")

            request_body = {
                "servingNetworkName": get_sn_name(self.config["mnc"], self.config["mcc"]),
                "ausfInstanceId": self.config["ausfInstanceId"]
            }

            if resync_info is not None:
                request_body["resynchronizationInfo"] = resync_info
        
            auth_resp = client.post(url, json=request_body, headers={'user-agent': "AUSF"})


            if not httpx.codes.is_success(auth_resp.status_code):
                raise Exception(f"Unable to generate authentication vector: {auth_resp.text}")

            auth_data = auth_resp.json()

            return auth_data

    @keyword
    def set_udm(self, udm_url:str="", is_http2:bool=False) -> None:
        self.udm_url = udm_url
        self.is_http2 = is_http2

    @keyword
    def config_udm_client(self, udm_config_path:str):

        with open(udm_config_path) as udm_json:
            udm_config = json.load(udm_json)
            jsonschema.validate(instance=udm_config, schema=CLIENT_SCHEMA)

            self.config = udm_config

    @keyword
    def config_subscriber_data(self, subscriber_config_path:str):
        with open(subscriber_config_path) as subscriber_json:
            subscriber = json.load(subscriber_json)
            jsonschema.validate(instance=subscriber, schema=SUBSCRIBER_SCHEMA)

            self.subscriber = subscriber
        
    @keyword
    def get_supi(self) -> str:
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        if "supi" not in self.subscriber:
            raise Exception("Missing SUPI in subscriber data")
        imsi = self.subscriber["supi"]
        
        return f"imsi-{imsi}"

    @keyword
    def is_deconceal_available(self):
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        
        return "supi" in self.subscriber and "home_network_key" in self.config and "protection_scheme" in self.config and "key_id" in self.config

    @keyword 
    def conceal_supi(self, supi:str) -> str:

        supi = supi.replace("imsi-", "")
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        mnc = self.config["mnc"]
        mcc = self.config["mcc"]

        msin = supi[len(mnc) + len(mcc):]


        if len(msin) % 2 == 1:  # Make the msin length even 
            msin = "0" + msin

        reversed_msin = ""
        for pos in range(0,len(msin),2):
            reversed_msin += msin[pos + 1] + msin[pos]
        

        ue = ECIES.ECIES_UE(profile=self.config["protection_scheme"])
        ue.generate_sharedkey(bytes.fromhex(self.config["home_network_key"]))
        ue_pubkey, ue_ciphertext, ue_mac = ue.protect(unhexlify(reversed_msin))

        suci = "suci-0-{}-{}-0-{}-{}-{}{}{}".format(mcc, mnc, PROTECTIONSCHEMES[self.config["protection_scheme"]], self.config["key_id"], bytes.hex(ue_pubkey), bytes.hex(ue_ciphertext), bytes.hex(ue_mac))

        return suci

    @keyword
    def deconceal_suci(self, suci:str) -> str:
        auth_data = self._gen_auth_data(supi_or_suci=suci)

        if "supi" not in auth_data:
            raise Exception("Missing supi in authentication data")
        
        return auth_data["supi"]
    

    @keyword
    def get_auth_vector(self, resync_info:dict|None=None) -> dict:
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        
        suci = self.subscriber["suci"]
        
        auth_data = self._gen_auth_data(supi_or_suci=suci, resync_info=resync_info)
        if "authenticationVector" not in auth_data:
            raise Exception("Missing authentication vector in response")
        
        auth_vect = auth_data["authenticationVector"]
        key_bytes = bytes.fromhex(self.subscriber["key"])
        opc_bytes = bytes.fromhex(self.subscriber["opc"])
        
        verify_mac(auth_vect=auth_vect, key_bytes=key_bytes, opc_bytes=opc_bytes)
        return auth_vect


    @keyword
    def get_sqn(self, auth_vect:dict) -> int:
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        
        autn = bytes.fromhex(auth_vect["autn"])
        rand = auth_vect["rand"]
        rand_bytes = bytes.fromhex(rand)

        key_bytes = bytes.fromhex(self.subscriber["key"])
        opc_bytes = bytes.fromhex(self.subscriber["opc"])

        sqn_bytes, _, _ = extract_autn_data(autn, key_bytes, rand_bytes, opc_bytes)

        sqn = int.from_bytes(sqn_bytes, byteorder='big')

        return sqn


    @keyword
    def gen_resynchronization_info(self, usim_sqn:int, auth_vect:dict) -> dict:
        if self.config is None or self.subscriber is None:
            raise Exception("UDM client is not configured")
        
        autn = bytes.fromhex(auth_vect["autn"])
        rand = auth_vect["rand"]
        rand_bytes = bytes.fromhex(rand)

        key_bytes = bytes.fromhex(self.subscriber["key"])
        opc_bytes = bytes.fromhex(self.subscriber["opc"])

        _, amf, _ = extract_autn_data(autn, key_bytes, rand_bytes, opc_bytes)

        usim = Milenage(amf)

        auts = usim.generate_auts(key_bytes, opc_bytes, rand_bytes, usim_sqn)
        
        
        return {
                "rand": rand,
                "auts": auts.hex() #.upper()
                }

    @keyword
    def auth_vectors_shoud_not_be_equal(self, auth_vect1:dict, auth_vect2:dict):
        for key, value in auth_vect2.items():
            if key != "avType" and value != "" and key in auth_vect1 and auth_vect1[key] == value:
                raise Exception(f"Same value in auth vectors: {key}={value}")
        return
    
