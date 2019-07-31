
import sys
import pandas as pd
import numpy as np
import time
import timeit
import httplib2
import requests
from bs4 import BeautifulSoup, SoupStrainer
import csv
import os
import glob
import datetime
import re
import string
import difflib
from difflib import ndiff

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents.

def list_comparison(logpath, xmldir1, xmldir2):
    print('Building xml list1...')
    df1 = pd.DataFrame({'col':os.listdir(xmldir1)})
    df1.to_csv(logpath+'old.csv', sep=',',index=False)
    print('Building xml list2...')
    df2 = pd.DataFrame({'col':os.listdir(xmldir2)})
    df2.to_csv(logpath+'new.csv', index=False)
    
    
    df1 = pd.read_csv(logpath+'old.csv')
    df2 = pd.read_csv(logpath+'new.csv')
    



    dfdel = pd.DataFrame(columns=['col'])
    for index, item in df1.itertuples():  #loop through each item in the older list
        if any(df2.col == item) == False: #if the older list item doesn't appear in the newer list, it must have been deleted
            dfdel.loc[len(dfdel)] = [item] #add item to end of fresh dataframe
            
    dfdel.to_csv(logpath+'deletions.csv', index=False)
    print('Exported deletions...')
    
    dfadd = pd.DataFrame(columns=['col'])
    for index, item in df2.itertuples(): #loop through each item in the newer list
        if any(df1.col == item) == False: #if the newer list item doesn't appear in the older list, it must have been added
            dfadd.loc[len(dfadd)] = [item] #add item to end of fresh dataframe
    
    dfadd.to_csv(logpath+'additions.csv', index=False)
    print('Exported additions...')
    
    dfrem1 = pd.DataFrame(columns=['col'])
    for index, item in df1.itertuples(): #loop through each item in the older list
        if any(dfdel.col == item) == False: #if the older item doesn't appear in the deleted list, must appear on both new and old lists
            dfrem1.loc[len(dfrem1)] = [item] #add item to end of fresh dataframe
    
    dfrem1.to_csv(logpath+'rem1.csv', index=False)
    print('Exported remainder version 1...')
    
    dfrem2 = pd.DataFrame(columns=['col'])
    for index, item in df2.itertuples(): #loop through each item in the older list
        if any(dfadd.col == item) == False: #if the older item doesn't appear in the deleted list, must appear on both new and old lists
            dfrem2.loc[len(dfrem2)] = [item] #add item to end of fresh dataframe
    
    dfrem2.to_csv(logpath+'rem2.csv', index=False)
    print('Exported remainder version 2...')

    

def Export(logpath):    
    print("Exporting to html...")
    pd.set_option('display.max_colwidth', -1) #stop the dataframe from truncating cell contents. This needs to be set if you want html links to work in cell contents
    dfdel = pd.read_csv(logpath+'deletions.csv') #read in the csv file
    dfadd = pd.read_csv(logpath+'additions.csv')
    dfchange = pd.read_csv(logpath+'change.csv')
    dfdelHTML = dfdel.to_html(na_rep = " ", index=False, header=False)
    dfaddHTML = dfadd.to_html(na_rep = " ", index=False, header=False)

    html = r'<html><head><link rel="stylesheet" type="text/css" href="style.css"/><style></style></head>'
    html += '<h1 id="home">HMRC updates</h1><hr />'
    html += '<p>' + str(len(dfdel)) + ' deletions found. <a href="deletions.csv" target="_blank">Download</a>.</p>'
    html += '<p>' + str(len(dfadd)) + ' additions found. <a href="additions.csv" target="_blank">Download</a>.</p>'
    html += '<p>' + str(len(dfchange)) + ' changes found. <a href="changes.html" target="_blank">View changes</a>. WARNING: a large amount of changes will mean a large page to load, be patient.</p>'
    html += '<hr /><h2>Deletions</h2>' + dfdelHTML
    html += '<hr /><h2>Additions</h2>' + dfdelHTML
    html = html.replace('&lt;', '<').replace('&gt;', '>').replace('\\', '/')#.replace('—', ' ').replace('’',"'")
        

    with open(logpath + "\\overview.html",'w', encoding='utf-8') as f:
        f.write(html)
        f.close()
        pass
    
    print ("HTML generated at: " + logpath + "\\overview.html")




