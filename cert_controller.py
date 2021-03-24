import shlex
import subprocess
import time
import sys

class CertController(object):
    """
    Class to handle the certificate grabbing flow.
    """

    def __init__(self, validHostList, validHostFile,
                outputCiphers, outputValidity, logger):
        self._validhostlist     = validHostList
        self._validhostfile     = validHostFile
        self._outputciphers     = outputCiphers
        self._outputvalidity    = outputValidity
        self.crtlogger          = logger
        
        if self._savetofile() == -1:
            sys.exit(0)
        
    def _savetofile(self):
        self.crtlogger.log_info("{:<18s}: Creating file {} to write certified hostnames".format(__name__, self._validhostfile))
        try:
            with open(self._validhostfile, mode="w", encoding="utf-8") as vhf: # creating the file needed for nmap
                self.crtlogger.log_debug("{:<18s}: Started writing hostnames on file {}".format(__name__, self._validhostfile))
            
                for hostname in self._validhostlist:
                
                    vhf.writelines(hostname + "\n")

        except IOError:
            self.crtlogger.log_error("{:<18s}: File {} does not exist".format(__name__, self._validhostfile))
            self.crtlogger.log_error("{:<18s}: Aborting mission. Ejection in 2 seconds.".format(__name__)) 
            time.sleep(2)
            return -1

        except AttributeError:
            self.crtlogger.log_error("{:<18s}: File {} is having some issues. Check if it's populated/well formatted".format(__name__, self._validhostfile))
            self.crtlogger.log_error("{:<18s}: Aborting mission. Ejection in 2 seconds.".format(__name__)) 
            time.sleep(2)
            return -1

        self.crtlogger.log_debug("{}: Finished writing hostnames on file {}.".format(__name__, self._validhostfile))
        self.crtlogger.log_debug("{}: Calling the certGrabber to launch the actual certificate scan with nmap.".format(__name__))
        

    def launch_scan(self):
        enum_ciphers = "nmap --script ssl-enum-ciphers -v -Pn -oX {} -p 80,443 -iL {}".format(self._outputciphers, self._validhostfile)
        ciphers_args = shlex.split(enum_ciphers) # using shlex to cook the command
        
        # nmap ssl-cert --> https://nmap.org/nsedoc/scripts/ssl-cert.html
        enum_validity = "nmap --script ssl-cert -Pn -oX {} -v -p 80,443 -iL {}".format(self._outputvalidity, self._validhostfile)
        validity_args = shlex.split(enum_validity) # using shlex to cook the command

        self.crtlogger.log_info("{:<18s}: Going to execute the following nmap scan:{}".format(__name__, enum_ciphers))
        self.crtlogger.log_info("{:<18s}: Going to execute the following nmap scan:{}".format(__name__, enum_validity))
        self.crtlogger.log_info("{:<18s}: 3..2..1.. Launch! Nmap scans launched.".format(__name__))
        
        try:
            self.crtlogger.log_info("{:<18s}: Started the following nmap scan: {}".format(__name__, "ssl-enum-ciphers"))
            subprocess.check_output(ciphers_args) # launching the ssl-enum-ciphers scan
            self.crtlogger.log_info("{:<18s}: Finished the following nmap scan: {}".format(__name__, "ssl-enum-ciphers"))   
            time.sleep(5) # cooling down the engine
            self.crtlogger.log_info("{:<18s}: Started the following nmap scan: {}".format(__name__, "ssl-cert"))
            subprocess.check_output(validity_args) # launching the ssl-cert scan
            self.crtlogger.log_info("{:<18s}: Finished the following nmap scan: {}".format(__name__, "ssl-cert"))

        except KeyboardInterrupt: # catching ctrl + c
            return
        except FileNotFoundError: #catch nmap not found
            self.crtlogger.log_error("{:<18s}: Hey.. It seems that you do not have nmap installed, check it please.".format(__name__))
            return -1
            
    def ping_from_above(self):
        """
            method to probe from the outside
            TODO:
                - Modify the nmap command or find a better solution
                - 
        """
        ping = "nmap --script ssl-enum-ciphers -v -Pn -oX {} -p 80,443 -iL {}".format(self._outputciphers, self._validhostfile)
        ping_args = shlex.split(ping) # using shlex to cook the command

        self.crtlogger.log_debug("{:<18s}: Going to execute the following nmap scan:{}".format(__name__, ping))
        self.crtlogger.log_debug("{:<18s}: 3..2..1.. Launch! Nmap scans launched.".format(__name__))
        
        try:
            self.crtlogger.log_debug("{:<18s}: Started the following nmap scan: {}".format(__name__, "ssl-enum-ciphers"))
            subprocess.check_output(ping_args) # launching the ssl-enum-ciphers scan
            self.crtlogger.log_debug("{:<18s}: Finished the following nmap scan: {}".format(__name__, "ssl-enum-ciphers"))
            
        except KeyboardInterrupt: # catching ctrl + c
            return