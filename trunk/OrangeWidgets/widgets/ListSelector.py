"""
<name>List Selection</name>
<description>Allows viewing of a list and picks parts of a list and sends them.</description>
<tags>Subsetting</tags>
<RFunctions>base:list</RFunctions>
<icon>icons/rexecutor.png</icon>
<author>Kyle R. Covington</author>
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
        self.inputs = [('R List', signals.RList, self.process)]
        self.outputs = [('R Data Frame', signals.RDataFrame), ('R Vector', signals.RVector), ('R List', signals.RList), ('R Variable', signals.RVariable)]
        
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
            print 'Data connected was', data
            self.names.clear()
            for signal in self.outputs:
                self.rSend(signal[0], None)
                
    def sendSelection(self):
        print self.names.selectedItems()[0]
        self.R(self.Rvariables['listelement']+'<-'+self.data+'[['+str(self.names.row(self.names.currentItem())+1)+']]')
        # use signals converter in OWWidget to convert to the signals class
        myclass = self.R('class('+self.Rvariables['listelement']+')')
        print 'myclass',myclass
        if myclass == 'data.frame':
            self.makeCM(self.Rvariables['cm'], self.Rvariables['listelement'])
            newData = signals.RDataFrame(data = self.Rvariables['listelement'], parent = self.Rvariables['listelement'], cm = self.Rvariables['cm'])
            self.rSend('R Data Frame', newData)
            print 'Sent Data Frame'
        elif myclass == 'list':
            newData = signals.RList(data = self.Rvariables['listelement'])
            self.rSend('R List', newData)
            print 'Sent List'
        elif myclass in ['vector', 'character', 'factor', 'logical', 'numeric']:
            newData = signals.RVector(data = self.Rvariables['listelement'])
            self.rSend('R Vector', newData)
            print 'Sent Vector'
        else:
            newData = signals.RVariable(data = self.Rvariables['listelement'])
            self.rSend('R Variable', newData)
