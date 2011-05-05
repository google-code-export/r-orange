"""
<name>Sequence</name>
<tags>Prototypes</tags>
"""
from OWRpy import * 
import redRGUI
import redRi18n
_ = redRi18n.get_(package = 'base')

# signals
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.signalClasses.RVector import RVector as redRRVector

# Qt widgets
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.comboBox import comboBox as redRcomboBox
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox

# code
class RedRseq(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        # R variables
        self.setRvariableNames(["seq"])


        # Output
        self.outputs.addOutput('id0', _('Sequence Output'), redRRVector)

        # GUI
        area = widgetBox(self.controlArea,orientation='vertical')
        methodBox = widgetBox(area)
        options = widgetBox(area)
        self.testOptions = widgetBox(options)
        
        self.methodButtons = redRcomboBox(methodBox,  label = "Select vector type",
        items = [('seq','Sequence'),
        ('rep','Repeat')],
        editable=False, callback = self.onTestChange)
        
        self.lineEditWidth = 100
        self.sequenceGroup = groupBox(self.testOptions,orientation='vertical', label='Sequence') 
        self.RFunctionParam_sfrom = lineEdit(self.sequenceGroup, label = "From", text = '', width=self.lineEditWidth)
        self.RFunctionParam_sto = lineEdit(self.sequenceGroup, label = "To", text = '', width=self.lineEditWidth)
        self.RFunctionParam_sby = lineEdit(self.sequenceGroup, label = "By", text = '', width=self.lineEditWidth)
        
        self.repeatGroup = groupBox(self.testOptions,orientation='vertical', label='Repeat') 
        self.RFunctionParam_robj = lineEdit(self.repeatGroup, label = "Object", text = '', width=self.lineEditWidth)
        self.RFunctionParam_rtimes = lineEdit(self.repeatGroup, label = "Times", text = '', width=self.lineEditWidth)
        self.repeatGroup.hide()
        
        self.commit = redRCommitButton(self.bottomAreaRight, _("Commit"), alignment=Qt.AlignLeft, 
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
            
        newData = redRRVector(self, data = self.Rvariables["seq"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