def Prelim(xmldir1, xmldir2, logpath, start):
    #list_comparison(logpath, xmldir1, xmldir2)
        
    dfrem = pd.read_csv(logpath+'rem1.csv')
    dfchange = pd.DataFrame(columns=['col'])
    i = 0
    for index, item in dfrem.itertuples(): #loop through each item in the remainder list
        while True:
            try:
                oldbytecount = os.path.getsize(xmldir1 + item)
                newbytecount = os.path.getsize(xmldir2 + item)
                if oldbytecount != newbytecount: 
                    dfchange.loc[len(dfchange)] = [item] #add item to end of fresh dataframe
                    dfchange.to_csv(logpath+'change.csv', index=False)
                    print(i, item)                
                    print("\nTime taken so far..." + str(datetime.datetime.now() - start))
                    
            
                i = i + 1
            except FileNotFoundError:
                var = input("Network failure: please make sure you're reconnected to the network and press return when ready")






def Snapshot(date, logdate, logname, xmldir, logpath):
    print("Entering Snapshot...")
    df = pd.DataFrame()
    dfchange = pd.read_csv(logpath+'change.csv')
    i = 0
    for index, item in dfchange.itertuples(): #loop through each item in the remainder list
        try:
            filename = xmldir + str(dfchange.iloc[i,0])
            print(i, filename)   
                
            #Get date stamp of opened file
            try: mtime = os.path.getmtime(filename)
            except OSError: mtime = 0    
            last_modified_date = str(datetime.date.fromtimestamp(mtime))
            logdate = str(logdate)
    
            #Import xml file into soup
            soup = BeautifulSoup(open(filename), 'lxml') 
            #print(soup)
            while True: 
                h = soup.find('h')
                if not h:
                    break
                h.name = 'text'
            #print(soup)
    
            try: title = soup.find("docinfo:doc-heading").text
            except AttributeError: title = ("NA")    
            try: chapnumber = soup.find("ci:content").text
            except AttributeError: chapnumber = ("NA")     
    
            k = 0
            #loop through all the para numbers in the doc    
            ps = soup.find_all('text')
            for p in ps:  
                if len(p.text) > 1:
                    para = p.text
                    key = chapnumber + '_' + str(k)
                    if para != '':
                        if ']>' not in para:
                            if 'Previous page' not in para:
                                if 'Next page' not in para:
                                    k = k + 1
                                    list1 = [[key, filename, last_modified_date, chapnumber, title, para]]#, logdate]]
                                    #print(list1)
                                    df = df.append(list1)
                

            print("\nTime taken so far..." + str(datetime.datetime.now() - start))
                
                
        except FileNotFoundError: pass
            #var = input("Network failure: please make sure you're reconnected to the network and press return when ready")
        i = i + 1
    df.to_csv((logpath+logname), sep=',',index=False,header=["Key", "Filename", "LMD", "ChapterNumber", "Title", "Para"], encoding="UTF8")
    print("Exported to..." + logpath + logname)
   
    

def HTMLExport(new_len, del_len, change_len, df_new, df_del, df_final, filters, exportfilepath):
    #build html
    css = """<head>            
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <style>td {
                word-wrap: break-word;
                min-width: 160px;
                max-width: 160px;
                }</style>
            </head>"""
    menu = '<p><a href="index.html">No Filter</a> | <a href="relevance.html">+ Relevance Filter</a> | <a href="parashift.html">+ Para Shift Filter</a> | <a href="levchar.html">+ Levenshtein Distance & Character Count Difference Filter</a></p>'

    bootstrap = '<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">'
    html = '<div class="container">'
    html += bootstrap + r'<link rel="stylesheet" type="text/css" media="screen" />'+ '\n' + css
    html += '<h1 id="home">' + source + ' UPDATES OVERVIEW: <b>' + filters + '</b></h1>' 
    html += menu + '<hr />'
    html += '<p>This is a comparison between the HMRC data sets for July and August 2018.</p>' 
    html += '<p>Filters: <b>' + filters + '</b></p>' 
    html += '<div style="max-width: 800px;">' 
    html += r'<p><b>' + new_len + '</b> new paras have been added, <a href="#new">see here</a></p>' 
    html += r'<p><b>' + del_len + '</b> paras have been deleted, <a href="#del">see here</a></p>'
    html += r'<p><b>' + change_len + '</b> changes have been found, <a href="#change">see here</a></p>'
    html += r'</div><div style="max-width: 800px;"><h1 id="new">ADDITIONS</h1><p>' + new_len + ' new paras have been added and are displayed below, (<a href="#home">scroll to top</a>)</p>'
    #html += df_new.style.render()
    html += df_new.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover")
    html += r'</div><div style="max-width: 800px;"><h1 id="del">DELETIONS</h1><p>' + del_len + ' paras have been deleted and are displayed below, (<a href="#home">scroll to top</a>)</p>'
    #html += df_del.style.render()
    html += df_del.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover")
    html += r'</div><div style="max-width: 800px;"><h1 id="change">CHANGES</h1><p>' + change_len + ' changes have been made and are displayed below, (<a href="#home">scroll to top</a>)</p>'
    #html += df_final.style.apply(highlight_diff, axis=None).render()
    html += df_final.to_html(na_rep = " ",index = False,  classes="table table-bordered text-left table-striped table-hover")
    html += '</div></div>'

    #write to html
    print("Exported HTML to...", exportfilepath)
    with open(exportfilepath,'w', encoding='utf-8') as f:
        f.write(html)
        f.close()
        pass
    
    
