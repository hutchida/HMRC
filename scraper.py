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

PreviousDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
LatestDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
dfUpdates = pd.DataFrame()

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
    HTMLTree = etree.parse(xml)
    HTMLRoot = HTMLTree.getroot()
    divcenter.append(HTMLRoot.find('.//article'))

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
    
    latest_html_root = latest_tree.getroot()
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
#state = 'live'
state = 'livedev'

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

logDir = reportDir + 'logs\\'
ChangeDir = OutputDir + 'Changes\\'
AddDir = OutputDir + 'Additions\\'
DelDir = OutputDir + 'Deletions\\'

reportFilepath = reportDir + 'HMRC_report_'+reportDate+'.html'
errorHTMLFilepath = reportDir + 'HMRC_error_template.html'
sender_email = 'LNGUKPSLDigitalEditors@ReedElsevier.com'
mainUpdatesPage = 'https://www.gov.uk/government/latest?departments%5B%5D=hm-revenue-customs'
#TodaysDate = str(time.strftime("%#d %B %Y"))
TodaysDate = "26 March 2020"
version_date = datetime.datetime.strptime(str(datetime.date.fromtimestamp(os.path.getctime(CrawlReport))), '%Y-%m-%d').strftime('%Y%m%d')

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
        if Date == "27 March 2020": continue    #skip loop        
        if TodaysDate == Date:    
            link = listitem.xpath(".//a/@href")[0] 
            if "hmrc-internal-manuals" in link: #check it's a link type we want        
                try: 
                    manual = re.search('\/([^\/]*)\/([^\/]*)\/([^\/]*)', link).group(2)
                    chapter = re.search('\/([^\/]*)\/([^\/]*)\/([^\/]*)', link).group(3)
                except AttributeError: continue #exception raised skip this iteration and continue rest of loop
                doc_title = listitem.xpath(".//a/@href/text")[0] 
                #check if this chapter exists, if it doesn't scrape it and produce some html
                previous_filepath = PreviousDir + manual + '\\' + chapter
                found_term = False
                full_link = 'https://www.gov.uk' + link
                chapter_content = scrapedPage(full_link, ".//div[@class='manual-body']")
                if os.path.exists(previous_filepath + '.xml') == False: #if not in archive could mean it's new    
                    termlist = ['content has been withheld because of exemptions in the Freedom of Information Act', 'Page Archived']
                    for term in termlist:
                        if found_term == False: 
                            if str(etree.tostring(chapter_content[0])).find(term) > -1:  found_term = True
                    if found_term == True: update_type = 'deletion'
                    else: 
                        update_type = 'new'
                        manual_dir = output_dir + manual + '\\'
                        if os.path.exists(manual_dir) == False: 
                            os.mkdir(manual_dir)
                            print('manual_dir did not exist, but now created...' + manual_dir)
                            log('manual_dir did not exist, but now created...' + manual_dir)
                        new_doc_filepath = manual_dir + chapter + '-' + version_date
                        create_single_new_HTML_page(chapter, doc_title, chapter_content, new_doc_filepath) 
                else: 
                    update_type = 'change'                    
                    previous_filepath = PreviousDir + manual + '\\' + chapter
                    manual_dir = OutputDir + manual + '\\'
                    if os.path.exists(manual_dir) == False: 
                        os.mkdir(manual_dir)
                        print('manual_dir did not exist, but now created...' + manual_dir)
                        log('manual_dir did not exist, but now created...' + manual_dir)
                    compared_filepath = manual_dir + chapter + '-' + versionDate
                    
                    previous_tree = etree.parse(previous_filepath + '.xml')
                    latest_tree = chapter_content
                    stripDodgyCharacters(latest_tree)
                    stripDodgyCharacters(previous_tree)

                    previous_root = previous_tree.getroot()
                    previous_data = previous_root.find('.//root')
                    latest_root = latest_tree.getroot()
                    latest_data = latest_root.find('.//root')
                    
                    stripNavigation(previous_data)
                    stripNavigation(latest_data)

                    
                    print('Comparing...\n')
                    log('Comparing...\n')
                    
                    diffed_version = htmldiff(previous_data, latest_data) #Get the diff html from lxml built in method    
                    diffed_version = diffed_version.replace('<br>', '<br/>').replace('<hr>', '<hr/>').replace('&lt;', '<').replace('&gt;','>')                    
                    diffed_version = re.sub(r'<img ([^>]*)>', r'<img \1 />', diffed_version)
                    diff_data = etree.Element('data') #create xml shell
                    try:
                        diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell
                    except:
                        #print(diffed_version)
                        diffed_version = '<div>' + diffed_version + '</div>'
                        diff_root = diff_data.insert(0, etree.fromstring(diffed_version)) #insert diff html into shell

                    diff_tree = etree.ElementTree(diff_data)  #define the shell as the tree    
                    diff_tree.write(compared_filepath + '.xml',encoding='utf-8') #write the tree out    
                    print('Exported marked up changes to: ' + compared_filepath + '.xml')
                    log('Exported marked up changes to: ' + compared_filepath + '.xml')
                    create_comparison_HTML_page(chapter, doc_title, previous_filepath, latest_tree, compared_filepath)
                    
                    levDist = levenshtein_distance(str(ET.tostring(previous_root, encoding='utf-8', method='text')), str(ET.tostring(latest_root, encoding='utf-8', method='text')))
                    threshold = 50
                    if levDist > threshold: significant = True
                    else: significant = False

                    lexis_link = '<a href="file:///' + manual_dir + chapter + '-' + versionDate + '.html' + '" target="_blank">View</a>'

                
                dictionary_row = {"Manual":manual.replace('-', ' ').title(),"Chapter":chapter.upper(),"Title":doc_title,"UpdateType":update_type, "PageNumber":page_number, "HMRC":full_link, "Lexis":lexis_link, "AboveThreshold":significant}#, "PrevFilepath": previous_filepath_xml}
                dfUpdates = dfUpdates.append(dictionary_row, ignore_index=True)
                print(dictionary_row)
        else: 
            reachedTheEndOfTheDay = True
            print('New date encountered, breaking out of loop: ', Date)
            break
    currentUpdatesPage = nextPageURL

    dfUpdates.to_csv("dfUpdates.csv", sep=',',index=False, encoding='UTF-8')


