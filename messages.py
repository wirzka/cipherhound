from art import tprint
import os

class Message(object):

    def __init__(self, name, doc):
        self._name      = name
        self._doc       = doc
        self.PURPLE     = '\033[95m'
        self.CYAN       = '\033[96m'
        self.DARKCYAN   = '\033[36m'
        self.BLUE       = '\033[94m'
        self.GREEN      = '\033[92m'
        self.YELLOW     = '\033[93m'
        self.RED        = '\033[91m'
        self.BOLD       = '\033[1m'
        self.UNDERLINE  = '\033[4m'
        self.END        = '\033[0m'            
    
    def title(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.DARKCYAN + self.BOLD)
        tprint("Cipherhound", font="cyberlarge")
        print(self.END)

    def helper(self):
        self.title()
        print(self.DARKCYAN + self.BOLD)
        print(self._doc)
        print(self.END)

    def disclaimer(self):
        your_fault ="""\n
                 [*]---------------- Be Aware ------------------[*]
                  |    I am not responsible for any damages      |
                  |   (tangible or intangible) you could make    |
                  |         because of using cipherhound.        |
                  |                   Stay safe.                 |     
                 [*]--------------------------------------------[*] 
         """
        print(self.BOLD + self.RED + your_fault + self.END)
