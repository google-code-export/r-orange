"""
<name>SandboxIII</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>R</tags>
<icon>icons/ReadFile.png</icon>
<priority>10</priority>
"""
import RSession
from OWRpy import *
import OWGUI
import redRGUI 
import OWToolbars
import re
import textwrap

class sbIII(OWRpy):
    
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(['Plot'])
        self.inputs = [('x', RvarClasses.RDataFrame, self.gotX)]
        self.outputs = [('test output', RvarClasses.RDataFrame)]
        self.data = None
        self.parent = None
        self.cm = None

        self.X = redRGUI.widgetLabel(self.controlArea, '')
        self.Y = redRGUI.widgetLabel(self.controlArea, '')
        self.Z = redRGUI.widgetLabel(self.controlArea, '')
        self.tabWidgeta = redRGUI.tabWidget(self.controlArea)
        #infoBox = OWGUI.widgetBox(self.controlArea, "Save Table")
        plotTab = self.tabWidgeta.createTabPage('Plot')
        self.xColumnSelector = redRGUI.comboBox(plotTab, items=[], callback = self.plot, callback2 = self.refresh)
        self.yColumnSelector = redRGUI.comboBox(plotTab, items=[], callback = self.plot, callback2 = self.refresh)
        self.subsetCMSelector = redRGUI.comboBox(plotTab, items=[' '], callback = self.populateCM)
        self.subsetCMClass = redRGUI.comboBox(plotTab, items=[], callback = self.plot, callback2 = self.refresh)
        paintTab = self.tabWidgeta.createTabPage('Paint')
        self.paintCMSelector = redRGUI.comboBox(paintTab, items = [' '], callback = self.plot)
        plotarea = redRGUI.widgetBox(self.controlArea, "graph")
        
        self.graph = redRGUI.redRGraph(plotarea)
        plotarea.layout().addWidget(self.graph)
        self.zoomSelectToolbarBox = redRGUI.widgetBox(self.controlArea, "Plot Tool Bar")
        self.zoomSelectToolbar = OWToolbars.ZoomSelectToolbar(self.zoomSelectToolbarBox, self, self.graph)
        redRGUI.button(self.controlArea, "selected", callback = self.showSelected)
        redRGUI.button(self.controlArea, label = 'Run QThread', callback = self.RunQthread)
        redRGUI.button(self.controlArea, label = 'play movie', callback = self.ShowText)
        self.movie = redRGUI.MyQMoviePlayer()
        self.RThread = MyThread()
        self.X.setText(str(self.movie.movie.fileName()))
        self.Y.setText(str(self.movie.movie.frameCount()))
        
    def ShowText(self):
        self.movie.show()
        
    def RunQthread(self):
        print str(self.RThread.run(command = 'txt<-c(1,2,3)'))
        
    def refresh(self):
        if self.cm != None:
            try:
                previous = self.paintCMSelector.currentText()
                self.paintCMSelector.clear()
                self.paintCMSelector.addRItems(' ')
                self.paintCMSelector.addRItems(self.R('colnames('+self.cm+')'))
                try:
                    self.paintCMSelector.setCurrentIndex(self.paintCMSelector.findText(previous))
                except: pass
                previous = self.subsetCMSelector.currentText()
                self.subsetCMSelector.clear()
                self.subsetCMSelector.addRItems(' ')
                self.subsetCMSelector.addRItems(self.R('colnames('+self.cm+')'))
                try:
                    self.subsetCMSelector.setCurrentIndex(self.subsetCMSelector.findText(previous))
                except: pass
            except:
                pass
        
    def showSelected(self):
        # set the values in the cm to selected 
        cmSelector = self.subsetCMSelector.currentText()
        cmClass = self.subsetCMClass.currentText()
        if cmSelector != ' ':
            subset = str(self.cm+'[,"'+cmSelector+'"] == "' + cmClass+'"')
        else: subset = 'rownames('+self.data+')'
        
        selected, unselected = self.graph.getSelectedPoints()
        self.R(self.cm+'['+subset+',"'+self.Rvariables['Plot']+'"]<-c('+str(selected)[1:-1]+')')
        self.sendMe()
        
    def gotX(self, data):
        if data:
            self.data = data['data']
            self.parent = data['parent']
            self.cm = data['cm']
            self.R(self.Rvariables['Plot']+'<-rep(0, length('+self.parent+'))')
            self.R(self.cm+'<-cbind('+self.cm+','+self.Rvariables['Plot']+')')
            # set some of the plot data
            self.xColumnSelector.clear()
            self.yColumnSelector.clear()
            self.subsetCMSelector.clear()
            self.paintCMSelector.clear()
            
            self.subsetCMSelector.addRItems(' ')
            self.paintCMSelector.addRItems(' ')
            
            self.xColumnSelector.addRItems(self.R('colnames('+self.data+')'))
            self.yColumnSelector.addRItems(self.R('colnames('+self.data+')'))
            self.subsetCMSelector.addRItems(self.R('colnames('+self.cm+')'))
            self.paintCMSelector.addRItems(self.R('colnames('+self.cm+')'))
            self.paintCMSelector.addRItems(self.R('colnames('+self.data+')'))
            
            self.plot()
    def populateCM(self):
        cmSelector = self.subsetCMSelector.currentText()
        self.subsetCMClass.clear()
        if cmSelector != ' ':
            command = "levels(as.factor("+self.cm+"[,"+str(self.subsetCMSelector.currentIndex())+"]))"
            try:
                self.R('tmp<-'+command) # must assign to a temp variable because otherwise R fails in the background.  This problem should be reported, and may be fixed in later Rpy releases.
                self.subsetCMClass.addRItems(self.R('tmp'))
            except:
                self.X.setText('Failed')
            #self.subsetCMClass.addItems(self.R('levels(as.factor('+self.cm+'[,"'+cmSelector+'"]))'))
            

    def plot(self):
        # populate the cm class columns
        cmSelector = self.subsetCMSelector.currentText()
        cmClass = self.subsetCMClass.currentText()
        xCol = self.xColumnSelector.currentText()
        yCol = self.yColumnSelector.currentText()
        paintClass = self.paintCMSelector.currentText()

        if cmSelector != ' ' and cmSelector != '' and int(self.subsetCMSelector.currentIndex()) != 0:
            subset = str(self.cm+'[,"'+cmSelector+'"] == "' + cmClass+'"')
            cmSubset = '[,"'+cmSelector+'"] == "' + cmClass+'"'
        else: 
            subset = ''
            cmSubset = ''
        
        if paintClass != ' ':
            if paintClass in self.R('colnames('+self.cm+')'):
                cm = self.R(self.cm+cmSubset)
            elif paintClass in self.R('colnames('+self.data+')'):
                cm = self.R(self.data+cmSubset)
            paint = cm[str(paintClass)]
        else: paint = []
        # make the plot
        if xCol == yCol: return
        self.graph.clear()
        XData = self.R(self.data + '['+subset+',"'+str(xCol)+'"]')
        YData = self.R(self.data + '['+subset+',"'+str(yCol)+'"]')
        self.subset = self.data + '['+subset+',]'
        if XData == [] or YData == []: return
        self.graph.points("MyData", xData = self.R('as.numeric('+self.data + '['+subset+',"'+str(xCol)+'"])'), yData = self.R('as.numeric('+self.data + '['+subset+',"'+str(yCol)+'"])'), brushColor = paint, penColor=paint, size=[])
        #self.X.setText(str(paint))

    def sendMe(self):
        data = {'data': self.parent+'['+self.cm+'[,"'+self.Rvariables['Plot']+'"] == 1,]', 'parent':self.parent, 'cm':self.cm} # data is sent forward relative to self parent as opposed to relative to the data that was recieved.  This makes the code much cleaner as recursive subsetting often generates NA's due to restriction.
        self.rSend('test output', data)
        self.sendRefresh()
        
    def widgetDelete(self):
        if self.cm:
            self.R(self.cm+'$'+self.Rvariables['Plot']+'<-NULL') #removes the column for this widget from the CM
            self.sendRefresh()
            
            
class MyThread(QThread, RSession):
    def __init__(self, parent = None):
        RSession.__init__(self)
        QThread.__init__(self, None)
        #self.command = ''
    def run(self, command):
        return self.R(command)
        