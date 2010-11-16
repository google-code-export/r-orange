## <redRSaveLoad Module.  This module (not a class) will contain and provide functions for loading and saving of objects.  The module will make great use of the redRObjects module to access and instantiate objects.>
    # Copyright (C) 2010 Kyle R Covington

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, redRObjects, cPickle, redREnviron, log, globalData, RSession, redRPackageManager
import cPickle, math, orngHistory, zipfile, urllib, sip
from xml.dom.minidom import Document, parse
from orngSignalManager import SignalManager
schemaPath = redREnviron.settings["saveSchemaDir"]
_schemaName = ""
canvasDlg = None
schemaDoc = None
signalManager = SignalManager()
def setSchemaDoc(doc):
    global schemaDoc
    schemaDoc = doc
def setCanvasDlg(dlg):
    global canvasDlg
    canvasDlg = dlg
def minimumY():
    y = 0
    for w in redRObjects.getIconsByTab(redRObjects.activeTabName())[redRObjects.activeTabName()]:
        if w.y() > y:
            y = w.y()
    if y != 0:
        y += 30
    return y
    
## ideas behind saveing.  we should think about the possibility that there will be a template in the saving process.

### we should save all of the R session in the event of saving the main file
### we need to save instances, icons, and connections.  As the instances are the core they will be saved first as all other objects must reffer to them, then we will instantiate the connections between the widgets, finally the tabs and icons will be instantiated because they do not require anything but references to the instances and their connection handlers.

### saveing the instances is fairly strait forward as is reloading them except that the signals must be started after all of the instances are loaded...  Thus there should be a special function for this.  Additionally, in the event of a template we can't only rely on the instance ID because this might be duplicated if a template is loaded multiple times.  To handle this templates will use a template crutch to map template id's to widget id's during loading.  For example, load instances and map old instnce ID's to new instance id's using the templateCrutchDict.  On loading of the signals and the icons we use the templateCrutchDict we connect signals using that instead of the orriginal ID's.


    
    
def saveIcon(widgetIconsXML, wi, doc):
    log.log(1, 9, 3, 'orngDoc makeTemplate; saving widget %s' % wi)
    witemp = doc.createElement('widgetIcon')
    witemp.setAttribute('name', str(wi.getWidgetInfo().fileName))             # save icon name
    witemp.setAttribute('instance', str(wi.instanceID))        # save instance ID
    witemp.setAttribute("xPos", str(int(wi.x())) )      # save the xPos
    witemp.setAttribute("yPos", str(int(wi.y())) )      # same the yPos
    witemp.setAttribute("caption", wi.caption)          # save the caption
    widgetIconsXML.appendChild(witemp)

def saveInstances(instances, widgets, doc, progressBar):
    settingsDict = {}
    requireRedRLibraries = {}
    progress = 0
    if type(instances) == dict:
        instances = instances.values()
    for widget in instances:
        temp = doc.createElement("widget")
        
        temp.setAttribute("widgetName", widget.widgetInfo.fileName)
        temp.setAttribute("packageName", widget.widgetInfo.package['Name'])
        temp.setAttribute("packageVersion", widget.widgetInfo.package['Version']['Number'])
        temp.setAttribute("widgetFileName", os.path.basename(widget.widgetInfo.fullName))
        temp.setAttribute('widgetID', widget.widgetID)
        print 'save in orngDoc ' + str(widget.captionTitle)
        progress += 1
        progressBar.setValue(progress)
        
        s = widget.getSettings()
        i = widget.getInputs()
        o = widget.getOutputs()
        c = widget.outputs.returnOutputs()
        
        settingsDict[widget.widgetID] = {}
        settingsDict[widget.widgetID]['settings'] = cPickle.dumps(s,2)
        settingsDict[widget.widgetID]['inputs'] = cPickle.dumps(i,2)
        settingsDict[widget.widgetID]['outputs'] = cPickle.dumps(o,2)
        settingsDict[widget.widgetID]['connections'] = cPickle.dumps(c, 2)
        
        if widget.widgetInfo.package['Name'] != 'base' and widget.widgetInfo.package['Name'] not in requireRedRLibraries.keys():
            requireRedRLibraries[widget.widgetInfo.package['Name']] = widget.widgetInfo.package
    
        widgets.appendChild(temp)
    return (widgets, settingsDict, requireRedRLibraries)
    
