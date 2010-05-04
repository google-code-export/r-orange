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
        self.urlOpener = urllib.FancyURLopener()
        self.tags = xml.dom.minidom.parseString('<tree></tree>')

    # we are about to close document
    # ask the user if he is sure
    def closeEvent(self,ce):
        QWidget.closeEvent(self, ce)
        orngHistory.logCloseSchema(self.schemaID)
        return # the close of red-r should be handled in red-rCanvas not in the schema???
        
        if self.canvasDlg.settings['dontAskBeforeClose']:
            res = QMessageBox.No
        else:
            res = QMessageBox.question(self, 'Red-R Canvas','Do you wish to save the schema?', QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
        
        if res == QMessageBox.Yes:
            #newSettings = self.loadedSettingsDict and self.loadedSettingsDict != dict([(widget.caption, widget.instance.saveSettingsStr()) for widget in self.widgets])
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
        if close:
            RSession.Rcommand('quit("no")') # close the entire session dropping anything that was open in case it was left by something else, makes the closing much cleaner than just loosing the session.

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
        required = doc.createElement("required")
        doc.appendChild(schema)
        schema.appendChild(widgets)
        schema.appendChild(lines)
        schema.appendChild(settings)
        schema.appendChild(required)
        
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
            print 'save in orngDoc ' + str(widget.caption)
            progress += 1
            progressBar.setValue(progress)
            
            s = widget.instance.getSettings()
            
            map(requiredRLibraries.__setitem__, s['requiredRLibraries']['pythonObject'], []) 
            #requiredRLibraries.extend()
            del s['requiredRLibraries']
            settingsDict[widget.caption] = cPickle.dumps(s)
            
            if widget.widgetInfo.package != 'base' and widget.widgetInfo.package not in requireRedRLibraries.keys():
                f = open(os.path.join(redREnviron.directoryNames['libraryDir'],
                widget.widgetInfo.package,widget.widgetInfo.package + '.rrp'),'r')
                rrp = f.read()
                f.close()
                requireRedRLibraries[widget.widgetInfo.package] = rrp
        
            widgets.appendChild(temp)
        
        r =  cPickle.dumps({'R': requiredRLibraries.keys(), 'RedR': requireRedRLibraries.values()})
        required.setAttribute("requiredPackages", str({'r':r}))
        
        settings.setAttribute("settingsDictionary", str(settingsDict))      
        
        #save connections
        for line in self.lines:
            temp = doc.createElement("channel")
            temp.setAttribute("outWidgetCaption", line.outWidget.caption)
            temp.setAttribute("inWidgetCaption", line.inWidget.caption)
            temp.setAttribute("enabled", str(line.getEnabled()))
            temp.setAttribute("signals", str(line.getSignals()))
            lines.appendChild(temp)

        
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
    def loadTemplate(self, filename, caption = None, freeze = 0, importBlank = 0):
        import redREnviron
        ### .rrw functionality
        if filename.split('.')[-1] in ['rrw', 'rrp']:
            self.loadRRW(filename)
            return # we don't need to load anything else, we are not really loading a rrs file. 
        ###
        print filename.split('.')[-1], 'File name extension'
        print 'document load called'
        #self.clear()
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        loadingProgressBar = QProgressDialog()
        loadingProgressBar.setCancelButtonText(QString())
        loadingProgressBar.setWindowIcon(QIcon(os.path.join(redREnviron.directoryNames['canvasDir'], 'icons', 'save.png')))
        loadingProgressBar.move(pos.x() + (size.width()/2) , pos.y() + (size.height()/2))
        loadingProgressBar.setWindowTitle('Loading '+str(os.path.basename(filename)))
        loadingProgressBar.show()
        loadingProgressBar.setLabelText('Loading '+str(filename))
        if not os.path.exists(filename):
            if os.path.splitext(filename)[1].lower() != ".tmp":
                QMessageBox.critical(self, 'Red-R Canvas', 'Unable to locate file "'+ filename + '"',  QMessageBox.Ok)
            
            loadingProgressBar.hide()
            loadingProgressBar.close()
            return
        # set cursor
        qApp.setOverrideCursor(Qt.WaitCursor)
        failureText = ""
        
        #if os.path.splitext(filename)[1].lower() == ".rrs":
            #self.schemaPath, self.schemaName = os.path.split(filename)
            #self.canvasDlg.setCaption(caption or self.schemaName)
        try:
            import re
            # for widget in self.widgets: # convert the caption names so there are no conflicts
                # widget.caption += 'A'
                
            loadingProgressBar.setLabelText('Loading Schema Data, please wait')
            zfile = zipfile.ZipFile( str(filename), "r" )
            for name in zfile.namelist():
                file(os.path.join(self.canvasDlg.canvasSettingsDir,os.path.basename(name)), 'wb').write(zfile.read(name))
                
                #if re.search('tempSchema.tmp',os.path.basename(name)):
            doc = parse(os.path.join(self.canvasDlg.canvasSettingsDir,'tempSchema.tmp'))
                
            schema = doc.firstChild
            widgets = schema.getElementsByTagName("widgets")[0]
            lines = schema.getElementsByTagName("channels")[0]
            settings = schema.getElementsByTagName("settings")
            settingsDict = eval(str(settings[0].getAttribute("settingsDictionary")))
            self.loadedSettingsDict = settingsDict
            
            
            
            required = schema.getElementsByTagName("required")
            required = eval(str(required[0].getAttribute("requiredPackages")))
            #print required
            required = cPickle.loads(required['r'])
            # print required
            
            try:
                if len(required['R']) > 0:
                    #print qApp.canvasDlg.settings.keys()
                    #print qApp.canvasDlg.settings['CRANrepos']
                    if 'CRANrepos' in qApp.canvasDlg.settings.keys():
                        repo = qApp.canvasDlg.settings['CRANrepos']
                    else:
                        repo = None
                    loadingProgressBar.setLabelText('Loading required R Packages. If not found they will be downloaded.\n This may take a while...')
                    RSession.require_librarys(required['R'], repository=repo)
            except: 
                import sys, traceback
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        

            for i in required['RedR']:
                self.loadRRW(fileText = i)
                
                
            #RSession.Rcommand('load("' + os.path.join(self.canvasDlg.canvasSettingsDir, "tmp.RData").replace('\\','/') +'")')

            
            # read widgets
            loadedOk = 1
            loadingProgressBar.setLabelText('Loading Widgets')
            loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
            loadingProgressBar.setValue(0)
            lpb = 0
            for widget in widgets.getElementsByTagName("widget"):
                try:
                    name = widget.getAttribute("widgetName")
                    #print 'Name: '+str(name)+' (orngDoc.py)'
                    #print settingsDict[widget.getAttribute("caption")]
                    settings = cPickle.loads(settingsDict[widget.getAttribute("caption")])
                    tempWidget = self.addWidgetByFileName(name, x = -1, #int(widget.getAttribute("xPos")), 
                    y = -1, caption = "", #int(widget.getAttribute("yPos")), widget.getAttribute("caption"), 
                    widgetSettings = settings, saveTempDoc = False)
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

        #self.saveTempDoc()

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
        # if self.canvasDlg.settings["saveWidgetsPosition"]:
            # for widget in self.widgets:
                # widget.instance.setLoadingSavedSession(False)
                #widget.instance.show()
        qApp.restoreOverrideCursor() 
        qApp.restoreOverrideCursor()
        loadingProgressBar.hide()
        loadingProgressBar.close()
    # save document as application
    
    
    
    def loadDocument(self, filename, caption = None, freeze = 0, importBlank = 0):
        
        import redREnviron
        ### .rrw functionality
        if filename.split('.')[-1] in ['rrw', 'rrp']:
            self.loadRRW(filename)
            return # we don't need to load anything else, we are not really loading a rrs file. 
        ###
        print filename.split('.')[-1], 'File name extension'
        print 'document load called'
        #self.clear()
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        loadingProgressBar = QProgressDialog()
        loadingProgressBar.setCancelButtonText(QString())
        loadingProgressBar.setWindowIcon(QIcon(os.path.join(redREnviron.directoryNames['canvasDir'], 'icons', 'save.png')))
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
                
                #if re.search('tempSchema.tmp',os.path.basename(name)):
            doc = parse(os.path.join(self.canvasDlg.canvasSettingsDir,'tempSchema.tmp'))
                
            schema = doc.firstChild
            widgets = schema.getElementsByTagName("widgets")[0]
            lines = schema.getElementsByTagName("channels")[0]
            settings = schema.getElementsByTagName("settings")
            settingsDict = eval(str(settings[0].getAttribute("settingsDictionary")))
            self.loadedSettingsDict = settingsDict
            
            required = schema.getElementsByTagName("required")
            required = eval(str(required[0].getAttribute("requiredPackages")))
            #print required
            required = cPickle.loads(required['r'])
            # print required
            
            try:
                if len(required['R']) > 0:
                    #print qApp.canvasDlg.settings.keys()
                    #print qApp.canvasDlg.settings['CRANrepos']
                    if 'CRANrepos' in qApp.canvasDlg.settings.keys():
                        repo = qApp.canvasDlg.settings['CRANrepos']
                    else:
                        repo = None
                    loadingProgressBar.setLabelText('Loading required R Packages. If not found they will be downloaded.\n This may take a while...')
                    RSession.require_librarys(required['R'], repository=repo)
            except: 
                import sys, traceback
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        

            for i in required['RedR']:
                self.loadRRW(fileText = i)
                
                
            RSession.Rcommand('load("' + os.path.join(self.canvasDlg.canvasSettingsDir, "tmp.RData").replace('\\','/') +'")')

            
            # read widgets
            loadedOk = 1
            loadingProgressBar.setLabelText('Loading Widgets')
            loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
            loadingProgressBar.setValue(0)
            lpb = 0
            for widget in widgets.getElementsByTagName("widget"):
                try:
                    name = widget.getAttribute("widgetName")
                    #print 'Name: '+str(name)+' (orngDoc.py)'
                    #print settingsDict[widget.getAttribute("caption")]
                    settings = cPickle.loads(settingsDict[widget.getAttribute("caption")])
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

                
    def loadRRW(self, filename = None, fileText = None, force = False):
        if filename == None and fileText == None:
            raise Exception, 'Must specify either a fileName or fileText'
        if filename != None and fileText != None:
            raise Exception, 'Only one of fileName or fileText can be specified'
            
        
        print 'Loading RRW file.  This will update your system.'
        
        if filename:
            f = open(filename, 'r')
            mainTabs = xml.dom.minidom.parse(f)
            f.close() 
        
        if fileText:
            mainTabs = xml.dom.minidom.parseString(fileText)
        
        version = self.getXMLText(mainTabs.getElementsByTagName('Version')[0].childNodes)
        if self.version not in version:
            print 'Warning, this widget does not work with your current version.  Please update!!'
            return
        try:
            repository = self.getXMLText(mainTabs.getElementsByTagName('Repository')[0].childNodes)
        except:
            repository = 'http://r-orange.googlecode.com/svn/'
            
        packageName = self.getXMLText(mainTabs.getElementsByTagName('PackageName')[0].childNodes)
        ### make the package directoryNames
        if not os.path.exists(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName)):
            dirs = [packageName, 
            os.path.join(packageName,'widgets'),
            os.path.join(packageName,'qtWidgets'),
            os.path.join(packageName,'signalClasses'),
            os.path.join(packageName,'icons'),
            os.path.join(packageName,'doc'),
            os.path.join(packageName,'schemas'), 
            os.path.join(packageName, 'templates')]
            for d in dirs: 
                if not os.path.exists(os.path.join(redREnviron.directoryNames['libraryDir'], d)):
                    os.mkdir(os.path.join(redREnviron.directoryNames['libraryDir'], d))
                    sys.path.insert(0, d)
            
        dependencies = self.getXMLText(mainTabs.getElementsByTagName('Dependencies')[0].childNodes)
        for dep in dependencies.split(','):
            dep = dep.strip(' /')
            if not os.path.exists(os.path.split(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, dep))[0]):
                os.mkdir(os.path.split(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, dep))[0])
            if (not os.path.isfile(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, dep)) and dep != 'None') or (force and dep != 'None'):
                print 'Downloading dependencies', dep
                if '.rrp' in dep:  # this is requiring a package so we need to go and get that
                    fileExt = os.path.split(dep)[1]
                    newPackage = os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, dep)
                    if not os.path.isfile(newPackage):
                        os.mkdir(os.path.split(newPackage)[0])
                    self.urlOpener.retrieve(repository+self.version+'/libraries/'+packageName+'/'+dep, newPackage)                    
                    self.loadRRW(newPackage)
                else:
                    newPackage = os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, dep)
                    if not os.path.exists(os.path.split(newPackage)[0]):
                        os.mkdir(os.path.split(newPackage)[0])
                    self.urlOpener.retrieve(repository+self.version+'/libraries/'+packageName+'/'+dep, newPackage)
                    #self.loadRRW(newPackage)
                    ### go to website, get the file, and repleat this process until success
                
        ## write the file, if there is one, to the file dir.
        fileDirName = self.getXMLText(mainTabs.getElementsByTagName('FileDirectoryStucture')[0].childNodes)
        code = mainTabs.getElementsByTagName('FileData')[0]
        code = code.toxml()
        code = code.strip('</FileData>')
        code = code.replace('&quot;', '\"')
        
        newFileDirectory = os.path.join(str(self.canvasDlg.redRDir), str(fileDirName.strip('/')))
        print newFileDirectory
        print str(self.canvasDlg.redRDir)
        print str(fileDirName.strip('/'))
        file = open(newFileDirectory, "wt")
        file.write(code)
        file.close()
        ## Done writing the file
        
        ## update the tags heitarchy
        # t = open(os.path.join(self.canvasDlg.redRDir, 'tagsSystem', 'tags.xml'), 'r')
        # mainTagsTabs = xml.dom.minidom.parse(t)
        # tags = mainTagsTabs.childNodes[0]
        # t.close()
        
        newTags = mainTabs.getElementsByTagName('menuTags')[0].childNodes
        
        for tag in newTags:
            if tag.nodeName == 'group': #picked a group element
                self.addTagsSystemTag(tag)
            # the tag is a structure is XML itself so we should add the xml if we don't find the right tab
            
        # file = open(os.path.join(self.canvasDlg.redRDir, 'tagsSystem', 'tags.xml'), 'wt')
        # file.write(tags.toxml())
        # file.close()
        # get the examples if there are anything
        examples = self.getXMLText(mainTabs.getElementsByTagName('Examples')[0].childNodes)
        for example in examples.split(','):
            example = example.strip(' ')
            if (not os.path.isfile(os.path.join(self.canvasDlg.redRDir,example)) and example != 'None')or (force and example != 'None'):
                if not os.path.exists(os.path.split(os.path.join(self.canvasDlg.redRDir,example))[0]):
                    os.mkdir(os.path.split(os.path.join(self.canvasDlg.redRDir,example))[0])
                print 'Downloading example file', example
                fileExt = os.path.split(example)[1]
                newExample = os.path.join(self.canvasDlg.redRDir, example)
                self.urlOpener.retrieve(repository+self.version+'/'+example, newExample)
                
        ## update tage; read in the tags, look for the tag heirarchy in your file; follow the tag heirarchy down the tags file, when you run out of decendents add the rest of the tags section to the tags file and save the whole thing as xml.
        if fileText or '.rpp' in filename:
            if not os.path.exists(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, packageName+'.rrp')):  # don't replace this if we already have it.
                rppFile = open(os.path.join(self.canvasDlg.redRDir, 'libraries', packageName, packageName+'.rrp'), 'wt')
                rppFile.write(mainTabs.toxml())
                rppFile.close()
        if filename != None and '.rrp' not in filename:
            os.remove(filename)
        print 'Package loaded successfully'
        self.canvasDlg.reloadWidgets()
    def addTagsSystemTag(self, tag):
        # tags is the current tags system, tag is the tag that should be added.
        name = str(tag.getAttribute('name'))
        # move through the group tags in tags, if you find the grouname of tag then you don't need to add it, rather just add the child tags to that tag.
        tags = self.tags.childNodes[0]
        #print tags.childNodes, 'Child Nodes'
        for t in tags.childNodes:
            if t.nodeName == 'group':
                #print t
                if str(t.getAttribute('name')) == name: ## found the right tag
                    #print 'Found the name'
                    #print t.childNodes
                    for tt in tag.childNodes:
                        if tt.nodeName == 'group':
                            self.addTagsSystemTag(t, tt) # add the child tags
                            
                    return
                    
        ## if we made it this far we didn't find the right tag so we need to add all of the tag xml to the tags xml
        print 'Name not found, appending to group.  This is normal, dont be worried.'
        tags.appendChild(tag)
        self.tags.childNodes[0] = tags
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
        
        canvasPicsDir  = os.path.join(self.canvasDlg.canvasDir, "icons")
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

        # GUI
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
            if not issubclass(outInstance.getOutputType(outS.name), outType): continue
            for inS in inputs:
                if inInstance.getOutputType(inS.name) == None: continue  # ignore if some signals don't exist any more, since we will report error somewhere else
                if not issubclass(inType, inInstance.getInputType(inS.name)): continue
                if issubclass(outInstance.getOutputType(outS.name), inInstance.getInputType(inS.name)): count+= 1

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
                if inType == None:
                    continue        #print "Unable to find signal type for signal %s. Check the definition of the widget." % (inS.name)
                if issubclass(outType, inType):
                        possibleLinks.append((outS.name, inS.name))
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

        pl1 = self.getPossibleConnections(majorOutputs, majorInputs)
        pl2 = self.getPossibleConnections(majorOutputs, minorInputs)
        pl3 = self.getPossibleConnections(minorOutputs, majorInputs)
        pl4 = self.getPossibleConnections(minorOutputs, minorInputs)

        all = pl1 + pl2 + pl3 + pl4

        if not all: return 0

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
        return len(all) > 0

    def addLink(self, outName, inName):
        if (outName, inName) in self._links: return 1

        # check if correct types
        outType = self.outWidget.instance.getOutputType(outName)
        inType = self.inWidget.instance.getInputType(inName)
        if not issubclass(outType, inType): return 0

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


