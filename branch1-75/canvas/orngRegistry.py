# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington
#

import os, sys, re, glob, stat
from orngSignalManager import OutputSignal, InputSignal
from PyQt4.QtCore import *
from PyQt4.QtGui import *
print 'Importing orngRegistry.py'
import orngOutput, redRGUI,redRPackageManager
import signals
import xml.dom.minidom

redRDir = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
if not redRDir in sys.path:
    sys.path.append(redRDir)

import redREnviron

class WidgetDescription:
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
class TemplateDescription:
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
        
class WidgetCategory(dict):
    def __init__(self, directory, widgets):
        self.update(widgets)
        self.directory = directory

AllPackages = {}
def readCategories():
    global widgetsWithError 
    widgetDirName = os.path.realpath(redREnviron.directoryNames["libraryDir"])
    canvasSettingsDir = os.path.realpath(redREnviron.directoryNames["canvasSettingsDir"])
    cacheFilename = os.path.join(canvasSettingsDir, "cachedWidgetDescriptions.pickle")

    try:
        import cPickle
        cats = cPickle.load(file(cacheFilename, "rb"))
        cachedWidgetDescriptions = dict([(w.fullName, w) for cat in cats.values() for w in cat.values()])
    except:
        cachedWidgetDescriptions = {} 

    directories = []
    for dirName in os.listdir(widgetDirName):
        directory = os.path.join(widgetDirName, dirName)
        if os.path.isdir(directory):
            directories.append((dirName, directory, ""))

    categories = {'widgets':[], 'templates':[], 'tags': None}     
    allWidgets = []
    theTags = xml.dom.minidom.parseString('<tree></tree>')

    for dirName, directory, plugin in directories:
        if not os.path.isfile(os.path.join(directory,'package.xml')): continue
        f = open(os.path.join(directory,'package.xml'), 'r')
        mainTabs = xml.dom.minidom.parse(f)
        f.close()
        package = redRPackageManager.packageManager.parsePackageXML(mainTabs)
        
        # we read in all the widgets in dirName, directory in the directories
        widgets = readWidgets(os.path.join(directory,'widgets'), package, cachedWidgetDescriptions)  ## calls an internal function
        AllPackages[package['Name']] = package
        if mainTabs.getElementsByTagName('menuTags'):
            newTags = mainTabs.getElementsByTagName('menuTags')[0].childNodes
            for tag in newTags:
                if tag.nodeName == 'group': 
                    addTagsSystemTag(theTags.childNodes[0],tag)

        #print '#########widgets',widgets
        allWidgets += widgets
    categories['tags'] = theTags
    # print theTags
    if allWidgets: ## collect all of the widgets and set them in the catepories
        categories['widgets'] = WidgetCategory(plugin and directory or "", allWidgets)

    allTemplates = []
    for dirName, directory, plugin in directories:
        templates = readTemplates(os.path.join(directory,'templates')) # a function to read in the templates that are in the directories
        allTemplates += templates
        #print templates
        
    allTemplates += readTemplates(redREnviron.directoryNames['templatesDir'])
    categories['templates'] = allTemplates
    cPickle.dump(categories, file(cacheFilename, "wb"))
    if splashWindow:
        splashWindow.hide()
    return categories ## return the widgets and the templates

hasErrors = False
splashWindow = None
widgetsWithError = []

def addTagsSystemTag(tags,newTag):
                
    name = str(newTag.getAttribute('name'))
    # move through the group tags in tags, if you find the grouname of tag 
    #then you don't need to add it, rather just add the child tags to that tag.
    #tags = theTags.childNodes[0]
    #print tags.childNodes, 'Child Nodes'
    for t in tags.childNodes:
        if t.nodeName == 'group':
            #print t
            if str(t.getAttribute('name')) == name: ## found the right tag
                #print 'Found the name'
                #print t.childNodes
                for tt in newTag.childNodes:
                    if tt.nodeName == 'group':
                        addTagsSystemTag(t, tt) # add the child tags
            
                return
                
    ## if we made it this far we didn't find the right tag so we need to add all of the tag xml to the tags xml
    #print '|#|Name not found, appending to group.  This is normal, dont be worried.'
    tags.appendChild(newTag)
    #theTags.childNodes[0] = tags    

