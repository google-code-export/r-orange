# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington and Anup Parikh
# Description:
#    document class - main operations (save, load, ...)
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, os.path, traceback
from xml.dom.minidom import Document, parse
import orngView, orngCanvasItems, orngTabs
from orngDlgs import *
import RSession

from orngSignalManager import SignalManager
import cPickle, math, orngHistory, zipfile
import pprint
pp = pprint.PrettyPrinter(indent=4)

class SchemaDoc(QWidget):
    def __init__(self, canvasDlg, *args):
        QWidget.__init__(self, *args)
        self.canvasDlg = canvasDlg
        self.ctrlPressed = 0

        self.lines = []                         # list of orngCanvasItems.CanvasLine items
        self.widgets = []                       # list of orngCanvasItems.CanvasWidget items
        self.signalManager = SignalManager()    # signal manager to correctly process signals

        self.schemaPath = self.canvasDlg.settings["saveSchemaDir"]
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


    # we are about to close document
    # ask the user if he is sure
    def closeEvent(self,ce):
        res = QMessageBox.question(self, 'Red-R Canvas','Do you wish to save the schema?', QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        
        if res == QMessageBox.Yes:
            newSettings = self.loadedSettingsDict and self.loadedSettingsDict != dict([(widget.caption, widget.instance.saveSettingsStr()) for widget in self.widgets])
            self.RVariableRemoveSupress = 1
            #if self.canvasDlg.settings["autoSaveSchemasOnClose"] and self.widgets != []:
            # if self.widgets != []:
                # self.save(os.path.join(self.canvasDlg.canvasSettingsDir, "lastSchema.tmp"))

            saveComplete = self.saveDocument()
            
            if not saveComplete: 
                QMessageBox.information(self, 'Red-R Canvas','Save interupted because no file name specified.\nData not saved.',  QMessageBox.Ok + QMessageBox.Default)
                print 'Saving interupted'
                ce.ignore()
                return
            ce.accept()
            self.clear(close = True)
        # if self.canvasDlg.settings["dontAskBeforeClose"]:
            # if newSettings and self.schemaName != "":
                # pass
                ##self.save(True)
            # self.clear(close = True)  
            # self.removeTempDoc()
            # ce.accept()
        elif res == QMessageBox.No:
            self.RVariableRemoveSupress = 1
            self.clear(close = True)
            ce.accept()
        else:
            ce.ignore()
            return
            
            # res = QMessageBox.question(self, 'Orange Canvas','Do you wish to save the schema?', QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            # if res == QMessageBox.Yes:
                # self.saveDocument()
                # ce.accept()
                # self.clear(close = True)
            # elif res == QMessageBox.No:
                # self.clear(close = True)
                # self.removeTempDoc()
                # ce.accept()
            # else:
                # ce.ignore()     # we pressed cancel - we don't want to close the document
                # return
        QWidget.closeEvent(self, ce)
        orngHistory.logCloseSchema(self.schemaID)
        
    # save a temp document whenever anything changes. this doc is deleted on closeEvent
    # in case that Orange crashes, Canvas on the next start offers an option to reload the crashed schema with links frozen
    def saveTempDoc(self):
        return
        if self.widgets != []:
            tempName = os.path.join(self.canvasDlg.canvasSettingsDir, "tempSchema.tmp")
            self.save(tempName,True)
        
    def removeTempDoc(self):
        tempName = os.path.join(self.canvasDlg.canvasSettingsDir, "tempSchema.tmp")
        if os.path.exists(tempName):
            os.remove(tempName)


            
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
    def removeLine1(self, line, close = False):
        #print 'removing a line from' + str(outName) +'to' +str(inName)
        for (outName, inName) in line.getSignals():
            self.signalManager.removeLink(line.outWidget.instance, line.inWidget.instance, outName, inName, close = close)   # update SignalManager

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
    def addWidget(self, widgetInfo, x= -1, y=-1, caption = "", widgetSettings = {}, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        qApp.setOverrideCursor(Qt.WaitCursor)
        try:
            #print str(forceInSignals) 
            #print str(forceOutSignals)
            #print 'adding widget '+caption
            if widgetInfo.name == 'dummy': print 'Loading dummy step 2'
            newwidget = orngCanvasItems.CanvasWidget(self.signalManager, self.canvas, self.canvasView, widgetInfo, self.canvasDlg.defaultPic, self.canvasDlg, widgetSettings, forceInSignals = forceInSignals, forceOutSignals = forceOutSignals)
            #if widgetInfo.name == 'dummy' and (forceInSignals or forceOutSignals):
        except:
            type, val, traceback = sys.exc_info()
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
            # if self.canvasDlg.settings["saveWidgetsPosition"]:
                # newwidget.instance.restoreWidgetPosition()
            newwidget.setProcessing(0)
            orngHistory.logAddWidget(self.schemaID, id(newwidget), (newwidget.widgetInfo.category, newwidget.widgetInfo.name), newwidget.x(), newwidget.y())
        except:
            type, val, traceback = sys.exc_info()
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas

        qApp.restoreOverrideCursor()
        return newwidget

    # remove widget
    def removeWidget(self, widget, saveTempDoc = True, close = False):
        if not widget:
            return
        widget.closing = close
        while widget.inLines != []: self.removeLine1(widget.inLines[0], close = True)
        while widget.outLines != []:  self.removeLine1(widget.outLines[0], close = True)

        self.signalManager.removeWidget(widget.instance) # sending occurs before this point
        self.widgets.remove(widget)
        if self.RVariableRemoveSupress == 1: #send occurs before this point
            widget.remove(suppress = 1)
        else:
            widget.remove()
        if self.RVariableRemoveSupress == 1:
            return
        if saveTempDoc:
            self.saveTempDoc()
        
        orngHistory.logRemoveWidget(self.schemaID, id(widget), (widget.widgetInfo.category, widget.widgetInfo.name))

    def clear(self, close = False):
        print 'clear called'
        self.canvasDlg.setCaption()
        for widget in self.widgets[::-1]:   
            self.removeWidget(widget, saveTempDoc = False, close = close)   # remove widgets from last to first
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
    def addWidgetByFileName(self, widgetFileName, x, y, caption, widgetSettings = {}, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        if widgetFileName == 'dummy': print 'Loading dummy step 1a'
        for category in self.canvasDlg.widgetRegistry.keys():
            for name, widget in self.canvasDlg.widgetRegistry[category].items():
                if widget.fileName == widgetFileName: 
                    if widgetFileName == 'dummy':
                        print 'Loading dummy step 1'
                    #print str(forceInSignals) + 'force in signals'
                    #print str(forceOutSignals) + 'force out signals'
                    return self.addWidget(widget, x, y, caption, widgetSettings, saveTempDoc, forceInSignals, forceOutSignals)
        return None

    # return the widget instance that has caption "widgetName"
    def getWidgetByCaption(self, widgetName):
        for widget in self.widgets:
            if (widget.caption == widgetName):
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
        if os.path.splitext(str(name))[1].lower() != ".rrs": name = os.path.splitext(str(name))[0] + ".rrs"
        return self.save(str(name),tmp=False)
        

    # save the file
    def save(self, filename = None,tmp = True):

        print 'start save schema'
        if filename == None:
            filename = os.path.join(self.schemaPath, self.schemaName)
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        progressBar = QProgressDialog()
        progressBar.setCancelButtonText(QString())
        progressBar.move(pos.x() + (size.width()/2) , pos.y() + (size.height()/2))
        progressBar.setWindowTitle('Saving '+str(os.path.basename(filename)))
        progressBar.setLabelText('Saving '+str(os.path.basename(filename)))
        progressBar.setMaximum(len(self.widgets)+len(self.lines)+3)
        progress = 0
        progressBar.setValue(progress)
        progressBar.show()
        
        # create xml document
        doc = Document()
        schema = doc.createElement("schema")
        widgets = doc.createElement("widgets")
        lines = doc.createElement("channels")
        settings = doc.createElement("settings")
        doc.appendChild(schema)
        schema.appendChild(widgets)
        schema.appendChild(lines)
        schema.appendChild(settings)
        settingsDict = {}

        
        #save widgets
        for widget in self.widgets:
            temp = doc.createElement("widget")
            temp.setAttribute("xPos", str(int(widget.x())) )
            temp.setAttribute("yPos", str(int(widget.y())) )
            temp.setAttribute("caption", widget.caption)
            temp.setAttribute("widgetName", widget.widgetInfo.fileName)
            print 'save in orngDoc ' + str(widget.caption)
            progress += 1
            progressBar.setValue(progress)
            settingsDict[widget.caption] = widget.instance.saveSettingsStr()
            widgets.appendChild(temp)

        #save connections
        for line in self.lines:
            temp = doc.createElement("channel")
            temp.setAttribute("outWidgetCaption", line.outWidget.caption)
            temp.setAttribute("inWidgetCaption", line.inWidget.caption)
            temp.setAttribute("enabled", str(line.getEnabled()))
            temp.setAttribute("signals", str(line.getSignals()))
            lines.appendChild(temp)

        settings.setAttribute("settingsDictionary", str(settingsDict))      
        
        xmlText = doc.toprettyxml()
        progress += 1
        progressBar.setValue(progress)

        if not tmp:
            tempschema = os.path.join(self.canvasDlg.canvasSettingsDir, "tempSchema.tmp")
            tempR = os.path.join(self.canvasDlg.canvasSettingsDir, "tmp.RData").replace('\\','/')
            file = open(tempschema, "wt")
            file.write(xmlText)
            file.close()
            doc.unlink()
            print 'saving image...'
            progressBar.setLabelText('Saving Data...')
            progress += 1
            progressBar.setValue(progress)

            RSession.Rcommand('save.image("' + tempR + '")')
            zout = zipfile.ZipFile(filename, "w")
            for fname in [tempschema,tempR]:
                zout.write(fname)
            zout.close()
            os.remove(tempR)
            os.remove(tempschema)
            print 'image saved.'
        else :
            file = open(filename, "wt")
            file.write(xmlText)
            file.close()
            doc.unlink()
            
        
        if os.path.splitext(filename)[1].lower() == ".rrs":
            (self.schemaPath, self.schemaName) = os.path.split(filename)
            self.canvasDlg.settings["saveSchemaDir"] = self.schemaPath
            self.canvasDlg.addToRecentMenu(filename)
            self.canvasDlg.setCaption(self.schemaName)
        progress += 1
        progressBar.setValue(progress)
        progressBar.close()

        return True
    # load a scheme with name "filename"
    def loadDocument(self, filename, caption = None, freeze = 0, importBlank = 0):
        
        import orngEnviron
        ### .rrw functionality
        if filename.split('.')[-1] == 'rrw':
            self.loadRRW(filename)
            return # we don't need to load anything else, we are not really loading a rrs file. 
        ###
        print 'document load called'
        #self.clear()
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        loadingProgressBar = QProgressDialog()
        loadingProgressBar.setCancelButtonText(QString())
        loadingProgressBar.setWindowIcon(QIcon(os.path.join(orngEnviron.directoryNames['canvasDir'], 'icons', 'save.png')))
        loadingProgressBar.move(pos.x() + (size.width()/2) , pos.y() + (size.height()/2))
        loadingProgressBar.setWindowTitle('Loading '+str(os.path.basename(filename)))
        loadingProgressBar.show()
        loadingProgressBar.setLabelText('Loading '+str(filename))
        if not os.path.exists(filename):
            if os.path.splitext(filename)[1].lower() != ".tmp":
                QMessageBox.critical(self, 'Red-R Canvas', 'Unable to locate file "'+ filename + '"',  QMessageBox.Ok)
            return
            loadingProgressBar.hide()
            loadingProgressBar.close()
        # set cursor
        qApp.setOverrideCursor(Qt.WaitCursor)
        failureText = ""
        
        if os.path.splitext(filename)[1].lower() == ".rrs":
            self.schemaPath, self.schemaName = os.path.split(filename)
            self.canvasDlg.setCaption(caption or self.schemaName)
        try:
            import re
            for widget in self.widgets: # convert the caption names so there are no conflicts
                widget.caption += 'A'
                
            loadingProgressBar.setLabelText('Loading Schema Data, please wait')
            zfile = zipfile.ZipFile( str(filename), "r" )
            for name in zfile.namelist():
                file(os.path.join(self.canvasDlg.canvasSettingsDir,os.path.basename(name)), 'wb').write(zfile.read(name))
                if re.search('tempSchema.tmp',os.path.basename(name)):
                    doc = parse(os.path.join(self.canvasDlg.canvasSettingsDir,os.path.basename(name)))
                else:
                    RSession.Rcommand('load("' + os.path.join(self.canvasDlg.canvasSettingsDir,os.path.basename(name)).replace('\\','/') +'")')
            schema = doc.firstChild
            widgets = schema.getElementsByTagName("widgets")[0]
            lines = schema.getElementsByTagName("channels")[0]
            settings = schema.getElementsByTagName("settings")
            settingsDict = eval(str(settings[0].getAttribute("settingsDictionary")))
            self.loadedSettingsDict = settingsDict
              
            # read widgets
            # read widgets
            loadedOk = 1
            loadingProgressBar.setLabelText('Loading Widgets')
            loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
            loadingProgressBar.setValue(0)
            lpb = 0
            for widget in widgets.getElementsByTagName("widget"):
                try:
                    name = widget.getAttribute("widgetName")
                    print 'Name: '+str(name)+' (orngDoc.py)'
                    settings = cPickle.loads(settingsDict[widget.getAttribute("caption")])
                    try:
                        if 'requiredRLibraries' in settings.keys():
                            if 'CRANrepos' in qApp.canvasDlg.settings.keys():
                                repo = qApp.canvasDlg.settings['CRANrepos']
                            else:
                                repo = None
                            loadingProgressBar.setLabelText('Downloading Required R Packages. This may take a while...')
                            RSession.require_librarys(settings['requiredRLibraries']['pythonObject'], repository=repo)
                    except: 
                        import sys, traceback
                        print '-'*60
                        traceback.print_exc(file=sys.stdout)
                        print '-'*60        

                        
                    tempWidget = self.addWidgetByFileName(name, int(widget.getAttribute("xPos")), 
                    int(widget.getAttribute("yPos")), widget.getAttribute("caption"), settings, saveTempDoc = False)
                    tempWidget.updateWidgetState()
                    tempWidget.instance.setLoadingSavedSession(True)
                    if not tempWidget:
                        #print settings
                        print 'Widget loading disrupted.  Loading dummy widget with ' + str(settings['inputs']) + ' and ' + str(settings['outputs']) + ' into the schema'
                        # we must build a fake widget this will involve getting the inputs and outputs and joining 
                        #them at the widget creation 
                        
                        tempWidget = self.addWidgetByFileName('dummy' , int(widget.getAttribute("xPos")), int(widget.getAttribute("yPos")), widget.getAttribute("caption"), settings, saveTempDoc = False,forceInSignals = settings['inputs'], forceOutSignals = settings['outputs']) 
                        
                        if not tempWidget:
                            #QMessageBox.information(self, 'Orange Canvas','Unable to create instance of widget \"'+ name + '\"',  QMessageBox.Ok + QMessageBox.Default)
                            failureText += '<nobr>Unable to create instance of a widget <b>%s</b></nobr><br>' %(name)
                            loadedOk = 0
                            print widget.getAttribute("caption") + ' settings did not exist, this widget does not conform to current loading criteria.  This should be changed in the widget as soon as possible.  Please report this to the widget creator.'
                except:
                    import sys, traceback
                    print 'Error occured during widget loading'
                    print '-'*60
                    traceback.print_exc(file=sys.stdout)
                    print '-'*60        
                lpb += 1
                loadingProgressBar.setValue(lpb)
            if not importBlank: # a normal load of the session
                pass
            else:
                self.schemaName = ""

            #read lines
            lineList = lines.getElementsByTagName("channel")
            loadingProgressBar.setLabelText('Loading Lines')
            # loadingProgressBar.setMaximum(len(lineList))
            # loadingProgressBar.setValue(0)
            # lpb = 0
            
            

            for line in lineList:
                inCaption = line.getAttribute("inWidgetCaption")
                outCaption = line.getAttribute("outWidgetCaption")
                if freeze: enabled = 0
                else:      enabled = int(line.getAttribute("enabled"))
                signals = line.getAttribute("signals")
                inWidget = self.getWidgetByCaption(inCaption)
                outWidget = self.getWidgetByCaption(outCaption)
                if inWidget == None or outWidget == None:
                    failureText += "<nobr>Failed to create a signal line between widgets <b>%s</b> and <b>%s</b></nobr><br>" % (outCaption, inCaption)
                    loadedOk = 0
                    continue

                signalList = eval(signals)
                for (outName, inName) in signalList:
                    
                    self.addLink(outWidget, inWidget, outName, inName, enabled)
                qApp.processEvents()
                # lpb += 1
                # loadingProgressBar.setValue(lpb)
            
        finally:
            qApp.restoreOverrideCursor()
            

        for widget in self.widgets: widget.updateTooltip()
        self.canvas.update()

        self.saveTempDoc()

        if not loadedOk:
            QMessageBox.information(self, 'Schema Loading Failed', 'The following errors occured while loading the schema: <br><br>' + failureText,  QMessageBox.Ok + QMessageBox.Default)
        
        loadingProgressBar.setLabelText('Loading Widget Data')
        loadingProgressBar.setMaximum(len(self.widgets))
        loadingProgressBar.setValue(0)
        lpb = 0
        for widget in self.widgets:
            print 'for widget (orngDoc.py) ' + widget.instance._widgetInfo['fileName']
            try: # important to have this or else failures in load saved settings will result in no links able to connect.
                widget.instance.onLoadSavedSession()
            except:
                import traceback,sys
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        
                QMessageBox.information(self,'Error', 'Loading Failed for ' + widget.instance._widgetInfo['fileName'], 
                QMessageBox.Ok + QMessageBox.Default)
            lpb += 1
            loadingProgressBar.setValue(lpb)
            
        print 'done on load'

        # do we want to restore last position and size of the widget
        if self.canvasDlg.settings["saveWidgetsPosition"]:
            for widget in self.widgets:
                widget.instance.setLoadingSavedSession(False)
                #widget.instance.show()
        qApp.restoreOverrideCursor() 
        qApp.restoreOverrideCursor()
        loadingProgressBar.hide()
        loadingProgressBar.close()
    # save document as application

        
    def dumpWidgetVariables(self):
        for widget in self.widgets:
            self.canvasDlg.output.write("<hr><b>%s</b><br>" % (widget.caption))
            v = vars(widget.instance).keys()
            v.sort()
            for val in v:
                self.canvasDlg.output.write("%s = %s" % (val, getattr(widget.instance, val)))

                
    def loadRRW(self, filename):
        pass # funcitons for loading the rrw file.
    def keyReleaseEvent(self, e):
        self.ctrlPressed = int(e.modifiers()) & Qt.ControlModifier != 0
        e.ignore()

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

#    def resizeEvent(self, ev):
#        QWidget.resizeEvent(self, ev)
#        self.canvas.addRect(self.canvasView.size().width()-1, self.canvasView.size().height()-1, 1, 1)