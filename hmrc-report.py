#Developed by Daniel Hutchings
import sys
import pandas as pd
import numpy as np
import time
import xml.etree.ElementTree as ET
from lxml import etree
from difflib import ndiff
import csv
import os
import glob
import datetime
import re
import string
from lxml.html.diff import htmldiff
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
from lxml import html 

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents.


def FindMostRecentFile(directory, pattern):
    try:
        filelist = os.path.join(directory, pattern) #builds list of file in a directory based on a pattern
        filelist = sorted(glob.iglob(filelist), key=os.path.getmtime, reverse=True) #sort by date modified with the most recent at the top
        return filelist[0]
    except: return 'na'            


def log(message):
    l = open(JCSLogFile,'a')
    l.write(message + '\n')
    l.close()

def ConvertUnoHtml(Chapter, DocTitle, FilepathXML, FilepathHTML):
    html = etree.Element('html')
    head = etree.SubElement(html, 'head')
    meta = etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')
    link = etree.SubElement(head, 'link') #local css
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'file:///' + reportDir + 'css/style.css')
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
    h6.text = 'New chapter added to the HMRC table of contents: ' + reportDate    
    hr = etree.SubElement(divcenter, 'hr')    
    HTMLTree = etree.parse(FilepathXML)
    HTMLRoot = HTMLTree.getroot()
    divcenter.append(HTMLRoot.find('.//article'))

    tree = etree.ElementTree(html)
    tree.write(FilepathHTML,encoding='utf-8')

def ConvertTrioHtml(Chapter, DocTitle, PreviousFilepathXML, LatestFilepathXML, ComparedFilepathXML, ComparedFilepathHTML):
    html = etree.Element('html')
    head = etree.SubElement(html, 'head')
    meta = etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')
    link = etree.SubElement(head, 'link') #local css
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'file:///' + reportDir + 'css/style.css')
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
    PreviousHTMLTree = etree.parse(PreviousFilepathXML)
    PreviousHTMLRoot = PreviousHTMLTree.getroot()
    divleft.append(PreviousHTMLRoot.find('.//article'))

    divmid = etree.SubElement(divmain, 'div')
    #divmid.set('contenteditable', 'true')
    divmid.set('class', 'container')
    divmid.set('style', 'width: 33%; height: 0%; float:center;')        
    h3 = etree.SubElement(divmid, 'h3')
    h3.text = 'Latest version'    
    hr = etree.SubElement(divmid, 'hr')    
    LatestHTMLTree = etree.parse(LatestFilepathXML)
    LatestHTMLRoot = LatestHTMLTree.getroot()
    divmid.append(LatestHTMLRoot.find('.//article'))

    divright = etree.SubElement(divmain, 'div')
    #divright.set('contenteditable', 'true')
    divright.set('class', 'container')
    divright.set('style', 'width: 33%; height: 0%; float:right;')        
    h3 = etree.SubElement(divright, 'h3')
    h3.text = 'Compared version'    
    hr = etree.SubElement(divright, 'hr')    
    ComparedHTMLTree = etree.parse(ComparedFilepathXML)
    ComparedHTMLRoot = ComparedHTMLTree.getroot()
    divright.append(ComparedHTMLRoot.find('.//article'))

    tree = etree.ElementTree(html)
    tree.write(ComparedFilepathHTML,encoding='utf-8')

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

def CreateReport(Date, changeLen, dfChange, additionsLen, dfAdditions, reportDir, reportFilepath):
    print('Creating report html...')
    log('Creating report html...')
    pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents. This needs to be set if you want html links to work in cell contents
    
    with open(reportDir + 'ReportTemplate.html','r') as template:
        htmltemplate = template.read()

    additionsTable = dfAdditions.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")
    changeTable = dfChange.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")

    with open(reportFilepath,'w', encoding='utf-8') as f:            
        html = htmltemplate.replace('__DATE__', Date).replace('__CHANGELEN__', changeLen).replace('__DFCHANGES__', changeTable)
        if len(dfAdditions) > 0: html = html.replace('__ADDITIONSLEN__', additionsLen).replace('__DFADDITIONS__', additionsTable)
        else: html = html.replace('__ADDITIONSLEN__', additionsLen).replace('__DFADDITIONS__', '')
        html = html.replace('&lt;', '<').replace('&gt;', '>').replace('\\', '/').replace('\u2011','-').replace('\u2015','&#8213;').replace('ī','').replace('─','&mdash;')
        f.write(html)
        f.close()
        pass

    print("Exported html report to..." + reportFilepath)
    log("Exported html report to..." + reportFilepath)

