import re, sys, os.path, glob
import pprint
pp = pprint.PrettyPrinter(indent=4)

#test = sys.argv[2]
path = sys.argv[1]
print path
if os.path.isdir(path):
    widgetPath = os.path.join(str(path),'widgets')
    helpPath = os.path.join(path,'help')
    files = glob.glob(widgetPath+'/*.py')
else:
    files = [sys.argv[1]]
    path = os.path.split(os.path.split(path)[0])[0]
    widgetPath = os.path.join(path,'widgets')
    helpPath = os.path.join(path,'help')
    
for n in files:
    print '\n\n####################%s######################\n\n' % n
    #data = open(n,'r').readlines()
    pyInfo = {}
    data = file(n).read()
    istart = data.find("<name>")
    iend = data.find("</name>")
    if istart < 0 or iend < 0:
        continue
    pyInfo['name'] = data[istart+6:iend]
    for attr, deflt in (
        #('inputs>', 'None'), ('outputs>', 'None'), 
        ("contact>", "")
        ,("icon>", "Default.png")
        ,("description>", "")
        ,("tags>", "Prototypes")
        ,("outputWidgets>", "")
        ,("inputWidgets>", "")
        ):
        istart, iend = data.find("<"+attr), data.find("</"+attr)
        pyInfo[attr[:-1]] = istart >= 0 and iend >= 0 and data[istart+1+len(attr):iend].strip() or deflt

    (name,ext) = os.path.splitext(os.path.basename(n))
    helpFile = os.path.join(helpPath,name+'.html')
    helpSections = {}
    if os.path.exists(helpFile):
        helpData = file(helpFile).read()
        #print helpData
        sections = re.split('<h2>(.*)</h2>',helpData)
        x = re.compile(r'<[^<]*?/?>')
        try:
            helpSections['Brief'] = sections[sections.index('Brief')+1]
            helpSections['Brief'] = x.sub('',helpSections['Brief']).strip()
        except:
            pass
        try:
            helpSections['Inputs'] = sections[sections.index('Inputs')+1]
            helpSections['Inputs'] = re.findall('<dt>(.*)</dt>\s+<dd>(.*)</dd>',helpSections['Inputs'])
        except:
            pass
        try:
            helpSections['Outputs'] = sections[sections.index('Outputs')+1]
            helpSections['Outputs'] = re.findall('<dt>(.*)</dt>\s+<dd>(.*)</dd>',helpSections['Outputs'])
        except:
            pass
        try:
            helpSections['Details'] = sections[sections.index('Details')+1].strip().replace('<br>','<br />').replace('</br>','<br />')
        except:
            pass
        try:
            helpSections['Parameters'] = sections[sections.index('Parameters')+1]
            helpSections['Parameters'] = re.findall('<dt>(.*)</dt>\s+<dd>(.*)</dd>',helpSections['Parameters'])
        except:
            pass
        try:
            helpSections['R Functions'] = sections[sections.index('R Functions')+1]
            helpSections['R Functions'] = re.findall('<li>(.*)</li>',helpSections['R Functions'])
        except:
            pass
        
        #helpSections['Citation'] = sections[sections.index('Citation')+1]
        
        
        
        
    
    if 'Brief' in helpSections.keys() and helpSections['Brief'] != '':
        summary = helpSections['Brief']
    else:
        summary = pyInfo['description']

    if 'Details' in helpSections.keys() and helpSections['Details'] != '':
        details = helpSections['Details']
    else:
        details = pyInfo['description']


        
    output = """<?xml version="1.0" encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl" href="../../help.xsl"?>
<documentation>
    <name>%s</name>
    <icon>%s</icon>
    <tags>""" % (pyInfo['name'],pyInfo['icon'].lower())
    tags = pyInfo['tags'].split(',')
    for x in tags:
        output += """ 
        <tag>%s</tag>""" % x.strip()
    output += """ 
    </tags>
    <screenshots></screenshots>
    <summary>%s</summary>
    <details>%s</details>
    <relatedWidgets>
        <inputWidget><!-- <package>:<widget> ie. base:apply, plotting:heatmap --></inputWidget>
        <outputWidget><!-- <package>:<widget> ie. base:apply, plotting:heatmap --></outputWidget>
    </relatedWidgets>
    <signals>
    <!-- [REQUIRED] List all the widget input output slots and their data type.-->""" % (summary,details)

    if 'Inputs' in helpSections.keys() and len(helpSections['Inputs'])>0:
        for x in helpSections['Inputs']:
            output += """
        <input>
            <signalClass>%s</signalClass>
            <description>%s</description>
        </input>""" % (x[0].replace('.',":"),x[1].replace('.',":"))

    if 'Outputs' in helpSections.keys() and len(helpSections['Outputs'])>0:
        for x in helpSections['Outputs']:
            output += """
        <output>
            <signalClass>%s</signalClass>
            <description>%s</description>
        </output>""" % (x[0].replace('.',":"),x[1].replace('.',":"))
            
    output += """
    </signals>
    <GUIElements>
        <!-- [REQUIRED] A list of the parameters and how to use them.-->"""
    if 'Parameters' in helpSections.keys() and len(helpSections['Parameters'])>0:
        for x in helpSections['Parameters']:
            output += """
        <parameter>
            <name>%s</name>
            <description>%s</description>
        </parameter>""" % x
    output += """
    </GUIElements>
    <RFunctions>
    <!-- [REQUIRED] R functions used in this widget.-->"""
    if 'R Functions' in helpSections.keys() and len(helpSections['R Functions'])>0:
        for x in helpSections['R Functions']:
            output += """
        <function>%s</function>""" % x
        

    output += """
    </RFunctions>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</documentation>"""
    #print output
    try:
        os.mkdir(os.path.join(path,'meta'))
    except:
        pass
    try:    
        os.mkdir(os.path.join(path,'meta','widgets'))
    except:
        pass
        
    f = open(os.path.join(path,'meta','widgets',name+'.xml'),'w')
    f.write(output)
    f.close()
    # pp.pprint(pyInfo)
    # pp.pprint(helpSections)
       
    