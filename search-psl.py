import zipfile
from bs4 import BeautifulSoup, SoupStrainer
import re
import pandas as pd
import datetime
import time

def read_zip_file(filepath, csv, termlist, lookupdpsi, start):
    zfile = zipfile.ZipFile(filepath)
    dfdpsi = pd.read_csv(lookupdpsi)

    i = 0
    for finfo in zfile.infolist():
        #if '0OLV' in finfo.filename:
        #print(finfo)

        #wait = input("PAUSED...when ready press enter")

        ifile = zfile.open(finfo)
        #try: df = pd.read_csv(csv, encoding='UTF8')
        #except: df = df
        dpsi = re.search('([^\/]*)\/([^\.]*\.xml)',str(ifile.name)).group(1)
        if any(dfdpsi['DPSI'] == str(dpsi)) == True:
            line_list = ifile.readlines()
            soup = BeautifulSoup(str(line_list), 'lxml') 
            count = 0
            for term in termlist:
                if term in soup.get_text():
                    count = count + len(re.findall(term,soup.get_text()))
                    
                    try: docid = re.search('_([\d]*)\.xml', str(ifile.name)).group(1)
                    except: docid = 'not found'
                    try:doctitle = soup.find('kh:document-title').string
                    except:doctitle = 'not found'
                    #try: dpsi = re.search('([^\/]*)\/([^\.]*\.xml)',str(ifile.name)).group(1)
                    #except: dpsi = 'not found'
                    try: filename = re.search('([^\/]*)\/([^\.]*\.xml)',str(ifile.name)).group(2)
                    except: filename = 'not found'
                    try: PA = re.search('(^[\D^_]+)_[\D]+_',filename).group(1)
                    except: PA = 'not found'
                        
                    if count != 0:    
                        list1 = [[docid, doctitle, PA, filename, term, count]]
                        print('\n\n' + str(i) + str(list1))

                        if i == 0:
                            df = pd.DataFrame()
                            df = df.append(list1)                    
                            df.to_csv(csv, sep=',',index=False, header=["DocID", "DocTitle", "PA", "Filename", "Pattern", "Count"])
                        else:
                            df = pd.read_csv(csv, encoding='UTF8') #open existing csv in df
                            df.loc[len(df)] = {"DocID" : docid, "DocTitle" : doctitle, "PA" : PA, "Filename" : filename, "Pattern" : term, "Count" : count} #add new row to end of df
                            df.to_csv(csv, sep=',',index=False) #overwrite to existing csv
                            print("Time taken so far..." + str(datetime.datetime.now() - start))
                
                
                        i = i + 1



start = datetime.datetime.now() 
dump = "C:\\Users\\Hutchida\\Documents\\PSL\\2019-03-02_08-01-02.zip"
#dump = "C:\\Users\\Hutchida\\Documents\\PSL\\TG-2019-05-22_16-48-52.zip"
#csv = "C:\\Users\\Hutchida\\Documents\\PSL\\reports\\jurisdiction-clauses.csv"
#csv = "C:\\Users\\Hutchida\\Documents\\PSL\\practice.csv"
csv = "C:\\Users\\Hutchida\\Documents\\HMRC\\logs\\hmrc-patterns-locations-" + str(time.strftime("%#d%M%Y")) + ".csv"
lookupdpsi = 'C:\\Users\\Hutchida\\Documents\\PSL\\AICER\\reports\\lookup-dpsis.csv'
#lookupdpsi = '\\\\atlas\\knowhow\\PSL_Content_Management\\Digital Editors\\Lexis_Recommends\\lookupdpsi\\lookup-dpsis.csv'
hmrcpatternlist = 'C:\\Users\\Hutchida\\Documents\\HMRC\\logs\\hmrc-patterns.csv'
dfhmrc = pd.read_csv(hmrcpatternlist)
termlist = dfhmrc.Pattern.tolist()
#print(termlist)
print(csv)
read_zip_file(dump, csv, termlist, lookupdpsi, start)
print(csv)
print("Finished! That took..." + str(datetime.datetime.now() - start))