def stripDodgyCharacters(tree):
    for elem in tree.iterfind(".//u"): toReplaceText = elem.text
    try: elem.text = toReplaceText.replace('&lt;', '').replace('&gt;','').replace('<', '').replace('>','')
    except: pass

def stripNavigation(data):
    try:
        for navElement in data.findall('.//nav'): 
            navElement.getparent().remove(navElement)
        print('Nav elements removed before comparison...', data)
    except: 
        print('No Nav elements to remove...', data)


#state = 'local'
state = 'live'
#state = 'livedev'

#lastupdated 06032020 1245

if state == 'live':
    CrawlReportDir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
    LatestDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    PreviousDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    OutputDir = "\\\\atlas\\knowhow\\HMRC\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    reportDir = "\\\\atlas\\knowhow\\HMRC\\"

    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk', 'zainabtaher.raja@lexisnexis.com', 'snehal.kulkarnis@lexisnexis.com', 'nagendra.k@lexisnexis.com', 'daniel.meredith@lexisnexis.co.uk', 'sunaina.srai-chohan@lexisnexis.co.uk', 'sean.maxwell@lexisnexis.co.uk', 'edd.thompson@lexisnexis.co.uk', 'georgina.jalbaud@lexisnexis.co.uk', 'robbie.watson@lexisnexis.co.uk', 'susi.dunn@lexisnexis.co.uk', 'lisa.moore@lexisnexis.co.uk']

if state == 'livedev':
    CrawlReportDir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
    LatestDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    PreviousDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    OutputDir = "\\\\atlas\\knowhow\\HMRC\\dev\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    reportDir = "\\\\atlas\\knowhow\\HMRC\\dev\\"

    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']
    
if state == 'local':
    CrawlReportDir = "HMRCrawlReports\\"
    LatestDir = "latest\\hmrc-internal-manuals\\"
    PreviousDir = "previous\\hmrc-internal-manuals\\"
    OutputDir = "C:\\GIT\\HMRC\\dev\\www\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    reportDir = "C:\\GIT\\HMRC\\dev\\www\\"

    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']


CrawlReport = FindMostRecentFile(CrawlReportDir, '*xml')
CrawlReportDate = datetime.datetime.fromtimestamp(os.path.getmtime(CrawlReport)).date()
#TodaysDate = datetime.date(2020, 2, 27)
TodaysDate = datetime.date.today()
reportDate = datetime.datetime.strptime(str(datetime.date.fromtimestamp(os.path.getctime(CrawlReport))), '%Y-%m-%d').strftime('%d-%m-%Y')
versionDate = datetime.datetime.strptime(str(datetime.date.fromtimestamp(os.path.getctime(CrawlReport))), '%Y-%m-%d').strftime('%Y%m%d')

logDir = reportDir + 'logs\\'
ChangeDir = OutputDir + 'Changes\\'
AddDir = OutputDir + 'Additions\\'
DelDir = OutputDir + 'Deletions\\'
print(CrawlReport)

CrawlRoot = ET.parse(CrawlReport)
additions = CrawlRoot.findall('added/document')
changes = CrawlRoot.findall('changed/document')
deletions = CrawlRoot.findall('removed/document')

reportFilepath = reportDir + 'HMRC_report_'+reportDate+'.html'
errorHTMLFilepath = reportDir + 'HMRC_error_template.html'


sender_email = 'LNGUKPSLDigitalEditors@ReedElsevier.com'

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


JCSLogFile = logDir + 'JCSlog-HMRC-report.txt'
l = open(JCSLogFile,'w')
logdate =  str(time.strftime("%d%m%Y"))
l.write("Start HMRC report generation..."+logdate+"\n")
l.close()

