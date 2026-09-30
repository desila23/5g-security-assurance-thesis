import hashlib
import hmac
from scasutils.crypto.octet_string import OctetString
from enum import Enum

class UeKeys:
    def __init__(self):
        self.abba = b''
        self.kAusf = b''
        self.kSeaf = b''
        self.kAmf = b''
        self.kNasInt = b''
        self.kNasEnc = b''

class Plmn:
    def __init__(self):
        self.mcc = 0
        self.mnc = 0

    def set_mcc(self, mcc):
        self.mcc = mcc

    def set_mnc(self, mnc):
        self.mnc = mnc

    def get_mcc(self):
        return self.mcc

    def get_mnc(self):
        return self.mnc

class NasSecurityContext:
    def __init__(self):
        self.ciphering = 0
        self.integrity = 0
        self.keys = UeKeys()
        self.plmn = Plmn()
        self.snn = ""
        self.supi = ''


N_NAS_enc_alg = 0x01
N_NAS_int_alg = 0x02
def CalculateKdfKey(key, fc1, fc2, parameters):
    inp = OctetString()
    inp.append_octet(fc1)
    inp.append_octet(fc2)

    for parameter in parameters:
        inp.append(parameter)
        inp.append_octet2(parameter.length())

    hmac_key = key.data()  # Supponendo che data() restituisca i byte della chiave
    kdf_key = hmac.new(hmac_key, inp.data(), hashlib.sha256).digest()

    return OctetString(kdf_key[16:32])  # Prendi i primi 16 byte come chiave

def CalculateKdfKey1(key, fc, parameters):
    inp = OctetString()
    inp.append_octet(fc)
    
    for param in parameters:
        inp.append(param)
        inp.append_octet2(param.length())
    hmac_key = key.data() 
    return hmac.new(hmac_key, inp.data(), hashlib.sha256).digest()

def EncodeKdfString(string):
    # Codifica la stringa normalizzata in UTF-8
    utf8_bytes = string.encode('utf-8')
    my_l = list(utf8_bytes)
    # Restituisci una OctetString con i byte UTF-8
    return OctetString(my_l)

def ConstructServingNetworkName(plmn):
    mcc = plmn.mcc
    mnc = plmn.mnc
    snn = f"5G:mnc{mnc:03d}.mcc{mcc:03d}.3gppnetwork.org"

    if len(snn) != 32:
        raise RuntimeError("SNN construction failure")

    return snn

def CalculateKAusfFor5gAka(ck, ik, snn, sqn_xor_ak):
    # Concatena ck e ik per creare la chiave "key"
    
    key = OctetString.concat(ck, ik)

    # Codifica la stringa snn come OctetString
    s = [EncodeKdfString(snn), sqn_xor_ak.copy()]
    # Calcola KDF
    return OctetString(CalculateKdfKey1(key, 0x6A, s))

def DeriveKeysSeafAmf(security_context):
    snn = ConstructServingNetworkName(security_context.plmn)

    s1 = [EncodeKdfString(snn)]
    s2 = [EncodeKdfString(security_context.supi), security_context.keys.abba.copy()]

    # Calcola kSeaf
    security_context.keys.kSeaf = OctetString(CalculateKdfKey1(security_context.keys.kAusf, 0x6C, s1))

    # Calcola kAmf
    security_context.keys.kAmf = OctetString(CalculateKdfKey1(security_context.keys.kSeaf, 0x6D, s2))

def DeriveNasKeys(security_context):
    s1 = [OctetString.from_octet(N_NAS_enc_alg), OctetString.from_octet(int(security_context.ciphering))]
    s2 = [OctetString.from_octet(N_NAS_int_alg), OctetString.from_octet(int(security_context.integrity))]

    kdf_enc = CalculateKdfKey1(security_context.keys.kAmf, 0x69, s1)
    kdf_int = CalculateKdfKey1(security_context.keys.kAmf, 0x69, s2)

    security_context.keys.kNasEnc = OctetString(kdf_enc).sub_copy(16,16)
    security_context.keys.kNasInt = OctetString(kdf_int).sub_copy(16,16)

def CalculateResStar(key, snn, rand, res):
    params = [EncodeKdfString(snn), OctetString(rand), OctetString(res)]
    output = CalculateKdfKey1(key, 0x6B, params)
    new_out = OctetString(output)
    return new_out.sub_copy1(new_out.length() - 16)



class ETypeOfCipheringAlgorithm(Enum):
    EA0 = 0b0000
    EA1_128 = 0b0001
    EA2_128 = 0b0010
    EA3_128 = 0b0011
    EA4 = 0b0100
    EA5 = 0b0101
    EA6 = 0b0110
    EA7 = 0b0111

class ETypeOfIntegrityProtectionAlgorithm(Enum):
    IA0 = 0b0000
    IA1_128 = 0b0001
    IA2_128 = 0b0010
    IA3_128 = 0b0011
    IA4 = 0b0100
    IA5 = 0b0101
    IA6 = 0b0110
    IA7 = 0b0111