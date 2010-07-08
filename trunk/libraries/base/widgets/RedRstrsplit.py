"""
<name>RedRstrsplit</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Split a vector of data by some text.  Returns a list of data containing the split results for each element in the vector and an optional vector of data of all of the splits pasted together.</description>
<RFunctions>base:strsplit</RFunctions>
<tags>Prototypes</tags>
<inputWidgets></inputWidgets>
<outputWidgets>base_summary, base_ListSelector</outputWidgets>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
class RedRstrsplit(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "strsplit", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["strsplit"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs = [("x", signals.RVector.RVector, self.processx)]
        self.outputs = [("strsplit Output", signals.RList.RList), ('strsplit Vector', signals.RVector.RVector)]
        
        self.RFunctionParamsplit_lineEdit =  redRGUI.lineEdit(self.controlArea,  label = "Split Text Using:", text = '')
        self.RFunctionParamfixed_radioButtons =  redRGUI.radioButtons(self.controlArea,  label = "fixed:", buttons = ['Use text exactly', 'Use text as expression (Advanced)'], setChecked = 'Use text exactly', orientation = 'horizontal')
        self.RFunctionParamextended_radiButtons =  redRGUI.radioButtons(self.controlArea,  label = "Extend Expressions:", buttons = ['Yes', 'No'], setChecked = 'No', orientation = 'horizontal')
        self.RFunctionParamperl_radioButtons =  redRGUI.radioButtons(self.controlArea,  label = "'Use Perl Expressions':", buttons = ['Yes', 'No'], setChecked = 'No', orientation = 'horizontal')
        self.RFunctionParamunlist_radioButtons = redRGUI.radioButtons(self.controlArea, label = 'Convert to RVector', buttons = ['Send only the list', 'Send list and vector'], setChecked = 'Send list and vector', orientation = 'horizontal')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': 
            self.status.setText('No Data to Split')
            return
        if str(self.RFunctionParamsplit_lineEdit.text()) == '':
            self.status.setText('No string to split on')
            return
        injection = []
        if str(self.RFunctionParamfixed_radioButtons.getChecked()) == 'Yes':
            string = 'fixed=TRUE'
            injection.append(string)
        else:
            string = 'fixed=FALSE'
            injection.append(string)
        if str(self.RFunctionParamextended_radiButtons.getChecked()) == 'Yes':
            string = 'extended=TRUE'
            injection.append(string)
        else:
            string = 'extended=FALSE'
            injection.append(string)
        if str(self.RFunctionParamsplit_lineEdit.text()) != '':
            string = 'split='+str(self.RFunctionParamsplit_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamperl_radioButtons.getChecked()) == 'Yes':
            string = 'perl=TRUE'
            injection.append(string)
        else:
            string = 'perl=FALSE'
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['strsplit']+'<-strsplit(x= as.character('+str(self.RFunctionParam_x)+') ,'+inj+')')
        newData = signals.RList.RList(data = self.Rvariables["strsplit"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("strsplit Output", newData)
        
        if str(self.RFunctionParamunlist_radioButtons.getChecked()) == 'Send list and vector':
            newData = signals.RVector.RVector(data = 'unlist('+self.Rvariables['strsplit']+')')
            self.rSend('strsplit Vector', newData)
