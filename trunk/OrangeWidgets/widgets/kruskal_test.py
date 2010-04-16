"""
<name>Kruskal</name>
<description>Performs the Kruskal Walis test on data.</description>
<author>Generated using Widget Maker written by Kyle R. Covington</author>

<icon>icons/stats.png</icon>
<tags>Non Parametric</tags>
<RFunctions>stats:kruskal.test</RFunctions>
"""
from OWRpy import * 
import redRGUI 
class kruskal_test(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.require_librarys(["stats"]) 
        self.loadSettings() 
        self.RFunctionParam_data = ''
        self.inputs = [("data", RvarClasses.RVariable, self.processdata)]
        
        self.help.setHtml('<small>Performs the Kruskal Walis test on a set of data.  This should be a data.frame or data tabel with one column representing the outcome and another representing a group or grouping variable.  The Formula section should be entered in the form of outcom variable ~ grouping variable.  If multiple groups are used you may use the * key to separate them.  Example: height ~ foodQuality * genes.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        #box = redRGUI.tabWidget(self.controlArea)
        #self.standardTab = box.createTabPage(name = "Standard")
        #self.advancedTab = box.createTabPage(name = "Advanced")
        #self.RFunctionParamsubset_lineEdit =  redRGUI.lineEdit(self.controlArea, label = "Subset:")
        #self.RFunctionParamx_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "x:")
        #self.RFunctionParamg_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "g:")
        self.RFunctionParamformula =  redRGUI.RFormulaEntry(self.controlArea)
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        redRGUI.button(self.controlArea, "Report", callback = self.sendReport)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processdata(self, data):
        self.RoutputWindow.clear()
        self.status.setText('New data recieved')
        if data:
            self.RFunctionParam_data=data["data"]
            self.data = data.copy()
            self.RFunctionParamformula.update(self.R('colnames('+self.RFunctionParam_data+')'))
            self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.RFunctionParamformula.clear()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': return
        formulaOutput = self.RFunctionParamformula.Formula()
        if formulaOutput == None or formulaOutput[0] == '' or formulaOutput[1] == '': return
        injection = []
        string = formulaOutput[0]+ ' ~ ' + formulaOutput[1]
        injection.append(string)
        # if str(self.RFunctionParamsubset_lineEdit.text()) != '':  # We nolonger support subsets, you may subset using an upstream widget
            # string = 'subset='+str(self.RFunctionParamsubset_lineEdit.text())
            # injection.append(string)

        inj = ','.join(injection)
        self.R('txt<-capture.output(kruskal.test('+inj+', data='+str(self.RFunctionParam_data)+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<pre>'+tmp+'</pre>')
        self.status.setText('Data sent')
    def compileReport(self):
        self.reportSettings("Input Settings",[("data", self.RFunctionParam_data)])
        self.reportSettings('Function Settings', [('subset',str(self.RFunctionParamsubset_lineEdit))])
        #self.reportSettings('Function Settings', [('x',str(self.RFunctionParam_x))])
        #self.reportSettings('Function Settings', [('g',str(self.RFunctionParam_g))])
        self.reportSettings('Function Settings', [('formula',str(self.RFunctionParamformula_lineEdit))])
    def sendReport(self):
        self.compileReport()
        self.showReport()
