""" Modified by Kyle R. Covington and Anup Parikh """
import os, sys, user, cPickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
if sys.platform=="win32":
    import win32com.client
#print 'Importing redREnviron.py'
def __getDirectoryNames():
    """Return a dictionary with Red-R directories."""
    try:
        redRDir = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
    except:
        pass

    canvasDir = os.path.join(redRDir, "canvas")
    RDir = os.path.join(os.path.split(redRDir)[0], "R")
    widgetDir = os.path.join(redRDir, "libraries")
    libraryDir = os.path.join(redRDir, "libraries")
    qtWidgetsDir = os.path.join(redRDir, "libraries",'base','qtWidgets')
    redRSignalsDir = os.path.join(redRDir, "libraries",'base','signalClasses')
    examplesDir = os.path.join(redRDir, "Examples")
    picsDir = os.path.join(widgetDir,'base', "icons")
    addOnsDir = os.path.join(redRDir, "add-ons")
    

    if not os.path.isdir(widgetDir) or not os.path.isdir(widgetDir):
        canvasDir = None
        widgetDir = None
    if not os.path.isdir(picsDir):
        picsDir = ""
    

    ## check that the settings directories are in place, this would be skipped over in the try
    try:
        if not os.path.isdir(os.path.join(os.environ['APPDATA'], 'red-r')):
            os.makedirs(os.path.join(os.environ['APPDATA'], 'red-r'))
        settingsDir = os.path.join(os.environ['APPDATA'],'red-r','settings')
    except:
        try:
            if not os.path.isdir(os.path.join(os.environ['HOME'], '.redr', 'red-r')):
                os.makedirs(os.path.join(os.environ['HOME'], '.redr', 'red-r'))
            settingsDir = os.path.join(os.environ['HOME'], '.redr', 'red-r','settings')
        except:
            print 'Error occured in setting the settingsDir'
    
    reportsDir = os.path.join(settingsDir, "RedRReports")
    canvasSettingsDir = os.path.join(settingsDir, "RedRCanvas") 
    widgetSettingsDir = os.path.join(settingsDir, "RedRWidgetSettings")
    downloadsDir = os.path.join(settingsDir, "downloads")

    if sys.platform=="win32":
        objShell = win32com.client.Dispatch("WScript.Shell")
        documentsDir = os.path.join(objShell.SpecialFolders("MyDocuments"),'Red-R')
        # print documentsDir
    else:
        documentsDir = os.path.join(os.path.expanduser('~'), 'Red-R')
        
    if not os.path.isdir(documentsDir):
        os.makedirs(documentsDir)
    templatesDir = os.path.join(documentsDir, 'Templates')
    if not os.path.isdir(templatesDir): 
        os.makedirs(templatesDir)
    schemaDir = os.path.join(documentsDir, 'Schemas')
    if not os.path.isdir(schemaDir): 
        os.makedirs(schemaDir)
        

    for dname in [settingsDir, widgetSettingsDir, canvasSettingsDir, reportsDir,downloadsDir]:
        if dname <> None and not os.path.isdir(dname):
            try: os.makedirs(dname)        
            # Vista has roaming profiles that will say that this folder does not exist and will then fail to create it, because it exists...
            except: pass
    
    tempDir = setTempDir(canvasSettingsDir, 1)
    # print tempDir
    return dict([(name, vars()[name]) for name in ["tempDir", "templatesDir","schemaDir", "documentsDir", "redRDir", "canvasDir", "libraryDir", "RDir", 'qtWidgetsDir', 'redRSignalsDir', "widgetDir", "examplesDir", "picsDir", "addOnsDir", "reportsDir", "settingsDir", "downloadsDir", "widgetSettingsDir",  "canvasSettingsDir"]])
def checkInternetConnection():
    import urllib
    try:
        urllib.urlopen('http://www.google.com/')
        return True
    except:
        return False
def samepath(path1, path2):
    return os.path.normcase(os.path.normpath(path1)) == os.path.normcase(os.path.normpath(path2))
