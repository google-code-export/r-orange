"""
<name>Heatmap</name>
<description>Makes heatmaps of data.  This data should be in the form of a data table and should contain only numeric data, no text.  Thought heatmap was designed to work with the Bioconductor package it is able to show any numeric data as a heatmap.  You may use the identify functions to create a collection of subclasses of your data.  This function uses the R identify function and will send two signals; one is the list generated from the selections, the second is a vector of class labels matching the columns of the data.  Clustering is done by columns as this is common in expression data.</description>
<tags>Plotting</tags>
<RFunctions>stats:heatmap</RFunctions>
<icon>heatmap.png</icon>
<priority>2040</priority>
"""

from OWRpy import *
import OWGUI
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RList import RList as redRRList
import libraries.base.signalClasses.RModelFit as rmf
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.spinBox import spinBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.graphicsView import graphicsView
from libraries.base.qtWidgets.radioButtons import radioButtons
class Heatmap(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.setRvariableNames(['heatsubset', 'hclust', 'heatvect'])
        self.plotOnConnect = 0
        self.plotdata = ''
        self.rowvChoice = None
        self.colvChoice = None
        
        self.inputs.addInput('id0', 'Expression Matrix', redRRDataFrame, self.processMatrix)
        self.inputs.addInput('id1', 'Classes Data', redRRVector, self.processClasses)

        #self.outputs.addOutput('id0', 'Cluster Subset List', redRRVector)
        self.outputs.addOutput('id1', 'Cluster Classes', redRRVector)

        

        
        #GUI
        infobox = groupBox(self.controlArea, label = "Options")
        button(self.bottomAreaRight, label = "Replot", callback=self.makePlot, width=200)
        button(infobox, label = 'Identify', callback = self.identify, width=200)
        self.groupOrHeight = radioButtons(infobox, label = 'Identify by:', buttons = ['Groups' , 'Height'], setChecked = 'Groups', orientation = 'horizontal')
        self.groupOrHeightSpin = spinBox(infobox, label = 'Identify Value:', min = 1, value = 5)
        self.startSaturation = spinBox(infobox, label = 'Starting Saturation:', min = 0, max = 100)
        self.endSaturation = spinBox(infobox, label = 'Ending Saturation:', min = 0, max = 100)
        self.endSaturation.setValue(30)
        self.colorTypeCombo = comboBox(infobox, label = 'Color Type:', items = ['rainbow', 'heat.colors', 'terrain.colors', 'topo.colors', 'cm.colors'])
        #self.classesDropdown = comboBox(infobox, label = 'Classes:', toolTip = 'If classes data is connected you may select columns in the data to represent classes of your columns in the plotted data')
        self.rowDendrogram = checkBox(infobox, buttons = ['Plot Row Dendrogram', 'Plot Column Dendrogram'], setChecked = ['Plot Row Dendrogram', 'Plot Column Dendrogram'])
        self.plotOnConnect = checkBox(infobox, buttons=['Plot on Connect'])
        self.showClasses = checkBox(infobox, buttons = ['Show Classes'])
        self.showClasses.setEnabled(False)
        #OWGUI.checkBox(infobox, self, )
        self.infoa = widgetLabel(infobox, label = "Nothing to report")
        self.gview1 = graphicsView(self.controlArea)
        self.gview1.image = 'heatmap1_'+self.widgetID
        self.gview2 = graphicsView(self.controlArea)
        self.gview2.image = 'heatmap2_'+self.widgetID
        
    def onLoadSavedSession(self):
        print 'load heatmap'
        self.processSignals()
    def processMatrix(self, data =None):
        
        if data:
            self.plotdata = data.getData()
            if data.optionalDataExists('classes'):
                self.classes = data.getOptionalData('classes')
                self.showClasses.setEnabled(True)
            else:
                self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
            if self.R('class('+self.plotdata+')') == "data.frame":
                self.plotdata = 'data.matrix('+self.plotdata+')'
            self.rowvChoiceprocess()
            if not self.R('is.numeric('+self.plotdata+')'):
                self.status.setText('Data connected was not numeric')
                self.plotdata = ''
            if 'Plot on Connect'  in self.plotOnConnect.getChecked():
                self.makePlot()
        else: 
            self.plotdata = ''
    def processClasses(self, data):
        if data:
            self.classesData = data.getData()
            #self.classesDropdown.update(self.R('colnames('+data.data+')', wantType = 'list'))
            self.showClasses.setEnabled(True)
        else:
            #self.classesDropdown.clear()
            self.classesData = ''
    def makePlot(self):
        if self.plotdata == '': return
        self.status.setText("You are plotting "+self.plotdata)
        # if str(self.classesDropdown.currentText()) != '':
            # self.classes = self.classesData+'[,\''+str(self.classesDropdown.currentText()) + '\']'
        if 'Show Classes' in self.showClasses.getChecked():
            colClasses = ', ColSideColors=' + self.classesData + ''
        else:
            colClasses = ''
        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rev(rainbow(50, start = '+str(start)+', end = '+str(end)+'))'
        else:
            col = colorType+'(50)'
        if 'Plot Row Dendrogram' in self.rowDendrogram.getChecked():
            self.rowvChoice = 'NULL'
        else:
            self.rowvChoice = 'NA'
        if 'Plot Column Dendrogram' in self.rowDendrogram.getChecked():
            self.colvChoice = 'NULL'
        else:
            self.colvChoice = 'NA'
        self.R('tempPalette<-colorRampPalette(c('+','.join(self.listOfColors)+'))', wantType = 'NoConversion')
        self.gview1.plot(function = 'heatmap', query = self.plotdata+', Rowv='+self.rowvChoice+', Colv = '+self.colvChoice+', col= tempPalette(50)'+ colClasses+'')
        # for making the pie plot
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rev(rainbow(10, start = '+str(start)+', end = '+str(end)+'))'
        else:
            col = colorType+'(10)'
        #self.R('dev.new()')
        self.gview2.plot(query = 'rep(1, 10), labels = c(\'Low\', 2:9, \'High\'), col = '+col+'', function = 'pie')
        
    def rowvChoiceprocess(self):
        if self.plotdata:
            rowlen = self.R('length(rownames('+self.plotdata+'))')
            if rowlen > 1000:
                self.rowvChoice = 'NA'
            else:
                self.rowvChoice = 'NULL'
                
    def identify(self, kill = True):
        if self.plotdata == '': return
        ## needs to be rewritten for Red-R 1.85 which uses rpy3.  no interactivity with graphics.
        
        self.R(self.Rvariables['hclust']+'<-hclust(dist(t('+self.plotdata+')))', wantType = 'NoConversion')
        
        
        ## now there is a plot the user must select the number of groups or the height at which to make the slices.
        print str(self.groupOrHeight.getChecked())
        if str(self.groupOrHeight.getChecked()) == 'Groups':
            inj = 'k = ' + str(self.groupOrHeightSpin.value())
        else:
            inj = 'h = ' + str(self.groupOrHeightSpin.value())
        self.R(self.Rvariables['heatsubset']+'<-cutree('+self.Rvariables['hclust']+', '+inj+')', wantType = 'NoConversion')       
        self.gview1.plotMultiple(query = self.Rvariables['hclust']+',col = %s' % self.Rvariables['heatsubset'], layers = ['rect.hclust(%s, %s, cluster = %s, which = 1:%s, border = 2:(%s + 1))' % (self.Rvariables['hclust'], inj, self.Rvariables['heatsubset'], self.groupOrHeightSpin.value(), self.groupOrHeightSpin.value())])
        newData = redRRVector(data = 'as.vector('+self.Rvariables['heatsubset']+')', parent = self.Rvariables['heatsubset'])
        self.rSend("id1", newData)
        
        
    
class colorListDialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical', title = 'Color List Dialog', data = ''):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        
        self.listOfColors = []
        self.controlArea = redRWidgetBox(self)
        mainArea = redRWidgetBox(self.controlArea, 'horizontal')
        leftBox = redRWidgetBox(mainArea)
        rightBox = redRWidgetBox(mainArea)
        ## GUI
        
        # color list
        self.colorList = redRListBox(leftBox, label = 'Color List')
        redRButton(leftBox, label = 'Add Color', callback = self.addColor)
        redRButton(leftBox, label = 'Remove Color', callback = self.removeColor)
        redRButton(leftBox, label = 'Clear Colors', callback = self.colorList.clear)
        redRButton(mainArea, label = 'Finished', callback = self.accept)
        # attribute list
        
        if data:
            self.attsList = listBox(rightBox, label = 'Data Parameters', callback = self.attsListSelected)
            names = self.R('names('+data+')')
            print names
            self.attsList.update(names)
        self.data = data
    def attsListSelected(self):
        ## return a list of numbers coresponding to the levels of the data selected.
        self.listOfColors = self.R('as.numeric(as.factor('+self.data+'$'+str(self.attsList.selectedItems()[0].text())+'))')
        
    def addColor(self):
        colorDialog = QColorDialog(self)
        color = colorDialog.getColor()
        colorDialog.hide()
        newItem = QListWidgetItem()
        newItem.setBackgroundColor(color)
        self.colorList.addItem(newItem)
        
        self.processColors()
    def removeColor(self):
        for item in self.colorList.selectedItems():
            self.colorList.removeItemWidget(item)
            
        self.processColors()
    def setColors(self, colorList):
        self.colorList.clear()
        try:
            for c in colorList:
                col = QColor()
                col.setNamedColor(str(c))
                newItem = QListWidgetItem()
                newItem.setBackgroundColor(col)
                self.colorList.addItem(newItem)
        except:
            pass # it might happen that we can't show the colors that's not good but also not disasterous either.
    def processColors(self):
        self.listOfColors = []
        for item in self.colorList.items():
            self.listOfColors.append('"'+str(item.backgroundColor().name())+'"')
    def R(self, query):
        return RSession.Rcommand(query = query)

