# -*- coding: utf-8 -*-
""" Modified by Kyle R. Covington and Anup Parikh """
import os, sys, user, cPickle, time
from OrderedDict import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import *
if sys.platform=="win32":
    import win32com.client
#print 'Importing redREnviron.py'
# import redRi18n
def _(a):
    return a
# _ = redRi18n.Coreget_()
def __getDirectoryNames():
    """Return a dictionary with Red-R directories."""
    
    dirs = {}
    createDir = {}
    
    dirs['redRDir'] = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
    dirs['canvasDir'] = os.path.join(dirs['redRDir'], "canvas")
    dirs['canvasIconsDir'] = os.path.join(dirs['redRDir'], "canvas",'icons')
    dirs['widgetDir'] = os.path.join(dirs['redRDir'], "libraries")
    dirs['libraryDir'] = os.path.join(dirs['redRDir'], "libraries")
    dirs['qtWidgetsDir'] = os.path.join(dirs['redRDir'], "libraries",'base','qtWidgets')
    dirs['redRSignalsDir'] = os.path.join(dirs['redRDir'], "libraries",'base','signalClasses')
    dirs['examplesDir'] = os.path.join(dirs['redRDir'], "Examples")
    dirs['includes'] = os.path.join(dirs['redRDir'], "includes")
    dirs['picsDir'] = os.path.join(dirs['widgetDir'],'base', "icons")
    #dirs['addOnsDir'] = os.path.join(dirs['redRDir'], "add-ons")
    
    ####### What does this code block do????################
    #if not os.path.isdir(widgetDir) or not os.path.isdir(widgetDir):
    #    canvasDir = None
    #    widgetDir = None
    #if not os.path.isdir(picsDir):
    #    picsDir = ""
    #####################
    
    
    
    ###############################
    ## Set system specific paths##
    ###############################
    
    
    ####Windows#####
    if sys.platform=="win32":
        ### architecture specific ####???
        dirs['RDir'] = os.path.join(os.path.split(dirs['redRDir'])[0], "R", 'R-2.11.1')        
        dirs['osSpecific'] = os.path.join(dirs['redRDir'], 'win32')
        #dirs['rpyDir'] = os.path.join(dirs['redRDir'], 'win32', 'rpy3')
        
        createDir['settingsDir'] = os.path.join(os.environ['APPDATA'],'red-r')
        objShell = win32com.client.Dispatch("WScript.Shell")
        dirs['documentsDir'] = os.path.join(objShell.SpecialFolders("MyDocuments"))
        dirs['RlibPath'] = os.path.join(dirs['RDir'], 'library').replace('\\','/')

    ####Mac#####
    elif sys.platform == 'darwin':
         dirs['RDir'] = '/Applications/Red-R.app/R/R.framework/Resources/'        
         dirs['osSpecific'] = os.path.join(dirs['redRDir'], 'mac')
         dirs['rpyDir'] = os.path.join(dirs['redRDir'], 'mac', 'rpy3')
         createDir['settingsDir'] = os.path.join(os.environ['HOME'], '.red-r')        
         dirs['documentsDir'] = os.path.join(os.path.expanduser('~'), 'Red-R')
         dirs['RlibPath'] = os.path.join(dirs['RDir'], 'library')

    ####Linux#####
    else:
         print 'loading linux files'
         import platform
         bit = platform.architecture()[0]
         if bit == '32bit':
            dirs['RDir'] = os.path.join(os.path.split(dirs['redRDir'])[0], "R", 'R-2.11.1')        
            dirs['osSpecific'] = os.path.join(dirs['redRDir'], 'linux32')
            dirs['rpyDir'] = os.path.join(dirs['redRDir'], 'linux32', 'rpy3')
         else:
            print 'loading 64bit linux'
            dirs['RDir'] = os.path.join(os.path.split(dirs['redRDir'])[0], "R", 'R-2.11.1')        
            dirs['osSpecific'] = os.path.join(dirs['redRDir'], 'linux64')
            dirs['rpyDir'] = os.path.join(dirs['redRDir'], 'linux64', 'rpy3')
         
         createDir['settingsDir'] = os.path.join(os.environ['HOME'], '.red-r')        
         dirs['documentsDir'] = os.path.join(os.path.expanduser('~'))
         dirs['RlibPath'] = ''

    ###########################
    ## Red-R settings dir######
    ###########################

    createDir['reportsDir'] = os.path.join(createDir['settingsDir'], "RedRReports")
    createDir['logsDir'] = os.path.join(createDir['settingsDir'], "RedRlogs")
    createDir['canvasSettingsDir'] = os.path.join(createDir['settingsDir'], "RedRCanvas") 
    createDir['tempDirHolder'] = os.path.join(createDir['settingsDir'], 'RedRTemp')
    createDir['widgetSettingsDir'] = os.path.join(createDir['settingsDir'], "RedRWidgetSettings")
    createDir['downloadsDir'] = os.path.join(createDir['settingsDir'], "downloads")

    ###########################
    ## User doc dirs     ######
    ###########################
    createDir['templatesDir'] = os.path.join(dirs['documentsDir'], 'Red-R', 'Templates')    
    createDir['schemaDir'] = os.path.join(dirs['documentsDir'],'Red-R', 'Schemas')
    

    for dname,path in createDir.items():
        if path <> None and not os.path.isdir(path):
            try: 
               print path
               os.makedirs(path)        
            # Vista has roaming profiles that will say that this folder does not exist and will then fail to create it, because it exists...
            except: pass
    dirs.update(createDir)        
    return dirs
    
