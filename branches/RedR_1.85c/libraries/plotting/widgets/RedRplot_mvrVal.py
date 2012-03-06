"""
<name>plot.mvrVal</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>pls:plot.mvrVal</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 

class RedRplot_mvrVal(OWRpy): 
        settingsList = []
        def __init__(self, **kwargs):
                OWRpy.__init__(self, **kwargs)
                self.RFunctionParam_x = ''
                self.inputs.addInput('id0', 'x', redRRModelFit, self.processx)

                
                self.RFunctionParamtype_comboBox = redRGUI.base.comboBox(self.controlArea, label = "type:", items = ["'b',both","'l','lines'","'p',points"])
                self.RFunctionParamlegendpos_comboBox = redRGUI.base.comboBox(self.controlArea, label = "legendpos:", items = ["'topright'","'topleft'","'bottomright'","'bottomleft'"])
                redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        def processx(self, data):
                if not self.require_librarys(["pls"]):
                        self.status.setText('R Libraries Not Loaded.')
                        return
                if data:
                        self.RFunctionParam_x=data.getData()
                        #self.data = data
                        self.commitFunction()
                else:
                        self.RFunctionParam_x=''
        def commitFunction(self):
                if unicode(self.RFunctionParam_x) == '': return
                injection = []
                string = 'type='+unicode(self.RFunctionParamtype_comboBox.currentText()).split(',')[0]+''
                injection.append(string)
                string = 'legendpos='+unicode(self.RFunctionParamlegendpos_comboBox.currentText())+''
                injection.append(string)
                inj = ','.join(injection)
                self.Rplot('plot.mvrVal(x='+unicode(self.RFunctionParam_x)+','+inj+')')
