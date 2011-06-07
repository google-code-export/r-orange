"""orngRegistry

This module registers widgets, signals, qtWidgets, and templates for use in Red-R.  

In general these functions should be called only by Core.
"""



# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by RRCDT
#

import os, sys, re, glob, stat, redRLog

#from orngSignalManager import OutputSignal, InputSignal
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# print 'Importing orngRegistry.py'
import redRPackageManager
import signals
import xml.dom.minidom
import orngDlgs, cPickle
# redRDir = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
# if not redRDir in sys.path:
    # sys.path.append(redRDir)

import redREnviron
import redRi18n
# def _(a):
    # return a
_ = redRi18n.Coreget_()
class WidgetDescription:
    """Widget description container"""
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
class TemplateDescription:
    """Template description container"""
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
        
class WidgetCategory(dict):
    """Widget category container"""
    def __init__(self, directory, widgets):
        self.update(widgets)
        self.directory = directory

AllPackages = {}
def readCategories(force = True):
    """Reads the categories of widgets from the libraries dir of Red-R.  force indicates if the categories should be remade.  If not then a cashed categories object is used instead.  Using the cashed categories makes loading of Red-R much faster, but might result in unexpected behavior for developers.  
    
    .. note::
        When new packages are loaded force is set to true.
        
    """
    if not force:  ## if this is a reload of Red-R and we are using the same categories.
        try:
            if os.path.exists(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetRegistry.pic')):
                with open(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetRegistry.pic'), 'rb') as f:
                    categories = cPickle.load(f)
                    import imp
                    for c, v in categories['widgets'].items():
                        # debugging print c, v, v.name
                        try:
                            wmod = imp.load_source(v.fileName, v.fullName)
                        except Exception as inst:
                            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, 'Error loading widget %s' % c) 
                            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException()) 
                            #redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('<b>Error loading meta data for %s; %s</b>') % (metaFile, unicode(inst)))
                            continue
                    return categories
        except Exception as inst:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass
    # print '##########################in readCategories'
    redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Loading repository of packages.'))
    global widgetsWithError 
    widgetDirName = os.path.realpath(redREnviron.directoryNames["libraryDir"])
    
    canvasSettingsDir = os.path.realpath(redREnviron.directoryNames["canvasSettingsDir"])
    
    directories = []
    for dirName in os.listdir(widgetDirName):
        directory = os.path.join(widgetDirName, dirName)
        if os.path.isdir(directory):
            directories.append((dirName, directory, ""))
    # addOnDirName = os.path.realpath(redREnviron.directoryNames['addOnDirName'])
    # if os.path.isdir(addOnDirName):  ## can't implement because everything imports from libraries
        # for dirName in os.listdir(addOnDirName):
            # directory = os.path.join(addOnDirName, dirName)
            # if os.path.isdir(directory):
                # directories.append((dirName, directory, ""))
    categories = {'widgets':{}, 'templates':[], 'tags': None}     
    allWidgets = []
    theTags = xml.dom.minidom.parseString('<tree></tree>')
    for dirName, directory, plugin in directories:
        if not os.path.isfile(os.path.join(directory,'package.xml')): continue
        try:
            with open(os.path.join(directory,'package.xml'), 'r') as f:
                mainTabs = xml.dom.minidom.parse(f)
            package = parsePackageXML(mainTabs)
            # we read in all the widgets in dirName, directory in the directories
            widgets = readWidgets(os.path.join(directory), package)  ## calls an internal function
            AllPackages[package['Name']] = package
            if mainTabs.getElementsByTagName('menuTags'):
                newTags = mainTabs.getElementsByTagName('menuTags')[0].childNodes
                for tag in newTags:
                    if tag.nodeName == 'group': 
                        addTagsSystemTag(theTags.childNodes[0],tag)

            #print '#########widgets',widgets
            allWidgets += widgets
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, 'Error in loading package %s' % directory)
    categories['tags'] = theTags
    # print theTags
    if allWidgets: ## collect all of the widgets and set them in the catepories
        categories['widgets'] = WidgetCategory(plugin and directory or "", allWidgets)

    allTemplates = []
    for dirName, directory, plugin in directories:
        allTemplates += readTemplates(os.path.join(directory,'templates')) # a function to read in the templates that are in the directories
         #+= templates
        #print templates
    
    for directory in redREnviron.settings['templateDirectories']:
        allTemplates += readTemplates(directory)
        
    #allTemplates += readTemplates(redREnviron.directoryNames['templatesDir'])
    categories['templates'] = allTemplates
    if splashWindow:
        splashWindow.hide()
    
    redRLog.log(redRLog.REDRCORE, redRLog.INFO, _('Finished loading repository of packages.'))
    with open(os.path.join(redREnviron.directoryNames['settingsDir'], 'widgetRegistry.pic'), 'wb') as f:
        cPickle.dump(categories, f, -1)
    
    return categories ## return the widgets and the templates