def checkInternetConnection():
    import urllib
    try:
        urllib.urlopen('http://www.google.com/')
        return True
    except:
        #redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
        return False
def samepath(path1, path2):
    return os.path.normcase(os.path.normpath(path1)) == os.path.normcase(os.path.normpath(path2))
def setTempDir(temp):
    # print _('setting temp dir') + unicode(time.time())
    
    tempDir = os.path.join(directoryNames['tempDirHolder'], temp) 
    os.mkdir(tempDir)
    directoryNames['tempDir'] = tempDir
    return tempDir
    # if not os.path.isdir():
        # os.mkdir(os.path.join(canvasSettingsDir, 'temp', unicode('temp'+unicode(dirNumber))))
        # return os.path.join(canvasSettingsDir, 'temp', unicode('temp'+unicode(dirNumber)))
    # else:
        # return setTempDir(canvasSettingsDir, int(dirNumber + 1))

        
# Loads settings from the canvas's .ini file
def loadSettings():
    # print '#################loadSettings'
    settings = {}
    filename = os.path.join(directoryNames['canvasSettingsDir'], "orngCanvas.ini")
    if os.path.exists(filename):
        try:
            settings = cPickle.load(open(filename, "rb"))
        except:
            #redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass

    settings['id'] = unicode(time.time())
    setTempDir('temp_'+ settings['id'])

    settings.setdefault("widgetListType", 3)
    settings.setdefault("iconSize", "40 x 40")
    settings.setdefault("toolbarIconSize", 1)
    settings.setdefault("toolboxWidth", 200)
    settings.setdefault('schemeIconSize', 2)
    settings.setdefault("snapToGrid", 1)
    settings.setdefault('helpMode', True)
    settings.setdefault("minSeverity", 5)
    settings.setdefault("saveWidgetsPosition", 1)
    # settings.setdefault("widgetSelectedColor", (0, 255, 0))
    # settings.setdefault("widgetActiveColor", (0,0,255))
    # settings.setdefault("lineColor", (0,255,0))
    
    settings.setdefault("exceptionLevel", 5)
    settings.setdefault("WidgetTabs", [])

    settings.setdefault("saveSchemaDir", directoryNames['documentsDir'])
    settings.setdefault("saveApplicationDir", directoryNames['canvasSettingsDir'])
    settings.setdefault("showSignalNames", 1)
    
    settings.setdefault("canvasWidth", 900)
    settings.setdefault("canvasHeight", 700)
    settings.setdefault('dockState', {'notesBox':True, 'outputBox':True, 'widgetBox':True})
        
    settings.setdefault("useDefaultPalette", 0)

    settings.setdefault('CRANrepos','http://cran.r-project.org')
    settings.setdefault('red-RPackagesUpdated',0)
    settings.setdefault('checkedForUpdates',0)
    settings.setdefault('keepForXDays', 7)
    ############################
    #Dubug and output settings##
    ############################

    settings.setdefault("dontAskBeforeClose", 0)
    settings.setdefault('askBeforeWidgetDelete', 1)
    
    settings.setdefault("writeLogFile", 1)
    settings.setdefault('logsDir', directoryNames['logsDir'])
    settings.setdefault("uploadError", 0)
    settings.setdefault("askToUploadError", 0)
    
    settings.setdefault("focusOnCatchException", 1)
    settings.setdefault("focusOnCatchOutput" , 0)
    settings.setdefault("printOutputInStatusBar", 0)
    settings.setdefault("printExceptionInStatusBar", 0)
    settings.setdefault("outputVerbosity", 3)
    settings.setdefault("displayTraceback", 0)
    
    settings.setdefault("ocShow", 1)
    settings.setdefault("owShow", 0)
    settings.setdefault("ocInfo", 1)
    settings.setdefault("owInfo", 1)
    settings.setdefault("ocWarning", 1)
    settings.setdefault("owWarning", 1)
    settings.setdefault("ocError", 1)
    settings.setdefault("owError", 1)
    
    settings.setdefault("synchronizeHelp", 1)
    settings.setdefault("firstLoad", 1)
    settings.setdefault("email", '')
    settings.setdefault('canContact', 1)
    
    ## language settings, these settings exist so that we can detect the language of the system
    settings.setdefault('language', OrderedDict([('en_EN.ISO8859-1', u'English'), ('fr_FR.ISO8859-1', u'Fran\u00E7aise'), ('de_DE.ISO8859-1', u'Deutsch'), ('latin', 'Latin')]))
    
    settings['availablelanguages'] = OrderedDict([('en_EN.ISO8859-1', u'English'), ('fr_FR.ISO8859-1', u'Fran\u00E7aise'), ('de_DE.ISO8859-1', u'Deutsch'), ('latin', 'Latin')])
    #print settings
    return settings
    
