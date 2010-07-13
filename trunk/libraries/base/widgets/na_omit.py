"""
<name>Remove NA</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:na.omit</RFunctions>
<tags>R</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RVariable as rvar
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RVector as rvec
import libraries.base.signalClasses.RMatrix as rmat
class na_omit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["na.omit"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs = [("object", signals.RVariable, self.processobject)]
        self.outputs = [('R Data Frame', rdf.RDataFrame), ('R List', rlist.RList), ('R Vector', rvec.RVector), ('R.object', rvar.RVariable)]
        
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.sendStatus = redRGUI.widgetLabel(self.standardTab, 'Nothing Sent')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
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
            self.rSend('R.object', self.data)
        elif type(thisdataclass) == str:
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                newData = rvec.RVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Vector', newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'character': #we have a character vector as the object
                newData = rvec.RVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Vector', newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'data.frame': # the object is a data.frame
                newData = rdf.RDataFrame(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Data Frame', newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'matrix': # the object is a matrix
                newData = rmat.RMatrix(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Data Frame', newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'list': # the object is a list
                newData = rlist.RList(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R List', newData)
                self.sendStatus.setText('Data  sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic
                newData = rvar.RVariable(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R.object', newData)
                self.sendStatus.setText('Data  sent through the R Object channel')
        else:
            newData = rvar.RVariable(data = self.Rvariables['na.omit'])
            newData.dictAttrs = self.data.dictAttrs.copy()
            self.rSend('R.object', newData)
            self.sendStatus.setText('Data  sent through the R Object channel')

