# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington and Anup Parikh
# Description:
#    document class - main operations (save, load, ...)
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os, os.path, traceback, log
from xml.dom.minidom import Document, parse
import xml.dom.minidom
import orngView, orngCanvasItems, orngTabs
from orngDlgs import *
import RSession, globalData, redRPackageManager, redRHistory
from orngSignalManager import SignalManager, SignalDialog
import cPickle, math, orngHistory, zipfile, urllib, sip, redRObjects, redRSaveLoad
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
from libraries.base.qtWidgets.splitter import splitter as redRSplitter
#import pprint, 
# pp = pprint.PrettyPrinter(indent=4)

class SchemaDoc(QWidget):
    def __init__(self, canvasDlg, *args):
        QWidget.__init__(self, *args)
        self.canvasDlg = canvasDlg
        self.ctrlPressed = 0
        self.version = 'trunk'                  # should be changed before making the installer or when moving to a new branch.
        #self.lines = []                         # list of orngCanvasItems.CanvasLine items
        #self.widgets = []                       # list of orngCanvasItems.CanvasWidget items
        self.signalManager = SignalManager()    # signal manager to correctly process signals

        self.sessionID = 0
        self.schemaPath = redREnviron.settings["saveSchemaDir"]
        self.schemaName = ""
        
        self.loadedSettingsDict = {}
        self.setLayout(QHBoxLayout())
        self.splitter = redRSplitter(self)
        left = self.splitter.widgetArea()
        self.tabsWidget = QTabWidget()
        QObject.connect(self.tabsWidget, SIGNAL('currentChanged(int)'), self.resetActiveTab)
        left.layout().addWidget(self.tabsWidget)
        #self.canvas = QGraphicsScene(0,0,2000,2000)
        right = self.splitter.widgetArea()
        self.notes = redRTextEdit(right, label = 'Notes')
        self.instances = {}
        self.makeSchemaTab('General')
        
        self.layout().setMargin(0)
        self.schemaID = orngHistory.logNewSchema()
        self.RVariableRemoveSupress = 0
        self.urlOpener = urllib.FancyURLopener()
    def resetActiveTab(self, int):
        self.setActiveTab(str(self.tabsWidget.tabText(int)))
    def setActiveTab(self, tabname):
        redRObjects.setActiveTab(tabname)
    def widgets(self):
        wlist = []
        rolist = redRObjects.getIconsByTab()
        for k, l in rolist.items():
            wlist += l
        return wlist
    def lines(self):
        llist = []
        rolist = redRObjects.getLinesByTab()
        for k, l in rolist.items():
            llist += l
        return llist
    def widgetIcons(self, tab):  # moving to redrObjects / moved
        return redRObjects.getIconsByTab(tab)
        # icons = []
        # for w in self.widgets:
            # if w.tab == tab:
                # icons.append(w)
        # return icons
    def widgetLines(self, tab): # moving to redrObjects / moved
        return redRObjects.getLinesByTab(tab)
        # lines = []
        # for l in self.lines:
            # if l.tab == tab:
                # lines.append(l)
        # return lines
    def activeTab(self): # part of the view
        return redRObjects.activeTab()
    def activeTabName(self):    # part of the view
        return str(self.tabsWidget.tabText(self.tabsWidget.currentIndex()))
    def activeCanvas(self):     # part of the view
        return redRObjects.activeCanvas() # self.canvas[str(self.tabsWidget.tabText(self.tabsWidget.currentIndex()))]
    def setTabActive(self, name):   # part of the view
        for i in range(self.tabsWidget.count()):
            if str(self.tabsWidget.tabText(i)) == name:
                self.tabsWidget.setCurrentIndex(i)
                break
        
    def makeSchemaTab(self, tabname):   # part of the view
        log.log(1, 1, 3, 'making new tab %s' % tabname)
        if tabname in redRObjects.tabNames():
            self.setTabActive(tabname)
            return
        redRObjects.setActiveTab(tabname)
        self.tabsWidget.addTab(redRObjects.makeTabView(tabname, self), tabname)
    def removeCurrentTab(self):
        mb = QMessageBox("Remove Current Tab", "Are you sure that you want to remove the current tab?\n\nAny widgets that have not been cloned will be lost!!!", 
            QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
            QMessageBox.No | QMessageBox.Escape, QMessageBox.NoButton)
        if mb.exec_() == QMessageBox.Ok:
            self.removeSchemaTab(redRObjects.activeTabName())
    def removeSchemaTab(self, tabname):
        # set the tab in question to the active tab, this will set the current tab index so we can remove easily.
        self.setTabActive(tabname)
        
        ## first we need to clear all of the widgets from the tab
        
        widgets = redRObjects.getIconsByTab(tabname)[tabname]
        for w in widgets:
            self.removeWidget(w)
        ## next find the index
        i = self.tabsWidget.currentIndex()
        ## remove the widget
        if tabname != 'General':  ## General tab is a special case, this will always be present.
            self.tabsWidget.removeTab(i)
            ## remove the references to the tab in the redRObjects
            redRObjects.removeSchemaTab(tabname)
    def showAllWidgets(self): # move to redRObjects
        redRObjects.showAllWidgets()
    def closeAllWidgets(self):   # move to redRObjects
        redRObjects.closeAllWidgets()
    def selectAllWidgets(self):
        self.activeTab().selectAllWidgets()
    # add line connecting widgets outWidget and inWidget
    # if necessary ask which signals to connect
    def addLine(self, outWidget, inWidget, enabled = True, process = True, ghost = False):  # adds the signal link between the data and instantiates the line on the canvas.  move to the signal manager or the view?
        log.log(1, 1, 3, '############ ADDING LINE ##################</br></br>%s, %s, %s' % (outWidget, inWidget, process))
        if outWidget == inWidget: 
            
            raise Exception, 'Same Widget'
        # check if line already exists
        line = self.getLine(outWidget, inWidget)
        if line:
            self.resetActiveSignals(outWidget, inWidget, None, enabled)
            return line
        canConnect = inWidget.instance().inputs.matchConnections(outWidget.instance().outputs)
        
        if not canConnect:
            mb = QMessageBox("Failed to Connect", "Connection Not Possible\n\nWould you like to search for templates\nwith these widgets?", 
                QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                QMessageBox.No | QMessageBox.Escape, QMessageBox.NoButton)
            if mb.exec_() == QMessageBox.Ok:
                ## go to the website and see if there are templates with the widgets in question
                import webbrowser
                url = 'http://www.red-r.org/?s='+outWidget.widgetInfo.name+'+'+inWidget.widgetInfo.name
                
                webbrowser.open(url)
                
            
            return None

        if process != False:
            
            dialog = SignalDialog(self.canvasDlg, None)
            dialog.setOutInWidgets(outWidget, inWidget)

            # if there are multiple choices, how to connect this two widget, then show the dialog
        
            possibleConnections = inWidget.instance().inputs.getPossibleConnections(outWidget.instance().outputs)  #  .getConnections(outWidget, inWidget)
            if len(possibleConnections) > 1:
                #print possibleConnections
                #dialog.addLink(possibleConnections[0][0], possibleConnections[0][1])  # add a link between the best signals.
                if dialog.exec_() == QDialog.Rejected:
                    return None
                possibleConnections = dialog.getLinks()
            

            #self.signalManager.setFreeze(1)
            
            for (outName, inName) in possibleConnections:
                
                self.addLink(outWidget, inWidget, outName, inName, enabled, process = process)

        #self.signalManager.setFreeze(0, outWidget.instance)

        # if signals were set correctly create the line, update widget tooltips and show the line
        line = self.getLine(outWidget, inWidget)
        if line:
            outWidget.updateTooltip()
            inWidget.updateTooltip()
            
        
        return line


    # reset signals of an already created line
    def resetActiveSignals(self, outWidget, inWidget, newSignals = None, enabled = 1):
        #print "<extra>orngDoc.py - resetActiveSignals() - ", outWidget, inWidget, newSignals
        signals = []
        for line in self.lines():
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

        #self.signalManager.setFreeze(1)
        for (outName, inName) in newSignals:
            if (outName, inName) not in signals:
                self.addLink(outWidget, inWidget, outName, inName, enabled)
        #self.signalManager.setFreeze(0, outWidget.instance)

        outWidget.updateTooltip()
        inWidget.updateTooltip()

    # add one link (signal) from outWidget to inWidget. if line doesn't exist yet, we create it
    def addLink(self, outWidget, inWidget, outSignalName, inSignalName, enabled = 1, fireSignal = 1, process = True, loading = False):
        ## addLink should move through all of the icons on all canvases and check if there are icons which are clones of the outWidget and inWidget
        ## after this lines should be created between those widgets and the lines should be set to enabled and data.
        
        if inWidget.instance().inputs.getSignal(inSignalName):
            if not inWidget.instance().inputs.getSignal(inSignalName)['multiple']:
                ## check existing link to the input signal
                
                existing = inWidget.instance().inputs.getLinks(inSignalName)
                for l in existing:
                    l['parent'].outputs.removeSignal(inWidget.instance().inputs.getSignal(inSignalName), l['sid'])
                    redRObjects.removeLine(l['parent'], inWidget.instance(), l['sid'], inSignalName)
        
        
        lines = redRObjects.addLine(outWidget.instance(), inWidget.instance(), outSignalName, inSignalName, doc = self, enabled = enabled, process = False, loading = loading)
        
        
        ok = outWidget.instance().outputs.connectSignal(inWidget.instance().inputs.getSignal(inSignalName), outSignalName, process = process)#    self.signalManager.addLink(outWidget, inWidget, outSignalName, inSignalName, enabled)
        if not ok and not loading:
            #remove the lines
            redRObjects.removeLine(outWidget.instance(), inWidget.instance(), outSignalName, inSignalName)
            ## we should change this to a dialog so that the user can connect the signals manually if need be.
            QMessageBox.information( self, "Red-R Canvas", "Unable to add link. Something is really wrong; try restarting Red-R Canvas.", QMessageBox.Ok + QMessageBox.Default )
            

            return 0
        elif not ok:
            return 0
        else:
            return 1
    """
        if outWidget.instance().outputs.getSignal(outSignalName) in inWidget.instance().inputs.getLinks(inSignalName): return ## the link already exists
            
        
        if inWidget.instance().inputs.getSignal(inSignalName):
            if not inWidget.instance().inputs.getSignal(inSignalName)['multiple']:
                ## check existing link to the input signal
                
                existing = inWidget.instance().inputs.getLinks(inSignalName)
                for l in existing:
                    l['parent'].outputs.removeSignal(inWidget.instance().inputs.getSignal(inSignalName), l['sid'])
                    self.removeLink(self.getWidgetByInstance(l['parent']), inWidget, l['sid'], inSignalName)
                
        line = self.getLine(outWidget, inWidget)
        if not line:
            line = orngCanvasItems.CanvasLine(self.signalManager, self.canvasDlg, self.activeTab(), outWidget, inWidget, self.activeCanvas(), self.activeTabName())
            self.lines.append(line)
            if enabled:
                line.setEnabled(1)
            else:
                line.setEnabled(0)
            line.show()
            outWidget.addOutLine(line)
            outWidget.updateTooltip()
            inWidget.addInLine(line)
            inWidget.updateTooltip()
        
        ok = outWidget.instance().outputs.connectSignal(inWidget.instance().inputs.getSignal(inSignalName), outSignalName, process = process)#    self.signalManager.addLink(outWidget, inWidget, outSignalName, inSignalName, enabled)
        if not ok and not loading:
            self.removeLink(outWidget, inWidget, outSignalName, inSignalName)
            ## we should change this to a dialog so that the user can connect the signals manually if need be.
            QMessageBox.information( self, "Red-R Canvas", "Unable to add link. Something is really wrong; try restarting Red-R Canvas.", QMessageBox.Ok + QMessageBox.Default )
            

            return 0
        elif not ok:
            return 0
        # else:
            # orngHistory.logAddLink(self.schemaID, outWidget, inWidget, outSignalName)
        line.updateTooltip()
        
        import redRHistory
        redRHistory.addConnectionHistory(outWidget, inWidget)
        redRHistory.saveConnectionHistory()
        return 1
        """
    def addLink175(self, outWidget, inWidget, outSignalName, inSignalName, enabled = 1, fireSignal = 1, process = False, loading = False):
        ## compatibility layer for older schemas on changing signal classes.  this is actually a good way to allow for full compatibility between versions.

        ## this is where we have a diversion from the normal loading.  obviously if we made it to here there aren't the signal names in the in or out widgets that match.
        ##      we will open a dialog and show the names of the signals and ask the user to connect them
        dialog = SignalDialog(self.canvasDlg, None)
        from libraries.base.qtWidgets.widgetLabel import widgetLabel
        widgetLabel(dialog, 'Please connect the signals that best match these: %s to %s' % (outSignalName, inSignalName)) 
        dialog.setOutInWidgets(outWidget, inWidget)

        # if there are multiple choices, how to connect this two widget, then show the dialog
    
        possibleConnections = inWidget.instance().inputs.getPossibleConnections(outWidget.instance().outputs)  #  .getConnections(outWidget, inWidget)
        if len(possibleConnections) > 1:
            #print possibleConnections
            #dialog.addLink(possibleConnections[0][0], possibleConnections[0][1])  # add a link between the best signals.
            if dialog.exec_() == QDialog.Rejected:
                return None
            possibleConnections = dialog.getLinks()
        

        #self.signalManager.setFreeze(1)
        for (outName, inName) in possibleConnections:
            
            self.addLink(outWidget, inWidget, outName, inName, enabled, process = False)  # under no circumstance will we process an old signal again.
        
    ### moved to redRObjects
    # remove only one signal from connected two widgets. If no signals are left, delete the line
    def removeLink(self, outWidget, inWidget, outSignalName, inSignalName):
        outWidget.outputs.removeSignal(inWidgetInstance.inputs.getSignal(inSignalName), outSignalName)
    
        if not outWidget.outputs.signalLinkExists(inWidgetInstance): ## move through all of the icons and remove all lines connecting, only do this if there is no more signal.
            return redRObjects.removeLine(outWidget, inWidget, outSignalName, inSignalName)
    """ ##Depricated removelink functionality
            #print "<extra> orngDoc.py - removeLink() - ", outWidget, inWidget, outSignalName, inSignalName
            outWidget.instance().outputs.removeSignal(inWidget.instance().inputs.getSignal(inSignalName), outSignalName)

            if not outWidget.instance().outputs.signalLinkExists(inWidget.instance):
                self.removeLine(outWidget, inWidget)

            #self.saveTempDoc()


        # remove line line
        def removeLine1(self, line):
            #print 'removing a line from' + str(outName) +'to' +str(inName)
            
            ## remove the signal by sending None through the channel
            print '##########  SEND NONE ###############'
            obsoleteSignals = line.outWidget.instance().outputs.getSignalLinks(line.inWidget.instance)
            for (s, id) in obsoleteSignals:
                signal = line.inWidget.instance().inputs.getSignal(id)
                line.outWidget.instance().outputs.removeSignal(signal, s)
            print '##########  REMOVE LINE #############'
            
            # print linksIn
            # for key in linksIn.keys():
                # print linksIn[key], 'linksIn[key]'
                # for i in range(len(linksIn[key])):
                    # if line.outWidget.instance == linksIn[key][i][1]:
                        # try:
                            # linksIn[key][i][2](None, linksIn[key][i][1].widgetID)
                        # except:
                            # linksIn[key][i][2](None)
            
            # remove the image of the line
            # for (outName, inName) in line.getSignals():
                # self.signalManager.removeLink(line.outWidget.instance, line.inWidget.instance, outName, inName)   # update SignalManager
            self.lines.remove(line)
            line.inWidget.removeLine(line)
            line.outWidget.removeLine(line)
            line.inWidget.updateTooltip()
            line.outWidget.updateTooltip()
            line.remove()
            #self.saveTempDoc()

        # remove line, connecting two widgets
        def removeLine(self, outWidget, inWidget):

            line = self.getLine(outWidget, inWidget)
            if line:
                self.removeLine1(line)
                
            
        """
    """ ##Depricated ghost functionality
        def addGhostWidgetsForWidget(self, newwidget):
            #return []
            if newwidget.instance().outputs != []:
                try:
                    print newwidget.widgetInfo.fileName
                    ## add the chost widgets to the canvas and attach ghost lines to them
                    
                    topCons = redRHistory.getTopConnections(newwidget)
                    print topCons
                    widgets = []
                    off = [150, 50, -50, -150]
                    i = 0
                    for con in topCons:
                        print con
                        ## con is the fileName of the widget we need to find the info from the filename
                        
                        wInfo = redRObjects.widgetRegistry()['widgets'][con]
                        
                        
                        widgets.append(self.addGhostWidget(wInfo, x = newwidget.x() + 150, y = newwidget.y() + off[i], creatingWidget = newwidget)) # add the ghost widget
                        #self.addLine(newwidget, widgets[-1], ghost = True)
                        i += 1
                except: 
                    type, val, traceback = sys.exc_info()
                    sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas           
                    widgets = []
                return widgets
        """
    def getSuggestWidgets(self, newwidget):
        topCons = redRHistory.getTopConnections(newwidget)
        actions = []
        for con in topCons:
            try:
                wInfo = redRObjects.widgetRegistry()['widgets'][con]
                newAct = QTreeWidgetItem([wInfo.name])
                newAct.setIcon(0, QIcon(wInfo.icon))
                newAct.widgetInfo = wInfo
                actions.append(newAct)
            except:
                continue
        return actions
    """ ## Depricated Ghost functionality
        def killGhost(self, widget): # remove the ghost widgets
            self.removeWidget(widget)
        # add new ghost widget
        def addGhostWidget(self, widgetInfo, x= -1, y=-1, caption = '', widgetSettings = None, saveTempDoc = True, creatingWidget = None):
            qApp.setOverrideCursor(Qt.WaitCursor)
            
            ## add the ghost widget to the canvas
            newGhostWidget = orngCanvasItems.GhostWidget(self.signalManager, self.activeCanvas(), self.activeTab(), widgetInfo, self.canvasDlg.defaultPic, self.canvasDlg, widgetSettings, creatingWidget = creatingWidget)
            
            ## resolve collisions
            self.resolveCollisions(newGhostWidget, x, y)
            
            ## set the caption and add the new widget to the list of widgets
            if caption == "": caption = newGhostWidget.caption

            if self.getWidgetByCaption(caption):
                i = 2
                while self.getWidgetByCaption(caption + " (" + str(i) + ")"): i+=1
                caption = caption + " (" + str(i) + ")"
            newGhostWidget.updateText(caption)
            newGhostWidget.caption = caption
            

            self.widgets.append(newGhostWidget)
            self.activeCanvas().update()
            # show the widget and activate the settings
            try:
                #self.signalManager.addWidget(newGhostWidget.instance)
                newGhostWidget.show()
                newGhostWidget.updateTooltip()
                newGhostWidget.setProcessing(0)
                orngHistory.logAddWidget(self.schemaID, id(newGhostWidget), (newGhostWidget.widgetInfo.packageName, newGhostWidget.widgetInfo.name), newGhostWidget.x(), newGhostWidget.y())
            except:
                type, val, traceback = sys.exc_info()
                sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas

            qApp.restoreOverrideCursor()
            return newGhostWidget  # now the ghost widgets are ready to be used.  To activate we just click them and make them permanent.  So we need a new setting (ghost and non ghost)
        # add new widget
        """
    def newTab(self): # part of the view
        td = NewTabDialog(self.canvasDlg)
        if td.exec_() != QDialog.Rejected:
            if str(td.tabName.text()) == "": return
            self.makeSchemaTab(str(td.tabName.text()))
            self.setTabActive(str(td.tabName.text()))
    def cloneToTab(self):   # part of the view
        tempWidgets = self.activeTab().getSelectedWidgets()
        td = CloneTabDialog(self.canvasDlg)
        if td.exec_() == QDialog.Rejected: return ## nothing interesting to do
        try:
            tabName = str(td.tabList.selectedItems()[0].text())
        except: return 
        if tabName == str(self.tabsWidget.tabText(self.tabsWidget.currentIndex())): return # can't allow two of the same widget on a tab.
        for w in tempWidgets:
            log.log(1, 2, 3, 'Creating clone widget %s in tab %s' % ( w.caption + ' (Clone)', tabName))
            self.cloneWidget(w, tabName, caption = w.caption + ' (Clone)')
        self.setTabActive(tabName) ## set the new tab as active so the user knows something happened.
    def cloneWidget(self, widget, viewID = None, x= -1, y=-1, caption = "", widgetSettings = None, saveTempDoc = True):
        ## we want to clone the widget.  This involves moving to the correct view and placing the icon on the canvas but setting the instance to be the same as the widget instance on the other widget.
        self.setTabActive(viewID)
        qApp.setOverrideCursor(Qt.WaitCursor)
        try:
            newwidget = redRObjects.newIcon(self.signalManager, self.activeCanvas(), self.activeTab(), widget.widgetInfo, self.canvasDlg.defaultPic, self.canvasDlg, instanceID = widget.instance().widgetID, tabName = self.activeTabName()) ## set the new orngCanvasItems.CanvasWidget, this item contains the instance!!!
            #if widgetInfo.name == 'dummy' and (forceInSignals or forceOutSignals):
            #print newwidget
        except:
            type, val, traceback = sys.exc_info()
            log.log(1, 9, 1, str(traceback))
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas
            qApp.restoreOverrideCursor()
            return None

        self.resolveCollisions(newwidget, x, y)
            
        #self.canvasView.ensureVisible(newwidget)

        if caption == "":
            caption = widget.caption + ' (Clone)'
        newwidget.updateText(caption)
        ##self.widgets.append(newwidget)
        # if saveTempDoc:
            # self.saveTempDoc()
        self.activeCanvas().update()

        # show the widget and activate the settings
        try:
            self.signalManager.addWidget(newwidget.instance())
            newwidget.show()
            newwidget.updateTooltip()
            newwidget.setProcessing(1)
            # if redREnviron.settings["saveWidgetsPosition"]:
                # newwidget.instance().restoreWidgetPosition()
            newwidget.setProcessing(0)
            orngHistory.logAddWidget(self.schemaID, id(newwidget), (newwidget.widgetInfo.packageName, newwidget.widgetInfo.name), newwidget.x(), newwidget.y())
        except:
            type, val, traceback = sys.exc_info()
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas

        ### add lines to widgets on the current active tab if there is a link from the widget in question to one of the other widgets on the canvas.
        print 'Adding lines'
        tabWidgets = redRObjects.getIconsByTab(redRObjects.activeTabName())[redRObjects.activeTabName()]
        for tw in tabWidgets: ## tw is a list of icons on the current tab (the only one we care about)
            
            lw = tw.instance().outputs.linkingWidgets()  ## lw is a list of instances that are linked to the instance of the tw icon.  
            
            if tw == newwidget: ## found the widget so we need to look at the connections made by this widget to others.
                for tw2 in tabWidgets:
                    
                    if tw2.instance() in lw: ## there is a link so we make a line.
                        line = redRObjects.getLine(tw, tw2)
                        line2 = redRObjects.addCanvasLine(tw, tw2, self, line.getEnabled())
                        line2.setNoData(line.noData)
            else:
                
                if newwidget.instance() in lw:
                    line = redRObjects.getLine(tw, newwidget)
                    line2 = redRObjects.addCanvasLine(tw, newwidget, self, line.getEnabled())
                    line2.setNoData(line.noData)
        qApp.restoreOverrideCursor()
        return newwidget
 
    #def addWidgetInstance(self, name, inputs = None, outputs = None, widgetID = None):
    def addWidgetIcon(self, widgetInfo, instanceID):
        newwidget = redRObjects.newIcon(self.signalManager, self.activeCanvas(), self.activeTab(), widgetInfo, self.canvasDlg.defaultPic, self.canvasDlg, instanceID =  instanceID, tabName = self.activeTabName())## set the new orngCanvasItems.CanvasWidget
        #if self.getWidgetByCaption(newwidget.caption):
        caption = newwidget.caption
        i = 1
        while self.getWidgetByCaption(caption + " (" + str(i) + ")"): i+=1
        caption = caption + " (" + str(i) + ")"
        log.log(1, 2, 2, 'Set widget caption to %s' % caption)
        newwidget.updateText(caption)
        ##self.widgets.append(newwidget)
        return newwidget
    def addWidget(self, widgetInfo, x= -1, y=-1, caption = "", widgetSettings = None, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        qApp.setOverrideCursor(Qt.WaitCursor)
        try:
            instanceID = self.addInstance(self.signalManager, widgetInfo, widgetSettings, forceInSignals, forceOutSignals)
            newwidget = self.addWidgetIcon(widgetInfo, instanceID)
            #if widgetInfo.name == 'dummy' and (forceInSignals or forceOutSignals):
            log.log(1, 9, 3, 'New Widget Created %s' % newwidget)
        except:
            type, val, traceback = sys.exc_info()
            log.log(1, 9, 1, str(traceback))
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas
            qApp.restoreOverrideCursor()
            return None

        self.resolveCollisions(newwidget, x, y)
            
        #self.canvasView.ensureVisible(newwidget)
        # print 'setting widget caption', caption
        # if caption == "": 
            # caption = newwidget.caption
            # print 'caption now set to ', caption
            # if self.getWidgetByCaption(caption):
                # i = 2
                # while self.getWidgetByCaption(caption + " (" + str(i) + ")"): i+=1
                # caption = caption + " (" + str(i) + ")"
                # print 'caption now set to ', caption
            # newwidget.updateText(caption)
        newwidget.instance().setWindowTitle(caption)
        

        
        # if saveTempDoc:
            # self.saveTempDoc()
        self.activeCanvas().update()

        # show the widget and activate the settings
        try:
            self.signalManager.addWidget(newwidget.instance())
            newwidget.show()
            newwidget.updateTooltip()
            newwidget.setProcessing(1)
            # if redREnviron.settings["saveWidgetsPosition"]:
                # newwidget.instance().restoreWidgetPosition()
            newwidget.setProcessing(0)
            orngHistory.logAddWidget(self.schemaID, id(newwidget), (newwidget.widgetInfo.packageName, newwidget.widgetInfo.name), newwidget.x(), newwidget.y())
        except:
            type, val, traceback = sys.exc_info()
            sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas

            
        ## try to set up the ghost widgets
        qApp.restoreOverrideCursor()
        return newwidget
    def addInstance(self, signalManager, widgetInfo, widgetSettings = None, forceInSignals = None, forceOutSignals = None, id = None):
        return redRObjects.addInstance(signalManager, widgetInfo, settings = widgetSettings, insig = forceInSignals, outsig = forceOutSignals, id = id)
        """
            print 'adding instance'
            m = __import__(widgetInfo.fileName)
            #m = __import__('libraries.' + widgetInfo.packageName + '.widgets.' + widgetInfo.widgetName)
            
            instance = m.__dict__[widgetInfo.widgetName].__new__(m.__dict__[widgetInfo.widgetName],
            _owInfo = redREnviron.settings["owInfo"],
            _owWarning = redREnviron.settings["owWarning"],
            _owError = redREnviron.settings["owError"],
            _owShowStatus = redREnviron.settings["owShow"],
            _packageName = widgetInfo.packageName)
            instance.__dict__['_widgetInfo'] = widgetInfo
            
            if widgetInfo.name == 'Dummy': 
                print 'Loading dummy step 3'
                instance.__init__(signalManager = signalManager,
                forceInSignals = forceInSignals, forceOutSignals = forceOutSignals)
            else: instance.__init__(signalManager = signalManager)
            
            instance.loadGlobalSettings()
            if widgetSettings:
                instance.setSettings(widgetSettings)
                if '_customSettings' in widgetSettings.keys():
                    instance.loadCustomSettings(widgetSettings['_customSettings'])
                else:
                    instance.loadCustomSettings(widgetSettings)

            instance.setProgressBarHandler(self.activeTab().progressBarHandler)   # set progress bar event handler
            instance.setProcessingHandler(self.activeTab().processingHandler)
            #instance.setWidgetStateHandler(self.updateWidgetState)
            instance.setEventHandler(self.canvasDlg.output.widgetEvents)
            instance.setWidgetWindowIcon(widgetInfo.icon)
            instance.canvasWidget = self
            instance.widgetInfo = widgetInfo
            print 'adding instance'
            self.instances[instance.widgetID] = instance
            
            return instance.widgetID
            """
    def returnInstance(self, id):
        return redRObjects.getWidgetInstanceByID(id)
    def resolveCollisions(self, newwidget, x, y):
        if x==-1 or y==-1:
            if self.activeTab().getSelectedWidgets():
                x = self.activeTab().getSelectedWidgets()[-1].x() + 110
                y = self.activeTab().getSelectedWidgets()[-1].y()
            elif self.widgets() != []:
                x = self.widgets()[-1].x() + 110  # change to selected widget 
                y = self.widgets()[-1].y()
            else:
                x = 30
                y = 50
        newwidget.setCoords(x, y)
        # move the widget to a valid position if necessary
        invalidPosition = (self.activeTab().findItemTypeCount(self.activeCanvas().collidingItems(newwidget), orngCanvasItems.CanvasWidget) > 0)
        if invalidPosition:
            for r in range(20, 200, 20):
                for fi in [90, -90, 180, 0, 45, -45, 135, -135]:
                    xOff = r * math.cos(math.radians(fi))
                    yOff = r * math.sin(math.radians(fi))
                    rect = QRectF(x+xOff, y+yOff, 48, 48)
                    invalidPosition = self.activeTab().findItemTypeCount(self.activeCanvas().items(rect), orngCanvasItems.CanvasWidget) > 0
                    if not invalidPosition:
                        newwidget.setCoords(x+xOff, y+yOff)
                        break
                if not invalidPosition:
                    break
    
    def instanceStillWithIcon(self, instanceID):
        for widget in self.widgets():
            
            if widget.instanceID == instanceID:
                return True
        return False
    # remove widget
    def removeWidget(self, widget, saveTempDoc = True):
        if not widget:
            
            return
        instanceID = widget.instanceID
        #widget.closing = close
        while widget.inLines != []: redRObjects.removeLineInstance(widget.inLines[0])
        while widget.outLines != []:  redRObjects.removeLineInstance(widget.outLines[0])

        try:
            #self.signalManager.removeWidget(widget.instance()) # sending occurs before this point
            
            widget.remove() ## here we need to check if others have the widget instance.
            if widget in self.widgets():
                redRObjects.removeWidgetIcon(widget)
        except:
            import redRExceptionHandling
            log.log(1, 9, 1, redRExceptionHandling.formatException())
        if not self.instanceStillWithIcon(instanceID):
            redRObjects.removeWidgetInstanceByID(instanceID)
    def clear(self):
        self.canvasDlg.setCaption()
        for t in redRObjects.tabNames():
            #if t == 'General': continue
            self.removeSchemaTab(t)
        RSession.Rcommand('rm(list = ls())')
        #self.activeCanvas().update()
        scenes = redRObjects.scenes()
        for s in scenes:
            s.update()
        self.schemaName = ""
        #self.saveTempDoc()
        

    def enableAllLines(self):
        for k, line in redRObjects.lines().items():
            self.signalManager.setLinkEnabled(line.outWidget.instance, line.inWidget.instance, 1)
            line.setEnabled(1)
            #line.repaintLine(self.canvasView)
        self.activeCanvas().update()

    def disableAllLines(self):
        for k, line in redRObjects.lines().items():
            self.signalManager.setLinkEnabled(line.outWidget.instance, line.inWidget.instance, 0)
            line.setEnabled(0)
            #line.repaintLine(self.canvasView)
        self.activeCanvas().update()

    # return a new widget instance of a widget with filename "widgetName"
    def addWidgetByFileName(self, widgetFileName, x, y, caption, widgetSettings=None, saveTempDoc = True, forceInSignals = None, forceOutSignals = None):
        try:
            if widgetFileName == 'base_dummy': print 'Loading dummy step 1a'
            widget = redRObjects.widgetRegistry()['widgets'][widgetFileName]
            return self.addWidget(widget, x, y, caption, widgetSettings, saveTempDoc, forceInSignals, forceOutSignals)
        except Exception as inst:
            log.log(1, 9, 1, 'Loading exception occured for widget '+widgetFileName)
            
            return None
    # addWidgetIconByFileName(name, x = xPos, y = yPos + addY, caption = caption, instance = instance) 
    def addWidgetIconByFileName(self, name, x= -1, y=-1, caption = "", instance = None):
        
        widget = redRObjects.widgetRegistry()['widgets'][name]
        newwidget = self.addWidgetIcon(widget, instance)
        self.resolveCollisions(newwidget, x, y)
        if caption == "": 
            caption = newwidget.caption
            if self.getWidgetByCaption(caption):
                i = 2
                while self.getWidgetByCaption(caption + " (" + str(i) + ")"): i+=1
                caption = caption + " (" + str(i) + ")"
            newwidget.updateText(caption)
        else:
            newwidget.updateText(caption)
    def addWidgetInstanceByFileName(self, name, settings = None, inputs = None, outputs = None, id = None):
        try:
            #if widgetFileName == 'base_dummy': print 'Loading dummy step 1a'
            widget = redRObjects.widgetRegistry()['widgets'][name]
            return self.addInstance(self.signalManager, widget, settings, inputs, outputs, id = id)
        except Exception as inst:
            log.log(1, 9, 1,  'Loading exception occured for widget '+name)
            
            return None
    # return the widget icon that has caption "widgetName"
    def getWidgetByCaption(self, widgetName):
        return redRObjects.getIconByIconCaption(widgetName)
    def getWidgetByInstance(self, instance):
        return redRObjects.getIconByIconInstanceRef(instance)
    def getWidgetByID(self, widgetID):
        return redRObjects.getIconByIconInstanceID(widgetID)
    def getWidgetByIDActiveTabOnly(self, widgetID):
        return redRObjects.getWidgetByIDActiveTabOnly(widgetID)
    def getWidgetCaption(self, widgetInstance):
        widget = redRObjects.getIconByIconInstanceRef(widgetInstance)
        if widget == None:
            log.log(1, 9, 1, "Error. Attempted to Access Invalid widget instance : ", widgetInstance)
            return ""
        return widget.caption

    # get line from outWidget to inWidget
    def getLine(self, outWidget, inWidget):
        return redRObjects.getLine(outWidget, inWidget)
    # find canvasItems from widget ID
    def findWidgetFromID(self, widgetID):
        return redRObjects.getIconByIconInstanceID()

    # find orngCanvasItems.CanvasWidget from widget instance
    def findWidgetFromInstance(self, widgetInstance):
        return redRObjects.getIconByIconInstanceRef(widgetInstance)
    def handleDirty(self, ow, iw, dirty):
        line = self.getLine(ow, iw)
        if not line or line == None:
            
            return
        line.dirty = dirty
        
        self.canvas.update()
    def handleNone(self, ow, iw, none):
        line = self.getLine(ow, iw)
        if line:
            line.noData = none
            log.log(1, 9, 3, 'Setting line %s noData slot to %s' % (line, noData))
        
        self.canvas.update()
    # ###########################################
    # SAVING, LOADING, ....
    # ###########################################
    def minimumY(self):
        ## calculate the miinimum Y position on the canvas.  
        ## When loading new widgets will be adjusted down by this amount.
        y = 0
        for widget in self.widgets():
            if widget.y() > y:
                y = widget.y()
                
        if y != 0:
            y += 30 # gives a little more space for the widgets.
        return y
    def saveDocument(self):
        log.log(1, 9, 3, 'Saving Document')
        #return
        if self.schemaName == "":
            return self.saveDocumentAs()
        else:
            return self.save(None,False)

    def saveDocumentAs(self):
        
        
        name = QFileDialog.getSaveFileName(self, "Save File", os.path.join(self.schemaPath, self.schemaName), "Red-R Widget Schema (*.rrs)")
        if not name or name == None: return False
        name = str(name.toAscii())
        if str(name) == '': return False
        if os.path.splitext(str(name))[0] == "": return False
        if os.path.splitext(str(name))[1].lower() != ".rrs": name = name + ".rrs"
        return self.save(str(name),template=False)
        
    def saveTemplate(self):
        name = QFileDialog.getSaveFileName(self, "Save Template", redREnviron.directoryNames['templatesDir'], "Red-R Widget Template (*.rrts)")
        if not name or name == None: return False
        name = str(name.toAscii())
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
                log.log(1, 7, 3, 'File added: ' + str(full_path))
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                log.log(1, 7, 3, 'Entering folder: ' + str(full_path))
                self.addFolderToZip(zip_file, full_path)  
    def addFolderToZip(self,myZipFile,folder):
        import glob
        folder = folder.encode('ascii') #convert path to ascii for ZipFile Method
        for file in glob.glob(folder+"/*"):
                if os.path.isfile(file):
                    
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
    
    def copy(self):
        ## copy the selected files and reload them as templates in the schema
        self.save(copy=True)
    
    def saveInstances(self, instances, widgets, doc, progressBar):
        return redRSaveLoad.saveInstances(instances, widgets, doc, progressBar)
        """
            settingsDict = {}
            requireRedRLibraries = {}
            progress = 0
            for k, widget in instances.items():
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
                
                #map(requiredRLibraries.__setitem__, s['requiredRLibraries']['pythonObject'], []) 
                #requiredRLibraries.extend()
                #del s['requiredRLibraries']
                settingsDict[widget.widgetID] = {}
                settingsDict[widget.widgetID]['settings'] = cPickle.dumps(s,2)
                settingsDict[widget.widgetID]['inputs'] = cPickle.dumps(i,2)
                settingsDict[widget.widgetID]['outputs'] = cPickle.dumps(o,2)
                
                if widget.widgetInfo.package['Name'] != 'base' and widget.widgetInfo.package['Name'] not in requireRedRLibraries.keys():
                    requireRedRLibraries[widget.widgetInfo.package['Name']] = widget.widgetInfo.package
            
                widgets.appendChild(temp)
            return (widgets, settingsDict, requireRedRLibraries)
            """
    
    
    # save the file
    
    def save(self, filename = None, template = False, copy = False):

        if template:
            tempDialog = TemplateDialog(self)
            if tempDialog.exec_() == QDialog.Rejected:
                return
        
        if filename == None and not copy:
            filename = os.path.join(self.schemaPath, self.schemaName)
        elif copy:
            filename = os.path.join(redREnviron.directoryNames['tempDir'], 'copy.rrts')
        pos = self.canvasDlg.pos()
        size = self.canvasDlg.size()
        progressBar = self.startProgressBar(
        'Saving '+str(os.path.basename(filename)),
        'Saving '+str(os.path.basename(filename)),
        len(self.widgets())+len(self.lines())+3)
        progress = 0

        # create xml document
        doc = Document()
        schema = doc.createElement("schema")
        header = doc.createElement('header')
        widgets = doc.createElement("widgets")
        lines = doc.createElement("channels")
        settings = doc.createElement("settings")
        required = doc.createElement("required")
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
        requiredRLibraries = {}
        
        # make the header
        header.setAttribute('version', redREnviron.version['REDRVERSION'])
        
        
        #save widgets
        if copy:  ## copy should obtain the selected widget icons and their associated widgets, we then make a temp copy of that and then redisplay
            tempWidgets = self.activeTab().getSelectedWidgets()
        else:
            tempWidgets = redRObjects.instances(wantType = 'dict') ## all of the widget instances, these are not the widget icons
        (widgets, settingsDict, requireRedRLibraries) = self.saveInstances(tempWidgets, widgets, doc, progressBar)
        
        
        # save tabs and the icons
        if not copy or template:
            #tabs.setAttribute('tabNames', str(self.canvasTabs.keys()))
            for t in redRObjects.tabNames():
                temp = doc.createElement('tab')
                temp.setAttribute('name', t)
                ## set all of the widget icons on the tab
                widgetIcons = doc.createElement('widgetIcons')
                for wi in self.widgetIcons(t)[t]:  ## extract only the list for this tab thus the [t] syntax
                   
                    witemp = doc.createElement('widgetIcon')
                    witemp.setAttribute('name', str(wi.getWidgetInfo().fileName))             # save icon name
                    witemp.setAttribute('instance', str(wi.instanceID))        # save instance ID
                    witemp.setAttribute("xPos", str(int(wi.x())) )      # save the xPos
                    witemp.setAttribute("yPos", str(int(wi.y())) )      # same the yPos
                    witemp.setAttribute("caption", wi.caption)          # save the caption
                    widgetIcons.appendChild(witemp)
                    
                    
                #save connections
                # if not copy:
                    # tempLines = self.lines
                # else:
                    # tempLines = [] ## the lines between the tempWidgets.
                    # for w in tempWidgets:
                        # for e in tempWidgets:
                            # tempLine = self.getLine(w, e)
                            # if tempLine:
                                # tempLines.append(tempLine)
                tabLines = doc.createElement('tabLines')
                for line in self.widgetLines(t)[t]:
                    chtemp = doc.createElement("channel")
                    chtemp.setAttribute("outWidgetCaption", line.outWidget.caption)
                    chtemp.setAttribute('outWidgetIndex', line.outWidget.instance().widgetID)
                    chtemp.setAttribute("inWidgetCaption", line.inWidget.caption)
                    chtemp.setAttribute('inWidgetIndex', line.inWidget.instance().widgetID)
                    chtemp.setAttribute("enabled", str(line.getEnabled()))
                    chtemp.setAttribute('noData', str(line.getNoData()))
                    chtemp.setAttribute("signals", str(line.outWidget.instance().outputs.getLinkPairs(line.inWidget.instance())))
                    tabLines.appendChild(chtemp)
                    
                    
                temp.appendChild(widgetIcons)       ## append the widgetIcons XML to the global XML
                temp.appendChild(tabLines)          ## append the tabLines XML to the global XML
                tabs.appendChild(temp)
        
        
        ## save the global settings ##
        settingsDict['_globalData'] = cPickle.dumps(globalData.globalData,2)
        settingsDict['_requiredPackages'] =  cPickle.dumps({'R': requiredRLibraries.keys(),'RedR': requireRedRLibraries},2)
        #print requireRedRLibraries
        file = open(os.path.join(redREnviron.directoryNames['tempDir'], 'settings.pickle'), "wt")
        file.write(str(settingsDict))
        file.close()

        #settings.setAttribute("settingsDictionary", str(settingsDict))
        #required.setAttribute("requiredPackages", str({'r':r}))
        
        
        # print '\n\n', lines, 'lines\n\n'
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
            
            self.createZipFile(filename,[],[redREnviron.directoryNames['tempDir']])# collect the files that are in the tempDir and save them into the zip file.
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
            self.loadTemplate(filename)
            
        
        if os.path.splitext(filename)[1].lower() == ".rrs":
            (self.schemaPath, self.schemaName) = os.path.split(filename)
            redREnviron.settings["saveSchemaDir"] = self.schemaPath
            self.canvasDlg.addToRecentMenu(filename)
            self.canvasDlg.setCaption(self.schemaName)
        progress += 1
        progressBar.setValue(progress)
        progressBar.close()
        log.log(1, 9, 3, 'Document Saved Successfully')
        return True
    # load a scheme with name "filename"
    def loadTemplate(self, filename, caption = None, freeze = 0):
        self.sessionID += 1 ## must increase the session ID here because otherwise the template will load in the current session and everything will be out of wack!!!
        self.loadDocument(filename = filename, caption = caption, freeze = freeze)
        
    def checkID(self, widgetID):
        for widget in self.widgets():
            if widget.instance().widgetID == widgetID:
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
            return
        
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
                self.loadDocument180(filename, caption = None, freeze = 0, importing = 0)
                loadingProgressBar.hide()
                loadingProgressBar.close()
                return
            else:
                print 'The version is:', version
        except:
            self.loadDocument180(filename, caption = None, freeze = 0, importing = 0)
            loadingProgressBar.hide()
            loadingProgressBar.close()
            return
        widgets = schema.getElementsByTagName("widgets")[0]
        tabs = schema.getElementsByTagName("tabs")[0]
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
                QMessageBox.information(self, 'Schema Loading Failed', 'Duplicated widgets were detected between this schema and the active one.  Loading is not possible.',  QMessageBox.Ok + QMessageBox.Default)
        
                return
            RSession.Rcommand('load("' + os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/') +'")')
        
        loadingProgressBar.setLabelText('Loading Widgets')
        loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
        loadingProgressBar.setValue(0)
        globalData.globalData = cPickle.loads(self.loadedSettingsDict['_globalData'])
        (loadedOkW, tempFailureTextW) = self.loadWidgets(widgets = widgets, loadingProgressBar = loadingProgressBar, tmp = tmp)
        ## LOAD tabs
        #####  move through all of the tabs and load them.
        (loadedOkT, tempFailureTextT) = self.loadTabs(tabs = tabs, loadingProgressBar = loadingProgressBar, tmp = tmp)
        
        qApp.restoreOverrideCursor() 
        qApp.restoreOverrideCursor()
        qApp.restoreOverrideCursor()
        loadingProgressBar.hide()
        loadingProgressBar.close()
    def loadDocument180(self, filename, caption = None, freeze = 0, importing = 0):
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
        self.loadedSettingsDict = settingsDict
        
        self.loadRequiredPackages(settingsDict['_requiredPackages'], loadingProgressBar = loadingProgressBar)
        
        ## make sure that there are no duplicate widgets.
        if not tmp:
            ## need to load the r session before we can load the widgets because the signals will beed to check the classes on init.
            if not self.checkWidgetDuplication(widgets = widgets):
                QMessageBox.information(self, 'Schema Loading Failed', 'Duplicated widgets were detected between this schema and the active one.  Loading is not possible.',  QMessageBox.Ok + QMessageBox.Default)
        
                return
            RSession.Rcommand('load("' + os.path.join(redREnviron.directoryNames['tempDir'], "tmp.RData").replace('\\','/') +'")')
        
        loadingProgressBar.setLabelText('Loading Widgets')
        loadingProgressBar.setMaximum(len(widgets.getElementsByTagName("widget"))+1)
        loadingProgressBar.setValue(0)
        globalData.globalData = cPickle.loads(self.loadedSettingsDict['_globalData'])
        (loadedOkW, tempFailureTextW) = self.loadWidgets180(widgets = widgets, loadingProgressBar = loadingProgressBar, tmp = tmp)
        
        lineList = lines.getElementsByTagName("channel")
        loadingProgressBar.setLabelText('Loading Lines')
        (loadedOkL, tempFailureTextL) = self.loadLines(lineList, loadingProgressBar = loadingProgressBar, 
        freeze = freeze, tmp = tmp)

        for widget in self.widgets(): widget.updateTooltip()
        self.activeCanvas().update()
        #self.saveTempDoc()
        
        if not loadedOkW and loadedOkL:
            failureText = tempFailureTextW + tempFailureTextL
            QMessageBox.information(self, 'Schema Loading Failed', 'The following errors occured while loading the schema: <br><br>' + failureText,  QMessageBox.Ok + QMessageBox.Default)
        
        for widget in self.widgets():
            widget.instance().setLoadingSavedSession(False)
        qApp.restoreOverrideCursor() 
        qApp.restoreOverrideCursor()
        qApp.restoreOverrideCursor()
        loadingProgressBar.hide()
        loadingProgressBar.close()
        
    def loadTabs(self, tabs, loadingProgressBar, tmp):
        # load the tabs
        
        loadedOK = True
        for t in tabs.getElementsByTagName('tab'):
            log.log(1, 5, 3, 'Loading tab %s' % t)
            self.makeSchemaTab(t.getAttribute('name'))
            self.setTabActive(t.getAttribute('name'))
            addY = self.minimumY()
            for witemp in t.getElementsByTagName('widgetIcons')[0].getElementsByTagName('widgetIcon'):
                name = witemp.getAttribute('name')             # save icon name
                instance = witemp.getAttribute('instance')        # save instance ID
                xPos = int(witemp.getAttribute("xPos"))      # save the xPos
                yPos = int(witemp.getAttribute("yPos"))      # same the yPos
                caption = witemp.getAttribute("caption")          # save the caption
                log.log(1, 5, 3, 'loading widgeticon %s, %s, %s' % (name, instance, caption))
                self.addWidgetIconByFileName(name, x = xPos, y = yPos + addY, caption = caption, instance = instance) ##  add the widget icon 
                
            for litemp in t.getElementsByTagName('tabLines')[0].getElementsByTagName('channel'):
                outIconID = litemp.getAttribute('outWidgetIndex')
                inIconID = litemp.getAttribute('inWidgetIndex')
                enabled = eval(litemp.getAttribute('enabled'))
                signals = eval(str(litemp.getAttribute('signals')))
                noData = eval(litemp.getAttribute('noData'))
                inWidget = self.getWidgetByIDActiveTabOnly(inIconID)
                outWidget = self.getWidgetByIDActiveTabOnly(outIconID)
                
                log.log(1, 5, 3, 'loading line %s, %s, %s' % (outIconID, inIconID, enabled))
                if outWidget == None or inWidget == None:
                    log.log(1, 9, 1, 'One of the widgets was a None on line loading; inIcon %s, outIconID %s, keys %s' % (inIconID, outIconID, redRObjects._widgetIcons.keys()))
                    loadedOK = False
                    continue
                ## now add the line with it's settings.
                for (outName, inName) in signals:
                    self.addLink(outWidget, inWidget, outName, inName, enabled, loading = True, process = False)
                lines = redRObjects.getLinesByWidgetInstanceID(outIconID, inIconID)
                for l in lines:
                    l.setNoData(noData)
                
        return (True, '')
    def loadLines(self, lineList, loadingProgressBar, freeze, tmp):
        failureText = ""
        loadedOk = 1
        for line in lineList:
            ## collect the indicies of the widgets to connect.
            inIndex = line.getAttribute("inWidgetIndex")
            outIndex = line.getAttribute("outWidgetIndex")
            #print inIndex, outIndex, '###################HFJSDADSHFAK#############'
            
            if inIndex == None or outIndex == None or str(inIndex) == '' or str(outIndex) == '': # drive down the except path
                #print inIndex, outIndex 
                
                raise Exception
            if freeze: enabled = 0
            else:      enabled = line.getAttribute("enabled")
            #print str(line.getAttribute('signals'))
            ## collect the signals to be connected between these widgets.
            signals = eval(str(line.getAttribute("signals")))
            #print '((((((((((((((((\n\nSignals\n\n', signals, '\n\n'
            if tmp: ## index up the index to match sessionID
                inIndex += '_'+str(self.sessionID)
                outIndex += '_'+str(self.sessionID)
                #print inIndex, outIndex, 'Settings template ID to these values'
            inWidget = self.getWidgetByID(inIndex)
            outWidget = self.getWidgetByID(outIndex)
            
            #print inWidget, outWidget, '#########$$$$$#########$$$$$$#######'
            if inWidget == None or outWidget == None:
                #print 'Expected ID\'s', inIndex, outIndex
                #print '\n\nAvailable indicies are listed here.\'\''
                # for widget in self.widgets():
                    # print widget.instance().widgetID
                failureText += "<nobr>Failed to create a signal line between widgets <b>%s</b> and <b>%s</b></nobr><br>" % (outIndex, inIndex)
                loadedOk = 0
                continue
                
            ## add a link for each of the signals.
            for (outName, inName) in signals:
                ## try to add using the new settings
                if not self.addLink(outWidget, inWidget, outName, inName, enabled, loading = True, process = False): ## connect the signal but don't process.
                    ## try to add using the old settings
                    self.addLink175(outWidget, inWidget, outName, inName, enabled)
            lineInstance = self.getLine(outWidget, inWidget)
            try: ## protection for update.
                lineInstance.dirty = eval(str(line.getAttribute("dirty")))
                ineInstance.noData = eval(str(line.getAttribute('noData')))
            except:
                pass
            print '######## enabled ########\n\n', enabled, '\n\n'
            #self.addLine(outWidget, inWidget, enabled, process = False)
            #self.signalManager.setFreeze(0)
            qApp.processEvents()
            
        return (loadedOk, failureText)
    def loadWidgets180(self, widgets, loadingProgressBar, tmp):
        lpb = 0
        loadedOk = 1
        failureText = ''
        addY = self.minimumY()
        for widget in widgets.getElementsByTagName("widget"):
            try:
                name = widget.getAttribute("widgetName")

                widgetID = widget.getAttribute('widgetID')
                settings = cPickle.loads(self.loadedSettingsDict[widgetID]['settings'])
                inputs = cPickle.loads(self.loadedSettingsDict[widgetID]['inputs'])
                outputs = cPickle.loads(self.loadedSettingsDict[widgetID]['outputs'])
                xPos = int(widget.getAttribute('xPos'))
                yPos = int(widget.getAttribute('yPos'))
                caption = str(widget.getAttribute('caption'))
                ## for backward compatibility we need to make both the widgets and the instances.
                #self.addWidgetInstanceByFileName(name, settings, inputs, outputs)
                widgetInfo =  redRObjects.widgetRegistry()['widgets'][name]
                self.addWidget(widgetInfo, x= xPos, y= yPos, caption = caption, widgetSettings = settings, forceInSignals = inputs, forceOutSignals = outputs)
                #print 'Settings', settings
                lpb += 1
                loadingProgressBar.setValue(lpb)
            except Exception as inst:
                print str(inst), 'Widget load failure 180'
        return (loadedOk, failureText)
    def loadWidgets(self, widgets, loadingProgressBar, tmp):
        
        lpb = 0
        loadedOk = 1
        failureText = ''
        addY = self.minimumY()
        for widget in widgets.getElementsByTagName("widget"):
            try:
                name = widget.getAttribute("widgetName")
                #print name
                widgetID = widget.getAttribute('widgetID')
                #print widgetID
                settings = cPickle.loads(self.loadedSettingsDict[widgetID]['settings'])
                inputs = cPickle.loads(self.loadedSettingsDict[widgetID]['inputs'])
                outputs = cPickle.loads(self.loadedSettingsDict[widgetID]['outputs'])
                #print 'adding instance', widgetID, inputs, outputs
                self.addWidgetInstanceByFileName(name, settings, inputs, outputs, id = widgetID)
                #print 'Settings', settings
                lpb += 1
                loadingProgressBar.setValue(lpb)
            except Exception as inst:
                log.log(1, 9, 1, str(inst))
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
            #print required['RedR']
            
            for name,package in required['RedR'].items():
                #print package
                if not (package['Name'] in installedPackages.keys() 
                and package['Version']['Number'] == installedPackages[package['Name']]['Version']['Number']):
                    downloadList[package['Name']] = {'Version':str(package['Version']['Number']), 'installed':False}

            if len(downloadList.keys()) > 0:
                self.canvasDlg.packageManagerGUI.show()
                self.canvasDlg.packageManagerGUI.askToInstall(downloadList,
                'The following packages need to be installed before the session can be loaded.')
        except: 
            import sys, traceback
            #print '-'*60
            traceback.print_exc(file=sys.stdout)
            #print '-'*60        
    def dumpWidgetVariables(self):
        for widget in self.widgets():
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
            if e.modifiers() & Qt.ShiftModifier and len(self.widgets()) > 1:
                self.addLine(self.widgets()[-2], self.widgets()[-1])
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
class CloneTabDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('New Tab')
        
        self.setLayout(QVBoxLayout())
        layout = self.layout()
        mainWidgetBox = QWidget(self)
        mainWidgetBox.setLayout(QVBoxLayout())
        layout.addWidget(mainWidgetBox)
        
        mainWidgetBox.layout().addWidget(QLabel('Select the Destination for the Clone.', mainWidgetBox))
        
        
        topWidgetBox = QWidget(mainWidgetBox)
        topWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(topWidgetBox)
        
        self.tabList = QListWidget(topWidgetBox)
        self.tabList.addItems(redRObjects.tabNames())
        topWidgetBox.layout().addWidget(self.tabList)
        
        buttonWidgetBox = QWidget(mainWidgetBox)
        buttonWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(buttonWidgetBox)
        
        acceptButton = QPushButton('Accept', buttonWidgetBox)
        cancelButton = QPushButton('Cancel', buttonWidgetBox)
        buttonWidgetBox.layout().addWidget(acceptButton)
        buttonWidgetBox.layout().addWidget(cancelButton)
        QObject.connect(acceptButton, SIGNAL("clicked()"), self.accept)
        QObject.connect(cancelButton, SIGNAL("clicked()"), self.reject)
class NewTabDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('New Tab')
        
        self.setLayout(QVBoxLayout())
        layout = self.layout()
        mainWidgetBox = QWidget(self)
        mainWidgetBox.setLayout(QVBoxLayout())
        layout.addWidget(mainWidgetBox)
        
        mainWidgetBox.layout().addWidget(QLabel('New Tab Name', mainWidgetBox))
        
        
        topWidgetBox = QWidget(mainWidgetBox)
        topWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(topWidgetBox)
        
        self.tabName = QLineEdit(topWidgetBox)
        topWidgetBox.layout().addWidget(self.tabName)
        
        buttonWidgetBox = QWidget(mainWidgetBox)
        buttonWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(buttonWidgetBox)
        
        acceptButton = QPushButton('Accept', buttonWidgetBox)
        cancelButton = QPushButton('Cancel', buttonWidgetBox)
        buttonWidgetBox.layout().addWidget(acceptButton)
        buttonWidgetBox.layout().addWidget(cancelButton)
        QObject.connect(acceptButton, SIGNAL("clicked()"), self.accept)
        QObject.connect(cancelButton, SIGNAL("clicked()"), self.reject)
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
        
        
