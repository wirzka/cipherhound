"""
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Usage:
    cipherhound.py  -n (-g | -p) FILENAME
    cipherhound.py  -x ROOT
    cipherhound.py  -h | --help

Options:

    User input:
    -n --nmap          Do the whole process: nmap + xml parsing + xlsx report
    -x --xmlonly       Do only: xml parsing + xlsx report
    -g --grabdomain    Insert the file name or absolute path
    -p --parsedomain   Insert the file name or absolute path
    
Misc:
    -h --help          Show this screen

Some examples:
    cipherhound.py -n -g domain.com
    cipherhound.py -n -p domain.com
    cipherhound.py -x domain.com

- - - - - - - - - - - - - - - - - - by @wirzka - - - - - - - - - - - - - - - - - - - -
"""
import time
import os
import sys
import datetime
from datetime import timedelta, date
from art import tprint
from docopt import docopt
import cert_controller
import xml_handler
import sub_domains_grabby
import custom_formatter
import messages
import xlsx_handler

"""
    +==================== GLOBAL VARIABLES =====================+
    |   This section is to tune the script as your needs are.   |
    |  Go deeper in the code to tune more.                      |
    |  SUBDOMAINSFILE is needed at this time as it indicates    |
    |   to cipherhound where it has to grab the subdomains      |          
    +===========================================================+
"""

SUBDOMAINSFILE      = "" # this value will be automatically changed in relation to the dns root     
ROOT                = "" # this value will be automatically changed in relation to the dns root
OUTPUT_VALIDITY     = "" # this value will be automatically changed in relation to the dns root     
OUTPUT_CIPHERS      = "" # this value will be automatically changed in relation to the dns root     
VALIDHOSTNAMEFILE   = "" # this value will be automatically changed in relation to the dns root     

logger = custom_formatter.CustomFormatter() # logger object to handle the logging behaviour all around the program

"""
    +=================== SUPPORT FUNCTIONS =====================+
    |  In this section you can find the support functions that  |
    |  CipherHound needs to start correctly.                    |          
    +===========================================================+
"""
def grab_root(file):
    """
        It grabs the root domain from the dnszone/subdomain's file name
        and updates all the global variables according to the root
    """
    path = os.path.split(file) # using os.path.split to split the absolute path
    root = path[1].replace(".txt", "") # getting rid off the file type extension

    global_update(root)

def global_update(root):
    """
        Update the global variables according to the given root
    """
    global  ROOT, SUBDOMAINSFILE, OUTPUT_VALIDITY,\
            OUTPUT_CIPHERS, VALIDHOSTNAMEFILE

    ROOT                = root
    SUBDOMAINSFILE      = root + ".txt"
    OUTPUT_VALIDITY     = root + "_Validity.xml"
    OUTPUT_CIPHERS      = root + "_Cipher.xml"
    VALIDHOSTNAMEFILE   = root + "_ValidHostnames.txt"


def main(arguments):

    # the following variables are used to handle the user's requests
    nmap_scan   = False
    grab_dom    = False
    parse_dom   = False

    msg_handler = messages.Message("Cipherhound", __doc__)
    
    if arguments["--help"]:
        msg_handler.helper()
        return 0
    else:
        msg_handler.title()
        
    if arguments["--nmap"]:
        nmap_scan = True
        grab_root(arguments["FILENAME"]) # grabbing the root from

    if arguments["--xmlonly"]:
        global_update(arguments["ROOT"])

    if arguments["--grabdomain"]:
        grab_dom = True
    elif arguments["--parsedomain"]:
        parse_dom = True

    logger.log_info("{:<18s}: Grabbing the root from the file name and updating variables accordingly to it.".format(main.__name__)) 
    
    # Creating a SubDomainsGrabby object to find the subdomains and info from given files
    dom_parser = sub_domains_grabby.SubDomainsGrabby(SUBDOMAINSFILE, ROOT, logger)

    if nmap_scan:
        if grab_dom:
            logger.log_info("{:<18s}: Grabbing the domains from the already formatted txt file {}.".format(main.__name__, SUBDOMAINSFILE)) 
            targetList = dom_parser.grab_domains()
        elif parse_dom:
            logger.log_info("{:<18s}: Parsing the dns zone file to grab the domains {}.".format(main.__name__, SUBDOMAINSFILE)) 
            targetList = dom_parser.parse_dns_zone()
        
        if targetList == -1:
            logger.log_error("{:<18s}: Aborting mission. Ejection in 2 seconds.".format(main.__name__)) 
            time.sleep(2)
            sys.exit(0)
        # Creating a CertController object to launch the scan phase
        scanner = cert_controller.CertController(targetList, VALIDHOSTNAMEFILE,
                                                OUTPUT_CIPHERS, OUTPUT_VALIDITY, logger)
        
        if scanner.launch_scan() == -1:
            logger.log_error("{:<18s}: Aborting mission. Ejection in 2 seconds.".format(main.__name__)) 
            time.sleep(2)
            sys.exit(0)

    # Creating an XmlHandler object to play with the xml files
    xml_parser = xml_handler.XmlHandler(OUTPUT_CIPHERS, OUTPUT_VALIDITY, logger)
    
    logger.log_info("{:<18s}: Creating the two lists of dictionaries that it'll merge together.".format(main.__name__)) 
    
    # Retrieving the two final lists of dictionaries
    infoList = dom_parser.grab_details_from_zone()
    detList = xml_parser.xml_reader_handler()
    if detList == -1:
        logger.log_error("{:<18s}: Aborting mission. Ejection in 2 seconds.".format(main.__name__))
        time.sleep(2)
        sys.exit(0)

    # Creating an xlsxHandler object to handle the final excel file creation
    xlsx_writer = xlsx_handler.XlsxHandler(ROOT, SUBDOMAINSFILE, logger)
    # Creating the final excel file by giving the two final list of dictionaries
    xlsx_writer.xlsx_writer(infoList, detList)
    
    msg_handler.disclaimer()

if __name__ == "__main__":
    arguments = docopt(__doc__ , help=False, version='0.2.2')
    main(arguments)
    
