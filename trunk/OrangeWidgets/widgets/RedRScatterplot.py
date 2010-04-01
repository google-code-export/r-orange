"""
<name>RedR Scatterplot</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Plotting, Data Classification</tags>
<icon>icons/plot.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI
import redRGUI 
import OWToolbars
import re
import textwrap, numpy

class RedRScatterplot(OWRpy):
    
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "RedR Scatterplot", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        self.setRvariableNames(['Plot'])
        self.inputs = [('x', RvarClasses.RDataFrame, self.gotX)]
        self.outputs = [('Scatterplot Output', RvarClasses.RDataFrame)]
        self.data = None
        self.parent = None
        self.cm = None
        self.loadSettings()


        self.xColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'X data', items=[], callback = self.plot, callback2 = self.refresh)
        self.yColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'Y data', items=[], callback = self.plot, callback2 = self.refresh)
        # self.subsetCMSelector = redRGUI.comboBox(plotTab, items=[' '], callback = self.populateCM)
        # self.subsetCMClass = redRGUI.comboBox(plotTab, items=[], callback = self.plot, callback2 = self.refresh)
        self.paintCMSelector = redRGUI.comboBox(self.GUIDialog, label = 'Painting Vector', items = [''], callback = self.plot)
        plotarea = redRGUI.groupBox(self.controlArea, label = "Graph")
        plotarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.graph = redRGUI.redRGraph(plotarea)
        plotarea.layout().addWidget(self.graph)
        self.zoomSelectToolbarBox = redRGUI.groupBox(self.GUIDialog, label = "Plot Tool Bar")
        self.zoomSelectToolbar = OWToolbars.ZoomSelectToolbar(self, self.zoomSelectToolbarBox, self.graph)
        redRGUI.button(self.bottomAreaRight, label = "Select", callback = self.showSelected, tooltip = 'Subset the data according to your selection.  This applied the selection to the CM also.')
        
        self.resize(600, 500)
        self.move(300, 25)
    def refresh(self):
        if self.cm != None:
            try:
                names = self.R('colnames('+self.cm+')')
                if type(names) == str:
                    names = [names]
                names += self.R('colnames('+self.data+')')
                names.insert(0, '')
                self.paintCMSelector.update(names)
                
                # names = ['']
                # names += list(self.R('colnames('+self.cm+')'))
                # self.subsetCMSelector.update(names)
                
            except:
                pass
        
    def showSelected(self):
        # set the values in the cm to selected 
        #cmSelector = self.subsetCMSelector.currentText()
        #cmClass = self.subsetCMClass.currentText()
        # if cmSelector != ' ':
            # subset = str(self.cm+'[,"'+cmSelector+'"] == "' + cmClass+'"')
        #else: 
        if self.R('rownames('+self.data+')') != None:
           subset = 'rownames('+self.data+')'
        else:
           subset = ''
        print self.R('as.matrix(t('+self.data+'[,\''+str(self.xColumnSelector.currentText())+'\']))')
        print type(self.R('as.matrix('+self.data+'[,\''+str(self.xColumnSelector.currentText())+'\'])'))
        selected, unselected = self.graph.getSelectedPoints(xData = list(self.R('as.matrix(t('+self.data+'[,\''+str(self.xColumnSelector.currentText())+'\']))')), yData = list(self.R('as.matrix(t('+self.data+'[,\''+str(self.yColumnSelector.currentText())+'\']))')))
        if self.cm == None or self.cm == '':
           newData = self.dataParent.copy()
           newData['data'] = self.data+'[c('+str(selected)[1:-1]+'),]'
           self.rSend('Scatterplot Output', newData)
        else:
           self.R(self.cm+'[,"'+self.Rvariables['Plot']+'"]<-c('+str(selected)[1:-1]+')')
           self.sendMe()
        
    def gotX(self, data):
        if data:
            self.data = data['data']
            self.parent = data['parent']
            self.dataParent = data.copy()
            if 'cm' in data:
                self.cm = data['cm']
                self.R(self.Rvariables['Plot']+'<-rep(0, length('+self.parent+'[,1]))')
                self.R(self.cm+'<-cbind('+self.cm+','+self.Rvariables['Plot']+')')
                cmColNames = self.R('colnames('+self.cm+')')
                #print cmColNames
                if type(cmColNames) == type(''): cmColNames = [cmColNames]
                if cmColNames == 'NULL': cmColNames = []
                #print cmColNames
                cmColNames.insert(0, ' ')
                # self.subsetCMSelector.update(cmColNames)
                # print cmColNames
                cmColNames.extend(self.R('colnames('+self.data+')'))
                self.paintCMSelector.update(cmColNames)
                print cmColNames
            else:
                self.cm = ''            
                cmColNames = self.R('colnames('+self.data+')')
                print cmColNames
                if type(cmColNames) == type(''): cmColNames = [cmColNames]
                if cmColNames == 'NULL': cmColNames = []
                print cmColNames.insert(0, '')
                self.paintCMSelector.update(cmColNames)
                print cmColNames
            # set some of the plot data
            self.xColumnSelector.update(self.R('colnames('+self.data+')'))
            self.yColumnSelector.update(self.R('colnames('+self.data+')'))
            

            self.plot()
    def populateCM(self):
    
        return
        cmSelector = self.subsetCMSelector.currentText()
        
        if cmSelector != ' ':
            command = "levels(as.factor("+self.cm+"[,"+str(self.subsetCMSelector.currentIndex())+"]))"
            try:
                self.R('tmp<-'+command) # must assign to a temp variable because otherwise R fails in the background.  This problem should be reported, and may be fixed in later Rpy releases.
                self.subsetCMClass.update(self.R('tmp'))
            except:
                self.subsetCMClass.clear()
                self.X.setText('Failed')
            #self.subsetCMClass.addItems(self.R('levels(as.factor('+self.cm+'[,"'+cmSelector+'"]))'))
            

    def plot(self):
        # populate the cm class columns
        #cmSelector = str(self.subsetCMSelector.currentText())
        #cmClass = str(self.subsetCMClass.currentText())
        xCol = str(self.xColumnSelector.currentText())
        yCol = str(self.yColumnSelector.currentText())
        paintClass = str(self.paintCMSelector.currentText())
        self.xData = []
        self.yData = []
        if xCol == yCol: return
        self.graph.clear()
        if paintClass not in ['', ' ']: # there is a paintclass selected so we should paint on the levels of the paintclass
            pc = 0
            vectorClass = self.R('class('+self.data+'[,\''+paintClass+'\'])')
            if vectorClass in ['numeric', 'character']: 
                QMessageBox.information(self, 'Red-R Canvas','Class of the paint vector is not appropriate\nfor this widget.',  QMessageBox.Ok + QMessageBox.Default)
                return
            for p in self.R('levels(as.factor('+self.data+'[,\''+paintClass+'\']))'):
                # generate the subset
                subset = '('+self.data+'[,\''+paintClass+'\'] == \''+p+'\')'
                # make a matrix for the levels
                matrix = self.R('as.matrix('+self.data+'['+subset+', c("'+str(xCol)+'", "'+str(yCol)+'")])')
                numArray = numpy.array(matrix)
                self.subset = self.data + '['+subset+',]'
                self.graph.points("MyData", xData = numArray[0:,0], yData = numArray[0:, 1], brushColor = pc, penColor=pc)
                print list(numArray[0:, 0])
                self.xData += list(numArray[0:, 0])
                print self.xData
                self.yData += list(numArray[0:, 1])
                pc += 1
        # make the plot
        
        else:
            matrix = self.R('as.matrix('+self.data + '[, c("'+str(xCol)+'", "'+str(yCol)+'")])')
            numArray = numpy.array(matrix)
            #self.subset = self.data + '['+subset+',]'
            self.graph.points("MyData", xData = numArray[0:,0], yData = numArray[0:, 1])
            self.xData += list(numArray[0:, 0])
            self.yData += list(numArray[0:, 1])
        self.graph.setNewZoom(float(min(self.xData)), float(max(self.xData)), float(min(self.yData)), float(max(self.yData)))
    def sendMe(self):
        data = {'data': self.parent+'['+self.cm+'[,"'+self.Rvariables['Plot']+'"] == 1,]', 'parent':self.parent, 'cm':self.cm} # data is sent forward relative to self parent as opposed to relative to the data that was recieved.  This makes the code much cleaner as recursive subsetting often generates NA's due to restriction.
        self.rSend('Scatterplot Output', data)
        self.sendRefresh()
        
    def widgetDelete(self):
        if self.cm:
            self.R(self.cm+'$'+self.Rvariables['Plot']+'<-NULL') #removes the column for this widget from the CM
            self.sendRefresh()