# Saves settings to this widget's .ini file
def saveSettings():
    #print 'red-r canvas saveSettings'
    filename = os.path.join(directoryNames['canvasSettingsDir'], "orngCanvas.ini")
    file=open(filename, "wb")
    if settings["widgetListType"] == 1:        # tree view
        settings["treeItemsOpenness"] = dict([(key, tabs.tabDict[key].isExpanded()) for key in tabs.tabDict.keys()])
    cPickle.dump(settings, file,2)
    file.close()
def getVersion():
    version = {}
    try:
      f = open(os.path.join(directoryNames["redRDir"],'version.txt'), 'r')
      file = f.readlines()
      f.close()
      import re
      for i in file:
	  m = re.search('!define\s(\S+)\s"(.*)"',i)
	  version[m.group(1)] = m.group(2)
    except:
      version = {'NAME': 'Red-R', 'REDRVERSION':'0', 'TYPE':'0', 'DATE':'2000.1.1', 'SVNVERSION':'0'}
    return version
            
def addOrangeDirectoriesToPath(directoryNames):
    """Add orange directory paths to Python path."""
    pathsToAdd = [directoryNames['redRDir']]
    pathsToAdd += [directoryNames['osSpecific']]
    pathsToAdd += [directoryNames['includes']]
    pathsToAdd += [directoryNames['canvasDir']]
        
    for path in pathsToAdd:
        if os.path.isdir(path) and not any([samepath(path, x) for x in sys.path]):
            sys.path.insert(0,path)
# print __name__
if __name__ =='redREnviron':   
    directoryNames = __getDirectoryNames()
    addOrangeDirectoriesToPath(directoryNames)
    version = getVersion()
    settings = loadSettings()
    print 'done with redREnviron'
#     import pprint
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(settings)