if TodaysDate == CrawlReportDate: 
    print("Today's date is the same as the Crawl Report date, so carry on...")
    log('Looping through changes...')
    dfAdditions = pd.DataFrame(columns = ['Manual', 'Chapter', 'Title', 'Additions'])
    dfChange = pd.DataFrame(columns = ['Manual', 'Chapter', 'Title', 'AboveThreshold', 'Changes'])

    print('Looping through additions...')
    log('Looping through additions...')
    a = 1
    for addition in additions:
        DocID = addition.get('id')
        DocTitle = addition.get('title')
        URI = addition.get('uri')
        try: 
            Chapter = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(2)
            Manual = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(1)
        except AttributeError: continue
        ManualDir = OutputDir + Manual + '\\'
        if os.path.exists(ManualDir) == False: 
            os.mkdir(ManualDir)
            print('ManualDir did not exist, but now created...' + ManualDir)
            log('ManualDir did not exist, but now created...' + ManualDir)
        newDocFilepathXML = ManualDir + Chapter + '-' + versionDate +'.xml'    
        newDocFilepathHTML = ManualDir + Chapter + '-' + versionDate + '.html'

        response = requests.get(URI)     # get response object     
        byte_data = response.content # get byte string 
        source_code = html.fromstring(byte_data) # get filtered source code 
        newDocTree = source_code.xpath('//div[@class="manual-body"]')[0]
        newDocStr = html.tostring(newDocTree[0])
        newData = etree.Element('data') #create xml shell
        newBody = etree.SubElement(newData, 'div')
        newBody.set('class', 'manual-body')
        newBody.set('id', 'content')
        newRoot = newBody.insert(0, etree.fromstring(newDocStr))
        newTree = etree.ElementTree(newData)  #define the shell as the tree    
        newTree.write(newDocFilepathXML,encoding='utf-8') #write the tree out  
        print(newDocFilepathXML)  
        ConvertUnoHtml(Chapter, DocTitle, newDocFilepathXML, newDocFilepathHTML)    
        print(newDocFilepathHTML)

        Link = '<a href="file:///' + ManualDir + Chapter + '-' + versionDate + '.html' + '" target="_blank">View</a>'

        dictionary_row = {"Manual":Manual.replace('-', ' ').title(),"Chapter":Chapter.upper(),"Title":DocTitle,"Additions":Link}
        dfAdditions = dfAdditions.append(dictionary_row, ignore_index=True)
        
        print(dictionary_row)
        log(str(dictionary_row))

        a+=1
        #wait = input("PAUSED...when ready press enter")



    print('Looping through changes...')
    log('Looping through changes...')
    c = 1
    for change in changes:
        DocID = change.get('id')
        DocTitle = change.get('title')
        URI = change.get('uri')
        try: 
            Chapter = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(2)
            Manual = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(1)
        except AttributeError: continue

        LatestFilepathXML = LatestDir + Manual + '\\' + Chapter + '.xml'
        PreviousFilepathXML = PreviousDir + Manual + '\\' + Chapter + '.xml'
        ManualDir = OutputDir + Manual + '\\'
        if os.path.exists(ManualDir) == False: 
            os.mkdir(ManualDir)
            print('ManualDir did not exist, but now created...' + ManualDir)
            log('ManualDir did not exist, but now created...' + ManualDir)
        ComparedFilepathXML = ManualDir + Chapter + '-' + versionDate +'.xml'
        ComparedFilepathHTML = ManualDir + Chapter + '-' + versionDate +'.html'
        try: CompTree = etree.parse(LatestFilepathXML)
        except OSError: 
            print('File not found, skipping loop: ' + LatestFilepathXML)
            log('File not found, skipping loop: ' + LatestFilepathXML)
            continue
        LatestTree = etree.parse(LatestFilepathXML)
        LatestRoot = LatestTree.getroot()
        PreviousTree = etree.parse(PreviousFilepathXML)
        
        stripDodgyCharacters(LatestTree)
        stripDodgyCharacters(PreviousTree)

        PreviousRoot = PreviousTree.getroot()
        PreviousData = PreviousRoot.find('.//root')
        LatestData = LatestRoot.find('.//root')
        
        stripNavigation(PreviousData)
        stripNavigation(LatestData)

        
        print('Comparing the following two files...\n' + LatestFilepathXML + '\n' + PreviousFilepathXML)
        log('Comparing the following two files...\n' + LatestFilepathXML + '\n' + PreviousFilepathXML)
        
        DiffedVersion = htmldiff(PreviousData, LatestData) #Get the diff html from lxml built in method    
        DiffedVersion = DiffedVersion.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('&lt;', '<').replace('&gt;','>')
        
        DiffedVersion = re.sub(r'<img ([^>]*)>', r'<img \1 />', DiffedVersion)
        diffData = etree.Element('data') #create xml shell
        try:
            diffRoot = diffData.insert(0, etree.fromstring(DiffedVersion)) #insert diff html into shell
        except:
            #print(DiffedVersion)
            DiffedVersion = '<div>' + DiffedVersion + '</div>'
            diffRoot = diffData.insert(0, etree.fromstring(DiffedVersion)) #insert diff html into shell

        Difftree = etree.ElementTree(diffData)  #define the shell as the tree    
        Difftree.write(ComparedFilepathXML,encoding='utf-8') #write the tree out    
        print('Exported marked up changes to: ' + ComparedFilepathXML)
        log('Exported marked up changes to: ' + ComparedFilepathXML)
        ConvertTrioHtml(Chapter, DocTitle, PreviousFilepathXML, LatestFilepathXML, ComparedFilepathXML, ComparedFilepathHTML)
        
        levDist = levenshtein_distance(str(ET.tostring(PreviousRoot, encoding='utf-8', method='text')), str(ET.tostring(LatestRoot, encoding='utf-8', method='text')))
        threshold = 50
        if levDist > threshold: significant = True
        else: significant = False

        Link = '<a href="file:///' + ManualDir + Chapter + '-' + versionDate + '.html' + '" target="_blank">View</a>'

        dictionary_row = {"Manual":Manual.replace('-', ' ').title(),"Chapter":Chapter.upper(),"Title":DocTitle,"AboveThreshold":significant,"Changes":Link}
        dfChange = dfChange.append(dictionary_row, ignore_index=True)
        
        print(dictionary_row)
        log(str(dictionary_row))

        #wait = input("PAUSED...when ready press enter")
            
        
        
        c+=1

    dfChange = dfChange.sort_values(['Manual'], ascending = True)
    dfChange.to_csv(OutputDir + "dfChange.csv", sep=',',index=False, encoding='UTF-8')
    dfChange = pd.read_csv(OutputDir + "dfChange.csv")

    dfAdditions = dfAdditions.sort_values(['Manual'], ascending = True)
    dfAdditions.to_csv(OutputDir + "dfAdditions.csv", sep=',',index=False, encoding='UTF-8')
    dfAdditions = pd.read_csv(OutputDir + "dfAdditions.csv")


    CreateReport(reportDate, str(len(changes)), dfChange, str(len(additions)), dfAdditions, reportDir, reportFilepath)

    Email(reportFilepath, 'HMRC Updates Report: ' + reportDate, receiver_email_list)
    print('Email sent to: ' + str(receiver_email_list))    
    log('Email sent to: ' + str(receiver_email_list))    
    #LogOutput('Email sent to: ' + str(receiver_email_list))


    print('Additions: ' + str(len(additions)))
    print('Changes: ' + str(len(changes)))
    print('Deletions: ' + str(len(deletions)))
    log('Additions: ' + str(len(additions)))
    log('Changes: ' + str(len(changes)))
    log('Deletions: ' + str(len(deletions)))
else:
    print("Today's date " + str(TodaysDate) + " not the same as the latest Crawl Report date " + str(CrawlReportDate))    
    log("Today's date " + str(TodaysDate) + " not the same as the latest Crawl Report date " + str(CrawlReportDate))    
    
    Email(errorHTMLFilepath, 'HMRC Updates Report: not generated', ['daniel.hutchings.1@lexisnexis.co.uk'])
    print('Email sent to: ' + str(['daniel.hutchings.1@lexisnexis.co.uk']))    
    log('Email sent to: ' + str(['daniel.hutchings.1@lexisnexis.co.uk']))    