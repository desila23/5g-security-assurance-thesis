from robot.api import logger
from robot.api.deco import keyword
import httpx
import json
import jsonschema
import socket


NRF_SCHEMA = {
    "type": "object",
    "properties": {
        "nfInstanceId": {"type": "string"},
        "nfType": {"type": "string"},
        "nfStatus": {"type": "string"},
        "sNssais": {
            "type": "array",
            "items": { "type": "object"}
        }
    },
    "required": ["nfType", "nfStatus", "sNssais"],
    "additionalProperties": True
}

ROBOT_AUTO_KEYWORDS = False

NNRF_NFM = "nnrf-nfm/v1"
NNRF_DISC = "nnrf-disc/v1"

NF_INSTS = "nf-instances"


class NRFClient:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self, nrf_url:str="", is_http2:bool=False) -> None:
        self.nrf_url = nrf_url
        self.is_http2 = is_http2

    @keyword
    def set_nrf(self, nrf_url:str="", is_http2:bool=False) -> None:
        self.nrf_url = nrf_url
        self.is_http2 = is_http2


    @keyword
    def register_nf(self, nf_uuid:str, body_json:str) -> int:
        with httpx.Client(http2=self.is_http2, http1= not self.is_http2, verify=False) as client, open(body_json) as nrf_info:
            nfinstances_url = f"{self.nrf_url}/{NNRF_NFM}/{NF_INSTS}"

            body = json.load(nrf_info)
            jsonschema.validate(instance=body, schema=NRF_SCHEMA)

            body["nfInstanceId"] = nf_uuid

            ip_addr = socket.gethostbyname(socket.gethostname())

            body["ipv4Addresses"] = [ip_addr]

            nf_type = body["nfType"]


            # Registering NF
            nf_reg_resp = client.put(url=f"{nfinstances_url}/{nf_uuid}",
                                      json=body, headers={'user-agent': nf_type})
            
            logger.debug(f"Status code: {nf_reg_resp.status_code} - Body: {nf_reg_resp.text}")

            #if not httpx.codes.is_success(nf_reg_resp.status_code):
            #
            #    logger.error(f"Unable to register NF - status code: {nf_reg_resp.status_code} - body: {nf_reg_resp.json()}")
            #    raise Exception("Unable to register NF")
            return nf_reg_resp.status_code
    

    @keyword
    def discover_nf(self, requester_uuid:str, target_uuid:str, requester_json:str, target_json:str):
        nfdisc_url = f"{self.nrf_url}/{NNRF_DISC}/{NF_INSTS}"
        with httpx.Client(http2=self.is_http2, http1= not self.is_http2, verify=False) as client, open(requester_json) as requester_info, open(target_json) as target_info:
            # Sending discovery request

            parsed_requester = json.load(requester_info)
            jsonschema.validate(instance=parsed_requester, schema=NRF_SCHEMA)

            parsed_target = json.load(target_info)
            jsonschema.validate(instance=parsed_target, schema=NRF_SCHEMA)

            requester_snssais = "["
            for nssai in parsed_requester["sNssais"]:
                requester_snssais+=f"{{ sd:{nssai['sd']},sst:{nssai['sst']} }},"
            requester_snssais+="]"


            discovery_params={
                "target-nf-type": parsed_target["nfType"],
                "requester-nf-type": parsed_requester["nfType"],
                "target-nf-instance-id": target_uuid,
                "requester-nf-instance-id": requester_uuid,
                "requester-snssais": requester_snssais
            }


            disc_resp = client.get(url=nfdisc_url, params=discovery_params, headers={'user-agent': parsed_requester["nfType"]})

            logger.debug(f"Status code: {disc_resp.status_code} - Body: {disc_resp.text}")
            return disc_resp.status_code


    @keyword
    def deregister_nf(self, nf_uuid:str, body_json:str) -> int:
        print(nf_uuid)
        print(body_json)
        with httpx.Client(http2=self.is_http2, http1= not self.is_http2, verify=False) as client, open(body_json) as nrf_info:
            nfinstances_url = f"{self.nrf_url}/{NNRF_NFM}/{NF_INSTS}"

            body = json.load(nrf_info)
            jsonschema.validate(instance=body, schema=NRF_SCHEMA)


            nf_type = body["nfType"]


            # De-registering NF
            nf_reg_resp = client.delete(url=f"{nfinstances_url}/{nf_uuid}", headers={'user-agent': nf_type})
            
            logger.debug(f"Status code: {nf_reg_resp.status_code} - Body: {nf_reg_resp.text}")

            return nf_reg_resp.status_code
    