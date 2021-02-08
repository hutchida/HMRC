#Developed by Daniel Hutchings
import sys
import pandas as pd
import numpy as np
import time
from lxml import etree
from difflib import ndiff
import csv
import os
import glob
import datetime
import re
import string
from lxml.html.diff import htmldiff
import requests
from lxml import html 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

previous_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
latest_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
dfUpdates = pd.DataFrame(columns = ['Manual', 'Chapter', 'Title', 'AboveThreshold', 'UpdateType', 'HMRC', 'Lexis'])
def scrapedPage(url, path):
    response = requests.get(url) 
    byte_data = response.content 
    source_code = html.fromstring(byte_data) 
    return source_code.xpath(path) 


def create_single_new_HTML_page(Chapter, DocTitle, xml, filepath):
    html = etree.Element('html')
    head = etree.SubElement(html, 'head')
    meta = etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')
    link = etree.SubElement(head, 'link') #local css
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'file:///' + report_dir + 'css/style.css')
    link = etree.SubElement(head, 'link') #bootstrap
    link.set('rel', 'stylesheet')
    link.set('href', 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')
    link.set('itegrity', 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm')
    link.set('crossorigin', 'anonymous')
    style = etree.SubElement(head, 'style') #doc css
    style.text = 'h1{ font-size: 2rem}'

    title = etree.SubElement(head, 'title')
    title.text = 'HMRC - ' + Chapter + ' - ' + DocTitle
    body = etree.SubElement(html, 'body')
    divmain = etree.SubElement(body, 'div')
    divmain.set('class', 'container')
    h1 = etree.SubElement(divmain, 'h1')
    h1.text = Chapter #+ ':'
    hr = etree.SubElement(divmain, 'hr')

    divcenter = etree.SubElement(divmain, 'div')
    #divcenter.set('contenteditable', 'true')
    divcenter.set('class', 'container')
    divcenter.set('style', 'width: 100%; height: 0%;')        
    h6 = etree.SubElement(divcenter, 'h6')
    h6.text = 'New chapter added to the HMRC table of contents: ' + report_date    
    hr = etree.SubElement(divcenter, 'hr')    
    #HTMLTree = etree.parse(xml)
    #HTMLRoot = HTMLTree.getroot()
    divcenter.append(xml)

    tree = etree.ElementTree(html)
    tree.write(filepath + '.html',encoding='utf-8')


def create_comparison_HTML_page(Chapter, DocTitle, previous_filepath, latest_tree, compared_filepath):
    html = etree.Element('html')
    head = etree.SubElement(html, 'head')
    meta = etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')
    link = etree.SubElement(head, 'link') #local css
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'file:///' + report_dir + 'css/style.css')
    link = etree.SubElement(head, 'link') #bootstrap
    link.set('rel', 'stylesheet')
    link.set('href', 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')
    link.set('itegrity', 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm')
    link.set('crossorigin', 'anonymous')
    style = etree.SubElement(head, 'style') #doc css
    style.text = 'h1{ font-size: 2rem}'

    title = etree.SubElement(head, 'title')
    title.text = 'HMRC - ' + Chapter + ' - ' + DocTitle
    body = etree.SubElement(html, 'body')
    divmain = etree.SubElement(body, 'div')
    divmain.set('class', 'container')
    h1 = etree.SubElement(divmain, 'h1')
    h1.text = Chapter #+ ':'
    hr = etree.SubElement(divmain, 'hr')
    #title = etree.SubElement(divmain, 'h3')
    #title.text = DocTitle

    divleft = etree.SubElement(divmain, 'div')
    #divleft.set('contenteditable', 'true')
    divleft.set('class', 'container')
    divleft.set('style', 'width: 33%; height: 0%; float:left;')        
    h3 = etree.SubElement(divleft, 'h3')
    h3.text = 'Previous version'    
    hr = etree.SubElement(divleft, 'hr')    
    #parser = etree.XMLParser(recover=True)
    previous_html_tree = etree.parse(previous_filepath + '.xml')
    previous_html_root = previous_html_tree.getroot()
    divleft.append(previous_html_root.find('.//article'))

    divmid = etree.SubElement(divmain, 'div')
    #divmid.set('contenteditable', 'true')
    divmid.set('class', 'container')
    divmid.set('style', 'width: 33%; height: 0%; float:center;')        
    h3 = etree.SubElement(divmid, 'h3')
    h3.text = 'Latest version'    
    hr = etree.SubElement(divmid, 'hr')    
    
    latest_html_root = latest_tree
    divmid.append(latest_html_root.find('.//article'))

    divright = etree.SubElement(divmain, 'div')
    #divright.set('contenteditable', 'true')
    divright.set('class', 'container')
    divright.set('style', 'width: 33%; height: 0%; float:right;')        
    h3 = etree.SubElement(divright, 'h3')
    h3.text = 'Compared version'    
    hr = etree.SubElement(divright, 'hr')    
    compared_html_tree = etree.parse(compared_filepath + '.xml')
    compared_html_root = compared_html_tree.getroot()
    divright.append(compared_html_root.find('.//article'))

    tree = etree.ElementTree(html)
    tree.write(compared_filepath + '.html',encoding='utf-8')

def CreateReport(Date, dfChange, dfAdditions, dfDeletions, report_filepath, template_filepath):
    log('Creating report html...')
    pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents. This needs to be set if you want html links to work in cell contents
    
    with open(template_filepath,'r') as template:
        htmltemplate = template.read()

    additionsTable = dfAdditions.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")
    changeTable = dfChange.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")
    deletionsTable = dfDeletions.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")

    with open(report_filepath,'w', encoding='utf-8') as f:            
        html = htmltemplate.replace('__DATE__', Date).replace('__CHANGELEN__', str(len(dfChange))).replace('__DFCHANGES__', changeTable)
        
        if len(dfAdditions) > 0: html = html.replace('__ADDITIONSLEN__', str(len(dfAdditions))).replace('__DFADDITIONS__', additionsTable)
        else: html = html.replace('__ADDITIONSLEN__', str(len(dfAdditions))).replace('__DFADDITIONS__', '')
        
        if len(dfDeletions) > 0: html = html.replace('__DELETIONSLEN__', str(len(dfDeletions))).replace('__DFDELETIONS__', deletionsTable)
        else: html = html.replace('__DELETIONSLEN__', str(len(dfDeletions))).replace('__DFDELETIONS__', '')

        html = html.replace('&lt;', '<').replace('&gt;', '>').replace('\\', '/').replace('\u2011','-').replace('\u2015','&#8213;').replace('ī','').replace('─','&mdash;')
        f.write(html)
        f.close()
        pass

    print("Exported html report to..." + report_filepath)
    log("Exported html report to..." + report_filepath)


def levenshtein_distance(str1, str2, ):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else: 
            counter[edit_code] += 1
    distance += max(counter.values())
    return distance

def stripDodgyCharacters(tree):
    for elem in tree.iterfind(".//u"): toReplaceText = elem.text
    try: elem.text = toReplaceText.replace('&lt;', '').replace('&gt;','').replace('<', '').replace('>','')
    except: pass

def stripNavigation(data):
    try:
        for navElement in data.findall('.//nav'): 
            navElement.getparent().remove(navElement)
        #print('Nav elements removed before comparison...', data)
    except: 
        pass
        #print('No Nav elements to remove...', data)


def Email(htmlFilepath, subject, distroList):
    with open(htmlFilepath,'r', encoding="utf-8") as f: 
        htmlToAttach = f.read()
        

    def sendEmail(sender_email, receiver_email, htmlToAttach):    
        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.attach(MIMEText(htmlToAttach, "html"))
        s = smtplib.SMTP("LNGWOKEXCP002.legal.regn.net")
        s.sendmail(sender_email, receiver_email, msg.as_string())
        
    for receiver_email in distroList: sendEmail(sender_email, receiver_email, htmlToAttach)



def log(message):
    l = open(JCSLogFile,'a')
    l.write(message + '\n')
    l.close()
    print(message)

#state = 'local'
state = 'live'
#state = 'livedev'

#last updated 
#020920 1013 - added divya to the email list
#150920 1027 - added metrics logging

if state == 'live':
    Crawlreport_dir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
    latest_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    previous_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    output_dir = "\\\\atlas\\knowhow\\HMRC\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    report_dir = "\\\\atlas\\knowhow\\HMRC\\"

    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk', 'divya.krupat@lexisnexis.com', 'zainabtaher.raja@lexisnexis.com', 'nagendra.k@lexisnexis.com', 'daniel.meredith@lexisnexis.co.uk', 'sunaina.srai-chohan@lexisnexis.co.uk', 'sean.maxwell@lexisnexis.co.uk', 'edd.thompson@lexisnexis.co.uk', 'georgina.jalbaud@lexisnexis.co.uk', 'robbie.watson@lexisnexis.co.uk', 'susi.dunn@lexisnexis.co.uk', 'lisa.moore@lexisnexis.co.uk']
    #receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']#, 'robbie.watson@lexisnexis.co.uk']
if state == 'livedev':
    Crawlreport_dir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
    latest_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    previous_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    output_dir = "\\\\atlas\\knowhow\\HMRC\\dev\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    report_dir = "\\\\atlas\\knowhow\\HMRC\\dev\\"
    
    #receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk', 'zainabtaher.raja@lexisnexis.com', 'snehal.kulkarnis@lexisnexis.com', 'nagendra.k@lexisnexis.com', 'daniel.meredith@lexisnexis.co.uk', 'sunaina.srai-chohan@lexisnexis.co.uk', 'sean.maxwell@lexisnexis.co.uk', 'edd.thompson@lexisnexis.co.uk', 'georgina.jalbaud@lexisnexis.co.uk', 'robbie.watson@lexisnexis.co.uk', 'susi.dunn@lexisnexis.co.uk', 'lisa.moore@lexisnexis.co.uk', 'amanpreet.sunner@lexisnexis.co.uk', 'abigail.mcgregor@lexisnexis.co.uk']

    #receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk', 'robbie.watson@lexisnexis.co.uk']
    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']#, 'robbie.watson@lexisnexis.co.uk']
    
if state == 'local':
    Crawlreport_dir = "HMRCrawlReports\\"
    latest_dir = "latest\\hmrc-internal-manuals\\"
    previous_dir = "previous\\hmrc-internal-manuals\\"
    output_dir = "C:\\GIT\\HMRC\\dev\\www\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    report_dir = "C:\\GIT\\HMRC\\dev\\www\\"

    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']


log_dir = report_dir + 'logs\\'
ChangeDir = output_dir + 'Changes\\'
AddDir = output_dir + 'Additions\\'
DelDir = output_dir + 'Deletions\\'



JCSLogFile = log_dir + 'JCSlog-HMRC-report-scraped.txt'
l = open(JCSLogFile,'w')
logdate =  str(time.strftime("%d%m%Y"))
l.write("Start HMRC report generation..."+logdate+"\n")
l.close()



report_date = str(time.strftime("%d-%m-%Y"))
report_filepath = report_dir + 'HMRC_report_'+report_date+'.html'
errorHTMLFilepath = report_dir + 'HMRC_error_template.html'
sender_email = 'LNGUKPSLDigitalEditors@ReedElsevier.com'
mainUpdatesPage = 'https://www.gov.uk/government/latest?departments%5B%5D=hm-revenue-customs'
todays_date = str(time.strftime("%#d %B %Y"))
#todays_date = "13 May 2020"
version_date = str(time.strftime("%Y%m%d"))
reachedTheEndOfTheDay = False
currentUpdatesPage = mainUpdatesPage
page_number = 0
while reachedTheEndOfTheDay == False:
    page_number +=1
    nextPageURL = 'https://www.gov.uk' + scrapedPage(currentUpdatesPage, '//nav/ul/li[@class="next"]/a/@href')[0]
    print(nextPageURL, 'reachedTheEndOfTheDay?', reachedTheEndOfTheDay, page_number)
    #while there is no exception to me clicking the next page link, loop through all the items on the page until you encounter a date that's not the same as today, so set variable to exit main while loop
    for listitem in scrapedPage(currentUpdatesPage, ".//li[@class='document-row']"):
        Date = re.sub('\s\s\s*', '', listitem.xpath(".//li[@class='date']/text()")[0])
        #if Date == "14 May 2020": continue    #skip loop        
        if todays_date == Date:    
            
            link = listitem.xpath(".//a/@href")[0] 
            print(link)
            if "hmrc-internal-manuals" in link: #check it's a link type we want        
                try: 
                    manual = re.search('\/([^\/]*)\/([^\/]*)\/([^\/]*)', link).group(2)
                    chapter = re.search('\/([^\/]*)\/([^\/]*)\/([^\/]*)', link).group(3)
                except AttributeError: continue #exception raised skip this iteration and continue rest of loop
                doc_title = listitem.xpath(".//a/text()")[0] 
                #check if this chapter exists, if it doesn't scrape it and produce some html
                previous_filepath = previous_dir + manual + '\\' + chapter
                found_term = False
                full_link = 'https://www.gov.uk' + link
                chapter_content = scrapedPage(full_link, ".//div[@class='manual-body']")
                significant = True #default
                manual_dir = output_dir + manual + '\\'
                if os.path.exists(previous_filepath + '.xml') == False: #if not in archive could mean it's new    
                    termlist = ['content has been withheld because of exemptions in the Freedom of Information Act', 'Page Archived']
                    for term in termlist:
                        if found_term == False: 
                            if str(etree.tostring(chapter_content[0])).find(term) > -1:  found_term = True
                    if found_term == True: update_type = 'deletion'
                    else: 
                        update_type = 'new'
                        if os.path.exists(manual_dir) == False: 
                            os.mkdir(manual_dir)
                            print('manual_dir did not exist, but now created...' + manual_dir)
                            log('manual_dir did not exist, but now created...' + manual_dir)
                        new_doc_filepath = manual_dir + chapter + '-' + version_date
                        create_single_new_HTML_page(chapter, doc_title, chapter_content[0], new_doc_filepath) 
                else: 
                    update_type = 'change'                    
                    previous_filepath = previous_dir + manual + '\\' + chapter
                    if os.path.exists(manual_dir) == False: 
                        os.mkdir(manual_dir)
                        print('manual_dir did not exist, but now created...' + manual_dir)
                        log('manual_dir did not exist, but now created...' + manual_dir)
                    compared_filepath = manual_dir + chapter + '-' + version_date
                    
                    previous_tree = etree.parse(previous_filepath + '.xml')
                    #latest_tree = etree.parse(etree.tostring(chapter_content))
                    latest_tree = chapter_content[0]
                    stripDodgyCharacters(latest_tree)
                    stripDodgyCharacters(previous_tree)

                    previous_root = previous_tree.getroot()
                    previous_data = previous_root.find('.//root')
                    #latest_root = latest_tree.getroot()
                    #latest_data = latest_root.find('.//root')
                    latest_data = latest_tree

                    stripNavigation(previous_data)
                    stripNavigation(latest_data)

                    log('Comparing: ' + chapter)
                    
                    diffed_version = htmldiff(previous_data, latest_data) #Get the diff html from lxml built in method    
                    diffed_version = diffed_version.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('&lt;', '<').replace('&gt;','>')                    
                    diffed_version = re.sub(r'<img ([^>]*)>', r'<img \1 />', diffed_version)
                    diff_data = etree.Element('data') #create xml shell
                    try:
                        diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell
                    except:
                        #print(diffed_version)
                        diffed_version = '<div>' + diffed_version + '</div>'
                        try: diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell
                        except: 
                            log('Error with structure of html, breaking out of loop...')
                            continue

                    diff_tree = etree.ElementTree(diff_data)  #define the shell as the tree    
                    diff_tree.write(compared_filepath + '.xml',encoding='utf-8') #write the tree out    
                    print('Exported marked up changes to: ' + compared_filepath + '.xml')
                    log('Exported marked up changes to: ' + compared_filepath + '.xml')
                    create_comparison_HTML_page(chapter, doc_title, previous_filepath, latest_tree, compared_filepath)
                    
                    levDist = levenshtein_distance(str(etree.tostring(previous_data, encoding='utf-8', method='text')), str(etree.tostring(latest_data, encoding='utf-8', method='text')))
                    threshold = 50
                    if levDist > threshold: significant = True
                    else: significant = False

                lexis_link = '<a href="file:///' + manual_dir + chapter + '-' + version_date + '.html' + '" target="_blank">View</a>'
                hmrc_link = '<a href="' + full_link + '" target="_blank">View</a>'
            
                dictionary_row = {"Manual":manual.replace('-', ' ').title(),"Chapter":chapter.upper(),"Title":doc_title,"UpdateType":update_type, "HMRC":hmrc_link, "Lexis":lexis_link, "AboveThreshold":significant}#, "PrevFilepath": previous_filepath_xml} "PageNumber":page_number
                dfUpdates = dfUpdates.append(dictionary_row, ignore_index=True)
                print(dictionary_row)
        else: 
            reachedTheEndOfTheDay = True
            print('New date encountered, breaking out of loop: ', Date)
            break
    currentUpdatesPage = nextPageURL

    dfUpdates.to_csv(report_dir + "dfUpdates.csv", sep=',',index=False, encoding='UTF-8')

df_change = dfUpdates[dfUpdates['UpdateType'].isin(['change'])]
df_additions = dfUpdates[dfUpdates['UpdateType'].isin(['new'])]
df_deletions = dfUpdates[dfUpdates['UpdateType'].isin(['deletion'])]

CreateReport(report_date, df_change, df_additions, df_deletions, report_filepath, report_dir + 'ReportTemplate-scraped.html')

if len(dfUpdates) > 0:
    Email(report_filepath, 'HMRC Updates Report: ' + report_date, receiver_email_list)
    log('Email sent to: ' + str(receiver_email_list))  

    
    def add_to_metrics_log(log_filepath, metric, metric_type, details): 
        if metric > 0:
            print('\nAdding metrics to log...')
            date = str(time.strftime("%Y-%m-%d"))
            df_metric = pd.read_csv(log_filepath) #Load the log
            #check metric hasn't been added to the df already for that document on that date
            df_metric.date = df_metric.date.astype(str)
            df_metric.details = df_metric.details.astype(str)
            new_row = {'metric_type':metric_type, 'details':details,'metric': metric, 'date': date}
            if any((df_metric.date == date) & (df_metric.details == details)) == False: 
                df_metric.loc[len(df_metric)] = new_row #add new row to the end of the dataframe
                #df_metric.loc[1] = new_row #add new row to the start of the dataframe
                df_metric = df_metric.sort_values('date', ascending = False)
                df_metric.to_csv(log_filepath,index=False)
            else:
                print('NO METRICS ADDED: date and details already exist in a row')

    add_to_metrics_log(log_dir+'hmrc-metrics.csv', 1, 'HMRC scraped report generated', 'Updates: ' + str(len(dfUpdates)))


else:    
    Email(errorHTMLFilepath, 'HMRC Updates Report: not generated', ['daniel.hutchings.1@lexisnexis.co.uk'])
    log('Email sent to: ' + str(['daniel.hutchings.1@lexisnexis.co.uk']))    
