"""
<name>na.omit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>base:na.omit</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class na_omit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "NA Omit", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["na.omit"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs = [("object", signals.RVariable, self.processobject)]
        self.outputs = [('R Data Frame', signals.RDataFrame), ('R List', signals.RList), ('R Vector', signals.RVector), ('R.object', signals.RVariable)]
        
        self.help.setHtml('<small>NA omit removes NA\'s from data tables.  This way other functions can work better by not having pesky NA\'s lying around.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.sendStatus = redRGUI.widgetLabel(self.standardTab, 'Nothing Sent')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processobject(self, data):
        self.require_librarys(["base"]) 
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
                newData = signals.RVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Vector', newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'character': #we have a character vector as the object
                newData = signals.RVector(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Vector', newData)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'data.frame': # the object is a data.frame
                newData = signals.RDataFrame(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Data Frame', newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'matrix': # the object is a matrix
                newData = signals.RMatrix(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R Data Frame', newData)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'list': # the object is a list
                newData = signals.RList(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R List', newData)
                self.sendStatus.setText('Data  sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic
                newData = signals.RVariable(data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend('R.object', newData)
                self.sendStatus.setText('Data  sent through the R Object channel')
        else:
            newData = signals.RVariable(data = self.Rvariables['na.omit'])
            newData.dictAttrs = self.data.dictAttrs.copy()
            self.rSend('R.object', newData)
            self.sendStatus.setText('Data  sent through the R Object channel')