def readWidgets(directory, package, cachedWidgetDescriptions):
    import sys, imp
    global hasErrors, splashWindow, widgetsWithError
    
    # print '################readWidgets', directory, package
    widgets = []
    for filename in glob.iglob(os.path.join(directory, "*.py")):
        if os.path.isdir(filename) or os.path.islink(filename):
            continue
        
        datetime = str(os.stat(filename)[stat.ST_MTIME])
        cachedDescription = cachedWidgetDescriptions.get(filename, None)
        if cachedDescription and cachedDescription.time == datetime and hasattr(cachedDescription, "inputClasses"):
            widgets.append((cachedDescription.name, cachedDescription))
            continue
        widgetID = str(package['Name']+'_'+os.path.split(filename)[1].split('.')[0])
        data = file(filename).read()
        istart = data.find("<name>")
        iend = data.find("</name>")
        if istart < 0 or iend < 0:
            continue
        name = data[istart+6:iend]
        inputList = getSignalList(re_inputs, data)
        outputList = getSignalList(re_outputs, data)
        
        dirname, fname = os.path.split(filename)
        widgetName = os.path.splitext(fname)[0]
        try:
            import redREnviron
            if not splashWindow:
                
                logo = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
                splashWindow = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
                splashWindow.setMask(logo.mask())
                splashWindow.show()
                
            splashWindow.showMessage("Registering widget %s" % name, Qt.AlignHCenter + Qt.AlignBottom)
            qApp.processEvents()
            
            # We import modules using imp.load_source to avoid storing them in sys.modules,
            # but we need to append the path to sys.path in case the module would want to load
            # something
            dirnameInPath = dirname in sys.path
            if not dirnameInPath:
                sys.path.append(dirname)
        
            wmod = imp.load_source(package['Name'] + '_' + widgetName, filename)

            #wmod.__dict__['widgetFilename'] = filename
            # if not dirnameInPath and dirname in sys.path: # I have no idea, why we need this, but it seems to disappear sometimes?!
                # sys.path.remove(dirname)
            
            widgetInfo = WidgetDescription(
                         name = data[istart+6:iend],
                         packageName = package['Name'],
                         package = package,
                         time = datetime,
                         fileName = package['Name'] + '_' + widgetName,
                         widgetName = widgetName,
                         fullName = filename,
                         inputList = inputList, outputList = outputList
                         )
    
            for attr, deflt in (("contact>", "") , ("icon>", "Default.png"), ("priority>", "5000"), ("description>", ""), ("tags>", "Prototypes"), ("outputWidgets>", ""), ("inputWidgets>", "")):
                istart, iend = data.find("<"+attr), data.find("</"+attr)
                setattr(widgetInfo, attr[:-1], istart >= 0 and iend >= 0 and data[istart+1+len(attr):iend].strip() or deflt)
                
            widgetInfo.tags = widgetInfo.tags.replace(' ', '')
            widgetInfo.tags = widgetInfo.tags.split(',')  # converts the tags to a list split by the comma
            ## set the icon, this might not exist so we need to check
            widgetInfo.outputWidgets = widgetInfo.outputWidgets.replace(' ', '').split(',')
            widgetInfo.inputWidgets = widgetInfo.inputWidgets.replace(' ', '')
            widgetInfo.inputWidgets = widgetInfo.inputWidgets.split(',')

                
            widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', widgetInfo.icon)
            if not os.path.isfile(widgetInfo.icon):
                if os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', 'Default.png')): 
                    widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', 'Default.png')
                else:
                    widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'],'base', 'icons', 'Unknown.png')
                
            # build the tooltip
            ## these widgetInfo.inputs and outputs are where Red-R defines connections.  This is unstable and should be changed in later versions.  Perhaps all of the widgets should be loaded into memory before they appear here.  Either that or the inputs and outputs should not be displayed in the tooltip.
            widgetInfo.inputs = [InputSignal(*signal) for signal in eval(widgetInfo.inputList)]
            if len(widgetInfo.inputs) == 0:
                formatedInList = "<b>Inputs:</b><br> &nbsp;&nbsp; None<br>"
            else:
                formatedInList = "<b>Inputs:</b><br>"
                for signal in widgetInfo.inputs:
                    formatedInList += " &nbsp;&nbsp; - " + signal.name + " (" + signal.type + ")<br>"
    
            widgetInfo.outputs = [OutputSignal(*signal) for signal in eval(widgetInfo.outputList)]
            if len(widgetInfo.outputs) == 0:
                formatedOutList = "<b>Outputs:</b><br> &nbsp; &nbsp; None<br>"
            else:
                formatedOutList = "<b>Outputs:</b><br>"
                for signal in widgetInfo.outputs:
                    formatedOutList += " &nbsp; &nbsp; - " + signal.name + " (" + signal.type + ")<br>"
    
            widgetInfo.tooltipText = "<b><b>&nbsp;%s</b></b><hr><b>Description:</b><br>&nbsp;&nbsp;%s<hr>%s<hr>%s" % (name, widgetInfo.description, formatedInList[:-4], formatedOutList[:-4]) 
            widgets.append((widgetID, widgetInfo))
        except Exception, msg:
            orngOutput.printException()
            # if not hasErrors:
                # print "There were problems importing the following widgets:"
                # hasErrors = True
            # print "   %s: %s" % (widgetName, msg)
            # widgetsWithError.append(widgetName)
        
    return widgets

