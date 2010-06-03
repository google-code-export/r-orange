# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington and Anup Parikh
# Description:
#    document class - main operations (save, load, ...)
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, os.path, traceback
from xml.dom.minidom import Document, parse
import xml.dom.minidom
import orngView, orngCanvasItems, orngTabs
from orngDlgs import *
import RSession
import globalData
import redRPackageManager

from orngSignalManager import SignalManager
import cPickle, math, orngHistory, zipfile
import pprint, urllib
pp = pprint.PrettyPrinter(indent=4)

class SchemaDoc(QWidget):
    def __init__(self, canvasDlg, *args):
        QWidget.__init__(self, *args)
        self.canvasDlg = canvasDlg
        self.ctrlPressed = 0
        self.version = 'trunk'                  # should be changed before making the installer or when moving to a new branch.
        self.lines = []                         # list of orngCanvasItems.CanvasLine items
        self.widgets = []                       # list of orngCanvasItems.CanvasWidget items
        self.signalManager = SignalManager()    # signal manager to correctly process signals

        self.sessionID = 0
        self.schemaPath = redREnviron.settings["saveSchemaDir"]
        self.schemaName = ""
        self.loadedSettingsDict = {}
        self.setLayout(QVBoxLayout())
        #self.canvas = QGraphicsScene(0,0,2000,2000)
        self.canvas = QGraphicsScene()
        self.canvasView = orngView.SchemaView(self, self.canvas, self)
        self.layout().addWidget(self.canvasView)
        self.layout().setMargin(0)
        self.schemaID = orngHistory.logNewSchema()
        self.RVariableRemoveSupress = 0
        self.urlOpener = urllib.FancyURLopener()
   


    # save a temp document whenever anything changes. this doc is deleted on closeEvent
    # in case that Orange crashes, Canvas on the next start offers an option to reload the crashed schema with links frozen
    def saveTempDoc(self):
        return
        if self.widgets != []:
            tempName = os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "tempSchema.tmp")
            self.save(tempName,True)
        
    def removeTempDoc(self):
        tempName = os.path.join(redREnviron.directoryNames['canvasSettingsDir'], "tempSchema.tmp")
        if os.path.exists(tempName):
            os.remove(tempName)


    def showAllWidgets(self):
        for i in self.widgets:
            i.instance.show()
    def closeAllWidgets(self):
        for i in self.widgets:
            i.instance.close()
            
    # add line connecting widgets outWidget and inWidget
    # if necessary ask which signals to connect
    def addLine(self, outWidget, inWidget, enabled = True):
        if outWidget == inWidget: 
            return None
        # check if line already exists
        line = self.getLine(outWidget, inWidget)
        if line:
            self.resetActiveSignals(outWidget, inWidget, None, enabled)
            return None

        if self.signalManager.existsPath(inWidget.instance, outWidget.instance):
            QMessageBox.critical( self, "Failed to Connect", "Circular connections are not allowed in Orange Canvas.", QMessageBox.Ok)
            return None

        dialog = SignalDialog(self.canvasDlg, None)
        dialog.setOutInWidgets(outWidget, inWidget)
        connectStatus = dialog.addDefaultLinks()
        if connectStatus == 0:
            QMessageBox.information( self, "Failed to Connect", "Selected widgets don't share a common signal type.", QMessageBox.Ok)
            return

        # if there are multiple choices, how to connect this two widget, then show the dialog
        if len(dialog.getLinks()) > 1 or dialog.multiplePossibleConnections or dialog.getLinks() == []:
            if dialog.exec_() == QDialog.Rejected:
                return None

        self.signalManager.setFreeze(1)
        linkCount = 0
        for (outName, inName) in dialog.getLinks():
            linkCount += self.addLink(outWidget, inWidget, outName, inName, enabled)

        self.signalManager.setFreeze(0, outWidget.instance)

        # if signals were set correctly create the line, update widget tooltips and show the line
        line = self.getLine(outWidget, inWidget)
        if line:
            outWidget.updateTooltip()
            inWidget.updateTooltip()
            
        self.saveTempDoc()
        return line


    # reset signals of an already created line
    def resetActiveSignals(self, outWidget, inWidget, newSignals = None, enabled = 1):
        #print "<extra>orngDoc.py - resetActiveSignals() - ", outWidget, inWidget, newSignals
        signals = []
        for line in self.lines:
            if line.outWidget == outWidget and line.inWidget == inWidget:
                signals = line.getSignals()

        if newSignals == None:
            dialog = SignalDialog(self.canvasDlg, None)
            dialog.setOutInWidgets(outWidget, inWidget)
            for (outName, inName) in signals:
                #print "<extra>orngDoc.py - SignalDialog.addLink() - adding signal to dialog: ", outName, inName
                dialog.addLink(outName, inName)

            # if there are multiple choices, how to connect this two widget, then show the dialog
            if dialog.exec_() == QDialog.Rejected:
                return

            newSignals = dialog.getLinks()

        for (outName, inName) in signals:
            if (outName, inName) not in newSignals:
                self.removeLink(outWidget, inWidget, outName, inName)
                signals.remove((outName, inName))

        self.signalManager.setFreeze(1)
        for (outName, inName) in newSignals:
            if (outName, inName) not in signals:
                self.addLink(outWidget, inWidget, outName, inName, enabled)
        self.signalManager.setFreeze(0, outWidget.instance)

        outWidget.updateTooltip()
        inWidget.updateTooltip()



    # add one link (signal) from outWidget to inWidget. if line doesn't exist yet, we create it
    def addLink(self, outWidget, inWidget, outSignalName, inSignalName, enabled = 1, fireSignal = 1):
        #print "<extra>orngDoc - addLink() - ", outWidget, inWidget, outSignalName, inSignalName
        # in case there already exists link to inSignalName in inWidget that is single, we first delete it
        widgetInstance = inWidget.instance.removeExistingSingleLink(inSignalName)
        if widgetInstance:
            widget = self.findWidgetFromInstance(widgetInstance)
            existingSignals = self.signalManager.findSignals(widgetInstance, inWidget.instance)
            for (outN, inN) in existingSignals:
                if inN == inSignalName:
                    self.removeLink(widget, inWidget, outN, inN)
                    line = self.getLine(widget, inWidget)
                    if line:
                        line.updateTooltip()

        # if line does not exist yet, we must create it
        existingSignals = self.signalManager.findSignals(outWidget.instance, inWidget.instance)
        if not existingSignals:
            line = orngCanvasItems.CanvasLine(self.signalManager, self.canvasDlg, self.canvasView, outWidget, inWidget, self.canvas)
            self.lines.append(line)
            line.setEnabled(enabled)
            line.show()
            outWidget.addOutLine(line)
            outWidget.updateTooltip()
            inWidget.addInLine(line)
            inWidget.updateTooltip()
        else:
            line = self.getLine(outWidget, inWidget)

        ok = self.signalManager.addLink(outWidget.instance, inWidget.instance, outSignalName, inSignalName, enabled)
        if not ok:
            self.removeLink(outWidget, inWidget, outSignalName, inSignalName)
            QMessageBox.information( self, "Orange Canvas", "Unable to add link. Something is really wrong; try restarting Orange Canvas.", QMessageBox.Ok + QMessageBox.Default )
            

            return 0
        else:
            orngHistory.logAddLink(self.schemaID, outWidget, inWidget, outSignalName)

        line.updateTooltip()
        return 1


    # remove only one signal from connected two widgets. If no signals are left, delete the line
    def removeLink(self, outWidget, inWidget, outSignalName, inSignalName):
        #print "<extra> orngDoc.py - removeLink() - ", outWidget, inWidget, outSignalName, inSignalName
        self.signalManager.removeLink(outWidget.instance, inWidget.instance, outSignalName, inSignalName)

        otherSignals = 0
        if self.signalManager.links.has_key(outWidget.instance):
            for (widget, signalFrom, signalTo, enabled) in self.signalManager.links[outWidget.instance]:
                    if widget == inWidget.instance:
                        otherSignals = 1
        if not otherSignals:
            self.removeLine(outWidget, inWidget)

        self.saveTempDoc()


    # remove line line
    def removeLine1(self, line):
        #print 'removing a line from' + str(outName) +'to' +str(inName)
        for (outName, inName) in line.getSignals():
            self.signalManager.removeLink(line.outWidget.instance, line.inWidget.instance, outName, inName)   # update SignalManager

        self.lines.remove(line)
        line.inWidget.removeLine(line)
        line.outWidget.removeLine(line)
        line.inWidget.updateTooltip()
        line.outWidget.updateTooltip()
        line.remove()
        self.saveTempDoc()

    # remove line, connecting two widgets
    def removeLine(self, outWidget, inWidget):
        #print "<extra> orngDoc.py - removeLine() - ", outWidget, inWidget
        line = self.getLine(outWidget, inWidget)
        if line:
            self.removeLine1(line)

    # add new widget
    def addWidget(self, widgetInfo, x= -1, y=-1, caption = "", widgetSettings = None, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        qApp.setOverrideCursor(Qt.WaitCursor)
        try:
            print str(forceInSignals) 
            print str(forceOutSignals)
            #print 'adding widget '+caption
            if widgetInfo.name == 'Dummy': print 'Loading dummy step 2'
            newwidget = orngCanvasItems.CanvasWidget(self.signalManager, self.canvas, self.canvasView, widgetInfo, self.canvasDlg.defaultPic, self.canvasDlg, widgetSettings, forceInSignals = forceInSignals, forceOutSignals = forceOutSignals)
            #if widgetInfo.name == 'dummy' and (forceInSignals or forceOutSignals):
        except:
            type, val, traceback = sys.exc_info()
            print str(traceback)
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas
            qApp.restoreOverrideCursor()
            return None

        if x==-1 or y==-1:
            if self.widgets != []:
                x = self.widgets[-1].x() + 110
                y = self.widgets[-1].y()
            else:
                x = 30
                y = 50
        newwidget.setCoords(x, y)
        # move the widget to a valid position if necessary
        invalidPosition = (self.canvasView.findItemTypeCount(self.canvas.collidingItems(newwidget), orngCanvasItems.CanvasWidget) > 0)
        if invalidPosition:
            for r in range(20, 200, 20):
                for fi in [90, -90, 180, 0, 45, -45, 135, -135]:
                    xOff = r * math.cos(math.radians(fi))
                    yOff = r * math.sin(math.radians(fi))
                    rect = QRectF(x+xOff, y+yOff, 48, 48)
                    invalidPosition = self.canvasView.findItemTypeCount(self.canvas.items(rect), orngCanvasItems.CanvasWidget) > 0
                    if not invalidPosition:
                        newwidget.setCoords(x+xOff, y+yOff)
                        break
                if not invalidPosition:
                    break
            
        #self.canvasView.ensureVisible(newwidget)

        if caption == "": caption = newwidget.caption

        if self.getWidgetByCaption(caption):
            i = 2
            while self.getWidgetByCaption(caption + " (" + str(i) + ")"): i+=1
            caption = caption + " (" + str(i) + ")"
        newwidget.updateText(caption)
        newwidget.instance.setWindowTitle(caption)
        

        self.widgets.append(newwidget)
        if saveTempDoc:
            self.saveTempDoc()
        self.canvas.update()

        # show the widget and activate the settings
        try:
            self.signalManager.addWidget(newwidget.instance)
            newwidget.show()
            newwidget.updateTooltip()
            newwidget.setProcessing(1)
            # if redREnviron.settings["saveWidgetsPosition"]:
                # newwidget.instance.restoreWidgetPosition()
            newwidget.setProcessing(0)
            orngHistory.logAddWidget(self.schemaID, id(newwidget), (newwidget.widgetInfo.packageName, newwidget.widgetInfo.name), newwidget.x(), newwidget.y())
        except:
            type, val, traceback = sys.exc_info()
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas

        qApp.restoreOverrideCursor()
        return newwidget

    # remove widget
    def removeWidget(self, widget, saveTempDoc = True):
        if not widget:
            return
        #widget.closing = close
        while widget.inLines != []: self.removeLine1(widget.inLines[0])
        while widget.outLines != []:  self.removeLine1(widget.outLines[0])

        self.signalManager.removeWidget(widget.instance) # sending occurs before this point
        widget.remove()
        self.widgets.remove(widget)
        
        # import gc
        # gc.collect()
        # print 'Remaining references to '+str(gc.get_referrers(widget))
        # print 'Remaining references from '+str(gc.get_referents(widget))
        #orngHistory.logRemoveWidget(self.schemaID, id(widget), (widget.widgetInfo.packageName, widget.widgetInfo.name))

    def clear(self):
        print '|#| orngDoc clear'
        self.canvasDlg.setCaption()
        for widget in self.widgets[::-1]:   
            self.removeWidget(widget, saveTempDoc = False)   # remove widgets from last to first
        RSession.Rcommand('rm(list = ls())')
        self.canvas.update()
        self.saveTempDoc()
        

    def enableAllLines(self):
        for line in self.lines:
            self.signalManager.setLinkEnabled(line.outWidget.instance, line.inWidget.instance, 1)
            line.setEnabled(1)
            #line.repaintLine(self.canvasView)
        self.canvas.update()

    def disableAllLines(self):
        for line in self.lines:
            self.signalManager.setLinkEnabled(line.outWidget.instance, line.inWidget.instance, 0)
            line.setEnabled(0)
            #line.repaintLine(self.canvasView)
        self.canvas.update()

    # return a new widget instance of a widget with filename "widgetName"
    def addWidgetByFileName(self, widgetFileName, x, y, caption, widgetSettings=None, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        try:
            if widgetFileName == 'base_dummy': print 'Loading dummy step 1a'
            widget = self.canvasDlg.widgetRegistry['widgets'][widgetFileName]
            return self.addWidget(widget, x, y, caption, widgetSettings, saveTempDoc, forceInSignals, forceOutSignals)
        except Exception as inst:
            print '|###| Loading exception occured for widget '+widgetFileName
            print str(inst)
            return None

    # return the widget instance that has caption "widgetName"
    def getWidgetByCaption(self, widgetName):
        for widget in self.widgets:
            if (widget.caption == widgetName):
                return widget
        return None

    def getWidgetByID(self, widgetID):
        for widget in self.widgets:
            if (widget.instance.widgetID == widgetID):
                return widget
        return None
        
    def getWidgetCaption(self, widgetInstance):
        for widget in self.widgets:
            if widget.instance == widgetInstance:
                return widget.caption
        print "Error. Invalid widget instance : ", widgetInstance
        return ""


    # get line from outWidget to inWidget
    def getLine(self, outWidget, inWidget):
        for line in self.lines:
            if line.outWidget == outWidget and line.inWidget == inWidget:
                return line
        return None


    # find orngCanvasItems.CanvasWidget from widget instance
    def findWidgetFromInstance(self, widgetInstance):
        for widget in self.widgets:
            if widget.instance == widgetInstance:
                return widget
        return None

    # ###########################################
    # SAVING, LOADING, ....
    # ###########################################
    def minimumY(self):
        ## calculate the miinimum Y position on the canvas.  
        ## When loading new widgets will be adjusted down by this amount.
        y = 0
        for widget in self.widgets:
            if widget.y() > y:
                y = widget.y()
                
        if y != 0:
            y += 30 # gives a little more space for the widgets.
        return y
    def saveDocument(self):
        print 'saveDocument'
        #return
        if self.schemaName == "":
            return self.saveDocumentAs()
        else:
            return self.save(None,False)

    def saveDocumentAs(self):
        print 'saveDocumentAs'
        
        name = QFileDialog.getSaveFileName(self, "Save File", os.path.join(self.schemaPath, self.schemaName), "Red-R Widget Schema (*.rrs)")
        if not name or name == None: return False
        if str(name) == '': return False
        if os.path.splitext(str(name))[0] == "": return False
        if os.path.splitext(str(name))[1].lower() != ".rrs": name = name + ".rrs"
        return self.save(str(name),template=False)
        
    def saveTemplate(self):
        name = QFileDialog.getSaveFileName(self, "Save Template", redREnviron.directoryNames['templatesDir'], "Red-R Widget Template (*.rrts)")
        if not name or name == None: return False
        if str(name) == '': return False
        if os.path.splitext(str(name))[0] == '': return False
        if os.path.splitext(str(name))[1].lower() != ".rrts": name = name + '.rrts'
        return self.save(str(name),template=True)
  
    def toZip(self, file, filename):
        zip_file = zipfile.ZipFile(filename, 'w')
        if os.path.isfile(file):
            zip_file.write(file)
        else:
            self.addFolderToZip(zip_file, file)
        zip_file.close()

    def addFolderToZip(self, zip_file, folder): 
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                print 'File added: ' + str(full_path)
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                print 'Entering folder: ' + str(full_path)
                self.addFolderToZip(zip_file, full_path)  
    def addFolderToZip(self,myZipFile,folder):
        import glob
        folder = folder.encode('ascii') #convert path to ascii for ZipFile Method
        for file in glob.glob(folder+"/*"):
                if os.path.isfile(file):
                    print file
                    myZipFile.write(file, os.path.basename(file), zipfile.ZIP_DEFLATED)
                elif os.path.isdir(file):
                    addFolderToZip(myZipFile,file)

    def createZipFile(self,zipFilename,files,folders):
        
        myZipFile = zipfile.ZipFile( zipFilename, "w" ) # Open the zip file for writing 
        for file in files:
            file = file.encode('ascii') #convert path to ascii for ZipFile Method
            if os.path.isfile(file):
                (filepath, filename) = os.path.split(file)
                myZipFile.write( file, filename, zipfile.ZIP_DEFLATED )

        for folder in  folders:   
            self.addFolderToZip(myZipFile,folder)  
        myZipFile.close()
        return (1,zipFilename)
        
    # save the file
    def save(self, filename = None,template = False):

        if template:
            tempDialog = TemplateDialog(self)
            if tempDialog.exec_() == QDialog.Rejected:
                return
        print '|#| start save schema'
        if filename == None:
            filename = os.path.join(self.schemaPath, self.schemaName)
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        progressBar = self.startProgressBar(
        'Saving '+str(os.path.basename(filename)),
        'Saving '+str(os.path.basename(filename)),
        len(self.widgets)+len(self.lines)+3)
        progress = 0

        # create xml document
        doc = Document()
        schema = doc.createElement("schema")
        widgets = doc.createElement("widgets")
        lines = doc.createElement("channels")
        settings = doc.createElement("settings")
        required = doc.createElement("required")
        saveTagsList = doc.createElement("TagsList")
        saveDescription = doc.createElement("saveDescription")
        doc.appendChild(schema)
        schema.appendChild(widgets)
        schema.appendChild(lines)
        schema.appendChild(settings)
        schema.appendChild(required)
        schema.appendChild(saveTagsList)
        schema.appendChild(saveDescription)
        
        requiredRLibraries = {}
        requireRedRLibraries = {}
        settingsDict = {}
        #save widgets
        for widget in self.widgets:
            temp = doc.createElement("widget")
            temp.setAttribute("xPos", str(int(widget.x())) )
            temp.setAttribute("yPos", str(int(widget.y())) )
            temp.setAttribute("caption", widget.caption)
            
            temp.setAttribute("widgetName", widget.widgetInfo.fileName)
            temp.setAttribute("widgetFileName", os.path.basename(widget.widgetInfo.fullName))
            temp.setAttribute('widgetID', widget.instance.widgetID)
            print 'save in orngDoc ' + str(widget.caption)
            progress += 1
            progressBar.setValue(progress)
            
            s = widget.instance.getSettings()
            i = widget.instance.getInputs()
            o = widget.instance.getOutputs()
            
            #map(requiredRLibraries.__setitem__, s['requiredRLibraries']['pythonObject'], []) 
            #requiredRLibraries.extend()
            #del s['requiredRLibraries']
            settingsDict[widget.instance.widgetID] = {}
            settingsDict[widget.instance.widgetID]['settings'] = cPickle.dumps(s,2)
            settingsDict[widget.instance.widgetID]['inputs'] = cPickle.dumps(i,2)
            settingsDict[widget.instance.widgetID]['outputs'] = cPickle.dumps(o,2)
            
            if widget.widgetInfo.package['Name'] != 'base' and widget.widgetInfo.package['Name'] not in requireRedRLibraries.keys():
                requireRedRLibraries[widget.widgetInfo.package['Name']] = widget.widgetInfo.package
        
            widgets.appendChild(temp)
        
        settingsDict['_globalData'] = cPickle.dumps(globalData.globalData,2)
        settingsDict['_requiredPackages'] =  cPickle.dumps({'R': requiredRLibraries.keys(),'RedR': requireRedRLibraries},2)
        print requireRedRLibraries
        file = open(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'), "wt")
        file.write(str(settingsDict))
        file.close()

        #settings.setAttribute("settingsDictionary", str(settingsDict))
        #required.setAttribute("requiredPackages", str({'r':r}))
        
        #save connections
        for line in self.lines:
            temp = doc.createElement("channel")
            temp.setAttribute("outWidgetCaption", line.outWidget.caption)
            temp.setAttribute('outWidgetIndex', line.outWidget.instance.widgetID)
            temp.setAttribute("inWidgetCaption", line.inWidget.caption)
            temp.setAttribute('inWidgetIndex', line.inWidget.instance.widgetID)
            temp.setAttribute("enabled", str(line.getEnabled()))
            temp.setAttribute("signals", str(line.getSignals()))
            lines.appendChild(temp)

        if template:
            taglist = str(tempDialog.tagsList.text())
            tempDescription = str(tempDialog.descriptionEdit.toHtml())
            saveTagsList.setAttribute("tagsList", taglist)
            saveDescription.setAttribute("tempDescription", tempDescription)
            print taglist, tempDescription
        xmlText = doc.toprettyxml()
        progress += 1
        progressBar.setValue(progress)

        if not template:
            tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
            tempR = os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/')
            file = open(tempschema, "wt")
            file.write(xmlText)
            file.close()
            doc.unlink()
            print 'saving image...'
            progressBar.setLabelText('Saving Data...')
            progress += 1
            progressBar.setValue(progress)

            RSession.Rcommand('save.image("' + tempR + '")')  # save the R data
            print 'image saved.'
            self.createZipFile(filename,[],[redREnviron.directoryNames['tempDir']])# collect the files that are in the tempDir and save them into the zip file.
        else :
            tempschema = os.path.join(redREnviron.directoryNames['tempDir'], "tempSchema.tmp")
            file = open(tempschema, "wt")
            file.write(xmlText)
            file.close()
            zout = zipfile.ZipFile(filename, "w")
            zout.write(tempschema,"tempSchema.tmp")
            zout.write(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'),'settings.pickle')
            zout.close()
            doc.unlink()
            
        
        if os.path.splitext(filename)[1].lower() == ".rrs":
            (self.schemaPath, self.schemaName) = os.path.split(filename)
            redREnviron.settings["saveSchemaDir"] = self.schemaPath
            self.canvasDlg.addToRecentMenu(filename)
            self.canvasDlg.setCaption(self.schemaName)
        progress += 1
        progressBar.setValue(progress)
        progressBar.close()

        return True
    # load a scheme with name "filename"
    def loadTemplate(self, filename, caption = None, freeze = 0):
        self.loadDocument(filename = filename, caption = caption, freeze = freeze)
        self.sessionID += 1
    def checkID(self, widgetID):
        for widget in self.widgets:
            if widget.instance.widgetID == widgetID:
                return False
        else:
            return True
    
    def loadDocument(self, filename, caption = None, freeze = 0, importing = 0):
        
        import redREnviron
        if filename.split('.')[-1] in ['rrts']:
            tmp=True
        elif filename.split('.')[-1] in ['rrs']:
            tmp=False
        else:
            QMessageBox.information(self, 'Red-R Error', 
            'Cannot load file with extension ' + str(filename.split('.')[-1]),  
            QMessageBox.Ok + QMessageBox.Default)

        loadingProgressBar = self.startProgressBar('Loading '+str(os.path.basename(filename)),
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
            self.schemaPath, self.schemaName = os.path.split(filename)
            self.canvasDlg.setCaption(caption or self.schemaName)
        if importing: # a normal load of the session
            self.schemaName = ""

        loadingProgressBar.setLabelText('Loading Schema Data, please wait')

        ### unzip the file ###
        print filename
        zfile = zipfile.ZipFile( str(filename), "r" )
        for name in zfile.namelist():
            file(os.path.join(redREnviron.directoryNames['tempDir'],os.path.basename(name)), 'wb').write(zfile.read(name)) ## put the data into the tempdir for this session for each file that was in the temp dir for the last schema when saved.
        doc = parse(os.path.join(redREnviron.directoryNames['tempDir'],'tempSchema.tmp')) # load the doc data for the data in the temp dir.

        ## get info from the schema
        schema = doc.firstChild
        widgets = schema.getElementsByTagName("widgets")[0]
        lines = schema.getElementsByTagName("channels")[0]
        #settings = schema.getElementsByTagName("settings")
        f = open(os.path.join(redREnviron.directoryNames['tempDir'],'settings.pickle'))
        settingsDict = eval(str(f.read()))
        f.close()
        
        #settingsDict = eval(str(settings[0].getAttribute("settingsDictionary")))
        self.loadedSettingsDict = settingsDict
        
        self.loadRequiredPackages(settingsDict['_requiredPackages'], loadingProgressBar = loadingProgressBar)
        
        ## make sure that there are no duplicate widgets.
        if not tmp:
            ## need to load the r session before we can load the widgets because the signals will beed to check the classes on init.
            if not self.checkWidgetDuplication(widgets = widgets):
                return
            RSession.Rcommand('load("' + os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/') +'")')
        
        loadingProgressBar.setLabelText('Loading Widgets')
        loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
        loadingProgressBar.setValue(0)
        globalData.globalData = cPickle.loads(self.loadedSettingsDict['_globalData'])
        (loadedOkW, tempFailureTextW) = self.loadWidgets(widgets = widgets, loadingProgressBar = loadingProgressBar, tmp = tmp)
        ## LOAD widgets
        
            
        lineList = lines.getElementsByTagName("channel")
        loadingProgressBar.setLabelText('Loading Lines')
        (loadedOkL, tempFailureTextL) = self.loadLines(lineList, loadingProgressBar = loadingProgressBar, 
        freeze = freeze, tmp = tmp)

        for widget in self.widgets: widget.updateTooltip()
        self.canvas.update()
        self.saveTempDoc()
        
        if not loadedOkW and loadedOkL:
            failureText = tempFailureTextW + tempFailureTextL
            QMessageBox.information(self, 'Schema Loading Failed', 'The following errors occured while loading the schema: <br><br>' + failureText,  QMessageBox.Ok + QMessageBox.Default)
        
        for widget in self.widgets:
            widget.instance.setLoadingSavedSession(False)
        qApp.restoreOverrideCursor() 
        qApp.restoreOverrideCursor()
        qApp.restoreOverrideCursor()
        loadingProgressBar.hide()
        loadingProgressBar.close()
    
    def loadLines(self, lineList, loadingProgressBar, freeze, tmp):
        failureText = ""
        loadedOk = 1
        for line in lineList:
            inIndex = line.getAttribute("inWidgetIndex")
            outIndex = line.getAttribute("outWidgetIndex")
            #print inIndex, outIndex, '###################HFJSDADSHFAK#############'
            
            if inIndex == None or outIndex == None or str(inIndex) == '' or str(outIndex) == '': # drive down the except path
                print inIndex, outIndex 
                
                raise Exception
            if freeze: enabled = 0
            else:      enabled = int(line.getAttribute("enabled"))
            signals = line.getAttribute("signals")
            if tmp: ## index up the index to match sessionID
                inIndex += '_'+str(self.sessionID)
                outIndex += '_'+str(self.sessionID)
                print inIndex, outIndex, 'Settings template ID to these values'
            inWidget = self.getWidgetByID(inIndex)
            outWidget = self.getWidgetByID(outIndex)
            
            #print inWidget, outWidget, '#########$$$$$#########$$$$$$#######'
            if inWidget == None or outWidget == None:
                print 'Expected ID\'s', inIndex, outIndex
                print '\n\nAvailable indicies are listed here.\'\''
                for widget in self.widgets:
                    print widget.instance.widgetID
                failureText += "<nobr>Failed to create a signal line between widgets <b>%s</b> and <b>%s</b></nobr><br>" % (outIndex, inIndex)
                loadedOk = 0
                continue
            signalList = eval(signals)
            for (outName, inName) in signalList:
                self.addLink(outWidget, inWidget, outName, inName, enabled)
            
            #required to process all the signals of the saved widgets.
            #without this all the signals are set to unprocessed 
            #and will re-process on any update of an upstream widget
            self.signalManager.setFreeze(0)
            qApp.processEvents()
            
        return (loadedOk, failureText)
    def loadWidgets(self, widgets, loadingProgressBar, tmp):
        lpb = 0
        loadedOk = 1
        failureText = ''
        addY = self.minimumY()
        for widget in widgets.getElementsByTagName("widget"):
            name = widget.getAttribute("widgetName")

            settings = cPickle.loads(self.loadedSettingsDict[widget.getAttribute('widgetID')]['settings'])
            inputs = cPickle.loads(self.loadedSettingsDict[widget.getAttribute('widgetID')]['inputs'])
            outputs = cPickle.loads(self.loadedSettingsDict[widget.getAttribute('widgetID')]['outputs'])

            print 'Settings', settings
            tempWidget = self.addWidgetByFileName(name, x = int(widget.getAttribute("xPos")), y = int(
            int(widget.getAttribute("yPos")) + addY), caption = widget.getAttribute("caption"), widgetSettings = settings, saveTempDoc = False)
            
            
            if not tempWidget:
                #print settings
                print 'Widget loading disrupted.  Loading dummy widget with ' + str(settings['inputs']) + ' and ' + str(settings['outputs']) + ' into the schema'
                # we must build a fake widget this will involve getting the inputs and outputs and joining 
                #them at the widget creation 
                
                tempWidget = self.addWidgetByFileName('base_dummy', int(widget.getAttribute("xPos")), int(int(widget.getAttribute("yPos")) + addY), widget.getAttribute("caption"), settings, saveTempDoc = False, forceInSignals = settings['inputs'], forceOutSignals = settings['outputs']) 
                
                if not tempWidget:
                    failureText += '<nobr>Unable to create instance of a widget <b>%s</b></nobr><br>' %(name)
                    loadedOk = 0
                    print widget.getAttribute("caption") + ' settings did not exist, this widget does not conform to current loading criteria.  This should be changed in the widget as soon as possible.  Please report this to the widget creator.'
                    
                    continue
            tempWidget.updateWidgetState()
            ## if tmp then adjust the widgetID to match the sessionID
            #print 'Widget ID orriginal is ', widget.getAttribute('widgetID')
            tempWidget.instance.widgetID = widget.getAttribute('widgetID')  ## reset the widgetID.
            if tmp:
                tempWidget.instance.widgetID += '_'+str(self.sessionID)
                #print tempWidget.instance.widgetID
            tempWidget.instance.setLoadingSavedSession(True)
            lpb += 1
            loadingProgressBar.setValue(lpb)
            
        return (loadedOk, failureText)
    def checkWidgetDuplication(self, widgets):
        for widget in widgets.getElementsByTagName("widget"):
            widgetIDisNew = self.checkID(widget.getAttribute('widgetID'))
            if widgetIDisNew == False:
                qApp.restoreOverrideCursor()
                QMessageBox.critical(self, 'Red-R Canvas', 
                'Widget ID is a duplicate, I can\'t load this!!!',  QMessageBox.Ok)
                return False
        return True

    def loadRequiredPackages(self, required, loadingProgressBar):
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
            print required['RedR']
            
            for name,package in required['RedR'].items():
                print package
                if not (package['Name'] in installedPackages.keys() 
                and package['Version']['Number'] == installedPackages[package['Name']]['Version']['Number']):
                    downloadList[package['Name']] = {'Version':str(package['Version']['Number']), 'installed':False}

            if len(downloadList.keys()) > 0:
                self.canvasDlg.packageManagerGUI.show()
                self.canvasDlg.packageManagerGUI.askToInstall(downloadList,
                'The following packages need to be installed before the session can be loaded.')
        except: 
            import sys, traceback
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        
    def dumpWidgetVariables(self):
        for widget in self.widgets:
            self.canvasDlg.output.write("<hr><b>%s</b><br>" % (widget.caption))
            v = vars(widget.instance).keys()
            v.sort()
            for val in v:
                self.canvasDlg.output.write("%s = %s" % (val, getattr(widget.instance, val)))

                
    
            
    def keyReleaseEvent(self, e):
        self.ctrlPressed = int(e.modifiers()) & Qt.ControlModifier != 0
        e.ignore()
    def getXMLText(self, nodelist):
        rc = ''
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    def keyPressEvent(self, e):
        self.ctrlPressed = int(e.modifiers()) & Qt.ControlModifier != 0
        if e.key() > 127:
            #e.ignore()
            QWidget.keyPressEvent(self, e)
            return

        # the list could include (e.ShiftButton, "Shift") if the shift key didn't have the special meaning
        pressed = "-".join(filter(None, [int(e.modifiers()) & x and y for x, y in [(Qt.ControlModifier, "Ctrl"), (Qt.AltModifier, "Alt")]]) + [chr(e.key())])
        widgetToAdd = self.canvasDlg.widgetShortcuts.get(pressed)
        if widgetToAdd:
            self.addWidget(widgetToAdd)
            if e.modifiers() & Qt.ShiftModifier and len(self.widgets) > 1:
                self.addLine(self.widgets[-2], self.widgets[-1])
        else:
            #e.ignore()
            QWidget.keyPressEvent(self, e)
# #######################################
# # Progress Bar
# #######################################
    def startProgressBar(self,title,text,max):
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        
        progressBar = QProgressDialog()
        progressBar.setCancelButtonText(QString())
        progressBar.move(pos.x() + (size.width()/2) , pos.y() + (size.height()/2))
        progressBar.setWindowTitle(title)
        progressBar.setLabelText(text)
        progressBar.setMaximum(max)
        progressBar.setValue(0)
        progressBar.show()
        return progressBar


# this class is needed by signalDialog to show widgets and lines
class SignalCanvasView(QGraphicsView):
    def __init__(self, dlg, canvasDlg, *args):
        apply(QGraphicsView.__init__,(self,) + args)
        self.dlg = dlg
        self.canvasDlg = canvasDlg
        self.bMouseDown = False
        self.tempLine = None
        self.inWidget = None
        self.outWidget = None
        self.inWidgetIcon = None
        self.outWidgetIcon = None
        self.lines = []
        self.outBoxes = []
        self.inBoxes = []
        self.texts = []
        self.ensureVisible(0,0,1,1)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setRenderHint(QPainter.Antialiasing)

    def addSignalList(self, outWidget, inWidget):
        self.scene().clear()
        outputs, inputs = outWidget.widgetInfo.outputs, inWidget.widgetInfo.inputs
        outIcon, inIcon = self.canvasDlg.getWidgetIcon(outWidget.widgetInfo), self.canvasDlg.getWidgetIcon(inWidget.widgetInfo)
        self.lines = []
        self.outBoxes = []
        self.inBoxes = []
        self.texts = []
        xSpaceBetweenWidgets = 100  # space between widgets
        xWidgetOff = 10             # offset for widget position
        yWidgetOffTop = 10          # offset for widget position
        yWidgetOffBottom = 30       # offset for widget position
        ySignalOff = 10             # space between the top of the widget and first signal
        ySignalSpace = 50           # space between two neighbouring signals
        ySignalSize = 20            # height of the signal box
        xSignalSize = 20            # width of the signal box
        xIconOff = 10
        iconSize = 48

        count = max(len(inputs), len(outputs))
        height = max ((count)*ySignalSpace, 70)

        # calculate needed sizes of boxes to show text
        maxLeft = 0
        for i in range(len(inputs)):
            maxLeft = max(maxLeft, self.getTextWidth("("+inputs[i].name+")", 1))
            maxLeft = max(maxLeft, self.getTextWidth(inputs[i].type))

        maxRight = 0
        for i in range(len(outputs)):
            maxRight = max(maxRight, self.getTextWidth("("+outputs[i].name+")", 1))
            maxRight = max(maxRight, self.getTextWidth(outputs[i].type))

        width = max(maxLeft, maxRight) + 70 # we add 70 to show icons beside signal names

        # show boxes
        brush = QBrush(QColor(60,150,255))
        self.outWidget = QGraphicsRectItem(xWidgetOff, yWidgetOffTop, width, height, None, self.dlg.canvas)
        self.outWidget.setBrush(brush)
        self.outWidget.setZValue(-100)

        self.inWidget = QGraphicsRectItem(xWidgetOff + width + xSpaceBetweenWidgets, yWidgetOffTop, width, height, None, self.dlg.canvas)
        self.inWidget.setBrush(brush)
        self.inWidget.setZValue(-100)
        
        canvasPicsDir  = os.path.join(redREnviron.directoryNames['canvasDir'], "icons")
        if os.path.exists(os.path.join(canvasPicsDir, "frame.png")):
            widgetBack = QPixmap(os.path.join(canvasPicsDir, "frame.png"))
        else:
            widgetBack = outWidget.imageFrame

        # if icons -> show them
        if outIcon:
            frame = QGraphicsPixmapItem(widgetBack, None, self.dlg.canvas)
            frame.setPos(xWidgetOff + xIconOff, yWidgetOffTop + height/2.0 - frame.pixmap().width()/2.0)
            self.outWidgetIcon = QGraphicsPixmapItem(outIcon.pixmap(iconSize, iconSize), None, self.dlg.canvas)
            self.outWidgetIcon.setPos(xWidgetOff + xIconOff, yWidgetOffTop + height/2.0 - self.outWidgetIcon.pixmap().width()/2.0)
        
        if inIcon:
            frame = QGraphicsPixmapItem(widgetBack, None, self.dlg.canvas)
            frame.setPos(xWidgetOff + xSpaceBetweenWidgets + 2*width - xIconOff - frame.pixmap().width(), yWidgetOffTop + height/2.0 - frame.pixmap().width()/2.0)
            self.inWidgetIcon = QGraphicsPixmapItem(inIcon.pixmap(iconSize, iconSize), None, self.dlg.canvas)
            self.inWidgetIcon.setPos(xWidgetOff + xSpaceBetweenWidgets + 2*width - xIconOff - self.inWidgetIcon.pixmap().width(), yWidgetOffTop + height/2.0 - self.inWidgetIcon.pixmap().width()/2.0)

        # show signal boxes and text labels
        #signalSpace = (count)*ySignalSpace
        signalSpace = height
        for i in range(len(outputs)):
            y = yWidgetOffTop + ((i+1)*signalSpace)/float(len(outputs)+1)
            box = QGraphicsRectItem(xWidgetOff + width, y - ySignalSize/2.0, xSignalSize, ySignalSize, None, self.dlg.canvas)
            box.setBrush(QBrush(QColor(0,0,255)))
            box.setZValue(200)
            self.outBoxes.append((outputs[i].name, box))

            self.texts.append(MyCanvasText(self.dlg.canvas, outputs[i].name, xWidgetOff + width - 5, y - 7, Qt.AlignRight | Qt.AlignVCenter, bold =1, show=1))
            self.texts.append(MyCanvasText(self.dlg.canvas, outputs[i].type, xWidgetOff + width - 5, y + 7, Qt.AlignRight | Qt.AlignVCenter, bold =0, show=1))

        for i in range(len(inputs)):
            y = yWidgetOffTop + ((i+1)*signalSpace)/float(len(inputs)+1)
            box = QGraphicsRectItem(xWidgetOff + width + xSpaceBetweenWidgets - xSignalSize, y - ySignalSize/2.0, xSignalSize, ySignalSize, None, self.dlg.canvas)
            box.setBrush(QBrush(QColor(0,0,255)))
            box.setZValue(200)
            self.inBoxes.append((inputs[i].name, box))

            self.texts.append(MyCanvasText(self.dlg.canvas, inputs[i].name, xWidgetOff + width + xSpaceBetweenWidgets + 5, y - 7, Qt.AlignLeft | Qt.AlignVCenter, bold =1, show=1))
            self.texts.append(MyCanvasText(self.dlg.canvas, inputs[i].type, xWidgetOff + width + xSpaceBetweenWidgets + 5, y + 7, Qt.AlignLeft | Qt.AlignVCenter, bold =0, show=1))

        self.texts.append(MyCanvasText(self.dlg.canvas, outWidget.caption, xWidgetOff + width/2.0, yWidgetOffTop + height + 5, Qt.AlignHCenter | Qt.AlignTop, bold =1, show=1))
        self.texts.append(MyCanvasText(self.dlg.canvas, inWidget.caption, xWidgetOff + width* 1.5 + xSpaceBetweenWidgets, yWidgetOffTop + height + 5, Qt.AlignHCenter | Qt.AlignTop, bold =1, show=1))

        return (2*xWidgetOff + 2*width + xSpaceBetweenWidgets, yWidgetOffTop + height + yWidgetOffBottom)

    def getTextWidth(self, text, bold = 0):
        temp = QGraphicsSimpleTextItem(text, None, self.dlg.canvas)
        if bold:
            font = temp.font()
            font.setBold(1)
            temp.setFont(font)
        temp.hide()
        return temp.boundingRect().width()

    # ###################################################################
    # mouse button was pressed
    def mousePressEvent(self, ev):
        print ' SignalCanvasView mousePressEvent'
        self.bMouseDown = 1
        point = self.mapToScene(ev.pos())
        activeItem = self.scene().itemAt(QPointF(ev.pos()))
        if type(activeItem) == QGraphicsRectItem and activeItem not in [self.outWidget, self.inWidget]:
            self.tempLine = QGraphicsLineItem(None, self.dlg.canvas)
            self.tempLine.setLine(point.x(), point.y(), point.x(), point.y())
            self.tempLine.setPen(QPen(QColor(0,255,0), 1))
            self.tempLine.setZValue(-300)
            
        elif type(activeItem) == QGraphicsLineItem:
            for (line, outName, inName, outBox, inBox) in self.lines:
                if line == activeItem:
                    self.dlg.removeLink(outName, inName)
                    return

    # ###################################################################
    # mouse button was released #########################################
    def mouseMoveEvent(self, ev):
        if self.tempLine:
            curr = self.mapToScene(ev.pos())
            start = self.tempLine.line().p1()
            self.tempLine.setLine(start.x(), start.y(), curr.x(), curr.y())
            self.scene().update()

    # ###################################################################
    # mouse button was released #########################################
    def mouseReleaseEvent(self, ev):
        if self.tempLine:
            activeItem = self.scene().itemAt(QPointF(ev.pos()))
            if type(activeItem) == QGraphicsRectItem:
                activeItem2 = self.scene().itemAt(self.tempLine.line().p1())
                if activeItem.x() < activeItem2.x(): outBox = activeItem; inBox = activeItem2
                else:                                outBox = activeItem2; inBox = activeItem
                outName = None; inName = None
                for (name, box) in self.outBoxes:
                    if box == outBox: outName = name
                for (name, box) in self.inBoxes:
                    if box == inBox: inName = name
                if outName != None and inName != None:
                    self.dlg.addLink(outName, inName)

            self.tempLine.hide()
            self.tempLine = None
            self.scene().update()


    def addLink(self, outName, inName):
        outBox = None; inBox = None
        for (name, box) in self.outBoxes:
            if name == outName: outBox = box
        for (name, box) in self.inBoxes:
            if name == inName : inBox  = box
        if outBox == None or inBox == None:
            print "error adding link. Data = ", outName, inName
            return
        line = QGraphicsLineItem(None, self.dlg.canvas)
        outRect = outBox.rect()
        inRect = inBox.rect()
        line.setLine(outRect.x() + outRect.width()-2, outRect.y() + outRect.height()/2.0, inRect.x()+2, inRect.y() + inRect.height()/2.0)
        line.setPen(QPen(QColor(0,255,0), 6))
        line.setZValue(100)
        self.scene().update()
        self.lines.append((line, outName, inName, outBox, inBox))


    def removeLink(self, outName, inName):
        for (line, outN, inN, outBox, inBox) in self.lines:
            if outN == outName and inN == inName:
                line.hide()
                self.lines.remove((line, outN, inN, outBox, inBox))
                self.scene().update()
                return


# #######################################
# # Signal dialog - let the user select active signals between two widgets
# #######################################
class SignalDialog(QDialog):
    def __init__(self, canvasDlg, *args):
        apply(QDialog.__init__,(self,) + args)
        self.canvasDlg = canvasDlg

        self.signals = []
        self._links = []
        self.allSignalsTaken = 0

        # GUI    ### canvas dialog that is shown when there are multiple possible connections.
        self.setWindowTitle('Connect Signals')
        self.setLayout(QVBoxLayout())

        self.canvasGroup = OWGUI.widgetBox(self, 1)
        self.canvas = QGraphicsScene(0,0,1000,1000)
        self.canvasView = SignalCanvasView(self, self.canvasDlg, self.canvas, self.canvasGroup)
        self.canvasGroup.layout().addWidget(self.canvasView)

        buttons = OWGUI.widgetBox(self, orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.buttonHelp = OWGUI.button(buttons, self, "&Help")
        buttons.layout().addStretch(1)
        self.buttonClearAll = OWGUI.button(buttons, self, "Clear &All", callback = self.clearAll)
        self.buttonOk = OWGUI.button(buttons, self, "&OK", callback = self.accept)
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        self.buttonCancel = OWGUI.button(buttons, self, "&Cancel", callback = self.reject)

    def clearAll(self):
        while self._links != []:
            self.removeLink(self._links[0][0], self._links[0][1])

    def setOutInWidgets(self, outWidget, inWidget):
        self.outWidget = outWidget
        self.inWidget = inWidget
        (width, height) = self.canvasView.addSignalList(outWidget, inWidget)
        self.canvas.setSceneRect(0, 0, width, height)
        self.resize(width+50, height+80)

    def countCompatibleConnections(self, outputs, inputs, outInstance, inInstance, outType, inType):
        count = 0
        for outS in outputs:
            if outInstance.getOutputType(outS.name) == None: continue  # ignore if some signals don't exist any more, since we will report error somewhere else
            if outInstance.getOutputType(outS.name) == 'All': pass
            elif not issubclass(outInstance.getOutputType(outS.name), outType): continue
            for inS in inputs:
                if inInstance.getOutputType(inS.name) == None: continue  # ignore if some signals don't exist any more, since we will report error somewhere else
                if inInstance.getOutputType(inS.name) == 'All': 
                    count += 1
                    continue
                if type(inInstance.getOutputType(inS.name)) not in [list]:
                    if not issubclass(inType, inInstance.getInputType(inS.name)): continue
                    if issubclass(outInstance.getOutputType(outS.name), inInstance.getInputType(inS.name)): count+= 1
                else:
                    for i in type(inInstance.getOutputType(inS.name)):
                        if not issubclass(inType, i): continue
                        if issubclass(outInstance.getOutputType(outS.name), i): count+= 1
        return count

    def existsABetterLink(self, outSignal, inSignal, outSignals, inSignals):
        existsBetter = 0

        betterOutSignal = None; betterInSignal = None
        for outS in outSignals:
            for inS in inSignals:
                if (outS.name != outSignal.name and outS.name == inSignal.name and outS.type == inSignal.type) or (inS.name != inSignal.name and inS.name == outSignal.name and inS.type == outSignal.type):
                    existsBetter = 1
                    betterOutSignal = outS
                    betterInSignal = inS
        return existsBetter, betterOutSignal, betterInSignal


    def getPossibleConnections(self, outputs, inputs):
        print 'getPossibleConnections'
        possibleLinks = []
        for outS in outputs:
            outType = self.outWidget.instance.getOutputType(outS.name)
            if outType == None:     #print "Unable to find signal type for signal %s. Check the definition of the widget." % (outS.name)
                continue
            for inS in inputs:
                inType = self.inWidget.instance.getInputType(inS.name)
                print outType, inType
                print issubclass(outType, inType)
                print '######'
                if inType == None:
                    print "Unable to find signal type for signal %s. Check the definition of the widget." % (inS.name)
                    continue
                if outType == 'All' or inType == 'All':  # if this is the special 'All' signal we need to let this pass
                    possibleLinks.append((outS.name, inS.name))
                    continue
                    
                if type(inType) not in [list]:
                    if issubclass(outType, inType):
                        possibleLinks.append((outS.name, inS.name))
                        continue
                else:
                    for i in inType:
                        if issubclass(outType, i):
                            possibleLinks.append((outS.name, inS.name))
                            continue
        print possibleLinks
        return possibleLinks

    def addDefaultLinks(self):
        canConnect = 0
        addedInLinks = []
        addedOutLinks = []
        self.multiplePossibleConnections = 0    # can we connect some signal with more than one widget

        minorInputs = [signal for signal in self.inWidget.widgetInfo.inputs if not signal.default]
        majorInputs = [signal for signal in self.inWidget.widgetInfo.inputs if signal.default]
        minorOutputs = [signal for signal in self.outWidget.widgetInfo.outputs if not signal.default]
        majorOutputs = [signal for signal in self.outWidget.widgetInfo.outputs if signal.default]

        inConnected = self.inWidget.getInConnectedSignalNames()
        outConnected = self.outWidget.getOutConnectedSignalNames()

        # input connections that can be simultaneously connected to multiple outputs are not to be considered as already connected
        for i in inConnected[::-1]:
            if not self.inWidget.instance.signalIsOnlySingleConnection(i):
                inConnected.remove(i)

        for s in majorInputs + minorInputs:
            if not self.inWidget.instance.hasInputName(s.name):
                return -1
        for s in majorOutputs + minorOutputs:
            if not self.outWidget.instance.hasOutputName(s.name):
                return -1

        print majorInputs, majorOutputs, minorInputs, minorOutputs
        pl1 = self.getPossibleConnections(majorOutputs, majorInputs)
        pl2 = self.getPossibleConnections(majorOutputs, minorInputs)
        pl3 = self.getPossibleConnections(minorOutputs, majorInputs)
        pl4 = self.getPossibleConnections(minorOutputs, minorInputs)

        all = pl1 + pl2 + pl3 + pl4

        if not all: 
            print all, 'All'
            return 0

        # try to find a link to any inputs that hasn't been previously connected
        self.allSignalsTaken = 1
        for (o,i) in all:
            if i not in inConnected:
                all.remove((o,i))
                all.insert(0, (o,i))
                self.allSignalsTaken = 0       # we found an unconnected link. no need to show the signal dialog
                break
        self.addLink(all[0][0], all[0][1])  # add only the best link

        # there are multiple possible connections if we have in the same priority class more than one possible unconnected link
        for pl in [pl1, pl2, pl3, pl4]:
            #if len(pl) > 1 and sum([i not in inConnected for (o,i) in pl]) > 1: # if we have more than one valid
            if len(pl) > 1:     # if we have more than one valid
                self.multiplePossibleConnections = 1
            if len(pl) > 0:     # when we find a first non-empty list we stop searching
                break
        print all, 'all'
        return len(all) > 0

    def addLink(self, outName, inName):
        if (outName, inName) in self._links: return 1

        # check if correct types
        outType = self.outWidget.instance.getOutputType(outName)
        inType = self.inWidget.instance.getInputType(inName)
        if type(inType) not in [list]:
            if outType == 'All' or inType == 'All': 
                print '|###| Allowing link from '+str(outName)+' to '+str(inName)
                
            elif not issubclass(outType, inType): return 0
        else:
            passes = 0
            for i in inType:
                if issubclass(outType, i): passes = 10
            if not passes: return 0
            
        inSignal = None
        inputs = self.inWidget.widgetInfo.inputs
        for i in range(len(inputs)):
            if inputs[i].name == inName: inSignal = inputs[i]

        # if inName is a single signal and connection already exists -> delete it
        for (outN, inN) in self._links:
            if inN == inName and inSignal.single:
                self.removeLink(outN, inN)

        self._links.append((outName, inName))
        self.canvasView.addLink(outName, inName)
        return 1


    def removeLink(self, outName, inName):
        if (outName, inName) in self._links:
            self._links.remove((outName, inName))
            self.canvasView.removeLink(outName, inName)

    def getLinks(self):
        return self._links

class TemplateDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        
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
        
        
