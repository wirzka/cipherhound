class SubDomainsGrabby(object):
    """
    Class used to:
    - enumerate subdomains with external tool (TODO)
    - grab initial details from dnszone
    - grab txt file already formatted ==> 1 subdomain per line
    - parse dns zone txt file
    """

    def __init__(self, subdomainsfile, ROOT, logger):
        self._subdomainsfile    = subdomainsfile
        self._root              = ROOT
        self.subdmnlogger       = logger
    
    def _removeduplicates(self, subdomainlist):
        """
            Remove duplicates using dict, returning to list
            the map object to list() and finally return it to the caller
        """
        return list(dict.fromkeys(subdomainlist))
    
    def _regexiporurl(self, dnsrecord):
        """
            Method to match the IP or URL in the dns zone record
            that must be put inside "data" record in our master dictionary

            TODO:
                - Add regex for url DONE
                - Change method name to be more accurate
        """
        import re
        
        ip_regex = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        url_regex = r"(\w+).(\w+).(\w+)"
        
        if re.search(ip_regex, dnsrecord):
            return dnsrecord
        elif re.search(url_regex, dnsrecord):
            return dnsrecord
        else:
            print("IP/URL NOT VALID")

    def grab_details_from_zone(self):
        """
            It opens the dnszone file and grab the initial information:
                - name -> subdomain name
                - type -> type of subdomain
                - data -> associated IP/URL
            It will call the _regexiporurl() to regex IP and URL
        """
        info = {
            "name"  :   "",
            "type"  :   "",
            "data"  :   ""
        }

        infoList = []
        
        self.subdmnlogger.log_info("{:<18s}: Opening file {} to get domain name and IP".format(__name__, self._subdomainsfile))
        try:
            with open(self._subdomainsfile, mode="r", encoding="utf-8") as dnszone:
                self.subdmnlogger.log_info("{:<18s}: Reading file {} to get domain name and IP".format(__name__, self._subdomainsfile))
                
                for lines in dnszone:
                    info = {
                        "name"  :   "",
                        "type"  :   "",
                        "data"  :   ""
                    }

                    if "(same as parent folder)" in lines and "Host (A)" in lines:
                        l = lines.split()
                        info["name"] = self._root
                        info["type"] = "Host (A)"
                        info["data"] = self._regexiporurl(l[-2])

                    elif "Host (A)" in lines and "localhost" not in lines: # type
                        l = lines.split()
                        info["name"] = l[0].replace("\tHost", "")
                        info["type"] = "Host (A)"
                        info["data"] = self._regexiporurl(l[-2])

                    elif "CNAME" in lines and "localhost" not in lines:
                        l = lines.split()
                        info["name"] = l[0].replace("\tAlias", "")
                        info["type"] = "Alias (CNAME)"
                        info["data"] = self._regexiporurl(l[-2])
                    else:
                        continue
                    
                    info["name"] = info["name"]+"."+self._root # adding the root to do not cause issues in the excel writing phase (Otherwise it doesn't find corresponding data)

                    if info["name"] or info["type"] or info["data"]:
                        infoList.append(info)
            return infoList
        except FileNotFoundError:
            self.subdmnlogger.log_error("{:<18s}: Can't find {}, check if it exists.".format(__name__, self._subdomainsfile))
            return -1
    
    def grab_domains(self):
        """
            This retrieves the subdomains from an already cleaned
            txt file where per each line there is a subdomain
        """
        file = self._subdomainsfile # file to read whre there are the subdomains
        subdomainlist = [] # support list

        try:
            self.subdmnlogger.log_info("{:<18s}: Opening file {} to grab subdomains.".format(__name__, file))
            with open(file, mode="r", encoding="utf-8") as domfile: # opening file to read subdomains
                self.subdmnlogger.log_info("{:<18s}: Reading file {} to grab subdomains.".format(__name__, file))
                
                for dom in domfile: # iterating the lines in the file
                    subdomainlist.append(dom.strip()+self._root) # appending the subdomain without EOL and adding the root domain

            subdomainlist = self._removeduplicates(subdomainlist) # removing duplicates
            return subdomainlist # giving back the list with unique subdomains

        except FileNotFoundError:
            self.subdmnlogger.log_error("{:<18s}: Can't find {}, check if it exists.".format(__name__, self._subdomainsfile))
            return -1

    def parse_dns_zone(self):
        """
            In the case that a dns zone file has been provided, this will parse it
            and retrieve the needed information
        """
        file = self._subdomainsfile
        subdomainlist = []
        
        try:
            self.subdmnlogger.log_info("{:<18s}: Opening file {} to grab subdomains.".format(__name__, file))
            with open(file, mode="r", encoding="utf-8") as dnszone:
                self.subdmnlogger.log_info("{:<18s}: Reading file {} to grab subdomains.".format(__name__, file))
                for lines in dnszone:
                    # TODO
                    # Handle the case for one same as
                    if "(same as" in lines or "_tcp" in lines:
                        continue
                    elif "Host (A)" in lines and "localhost" not in lines:
                        l = lines.split(" ")
                        subdomainlist.append(l[0].replace("\tHost", "")+"."+self._root)

                    elif "CNAME" in lines and "localhost" not in lines:
                        l = lines.split(" ")
                        subdomainlist.append(l[0].replace("\tAlias", "")+"."+self._root)
            
            subdomainlist = self._removeduplicates(subdomainlist)
            return subdomainlist

        except FileNotFoundError:
            self.subdmnlogger.log_error("{:<18s}: Can't find {}, check if it exists.".format(__name__, self._subdomainsfile))
            return -1