def makeTemplate(filename = None, copy = False):
    ## this is different from saving.  We want to make a special file that only has the selected widgets, their connections, and settings.  No R data or tabs are saved.
    if not copy:
        if not filename:
            log.log(1, 3, 3, 'orngDoc in makeTemplate; no filename specified, this is highly irregular!! Exiting from template save.')
            return
        tempDialog = TemplateDialog()
        if tempDialog.exec_() == QDialog.Rejected:
            return
    else:
        filename = redREnviron.directoryNames['tempDir']+'/copy.rrts'
    progressBar = startProgressBar(
    'Saving '+str(os.path.basename(filename)),
    'Saving '+str(os.path.basename(filename)),
    len(redRObjects.instances(wantType = 'list'))+len(redRObjects.lines().values())+3)
    progress = 0
    # create xml document
    (doc, schema, header, widgets, lines, settings, required, tabs, saveTagsList, saveDescription) = makeXMLDoc()
    requiredRLibraries = {}
    
    # save the widgets
    tempWidgets = {}
    for w in redRObjects.activeTab().getSelectedWidgets():
        tempWidgets[w.instanceID] = w.instance()
    (widgets, settingsDict, requireRedRLibraries) = saveInstances(tempWidgets, widgets, doc, progressBar)
    # save the icons and the lines
    sw = redRObjects.activeTab().getSelectedWidgets()
    log.log(1, 9, 3, 'orngDoc makeTemplate; selected widgets: %s' % sw)
    temp = doc.createElement('tab')
    temp.setAttribute('name', 'template')
    
    ## set all of the widget icons on the tab
    widgetIcons = doc.createElement('widgetIcons')
    for wi in sw:
        saveIcon(widgetIcons, wi, doc)
        
    # tabLines = doc.createElement('tabLines')
    # for line in redRObjects.getLinesByTab()[redRObjects.activeTabName()]:
        # log.log(1, 3, 3, 'orngDoc makeTemplate; checking line %s, inWidget %s, outWidget %s' % (line, line.inWidget, line.outWidget))
        # if (line.inWidget not in sw) or (line.outWidget not in sw): 
            # continue
        # saveLine(tabLines, line)
        
    temp.appendChild(widgetIcons)       ## append the widgetIcons XML to the global XML
    #temp.appendChild(tabLines)          ## append the tabLines XML to the global XML
    tabs.appendChild(temp)

    
    ## save the global settings ##
    settingsDict['_globalData'] = cPickle.dumps(globalData.globalData,2)
    settingsDict['_requiredPackages'] =  cPickle.dumps({'R': requiredRLibraries.keys(),'RedR': requireRedRLibraries},2)
    #print requireRedRLibraries
    file = open(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'), "wt")
    file.write(str(settingsDict))
    file.close()
    
    if not copy:
        taglist = str(tempDialog.tagsList.text())
        tempDescription = str(tempDialog.descriptionEdit.toPlainText())
        saveTagsList.setAttribute("tagsList", taglist)
        saveDescription.setAttribute("tempDescription", tempDescription)
        
    xmlText = doc.toprettyxml()
    progress += 1
    progressBar.setValue(progress)
    
    
    tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
    file = open(tempschema, "wt")
    file.write(xmlText)
    file.close()
    zout = zipfile.ZipFile(filename, "w")
    zout.write(tempschema,"tempSchema.tmp")
    zout.write(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'),'settings.pickle')
    zout.close()
    doc.unlink()
    if copy:
        loadTemplate(filename)
        
    
    progress += 1
    progressBar.setValue(progress)
    progressBar.close()
    log.log(1, 9, 3, 'Template saved successfully')
    return True
    
def copy():
    ## copy the selected files and reload them as templates in the schema
    makeTemplate(copy=True)
    
def saveDocument():
    log.log(1, 9, 3, 'Saving Document')
    #return
    if _schemaName == "":
        return saveDocumentAs()
    else:
        return save(None,False)
def save(filename = None, template = False, copy = False):
    global _schemaName
    global schemaPath
    log.log(1, 9, 3, '%s' % filename)
    if filename == None and not copy:
        filename = os.path.join(schemaPath, _schemaName)
    elif copy:
        filename = os.path.join(redREnviron.directoryNames['tempDir'], 'copy.rrts')
    log.log(1, 9, 3, 'Saveing file as name %s' % filename)
    progressBar = startProgressBar(
    'Saving '+str(os.path.basename(filename)),
    'Saving '+str(os.path.basename(filename)),
    len(redRObjects.instances())+len(redRObjects.lines())+3)
    progress = 0

    # create xml document
    (doc, schema, header, widgets, lines, settings, required, tabs, saveTagsList, saveDescription) = makeXMLDoc()
    requiredRLibraries = {}
    
    
    #save widgets
    tempWidgets = redRObjects.instances(wantType = 'dict') ## all of the widget instances, these are not the widget icons
    (widgets, settingsDict, requireRedRLibraries) = saveInstances(tempWidgets, widgets, doc, progressBar)
    
    
    # save tabs and the icons and the channels
    if not copy or template:
        #tabs.setAttribute('tabNames', str(self.canvasTabs.keys()))
        for t in redRObjects.tabNames():
            temp = doc.createElement('tab')
            temp.setAttribute('name', t)
            ## set all of the widget icons on the tab
            widgetIcons = doc.createElement('widgetIcons')
            for wi in redRObjects.getIconsByTab(t)[t]:  ## extract only the list for this tab thus the [t] syntax
                saveIcon(widgetIcons, wi, doc)
            # tabLines = doc.createElement('tabLines')
            # for line in self.widgetLines(t)[t]:
                # saveLine(tabLines, line)
                
            temp.appendChild(widgetIcons)       ## append the widgetIcons XML to the global XML
            #temp.appendChild(tabLines)          ## append the tabLines XML to the global XML
            tabs.appendChild(temp)
    
    
    ## save the global settings ##
    settingsDict['_globalData'] = cPickle.dumps(globalData.globalData,2)
    settingsDict['_requiredPackages'] =  cPickle.dumps({'R': requiredRLibraries.keys(),'RedR': requireRedRLibraries},2)
    #print requireRedRLibraries
    file = open(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'), "wt")
    file.write(str(settingsDict))
    file.close()
    if template:
        taglist = str(tempDialog.tagsList.text())
        tempDescription = str(tempDialog.descriptionEdit.toPlainText())
        saveTagsList.setAttribute("tagsList", taglist)
        saveDescription.setAttribute("tempDescription", tempDescription)
        
    xmlText = doc.toprettyxml()
    progress += 1
    progressBar.setValue(progress)

    if not template and not copy:
        tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
        tempR = os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/')
        file = open(tempschema, "wt")
        file.write(xmlText)
        file.close()
        doc.unlink()
        
        progressBar.setLabelText('Saving Data...')
        progress += 1
        progressBar.setValue(progress)

        RSession.Rcommand('save.image("' + tempR + '")')  # save the R data
        
        createZipFile(filename,[],[redREnviron.directoryNames['tempDir']])# collect the files that are in the tempDir and save them into the zip file.
    elif template:
        tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
        file = open(tempschema, "wt")
        file.write(xmlText)
        file.close()
        zout = zipfile.ZipFile(filename, "w")
        zout.write(tempschema,"tempSchema.tmp")
        zout.write(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'),'settings.pickle')
        zout.close()
        doc.unlink()
    elif copy:
        tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
        file = open(tempschema, "wt")
        file.write(xmlText)
        file.close()
        zout = zipfile.ZipFile(filename, "w")
        zout.write(tempschema,"tempSchema.tmp")
        zout.write(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'),'settings.pickle')
        zout.close()
        doc.unlink()
        loadTemplate(filename)
        
    
    if os.path.splitext(filename)[1].lower() == ".rrs":
        (schemaPath, schemaName) = os.path.split(filename)
        redREnviron.settings["saveSchemaDir"] = schemaPath
        canvasDlg.addToRecentMenu(filename)
        canvasDlg.setCaption(schemaName)
    progress += 1
    progressBar.setValue(progress)
    progressBar.close()
    log.log(1, 9, 3, 'Document Saved Successfully')
    return True
# load a scheme with name "filename"

####################
####   loading #####
####################
def loadRequiredPackages(required, loadingProgressBar):
    try:  # protect the required functions in a try statement, we want to load these things and they should be there but we can't force it to exist in older schemas, so this is in a try.
        required = cPickle.loads(required)
        if len(required) > 0:
            if 'CRANrepos' in redREnviron.settings.keys():
                repo = redREnviron.settings['CRANrepos']
            else:
                repo = None
            loadingProgressBar.setLabelText('Loading required R Packages. If not found they will be downloaded.\n This may take a while...')
            RSession.require_librarys(required['R'], repository=repo)
        
        installedPackages = redRPackageManager.packageManager.getInstalledPackages()
        downloadList = {}
        print type(required['RedR'])
        #print required['RedR']
        
        for name,package in required['RedR'].items():
            #print package
            if not (package['Name'] in installedPackages.keys() 
            and package['Version']['Number'] == installedPackages[package['Name']]['Version']['Number']):
                downloadList[package['Name']] = {'Version':str(package['Version']['Number']), 'installed':False}

        if len(downloadList.keys()) > 0:
            pm = redRPackageManager.packageManagerDialog()
            pm.show()
            pm.askToInstall(downloadList, 'The following packages need to be installed before the session can be loaded.')
    except Exception as inst: 
        log.log(1, 9, 1, 'redRSaveLoad loadRequiredPackages; error loading package %s' % inst)  

def loadTemplate(filename, caption = None, freeze = 0):
    
    loadDocument(filename = filename, caption = caption, freeze = freeze)

def loadDocument(filename, caption = None, freeze = 0, importing = 0):
    global _schemaName
    
    import redREnviron
    if filename.split('.')[-1] in ['rrts']:
        tmp=True
    elif filename.split('.')[-1] in ['rrs']:
        tmp=False
    else:
        QMessageBox.information(None, 'Red-R Error', 
        'Cannot load file with extension ' + str(filename.split('.')[-1]),  
        QMessageBox.Ok + QMessageBox.Default)
        return
    
    loadingProgressBar = startProgressBar('Loading '+str(os.path.basename(filename)),
    'Loading '+str(filename), 2)
    
        
    # set cursor
    qApp.setOverrideCursor(Qt.WaitCursor)
    
    if os.path.splitext(filename)[1].lower() == ".rrs":
        schemaPath, _schemaName = os.path.split(filename)
        canvasDlg.setCaption(caption or _schemaName)
    if importing: # a normal load of the session
        _schemaName = ""

    loadingProgressBar.setLabelText('Loading Schema Data, please wait')

    ### unzip the file ###
    
    zfile = zipfile.ZipFile( str(filename), "r" )
    for name in zfile.namelist():
        file(os.path.join(redREnviron.directoryNames['tempDir'],os.path.basename(name)), 'wb').write(zfile.read(name)) ## put the data into the tempdir for this session for each file that was in the temp dir for the last schema when saved.
    doc = parse(os.path.join(redREnviron.directoryNames['tempDir'],'tempSchema.tmp')) # load the doc data for the data in the temp dir.

    ## get info from the schema
    schema = doc.firstChild
    try:
        
        version = schema.getElementsByTagName("header")[0].getAttribute('version')
        if not version:
            ## we should move everything to the earlier versions of orngDoc for loading.
            loadDocument180(filename, caption = None, freeze = 0, importing = 0)
            loadingProgressBar.hide()
            loadingProgressBar.close()
            return
        else:
            print 'The version is:', version
    except:
        loadDocument180(filename, caption = None, freeze = 0, importing = 0)
        loadingProgressBar.hide()
        loadingProgressBar.close()
        return
    widgets = schema.getElementsByTagName("widgets")[0]
    tabs = schema.getElementsByTagName("tabs")[0]
    #settings = schema.getElementsByTagName("settings")
    f = open(os.path.join(redREnviron.directoryNames['tempDir'],'settings.pickle'))
    settingsDict = eval(str(f.read()))
    f.close()
    
    ## load the required packages
    loadRequiredPackages(settingsDict['_requiredPackages'], loadingProgressBar = loadingProgressBar)
    
    ## make sure that there are no duplicate widgets.
    if not tmp:
        ## need to load the r session before we can load the widgets because the signals will beed to check the classes on init.
        if not checkWidgetDuplication(widgets = widgets):
            QMessageBox.information(canvasDlg, 'Schema Loading Failed', 'Duplicated widgets were detected between this schema and the active one.  Loading is not possible.',  QMessageBox.Ok + QMessageBox.Default)
    
            return
        RSession.Rcommand('load("' + os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/') +'")')
    
    loadingProgressBar.setLabelText('Loading Widgets')
    loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
    loadingProgressBar.setValue(0)
    if not tmp:
        globalData.globalData = cPickle.loads(settingsDict['_globalData'])
        (loadedOkW, tempFailureTextW) = loadWidgets(widgets = widgets, loadingProgressBar = loadingProgressBar, loadedSettingsDict = settingsDict, tmp = tmp)
    
    ## LOAD tabs
    #####  move through all of the tabs and load them.
    (loadedOkT, tempFailureTextT) = loadTabs(tabs = tabs, loadingProgressBar = loadingProgressBar, tmp = tmp, loadedSettingsDict = settingsDict)
    if not tmp:
        for widget in redRObjects.instances():
            if widget.widgetID not in settingsDict.keys(): continue
            widget.outputs.setOutputs(cPickle.loads(settingsDict[widget.widgetID]['connections']), tmp)
    else:
        for widget in redRObjects.instances():
            if widget.tempID and widget.tempID in settingsDict.keys():
                widget.outputs.setOutputs(cPickle.loads(settingsDict[widget.tempID]['connections']), tmp)
    for widget in redRObjects.instances():
        widget.tempID = None  ## we set the temp ID to none so that there won't be a conflict with other temp loading.
    qApp.restoreOverrideCursor() 
    qApp.restoreOverrideCursor()
    qApp.restoreOverrideCursor()
    loadingProgressBar.hide()
    loadingProgressBar.close()
def loadDocument180(filename, caption = None, freeze = 0, importing = 0):
    import redREnviron
    if filename.split('.')[-1] in ['rrts']:
        tmp=True
    elif filename.split('.')[-1] in ['rrs']:
        tmp=False
    else:
        QMessageBox.information(self, 'Red-R Error', 
        'Cannot load file with extension ' + str(filename.split('.')[-1]),  
        QMessageBox.Ok + QMessageBox.Default)
        return
    
    loadingProgressBar = startProgressBar('Loading '+str(os.path.basename(filename)),
    'Loading '+str(filename), 2)
    
    ## What is the purpose of this???
    if not os.path.exists(filename):
        if os.path.splitext(filename)[1].lower() != ".tmp":
            QMessageBox.critical(self, 'Red-R Canvas', 
            'Unable to locate file "'+ filename + '"',  QMessageBox.Ok)
        return
        loadingProgressBar.hide()
        loadingProgressBar.close()
    ###
        
    # set cursor
    qApp.setOverrideCursor(Qt.WaitCursor)
    
    if os.path.splitext(filename)[1].lower() == ".rrs":
        schemaPath, _schemaName = os.path.split(filename)
        canvasDlg.setCaption(caption or _schemaName)
    if importing: # a normal load of the session
        _schemaName = ""

    loadingProgressBar.setLabelText('Loading Schema Data, please wait')

    ### unzip the file ###
    
    zfile = zipfile.ZipFile( str(filename), "r" )
    for name in zfile.namelist():
        file(os.path.join(redREnviron.directoryNames['tempDir'],os.path.basename(name)), 'wb').write(zfile.read(name)) ## put the data into the tempdir for this session for each file that was in the temp dir for the last schema when saved.
    doc = parse(os.path.join(redREnviron.directoryNames['tempDir'],'tempSchema.tmp')) # load the doc data for the data in the temp dir.

    ## get info from the schema
    schema = doc.firstChild
    widgets = schema.getElementsByTagName("widgets")[0]
    lines = schema.getElementsByTagName('channels')[0]
    f = open(os.path.join(redREnviron.directoryNames['tempDir'],'settings.pickle'))
    settingsDict = eval(str(f.read()))
    f.close()
    
    #settingsDict = eval(str(settings[0].getAttribute("settingsDictionary")))
    loadedSettingsDict = settingsDict
    
    loadRequiredPackages(settingsDict['_requiredPackages'], loadingProgressBar = loadingProgressBar)
    
    ## make sure that there are no duplicate widgets.
    if not tmp:
        ## need to load the r session before we can load the widgets because the signals will beed to check the classes on init.
        if not checkWidgetDuplication(widgets = widgets):
            QMessageBox.information(self, 'Schema Loading Failed', 'Duplicated widgets were detected between this schema and the active one.  Loading is not possible.',  QMessageBox.Ok + QMessageBox.Default)
    
            return
        RSession.Rcommand('load("' + os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/') +'")')
    
    loadingProgressBar.setLabelText('Loading Widgets')
    loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
    loadingProgressBar.setValue(0)
    globalData.globalData = cPickle.loads(loadedSettingsDict['_globalData'])
    (loadedOkW, tempFailureTextW) = loadWidgets180(widgets = widgets, loadingProgressBar = loadingProgressBar, tmp = tmp)
    
    lineList = lines.getElementsByTagName("channel")
    loadingProgressBar.setLabelText('Loading Lines')
    (loadedOkL, tempFailureTextL) = loadLines(lineList, loadingProgressBar = loadingProgressBar, 
    freeze = freeze, tmp = tmp)

    for widget in redRObjects.instances(): widget.updateTooltip()
    activeCanvas().update()
    #saveTempDoc()
    
    if not loadedOkW and loadedOkL:
        failureText = tempFailureTextW + tempFailureTextL
        QMessageBox.information(canvasDlg, 'Schema Loading Failed', 'The following errors occured while loading the schema: <br><br>' + failureText,  QMessageBox.Ok + QMessageBox.Default)
    
    for widget in redRObjects.instances():
        widget.instance().setLoadingSavedSession(False)
    qApp.restoreOverrideCursor() 
    qApp.restoreOverrideCursor()
    qApp.restoreOverrideCursor()
    loadingProgressBar.hide()
    loadingProgressBar.close()
    

def loadTabs(tabs, loadingProgressBar, tmp, loadedSettingsDict = None):
    # load the tabs
    
    loadedOK = True
    for t in tabs.getElementsByTagName('tab'):
        if not tmp:
            log.log(1, 5, 3, 'Loading tab %s' % t)
            schemaDoc.makeSchemaTab(t.getAttribute('name'))
            schemaDoc.setTabActive(t.getAttribute('name'))
        addY = minimumY()
        for witemp in t.getElementsByTagName('widgetIcons')[0].getElementsByTagName('widgetIcon'):
            name = witemp.getAttribute('name')             # save icon name
            instance = witemp.getAttribute('instance')        # save instance ID
            
            xPos = int(witemp.getAttribute("xPos"))      # save the xPos
            yPos = int(witemp.getAttribute("yPos"))      # same the yPos
            if not tmp:
                caption = witemp.getAttribute("caption")          # save the caption
                log.log(1, 5, 3, 'loading widgeticon %s, %s, %s' % (name, instance, caption))
                schemaDoc.addWidgetIconByFileName(name, x = xPos, y = yPos + addY, caption = caption, instance = str(instance)) ##  add the widget icon 
            else:
                caption = ""
                settings = cPickle.loads(loadedSettingsDict[instance]['settings'])
            
                import time
                loadingInstanceID = str(time.time())
                newwidget = schemaDoc.addWidgetByFileName(name, x = xPos, y = yPos + addY, widgetSettings = settings, id = loadingInstanceID)
                nw = redRObjects.getWidgetInstanceByID(newwidget)
                ## if tmp we need to set the tempID
                nw.tempID = instance
                nw.widgetID = loadingInstanceID
                nw.variable_suffix = '_' + loadingInstanceID
                nw.resetRvariableNames()
                ## send None through all of the widget ouptuts if this is a template
                nw.outputs.propogateNone()
        
    return (True, '')

def loadWidgets(widgets, loadingProgressBar, loadedSettingsDict, tmp):
        
    lpb = 0
    loadedOk = 1
    failureText = ''
    for widget in widgets.getElementsByTagName("widget"):
        try:
            name = widget.getAttribute("widgetName")
            #print name
            widgetID = widget.getAttribute('widgetID')
            #print widgetID
            settings = cPickle.loads(loadedSettingsDict[widgetID]['settings'])
            inputs = cPickle.loads(loadedSettingsDict[widgetID]['inputs'])
            outputs = cPickle.loads(loadedSettingsDict[widgetID]['outputs'])
            #print 'adding instance', widgetID, inputs, outputs
            newwidget = addWidgetInstanceByFileName(name, settings, inputs, outputs)
            if newwidget and tmp:
                import time
                nw = redRObjects.getWidgetInstanceByID(newwidget)
                ## if tmp we need to set the tempID
                nw.tempID = widgetID
                nw.widgetID = str(time.time())
                nw.variable_suffix = '_' + widgetID
                nw.resetRvariableNames()
                ## send None through all of the widget ouptuts if this is a template
                nw.outputs.propogateNone()
            
            #print 'Settings', settings
            lpb += 1
            loadingProgressBar.setValue(lpb)
        except Exception as inst:
            log.log(1, 9, 1, str(inst))
    ## now the widgets are loaded so we can move on to setting the connections
    
    return (loadedOk, failureText)
def addWidgetInstanceByFileName(name, settings = None, inputs = None, outputs = None):
    widget = redRObjects.widgetRegistry()['widgets'][name]
    return redRObjects.addInstance(signalManager, widget, settings, inputs, outputs)
    
        
def loadWidgets180(widgets, loadingProgressBar, tmp):
    lpb = 0
    loadedOk = 1
    failureText = ''
    addY = minimumY()
    for widget in widgets.getElementsByTagName("widget"):
        try:
            name = widget.getAttribute("widgetName")

            widgetID = widget.getAttribute('widgetID')
            settings = cPickle.loads(loadedSettingsDict[widgetID]['settings'])
            inputs = cPickle.loads(loadedSettingsDict[widgetID]['inputs'])
            outputs = cPickle.loads(loadedSettingsDict[widgetID]['outputs'])
            xPos = int(widget.getAttribute('xPos'))
            yPos = int(widget.getAttribute('yPos'))
            caption = str(widget.getAttribute('caption'))
            ## for backward compatibility we need to make both the widgets and the instances.
            #addWidgetInstanceByFileName(name, settings, inputs, outputs)
            widgetInfo =  redRObjects.widgetRegistry()['widgets'][name]
            addWidget(widgetInfo, x= xPos, y= yPos, caption = caption, widgetSettings = settings, forceInSignals = inputs, forceOutSignals = outputs)
            #print 'Settings', settings
            lpb += 1
            loadingProgressBar.setValue(lpb)
        except Exception as inst:
            print str(inst), 'Widget load failure 180'
    return (loadedOk, failureText)
def getXMLText(nodelist):
    rc = ''
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc
#####################
### zip files ###
#####################
def addFolderToZip(myZipFile,folder):
    import glob
    folder = folder.encode('ascii') #convert path to ascii for ZipFile Method
    for file in glob.glob(folder+"/*"):
            if os.path.isfile(file):
                
                myZipFile.write(file, os.path.basename(file), zipfile.ZIP_DEFLATED)
            elif os.path.isdir(file):
                addFolderToZip(myZipFile,file)

def createZipFile(zipFilename,files,folders):
    
    myZipFile = zipfile.ZipFile(zipFilename, "w" ) # Open the zip file for writing 
    for file in files:
        file = file.encode('ascii') #convert path to ascii for ZipFile Method
        if os.path.isfile(file):
            (filepath, filename) = os.path.split(file)
            myZipFile.write( file, filename, zipfile.ZIP_DEFLATED )

    for folder in  folders:   
        addFolderToZip(myZipFile,folder)  
    myZipFile.close()
    return (1,zipFilename)
    
def toZip(file, filename):
    zip_file = zipfile.ZipFile(filename, 'w')
    if os.path.isfile(file):
        zip_file.write(file)
    else:
        addFolderToZip(zip_file, file)
    zip_file.close()
    
def saveDocumentAs():
    name = QFileDialog.getSaveFileName(None, "Save File", os.path.join(schemaPath, _schemaName), "Red-R Widget Schema (*.rrs)")
    if not name or name == None: return False
    name = str(name.toAscii())
    if str(name) == '': return False
    if os.path.splitext(str(name))[0] == "": return False
    if os.path.splitext(str(name))[1].lower() != ".rrs": name = name + ".rrs"
    log.log(1, 9, 3, 'saveDocument: name is %s' % name)
    return save(name,template=False)
def checkWidgetDuplication(widgets):
    for widget in widgets.getElementsByTagName("widget"):
        #widgetIDisNew = self.checkID(widget.getAttribute('widgetID'))
        if widget.getAttribute('widgetID') in redRObjects.instances(wantType = 'dict').keys():
            qApp.restoreOverrideCursor()
            QMessageBox.critical(canvasDlg, 'Red-R Canvas', 
            'Widget ID is a duplicate, I can\'t load this!!!',  QMessageBox.Ok)
            return False
    return True
def saveTemplate():
    name = QFileDialog.getSaveFileName(None, "Save Template", redREnviron.directoryNames['templatesDir'], "Red-R Widget Template (*.rrts)")
    if not name or name == None: return False
    name = str(name.toAscii())
    if str(name) == '': return False
    if os.path.splitext(str(name))[0] == '': return False
    if os.path.splitext(str(name))[1].lower() != ".rrts": name = name + '.rrts'
    return makeTemplate(str(name),copy=False)

def makeXMLDoc():
    doc = Document() ## generates the main document type.
    schema = doc.createElement("schema")
    header = doc.createElement('header')
    # make the header
    header.setAttribute('version', redREnviron.version['REDRVERSION'])
    widgets = doc.createElement("widgets")  # holds the widget instances
    lines = doc.createElement("channels")  # holds the lines
    settings = doc.createElement("settings")  
    required = doc.createElement("required")  # holds the required elements
    tabs = doc.createElement("tabs") # the tab names are saved here.
    saveTagsList = doc.createElement("TagsList")
    saveDescription = doc.createElement("saveDescription")
    doc.appendChild(schema)
    schema.appendChild(widgets)
    #schema.appendChild(lines)
    schema.appendChild(settings)
    schema.appendChild(required)
    schema.appendChild(saveTagsList)
    schema.appendChild(saveDescription)
    schema.appendChild(tabs)
    schema.appendChild(header)
    return (doc, schema, header, widgets, lines, settings, required, tabs, saveTagsList, saveDescription)
def startProgressBar(title,text,max):
    progressBar = QProgressDialog()
    progressBar.setCancelButtonText(QString())
    progressBar.setWindowTitle(title)
    progressBar.setLabelText(text)
    progressBar.setMaximum(max)
    progressBar.setValue(0)
    progressBar.show()
    return progressBar

    
class TemplateDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        
        self.setWindowTitle('Save as template')
        
        self.setLayout(QVBoxLayout())
        layout = self.layout()
        
        mainWidgetBox = QWidget(self)
        mainWidgetBox.setLayout(QVBoxLayout())
        layout.addWidget(mainWidgetBox)
        
        mainWidgetBox.layout().addWidget(QLabel('Set tags as comma ( , ) delimited list', mainWidgetBox))
        
        
        topWidgetBox = QWidget(mainWidgetBox)
        topWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(topWidgetBox)
        
        topWidgetBox.layout().addWidget(QLabel('Tags:', topWidgetBox))
        self.tagsList = QLineEdit(topWidgetBox)
        topWidgetBox.layout().addWidget(self.tagsList)
        
        bottomWidgetBox = QWidget(mainWidgetBox)
        bottomWidgetBox.setLayout(QVBoxLayout())
        mainWidgetBox.layout().addWidget(bottomWidgetBox)
        
        bottomWidgetBox.layout().addWidget(QLabel('Description:', bottomWidgetBox))
        self.descriptionEdit = QTextEdit(bottomWidgetBox)
        bottomWidgetBox.layout().addWidget(self.descriptionEdit)
        
        buttonWidgetBox = QWidget(mainWidgetBox)
        buttonWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(buttonWidgetBox)
        
        acceptButton = QPushButton('Accept', buttonWidgetBox)
        cancelButton = QPushButton('Cancel', buttonWidgetBox)
        buttonWidgetBox.layout().addWidget(acceptButton)
        buttonWidgetBox.layout().addWidget(cancelButton)
        QObject.connect(acceptButton, SIGNAL("clicked()"), self.accept)
        QObject.connect(cancelButton, SIGNAL("clicked()"), self.reject)