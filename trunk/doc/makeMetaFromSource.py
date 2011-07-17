"""
Make meta files from source files.

"""

import re, os
import xml.dom.minidom
from docutils.core import publish_string, publish_parts
doc = None
document = None

overrides = {}#{'stylesheet_path': ','.join([os.path.join(os.path.split(os.path.split(root)[0])[0], 'doc', 'userHelpStyles', 'userHelpCSS.css')])}

header = """
"""

sidebar = """

    <a href="http://www.red-r.org"><img src="../../../../canvas/icons/CanvasIcon.png" alt="Red-R.org"/></a></br>
    
    <a href="http://www.red-r.org/Documentation">Red-R Documentation</a></br>
    <a href="../../../index.html">Packages</a></br>
    <a href="../index.html">Parent Package</a>
    
"""

getDirective = re.compile(r'.. (?P<directive>.+?)::', re.DOTALL)
getKeyValue = re.compile(r'\s:(?P<key>.+?):\s`(?P<value>.+?)`', re.DOTALL)
getSignalType = re.compile(r'self\.(?P<type>.+?)s.add', re.DOTALL)

getQuote = re.compile(r"""(_\()?['\"](?P<quote>.+?)['"]""", re.DOTALL)

getGUIClass = re.compile(r'redRGUI\.(?P<class>[a-zA-Z\.]+)', re.DOTALL)
getLabel = re.compile(r'label\s*=\s*(?P<label>.+?)[,\)]', re.DOTALL)
getWidgetXML = re.compile(r'(<widgetXML>.*</widgetXML>)', re.DOTALL)
getBlock = re.compile(r'""".*?"""[\s\n]*?.*?(?=""")|(.*?\n\s*\n)', re.DOTALL)
getSignalClass = re.compile(r'signals\.(?P<signalClass>.+?)[,\]\)]')
getRawRST = re.compile(r'\s::rawrst::(?P<rawrst>.+?)(?=""")', re.DOTALL)
getRLibraryCall = re.compile(r'self\.require_librarys\((?P<libs>.+?)\)', re.DOTALL)
getHelpDoc = re.compile(r'.. helpdoc::(?P<helpdoc>.*?)"""', re.DOTALL)
getName = re.compile(r'<name>\s*(?P<name>.+?)\s*</name>', re.DOTALL)
getAuthor = re.compile(r'<author>(?P<authorBlock>.*?)</author>', re.DOTALL)
getAuthorName = re.compile(r'<name>(?P<authorname>.*?)</name>', re.DOTALL)
getAuthorContact = re.compile(r'<contact>(?P<authorcontact>.*?)</contact>', re.DOTALL)
        
getSignalXML = re.compile(r'<signalXML>.*?</signalXML>', re.DOTALL)
getSignalParent = re.compile(r'.. signalClass:: *(?P<signalClass>.+?)[ "]')
getSignalConvertTo = re.compile(r'.. convertTo:: *`(?P<convertTo>.+?)`')
getSignalConvertFrom = re.compile(r'.. convertFrom:: *`(?P<convertFrom>.+?)`')

getQTClass = re.compile(r'class .+?\((?P<parent>Q[A-Xa-z]+?)[, \)]')

    
def _getXMLDirective(string):
    """Returns an rst directive or None in the form \.\.\ (?P<directive>.*?)::"""
    match = re.search(getDirective, string)
    if not match: return None
    else: return match.group('directive')

def _getKeyValuePairs(string):
    d = {}
    for m in re.finditer(getKeyValue, string):
        d[m.group('key')] = m.group('value')
    return d
    
def _getRvariableNames(string):
    """Matches the names of R variables in the setRvariableNames declaration.  Returns a a list of names"""
    match = re.search(r'self\.setRvariableNames\(\[.+?\)\]', string)
    if not match: return None
    names = []
    for m in re.finditer(getQuote, match.group()):
        names.append(m.group('quote'))
    return names

