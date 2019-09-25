
import difflib

outputdir = "www\\"

input1 = 'The following paper was issued to UKOITC (The United Kingdom Oil Industry Taxation Committee, formed in 1965) and BRINDEX on 2 July 1991.'
input2 = 'Purpose of this PaperWhy reconciliations are neededOTO’s aimThe accounts and CT computationsThe reconciliationExamination of the ReconciliationsResults'
diff = difflib.HtmlDiff(wrapcolumn=170,tabsize=1).make_file(input1,input2)
diff = diff.replace(' nowrap="nowrap"','')


with open(outputdir + "diff.html",'w', encoding='utf-8') as f:
    f.write(diff)
    f.close()
    pass

print ("HTML generated at: " + outputdir + "diff.html")

offset = 0
for entry in dict1:    
    n = entry + offset       
    if dict1[n][1] != dict2[n][1]:
        #could be a change, check string 1 or 2 found on next line
        if dict1[n+1][1] == dict2[n][1]: #then string1 has been deleted and needs to be reflected in right div
            offset+=1
            #left div
            sup = etree.SubElement(divleft, 'sup')
            sup.text = str(n)
            left = etree.SubElement(divleft, dict1[n][0])
            left.text = dict1[n][1]
            left.set('style', 'background-color: red')
            #right div
            try: 
                sup = etree.SubElement(divright, 'sup')
                sup.text = str(n+1)
                right = etree.SubElement(divright, 'p')
                right.text = '' #insert blank para
                right.set('style', 'background-color: red')
            except KeyError: 
                print('Page 1 has more elements than page 2...')
                x+=1
        else: #string1 hasn't been deleted, but now check whether string2 has been added
            if dict1[n][1] == dict2[n+1][1] #then string2 has been added and needs to be reflected in left div
                offset+=1
                #left div
                sup = etree.SubElement(divleft, 'sup')
                sup.text = str(n+1)
                left = etree.SubElement(divleft, 'p')
                left.text = '' #insert blank para
                left.set('style', 'background-color: green')
                #right div
                try: 
                    sup = etree.SubElement(divright, 'sup')
                    sup.text = str(n)
                    right = etree.SubElement(divright, dict2[n][0])
                    right.text = dict2[n][1]
                    right.set('style', 'background-color: green')
                except KeyError: 
                    print('Page 1 has more elements than page 2...')
                    x+=1
            else: #string1 hasn't been deleted nor string2 been added, therefore highlight yellow as a change        
                sup = etree.SubElement(divleft, 'sup')
                sup.text = str(n)
                left = etree.SubElement(divleft, dict1[n][0])
                left.text = dict1[n][1]
                try: 
                    sup = etree.SubElement(divright, 'sup')
                    sup.text = str(n)
                    right = etree.SubElement(divright, dict2[n][0])
                    right.text = dict2[n][1]
                    if dict1[n][1] != dict2[n][1]: right.set('style', 'background-color: #FFFF00')
                except KeyError: 
                    print('Page 1 has more elements than page 2...')
                    x+=1
    else: #no changes, additions, or deletions found, so add the paras without styling
        sup = etree.SubElement(divleft, 'sup')
        sup.text = str(n)
        left = etree.SubElement(divleft, dict1[n][0])
        left.text = dict1[n][1]
        try: 
            sup = etree.SubElement(divright, 'sup')
            sup.text = str(n)
            right = etree.SubElement(divright, dict2[n][0])
            right.text = dict2[n][1]
        except KeyError: 
            print('Page 1 has more elements than page 2...')
            x+=1