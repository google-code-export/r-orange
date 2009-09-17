"""
<name>Heatmap</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/HeatMap.png</icon>
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
        
        self.inputs = [("Expression Matrix", RvarClasses.RDataFrame, self.processMatrix)]
        self.outputs = [("Cluster Subset", RvarClasses.RList)]
        
        self.rowvChoice = None
        
        #GUI
        infobox = OWGUI.widgetBox(self.controlArea, "Options")
        OWGUI.button(infobox, self, "Replot", callback=self.makePlot, width=200)
        OWGUI.button(infobox, self, 'Identify', callback = self.identify, width=200)
        OWGUI.checkBox(infobox, self, 'plotOnConnect', 'Plot on Connect')
        #OWGUI.checkBox(infobox, self, )
        self.infoa = OWGUI.widgetLabel(infobox, "Nothing to report")
        
        
    def onLoadSavedSession(self):
        print 'load heatmap'
        self.processSignals()

    def processMatrix(self, data):
        if data:
            self.plotdata = data['data']
            if 'classes' in data:
                self.classes = data['classes']
            else:
                self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
            if self.rsession('class('+self.plotdata+')') == "data.frame":
                self.plotdata = 'as.matrix('+self.plotdata+')'
            self.rowvChoiceprocess()
            if self.plotOnConnect:
                self.makePlot()
        else: 
            self.Rplot('par(mfrow=c(1,1))')

    def makePlot(self):
        #self.require_libraries([heatmap.plus])
        self.infoa.setText("You are plotting "+self.plotdata)
        self.Rplot('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', ColSideColors=rgb(t(col2rgb('+self.classes+'+2)), maxColorValue=255), col= topo.colors(50))', 3, 4)
        
    def rowvChoiceprocess(self):
        if self.plotdata:
            rowlen = self.rsession('length(rownames('+self.plotdata+'))')
            if rowlen > 1000:
                self.rowvChoice = 'NA'
            else:
                self.rowvChoice = 'NULL'
                
    def identify(self, kill = True):
        self.R(self.Rvariables['hclust']+'<-hclust(dist(t('+self.plotdata+')))')
        self.Rplot('plot('+self.Rvariables['hclust']+')', devNumber = 1)
        self.R(self.Rvariables['heatsubset']+'<-identify('+self.Rvariables['hclust']+')')
        self.rSend("Cluster Subset", {'data':self.Rvariables['heatsubset'], 'kill':kill, 'cluster':self.Rvariables['hclust']})
