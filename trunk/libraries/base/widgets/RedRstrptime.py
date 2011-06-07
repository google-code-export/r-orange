"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>strptime</name>
    <icon>default.png</icon>
    <tags> 
        <tag>Prototypes</tag> 
    </tags>
    <summary></summary>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</widgetXML>
"""

"""
<name>strptime</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description></description>
<RFunctions>base:strptime</RFunctions>
<tags>Prototypes</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRi18n
_ = redRi18n.get_(package = 'base')
class RedRstrptime(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["strptime"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs.addInput("x", _("Input Data"), signals.base.RDataFrame, self.processx)
        self.outputs.addOutput("strptime Output",_("strptime Output"), signals.base.RDataFrame)
        
        self.columnSelection = redRGUI.base.comboBox(self.controlArea, label = _("Data Column:"))
        self.RFunctionParamformat_comboBox = redRGUI.base.comboBox(self.controlArea, label = "format:", items = [_("yyyymmdd"), _("yymmdd"), _("ddmmyyyy"), _("ddmmyy"), _("mmddyyyy"), _("mmddyy")], toolTip = _("Select the format of the date time.  y is year m is month and d is day."))
        redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.columnSelection.update(self.R('names('+self.RFunctionParam_x+')', wantType = 'list'))
            self.R(self.Rvariables['strptime']+'<-'+self.RFunctionParam_x)
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        if unicode(self.RFunctionParamformat_comboBox.currentText()) == _('yyyymmdd'):
            
            string = ',format="%Y/%m/%d"'
            injection.append(string)
        elif unicode(self.RFunctionParamformat_comboBox.currentText()) == _('yymmdd'):
            
            string = ',format="%y/%m/%d"'
            injection.append(string)
        elif unicode(self.RFunctionParamformat_comboBox.currentText()) == _('ddmmyy'):
            
            string = ',format="%d/%m/%y"'
            injection.append(string)
        elif unicode(self.RFunctionParamformat_comboBox.currentText()) == _('ddmmyyyy'):
            
            string = ',format="%d/%m/%Y"'
            injection.append(string)
        elif unicode(self.RFunctionParamformat_comboBox.currentText()) == _('mmddyy'):
            
            string = ',format="%m/%d/%y"'
            injection.append(string)
        elif unicode(self.RFunctionParamformat_comboBox.currentText()) == _('mmddyyyy'):
            
            string = ',format="%m/%d/%Y"'
            injection.append(string)
        inj = ''.join(injection)
        self.R(self.Rvariables['strptime']+'$'+self.Rvariables['strptime']+'<-as.numeric(strptime(x='+unicode(self.RFunctionParam_x)+'$'+unicode(self.columnSelection.currentText())+inj+'))')
        newData = signals.base.RDataFrame(self, data = self.Rvariables["strptime"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("strptime Output", newData)