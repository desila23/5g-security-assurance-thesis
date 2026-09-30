from threading import Lock
from pycrate_asn1dir import NGAP

PDU_NGAP  = NGAP.NGAP_PDU_Descriptions.NGAP_PDU

ASN_READY_NGAP  = Lock()


def asn_ngap_acquire():
   return ASN_READY_NGAP.acquire()

def asn_ngap_release():
    ASN_READY_NGAP.release()