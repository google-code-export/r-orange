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
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["na.omit"])
        self.data = {}
        self.require_librarys(["base"]) 
        self.loadSettings() 
        self.RFunctionParam_object = ''
        self.inputs = [("object", RvarClasses.RVariable, self.processobject)]
        self.outputs = [('R Data Frame', RvarClasses.RDataFrame), ('R List', RvarClasses.RList), ('R Vector', RvarClasses.RVector), ('R.object', RvarClasses.RVariable)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.sendStatus = redRGUI.widgetLabel(self.standardTab, 'Nothing Sent')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
    def processobject(self, data):
        
        if data:
            self.RFunctionParam_object=data["data"]
            self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if str(self.RFunctionParam_object) == '': return
        injection = []
        inj = ','.join(injection)
        self.R(self.Rvariables['na.omit']+'<-na.omit(object='+str(self.RFunctionParam_object)+','+inj+')')
        self.data["data"] = self.Rvariables["na.omit"]
        self.data["parent"] = self.Rvariables["na.omit"]
        thisdataclass = self.R('class('+self.data["data"]+')')
        if type(thisdataclass) == list: #this is a special R type so just send as generic
            self.rSend('R.object', self.data)
        elif type(thisdataclass) == str:
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                self.rSend('R Vector', self.data)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'character': #we have a character vector as the object
                self.rSend('R Vector', self.data)
                self.sendStatus.setText('Data  sent through the R Vector channel')
            elif thisdataclass == 'data.frame': # the object is a data.frame
                self.R('cm_'+self.data['data']+'<-data.frame(row.names = rownames('+self.data['data']+'))')
                self.data['cm'] = 'cm_'+self.data['data']
                self.rSend('R Data Frame', self.data)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'matrix': # the object is a matrix
                self.R('cm_'+self.data['data']+'<-data.frame(row.names = rownames('+self.data['data']+'))')
                self.data['cm'] = 'cm_'+self.data['data']
                self.rSend('R Data Frame', self.data)
                self.sendStatus.setText('Data  sent through the R Data Frame channel')
            elif thisdataclass == 'list': # the object is a list
                self.rSend('R List', self.data)
                self.sendStatus.setText('Data  sent through the R List channel')
            else:    # the data is of a non-normal type send anyway as generic
                self.rSend('R.object', self.data)
                self.sendStatus.setText('Data  sent through the R Object channel')
        else:
            self.rSend('R.object', self.data)
            self.sendStatus.setText('Data  sent through the R Object channel')
    def compileReport(self):
        self.reportSettings("Input Settings",[("object", self.RFunctionParam_object)])
        self.reportRaw(self.Rvariables["na.omit"])
    def sendReport(self):
        self.compileReport()
        self.showReport()
