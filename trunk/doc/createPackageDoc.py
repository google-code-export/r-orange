"""Make package docs.

This module aids developers in making documentation files from annotated package files.  The widgets, qtWidgets, and signal classes are parsed to generate the documentation.
"""

import sys,os,glob,subprocess
import shutil
import makeMetaFromSource
from docutils.core import publish_string

root = os.path.abspath(sys.argv[1])
helpDir = os.path.join(root, 'help')
widgetHelp = os.path.join(helpDir, 'widgets')
metaDir = os.path.join(root, 'meta')
widgetMeta = os.path.join(metaDir, 'widgets')
signalMeta = os.path.join(metaDir, 'signalClasses')
qtMeta = os.path.join(metaDir, 'qtWidgets')



def makeHelpDirs():
    """Make essential files for the help directories"""
    if not os.path.exists(helpDir): os.mkdir(helpDir)
    if not os.path.exists(metaDir): os.mkdir(metaDir)
    if not os.path.exists(widgetHelp): os.mkdir(widgetHelp)
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
    
def makeFiles():
    d = getPackageComponents()
    
    ## make rst and xml files.
    for w in [os.path.splitext(os.path.split(w)[1])[0] for w in d['widgets']]:
        print 'Parsing file %s.' % w
        makeMetaFromSource.parseWidgetFile(os.path.join(root, 'widgets', '%s.py' % w), os.path.join(widgetMeta, '%s.xml' % w), os.path.join(widgetHelp, '%s.rst' % w))
    for s in [os.path.splitext(os.path.split(s)[1])[0] for s in d['signalClasses']]:
        print 'Parsing signal %s.' % s
        makeMetaFromSource.parseSignalFile(os.path.join(root, 'signalClasses', '%s.py' % s), os.path.join(signalMeta, '%s.xml'))
    
    ## now make the html by converting .rst to html
    for w in [os.path.splitext(os.path.split(w)[1])[0] for w in d['widgets']]:
        with open(os.path.join(widgetHelp, '%s.rst' % w), 'r') as f:
            thisFile = f.read()
            output = publish_string(thisFile, writer_name='html')
            with open(os.path.join(widgetHelp, '%s.html' % w), 'w') as h:
                h.write(output)
                
makeHelpDirs()
makeFiles()