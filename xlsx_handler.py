import pandas

class XlsxHandler(object):
    
    def __init__(self, ROOT, SUBDOMAINSFILE, logger):
        self._root              = ROOT
        self._subdomainsfile    = SUBDOMAINSFILE
        self._xlsxlogger        = logger

    def xlsx_writer(self, list_of_dict1, list_of_dict2):
        final_list = []
        self._xlsxlogger.log_info("{:<18s}: Merging the lists on same name.".format(__name__))
        for item in enumerate(list_of_dict1):
            for item2 in enumerate(list_of_dict2):
                if item2[1]["name"] == item[1]["name"]: # if the hostname is equal
                    final_list.append({**item[1], **item2[1]}) # merge the two dicts and append the resulting dict to the final list
        
        finalfile = self._root+".xlsx"

        df = pandas.DataFrame.from_dict(final_list)
        self._xlsxlogger.log_info("{:<18s}: Writing the final list of dicts to the excel file {}.".format(__name__, finalfile))
        df.to_excel(finalfile)