"""
<name>Correlation</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:cor</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class cor(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["cor"])
        self.data = {}
        self.loadSettings() 
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs = [("x", RvarClasses.RDataFrame, self.processx),("y", RvarClasses.RVector, self.processy)]
        self.outputs = [("cor Output", RvarClasses.RMatrix)]
        
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamuse_lineEdit =  redRGUI.lineEdit(self.advancedTab, label = "use:")
        self.RFunctionParammethod_comboBox =  redRGUI.comboBox(self.standardTab,  label = "method:", items = ['pearson', 'kendall', 'spearman'])
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processy(self, data):
        self.require_librarys(["stats"]) 
        if data:
            self.RFunctionParam_y=data.data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        self.require_librarys(["stats"]) 
        if data:
            self.RFunctionParam_x=data.data
            dims = self.R('dim('+self.RFunctionParam_x+')', silent = True, wantType = 'list')
            if dims[0] == 1 or dims[1] == 1:
                self.RFunctionParam_x = 'as.vector('+self.RFunctionParam_x+')'
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_x) == '': return
        
        injection = []
        if str(self.RFunctionParamuse_lineEdit.text()) != '':
            string = 'use=\''+str(self.RFunctionParamuse_lineEdit.text())+'\''
            injection.append(string)
        if str(self.RFunctionParammethod_comboBox.currentText()) != '':
            string = 'method=\''+str(self.RFunctionParammethod_comboBox.currentText())+'\''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['cor']+'<-cor(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('txt<-capture.output('+self.Rvariables['cor']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        newData = RvarClasses.RMatrix(data = self.Rvariables["cor"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.dictAttrs = self.data.dictAttrs.copy()  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("cor Output", newData)
