"""
Make meta files from source files.

"""

import re
import xml.dom.minidom
doc = None
document = None

getDirective = re.compile(r'.. (?P<directive>.+?)::', re.DOTALL)
getKeyValue = re.compile(r'\s:(?P<key>.+?):\s`(?P<value>.+?)`', re.DOTALL)
getSignalType = re.compile(r'self\.(?P<type>.+?)s.add', re.DOTALL)

getQuote = re.compile(r"""(_\()?['\"](?P<quote>.+?)['"]""", re.DOTALL)

getGUIClass = re.compile(r'redRGUI\.(?P<class>[a-zA-Z\.]+)', re.DOTALL)
getLabel = re.compile(r'label\s*=\s*(?P<label>.+?)[,\)]', re.DOTALL)
getWidgetXML = re.compile(r'<widgetXML>(?P<widgetXML>.*?)</widgetXML>', re.DOTALL)
getBlock = re.compile(r'""".*?"""[\s\n]*?.*?(?=""")|(.*?\n\s*\n)', re.DOTALL)
getSignalClass = re.compile(r'signals\.(?P<signalClass>.+?)[,\]\)]')
getRawRST = re.compile(r'\s::rawrst::(?P<rawrst>.+?)(?=""")', re.DOTALL)
getRLibraryCall = re.compile(r'self\.require_librarys\((?P<libs>.+?)\)', re.DOTALL)
getHelpDoc = re.compile(r'.. helpdoc::(?P<helpdoc>.*?)"""', re.DOTALL)
getName = re.compile(r'<name>\s*(?P<name>.+?)\s*</name>', re.DOTALL)
getAuthor = re.compile(r'<author>(?P<authorBlock>.*?)</author>', re.DOTALL)
getAuthorName = re.compile(r'<authorname>(?P<authorname>.*?)</authorname>', re.DOTALL)
getAuthorContact = re.compile(r'<authorcontact>(?P<authorcontact>.*?)</authorcontact>', re.DOTALL)
        
getSignalXML = re.compile(r'<signalXML>.*?</signalXML>', re.DOTALL)
    
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

def _parsefile(myFile):
    d = {'widgetXML':'', 'signals':[], 'rrgui':[], 'rrvarnammes':[], 'rpackages':[], 'helpdoc':[], 'name':'', 'author':[]}
    
    # parse the widgetXML and handle that.
    widgetXML = re.search(getWidgetXML, myFile)
    if not widgetXML: raise Exception('Widget does not have a widgetXML section')
    d['widgetXML'] = widgetXML.group('widgetXML')
        
    # get any loaded R libraries, wrapped in a try because some widgets might not load R libraries
    try:
        for m in re.finditer(getRLibraryCall, myFile):
            for q in re.finditer(getQuote, m.group()):
                d['rpackages'].append(q.group('quote'))
    except:pass
    
    if not re.search(getName, myFile): raise Exception('There is not a name tag.')
    d['name'] = re.search(getName, myFile).group('name')
    
    # get the authors
    try:
        for m in re.finditer(getAuthor, myFile):
            d['author'].append((re.search(getAuthorName, m.group('authorBlock')).group('authorname'), re.search(getAuthorContact, m.group('authorBlock')).group('authorcontact')))
    except:
        raise Exception('Widget must contain at least one author block and each author block must have a name and contact.  Please use the form;\n<author>\n\t<authorname>Name</authorname>\n\t<authorcontact>name@x.com</authorcontact>\n</author>\n\nThis should be in the widgetXML block')
    
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
    return d
    
    
def parseWidgetFile(filename, outputXML, outputHelp):
    """Reads a file and parses out the relevant widget xml settings, writes to the file output an xml document representing the parsed data.  Prints success message on success."""
    global doc
    fileStrings = []
    with open(filename, 'r') as f:
        myFile = f.read()

    """Pass the list of strings to the parser to extract the relevant structure"""
    d = _parsefile(myFile)
    with open(outputXML, 'w') as f:
        f.write(makeXML(d))
    with open(outputHelp, 'w') as f:
        f.write(makeHelp(d))
    print 'Success for %s' % filename
    
def makeXML(d):
    """Makes an xml file as plain text"""
    """make the header"""
    s = """
<?xml version="1.0" encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl" href="../../help.xsl"?>
<documentation>"""
    s += d['widgetXML']
    """put in the signal classes"""
    s += '<signals>'
    for rs in d['signals']:
        s += '<%(type)s>\n' % rs
        s += '\t<name>%(name)s</name>\n' % rs
        s += '\t<description>\n%(description)s\n\t</description>\n' % rs
        s += '\t<signal>%s</signal>\n' % ','.join(rs['signals'])
        s += '</%(type)s>\n' % rs
    s += '</signals>\n'
    s += '</documentation>'
    return s
    
def makeHelp(d):
    """Makes a help document from the source as a .rst document"""
    s = '%s\n%s\n\n' % (d['name'], ')'*len(d['name']))
    s += 'Authors\n((((((((((((\n\n'
    for n, c in d['author']:
        s += '%s, %s\n' % (n, c)
    s += '\nDocumentation\n((((((((((((((((((\n\n'
    s += '\n'.join(d['helpdoc'])
    s += '\n\n'
    s += 'Interface\n((((((((((((\n\n'
    for gui in d['rrgui']:
        s += '%s\n%s\n\n' % (gui['label'], '}'*len(gui['label']))
        s += 'Description\n{{{{{{{{{{{{{{{\n\n'
        s += '%s\n\n' % gui['description']
        s += '%s\n\n' % gui['rst']
        s += 'Class: %s\n\n' % gui['class']
    s += 'Signals\n((((((((((((((\n\n'
    for sig in d['signals']:
        s += '%s\n%s\n\n' % (sig['name'], '}'*len(sig['name']))
        s += 'Classes: %s\n\n' % ','.join(sig['signals'])
        s += 'Description\n{{{{{{{{{{{{{{{\n\n'
        s += '%s\n\n' % sig['description']
        s += '%s\n\n' % sig['rst']
        
    s += 'R Packages\n((((((((((((((\n\n'
    s += ','.join(d['rpackages'])
    return s

def parseSignalFile(filename, outputXML):
    with open(filename, 'r') as f:
        myFile = f.read()
    x = re.search(getSignalXML, myFile)
    if x:
        with open(outputXML, 'w') as f:
            f.write(x.group())
# def test(path):

    # parseFile(path, 'outputXML.xml', 'outputTest.txt', 'outputDevel.txt')
    
# import sys
# test(sys.argv[1])