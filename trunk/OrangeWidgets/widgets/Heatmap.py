"""
<name>Heatmap</name>
<description>Makes heatmaps of data.  This data should be in the form of a data table and should contain only numeric data, no text.  Thought heatmap was designed to work with the Bioconductor package it is able to show any numeric data as a heatmap.</description>
<tags>Plotting</tags>
<RFunctions>stats:heatmap</RFunctions>
<icon>icons/heatmap.png</icon>
<priority>2040</priority>
"""

from OWRpy import *
import OWGUI

class Heatmap(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.setRvariableNames(['heatsubset', 'hclust'])
        self.plotOnConnect = 0
        self.plotdata = ''
        self.rowvChoice = None
        self.loadSettings()
        self.inputs = [("Expression Matrix", RvarClasses.RRectangularData, self.processMatrix)]
        self.outputs = [("Cluster Subset List", RvarClasses.RList)]
        

        
        #GUI
        infobox = redRGUI.groupBox(self.controlArea, label = "Options")
        redRGUI.button(self.bottomAreaRight, label = "Replot", callback=self.makePlot, width=200)
        redRGUI.button(infobox, label = 'Save as PDF', callback = self.saveAsPDF)
        redRGUI.button(infobox, label = 'Identify', callback = self.identify, width=200)
        self.startSaturation = redRGUI.spinBox(infobox, label = 'Starting Saturation:', min = 0, max = 100)
        self.endSaturation = redRGUI.spinBox(infobox, label = 'Ending Saturation:', min = 0, max = 100)
        self.endSaturation.setValue(30)
        self.colorTypeCombo = redRGUI.comboBox(infobox, label = 'Color Type:', items = ['rainbow', 'heat.colors', 'terrain.colors', 'topo.colors', 'cm.colors'])
        self.plotOnConnect = redRGUI.checkBox(infobox, buttons=['Plot on Connect'])
        self.showClasses = redRGUI.checkBox(infobox, buttons = ['Show Classes'])
        self.showClasses.setEnabled(False)
        #OWGUI.checkBox(infobox, self, )
        self.infoa = redRGUI.widgetLabel(infobox, label = "Nothing to report")
        
    def onLoadSavedSession(self):
        print 'load heatmap'
        self.processSignals()
    def saveAsPDF(self):
        self.status.setText('Saving as PDF')
        if self.classes and ('Show Classes' in self.showClasses.getChecked()):
            colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
        else:
            colClasses = ''
        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            col = 'rainbow(50, start = '+str(self.startSaturation.value()/100)+', end = '+str(self.endSaturation.value()/100)+')'
        else:
            col = colorType+'(50)'
        self.savePDF('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')')
        #self.stats.setText('File Saved')
    def processMatrix(self, data =None):
        
        if data:
            self.plotdata = data['data']
            if 'classes' in data.dictAttrs:
                self.classes = data.dictAttrs['classes']
                self.showClasses.setEnabled(True)
            else:
                self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
            if self.R('class('+self.plotdata+')') == "data.frame":
                self.plotdata = 'data.matrix('+self.plotdata+')'
            self.rowvChoiceprocess()
            if 'Plot on Connect'  in self.plotOnConnect.getChecked():
                self.makePlot()
        else: 
            self.Rplot('par(mfrow=c(1,1))')

    def makePlot(self):
        if self.plotdata == '': return
        self.status.setText("You are plotting "+self.plotdata)
        if self.classes and ('Show Classes' in self.showClasses.getChecked()):
            colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
        else:
            colClasses = ''
        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rainbow(50, start = '+str(start)+', end = '+str(end)+')'
        else:
            col = colorType+'(50)'
        self.Rplot('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')', 3, 4)
        # for making the pie plot
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rainbow(10, start = '+str(start)+', end = '+str(end)+')'
        else:
            col = colorType+'(10)'
        self.Rplot('pie(rep(1, 10), labels = c(\'Low\', 2:9, \'High\'), col = '+col+')', devNumber = 2)
        
    def rowvChoiceprocess(self):
        if self.plotdata:
            rowlen = self.R('length(rownames('+self.plotdata+'))')
            if rowlen > 1000:
                self.rowvChoice = 'NA'
            else:
                self.rowvChoice = 'NULL'
                
    def identify(self, kill = True):
        if self.plotdata == '': return
        
        self.R(self.Rvariables['hclust']+'<-hclust(dist(t('+self.plotdata+')))')
        self.Rplot('plot('+self.Rvariables['hclust']+')', devNumber = 1)
        self.R(self.Rvariables['heatsubset']+'<-lapply(identify('+self.Rvariables['hclust']+'),names)')        
        
        newData = RvarClasses.RList(data = self.Rvariables['heatsubset'], parent = self.Rvariables['heatsubset'])
        hclust = RvarClasses.RModelFit(data = self.Rvariables['hclust'])
        newData.dictAttrs['cluster'] = hclust
        self.rSend("Cluster Subset List", newData)
