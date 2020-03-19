
import sys
import pandas as pd
import numpy as np
import time
import timeit
import httplib2
import requests
import xml.etree.ElementTree as ET
from lxml import etree
from bs4 import BeautifulSoup, SoupStrainer
import csv
import os
import glob
import datetime
import re
import string
import difflib
from difflib import ndiff
from docx import Document
import win32com.client
import pypandoc
from lxml.html.diff import htmldiff

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

def ConvertToWordDoc(InputFilepath, OutputFilepath):
    print(InputFilepath)
    print(OutputFilepath)
    word = win32com.client.Dispatch('Word.Application')
    doc = word.Documents.Add(InputFilepath)
    doc.SaveAs(OutputFilepath, FileFormat=0)
    doc.Close()
    word.Quit()
    print('Exported: ' + OutputFilepath)

def GenerateWordTrackChangesDoc(Doc1Filepath, Doc2Filepath, CompFilepath):
    Application=win32com.client.gencache.EnsureDispatch("Word.Application")
    #Application=win32com.client.Dispatch('Word.Application')
    Application.CompareDocuments(Application.Documents.Open(Doc1Filepath), Application.Documents.Open(Doc2Filepath))
    #Application.ActiveDocument.ActiveWindow.View.Type = 3 # prevent that word opens itself
    Application.ActiveDocument.SaveAs(CompFilepath)
    Application.Documents.Close()
    Application.Quit()
    print('Exported: ' + CompFilepath)

def ConvertBackToXML(Filepath):
    print('Converting word track changes doc back to xml: ' + Filepath)

