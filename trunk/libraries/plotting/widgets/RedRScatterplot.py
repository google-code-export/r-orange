"""
<name>Scatterplot</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Plotting, Subsetting</tags>
<icon>plot.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI
import redRGUI 
import re
import textwrap, numpy
import libraries.base.signalClasses.RDataFrame as rdf
from PyQt4.QtGui import *
### currently depricated until fixed
class RedRScatterplot(OWRpy):
    
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "RedR Scatterplot", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        self.setRvariableNames(['Plot','paint','selected'])
        self.inputs = [('x', rdf.RDataFrame, self.gotX)]
        self.outputs = [('Scatterplot Output', rdf.RDataFrame)]
        self.data = None
        self.parent = None
        self.cm = None

        # GUI
        self.xColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'X data', items=[])
        # self.forceXNumeric = redRGUI.checkBox(self.GUIDialog, buttons = ['Force Numeric'], toolTips = ['Force the values to be treated as numeric, may fail!!!'])
        self.yColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'Y data', items=[])
        # self.forceYNumeric = redRGUI.checkBox(self.GUIDialog, buttons = ['Force Numeric'], toolTips = ['Force the values to be treated as numeric, may fail!!!'])
        self.paintCMSelector = redRGUI.comboBox(self.GUIDialog, label = 'Color Points By:', items = [''])
        self.replotCheckbox = redRGUI.checkBox(self.GUIDialog, buttons = ['Reset Zoom On Selection'], toolTips = ['When checked this plot will readjust it\'s zoom each time a new seleciton is made.']) 
        self.replotCheckbox.setChecked(['Reset Zoom On Selection'])
        
        # plot area
        plotarea = redRGUI.groupBox(self.controlArea, label = "Graph")
        plotarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.graph = redRGUI.redRGraph(plotarea)
        plotarea.layout().addWidget(self.graph)
        #self.zoomSelectToolbarBox = redRGUI.groupBox(self.GUIDialog, label = "Plot Tool Bar")
        
        redRGUI.separator(self.GUIDialog,height=8)
        buttonBox = redRGUI.widgetBox(self.GUIDialog,orientation='horizontal')
        redRGUI.button(buttonBox, label = "Plot", callback = self.plot, toolTip = 'Subset the data according to your selection.  This applied the selection to the CM also.')
        redRGUI.button(buttonBox, label = "Select", callback = self.sendMe, toolTip = 'Subset the data according to your selection.  This applied the selection to the CM also.')
        redRGUI.separator(self.GUIDialog,height=8)
        self.zoomSelectToolbar = redRGUI.zoomSelectToolbar(self, self.GUIDialog, self.graph)
        self.paintLegend = redRGUI.textEdit(self.GUIDialog)
        
        self.resize(600, 500)

        
    def showSelected(self):
        if self.data == None:
            self.status.setText('No Data')
            return
            
        xData = self.data.getData()[str(self.xColumnSelector.currentText())]
        yData = self.data.getData()[str(self.yColumnSelector.currentText())]
        selected, unselected = self.graph.getSelectedPoints(xData = xData, yData = yData)
        
        ## use the selected and unselected lists to generate the new dict.
        newData = {}
        for key in self.data.getData().keys():
            newData[key] = []
            for i in range(len(selected)):
                if selected[i]:
                    newData[key].append(self.data.getData()[key][i])
                    
        sendData = signals.StructuredDict(data = newData, parent = self.data.getData(), keys = self.data.getItem('keys'))
        self.rSend('Scatterplot Output', newData)
        self.sendRefresh()
        
    def gotX(self, data):
        if data:
            self.dataParent = data
            self.data = data.getData()
            colnames = self.R('colnames(%s)' % self.data)
            keys = ['']
            keys += colnames
            self.paintCMSelector.update(keys)
            
            ## might be good to limit the user to selecting only those indicies that have numeric values
            self.xColumnSelector.update(colnames)
            self.yColumnSelector.update(colnames)
            self.plot()
        else:
            self.data = None
            self.xData = []
            self.yData = []
            self.graph.clear()
    def plot(self, newZoom = True):
        xCol = str(self.xColumnSelector.currentText())
        yCol = str(self.yColumnSelector.currentText())
        paintClass = str(self.paintCMSelector.currentText())
        self.xData = []
        self.yData = []
        if xCol == yCol: return
        self.graph.setXaxisTitle(str(xCol))
        self.graph.setYLaxisTitle(str(yCol))
        self.graph.setShowXaxisTitle(True)
        self.graph.setShowYLaxisTitle(True)
        self.graph.clear()
        # there is a paintclass selected so we should paint on the levels of the paintclass
        subset = []
        d = self.data
        self.paintLegend.clear()
        if paintClass in self.R('colnames('+self.data+')'): 
            self.R(self.Rvariables['paint'] + ' <-as.factor('+self.data+'[,\''+paintClass+'\'])')
            levels = self.R('levels('+self.Rvariables['paint']+')', wantType = 'list')
            #print vectorClass
            if len(levels) > 50:
                runMe = QMessageBox.information(None, 'RedRWarning', 'You are asking to paint on more than 50 colors.\nRed-R supports a limited number of colors in this plot widget.\nIt is unlikely that you will be able to interperte this data\nand plotting may take a very long time.\nAre you sure you want to plot this???', QMessageBox.Yes, QMessageBox.No)
                if runMe == QMessageBox.No: return
                
            for level in levels:
                subset.append((level, self.data+'[,\''+paintClass+'\'] == "'+level + '"'))

            if self.R('sum(is.na('+self.data+'[,\''+paintClass+'\']))') > 0:
                subset.append(('NA', 'is.na('+self.data+'[,\''+paintClass+'\'])'))
                levels.append('NA')
        else:
            self.R(self.Rvariables['paint']+'<-TRUE')
            levels = ['ALL']
            subset.append(('ALL','TRUE'))
            
        pc = 0
        xDataClass = self.R('class('+self.data+'[,\''+str(xCol)+'\'])', silent = True)
        yDataClass = self.R('class('+self.data+'[,\''+str(yCol)+'\'])', silent = True)
        self.paintLegend.insertHtml('<h5>Color Legend</h5>')
        self.paintLegend.insertHtml('<table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="25%">Color</th><th align="left" width="75%">Group Name</th></tr>')
        for (p, subset) in subset:
            print p
            if p in ['NA','ALL']:
                pc=0
            else:
                pc = levels.index(p)+1
                
            lColor = self.setColor(pc)
            
            self.paintLegend.insertHtml('<tr><td width = "25%" bgcolor="'+lColor+'">&nbsp;</td><td width = "75%">'+p+'</td></tr>')
            # generate the subset
            # check if the column is a factor
            # print '|#| '+str(self.forceXNumeric.getChecked())
            
            # if xDataClass in ['factor'] and 'Force Numeric' not in self.forceXNumeric.getChecked():
                # print 'Setting xData as factor'
                # xData = self.R('match('+self.data+'['+subset+',\''+str(xCol)+'\'], levels('+self.data+'[,\''+str(xCol)+'\']))', wantType = 'list', silent = True)
            # else:
            xData = self.R('as.numeric('+self.data+'['+subset+',\''+str(xCol)+'\'])', wantType = 'list')

            # if yDataClass in ['factor'] and 'Force Numeric' not in self.forceYNumeric.getChecked():
                # print 'Setting yData as factor'
                # yData = self.R('match('+self.data+'['+subset+',\''+str(yCol)+'\'], levels('+self.data+'[,\''+str(yCol)+'\']))', wantType = 'list', silent = True)
            # else:
            yData = self.R('as.numeric('+self.data+'['+subset+',\''+str(yCol)+'\'])', wantType = 'list')

            # print xData
            # print yData
            
            if len(xData) == 0 or len(yData) == 0: continue
            self.graph.points("MyData", xData = xData, yData = yData, brushColor = pc, penColor=pc)
            self.xData += xData
            self.yData += yData
        self.paintLegend.insertHtml('</table>')
        
        ## make a fake call to the zoom to repaint the points and to add some interest to the graph
        if newZoom and 'Reset Zoom On Selection' in self.replotCheckbox.getChecked():
            self.graph.setNewZoom(float(min(self.xData)), float(max(self.xData)), float(min(self.yData)), float(max(self.yData)))
            
        self.graph.replot()
        
    def asNumeric(self, listItems):
        ## convert a list to a numeric list
        newList = []
        for i in listItems:
            try:
                newList.append(float(i))
            except:
                newList.append(None)
                
        return newList
    def sendMe(self):
        xCol = str(self.xColumnSelector.currentText())
        yCol = str(self.yColumnSelector.currentText())

        xData = self.R('as.numeric('+self.data+'[,"'+str(xCol)+'"])', wantType = 'list')
        yData = self.R('as.numeric('+self.data+'[,"'+str(yCol)+'"])', wantType = 'list')
        
        selected, unselected = self.graph.getSelectedPoints(xData = xData, yData = yData)
        print selected
        print unselected
        index = []
        for x in selected:
            if x ==1: index.append('T')
            else: index.append('F')
            
        index = 'c('+','.join(index) + ')'
        self.R('%s<-%s[%s,]' % (self.Rvariables['selected'],self.data,index),silent=True)
        
        data = rdf.RDataFrame(data = self.Rvariables['selected'], parent = self.dataParent.getDataParent()) 
        data.copyAllOptionalData(self.dataParent)
        self.rSend('Scatterplot Output', data)
        #self.sendRefresh()
        
    def loadCustomSettings(self, settings = None):
        # custom function to replot the data that is in the scatterplot
        self.plot()
    def widgetDelete(self):
        if self.cm and self.Rvariables['Plot'] in self.R('colnames('+self.cm+')', wantType = 'list'):
            self.R(self.cm+'$'+self.Rvariables['Plot']+'<-NULL') #removes the column for this widget from the CM
            self.sendRefresh()
    def setColor(self, colorint):
        # import colorsys
        # N = 50
        # HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
        # RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
        # return RGB_tuples[colorint]
        
        if colorint == 0 or colorint == 'FALSE':
            return '#000000'
        elif colorint == 1 or colorint == 'TRUE':
            return '#ff0000'
        elif colorint == 2:
            return '#00ff00'
        elif colorint == 3:
            return '#0000ff'
        elif colorint == 4:
            return '#ffff00'
        elif colorint == 5:
            return '#a0a0a4'
        elif colorint == 6:
            return '#ff00ff'
        elif colorint == 7:
            return '#00ffff'
        elif colorint == 8:
            return '#000080'
        elif colorint == 9:
            return '#800000'
        
        else:
            return self.setColor(colorint - 10) # run back through the levels and reduce by 5, the colors cycle every 5