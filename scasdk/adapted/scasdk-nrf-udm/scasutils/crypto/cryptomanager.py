# ******************************************************************** #
# Classe per gestire cifratura e decifratura dei messaggi nas.         #
# Implementa i metodi decrypt, encrypt e mac_compute, più alcuni       #
# metodi che processano i messaggi di security command, authentication #
# request e registration request per ottenere i parametri necessari.   #
# ******************************************************************** #
import binascii
from scasutils.log_utils import initialize_logger
from scasutils.crypto.keys import *
from scasutils.crypto.milenage import Milenage

class CryptoManager:
    def __init__(self, ue_conf):
        self.logger = initialize_logger('Crypto module')
        self.security_context = NasSecurityContext()
        self.key = binascii.unhexlify(ue_conf["key"])
        self.opc = binascii.unhexlify(ue_conf["opc"])
        self.rand = -1
        self.sqnxak = -1
        self.security_context.supi = ue_conf["imsi"]
        self.reg = False
        self.auth = False
        self.seccmd = False

    def get_security_context(self):
        if self.reg and self.auth and self.seccmd:
            return self.security_context
        else:
            return None
    
    def process_authrequest(self, nas_pdu):
        rand = nas_pdu["RAND"]["V"]
        self.rand = rand.get_val()
        sqnxak = nas_pdu["AUTN"]["AUTN"]["SQNxAK"]
        self.sqnxak = OctetString(sqnxak.get_val())
        abba = nas_pdu["ABBA"]["V"].get_val()
        self.security_context.keys.abba = OctetString(abba)
        if self.auth:
            self.seccmd = False
        elif self.reg:
            self.auth = True

    def process_seccommand(self, nas_pdu):
        protection = nas_pdu["NASSecAlgo"]["NASSecAlgo"]
        c = protection["CiphAlgo"].get_val()
        i = protection["IntegAlgo"].get_val()
        self.security_context.ciphering = c
        self.security_context.integrity = i
        ck_b =Milenage.f3(self.key, self.rand, self.opc)
        ik_b = Milenage.f4(self.key, self.rand, self.opc)
        ck = OctetString(ck_b)
        ik = OctetString(ik_b)
        self.security_context.keys.kAusf = CalculateKAusfFor5gAka(ck, ik, self.security_context.snn, self.sqnxak)
        DeriveKeysSeafAmf(self.security_context)
        DeriveNasKeys(self.security_context)
        if self.auth:
            self.seccmd = True

    def process_regrequest(self, nas_pdu):
        fgsid_ie = nas_pdu["5GSID"]["5GSID"]
        for element in fgsid_ie:
            if element._name == "Value":
                plmn_ie = element["PLMN"]
            elif element._name == "PLMN":
                plmn_ie = element
        plmn = plmn_ie.decode()
        self.security_context.plmn.set_mcc(int(plmn[:3]))
        self.security_context.plmn.set_mnc(int(plmn[3:]))
        self.security_context.snn = ConstructServingNetworkName(self.security_context.plmn)
        if self.reg:
            self.seccmd = False
            self.auth = False
        self.reg = True

    def decrypt(self, nas_pdu):
        if self.reg and self.auth and self.seccmd:
            nas_pdu.decrypt(self.security_context.keys.kNasEnc.data(), fgea = self.security_context.ciphering)
        else:
            self.logger.error("Security context not ready, decryption impossible")
        return nas_pdu
        
    def encrypt(self, nas_pdu):
        if self.reg and self.auth and self.seccmd:
            nas_pdu.encrypt(self.security_context.keys.kNasEnc.data(), fgea = self.security_context.ciphering)
        else:
            self.logger.error("Security context not ready, encryption impossible")
        return nas_pdu
        
    def mac_compute(self, nas_pdu):
        if self.reg and self.auth and self.seccmd:
            nas_pdu.mac_compute(self.security_context.keys.kNasInt.data(), fgia = self.security_context.integrity)
        else:
            self.logger.error("Security context not ready, impossible to compute MAC")
        return nas_pdu