"""
<name>Attributes</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:attributes</RFunctions>
<tags>Stats</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 


class RedRattributes(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["attributes"])
        self.data = {}
        self.RFunctionParam_obj = ''
        
        """.. rrsignals::
            :description: `Model object`"""
        self.inputs.addInput('id0', 'Objectd', signals.base.RVariable, self.processobj)

        
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = "R Output Window")
    def processobj(self, data):
            if data:
                    self.RFunctionParam_obj=data.getData()
                    #self.data = data
                    self.commitFunction()
            else:
                    self.RFunctionParam_obj=''
    def commitFunction(self):
            if unicode(self.RFunctionParam_obj) == '': 
                self.status.setText('No data')
                return
            injection = []
            inj = ','.join(injection)
            self.R(self.Rvariables['attributes']+'<-attributes(obj='+unicode(self.RFunctionParam_obj)+','+inj+')')
            self.R('txt<-capture.output('+self.Rvariables['attributes']+')')
            self.RoutputWindow.clear()
            tmp = self.R('paste(txt, collapse ="\n")')
            self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
