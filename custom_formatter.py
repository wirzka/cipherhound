import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    bold_green = "\x1b[32;1m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(message)s"
            #%(levelname)s %(asctime)s - %(name)s - (%(filename)s:%(lineno)d) 
    FORMATS = {
        logging.DEBUG: bold_green + "[D] " + fmt + reset,
        logging.INFO: bold_green + "[+] " + fmt + reset,
        logging.WARNING: yellow + "[?] " + fmt + reset,
        logging.ERROR: bold_red + "[!] " + fmt + reset,
        logging.CRITICAL: bold_red + "[/] " + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def log_debug(self, message):
        logger = logging.getLogger("Cipherhound")
        # logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())
        logger.propagate = False

        logger.addHandler(ch)
        
        logger.debug(message)

        logger.removeHandler(ch)
    
    def log_error(self, message):
        logger = logging.getLogger("Cipherhound")
        logger.setLevel(logging.ERROR)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(CustomFormatter())
        logger.propagate = False

        logger.addHandler(ch)
        
        logger.error(message)

        logger.removeHandler(ch)

    def log_info(self, message):
        logger = logging.getLogger("Cipherhound")
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(CustomFormatter())
        logger.propagate = False

        logger.addHandler(ch)
        
        logger.info(message)

        logger.removeHandler(ch)