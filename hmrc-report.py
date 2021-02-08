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


def find_most_recent_file(directory, pattern):
    try:
        filelist = os.path.join(directory, pattern) #builds list of file in a directory based on a pattern
        filelist = sorted(glob.iglob(filelist), key=os.path.getmtime, reverse=True) #sort by date modified with the most recent at the top
        return filelist[0]
    except: return 'na'            


def log(message):
    l = open(JCSLogFile,'a')
    l.write(message + '\n')
    l.close()
    print(message)

def convert_to_single_html(Chapter, doc_title, FilepathXML, FilepathHTML):
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
    title.text = 'HMRC - ' + Chapter + ' - ' + doc_title
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
    HTMLTree = etree.parse(FilepathXML)
    HTMLRoot = HTMLTree.getroot()
    divcenter.append(HTMLRoot.find('.//article'))

    tree = etree.ElementTree(html)
    tree.write(FilepathHTML,encoding='utf-8')

def convert_to_three_div_html(Chapter, doc_title, previous_filepath_xml, latest_filepath_xml, compared_filepath_xml, compared_filepath_html):
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
    title.text = 'HMRC - ' + Chapter + ' - ' + doc_title
    body = etree.SubElement(html, 'body')
    divmain = etree.SubElement(body, 'div')
    divmain.set('class', 'container')
    h1 = etree.SubElement(divmain, 'h1')
    h1.text = Chapter #+ ':'
    hr = etree.SubElement(divmain, 'hr')
    #title = etree.SubElement(divmain, 'h3')
    #title.text = doc_title

    divleft = etree.SubElement(divmain, 'div')
    #divleft.set('contenteditable', 'true')
    divleft.set('class', 'container')
    divleft.set('style', 'width: 33%; height: 0%; float:left;')        
    h3 = etree.SubElement(divleft, 'h3')
    h3.text = 'Previous version'    
    hr = etree.SubElement(divleft, 'hr')    
    #parser = etree.XMLParser(recover=True)
    PreviousHTMLTree = etree.parse(previous_filepath_xml)
    PreviousHTMLRoot = PreviousHTMLTree.getroot()
    divleft.append(PreviousHTMLRoot.find('.//article'))

    divmid = etree.SubElement(divmain, 'div')
    #divmid.set('contenteditable', 'true')
    divmid.set('class', 'container')
    divmid.set('style', 'width: 33%; height: 0%; float:center;')        
    h3 = etree.SubElement(divmid, 'h3')
    h3.text = 'Latest version'    
    hr = etree.SubElement(divmid, 'hr')    
    LatestHTMLTree = etree.parse(latest_filepath_xml)
    LatestHTMLRoot = LatestHTMLTree.getroot()
    divmid.append(LatestHTMLRoot.find('.//article'))

    divright = etree.SubElement(divmain, 'div')
    #divright.set('contenteditable', 'true')
    divright.set('class', 'container')
    divright.set('style', 'width: 33%; height: 0%; float:right;')        
    h3 = etree.SubElement(divright, 'h3')
    h3.text = 'Compared version'    
    hr = etree.SubElement(divright, 'hr')    
    ComparedHTMLTree = etree.parse(compared_filepath_xml)
    ComparedHTMLRoot = ComparedHTMLTree.getroot()
    divright.append(ComparedHTMLRoot.find('.//article'))

    tree = etree.ElementTree(html)
    tree.write(compared_filepath_html,encoding='utf-8')

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

def create_html_report(Date, changeLen, df_change, additionsLen, df_additions, report_dir, report_filepath):
    log('Creating report html...')
    pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents. This needs to be set if you want html links to work in cell contents
    
    with open(report_dir + 'ReportTemplate.html','r') as template:
        htmltemplate = template.read()

    additionsTable = df_additions.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")
    changeTable = df_change.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover table-sm")

    with open(report_filepath,'w', encoding='utf-8') as f:            
        html = htmltemplate.replace('__DATE__', Date).replace('__CHANGELEN__', changeLen).replace('__DFCHANGES__', changeTable)
        if len(df_additions) > 0: html = html.replace('__ADDITIONSLEN__', additionsLen).replace('__DFADDITIONS__', additionsTable)
        else: html = html.replace('__ADDITIONSLEN__', additionsLen).replace('__DFADDITIONS__', '')
        html = html.replace('&lt;', '<').replace('&gt;', '>').replace('\\', '/').replace('\u2011','-').replace('\u2015','&#8213;').replace('ī','').replace('─','&mdash;')
        f.write(html)
        f.close()
        pass

    log("Exported html report to..." + report_filepath)