def _getRRSignals(string):
    """returns a dict with values: type, name, signals, description, """
    d = {}
    ## get the type
    type = re.search(getSignalType, string)
    if type:
        d['type'] = type.group('type')
    d.update(_getKeyValuePairs(string))
    if not 'name' in d:
        nameGroup = re.search(r'put\(.*?,\s*(?P<nameGroup>.+?),', string)
        if nameGroup:
            nameString = re.search(getQuote, nameGroup.group('nameGroup'))
            if nameString:
                d['name'] = nameString.group('quote')
    if not 'name' in d: d['name'] = ''
    if not 'signals' in d: d['signals'] = [m.group('signalClass') for m in re.finditer(getSignalClass, string)]
    if not 'description' in d: d['description'] = ''
    rawRST = re.search(getRawRST, string) # return any raw rst string
    if rawRST: d['rst'] = rawRST.group('rawrst')
    else: d['rst'] = ''
    return d

def _getRRGUISettings(string):
    """Parses an rrgui setting and returns a tuple of class, label or None"""
    d = {}
    d.update(_getKeyValuePairs(string))
    if not 'class' in d:
        guiClass = re.search(getGUIClass, string)
        if guiClass: d.update(guiClass.groupdict())
    if not 'class' in d: d['class'] = ''
    if not 'label' in d:
        guiLabel = re.search(getLabel, string)
        if guiLabel: 
            label = re.search(getQuote, guiLabel.group('label'))
            if label: d['label'] = label.group('quote')
    if not 'label' in d: d['label'] = ''
    if not 'description' in d: d['description'] = 'No description entered for this GUI parameter'
    rawRST = re.search(getRawRST, string) # return any raw rst string
    if rawRST: d['rst'] = rawRST.group('rawrst')
    else: d['rst'] = ''
    return d
def getXMLText(nodelist):
    """A function to handle retrieval of xml text.  
    
    .. note:: 
        This is such a ubiquitous function that we may consider making our own xml handler with this built in.
    """
    rc = ''
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
            
    rc = unicode(rc).strip()
    return rc


def _parsefile(myFile):
    d = {'widgetXML':'', 'signals':[], 'rrgui':[], 'rrvarnammes':[], 'rpackages':[], 'helpdoc':[], 'name':'', 'author':[]}
    # parse the widgetXML and handle that.
    widgetXML = re.search(getWidgetXML, myFile)
    if not widgetXML: raise Exception('Widget does not have a widgetXML section')
    d['widgetXML'] = widgetXML.group(1)
    # print d['widgetXML']
    widgetMetaXML = xml.dom.minidom.parseString(d['widgetXML'])
    d['name'] = getXMLText(widgetMetaXML.getElementsByTagName('name')[0].childNodes)
    d['icon'] = getXMLText(widgetMetaXML.getElementsByTagName('icon')[0].childNodes)
    d['summary'] = getXMLText(widgetMetaXML.getElementsByTagName('summary')[0].childNodes)
    
    d['tags'] = [] ## will be a list of tuples in the form (<tag>, <priority>); ('Data Input', 4)
    for tag in widgetMetaXML.getElementsByTagName('tags')[0].childNodes:
        if getXMLText(tag.childNodes) != '':
            if tag.hasAttribute('priority'):
                d['tags'].append((getXMLText(tag.childNodes), int(tag.getAttribute('priority'))))
            else:
                d['tags'].append((getXMLText(tag.childNodes), 0))
    
    d['author'] = [] ## will be a list of tuples in the form (<tag>, <priority>); ('Data Input', 4)
    for author in widgetMetaXML.getElementsByTagName('author'):
        #print author
        #print getXMLText(author.getElementsByTagName('name')[0].childNodes)
        d['author'].append((getXMLText(author.getElementsByTagName('authorname')[0].childNodes), 
        getXMLText(author.getElementsByTagName('authorcontact')[0].childNodes)))
    # get any loaded R libraries, wrapped in a try because some widgets might not load R libraries
    try:
        for m in re.finditer(getRLibraryCall, myFile):
            for q in re.finditer(getQuote, m.group()):
                d['rpackages'].append(q.group('quote'))
    except:pass
    
    # get the help documentation, wrapped in a try because some widget might not have any help documentation
    try:
        for m in re.finditer(getHelpDoc, myFile):
            d['helpdoc'].append(m.group('helpdoc'))
    except: pass
    
    for m in  re.finditer(getBlock, myFile.replace('\r', '')):
        """ m is a block of code, that is a docstring followed by one block of code.  The block must start with tripple quotes."""
        if not re.search(re.compile(r'\s*"""', re.DOTALL), m.group().split('\n')[0]): continue # """The docstring must be at the beginning of the block"""
        
        string = m.group()
        """if the string contains a directive we should find out what the directive is and then how to handle it."""
        directive = _getXMLDirective(string)
        if directive == None: continue
        if directive in ['rrsignals', 'rrgui']:  # it's one of ours!!
            """if there are other options in the docstring then they belong to this directive, we try to get them"""
            if directive == 'rrsignals':
               d['signals'].append(_getRRSignals(string))
            elif directive == 'rrgui':
                d['rrgui'].append(_getRRGUISettings(string))
    
    # print d
    # asdfafd
    return d
    
    
