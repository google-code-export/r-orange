""" Modified by Kyle R. Covington and Anup Parikh """
import os, sys, user

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
    tagsDir = os.path.join(redRDir, "tagsSystem")
    picsDir = os.path.join(widgetDir,'base', "icons")
    addOnsDir = os.path.join(redRDir, "add-ons")
    

    if not os.path.isdir(widgetDir) or not os.path.isdir(widgetDir):
        canvasDir = None
        widgetDir = None
    if not os.path.isdir(picsDir):
        picsDir = ""
    

    ## check that the settings directories are in place, this would be skipped over in the try
    if not os.path.isdir(os.path.join(os.environ['APPDATA'], 'red-r')):
        os.mkdir(os.path.join(os.environ['APPDATA'], 'red-r'))
    orangeSettingsDir = os.path.join(os.environ['APPDATA'],'red-r','settings')
    
    reportsDir = os.path.join(orangeSettingsDir, "RedRReports")
    canvasSettingsDir = os.path.join(orangeSettingsDir, "RedRCanvas") 
    
    
    widgetSettingsDir = os.path.join(orangeSettingsDir, "RedRWidgetSettings")

    for dname in [orangeSettingsDir, widgetSettingsDir, canvasSettingsDir, reportsDir]:
        if dname <> None and not os.path.isdir(dname):
            try: os.makedirs(dname)        # Vista has roaming profiles that will say that this folder does not exist and will then fail to create it, because it exists...
            except: pass
    
    tempDir = setTempDir(canvasSettingsDir, 1)
    print tempDir
    return dict([(name, vars()[name]) for name in ["tempDir", "redRDir", "canvasDir", "libraryDir", "RDir", 'qtWidgetsDir', 'redRSignalsDir', "widgetDir", "tagsDir", "picsDir", "addOnsDir", "reportsDir", "orangeSettingsDir", "widgetSettingsDir",  "canvasSettingsDir"]])
def checkInternetConnection():
    import urllib
    try:
        urllib.urlopen('http://www.red-r.org/')
        return True
    except:
        return False
def samepath(path1, path2):
    return os.path.normcase(os.path.normpath(path1)) == os.path.normcase(os.path.normpath(path2))
def setTempDir(canvasSettingsDir, dirNumber):
    try:  # try to make the canvas temp dir.  This should work but I would be cautious given the problems with the Vista system.
        if not os.path.isdir(os.path.join(canvasSettingsDir, 'temp')):
            os.mkdir(os.path.join(canvasSettingsDir, 'temp'))
    except: pass
    if not os.path.isdir(os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber)))):
        os.mkdir(os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber))))
        return os.path.join(canvasSettingsDir, 'temp', str('temp'+str(dirNumber)))
    else:
        return setTempDir(canvasSettingsDir, int(dirNumber + 1))
def addOrangeDirectoriesToPath(directoryNames):
    """Add orange directory paths to Python path."""
    pathsToAdd = [directoryNames['redRDir']]

    if canvasDir <> None:
        pathsToAdd.append(canvasDir)

    if directoryNames['libraryDir'] <> None and os.path.isdir(directoryNames['libraryDir']):
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x) for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'widgets') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'qtWidgets') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        pathsToAdd.extend([os.path.join(directoryNames['libraryDir'], x,'signalClasses') for x in os.listdir(directoryNames['libraryDir']) if os.path.isdir(os.path.join(directoryNames['libraryDir'], x))])
        
    
    for path in pathsToAdd:
        if os.path.isdir(path) and not any([samepath(path, x) for x in sys.path]):
            sys.path.insert(0, path)

directoryNames = __getDirectoryNames()
globals().update(directoryNames)
addOrangeDirectoriesToPath(directoryNames)
