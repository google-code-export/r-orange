"""
<name>Sequence</name>
<tags>Prototypes</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI
import redRi18n
_ = redRi18n.get_(package = 'base')

# signals

# Qt widgets

# code
class RedRseq(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        # R variables
        self.setRvariableNames(["seq"])


        # Output
        self.outputs.addOutput('id0', _('Sequence Output'), signals.base.RVector)

        # GUI
        area = redRGUI.base.widgetBox(self.controlArea,orientation='vertical')
        methodBox = redRGUI.base.widgetBox(area)
        options = redRGUI.base.widgetBox(area)
        self.testOptions = redRGUI.base.widgetBox(options)
        
        self.methodButtons = redRGUI.base.comboBox(methodBox,  label = "Select vector type",
        items = [('seq','Sequence'),
        ('rep','Repeat')],
        editable=False, callback = self.onTestChange)
        
        self.lineEditWidth = 100
        self.sequenceGroup = redRGUI.base.groupBox(self.testOptions,orientation='vertical', label='Sequence') 
        self.RFunctionParam_sfrom = redRGUI.base.lineEdit(self.sequenceGroup, label = "From", text = '', width=self.lineEditWidth)
        self.RFunctionParam_sto = redRGUI.base.lineEdit(self.sequenceGroup, label = "To", text = '', width=self.lineEditWidth)
        self.RFunctionParam_sby = redRGUI.base.lineEdit(self.sequenceGroup, label = "By", text = '', width=self.lineEditWidth)
        
        self.repeatGroup = redRGUI.base.groupBox(self.testOptions,orientation='vertical', label='Repeat') 
        self.RFunctionParam_robj = redRGUI.base.lineEdit(self.repeatGroup, label = "Object", text = '', width=self.lineEditWidth)
        self.RFunctionParam_rtimes = redRGUI.base.lineEdit(self.repeatGroup, label = "Times", text = '', width=self.lineEditWidth)
        self.repeatGroup.hide()
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), alignment=Qt.AlignLeft, 
        callback = self.commitFunction, processOnInput=True)

    def onTestChange(self):
        for i in self.testOptions.findChildren(groupBox):
            i.setHidden(True)
        if self.methodButtons.currentId() == 'seq':
            self.sequenceGroup.show()
        elif self.methodButtons.currentId() == 'rep':
            self.repeatGroup.show()
        
    def commitFunction(self):
        injection = []
        test = unicode(self.methodButtons.currentId())
        if test == 'seq':
            if unicode(self.RFunctionParam_sfrom.text()) != '':
                string = 'from='+unicode(self.RFunctionParam_sfrom.text())+''
                injection.append(string)
            if unicode(self.RFunctionParam_sto.text()) != '':
                string = 'to='+unicode(self.RFunctionParam_sto.text())+''
                injection.append(string)
            if unicode(self.RFunctionParam_sby.text()) != '':
                string = 'by='+unicode(self.RFunctionParam_sby.text())+''
                injection.append(string)
            inj = ','.join(injection)
            self.R(self.Rvariables['seq']+'<-seq('+inj+')', wantType = 'NoConversion')
            
        elif test == 'rep':
            if unicode(self.RFunctionParam_robj.text()) != '':
                string = 'x='+unicode(self.RFunctionParam_robj.text())+''
                injection.append(string)
            if unicode(self.RFunctionParam_rtimes.text()) != '':
                string = 'times='+unicode(self.RFunctionParam_rtimes.text())+''
                injection.append(string)
            inj = ','.join(injection)
            self.R(self.Rvariables['seq']+'<-rep('+inj+')', wantType = 'NoConversion')
            
        newData = signals.base.RVector(self, data = self.Rvariables["seq"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