def strip_dodgy_characters(tree):
    for elem in tree.iterfind(".//u"): toReplaceText = elem.text
    try: elem.text = toReplaceText.replace('&lt;', '').replace('&gt;','').replace('<', '').replace('>','')
    except: pass

def strip_navigation(data):
    try:
        for navElement in data.findall('.//nav'): 
            navElement.getparent().remove(navElement)
        print('Nav elements removed before comparison...', data)
    except: 
        print('No Nav elements to remove...', data)


def Email(htmlFilepath, subject, distroList):
    with open(htmlFilepath,'r', encoding="utf-8") as f: 
        htmlToAttach = f.read()
        

    def send_email(sender_email, receiver_email, htmlToAttach):    
        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.attach(MIMEText(htmlToAttach, "html"))
        s = smtplib.SMTP("LNGWOKEXCP002.legal.regn.net")
        s.sendmail(sender_email, receiver_email, msg.as_string())
        
    for receiver_email in distroList: send_email(sender_email, receiver_email, htmlToAttach)

state = 'live'
#state = 'dev'

#last updated 
#180820 1617 - update to remove sols dodgy markup in the source before creating new html pages
#020920 1013 - added divya to the email list

crawl_report_dir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
latest_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
previous_dir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
main_dir = "\\\\atlas\\knowhow\\HMRC\\"

if state == 'live':
    output_dir = main_dir + "data\\www.gov.uk\\hmrc-internal-manuals\\"
    report_dir = main_dir
    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk', 'zainabtaher.raja@lexisnexis.com', 'divya.krupat@lexisnexis.com', 'nagendra.k@lexisnexis.com', 'daniel.meredith@lexisnexis.co.uk', 'sunaina.srai-chohan@lexisnexis.co.uk', 'sean.maxwell@lexisnexis.co.uk', 'edd.thompson@lexisnexis.co.uk', 'georgina.jalbaud@lexisnexis.co.uk', 'robbie.watson@lexisnexis.co.uk', 'susi.dunn@lexisnexis.co.uk', 'lisa.moore@lexisnexis.co.uk', 'amanpreet.sunner@lexisnexis.co.uk']

if state == 'dev':
    output_dir = main_dir + "\\dev\\data\\www.gov.uk\\hmrc-internal-manuals\\"
    report_dir = main_dir + "dev\\"
    receiver_email_list = ['daniel.hutchings.1@lexisnexis.co.uk']
    
crawl_report = find_most_recent_file(crawl_report_dir, '*xml')
crawl_report_date = datetime.datetime.fromtimestamp(os.path.getmtime(crawl_report)).date()
#todays_date = datetime.date(2020, 4, 30)
todays_date = datetime.date.today()
report_date = datetime.datetime.strptime(str(datetime.date.fromtimestamp(os.path.getctime(crawl_report))), '%Y-%m-%d').strftime('%d-%m-%Y')
version_date = datetime.datetime.strptime(str(datetime.date.fromtimestamp(os.path.getctime(crawl_report))), '%Y-%m-%d').strftime('%Y%m%d')

log_dir = report_dir + 'logs\\'
change_dir = output_dir + 'Changes\\'
add_dir = output_dir + 'Additions\\'
del_dir = output_dir + 'Deletions\\'
print(crawl_report)

crawl_root = ET.parse(crawl_report)
additions = crawl_root.findall('added/document')
changes = crawl_root.findall('changed/document')
deletions = crawl_root.findall('removed/document')

report_filepath = report_dir + 'HMRC_report_'+report_date+'.html'
error_html_filepath = report_dir + 'HMRC_error_template.html'

sender_email = 'LNGUKPSLDigitalEditors@ReedElsevier.com'

JCSLogFile = log_dir + 'JCSlog-HMRC-report.txt'
l = open(JCSLogFile,'w')
logdate =  str(time.strftime("%d%m%Y"))
l.write("Start HMRC report generation..."+logdate+"\n")
l.close()

