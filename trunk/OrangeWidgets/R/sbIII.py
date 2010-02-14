"""
<name>SandboxIII</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>R</tags>
<icon>icons/ReadFile.png</icon>
<priority>10</priority>
"""

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
        
        self.inputs = [('x', RvarClasses.RVariable, self.gotX),('y', RvarClasses.RVariable, self.gotY)]
        self.outputs = [('test output', RvarClasses.RVariable)]
        self.data = None
        self.parent = None
        self.cm = None
        
        self.X = redRGUI.widgetLabel(self.controlArea, '')
        self.Y = redRGUI.widgetLabel(self.controlArea, '')
        self.Z = redRGUI.widgetLabel(self.controlArea, '')
        
        self.xColumnSelector = redRGUI.comboBox(self.controlArea, items=[], callback = self.plot)
        self.yColumnSelector = redRGUI.comboBox(self.controlArea, items=[], callback = self.plot)
        self.subsetCMSelector = redRGUI.comboBox(self.controlArea, items=[' '], callback = self.plot)
        plotarea = redRGUI.widgetBox(self.controlArea, "graph")
        
        self.graph = redRGUI.redRGraph(plotarea)
        plotarea.layout().addWidget(self.graph)
        self.zoomSelectToolbarBox = redRGUI.widgetBox(self.controlArea, "Plot Tool Bar")
        self.zoomSelectToolbar = OWToolbars.ZoomSelectToolbar(self.zoomSelectToolbarBox, self, self.graph)
        redRGUI.button(self.controlArea, self, "selected", callback = self.showSelected)
        
    def showSelected(self):
        self.Z.setText(str(self.graph.getSelectedPoints()))
        
    def gotX(self, data):
        if data:
            self.data = data['data']
            self.parent = data['parent']
            self.cm = data['cm']
            
            # set some of the plot data
            self.xColumnSelector.addItems(self.R('colnames('+self.data+')'))
            self.yColumnSelector.addItems(self.R('colnames('+self.data+')'))
            self.subsetCMSelector.addItems(self.R('colnames('+self.cm+')'))
            self.plot()

    def plot(self):
        self.graph.clear()
        self.graph.points("MyData", xData = self.R(self.data + '['+self.subsetCMSelector.currentText()+','+self.xColumnSelector.currentText()+']'), yData = self.R(self.data + '['+self.subsetCMSelector.currentText()+','+self.yColumnSelector.currentText()+']'), brushColor = self.R('as.numeric('+self.data+'[,2] < 30)'), penColor=self.R('as.numeric('+self.data+'[,2] < 30)'), size=[])
        #self.X.setText(str(self.R('as.numeric('+self.data+'[,2] < 30)')))

    def showLinks(self):
        self.Z.setText(str(self.linksOut))