def parseWidgetFile(filename, outputXML, userHelp,devHelp):
    """Reads a file and parses out the relevant widget xml settings, writes to the file output an xml document representing the parsed data.  Prints success message on success."""
    global doc
    fileStrings = []
    with open(filename, 'r') as f:
        myFile = f.read()
    moduleName = os.path.basename(filename).split('.')[0]
    packgeName = os.path.split(os.path.split(os.path.split(filename)[0])[0])[1]
    
    """Pass the list of strings to the parser to extract the relevant structure"""
    d = _parsefile(myFile)

    with open(outputXML, 'w') as f:
        f.write(makeXML(d))
    with open(userHelp, 'w') as f:
        helprst = makeHelp(d)
        f.write(helprst)

    with open(devHelp, 'w') as f:
        output = """%(WIDGETNAME)s
=================================
   
.. automodule:: libraries.%(PACKAGENAME)s.widgets.%(WIDGETNAME)s
   :members:
   :undoc-members:
   :show-inheritance:
   
""" % {'WIDGETNAME':moduleName, 'PACKAGENAME':packgeName}
        f.write(output)

    print 'Success for %s' % filename
    return d['name']
    
    
def makeXML(d):
    """Makes an xml file as plain text"""
    """make the header"""
    s = """<?xml version="1.0" encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl" href="../../help.xsl"?>
<documentation>"""
    s += d['widgetXML']
    """put in the signal classes"""
    s += '\n<signals>\n'
    for rs in d['signals']:
        s += '<%(type)s>\n' % rs
        s += '\t<name>%(name)s</name>\n' % rs
        s += '\t<description>\n%(description)s\n\t</description>\n' % rs
        s += '\t<signalClass>%s</signalClass>\n' % ','.join(rs['signals'])
        s += '</%(type)s>\n' % rs
    s += '</signals>\n'
    s += '</documentation>'
    return s
    
    