def readTemplates(directory):
    import sys, imp
    global hasErrors, splashWindow, widgetsWithError
    
    # print '################readWidgets', directory, package
    templates = []
    for filename in glob.iglob(os.path.join(directory, "*.rrts")):
        if os.path.isdir(filename) or os.path.islink(filename):
            continue  # protects from a direcoty that has .rrs in it I guess

        dirname, fname = os.path.split(filename)
        # dirname, package = os.path.split(dirname)
        templateName = fname
        #widgetName = package + '_' + widget
        try:
            if not splashWindow:
                import redREnviron
                logo = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
                splashWindow = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
                splashWindow.setMask(logo.mask())
                splashWindow.show()
                
            splashWindow.showMessage("Registering template %s" % templateName, Qt.AlignHCenter + Qt.AlignBottom)
            qApp.processEvents()
            templateInfo = TemplateDescription(name = templateName, file = filename) 
            templates.append(templateInfo)
        except Exception, msg:
            orngOutput.printException()
        
    return templates
def loadPackage(package):
    # print package
    downloadList = {}
    downloadList[package['Name']] = {'Version':str(package['Version']['Number']), 'installed':False}
    deps = redRPackageManager.packageManager.getDependencies(downloadList)
    downloadList.update(deps)
    # print downloadList
    for name,version in downloadList.items():
        if package =='base': continue
        if not hasattr(redRGUI,name):
            redRGUI.registerQTWidgets(name)
        if not hasattr(signals,name):
            signals.registerRedRSignals(name)
    
    
    
    
### we really need to change this...
re_inputs = re.compile(r'[ \t]+self.inputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)
re_outputs = re.compile(r'[ \t]+self.outputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)


re_tuple = re.compile(r"\(([^)]+)\)")

def getSignalList(regex, data):
    inmo = regex.search(data)
    if inmo:
        return str([tuple([y[0] in "'\"" and y[1:-1] or str(y) for y in (x.strip() for x in ttext.group(1).split(","))])
               for ttext in re_tuple.finditer(inmo.group("signals"))])
    else:
        return "[]"
