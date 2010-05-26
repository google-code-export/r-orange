"""
<name>Scatterplot</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Plotting, Subsetting</tags>
<icon>icons/plot.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI
import redRGUI 
# import OWToolbars
import re
import textwrap, numpy
from PyQt4.QtGui import *

class RedRScatterplot(OWRpy):
    
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "RedR Scatterplot", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        self.setRvariableNames(['Plot'])
        self.inputs = [('x', signals.StructuredDict, self.gotX)]
        self.outputs = [('Scatterplot Output', signals.RDataFrame)]
        self.data = None
        self.parent = None
        self.dataParent = {}
        self.cm = None

        # GUI
        self.xColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'X data', items=[], callback = self.plot, callback2 = self.refresh)
        self.forceXNumeric = redRGUI.checkBox(self.GUIDialog, buttons = ['Force Numeric'], toolTips = ['Force the values to be treated as numeric, may fail!!!'])
        self.yColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'Y data', items=[], callback = self.plot, callback2 = self.refresh)
        self.forceYNumeric = redRGUI.checkBox(self.GUIDialog, buttons = ['Force Numeric'], toolTips = ['Force the values to be treated as numeric, may fail!!!'])
        self.paintCMSelector = redRGUI.comboBox(self.GUIDialog, label = 'Color Points By:', items = [''], callback = self.plot)
        self.replotCheckbox = redRGUI.checkBox(self.GUIDialog, buttons = ['Reset Zoom On Selection'], toolTips = ['When checked this plot will readjust it\'s zoom each time a new seleciton is made.']) 
        self.replotCheckbox.setChecked(['Reset Zoom On Selection'])
        self.paintLegend = redRGUI.textEdit(self.GUIDialog)
        
        # plot area
        plotarea = redRGUI.groupBox(self.controlArea, label = "Graph")
        plotarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.graph = redRGUI.redRGraph(plotarea)
        plotarea.layout().addWidget(self.graph)
        self.zoomSelectToolbarBox = redRGUI.groupBox(self.GUIDialog, label = "Plot Tool Bar")
        self.zoomSelectToolbar = redRGUI.zoomSelectToolbar(self, self.zoomSelectToolbarBox, self.graph)
        redRGUI.button(self.bottomAreaRight, label = "Print", callback = self.printGraph, tooltip = 'Print your selection to the default printer')
        redRGUI.button(self.bottomAreaRight, label = "Select", callback = self.showSelected, tooltip = 'Subset the data according to your selection.  This applied the selection to the CM also.')
        
        self.resize(600, 500)
        self.move(300, 25)
    def printGraph(self):
        printer = QPrinter()
        printerDialog = QPrintDialog(printer)

        if printerDialog.exec_() == QDialog.Rejected: 
            print 'Printing Rejected'
            return
        print printer
        self.graph.print_(printer)
    def refresh(self):
        if self.cm != None:
            try:
                names = self.R('names('+self.cm+')')
                if type(names) == str and names != None and names != 'NULL':
                    names = [names]
                else:
                    names = []
                names += self.R('colnames('+self.data+')')
                names.insert(0, '')
                self.paintCMSelector.update(names)
                
                self.plot(newZoom = False)
                
            except:
                pass
        
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
            self.data = data
            keys = ['']
            keys += self.data.getItem('keys')
            self.paintCMSelector.update(keys)
            
            ## might be good to limit the user to selecting only those indicies that have numeric values
            self.xColumnSelector.update(self.data.getItem('keys'))
            self.yColumnSelector.update(self.data.getItem('keys'))
            self.plot()
        else:
            self.data = None
            self.xData = []
            self.yData = []
            self.graph.clear()
    def unique(self, seq, idfun=None):  
        # order preserving 
        if idfun is None: 
            def idfun(x): return x 
        seen = {} 
        result = [] 
        for item in seq: 
            marker = idfun(item) 
            # in old Python versions: 
            # if seen.has_key(marker) 
            # but in new ones: 
            if marker in seen: continue 
            seen[marker] = 1 
            result.append(item) 
        return result
    def plot(self, newZoom = True):
        
        ## remake the plot function to work on dictionaries.  This will be much better than only being able to work on data frames.
        if self.data == None:
            self.status.setText('No Data, nothing to plot')
            return
        xIndex = str(self.xColumnSelector.currentText())
        yIndex = str(self.yColumnSelector.currentText())
        paintClass = str(self.paintCMSelector.currentText())
        self.xData = []
        self.yData = []
        if xIndex == yIndex: 
            self.status.setText('X and Y data are the same, can\'t plot.')
            return
        
        # prepare the graph
        self.graph.setXaxisTitle(str(xIndex))
        self.graph.setYLaxisTitle(str(yIndex))
        self.graph.setShowXaxisTitle(True)
        self.graph.setShowYLaxisTitle(True)
        self.graph.clear()

        # start to make the plot we need to move across all of the levels (though they may not be levels in the dict case) of the paintclass and plot those points.
        if paintClass not in ['', ' ']:  # There are paintClass and we now need to find out what they are.
            paintclasses = self.unique(self.data.getData()[paintClass]) # returns the unique items.
            if len(paintclasses) > 50:
                runMe = QMessageBox.information(None, 'RedRWarning', 'You are asking to paint on more than 50 colors.\nRed-R supports a limited number of colors in this plot widget.\nIt is unlikely that you will be able to interperte this data\nand plotting may take a very long time.\nAre you sure you want to plot this???', QMessageBox.Yes, QMessageBox.No)
                if runMe == QMessageBox.No: return
            pc = 0
            self.paintLegend.insertHtml('<h5>Color Legend</h5>')
            self.paintLegend.insertHtml('<table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="25%">Color</th><th align="left" width="75%">Group Name</th></tr>')
                
            for pclass in paintclasses: # move across all of the paint classes.
                index = []
                for i, v in enumerate(self.data.getData()[paintClass]):
                    if v == pclass:
                        index.append(i)
                ## form the list for the data
                xData = []
                yData = []
                for i in index:
                    xData.append(self.data.getData()[xIndex][i])
                    yData.append(self.data.getData()[yIndex][i])
                lColor = self.setColor(pc)
                self.paintLegend.insertHtml('<tr><td width = "25%" bgcolor = \"'+lColor+'\">&nbsp;</td><td width = "75%">'+str(pclass)+'</td></tr>')
                self.graph.points("MyData", xData = xData, yData = yData, brushColor = pc, penColor=pc)
                self.xData += xData
                self.yData += yData
                pc += 1
            self.paintLegend.insertHtml('</table>')
            
        else:
            self.xData = self.data.getData()[xIndex]
            self.yData = self.data.getData()[yIndex]
            self.graph.points("MyData", xData = self.xData, yData = self.yData, brushColor = 0, penColor = 0)
        # make the plot
        
        
        if newZoom and 'Reset Zoom On Selection' in self.replotCheckbox.getChecked():
             
            if type(min(self.xData)) in [int, float, long] and type(min(self.yData)) in [int, float, long]:
                self.graph.setNewZoom(float(min(self.xData)), float(max(self.xData)), float(min(self.yData)), float(max(self.yData)))
            else:
                try:
                    self.graph.setNewZoom(float(min(self.xData)), float(max(self.xData)), float(min(self.yData)), float(max(self.yData)))
                except:
                    self.status.setText('X or Y data not numeric, can not reset the zoom.')
                    print type(min(self.xData)), min(self.xData)
                    print type(min(self.yData)), min(self.yData)
        self.graph.replot()
        
        
        return
        # populate the cm class columns
        #cmSelector = str(self.subsetCMSelector.currentText())
        #cmClass = str(self.subsetCMClass.currentText())
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
        print paintClass
        if paintClass not in ['', ' ']: # there is a paintclass selected so we should paint on the levels of the paintclass
            self.paintLegend.clear()
            subset = []
            if paintClass in self.R('colnames('+self.data+')'): # the data comes from the parent data frame and not the cm
                d = self.data
                vectorClass = self.R('class('+self.data+'[,\''+paintClass+'\'])')
                print vectorClass
                if vectorClass in ['character']: 
                    QMessageBox.information(self, 'Red-R Canvas','Class of the paint vector is not appropriate\nfor this widget.',  QMessageBox.Ok + QMessageBox.Default)
                    print vectorClass
                    return
                    
                elif vectorClass in ['numeric', 'integer']:
                    levelType = 'numeric'
                    levels = self.R('levels(as.factor('+self.data+'[,\''+paintClass+'\']))', wantType = 'list')
                    if len(levels) > 50:
                        runMe = QMessageBox.information(None, 'RedRWarning', 'You are asking to paint on more than 50 colors.\nRed-R supports a limited number of colors in this plot widget.\nIt is unlikely that you will be able to interperte this data\nand plotting may take a very long time.\nAre you sure you want to plot this???', QMessageBox.Yes, QMessageBox.No)
                        if runMe == QMessageBox.No: return
                        
                    for level in levels:
                        subset.append((level, self.data+'[,\''+paintClass+'\'] == '+level))
                elif vectorClass in ['logical']:
                    levelType = 'logical'
                    levels = ['FALSE', 'TRUE']
                    for level in levels:
                        subset.append((level, '!is.na('+self.data+'$'+paintClass+') & '+self.data+'[,\''+paintClass+'\'] == '+level))
                    subset.append(('NA', 'is.na('+self.data+'[,\''+paintClass+'\'])'))
                    levels.append('NA')
                else:
                    levelType = 'other'
                    levels = self.R('levels(as.factor(na.omit('+self.data+'[,\''+paintClass+'\'])))', wantType = 'list')
                    if len(levels) > 50:
                        runMe = QMessageBox.information(None, 'RedRWarning', 'You are asking to paint on more than 50 colors.\nRed-R supports a limited number of colors in this plot widget.\nIt is unlikely that you will be able to interperte this data\nand plotting may take a very long time.\nAre you sure you want to plot this???', QMessageBox.Yes, QMessageBox.No)
                        if runMe == QMessageBox.No: return
                    for level in levels:
                        subset.append((level, '!is.na('+self.data+'$'+paintClass+') & '+self.data+'[,\''+paintClass+'\'] == \''+level+'\''))
                    subset.append(('NA', 'is.na('+self.data+'[,\''+paintClass+'\'])'))
                    levels.append('NA')
            else: # we made it this far so the data must be in the cm
                d = self.cm # be mindful that the cm is a list and should be subset as such
                # in this case we need to subset on the rownames making groups that are either in or out of the set, so these cm's will only be 1 or 0
                levels = self.R('names('+self.cm+'$'+paintClass+')', wantType = 'list')
                for level in levels:
                    levelType = 'cm'
                    subset.append((level, '(rownames('+self.data+') %in% '+self.cm+'$'+paintClass+'$'+level+')'))
                    
            
            
            pc = 0
            xDataClass = self.R('class('+self.data+'[,\''+str(xCol)+'\'])', silent = True)
            yDataClass = self.R('class('+self.data+'[,\''+str(yCol)+'\'])', silent = True)
            self.paintLegend.insertHtml('<h5>Color Legend</h5>')
            self.paintLegend.insertHtml('<table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="25%">Color</th><th align="left" width="75%">Group Name</th></tr>')
            for (p, subset) in subset:
                print p
                # collect the color
                if levelType not in ['logical', 'numeric', 'cm'] and p != 'NA':
                    pc = self.R('match(\''+p+'\', levels(as.factor('+d+'[,\''+paintClass+'\'])))', silent = True)
                elif levelType not in ['logical', 'numeric'] and p == 'NA':
                    pc = 0
                elif levelType in ['cm']:
                    pc = self.R('match(\''+p+'\', names('+d+'$'+paintClass+'))')
                lColor = self.setColor(pc)
                self.paintLegend.insertHtml('<tr><td width = "25%" bgcolor = \"'+lColor+'\">&nbsp;</td><td width = "75%">'+p+'</td></tr>')
                # generate the subset
                # check if the column is a factor
                print '|#| '+str(self.forceXNumeric.getChecked())
                if xDataClass in ['factor'] and 'Force Numeric' not in self.forceXNumeric.getChecked():
                    print 'Setting xData as factor'
                    xData = self.R('match('+self.data+'['+subset+',\''+str(xCol)+'\'], levels('+self.data+'[,\''+str(xCol)+'\']))', wantType = 'list', silent = True)
                else:
                    xData = self.R('as.numeric('+self.data+'['+subset+',\''+str(xCol)+'\'])', wantType = 'list')
                if yDataClass in ['factor'] and 'Force Numeric' not in self.forceYNumeric.getChecked():
                    print 'Setting yData as factor'
                    yData = self.R('match('+self.data+'['+subset+',\''+str(yCol)+'\'], levels('+self.data+'[,\''+str(yCol)+'\']))', wantType = 'list', silent = True)
                else:
                    yData = self.R('as.numeric('+self.data+'['+subset+',\''+str(yCol)+'\'])', wantType = 'list')
                print xData
                print yData
                
                if len(xData) == 0 or len(yData) == 0:
                    pc += 1
                    continue
                self.graph.points("MyData", xData = xData, yData = yData, brushColor = pc, penColor=pc)
                self.xData += xData
                self.yData += yData
                pc += 1
            self.paintLegend.insertHtml('</table>')
        # make the plot
        else:
            self.paintLegend.clear()
            self.paintLegend.insertHtml('<h5>Color Legend</h5><table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="25%">Color</th><th align="left" width="75%">Group Name</th></tr>')
            lColor = self.setColor(1)
            self.paintLegend.insertHtml('<tr><td width = "25%" bgcolor = \"'+lColor+'\">&nbsp;</td><td width = "75%">All</td></tr></table>')
            xDataClass = self.R('class('+self.data+'[,\''+str(xCol)+'\'])', silent = True)
            yDataClass = self.R('class('+self.data+'[,\''+str(yCol)+'\'])', silent = True)
            # check if the column is a factor
            if xDataClass in ['factor'] and 'Force Numeric' not in self.forceXNumeric.getChecked():
                xData = self.R('match('+self.data+'[!is.na('+self.data+'$'+str(xCol)+'),\''+str(xCol)+'\'], levels('+self.data+'[,\''+str(xCol)+'\']))', wantType = 'list')
            else:
                xData = self.R(self.data+'[!is.na('+self.data+'$'+str(xCol)+'),\''+str(xCol)+'\']', wantType = 'list')
            if yDataClass in ['factor'] and 'Force Numeric' not in self.forceYNumeric.getChecked():
                yData = self.R('match('+self.data+'[!is.na('+self.data+'$'+str(yCol)+'),\''+str(yCol)+'\'], levels('+self.data+'[,\''+str(yCol)+'\']))', wantType = 'list')
            else:
                yData = self.R(self.data+'[!is.na('+self.data+'$'+str(yCol)+'),\''+str(yCol)+'\']', wantType = 'list')
            
            self.graph.points("MyData", xData = xData, yData = yData)
            self.xData += xData
            self.yData += yData
        ## make a fake call to the zoom to repaint the points and to add some interest to the graph
            
    def sendMe(self):

        return
        data = signals.RDataFrame(data = self.dataParent.parent+'[rownames('+self.dataParent.parent+') %in% '+self.cm+'$'+self.Rvariables['Plot']+'$True,]', parent = self.parent) # data is sent forward relative to self parent as opposed to relative to the data that was recieved.  This makes the code much cleaner as recursive subsetting often generates NA's due to restriction.
        data.copyAllOptionalData(self.dataParent)
        self.rSend('Scatterplot Output', data)
        self.sendRefresh()
    def loadCustomSettings(self, settings = None):
        # custom function to replot the data that is in the scatterplot
        self.plot()
    def widgetDelete(self):
        if self.cm and self.Rvariables['Plot'] in self.R('colnames('+self.cm+')', wantType = 'list'):
            self.R(self.cm+'$'+self.Rvariables['Plot']+'<-NULL') #removes the column for this widget from the CM
            self.sendRefresh()
    def setColor(self, colorint):
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