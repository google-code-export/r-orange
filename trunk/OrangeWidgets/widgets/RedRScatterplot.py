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

        # GUI
        self.xColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'X data', items=[], callback = self.plot, callback2 = self.refresh)
        self.yColumnSelector = redRGUI.comboBox(self.GUIDialog, label = 'Y data', items=[], callback = self.plot, callback2 = self.refresh)
        self.paintCMSelector = redRGUI.comboBox(self.GUIDialog, label = 'Color Points By:', items = [''], callback = self.plot)
        self.paintLegend = redRGUI.textEdit(self.GUIDialog)
        self.paintLegend.hide()
        
        # plot area
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
        xData = self.R('as.matrix(t('+self.data+'[,\''+str(self.xColumnSelector.currentText())+'\']))')
        yData = self.R('as.matrix(t('+self.data+'[,\''+str(self.yColumnSelector.currentText())+'\']))')
        if type(xData) in [numpy.ndarray]:
           xData = xData[0]
           yData = yData[0]
        print type(xData), 'Data type'   
        print xData
        selected, unselected = self.graph.getSelectedPoints(xData = xData, yData = yData)
        if self.cm == None or self.cm == '':
           newData = self.dataParent.copy()
           newData['data'] = self.data+'[c('+str(selected)[1:-1]+'),]'
           self.rSend('Scatterplot Output', newData)
        else:
           self.R(self.cm+'[,"'+self.Rvariables['Plot']+'"]<-rep(0, length('+self.cm+'[,1]))')
           self.R(self.cm+'[rownames('+self.data+'),"'+self.Rvariables['Plot']+'"]<-c('+str(selected)[1:-1]+')')
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
            self.paintLegend.clear()
            self.paintLegend.show()
            pc = 0
            if paintClass in self.R('colnames('+self.data+')'): # the data comes from the parent data frame and not the cm
                d = self.data
                vectorClass = self.R('class('+self.data+'[,\''+paintClass+'\'])')
                if vectorClass in ['character']: 
                    QMessageBox.information(self, 'Red-R Canvas','Class of the paint vector is not appropriate\nfor this widget.',  QMessageBox.Ok + QMessageBox.Default)
                    print vectorClass
                    return
                    
                elif vectorClass in ['numeric']:
                    numericLevels = True
                else:
                    numericLevels = False
                levels = self.R('levels(as.factor('+self.data+'[,\''+paintClass+'\']))')
            else: # we made it this far so the data must be in the cm
                d = self.cm                
                vectorClass = self.R('class('+self.cm+'[,\''+paintClass+'\'])')                
                if vectorClass in ['character']: 
                    QMessageBox.information(self, 'Red-R Canvas','Class of the paint vector is not appropriate\nfor this widget.',  QMessageBox.Ok + QMessageBox.Default)
                    print vectorClass                    
                    return
                elif vectorClass in ['numeric']:
                    numericLevels = True
                else:
                    numericLevels = False
                levels = self.R('levels(as.factor('+self.cm+'[,\''+paintClass+'\']))', wantType = 'list')    
            print levels            
            color = 0
            self.paintLegend.insertHtml('<h5>Color Legend</h5>')
            self.paintLegend.insertHtml('<table class="reference" cellspacing="0" border="1" width="100%"><tr><th align="left" width="25%">Color</th><th align="left" width="75%">Group Name</th></tr>')
            for p in levels:
                # collect the color
                lColor = self.setColor(color)
                self.paintLegend.insertHtml('<tr><td width = "25%" bgcolor = \"'+lColor+'\">&nbsp;</td><td width = "75%">'+p+'</td></tr>')
                color += 1
                # generate the subset
                if not numericLevels:
                    subset = '('+d+'[,\''+paintClass+'\'] == \''+p+'\')'
                else: 
                    subset = '('+d+'[,\''+paintClass+'\'] == as.numeric('+p+'))'
                # make a list of points
                # check if the column is a factor
                if self.R('class('+self.data+'[,\''+str(xCol)+'\'])') in ['factor']:
                    xData = self.R('match('+self.data+'['+subset+',\''+str(xCol)+'\'], levels('+self.data+'[,\''+str(xCol)+'\']))', wantType = 'list')
                else:
                    xData = self.R(self.data+'['+subset+',\''+str(xCol)+'\']', wantType = 'list')
                if self.R('class('+self.data+'[,\''+str(yCol)+'\'])') in ['factor']:
                    yData = self.R('match('+self.data+'['+subset+',\''+str(yCol)+'\'], levels('+self.data+'[,\''+str(yCol)+'\']))', wantType = 'list')
                else:
                    yData = self.R(self.data+'['+subset+',\''+str(yCol)+'\']', wantType = 'list')
                
                self.graph.points("MyData", xData = xData, yData = yData, brushColor = pc, penColor=pc)
                self.xData += xData
                self.yData += yData
                pc += 1
            self.paintLegend.insertHtml('</table>')
        # make the plot
        
        else:
            self.paintLegend.hide()
            # check if the column is a factor
            if self.R('class('+self.data+'[,\''+str(xCol)+'\'])') in ['factor']:
                xData = self.R('match('+self.data+'[,\''+str(xCol)+'\'], levels('+self.data+'[,\''+str(xCol)+'\']))', wantType = 'list')
            else:
                xData = self.R(self.data+'[,\''+str(xCol)+'\']', wantType = 'list')
            if self.R('class('+self.data+'[,\''+str(yCol)+'\'])') in ['factor']:
                yData = self.R('match('+self.data+'[,\''+str(yCol)+'\'], levels('+self.data+'[,\''+str(yCol)+'\']))', wantType = 'list')
            else:
                yData = self.R(self.data+'[,\''+str(yCol)+'\']', wantType = 'list')
            
            self.graph.points("MyData", xData = xData, yData = yData)
            self.xData += xData
            self.yData += yData

        self.graph.setNewZoom(float(min(self.xData)), float(max(self.xData)), float(min(self.yData)), float(max(self.yData)))
    def sendMe(self):
        data = {'data': self.parent+'['+self.cm+'[,"'+self.Rvariables['Plot']+'"] == 1,]', 'parent':self.parent, 'cm':self.cm} # data is sent forward relative to self parent as opposed to relative to the data that was recieved.  This makes the code much cleaner as recursive subsetting often generates NA's due to restriction.
        self.rSend('Scatterplot Output', data)
        self.sendRefresh()
    def loadCustomSettings(self, settings = None):
        # custom function to replot the data that is in the scatterplot
        self.plot()
    def widgetDelete(self):
        if self.cm:
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