def makeHelp(d):
    """Makes a help document from the source as a .rst document"""
    s = ''
    s += '%s\n%s\n\n' % (d['name'], ')'*len(d['name']))
    s += 'Authors\n((((((((((((\n\n'
    for n, c in d['author']:
        s += '%s, %s\n\n' % (n, c)
    s += '\nDocumentation\n((((((((((((((((((\n\n'
    if len(d['helpdoc']) == 0:
        s += 'No help documentation entered for this widget'
    else:
        s += '\n'.join(d['helpdoc'])
    s += '\n\n'
    s += 'Interface\n((((((((((((\n\n'
    for gui in d['rrgui']:
        s += '%s\n%s\n\n' % (gui['label'], '}'*len(gui['label']))
        s += '**Description**\n\n'
        s += '%s\n\n' % gui['description']
        s += '%s\n\n' % gui['rst']
        s += 'Class: `%s`_\n\n' % gui['class']
    s += 'Signals\n((((((((((((((\n\n'
    for sig in d['signals']:
        s += '%s\n%s\n\n' % (sig['name'], '}'*len(sig['name']))
        s += 'Classes:'
        for ss in sig['signals']:
            s += '`%s`_ ' % ss
        s+= '\n\n'
        s += '**Description**\n\n'
        s += '%s\n\n' % sig['description']
        s += '%s\n\n' % sig['rst']
        
    s += 'R Packages\n((((((((((((((\n\n'
    s += ','.join(d['rpackages'])
    s += '\n\n'
    for gui in d['rrgui']:
        if gui['class'] =='': 
            s += '.. _%s: #\n\n' % (gui['class'])          
        else: 
            (package,guiClass) = gui['class'].split('.')
            s += '.. _%s: ../../../../../libraries/%s/help/userDoc/qtWidgets/%s.html\n\n' % (gui['class'],package,guiClass)
        
    for sig in d['signals']:
        # print sig, len(sig['signals'])
        if len(sig['signals']) ==0: 
            s += '.. _%s: #\n\n' % (sig['signals'])
        else:
            for ss in sig['signals']:
                (package,sigClass) = ss.split('.')
                s += '.. _%s: ../../../../libraries/%s/help/userDoc/signalClasses/%s.html\n\n' % (ss, package,sigClass)                
        
    return s

def parseSignalFile(filename, userHelp,devHelp, outputXML):
    with open(filename, 'r') as f:
        myFile = f.read()
    moduleName = os.path.basename(filename).split('.')[0]
    packgeName = os.path.split(os.path.split(os.path.split(filename)[0])[0])[1]
    
    d = {'helpdoc':[], 'signalClass':[], 'name':os.path.split(filename)[1], 'convertFrom':[], 'convertTo':[]}
    
    try:
        for m in re.finditer(getHelpDoc, myFile):
            d['helpdoc'].append(m.group('helpdoc'))
    except: pass
    try:
        for m in re.finditer(getSignalParent, myFile):
            d['signalClass'].append(m.group('signalClass').strip())
    except: pass
    try:
        d['convertTo'] = [c.strip() for c in re.search(getSignalConvertTo, myFile).group('convertTo').split(',')]
    except: pass
    try:
        d['convertFrom'] = [c.strip() for c in re.search(getSignalConvertFrom, myFile).group('convertFrom').split(',')]
    except: pass
    
    with open(userHelp, 'w') as f:
        f.write(makeSignalHelp(d))
    
    with open(devHelp, 'w') as f:
        output = """%(WIDGETNAME)s
=================================
   
.. automodule:: libraries.%(PACKAGENAME)s.signalClasses.%(WIDGETNAME)s
   :members:
   :undoc-members:
   :show-inheritance:
   
""" % {'WIDGETNAME':moduleName, 'PACKAGENAME':packgeName}
        f.write(output)
        
    with open(outputXML, 'w') as f:
        f.write(makeSignalXML(d))
        
    print 'Success for %s' % filename
    return d['name']
def parseQTWidgetFile(filename, userHelp,devHelp, outputXML):
    with open(filename, 'r') as f:
        myFile = f.read()
    moduleName = os.path.basename(filename).split('.')[0]
    packgeName = os.path.split(os.path.split(os.path.split(filename)[0])[0])[1]

    d = {'helpdoc':[], 'name':os.path.split(filename)[1], 'parent':''}
    try:
        for m in re.finditer(getHelpDoc, myFile):
            d['helpdoc'].append(m.group('helpdoc'))
    except: pass
    try:
        d['parent'] = re.search(getQTClass, myFile).group('parent')
    except: pass
    
    with open(userHelp, 'w') as f:
        helprst = makeQTHelp(d)
        f.write(helprst)
    with open(outputXML, 'w') as f:
        f.write(makeQTXML(d))
    with open(devHelp, 'w') as f:
        output = """%(WIDGETNAME)s
=================================
   
.. automodule:: libraries.%(PACKAGENAME)s.qtWidgets.%(WIDGETNAME)s
   :members:
   :undoc-members:
   :show-inheritance:
   
""" % {'WIDGETNAME':moduleName, 'PACKAGENAME':packgeName}
        f.write(output)

    return d['name']