def setTempDir(canvasSettingsDir, dirNumber):
    # print 'setting temp dir'
    # print dirNumber
    # if dirNumber > 5:
        # res = QMessageBox('Red-R Canvas','You seem to have several temp directories open.  Would you like to remove them?\n\nAnswer NO if you have another Red-R session open.', QMessageBox.Question, QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        
        # if res.exec_() == QMessageBox.Yes:
            # import shutil
            # shutil.rmtree(os.path.join(canvasSettingsDir, 'temp'), True)
    try:  # try to make the canvas temp dir.  This should work but I would be cautious given the problems with the Vista system.
        if not os.path.isdir(os.path.join(canvasSettingsDir, 'temp')):
            os.mkdir(os.path.join(canvasSettingsDir, 'temp'))
    except: pass
    if not os.path.isdir(os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber)))):
        os.mkdir(os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber))))
        return os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber)))
    else:
        return setTempDir(canvasSettingsDir, int(dirNumber + 1))

        
# Loads settings from the canvas's .ini file
def loadSettings():
    settings = {}
    filename = os.path.join(directoryNames['canvasSettingsDir'], "orngCanvas.ini")
    if os.path.exists(filename):
        try:
            settings = cPickle.load(open(filename, "rb"))
        except:
            pass

    settings.setdefault("widgetListType", 3)
    settings.setdefault("iconSize", "40 x 40")
    settings.setdefault("toolbarIconSize", 2)
    settings.setdefault("toolboxWidth", 200)
    settings.setdefault('schemeIconSize', 1)
    settings.setdefault("snapToGrid", 1)
    
    
    settings.setdefault("saveWidgetsPosition", 1)
    settings.setdefault("widgetSelectedColor", (0, 255, 0))
    settings.setdefault("widgetActiveColor", (0,0,255))
    settings.setdefault("lineColor", (0,255,0))


    settings.setdefault("saveSchemaDir", directoryNames['documentsDir'])
    settings.setdefault("saveApplicationDir", directoryNames['canvasSettingsDir'])
    settings.setdefault("showSignalNames", 1)
    
    settings.setdefault("canvasWidth", 700)
    settings.setdefault("canvasHeight", 600)

        
    settings.setdefault("useDefaultPalette", 0)

    settings.setdefault('CRANrepos','http://cran.r-project.org')
    settings.setdefault('red-RPackagesUpdated',0)
    
    
    settings.setdefault("writeLogFile", 1)
    settings.setdefault("dontAskBeforeClose", 0)
    settings.setdefault("debugMode", 0)
    settings.setdefault("uploadError", 0)
    settings.setdefault("askToUploadError", 0)
    settings.setdefault("focusOnCatchException", 1)
    settings.setdefault("focusOnCatchOutput" , 0)
    settings.setdefault("printOutputInStatusBar", 1)
    settings.setdefault("printExceptionInStatusBar", 1)
    settings.setdefault("outputVerbosity", 0)
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
    return settings
    
# Saves settings to this widget's .ini file
def saveSettings():
    print 'red-r canvas saveSettings'
    filename = os.path.join(directoryNames['canvasSettingsDir'], "orngCanvas.ini")
    file=open(filename, "wb")
    if settings["widgetListType"] == 1:        # tree view
        settings["treeItemsOpenness"] = dict([(key, tabs.tabDict[key].isExpanded()) for key in tabs.tabDict.keys()])
    cPickle.dump(settings, file,2)
    file.close()
def getVersion():
    if len(version.keys()) ==0:
        f = open(os.path.join(directoryNames["redRDir"],'version.txt'), 'r')
        file = f.readlines()
        f.close()
        import re
        for i in file:
            m = re.search('!define\s(\S+)\s"(.*)"',i)
            version[m.group(1)] = m.group(2)
    return version
        
def addOrangeDirectoriesToPath(directoryNames):
    """Add orange directory paths to Python path."""
    pathsToAdd = [directoryNames['redRDir']]
    pathsToAdd.append(directoryNames['canvasDir'])
    pathsToAdd.append(directoryNames['libraryDir'])

    if directoryNames['libraryDir'] <> None and os.path.isdir(directoryNames['libraryDir']):
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x) for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'widgets') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'qtWidgets') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'signalClasses') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        
    
    for path in pathsToAdd:
        if os.path.isdir(path) and not any([samepath(path, x) for x in sys.path]):
            #sys.path.insert(0, path)
            sys.path.append(path)

directoryNames = __getDirectoryNames()
addOrangeDirectoriesToPath(directoryNames)

version = {}
version = getVersion()
settings = loadSettings()


