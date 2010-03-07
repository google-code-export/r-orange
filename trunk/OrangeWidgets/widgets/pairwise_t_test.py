"""
<name>Pairwise T-Test</name>
<description>This widget performs pairwise t-tests on the supplied samples.  This is also effective at performing t-tests on two samples if supplied.  Data should be supplied in the form of a two columned table with one column representing values and the other the groupings.  Use of Melt DF and Column Selector may be helpful in transforming your data.</description>
<tags>Parametric, Stats</tags>
<icon>icons/stats.png</icon>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:pairwise.t.test</RFunctions>
"""
from OWRpy import * 
import OWGUI 
class pairwise_t_test(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["pairwise.t.test"])
        self.RFunctionParam_x = ""
        self.RFunctionParam_pool_sd = "TRUE"
        self.RFunctionParam_g = ""
        self.RFunctionParam_p_adjust_method = "p.adjust.methods"
        self.indata = None
        self.inputs = [('R Data Frame', RvarClasses.RDataFrame, self.process)]
        self.outputs = [("pairwise.t.test Output", RvarClasses.RVariable)]
        
        box = OWGUI.widgetBox(self.controlArea, "Widget Box")
        self.values = OWGUI.comboBox(box, self, "RFunctionParam_x", label = "Values:")
        OWGUI.lineEdit(box, self, "RFunctionParam_pool_sd", label = "pool_sd:")
        self.groups = OWGUI.comboBox(box, self, "RFunctionParam_g", label = "Groups:")
        OWGUI.lineEdit(box, self, "RFunctionParam_p_adjust_method", label = "p_adjust_method:")
        OWGUI.button(box, self, "Commit", callback = self.commitFunction, width = 500)
        self.RoutputWindow = QTextEdit()
        box.layout().addWidget(self.RoutputWindow)
    
    def process(self, data):
        if data:
            self.indata = data['data']
            self.values.clear()
            self.groups.clear()
            cols = self.R('colnames('+self.indata+')')
            self.values.addItems(cols)
            self.groups.addItems(cols)
            self.commitFunction()
        else:
            return
            
            
    
    def commitFunction(self):
        if self.indata == None: return
        if self.values.currentText() == self.groups.currentText(): return
        self.R('attach('+self.indata+')')
        self.R(self.Rvariables['pairwise.t.test']+'<-pairwise.t.test(x='+str(self.values.currentText())+',pool_sd='+str(self.RFunctionParam_pool_sd)+',g='+str(self.groups.currentText())+',p.adjust.method='+str(self.RFunctionParam_p_adjust_method)+')')
        self.R('detach()')
        self.R('txt<-capture.output('+self.Rvariables['pairwise.t.test']+')')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<pre>'+tmp+'</pre>')
        self.rSend("pairwise.t.test Output", {"data":self.Rvariables["pairwise.t.test"]})