hasErrors = False
splashWindow = None
widgetsWithError = []

# takes an xml object representing a red-r package and creates a structured dict
# TODO: should perform error checking to make sure the xml file is valid
def parsePackageXML(node):
    """Parse the XML data structure of the meta file."""
    packageDict = {}
    packageDict['Name'] = getXMLText(node.getElementsByTagName('Name')[0].childNodes)
    packageDict['Author'] = getXMLText(node.getElementsByTagName('Author')[0].childNodes)
    packageDict['License'] = getXMLText(node.getElementsByTagName('License')[0].childNodes)
    
    deps = getXMLText(node.getElementsByTagName('Dependencies')[0].childNodes)
    if (deps.lower() == 'none' or deps.lower() == 'base' or deps.lower() == ''):
        packageDict['Dependencies'] = []
    else:
        packageDict['Dependencies'] = deps.split(',')
        
    packageDict['Summary'] = getXMLText(node.getElementsByTagName('Summary')[0].childNodes)
    packageDict['Description'] = getXMLText(node.getElementsByTagName('Description')[0].childNodes)
    if len(node.getElementsByTagName('RLibraries')):
        Rpacks = getXMLText(node.getElementsByTagName('RLibraries')[0].childNodes)
        packageDict['RLibraries'] =  [x.strip() for x in Rpacks.split(',')]


    version = node.getElementsByTagName('Version')[0]
    # print node, version
    packageDict['Version'] = {}
    packageDict['Version']['Number'] = getXMLText(version.getElementsByTagName('Number')[0].childNodes)
    packageDict['Version']['Stability'] = getXMLText(version.getElementsByTagName('Stability')[0].childNodes)
    packageDict['Version']['Date'] = getXMLText(version.getElementsByTagName('Date')[0].childNodes)

    return packageDict

def addTagsSystemTag(tags,newTag):
    """Make the tag system that will appear in the tree view.
    
    move through the group tags in tags, if you find the grouname of tag 
    then you don't need to add it, rather just add the child tags to that tag.
    tags = theTags.childNodes[0]
    print tags.childNodes, _('Child Nodes')
    
    """
    name = unicode(newTag.getAttribute('name'))
    
    for t in tags.childNodes:
        if t.nodeName == 'group':
            #print t
            if unicode(t.getAttribute('name')) == name: ## found the right tag
                #print _('Found the name')
                #print t.childNodes
                for tt in newTag.childNodes:
                    if tt.nodeName == 'group':
                        addTagsSystemTag(t, tt) # add the child tags
            
                return
                
    ## if we made it this far we didn't find the right tag so we need to add all of the tag xml to the tags xml
    #print '|#|Name not found, appending to group.  This is normal, dont be worried.'
    tags.appendChild(newTag)
    #theTags.childNodes[0] = tags    
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