def makeQTHelp(d):
    """Takes a dict of helpdoc, name, and parent and makes an rst file for documentation."""
    s = header
    s += '%s\n%s\n\n' % (d['name'], ')'*len(d['name']))
    s += '.. contents::\n\n'
    
    if d['parent'] == '':
        s += 'Non standard parent as parent class.\n\n'
    else:
        s += 'Inherits from `%s`_.\n\n' % d['parent']
        s += '.. _`%s`: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/%s.html\n\n' % (d['parent'], d['parent'].lower())
        
    
    s += '\nDocumentation\n((((((((((((((((((\n\n'
    if len(d['helpdoc']) == 0:
        s += 'No help documentation entered for this onject'
    else:
        s += '\n'.join(d['helpdoc'])
    s += '\n\n'
    return s

def makeQTXML(d):
    """Makes an xml file as plain text"""
    """make the header"""
    s = """<?xml version="1.0" encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl" href="../../help.xsl"?>
<documentation>"""
    s += '</documentation>'
    return s
    
def makeSignalHelp(d):
    """Makes a signal help file using a dict containing two lists, helpdoc and signalClass"""
    s = header
    s += '%s\n%s\n\n' % (d['name'], ')'*len(d['name']))
    s += '.. contents::\n\n'
    s += 'Dependent signals\n(((((((((((((((((((((((\n\n'
    for sig in d['signalClass']:
        s += '%s\n%s\n\n' % (sig+'_', '}'*(len(sig)+5))
    s += '\n\nConvert To\n{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{\n\n'
    for sig in d['convertTo']:
        s += '%s\n' % (sig+'_')
    s += '\n\nConvert From\n{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{\n\n'    
    for sig in d['convertFrom']:
        s += '%s\n' % (sig+'_')
        
    s += '\nDocumentation\n((((((((((((((((((\n\n'
    if len(d['helpdoc']) == 0:
        s += 'No help documentation entered for this signal class'
    else:
        s += '\n'.join(d['helpdoc'])
    s += '\n\n'
    for sig in d['signalClass']:
        s += '.. _%s: ../../../../%s/help/userDoc/signalClasses/%s.html\n\n' % (sig, sig.split(':')[0], sig.split(':')[1])
    for sig in d['convertTo']:
        s += '.. _%s: ../../../../%s/help/userDoc/signalClasses/%s.html\n\n' % (sig, sig.split(':')[0], sig.split(':')[1])
    for sig in d['convertFrom']:
        s += '.. _%s: ../../../../%s/help/userDoc/signalClasses/%s.html\n\n' % (sig, sig.split(':')[0], sig.split(':')[1])
    return s
    
def makeSignalXML(d):
    """Makes an xml file as plain text"""
    """make the header"""
    s = """<?xml version="1.0" encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl" href="../../help.xsl"?>
<documentation>"""
    """put in the signal classes"""
    s += '<signals>'
    for rs in d['signalClass']:
        s += '<signal>%s</signal>\n' % rs
    s += '</signals>\n'
    s += '<convertTo>%s</convertTo>\n' % ','.join(d['convertTo'])
    s += '<convertFrom>%s</convertFrom>\n' % ','.join(d['convertFrom'])
    s += '</documentation>'
    return s
# def test(path):

    # parseFile(path, 'outputXML.xml', 'outputTest.txt', 'outputDevel.txt')
    
# import sys
# test(sys.argv[1])