def Comparison(logpath, source, maindir):   
    logslist = sorted(glob.iglob(os.path.join(logpath, '*.csv')), key=os.path.getmtime, reverse=True) 
    lognew = logslist[0] #most recent report
    logold = logslist[1] #second most recent report

    print("Opening two most recent logs files...")
    df1 = pd.read_csv(logold, encoding ='utf-8')
    df2 = pd.read_csv(lognew, encoding ='utf-8')

    #print("older log (df1) number of rows before cull: " + str(len(df1)))
    #print("newer log (df2) number of rows before cull: " + str(len(df2)))
    print("Discovering additions and deletions...")

    #find new
    df_new = pd.merge(df1,df2, on='Key', how='outer', indicator=True)

    #print("Extracting new paras only...")
    df_new = df_new.ix[df_new['_merge']=='right_only']
    #delete newly generated columns from the merge function that we don't need
    del df_new['Filename_x']
    del df_new['LMD_x']
    del df_new['ChapterNumber_x']
    del df_new['Title_x']
    del df_new['Para_x']
    del df_new['_merge']
    df_new = df_new.rename(columns={'Filename_y': 'Filename', 'LMD_y': 'LMD', 'ChapterNumber_y': 'ChapterNumber', 'Title_y': 'Title', 'Para_y': 'Para'})

    new_len = str(len(df_new.index))
    #print("Removing new rows from the latest dataframe in order to do a valid comparison...")
    print("Number of new paras added: ", new_len)

    for x in range(len(df_new.index)):
        key = df_new['Key'].iloc[x]
        df2 = df2[df2['Key'] != key]

    #removing superfluous columns for final presentation
    del df_new['Key']

    #resetting the index after row removal
    df2 = df2.reset_index(drop=True)

    #to find deleted paras do it the same way but swap the dfs around
    df_del = pd.merge(df2,df1, on='Key', how='outer', indicator=True)

    #print("Extracting deleted paras only...")
    df_del = df_del.ix[df_del['_merge']=='right_only']

    #delete newly generated columns from the merge function that we don't need
    del df_del['Filename_x']
    del df_del['LMD_x']
    del df_del['ChapterNumber_x']
    del df_del['Title_x']
    del df_del['Para_x']
    del df_del['_merge']
    df_del = df_del.rename(columns={'Filename_y': 'Filename', 'LMD_y': 'LMD', 'ChapterNumber_y': 'ChapterNumber', 'Title_y': 'Title', 'Para_y': 'Para'})

    del_len = str(len(df_del.index))
    #print("Removing deleted rows from the previous dataframe in order to do a valid comparison...")
    print("Number of paras deleted: ", del_len)

    for x in range(len(df_del.index)):
        pattern = df_del['Key'].iloc[x]
        df1 = df1[df1['Key'] != pattern]

    #removing superfluous columns for final presentation
    del df_del['Key']

    #resetting the index after row removal
    df1 = df1.reset_index(drop=True)

    #print('Removing spaces at the end of strings...')
    df1['Para'] = df1['Para'].str.replace(" ^", "")
    df2['Para'] = df2['Para'].str.replace(" ^", "")
    df1['Para'] = df1['Para'].str.replace(" $", "")
    df2['Para'] = df2['Para'].str.replace(" $", "")

    print('Number of potentially changed paras in HMRC: ', str(len(df1)))