def readWidgets(directory, package):
    """This function makes the widgets categories in the categories dict.  All .py files in the widgets dir of the package are cataloged into the registry.
    
    All widgets are compiled at this time.
    """
    import sys, imp
    global hasErrors, splashWindow, widgetsWithError
    import compileall
    compileall.compile_dir(directory,quiet=True) # compile the directory for later importing.
    #print '################readWidgets', directory, package
    widgets = []
    for filename in glob.iglob(os.path.join(directory,'widgets', "*.py")):
        if os.path.isdir(filename) or os.path.islink(filename) or '__init__' in filename:
            continue
        
        datetime = unicode(os.stat(filename)[stat.ST_MTIME])
        # cachedDescription = cachedWidgetDescriptions.get(filename, None)
        # if cachedDescription and cachedDescription.time == datetime and hasattr(cachedDescription, "inputClasses"):
            # widgets.append((cachedDescription.name, cachedDescription))
            # continue
        
        dirname, fname = os.path.split(filename)
        widgetName = os.path.splitext(fname)[0]
        widgetID = unicode(package['Name']+'_'+widgetName)
        
        widgetMetaData = {}
        metaFile = os.path.join(directory,'meta','widgets',widgetName+'.xml')
        makeXML = True
        if not os.path.exists(metaFile) and '__init__' not in filename:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('<b>Meta file for %s does not exist.</b>') % (filename))
            
            if redREnviron.settings['outputVerbosity'] == 5 and makeXML and '__init__' not in filename:
                try:
                    md = orngDlgs.MetaDialog(filename)
                    if md.exec_() == orngDlgs.QDialog.Accepted:
                        text = md.text.toPlainText()
                        if not os.path.exists(os.path.join(directory, 'meta')):
                            os.mkdir(os.path.join(directory, 'meta'))
                        if not os.path.exists(os.path.join(directory, 'meta', 'widgets')):
                            os.mkdir(os.path.join(directory, 'meta', 'widgets'))
                        with open(os.path.join(directory,'meta','widgets',widgetName+'.xml'), 'w') as f: f.write(text)
                    else:
                        if md.notNow:
                            makeXML = False
                            continue
                        else:
                            continue
                except: pass
            else:
                continue
        try:
            widgetMetaXML = xml.dom.minidom.parse(metaFile)
        except Exception as inst:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException()) 
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('<b>Error loading meta data for %s; %s</b>') % (metaFile, unicode(inst)))
            continue
        widgetMetaData['name'] = getXMLText(widgetMetaXML.getElementsByTagName('name')[0].childNodes)
        widgetMetaData['icon'] = getXMLText(widgetMetaXML.getElementsByTagName('icon')[0].childNodes)
        widgetMetaData['description'] = getXMLText(widgetMetaXML.getElementsByTagName('summary')[0].childNodes)
        #widgetMetaData['details'] = getXMLText(widgetMetaXML.getElementsByTagName('summary')[0].childNodes)
        
        widgetMetaData['tags'] = [] ## will be a list of tuples in the form (<tag>, <priority>); ('Data Input', 4)
        for tag in widgetMetaXML.getElementsByTagName('tags')[0].childNodes:
            if getXMLText(tag.childNodes) != '':
                if tag.hasAttribute('priority'):
                    widgetMetaData['tags'].append((getXMLText(tag.childNodes), int(tag.getAttribute('priority'))))
                else:
                    widgetMetaData['tags'].append((getXMLText(tag.childNodes), 0))
        # debugging print widgetMetaData['tags']
        widgetMetaData['inputs'] = []
        if len(widgetMetaXML.getElementsByTagName('input')):
            for input in widgetMetaXML.getElementsByTagName('input'):
                try:
                    widgetMetaData['inputs'].append((
                    getXMLText(input.getElementsByTagName('signalClass')[0].childNodes),
                    getXMLText(input.getElementsByTagName('description')[0].childNodes)))
                except Exception as inst:
                    redRLog.log(redRLog.REDRCORE, redRLog.WARNING, 'Error in loading signals for %s, %s' % (widgetMetaData['name'], unicode(inst)))
        widgetMetaData['outputs'] = []
        if len(widgetMetaXML.getElementsByTagName('output')):
            for outputs in widgetMetaXML.getElementsByTagName('output'):
                try:
                    widgetMetaData['outputs'].append(
                    (getXMLText(outputs.getElementsByTagName('signalClass')[0].childNodes),
                    getXMLText(outputs.getElementsByTagName('description')[0].childNodes)))
                except Exception as inst:
                    redRLog.log(redRLog.REDRCORE, redRLog.WARNING, 'Error in loading signals for %s, %s' % (widgetMetaData['name'], unicode(inst)))
        # print widgetMetaData

        if splashWindow:
            splashWindow.showMessage("Registering widget %s" % widgetMetaData['name'], Qt.AlignHCenter + Qt.AlignBottom)
        qApp.processEvents()
        
        # We import modules using imp.load_source to avoid storing them in sys.modules,
        # but we need to append the path to sys.path in case the module would want to load
        # something
        dirnameInPath = dirname in sys.path
        if not dirnameInPath:
            sys.path.append(dirname)
        # print widgetName, 'redREnviron' in sys.modules.keys()
        try:
            wmod = imp.load_source(widgetID, filename)
        except Exception, msg:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, _('Exception occurred in <b>%s: %s<b>') % (filename, msg))
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, redRLog.formatException())
            continue
        
        widgetInfo = WidgetDescription(
                     name = widgetMetaData['name'],
                     packageName = package['Name'],
                     package = package,
                     time = datetime,
                     fileName = package['Name'] + '_' + widgetName,
                     widgetName = widgetName,
                     fullName = filename
                     )
        #redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, 'logging widget info %s' % widgetInfo.name)
        for k,v in widgetMetaData.items():
            setattr(widgetInfo,k,v)
     
        widgetInfo.tooltipText = "<b>%s</b><br />%s" % (widgetInfo.name, widgetInfo.description)

        ### inputs not yet working with the widet xml will include at a later time.
        #if len(widgetInfo.inputs):
            #widgetInfo.tooltipText +='<hr><b>Inputs</b><dl>'
            #for x in widgetInfo.inputs:
                #widgetInfo.tooltipText +='<dt>%s</dt><dd>%s</dd>' % x
            #widgetInfo.tooltipText +='</dl>'
        #else:
            #widgetInfo.tooltipText +='<hr><b>Inputs</b><dl>'
            #widgetInfo.tooltipText +='<dt>None</dt><dd></dd>' 
            #widgetInfo.tooltipText +='</dl>'

        #if len(widgetInfo.outputs):
            #widgetInfo.tooltipText +='<hr><b>Outputs</b><dl>'
            #for x in widgetInfo.outputs:
                #widgetInfo.tooltipText +='<dt>%s</dt><dd>%s</dd>' % x
            #widgetInfo.tooltipText +='</dl>'
        #else:
            #widgetInfo.tooltipText +='<hr><b>Inputs</b><dl>'
            #widgetInfo.tooltipText +='<dt>None</dt><dd></dd>' 
            #widgetInfo.tooltipText +='</dl>'

            
        widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', widgetInfo.icon)
        if not os.path.isfile(widgetInfo.icon):
            if os.path.isfile(os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', 'Default.png')): 
                widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'], widgetInfo.packageName,'icons', 'Default.png')
            else:
                widgetInfo.icon = os.path.join(redREnviron.directoryNames['libraryDir'],'base', 'icons', 'Unknown.png')
            
        widgets.append((widgetID, widgetInfo))
        
    return widgets

def readTemplates(directory):
    """Reads the templates that are availabel in the package specified by directory."""
    
    import sys, imp
    import zipfile
    global hasErrors, splashWindow, widgetsWithError
    
    # print '################readWidgets', directory, package
    templates = []
    for filename in glob.iglob(os.path.join(directory, "*.rrts")):
        if os.path.isdir(filename) or os.path.islink(filename):
            continue  # protects from a direcoty that has .rrs in it I guess
        print filename
        dirname, fname = os.path.split(filename)
        # dirname, package = os.path.split(dirname)
        templateName = fname
        #widgetName = package + '_' + widget
        try:
            # make a zipfile and then extract the template xml from it, then we can parse the template xml and set up the registry.
            try:
                tempZip = zipfile.ZipFile(filename)
            except zipfile.BadZipfile: continue
            if 'template.xml' not in tempZip.namelist():
                print 'no template.xml in %s, atts are %s' % (filename, unicode(tempZip.namelist()))
                continue # these templates will not work with the current settings.
            
            tempXML = xml.dom.minidom.parseString(tempZip.read('template.xml'))
            description = tempXML.getElementsByTagName('saveDescription')[0].getAttribute('tempDescription')
            try:
                name = tempXML.getElementsByTagName('Name')[0].getAttribute('name')
            except:
                name = templateName
            #if not splashWindow:
                #import redREnviron
                #logo = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
                #splashWindow = QSplashScreen(logo, Qt.WindowStaysOnTopHint)
                #splashWindow.setMask(logo.mask())
                #splashWindow.show()
            qApp.processEvents()
            templateInfo = TemplateDescription(name = name, file = filename, description = description, icon = os.path.join(redREnviron.directoryNames['canvasIconsDir'],'dialog-information.png'))
            
            templates.append((filename, templateInfo))
            
            if splashWindow:    
                splashWindow.showMessage("Registering template %s" % templateName, Qt.AlignHCenter + Qt.AlignBottom)
            
        except Exception, msg:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR,redRLog.formatException())
    print 'templates are ', templates
    return templates
def loadPackage(package):
    """Loads a Red-R package.  This will also ensure that dependencies are fulfilled for each package."""
    # print package
    downloadList = {}
    downloadList[package['Name']] = {'Version':unicode(package['Version']['Number']), 'installed':False}
    deps = redRPackageManager.packageManager.getDependencies(downloadList)
    downloadList.update(deps)
    
#### Depricated
#### we really need to change this...
#re_inputs = re.compile(r'[ \t]+self.inputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)
#re_outputs = re.compile(r'[ \t]+self.outputs\s*=\s*(?P<signals>\[[^]]*\])', re.DOTALL)


#re_tuple = re.compile(r"\(([^)]+)\)")

#def getSignalList(regex, data):
    #inmo = regex.search(data)
    #if inmo:
        #return unicode([tuple([y[0] in "'\"" and y[1:-1] or unicode(y) for y in (x.strip() for x in ttext.group(1).split(","))])
               #for ttext in re_tuple.finditer(inmo.group("signals"))])
    #else:
        #return "[]"