def ConvertTrioHtml(Chapter, DocTitle, PreviousFilepathXML, LatestFilepathXML, ComparedFilepathXML, ComparedFilepathHTML):
    html = etree.Element('html')
    head = etree.SubElement(html, 'head')
    meta = etree.SubElement(head, 'meta')
    meta.set('http-equiv', 'Content-Type')
    meta.set('content', 'text/html; charset=utf-8')
    link = etree.SubElement(head, 'link') #local css
    link.set('rel', 'stylesheet')
    link.set('type', 'text/css')
    link.set('href', 'css/style.css')
    link = etree.SubElement(head, 'link') #bootstrap
    link.set('rel', 'stylesheet')
    link.set('href', 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')
    link.set('itegrity', 'sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm')
    link.set('crossorigin', 'anonymous')

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
    divleft.set('contenteditable', 'true')
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
    divmid.set('contenteditable', 'true')
    divmid.set('class', 'container')
    divmid.set('style', 'width: 33%; height: 0%; float:center;')        
    h3 = etree.SubElement(divmid, 'h3')
    h3.text = 'Latest version'    
    hr = etree.SubElement(divmid, 'hr')    
    LatestHTMLTree = etree.parse(LatestFilepathXML)
    LatestHTMLRoot = LatestHTMLTree.getroot()
    divmid.append(LatestHTMLRoot.find('.//article'))

    divright = etree.SubElement(divmain, 'div')
    divright.set('contenteditable', 'true')
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

def CustomDiff():
    #deconstruct xml into dictionaries for comparison later        
    dictNew = {}
    dictOld = {}
    d=0
    for elem in LatestTree.iter():    
        dictNew.update({d: [elem, elem.tag, elem.text, elem.tail]})
        d+=1

    d=0
    for elem in PreviousTree.iter():    
        dictOld.update({d: [elem, elem.tag, elem.text, elem.tail]})
        d+=1

    print('dictNew len: ' + str(len(dictNew)))
    print('dictOld len: ' + str(len(dictOld)))

    #Discovering insertions
    for entry in dictNew:      
        try:
            if dictNew[entry][2] != dictOld[entry][2]: #change detected
                if dictNew[entry][2] is not None:
                    #print(htmldiff(dictNew[entry][0], dictOld[entry][0])) #get html diff
                    found = 0
                    for x in range(0,len(dictOld)): #test new para not found in old doc

                        if dictNew[entry][2] == dictOld[x][2]: found +=1
                    if found == 0:
                        #print(dictNew[entry][2])
                        #print('Para not found in old doc, must be brand new, marking up...')
                        for elem in CompTree.iter(): #Loop through copy of latest xml doc looking for element with the latest text, update that element         
                            if elem.text is not None:
                                if elem.text == dictNew[entry][2]:
                                    elemTemp = etree.Element(dictNew[entry][1]) #recreate the tag
                                    span = etree.SubElement(elemTemp, 'span')   #add span
                                    span.set('class', 'insertion')
                                    span.text = elem.text                       #add text
                                    elem.addprevious(elemTemp)                  #add reconstructed element before current element
                                    elem.getparent().remove(elem)               #delete current element

            #elif str(dictNew[entry][3]) != str(dictNew[entry][3]):
            #    print(dictNew[entry][2], dictNew[entry][3])
            #    print(dictOld[entry][2], dictOld[entry][3])
        except KeyError: print('EXCEPTION: KEY ERROR 1')

    #Discovering deletions
    for entryOld in dictOld:    

        found = 0
        for entryNew in dictNew:
            if dictNew[entry][2] is not None:
                if dictOld[entryOld][2] == dictNew[entryNew][2]: found += 1
        if found == 0: 
            #append to list item 4 whether this element found in new doc
            dictOld[entryOld].append(False) 
        else: 
            dictOld[entryOld].append(True)

    #append to list item 5 whether current element is a deletion marker, i.e. first element before where a deleted element once was
    for entryOld in dictOld:               
        try:
            if dictOld[entryOld + 1][4] == False: #if next element is False it means a series of deletions is about to start and that this element is the deletion marker
                dictOld[entryOld].append(True) #append to 6th item to say this element IS a deletion marker
                listOfElements = []
                for x in range(entryOld + 1,len(dictOld)): #from next element position up to the end of the dict
                    if dictOld[x][4] == False:  #if False it means it's a deleted para
                        listOfElements.append(dictOld[x][0]) #append deleted para element to temp list
                        if dictOld[x+1][4] == True: #if next element is True it means the series of deleted paras has finished, so break out of this loop
                            break
                dictOld[entryOld].append(listOfElements) #append temp list to 7th item in list
            else: 
                dictOld[entryOld].append(False) #append False to 6th item in list to say this element is NOT a deletion marker
                dictOld[entryOld].append(None) #append default None to 7th item in list

        except KeyError: print('EXCEPTION: KEY ERROR 2')

    #inserting deletions into the comp doc after the elements where they used to be, span red
    for elem in CompTree.iter(): #Loop through copy of latest xml doc which is our comp doc 
        for entryOld in dictOld:   

            if elem.text is None:                    
                if elem.tag == dictOld[entryOld][1]: #match tags
                    elemChildren = elem.getchildren()
                    try: firstElem = elemChildren[0].xpath("span[@class='insertion']")
                    except: firstElem = []
                    if len(firstElem) > 0: 

                    #print(ET.tostring(firstElem[0]))
                        if dictOld[entryOld][5] == True: #deletion marker, so insert after
                            print('First elem present')
                            print(firstElem)
                            ellipsis = etree.Element('p')
                            ellipsis.text = ' . . . '
                            elem.addprevious(ellipsis)
                            for item in dictOld[entryOld][6][::-1]: #backwards for loop, reverse iteration [::-1]
                                #print(item.text)
                                elemTemp = etree.Element(item.tag) #recreate the tag
                                span = etree.SubElement(elemTemp, 'span')   #add span
                                span.set('class', 'deletion')
                                span.text = item.text                       #add text
                                elem.addprevious(elemTemp)                  #add reconstructed element after current element

                            #elem.getparent().remove(elem)               #delete current element
            else:
                if elem.text == dictOld[entryOld][2]:
                    try: #this triggers exception when it gets to last item in dict which doesn't have a 5th or 6th item, need to fix later
                        if dictOld[entryOld][5] == True: #deletion marker, so insert after
                            ellipsis = etree.Element('p')
                            ellipsis.text = ' . . . '
                            for item in dictOld[entryOld][6][::-1]: #backwards for loop, reverse iteration [::-1]
                                #print(item.text)
                                elemTemp = etree.Element(item.tag) #recreate the tag
                                span = etree.SubElement(elemTemp, 'span')   #add span
                                span.set('class', 'deletion')
                                span.text = item.text                       #add text
                                elem.addnext(elemTemp)                  #add reconstructed element after current element
                            elem.addnext(ellipsis) 
                            #elem.getparent().remove(elem)               #delete current element
                    except IndexError: print('FIX LAST ITEM IN DICT')

             #print(dictOld[entryOld])


    #CompTree.write(ComparedFilepathXML,encoding='utf-8')



CrawlReportDir = "\\\\atlas\\Knowhow\\AutomatedContentReports\\HMRCrawlReports\\"
#CrawlReportDir = "HMRCrawlReports\\"
LatestDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Data_RX\\data\\www.gov.uk\\hmrc-internal-manuals\\"
#LatestDir = "latest\\hmrc-internal-manuals\\"
PreviousDir = "\\\\lngoxfdatp16vb\\Fabrication\\build\\02HT\\Yesterdays_Archive\\data\\www.gov.uk\\hmrc-internal-manuals\\"
#PreviousDir = "previous\\hmrc-internal-manuals\\"
CrawlReport = FindMostRecentFile(CrawlReportDir, '*xml')
#OutputDir = "dev\\www\\"
OutputDir = "C:\\GIT\\HMRC\\dev\\www\\"
ChangeDir = OutputDir + 'Changes\\'
AddDir = OutputDir + 'Additions\\'
DelDir = OutputDir + 'Deletions\\'
print(CrawlReport)

CrawlRoot = ET.parse(CrawlReport)
additions = CrawlRoot.findall('added/document')
changes = CrawlRoot.findall('changed/document')
deletions = CrawlRoot.findall('removed/document')

c = 1
for change in changes:
    DocID = change.get('id')
    DocTitle = change.get('title')
    URI = change.get('uri')
    try: 
        Chapter = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(2)
        ManualName = re.search('https:\/\/www\.gov\.uk\/hmrc-internal-manuals\/([^\/]*)\/(.*$)', URI).group(1)
    except AttributeError: continue

    #.replace('-', ' ').title()
    LatestFilepathXML = LatestDir + ManualName + '\\' + Chapter + '.xml'
    PreviousFilepathXML = PreviousDir + ManualName + '\\' + Chapter + '.xml'
    ComparedFilepathXML = OutputDir + Chapter + '-comp.xml'
    ComparedFilepathHTML = OutputDir + Chapter + '-comp.html'
    LatestFilepathDoc = OutputDir + Chapter + '-new.doc'
    PreviousFilepathDoc = OutputDir + Chapter + '-old.doc'
    ComparedFilepathDoc = OutputDir + Chapter + '-comp.doc'
    CompTree = etree.parse(LatestFilepathXML)
    LatestTree = etree.parse(LatestFilepathXML)
    LatestRoot = LatestTree.getroot()
    #etree.strip_tags(LatestRoot, 'nav')
    PreviousTree = etree.parse(PreviousFilepathXML)
    PreviousRoot = PreviousTree.getroot()
    #etree.strip_tags(PreviousRoot, 'nav')
    print(LatestFilepathXML)
    print(PreviousFilepathXML)

    #deconstruct xml into dictionaries for comparison later        
    #CustomDiff()
    #CompTree.write(ComparedFilepathXML,encoding='utf-8')
    print(PreviousRoot.find('.//root'), LatestRoot.find('.//root'))
    DiffedVersion = htmldiff(PreviousRoot.find('.//root'), LatestRoot.find('.//root')) #Get the diff html from lxml built in method    
    print(DiffedVersion)
    DiffedVersion = DiffedVersion.replace('<br>', '<br/>').replace('<hr>', '<hr/>')
    diffData = etree.Element('data') #create xml shell
    try:
        diffRoot = diffData.insert(0, etree.fromstring(DiffedVersion)) #insert diff html into shell
    except:
        DiffedVersion = '<div>' + DiffedVersion + '</div>'
        print(DiffedVersion)
        diffRoot = diffData.insert(0, etree.fromstring(DiffedVersion)) #insert diff html into shell
        
    
    
    Difftree = etree.ElementTree(diffData)  #define the shell as the tree    
    Difftree.write(ComparedFilepathXML,encoding='utf-8') #write the tree out    
    print('Exported to: ' + ComparedFilepathXML)

    print('Changes: ' + str(c) + ' of ' + str(len(changes)))
    ConvertTrioHtml(Chapter, DocTitle, PreviousFilepathXML, LatestFilepathXML, ComparedFilepathXML, ComparedFilepathHTML)
    #wait = input("PAUSED...when ready press enter")
        

    #xmlstr = ET.tostring(LatestRoot.getroot(), encoding='utf8', method='xml')
    #print(xmlstr)
    #WORD
    #ConvertToWordDoc(LatestFilepathXML, LatestFilepathDoc)
    #ConvertToWordDoc(PreviousFilepathXML, PreviousFilepathDoc)
    #GenerateWordTrackChangesDoc(LatestFilepathDoc, PreviousFilepathDoc, ComparedFilepathDoc)
    #ConvertBackToXML(ComparedFilepathDoc)
    #print(output)
    
    
    c+=1



print('Additions: ' + str(len(additions)))
print('Changes: ' + str(len(changes)))
print('Deletions: ' + str(len(deletions)))