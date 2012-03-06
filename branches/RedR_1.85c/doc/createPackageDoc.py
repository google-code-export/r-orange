"""Make package docs.

This module aids developers in making documentation files from annotated package files.  The widgets, qtWidgets, and signal classes are parsed to generate the documentation.
"""

import sys,os,glob,subprocess
import shutil, re, xml.dom.minidom
import makeMetaFromSource
from docutils.core import publish_string



def createDoc(root):
    print 'Compiling %s' % root
    if not os.path.exists(os.path.join(root, 'package.xml')):
        print 'package.xml not found, either not a package or not complete. Please check directory'
        return
    core = os.path.split(os.path.split(root)[0])[0]

    helpDir = os.path.join(root, 'help')
    userHelpDir = os.path.join(root, 'help','userDoc')
    devHelpDir = os.path.join(root, 'help','devDoc')

    userWidgetHelp = os.path.join(userHelpDir, 'widgets')
    userSignalHelp = os.path.join(userHelpDir, 'signalClasses')
    userQtHelp = os.path.join(userHelpDir, 'qtWidgets')

    devWidgetHelp = os.path.join(devHelpDir, 'widgets')
    devSignalHelp = os.path.join(devHelpDir, 'signalClasses')
    devQtHelp = os.path.join(devHelpDir, 'qtWidgets')

    metaDir = os.path.join(root, 'meta')
    widgetMeta = os.path.join(metaDir, 'widgets')
    signalMeta = os.path.join(metaDir, 'signalClasses')
    qtMeta = os.path.join(metaDir, 'qtWidgets')
    qtMeta = os.path.join(metaDir, 'qtWidgets')

    overrides = {'stylesheet':[os.path.join(os.path.split(os.path.split(root)[0])[0], 'doc', 'helpDocStyle.css')]}

    def makeHelpDirs():
        """Make essential files for the help directories"""
        
        if not os.path.exists(helpDir): os.mkdir(helpDir)
        if not os.path.exists(userHelpDir): os.mkdir(userHelpDir)
        if not os.path.exists(devHelpDir): os.mkdir(devHelpDir)
        if not os.path.exists(metaDir): os.mkdir(metaDir)
        
        if not os.path.exists(userWidgetHelp): os.mkdir(userWidgetHelp)
        if not os.path.exists(userSignalHelp): os.mkdir(userSignalHelp)
        if not os.path.exists(userQtHelp): os.mkdir(userQtHelp)
        
        if not os.path.exists(devWidgetHelp): os.mkdir(devWidgetHelp)
        if not os.path.exists(devSignalHelp): os.mkdir(devSignalHelp)
        if not os.path.exists(devQtHelp): os.mkdir(devQtHelp)
        
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
        
        userIndex = """%(Name)s Package (%(Number)s)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

General Info
========================

Author: %(Author)s

Number: %(Number)s

Stability: %(Stability)s, Date: %(Date)s

Description
================

%(Description)s

User Doc
========

.. toctree::
   :glob:
   :maxdepth: 1
   
   extra/*

Widgets
=======

.. toctree::
   :glob:
   :maxdepth: 1
   
   widgets/*

Signals
=====================================================

.. toctree::
   :glob:
   :maxdepth: 1
   
   signalClasses/*

QT Widgets
===========

.. toctree::
   :glob:
   :maxdepth: 1
   
   qtWidgets/*
   """ % pDict

        
        index = """
User Doc
========
.. toctree::
   :glob:
   :maxdepth: 2
   
   userDoc/*

Dev Doc
========
.. toctree::
   :glob:
   :maxdepth: 2

   devDoc/*
   
   """
        
        with open(os.path.join(userHelpDir, 'index.rst'), 'w') as h:
            h.write(userIndex)
        with open(os.path.join(devHelpDir, 'index.rst'), 'w') as h:
            h.write(userIndex)
        with open(os.path.join(helpDir, 'index.rst'), 'w') as h:
            h.write(index)
            
            
    def makeFiles():
        d = getPackageComponents()
        nd = {'W':[], 'S':[], 'Q':[]}
        ## make rst and xml files.
        for w in d['widgets']:
            print os.path.join(root, 'widgets', '%s.py' % w)
            wn = makeMetaFromSource.parseWidgetFile(os.path.join(root, 'widgets', '%s.py' % w), 
                os.path.join(widgetMeta, '%s.xml' % w), 
                os.path.join(userWidgetHelp, '%s.rst' % w), os.path.join(devWidgetHelp, '%s.rst' % w))
            nd['W'].append((w, wn))
            
            
            
        for s in d['signalClasses']:
            sn = makeMetaFromSource.parseSignalFile(os.path.join(root, 'signalClasses', '%s.py' % s), 
                os.path.join(userSignalHelp, '%s.rst' % s),
                os.path.join(devSignalHelp, '%s.rst' % s),
                os.path.join(signalMeta, '%s.xml' % s))
            nd['S'].append((s, sn))
        
        
        for q in d['qtWidgets']:
            qn = makeMetaFromSource.parseQTWidgetFile(os.path.join(root, 'qtWidgets', '%s.py' % q), 
                os.path.join(userQtHelp, '%s.rst' % q),
                os.path.join(devQtHelp, '%s.rst' % q),
                os.path.join(qtMeta, '%s.xml' % q))
            nd['Q'].append((q, qn))
        
        ## make the index files
        makeIndex(nd)
        
    makeHelpDirs()
    makeFiles()
    
    cmd = 'sphinx-build -c ./ -b html %s %s' % (helpDir.replace('\\','/'),helpDir.replace('\\','/'))# os.path.join(root, 'help').replace('\\','/'))
    print 'Running doc compiler: ' + cmd
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    print p

if sys.argv[1]:
    createDoc(sys.argv[1])
# import docSearcher
# docSearcher.createIndex()

# if os.path.exists(os.path.join(root, 'help')):
    # shutil.rmtree(os.path.join(root, 'help'))
  

#cmd = 'sphinx-build -c ./ -b html %s %s' % (helpDir.replace('\\','/'),helpDir.replace('\\','/'))# os.path.join(root, 'help').replace('\\','/'))
#print 'Running doc compiler: ' + cmd
#p = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
#print p

