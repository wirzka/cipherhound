import pprint
import pandas
import datetime
import json
import xml.etree.ElementTree as ET
from datetime import timedelta, date

class XmlHandler(object):

    def __init__(self, output_ciphers,
                output_validity, logger):
        self._outputciphers     = output_ciphers
        self._outputvalidity    = output_validity
        self.xmllogger          = logger
  
    def _xmlhostnamereader(self, elements, cipher_detail):
        # self.xmllogger.log_info("{:<18s}: Searching the hostname tag and grabbing the value.".format(__name__))
        for hostnames in elements.iter(tag="hostname"):
            if hostnames.attrib["type"] == "user":
                cipher_detail["name"] = hostnames.attrib["name"].replace(".lovevda.it", "")
        
        return cipher_detail

    def _xmlportreader(self, port, cipher_detail):
        # self.xmllogger.log_info("{:<18s}: Searching the port tag and grabbing the value.".format(__name__))
        for state in port.iter(tag="state"):
            if port.attrib["portid"] == "443":
                cipher_detail["443"] = state.attrib["state"]
            elif port.attrib["portid"] == "80":
                cipher_detail["80"] = state.attrib["state"]
            else:
                continue

        return cipher_detail

    def _xmlcertdetails(self, root, cipher_validity):
        results_details = [] # list to put each resulting dictionary as a list element
        not_sec_proto  = ('SSLv3', 'TLSv1.0', 'TLSv1.1') # list of protocols that are unsecure for AgID
        sec_proto = ('TLSv1.2', 'TLSv1.3') # list of protocols that are secure for AgID
        
        tlsv12_intermediate =   ("TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256", "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                                "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",  "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                                "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305",   "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305",
                                "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",      "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384")

        tlsv13_intermediate =   ("TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256")
        
        self.xmllogger.log_info("{:<18s}: Starting iterating through the ssl-enum-ciphers' XML tree.".format(__name__))
        for elements in root.iter(tag="host"):
            cipher_detail = { # zeoring the dictionary
                "name"  : "",
                "443"       : False,
                "80"        : False,
                "sslv3"     : False,
                "tlsv10"    : False,
                "tlsv11"    : False,
                "tlsv12"    : False,
                "tlsv13"    : False,
                "secure"    : False,
            }
            
            self.xmllogger.log_debug("{:<18s}: Calling {} to grab ciphers' details.".format(__name__, "xmlCipher"))
            cipher_detail = self._xmlcipherreader(cipher_detail, elements, not_sec_proto, sec_proto,
                                                  tlsv12_intermediate, tlsv13_intermediate)
            
            self.xmllogger.log_debug("{:<18s}: Calling {} to grab hostname.".format(__name__, "xmlHostnameReader"))
            cipher_detail = self._xmlhostnamereader(elements, cipher_detail)
            
            self.xmllogger.log_debug("{:<18s}: Calling {} to grab ports' status.".format(__name__, "xmlPortReader"))
            for ports in elements.iter(tag="ports"):
                for port in ports.iter(tag="port"):
                    cipher_detail = self._xmlportreader(port, cipher_detail)
            
            self.xmllogger.log_debug("{:<18s}: Appending resulting dictionary to the result support list.".format(__name__))
            results_details.append(cipher_detail)
        return results_details


    def _xmlcertvalidity(self, root, cipher_validity):
        result_validity = [] # list to put each resulting dictionary as a list element
        self.xmllogger.log_info("{:<18s}: Checking validity for each hostname.".format(__name__))

        for elements in root.iter(tag="host"):

            cipher_validity = { # zeoring the dictionary
                "name"  : "",
                "valid"     : ""
            }
            
            cipher_validity = self._xmlhostnamereader(elements, cipher_validity)

            for ports in elements.iter(tag="ports"):
                for port in ports.iter(tag="port"):
                    for scripts in port.iter(tag="script"):
                        for tables in scripts.iter(tag="table"):
                            try:
                                if tables.attrib["key"] == "validity":
                                    today_full_time = str(datetime.datetime.now())
                                    today = today_full_time[:-7].replace(" ", "T")
                                    datetimeformat = '%Y-%m-%dT%H:%M:%S'
                                    not_before = ""
                                    not_after = ""
                                    for keys in tables.iter(tag="elem"):                
                                        if keys.attrib["key"] == "notBefore":
                                            not_before = keys.text
                                            
                                        elif keys.attrib["key"] == "notAfter":
                                            not_after = keys.text
                                            
                                        else:
                                            print("fuq")
                                        
                                    if datetime.datetime.strptime(not_before, datetimeformat) < datetime.datetime.strptime(today, datetimeformat) and datetime.datetime.strptime(not_after, datetimeformat) > datetime.datetime.strptime(today, datetimeformat):
                                        cipher_validity["valid"] = "OK"
                                    elif datetime.datetime.strptime(not_before, datetimeformat) > datetime.datetime.strptime(today, datetimeformat) or datetime.datetime.strptime(not_after, datetimeformat) < datetime.datetime.strptime(today, datetimeformat):
                                        cipher_validity["valid"] = "EXPIRED"
                        
                            except KeyError: continue # just for handling cases where key is not validity
                
                result_validity.append(cipher_validity) # appending the resulting dictionary to the list
        
        return result_validity


    def _xmlcipherreader(self, cipher_detail, elem, not_sec_proto, sec_proto, 
                tlsv12_intermediate, tlsv13_intermediate):

        # self.xmllogger.log_info("{:<18s}: Hunting down all the ciphers' details.".format(__name__))
        for e in elem.iter():
            try:
                if e.attrib["key"] == "name":
                    """
                        TODO: 
                            [ ] Handle separate case for TLSv1.2 and TLSv1.3
                        At the moment it is not fundamental
                    """
                    if e.text not in tlsv12_intermediate :
                        cipher_detail["secure"] = False
                    elif e.text not in tlsv12_intermediate:
                        cipher_detail["secure"] = True

                if e.attrib["key"] in not_sec_proto: # checking if the key is inside the unsecure AgID's list
                    if e.attrib['key'] == "SSLv3": 
                        cipher_detail["sslv3"] = True
                    elif e.attrib['key'] == "TLSv1.0":
                        cipher_detail["tlsv10"] = True
                    elif e.attrib['key'] == "TLSv1.1":
                        
                        cipher_detail["tlsv11"] = True                
                
                if e.attrib["key"] in sec_proto: # checking if the key is inside the secure AgID's list
                    if e.attrib['key'] == "TLSv1.2":
                        cipher_detail["tlsv12"] = True
                    elif e.attrib['key'] == "TLSv1.3":                   
                        cipher_detail["tlsv13"] = True

            except: continue
        
        return cipher_detail

    def xml_reader_handler(self):
        cipher_detail = { # dictionary to put all cipher details 
            "name"  : "",
            "443"       : False,
            "80"        : False,
            "sslv3"     : False,
            "tlsv10"    : False,
            "tlsv11"    : False,
            "tlsv12"    : False,
            "tlsv13"    : False,
            "secure"    : True
        }
        cipher_validity = { # dictionary to put the certificate validity relative to date range
                "hostname"  : "",
                "valid"     : ""
        }
        
        # logging.debug("{}: Parsing the file {} to grab the XML tree.".format(__name__, self._outputvalidity))
        try:
            cert_tree = ET.parse(self._outputvalidity) # retrieve the XML tree from the ssl-cert output
        except FileNotFoundError:
            self.xmllogger.log_error("{:<18s}: Can't find {}, check if it exists.".format(__name__, self._outputvalidity))
            return -1
        self.xmllogger.log_info("{:<18s}: Parsing the file {} to grab the XML tree.".format(__name__, self._outputciphers))
        try:
            cipherTree = ET.parse(self._outputciphers) # retrieve the XML tree from the ssl-enum-ciphers output
        except FileNotFoundError:
            self.xmllogger.log_error("{:<18s}: Can't find {}, check if it exists.".format(__name__, self._outputciphers))
            return -1

        # logging.debug("{}: Getting the root of ssl-cert's XML tree.".format(__name__))
        cert_root = cert_tree.getroot()
        self.xmllogger.log_info("{:<18s}: Getting the root of ssl-enum-ciphers' XML tree.".format(__name__))
        cipherRoot = cipherTree.getroot()

        # logging.debug("{}: Calling {} to check date range of each certificate.".format(__name__, xmlCertValidity))
        validity_dict = self._xmlcertvalidity(cert_root, cipher_validity) # calling xmlCertValidity to check the date range of each certificate
        self.xmllogger.log_info("{:<18s}: Calling to check ciphers' details of each certificate.".format(__name__))
        detail_dict = self._xmlcertdetails(cipherRoot, cipher_detail) # calling _xmlcertdetails to check the ciphers details of each certificate
        
        support_list = []

        for index in enumerate(validity_dict):
            validity_dict[index[0]].update(detail_dict[index[0]])
            support_list.append(validity_dict[index[0]])
        
        return support_list