#COMPARISON - with the new and deleted paras removed, we can now do a valid comparison of what remains
    #print("Merging paras that both logs share...")
    df = pd.concat([df1, df2], axis='columns', keys=['Previous', 'Current'])

    #swap columns around so they're next to eachother, easier to spot the difference
    df_final = df.swaplevel(axis='columns')[df1.columns[0:]]


    #compare previous and current and mark in new column whether any change
    def f(x):
       state = "no"
   
       #test for chapter number change
       prev = str(x['ChapterNumber','Previous'])
       curr = str(x['ChapterNumber','Current'])
       if  prev and curr != 'nan':
            if prev != curr:
                state = 'yes'
            else:
                state = 'no'
       else:
            state = 'no'   

       if state == 'no':
            #test for title change
            prev = str(x['Title','Previous'])
            curr = str(x['Title','Current'])
            if  prev and curr != 'nan':
                if prev != curr:
                    state =  'yes'
                else:
                    state =  'no'
            else:
                state =  'no'

       if state == 'no':
            #test for para change
            prev = str(x['Para','Previous'])
            curr = str(x['Para','Current'])
            if  prev and curr != 'nan':
                if prev != curr:
                    state =  'yes'
                else:
                    state =  'no'
            else:
                state =  'no'


       if state == 'no': return 'no' 
       else: return 'yes'


    #print("Adding new column to show whether a change is present...")
    df_final['Changed'] = df_final.apply(f, axis=1)


    # Filter the data by new column that indicates changes
    df_final = df_final[df_final['Changed'] == 'yes']


    change_len = str(len(df_final.index))
    print("Number of changes found after comparing paras and paranumbers: " + change_len)


    del df_new['Filename']
    del df_new['LMD']

    del df_del['Filename']
    del df_del['LMD']

    del df_final['Filename']
    del df_final['Key']
    del df_final['LMD']
    del df_final['Changed']
    del df_final['ChapterNumber']
    df_final.insert(0, 'ChapterNum', df1['ChapterNumber'])

    #Exporting useful dataframes to csv
    df_new.to_csv(outputdir + source + "_additions_nofilter.csv", sep=',',index=False)
    df_del.to_csv(outputdir + source + "_deletions_nofilter.csv", sep=',',index=False)
    df_final.to_csv(outputdir + "\\" + source + "_changes_nofilter.csv", sep=',',index=False)
            
    #no filters    
    HTMLExport(new_len, del_len, change_len, df_new, df_del, df_final, 'NO FILTER APPLIED', outputdir + 'index.html')



    #Check whether chapter number appears on the list of hmrc links actually in use
    def Relevant(x):
        if any(dfreference.Pattern == x.ChapterNumber) == True:
            return True
        else:
            return False
        
    dfreference = pd.read_csv(maindir + 'hmrc-patterns-locations-28252019.csv', encoding ='utf-8')
    
    print('Number of HMRC links in use on PSL: ', str(len(dfreference)))

    #print("Adding new column to show whether a change is relevant, then filtering out irrelevant rows...")

    df1['Relevant'] = df1.apply(Relevant, axis=1)
    df2['Relevant'] = df2.apply(Relevant, axis=1)    
    df1 = df1[df1['Relevant'] == True]
    df2 = df2[df2['Relevant'] == True]    

    #ParaShift filter   

    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)
    df3 = pd.DataFrame()
    #df1.to_csv(outputdir + "df1.csv", sep=',')
    #df2.to_csv(outputdir + "df2.csv", sep=',') 

    i=0
    for index, row in df1.iterrows(): 
        ParaDf1 = df1.Para.iloc[i]
        try: ParaDf2 = df2.Para.iloc[i+1] #Index error will be thrown when the loop reaches the last row and there is no row plus one to access, at which point exit the loop
        except IndexError: continue

        if ParaDf1 == ParaDf2:
            row = {"ParaShifted": 'True'}
        else:
            ParaDf1 = df1.Para.iloc[i]
            ParaDf2 = df2.Para.iloc[i+2]
            if ParaDf1 == ParaDf2:
                row = {"ParaShifted": 'True'}
            else:
                ParaDf1 = df1.Para.iloc[i]
                ParaDf2 = df2.Para.iloc[i+3]
                if ParaDf1 == ParaDf2:
                    row = {"ParaShifted": 'True'}
                else:
                    row = {"ParaShifted": 'False'}
        if ParaDf1 == 'Capitalised amounts':
            print(ParaDf1, ParaDf2, row)
            
        df3 = df3.append(row, ignore_index=True) 
        #df_final.iloc[i, 3] = 'False' #df.columns.get_loc('ParaShifted')
        i=i+1
    row = {"ParaShifted": 'False'} #Add one more row to the end    
    df3 = df3.append(row, ignore_index=True) 

    df = pd.concat([df1, df2], axis='columns', keys=['Previous', 'Current'])
    df_final = df.swaplevel(axis='columns')[df1.columns[0:]]
    df3 = df3.reset_index(drop=True)
    df_final = df_final.reset_index(drop=True)
    df_final['ParaShifted'] = df3['ParaShifted']  
    df_final['Changed'] = df_final.apply(f, axis=1)
    df_final = df_final[df_final['Changed'] == 'yes']
    df_final_parashift = df_final
    del df_final_parashift['ChapterNumber']
    df_final_parashift.insert(0, 'ChapterNum', df1['ChapterNumber'])
    
    change_len = str(len(df_final.index))

    print('Number of relevant paras after cross referencing with list of PSL HRMC references: ', change_len)


    del df_final['Filename']
    del df_final['Key']
    del df_final['LMD']
    del df_final['Changed']
    del df_final['Relevant']
    #del df_final['ChapterNumber']
    #del df_final['ParaShifted']
    #df_final.insert(0, 'ChapterNum', df1['ChapterNumber'])

    df_final_parashift.to_csv(outputdir + "df_final_parashift.csv", sep=',')

    #Exporting useful dataframes to csv
    print("Exporting useful dataframes to csv in dated folder...")
    df_new.to_csv(outputdir + source + "_additions_relevance.csv", sep=',',index=False)
    df_del.to_csv(outputdir + source + "_deletions_relevance.csv", sep=',',index=False)
    df_final.to_csv(outputdir + "\\" + source + "_changes_relevance.csv", sep=',',index=False)
             
    HTMLExport(new_len, del_len, change_len, df_new, df_del, df_final, 'RELEVANT CHAPTERS ONLY', outputdir + 'relevance.html')

    #print(str(len(df1)), str(len(df2)), str(len(df_final)))

    #df3 = df3.reset_index(drop=True)
    #df_final = df_final.reset_index(drop=True)
    #df_final['ParaShifted'] = df3['ParaShifted']  
    
    #print(df_final)   
    #df_final.insert(5, 'ParaShifted', df3['ParaShifted'])
    # Filter the data by new column that indicates changes
    df_final_parashift = df_final_parashift[df_final_parashift['ParaShifted'] == 'False']
    
    #del df_final['Filename']
    #del df_final['Key']
    #del df_final['LMD']
    #del df_final['Changed']
    #del df_final['Relevant']
    #del df_final['ChapterNumber']
    #del df_final['ParaShifted']    
    #df_final.insert(0, 'ChapterNum', df2['ChapterNumber'])
    #wait = input("PAUSED...when ready press enter")

    #compare previous and current character lengths of the paras and return difference
    def CharacterCountDiff(x):        
        prev = len(str(x['Para','Previous']))
        curr = len(str(x['Para','Current']))
        #print(prev, curr)
        if prev == curr:
            CharCount = 0
        else:
            if prev > curr: 
                CharCount = prev - curr
            else: 
                if curr > prev: 
                    CharCount = curr - prev
                else: CharCount = ''
        #print(CharCount) 
        return CharCount


    #print("Adding new column to show the character count difference between paragraphs...")
    df_final_parashift['CharacterCountDifference'] = df_final_parashift.apply(CharacterCountDiff, axis=1)

    def levenshtein_distance(x):
        counter = {"+": 0, "-": 0}
        distance = 0
        for edit_code, *_ in ndiff(str(x['Para','Previous']), str(x['Para','Current'])):
            if edit_code == " ":
                distance += max(counter.values())
                counter = {"+": 0, "-": 0}
            else: 
                counter[edit_code] += 1
        distance += max(counter.values())
        return distance
    
    #print("Adding new column to show the Levenshtein Distance between paragraphs...")
    df_final_parashift['LevenshteinDistance'] = df_final_parashift.apply(levenshtein_distance, axis=1)

    
    def levchar_algorithm(x):
        charcountdiff = int(x['CharacterCountDifference'])
        levdist = int(x['LevenshteinDistance'])
        print(str(charcountdiff), str(levdist))
        if charcountdiff < 10:
            if levdist > charcountdiff + 10:
                return True
            else: 
                return False
        else: return True
    
    #print("Adding new column to show the Levenshtein Distance between paragraphs...")
    df_final_parashift['AboveLevCharThreshold'] = df_final_parashift.apply(levchar_algorithm, axis=1)

    
    change_len = str(len(df_final_parashift.index))
    print('Number of relevant paras after the para shift analysis: ', change_len)


    #Exporting useful dataframes to csv
    df_new.to_csv(outputdir + source + "_additions_parashift.csv", sep=',',index=False)
    df_del.to_csv(outputdir + source + "_deletions_parashift.csv", sep=',',index=False)
    df_final_parashift.to_csv(outputdir + "\\" + source + "_changes_parashift.csv", sep=',',index=False)
            
    #Relevant chapters and Para Shift filters    
    HTMLExport(new_len, del_len, change_len, df_new, df_del, df_final_parashift, 'RELEVANT CHAPTERS ONLY + PARA SHIFT ANALYSIS APPLIED', outputdir + 'parashift.html')


    #clean up the df before print it out
    #del df_final['Relevant']
    #del df_final['ChapterNumber']
    
    
    #keep just one Chapter Number
    #df_final['ChapterNum'] = df1['ChapterNumber']
    #df_final.insert(0, 'ChapterNum', df1['ChapterNumber'])
    
    #reorder columns by list of columnTitles
    #columnsTitles = ['ChapterNum', 'Title', 'Para', 'CharacterCountDifference', 'LevenshteinDistance', 'ParaShifted']
    #df_final = df_final.reindex(columns=columnsTitles)

    #remove index drop index
    #df_final=df_final.drop(['index'],axis=1)
    #df_final.set_index('ChapterNum', inplace=True)
    
    #df_final = df_final.reset_index(drop=True)
    #df_new = df_new.reset_index(drop=True)
    #df_del = df_del.reset_index(drop=True)
    #print(df_final.style.apply(highlight_diff, axis=None).render())
 

    
    #grabbing the dates the reports were run, hardcoded for now
    #df1_date = str(datetime.date.fromtimestamp(os.path.getmtime(lognew)))
    #df2_date = str(datetime.date.fromtimestamp(os.path.getmtime(logold)))
    df_final_levchar = df_final_parashift[df_final_parashift['AboveLevCharThreshold'] == True]

    change_len = str(len(df_final_levchar.index))
    print('Number of relevant paras after the Levenshtein Distance & Character Count Difference analysis: ', change_len)


    #Exporting useful dataframes to csv
    df_new.to_csv(outputdir + source + "_additions_levchar.csv", sep=',',index=False)
    df_del.to_csv(outputdir + source + "_deletions_levchar.csv", sep=',',index=False)
    df_final_levchar.to_csv(outputdir + "\\" + source + "_changes_levchar.csv", sep=',',index=False)
            
    #Relevant chapters and Para Shift filters    
    HTMLExport(new_len, del_len, change_len, df_new, df_del, df_final_levchar, 'RELEVANT DOCS ONLY + PARASHIFT ANALYSIS + LEVENSHTEIN DISTANCE & CHAR COUNT DIFFERENCE THRESHOLD', outputdir + 'levchar.html')

    #wait = input("PAUSED...when ready press enter")

