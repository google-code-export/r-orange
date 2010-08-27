"""
<name>Remove NA</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:na.omit</RFunctions>
<tags>R</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.signalClasses.RVector import RVector as redRRVector
import libraries.base.signalClasses.RMatrix as rmat
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.widgetLabel import widgetLabel
class na_omit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["na.omit"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', 'object', redRRVariable, self.processobject)

        self.outputs.addOutput('id0', 'R Data Frame', redRRDataFrame)
        self.outputs.addOutput('id1', 'R List', redRRList)
        self.outputs.addOutput('id2', 'R Vector', redRRVector)
        self.outputs.addOutput('id3', 'R.object', redRRVariable)

        
        box = tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.sendStatus = widgetLabel(self.standardTab, 'Nothing Sent')
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processobject(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_object=data.getData()
            self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if str(self.RFunctionParam_object) == '': return
        injection = []
        inj = ','.join(injection)
        self.R(self.Rvariables['na.omit']+'<-na.omit(object='+str(self.RFunctionParam_object)+','+inj+')')
        thisdataclass = self.R('class('+self.Rvariables['na.omit']+')')
        if type(thisdataclass) == list: #this is a special R type so just send as generic
            self.rSend("id3", self.data)
        elif type(thisdataclass) == str:
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                newData = redRRVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id2", newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'character': #we have a character vector as the object
                newData = redRRVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id2", newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'data.frame': # the object is a data.frame
                newData = redRRDataFrame(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id0", newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'matrix': # the object is a matrix
                newData = rmat.RMatrix(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id0", newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'list': # the object is a list
                newData = redRRList(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id1", newData)
                self.sendStatus.setText('Data  sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic
                newData = redRRVariable(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id3", newData)
                self.sendStatus.setText('Data  sent through the R Object channel')
        else:
            newData = redRRVariable(data = self.Rvariables['na.omit'])
            newData.dictAttrs = self.data.dictAttrs.copy()
            self.rSend("id3", newData)
            self.sendStatus.setText('Data  sent through the R Object channel')
            
    def getReportText(self, fileDir):
        return "NA's were removed from the data and the modified data structure was sent to downstream widgets.\n\n"

