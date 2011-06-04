"""Make package docs.

This module aids developers in making documentation files from annotated package files.  The widgets, qtWidgets, and signal classes are parsed to generate the documentation.
"""

import sys,os,glob,subprocess
import shutil, re, xml.dom.minidom, subprocess
import makeMetaFromSource
from docutils.core import publish_string



root = sys.argv[1]
if not os.path.exists(os.path.join(root, 'package.xml')):
    raise Exception('package.xml not found, either not a package or not complete. Please check directory')
core = os.path.split(os.path.split(root)[0])[0]
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
    if not os.path.exists(helpDir): 
        os.mkdir(helpDir)
    shutil.copyfile(os.path.join(core, 'doc', 'make.bat'), os.path.join(helpDir, 'make.bat'))
    shutil.copyfile(os.path.join(core, 'doc', 'conf.py'), os.path.join(helpDir, 'conf.py'))
    if os.path.exists(os.path.join(helpDir, '_static')):
        shutil.rmtree(os.path.join(helpDir, '_static'))
    shutil.copytree(os.path.join(core, 'doc', '_static'), os.path.join(helpDir, '_static'), ignore = shutil.ignore_patterns('*.svn', '*.svn*'))
    #shutil.copyfile(os.path.join(core, 'doc', 'make.bat'), os.path.join(helpDir, 'Makefile'))
    #shutil.copyfile(os.path.join(core, 'doc', 'packageIndex.rst'), os.path.join(helpDir, 'index.rst'))
    # if not os.path.exists(os.path.join(helpDir, 'introduction.rst')):
        # shutil.copyfile(os.path.join(core, 'doc', 'defaultPackageIntroduciton.rst'), os.path.join(helpDir, 'introduction.rst'))
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
    d['widgets'] = [os.path.splitext(os.path.split(g)[1])[0] for g in glob.glob(os.path.join(root, 'widgets', '*.py')) if os.path.split(g)[1] != '__init__.py']
    d['qtWidgets'] = [os.path.splitext(os.path.split(g)[1])[0] for g in glob.glob(os.path.join(root, 'qtWidgets', '*.py')) if os.path.split(g)[1] != '__init__.py']
    d['signalClasses'] = [os.path.splitext(os.path.split(g)[1])[0] for g in glob.glob(os.path.join(root, 'signalClasses', '*.py')) if os.path.split(g)[1] != '__init__.py']
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
    d['Number'] = getXMLText(dom.getElementsByTagName('Number')[0].childNodes)
    d['Stability'] = getXMLText(dom.getElementsByTagName('Stability')[0].childNodes)
    d['Date'] = getXMLText(dom.getElementsByTagName('Date')[0].childNodes)
    d['Dependencies'] = getXMLText(dom.getElementsByTagName('Dependencies')[0].childNodes)
    d['Description'] = getXMLText(dom.getElementsByTagName('Description')[0].childNodes)
    
    return d
    
def makeIndex(nd):
    """Make the index files for the package."""
    
    pDict = packageToDict(os.path.join(root, 'package.xml'))
    
    index = """.. Red-R package documentation master file, created by
   sphinx-quickstart on Sat May 07 17:15:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to %(Name)s's documentation!
=========================================================================

Contents:

.. toctree::
   :glob:
   :maxdepth: 2
    
   introduction
   widgets
   signals
   qtWidgets


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""" % pDict
    
    widgets = """%(Name)s Widgets
=========================================================
Contents:

.. toctree::
   :glob:
   :maxdepth: 2
   
   widgets/*
   """ % pDict

    signals = """%(Name)s Signals
=====================================================
Contents:

.. toctree::
   :glob:
   :maxdepth: 2
   
   signalClasses/*
   """ % pDict
   
    qtWidgets = """%(Name)s QT Widgets
========================================================
Contents:

.. toctree::
   :glob:
   :maxdepth: 2
   
   qtWidgets/*
   """ % pDict

    
    s = '%s\n%s\n\n' % (pDict['Name'], '}'*len(pDict['Name']))
    s += '%s\n%s\n\n' % ('Description', '{'*len('Description'))
    s += '%s\n\n' % pDict['Description']
    
    with open(os.path.join(helpDir, 'widgets.rst'), 'w') as f:
        f.write(widgets)
    with open(os.path.join(helpDir, 'signals.rst'), 'w') as f:
        f.write(signals)
    with open(os.path.join(helpDir, 'qtWidgets.rst'), 'w') as f:
        f.write(qtWidgets)
    if not os.path.exists(os.path.join(helpDir, 'introduction.rst')):
        with open(os.path.join(helpDir, 'introduction.rst'), 'w') as f:
            f.write(s)
    ### bullet list
        
    with open(os.path.join(helpDir, 'index.rst'), 'w') as h:
        h.write(index)
        
        
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
    
    ## make the index files
    makeIndex(nd)
    
    ## now make the html by converting .rst to html.  We do this using sphinx
    shutil.rmtree(os.path.join(os.path.abspath(helpDir),'build'),True)
    cmd = 'sphinx-build -b html %s %s' % (helpDir, os.path.join(helpDir, 'build'))
    print 'Running doc compiler: ' + cmd
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
    print p
    
    # for w in d['widgets']:
        # with open(os.path.join(widgetHelp, '%s.rst' % w), 'r') as f:
            # thisFile = f.read()
            # output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            # with open(os.path.join(widgetHelp, '%s.html' % w), 'w') as h:
                # h.write(output)
                
    # for s in d['signalClasses']:
        # with open(os.path.join(signalHelp, '%s.rst' % s), 'r') as f:
            # thisFile = f.read()
            # output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            # with open(os.path.join(signalHelp, '%s.html' % w), 'w') as h:
                # h.write(output)
            
    # for s in d['qtWidgets']:
        # with open(os.path.join(qtHelp, '%s.rst' % s), 'r') as f:
            # thisFile = f.read()
            # output = publish_string(thisFile, writer_name='html', settings_overrides = overrides)
            # with open(os.path.join(qtHelp, '%s.html' % w), 'w') as h:
                # h.write(output)
    
    
    
makeHelpDirs()
makeFiles()