def Diff(logpath, start, xmldir1, xmldir2):
    
    print('Loading list of changed files...')
    
    dfchange = pd.read_csv(logpath+'change.csv')
    i = 0
    
    print('Stepping through each doc and comparing...')
    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><link rel="stylesheet" type="text/css" href="style.css"/><title></title><style type="text/css">table.diff {font-family:Courier; border:medium;} .diff_header {background-color:#e0e0e0} td.diff_header {text-align:right} .diff_next {background-color:#c0c0c0} .diff_add {background-color:#aaffaa} .diff_chg {background-color:#ffff77} .diff_sub {background-color:#ffaaaa}</style></head><body><table id="diff_next">'
    
    with open(logpath + "\\test_updates_overview.html",'w', encoding='utf-8') as f:
            f.write(html) 
            f.close()
            pass
    
    for index, item in dfchange.itertuples(): #loop through each item in the remainder list
        
        filename1 = xmldir1 + str(dfchange.iloc[i,0])
        filename2 = xmldir2 + str(dfchange.iloc[i,0])
        print(i, filename1, filename2)   
                
    
        #Import xml file into soup
        soup1 = BeautifulSoup(open(filename1), 'lxml') 
        soup2 = BeautifulSoup(open(filename2), 'lxml')         
        input1 = [soup1.text] #have to put it as a one itemed list for some reason in order for it to work properly
        input2 = [soup2.text]     

        #input1 = re.sub(r'</[^>]*>','\n', str(input1))
        #input1 = re.sub(r'<[^>]*>','', str(input1))
        #input1 = re.sub(r'\n\n','\n', str(input1))
        #input1 = re.sub(r'\n\n','\n', str(input1))
        #input1 = re.sub(r'\n\n','\n', str(input1))

        #input2 = re.sub(r'</[^>]*>','\n', str(input2))
        #input2 = re.sub(r'<[^>]*>','', str(input2))
        #input2 = re.sub(r'\n\n','\n', str(input2))
        #input2 = re.sub(r'\n\n','\n', str(input2))
        #input2 = re.sub(r'\n\n','\n', str(input2))

        try: diff = difflib.HtmlDiff(wrapcolumn=60).make_table(input1,input2,filename1,filename2,context=True)
        except: diff = '<span class="diff">Exception raised whilst comparing</span>'
        soup3 = BeautifulSoup(diff, 'lxml') #put the diff generated html in soup

        if bool(re.search('<span class="diff', str(soup3))) == True:
            html = html + str(soup3.select_one("thead:nth-of-type(1)")) + str(soup3.select_one("tbody:nth-of-type(1)"))
            #html = html.replace('>t<', '><')
            html = html.replace('>1<', '>' + str(i) + '<')
            html = html.replace(']&gt;', '')
            #html = html.replace('<td nowrap="nowrap"> Previous page •         Next page </td>', '')  
    
        
        
        print("Time taken so far..." + str(datetime.datetime.now() - start))
        #if i == 10: break
        i = i + 1
    
    html += '</body></html>'
    with open(logpath + "\\changes.html",'w', encoding='utf-8') as f:
        f.write(html)  #select the first table and append to the html variable
        f.close()
        pass
    print("Writing results to HTML file..." + logpath + "\\test_updates_overview.html")
    




#### MAIN ####

date =  time.strftime("%d/%m/%Y")
logdate = datetime.datetime.now()
logname = time.strftime("HMRC-02FO-%d%m%Y-%H%M%S.csv")
#xmldir1 =  "C:\\Users\\Hutchida\\Documents\\HMRC\\july\\"
#xmldir2 =  "C:\\Users\\Hutchida\\Documents\\HMRC\\august\\"
xmldir1 = '\\\\lngoxfdatp16vb\\Fabrication\\Build\\0Y02\Data\\'
xmldir2 = '\\\\lngoxfdatp16vb\\Fabrication\\Build\\0Y04\\Data\\'
logpath = "C:\\Users\\Hutchida\\Documents\\HMRC\\logs\\"
source = "HMRC"
maindir = "C:\\Users\\Hutchida\\Documents\\HMRC\\"
outputdir = maindir + "\\output\\"

start = datetime.datetime.now() 

#print("\n\n\nEntering prelim phase..." + str(datetime.datetime.now()))
#Prelim(xmldir1, xmldir2, logpath, start)

#print("\n\n\nEntering first snapshot..." + str(datetime.datetime.now()))
#Snapshot(date, logdate, logname, xmldir1, logpath)

#print("\n\n\nSo far time taken..." + str(datetime.datetime.now() - start))

#reset the log date the filename will take so that it differs from the previous log
#logdate = datetime.datetime.now()
#logname = time.strftime("HMRC-02FO-%d%m%Y-%H%M%S.csv")

#print("\n\n\nEntering second snapshot..." + str(datetime.datetime.now()))
#Snapshot(date, logdate, logname, xmldir2, logpath)

#print("\n\n\nSo far time taken..." + str(datetime.datetime.now() - start))

print("\n\n\nEntering comparison phase..." + str(datetime.datetime.now()))

Comparison(logpath, source, maindir)
#Diff(logpath, start, xmldir1, xmldir2)
print("\n\n\nFinished! Total time taken..." + str(datetime.datetime.now() - start))

#Export(logpath)