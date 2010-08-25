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
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVector as rvec
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RMatrix as rmat
import libraries.base.signalClasses.RVariable as rvar

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
        
        self.inputs = [('R List', rlist.RList, self.process)]
        self.outputs = [('R Data Frame', rdf.RDataFrame), ('R Vector', rvec.RVector), ('R List', rlist.RList), ('R Variable', rvar.RVariable), ('R Matrix', rmat.RMatrix)]
        
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
            for signal in self.outputs:
                self.rSend(signal[0], None)
                
    def sendSelection(self):
        print self.names.selectedItems()[0]
        self.Rvariables['listelement'] = self.data+'[['+str(self.names.row(self.names.currentItem())+1)+']]'
        # use signals converter in OWWidget to convert to the signals class
        myclass = self.R('class('+self.Rvariables['listelement']+')')
        if myclass == 'data.frame':
            self.makeCM(self.Rvariables['cm'], self.Rvariables['listelement'])
            newData = rdf.RDataFrame(data = self.Rvariables['listelement'], parent = self.Rvariables['listelement'], cm = self.Rvariables['cm'])
            self.rSend('R Data Frame', newData)
            self.infoa.setText('Sent Data Frame')
        elif myclass == 'list':
            newData = rlist.RList(data = self.Rvariables['listelement'])
            self.rSend('R List', newData)
            self.infoa.setText('Sent List')
        elif myclass in ['vector', 'character', 'factor', 'logical', 'numeric', 'integer']:
            newData = rvec.RVector(data = self.Rvariables['listelement'])
            self.rSend('R Vector', newData)
            self.infoa.setText('Sent Vector')
        elif myclass in ['matrix']:
            newData = rmat.RMatrix(data = self.Rvariables['listelement'])
            self.rSend('R Matrix', newData)
            self.infoa.setText('Sent Matrix')
        else:
            newData = rvar.RVariable(data = self.Rvariables['listelement'])
            self.rSend('R Variable', newData)
            self.infoa.setText('Send Variable', myclass)
    def getReportText(self, fileDir):
        return 'The %s element of the incomming data was sent.\n\n' % (self.Rvariables['listelement'])