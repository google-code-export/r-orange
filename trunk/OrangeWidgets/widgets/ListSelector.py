"""
<name>List Selector</name>
<description>Allows viewing of a list and picks parts of a list and sends them.</description>
<tags>Data Exploration and Visualization</tags>
<RFunctions>base:list</RFunctions>
<icon>icons/rexecutor.png</icon>
<author>Kyle R. Covington</author>
<priority>3010</priority>
"""

from OWRpy import *
import redRGUI

class ListSelector(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "ListSelector", wantMainArea = 0, resizingEnabled = 1)
        
        #self.selection = 0
        self.setRvariableNames(['cm', 'listelement'])
        self.data = None
        self.loadSettings()
        self.inputs = [('R List', RvarClasses.RList, self.process)]
        self.outputs = [('R Data Frame', RvarClasses.RDataFrame), ('R Vector', RvarClasses.RVector), ('R List', RvarClasses.RList)]
        
        #GUI
        box = redRGUI.groupBox(self.controlArea, "List Data")
        self.names = redRGUI.listBox(box, callback = self.sendSelection)
        
    def process(self, data):
        self.data = None
        if data:
            self.data = data['data']
            names = self.R('names('+self.data+')')
            print str(names)
            if names == None:
                names = range(1, self.R('length('+self.data+')')+1)
                print names
            self.names.update(names)
        else:
            self.name.clear()
            for signal in self.outputs:
                self.rSend(signal[0], None)
                
    def sendSelection(self):
        print self.names.selectedItems()[0]
        self.R(self.Rvariables['listelement']+'<-'+self.data+'[['+str(self.names.row(self.names.currentItem())+1)+']]')
        myclass = self.R('class('+self.Rvariables['listelement']+')')
        if myclass == 'data.frame':
            self.makeCM(self.Rvariables['cm'], self.Rvariables['listelement'])
            self.rSend('R Data Frame', {'data':self.Rvariables['listelement'], 'parent':self.Rvariables['listelement'], 'cm':self.Rvariables['cm']})
            print 'Sent Data Frame'
        elif myclass == 'list':
            self.rSend('R List', {'data':self.Rvariables['listelement']})
            print 'Sent List'
        elif myclass == 'vector' or myclass == 'character':
            self.rSend('R Vector', {'data':self.Rvariables['listelement']})
            print 'Sent Vector'