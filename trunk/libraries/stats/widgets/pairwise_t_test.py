"""
<name>Pairwise T-Test</name>
<description>This widget performs pairwise t-tests on the supplied samples.  This is also effective at performing t-tests on two samples if supplied.  Data should be supplied in the form of a two columned table with one column representing values and the other the groupings.  Use of Melt DF and Column Selector may be helpful in transforming your data.</description>
<tags>Parametric</tags>
<icon>stats.png</icon>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:pairwise.t.test</RFunctions>
"""
from OWRpy import * 
import redRGUI, signals
import OWGUI 
class pairwise_t_test(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["pairwise.t.test"])
        self.RFunctionParam_x = ""
        self.RFunctionParam_pool_sd = "TRUE"
        self.RFunctionParam_g = ""
        self.RFunctionParam_p_adjust_method = "p.adjust.methods"
        self.indata = ''
        self.inputs.addInput('id0', 'R Data Frame', signals.base.RDataFrame, self.process)

        self.outputs.addOutput('id0', 'pairwise.t.test Output', signals.base.RVariable)

        
        box = redRGUI.base.widgetBox(self.controlArea)
        self.RFunctionParam_x = redRGUI.base.comboBox(box, label = "Values:")
        self.RFunctionParam_pool_sd = redRGUI.base.comboBox(box, label = "Pool Standard Deviation:", items = ['True', 'False'])
        self.RFunctionParam_g = redRGUI.base.comboBox(box, label = "Groups Column:")
        self.RFunctionParam_p_adjust_method = redRGUI.base.comboBox(box, label = "P-value Adjust Method:", items = ["holm", "hochberg", "hommel", "bonferroni", "BH", "BY", "fdr", "none"])
        self.alternative = redRGUI.base.comboBox(box, label = 'Alternative Hypothesis:', items = ['two.sided', 'greater', 'less'])
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.base.textEdit(box,label='R Output')
        #box.layout().addWidget(self.RoutputWindow)
    
    def process(self, data):
        if data:
            self.indata = data.getData()
            cols = self.R('colnames('+self.indata+')')
            self.RFunctionParam_x.update(cols)
            self.RFunctionParam_g.update(cols)
            self.commitFunction()
        else:
            self.indata = ''
            self.RFunctionParam_g.clear()
            self.RFunctionParam_x.clear()
            return
            
            
    
    def commitFunction(self):
        if self.indata == '': return
        if self.RFunctionParam_x.currentText() == self.RFunctionParam_g.currentText(): return
        #self.R('attach('+self.indata+')')
        self.R(self.Rvariables['pairwise.t.test']+'<-pairwise.t.test(x='+self.indata+'[,\''+unicode(self.RFunctionParam_x.currentText())+'\'],pool_sd='+unicode(self.RFunctionParam_pool_sd.currentText())+',g='+self.indata+'[,\''+unicode(self.RFunctionParam_g.currentText())+'\'],p.adjust.method=\''+unicode(self.RFunctionParam_p_adjust_method.currentText())+'\', alternative = \''+unicode(self.alternative.currentText())+'\')')
        # self.R('detach()')
        self.R('txt<-capture.output('+self.Rvariables['pairwise.t.test']+')', wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        #print tmp
        self.RoutputWindow.insertPlainText(tmp)
        out = signals.base.RVariable(self, data=self.Rvariables["pairwise.t.test"])
        self.rSend("id0", out)