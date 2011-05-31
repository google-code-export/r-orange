"""Make package docs.

This module aids developers in making documentation files from annotated package files.  The widgets, qtWidgets, and signal classes are parsed to generate the documentation.
"""

import sys,os,glob,subprocess
import shutilm, re, xml.dom.minidom
import makeMetaFromSource
from docutils.core import publish_string



root = sys.argv[1]
helpDir = os.path.join(root, 'help')
widgetHelp = os.path.join(helpDir, 'widgets')
signalHelp = os.path.join(helpDir, 'signalClasses')
qtHelp = os.path.join(helpDir, 'qtWidgets')
metaDir = os.path.join(root, 'meta')
widgetMeta = os.path.join(metaDir, 'widgets')
signalMeta = os.path.join(metaDir, 'signalClasses')
qtMeta = os.path.join(metaDir, 'qtWidgets')

overrides = {'stylesheet':[os.path.join(os.path.split(os.path.split(root)[0])[0], 'doc', 'helpDocStyle.css')]}

def makeHelpDirs():
    """Make essential files for the help directories"""
    if not os.path.exists(helpDir): os.mkdir(helpDir)
    if not os.path.exists(metaDir): os.mkdir(metaDir)
    if not os.path.exists(widgetHelp): os.mkdir(widgetHelp)
    if not os.path.exists(signalHelp): os.mkdir(signalHelp)
    if not os.path.exists(qtHelp): os.mkdir(qtHelp)
    if not os.path.exists(widgetMeta): os.mkdir(widgetMeta)
    if not os.path.exists(signalMeta): os.mkdir(signalMeta)
    if not os.path.exists(qtMeta): os.mkdir(qtMeta)
    
def getPackageComponents():
    """Returns a dict of all files in a package directory structure.  Dict keys are widgets, qtWidgets, and signalClasses."""
    d = {}
    d['widgets'] = [g for g in glob.glob(os.path.join(root, 'widgets', '*.py')) if g != '__init__']
    d['qtWidgets'] = [g for g in glob.glob(os.path.join(root, 'qtWidgets', '*.py')) if g != '__init__']
    d['signalClasses'] = [g for g in glob.glob(os.path.join(root, 'signalClasses', '*.py')) if g != '__init__']
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

def packageToDict(filename):
    with open(filename, 'r') as f:
        xmlFile = f.read()
    dom = xml.dom.minidom.parseString(xmlFile)
    d = {'Name':'', 'Author':'', 'Number':'', 'Stability':'', 'Date':'', 'Dependencies':'', 'Description':''}
    d['Name'] = getXMLText(dom.getElementsByTagName('Name')[0].childNodes)
    d['Author'] = getXMLText(dom.getElementsByTagName('Author')[0].childNodes)
    d['Number'] = getXMLText(dom.getElementsByTagName('Nunmber')[0].childNodes)
    d['Stability'] = getXMLText(dom.getElementsByTagName('Stability')[0].childNodes)
    d['Date'] = getXMLText(dom.getElementsByTagName('Date')[0].childNodes)
    d['Dependencies'] = getXMLText(dom.getElementsByTagName('Dependencies')[0].childNodes)
    d['Description'] = getXMLText(dom.getElementsByTagName('Description')[0].childNodes)
    
    return d
    
def makeIndex(nd):
    """Make the index files for the package."""
    pDict = packageToDict(os.path.join(root, 'package.xml'))
    s = '%s\n%s\n\n' % (pDict['Name'], '}'*len(pDict['Name']))
    s += '%s\n%s\n\n' % ('Description', '{'*len('Description'))
    s += '%s\n\n' % pDict['Description']
    
    ### bullet list
    s += '%s\n%s\n\n' % ('Widgets', '{'*len('Widgets'))
    for n, dn in nd['W']:
        s += '-%s_\n' % dn
    
    s += '%s\n%s\n\n' % ('Signals', '{'*len('Signals'))
    for n, dn in nd['S']:
        s += '-%s_\n' % dn
    
    s += '%s\n%s\n\n' % ('Widgets', '{'*len('Widgets'))
    for n, dn in nd['Q']:
        s += '-%s_\n' % dn
        
    ### put in the links
    for n, dn in nd['W']:
        s += '.. _%s: ./widgets/%s.html\n\n' % (dn, n)
    
    s += '%s\n%s\n\n' % ('Signals', '{'*len('Signals'))
    for n, dn in nd['S']:
        s += '.. _%s: ./signalClasses/%s.html\n\n' % (dn, n)
    
    s += '%s\n%s\n\n' % ('Widgets', '{'*len('Widgets'))
    for n, dn in nd['Q']:
        s += '.. _%s: ./qtWidgets/%s.html\n\n' % (dn, n)
        
    output = publish_string(s, writer_name='html', settings_overrides = overrides)
    with open(os.path.join(helpDir, 'index.html'), 'w') as h:
        h.write(output)
def makeFiles():
    d = getPackageComponents()
    nd = {'W':[], 'S':[], 'Q':[]}
    ## make rst and xml files.
    for w in d['widgets']:
        wn = makeMetaFromSource.parseWidgetFile(os.path.join(root, 'widgets', '%s.py' % w), 
            os.path.join(widgetMeta, '%s.xml' % w), 
            os.path.join(widgetHelp, '%s.rst' % w))
        nd['W'].append((w, wn))
    for s in d['signalClasses']:
        sn = makeMetaFromSource.parseSignalFile(os.path.join(root, 'signalClasses', '%s.py' % s), 
            os.path.join(signalHelp, '%s.rst' % s),
            os.path.join(signalMeta, '%s.xml' % s))
        nd['S'].append((s, sn))
    for q in d['qtWidgets']:
        qn = makeMetaFromSource.parseQTWidgetFile(os.path.join(root, 'qtWidgets', '%s.py' % s), 
            os.path.join(qtHelp, '%s.rst' % q),
            os.path.join(qtMeta, '%s.xml' % q))
        nd['Q'].append((q, qn))
    ## now make the html by converting .rst to html
    for w in d['widgets']:
        with open(os.path.join(widgetHelp, '%s.rst' % w), 'r') as f:
            thisFile = f.read()
            output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            with open(os.path.join(widgetHelp, '%s.html' % w), 'w') as h:
                h.write(output)
                
    for s in d['signalClasses']:
        with open(os.path.join(signalHelp, '%s.rst' % s), 'r') as f:
            thisFile = f.read()
            output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            with open(os.path.join(signalHelp, '%s.html' % w), 'w') as h:
                h.write(output)
            
    for s in d['qtWidgets']:
        with open(os.path.join(qtHelp, '%s.rst' % s), 'r') as f:
            thisFile = f.read()
            output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            with open(os.path.join(qtHelp, '%s.html' % w), 'w') as h:
                h.write(output)
    
    ## make the index files
    makeIndex(nd)
    
makeHelpDirs()
makeFiles()