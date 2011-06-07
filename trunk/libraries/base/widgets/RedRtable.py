"""
.. helpdoc::
<p><!-- [REQUIRED] A detailed description of the widget and what it does--></p>
"""

"""
<widgetXML>    
    <name>Convert To Table/Prop Table</name>
    <icon>default.png</icon>
    <tags> 
        <tag>Data Manipulation</tag> 
    </tags>
    <summary>Converts a data table of factors to counts of the unique combinations of levels.  For exampel if your data table consisted of rows representing observations of cars with columns indicating make, color, and year, this widget would return a list of counts for each make color year combination.</summary>
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
<name>Convert To Table/Prop Table</name>
<tags>Data Manipulation</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRi18n
_ = redRi18n.get_(package = 'base')
class RedRtable(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["table", "propTable"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.inputs.addInput("data", _("Data Table"), signals.base.RDataFrame, self.processdata)
        self.outputs.addOutput("table Output",_("Table Output"), signals.base.RDataFrame)
        self.outputs.addOutput("propTable", _("Prob Table Output"), signals.base.RDataFrame)
        
        self.cols = redRGUI.base.listBox(self.controlArea, label = _('Use Columns:'), selectionMode = QAbstractItemView.MultiSelection)
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,processOnInput=True)
        
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = _("R Output Window"))
    def processdata(self, data):
        if data:
            self.RFunctionParam_data=data.getData()
            self.cols.update(self.R('colnames('+self.RFunctionParam_data+')', wantType = 'list'))
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_data=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_data) == '': return
        if len(self.cols.selectedItems()) > 0:
            self.R(self.Rvariables['table']+'<-table(data='+unicode(self.RFunctionParam_data)+')', wantType = 'NoConversion')
        else:
            self.R(self.Rvariables['table']+'<-table('+self.RFunctionParam_data+'$'+unicode(', '+self.RFunctionParam_data+'$').join([unicode(a.text()) for a in self.cols.selectedItems()])+')', wantType = 'NoConversion')
        self.R('txt<-capture.output('+self.Rvariables['table']+')', wantType = 'NoConversion')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.R(self.Rvariables['propTable']+'<-prop.table('+self.Rvariables['table']+')', wantType = 'NoConversion')
        self.R('txt<-capture.output('+self.Rvariables['propTable']+')', wantType = 'NoConversion')
        tmp2 = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertPlainText(tmp+'\n\n'+tmp2)
        newData = signals.base.RDataFrame(self, data = 'as.data.frame('+self.Rvariables["table"]+')', parent = 'as.data.frame('+self.Rvariables["table"]+')') # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("table Output", newData)
        newDataProp = signals.base.RDataFrame(self, data = 'as.data.frame('+self.Rvariables['propTable']+')', parent = 'as.data.frame('+self.Rvariables['propTable']+')')
        self.rSend('propTable', newDataProp)