#START MAIN 
if todays_date == crawl_report_date: 
    log("Today's date is the same as the Crawl Report date, so carry on...")
    df_additions = pd.DataFrame(columns = ['Manual', 'Chapter', 'Title', 'Additions'])
    df_change = pd.DataFrame(columns = ['Manual', 'Chapter', 'Title', 'AboveThreshold', 'Changes'])

    log('Looping through additions...')
    a = 1
    for addition in additions:
        doc_id = addition.get('id')
        doc_title = addition.get('title')
        URI = addition.get('uri')
        try: 
            Chapter = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(2)
            Manual = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(1)
        except AttributeError: continue
        manual_dir = output_dir + Manual + '\\'
        if os.path.exists(manual_dir) == False: 
            os.mkdir(manual_dir)
            log('manual_dir did not exist, but now created...' + manual_dir)
        new_doc_filepath_xml = manual_dir + Chapter + '-' + version_date +'.xml'    
        new_doc_filepath_html = manual_dir + Chapter + '-' + version_date + '.html'

        #GO TO HMRC WEBSITE TO GET PAGE CONTENT
        response = requests.get(URI)     # get response object     
        byte_data = response.content # get byte string 
        source_code = html.fromstring(byte_data) # get filtered source code 
        new_doc_tree = source_code.xpath('//div[@class="manual-body"]')[0] #extract key part of the page
        new_doc_str = html.tostring(new_doc_tree[0])
        new_data = etree.Element('data') #create xml shell
        new_body = etree.SubElement(new_data, 'div')
        new_body.set('class', 'manual-body')
        new_body.set('id', 'content')
        new_root = new_body.insert(0, html.fromstring(new_doc_str)) #insert into new root
        new_tree = etree.ElementTree(new_data)  #define the shell as the tree    
        new_tree.write(new_doc_filepath_xml,encoding='utf-8') #write the tree out  
        
        #SAVE LATEST PAGE FROM HMRC WEBSITE AS HTML FILE WITH DATED FILENAME
        convert_to_single_html(Chapter, doc_title, new_doc_filepath_xml, new_doc_filepath_html)    

        #SAVE PAGE DETAILS TO ADDITIONS DATAFRAME FOR RENDER IN EMAIL LATER
        Link = '<a href="file:///' + manual_dir + Chapter + '-' + version_date + '.html' + '" target="_blank">View</a>'
        dictionary_row = {"Manual":Manual.replace('-', ' ').title(),"Chapter":Chapter.upper(),"Title":doc_title,"Additions":Link}
        df_additions = df_additions.append(dictionary_row, ignore_index=True)
        log(str(dictionary_row))
        a+=1
        
        
    log('Looping through changes...')
    c = 1
    for change in changes:
        doc_id = change.get('id')
        doc_title = change.get('title')
        URI = change.get('uri')
        try: 
            Chapter = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(2)
            Manual = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(1)
        except AttributeError: continue

        #LOADING YESTERDAY AND TODAY'S VERSIONS WE HAVE STORED OF THE HMRC PAGES
        latest_filepath_xml = latest_dir + Manual + '\\' + Chapter + '.xml'
        previous_filepath_xml = previous_dir + Manual + '\\' + Chapter + '.xml'
        manual_dir = output_dir + Manual + '\\'
        if os.path.exists(manual_dir) == False: 
            os.mkdir(manual_dir)
            log('manual_dir did not exist, but now created...' + manual_dir)
        compared_filepath_xml = manual_dir + Chapter + '-' + version_date +'.xml'
        compared_filepath_html = manual_dir + Chapter + '-' + version_date +'.html'
        try: comparison_tree = etree.parse(latest_filepath_xml)
        except OSError: 
            log('File not found, skipping loop: ' + latest_filepath_xml)
            continue
        latest_tree = etree.parse(latest_filepath_xml)
        latest_root = latest_tree.getroot()
        previous_tree = etree.parse(previous_filepath_xml)
        
        #CLEANING UP BOTH TREES BEFORE COMPARISON
        strip_dodgy_characters(latest_tree)
        strip_dodgy_characters(previous_tree)
        previous_root = previous_tree.getroot()
        previous_data = previous_root.find('.//root')
        latest_data = latest_root.find('.//root')        
        strip_navigation(previous_data)
        strip_navigation(latest_data)
        log('Comparing the following two files...\n' + latest_filepath_xml + '\n' + previous_filepath_xml)
        
        #DIFF - GET REDLINE
        diffed_version = htmldiff(previous_data, latest_data) #Get the diff html from lxml built in method    
        diffed_version = diffed_version.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('&lt;', '<').replace('&gt;','>').replace('<ul><li></ul>', '')
        diffed_version = diffed_version.replace('<u>', '').replace('</u>', '')
        diffed_version = diffed_version.replace('<SOLS', '').replace('(SOLS)>', '')        
        diffed_version = re.sub(r'<img ([^>]*)>', r'<img \1 />', diffed_version)
        diffed_version = re.sub(r'<LPUTeam([^>]*)>', r'<p>LPUTeam\1 </p>', diffed_version)
        diffed_version = re.sub(r'<5x5x5gateway@DWP.GSI.GOV.UK.', r'5x5x5gateway@DWP.GSI.GOV.UK.', diffed_version)
        diffed_version = re.sub(r'<APA.mailbox@hmrc.gov.uk>', r'APA.mailbox@hmrc.gov.uk', diffed_version)
        diffed_version = re.sub(r'”', r'"', diffed_version)
        diffed_version = re.sub(r'<span [^>]*>', r'<span>', diffed_version)
        diffed_version = re.sub(r'<span>', '', diffed_version)
        diffed_version = re.sub(r'</span>', '', diffed_version)
        
        #INSERT DIFF HTML INTO SKELETON TREE - if there's a script failure it's usually here because of some dodgy tags that haven't been accounted for and that make the doc structurally invalid. Uncomment the print below to inspect further, then make search and replace directly above this line
        print(diffed_version)
        diff_data = etree.Element('data') #create xml shell
        try:
            diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell
        except:
            #print(diffed_version)
            diffed_version = '<div>' + diffed_version + '</div>'
            try:
                diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell
            except:
                log('Something wrong with this html, could not save...')
                log(str(diffed_version))
                continue #to the next iteration of the loop

        diff_tree = etree.ElementTree(diff_data)  #define the shell as the tree    
        diff_tree.write(compared_filepath_xml,encoding='utf-8') #write the tree out    
        log('Exported marked up changes to: ' + compared_filepath_xml)

        #CREATE WEBPAGE WITH 3 DIVS - 1 shows previous, 1 shows latest, 1 shows differences in redline
        convert_to_three_div_html(Chapter, doc_title, previous_filepath_xml, latest_filepath_xml, compared_filepath_xml, compared_filepath_html)
        
        #SAVE PAGE DETAILS TO ADDITIONS DATAFRAME FOR RENDER IN EMAIL LATER
        lev_dist = levenshtein_distance(str(ET.tostring(previous_root, encoding='utf-8', method='text')), str(ET.tostring(latest_root, encoding='utf-8', method='text')))
        threshold = 50
        if lev_dist > threshold: significant = True
        else: significant = False        
        Link = '<a href="file:///' + manual_dir + Chapter + '-' + version_date + '.html' + '" target="_blank">View</a>'
        dictionary_row = {"Manual":Manual.replace('-', ' ').title(),"Chapter":Chapter.upper(),"Title":doc_title,"AboveThreshold":significant,"Changes":Link}
        df_change = df_change.append(dictionary_row, ignore_index=True)
        log(str(dictionary_row))
        c+=1

    df_change = df_change.sort_values(['Manual'], ascending = True)
    df_change.to_csv(output_dir + "df_change.csv", sep=',',index=False, encoding='UTF-8')
    df_change = pd.read_csv(output_dir + "df_change.csv")

    df_additions = df_additions.sort_values(['Manual'], ascending = True)
    df_additions.to_csv(output_dir + "df_additions.csv", sep=',',index=False, encoding='UTF-8')
    df_additions = pd.read_csv(output_dir + "df_additions.csv")

    #CREATE HTML REPORT THAT IS THEN EMAILED
    create_html_report(report_date, str(len(changes)), df_change, str(len(additions)), df_additions, report_dir, report_filepath)

    Email(report_filepath, 'HMRC Updates Report: ' + report_date, receiver_email_list)
    log('Email sent to: ' + str(receiver_email_list))    
    
    log('Additions: ' + str(len(additions)))
    log('Changes: ' + str(len(changes)))
    log('Deletions: ' + str(len(deletions)))
        

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

    add_to_metrics_log(log_dir+'hmrc-metrics.csv', 1, 'HMRC report generated', 'Additions: ' + str(len(additions))+ ', Changes: ' + str(len(changes))+', Deletions: ' + str(len(deletions)))


else:   
    log("Today's date " + str(todays_date) + " not the same as the latest Crawl Report date " + str(crawl_report_date))    
    #EMAIL IF THERE WAS AN ERROR WITH THE CRAWL REPORT LOG
    Email(error_html_filepath, 'HMRC Updates Report: not generated', ['daniel.hutchings.1@lexisnexis.co.uk'])
    log('Email sent to: ' + str(['daniel.hutchings.1@lexisnexis.co.uk']))    