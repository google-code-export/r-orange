"""
<name>List Selection</name>
<description>Allows viewing of a list and picks parts of a list and sends them.</description>
<tags>Subsetting</tags>
<RFunctions>base:list</RFunctions>
<icon>rexecutor.png</icon>
<author>Kyle R. Covington</author>
"""

from OWRpy import *
import redRGUI
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable

from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
class ListSelector(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        #self.selection = 0
        self.setRvariableNames(['cm', 'listelement'])
        self.data = None
        
        self.inputs.addInput('id0', 'R List', redRRList, self.process)

        self.outputs.addOutput('id0', 'R Data Frame', redRRDataFrame)
        self.outputs.addOutput('id1', 'R Vector', redRRVector)
        self.outputs.addOutput('id2', 'R List', redRRList)
        self.outputs.addOutput('id3', 'R Variable', redRRVariable)
        self.outputs.addOutput('id4', 'R Matrix', redRRMatrix)

        
        #GUI
        box = groupBox(self.controlArea, "List Data")
        self.infoa = widgetLabel(self.controlArea, '')
        self.names = listBox(box, callback = self.sendSelection)
        
    def process(self, data):
        self.data = None
        
        if data:
            self.data = data.getData()
            names = self.R('names('+self.data+')')
            print str(names)
            if names == None:
                names = range(1, self.R('length('+self.data+')')+1)
                print names
            self.names.update(names)
        else:
            self.names.clear()
            for signal in self.outputs.outputIDs():
                self.rSend(signal[0], None)
                
    def sendSelection(self):
        print self.names.selectedItems()[0]
        self.Rvariables['listelement'] = self.data+'[['+str(self.names.row(self.names.currentItem())+1)+']]'
        # use signals converter in OWWidget to convert to the signals class
        myclass = self.R('class('+self.Rvariables['listelement']+')')
        if myclass == 'data.frame':
            self.makeCM(self.Rvariables['cm'], self.Rvariables['listelement'])
            newData = redRRDataFrame(data = self.Rvariables['listelement'], parent = self.Rvariables['listelement'], cm = self.Rvariables['cm'])
            self.rSend("id0", newData)
            self.infoa.setText('Sent Data Frame')
        elif myclass == 'list':
            newData = redRRList(data = self.Rvariables['listelement'])
            self.rSend("id2", newData)
            self.infoa.setText('Sent List')
        elif myclass in ['vector', 'character', 'factor', 'logical', 'numeric', 'integer']:
            newData = redRRVector(data = self.Rvariables['listelement'])
            self.rSend("id1", newData)
            self.infoa.setText('Sent Vector')
        elif myclass in ['matrix']:
            newData = redRRMatrix(data = self.Rvariables['listelement'])
            self.rSend("id4", newData)
            self.infoa.setText('Sent Matrix')
        else:
            newData = redRRVariable(data = self.Rvariables['listelement'])
            self.rSend("id3", newData)
            self.infoa.setText('Send Variable', myclass)
    def getReportText(self, fileDir):
        return 'The %s element of the incomming data was sent.\n\n' % (self.Rvariables['listelement'])