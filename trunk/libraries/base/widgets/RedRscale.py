"""
<name>scale</name>
<tags>Prototypes</tags>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRDataFrame
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.widgetLabel import widgetLabel
import redRi18n
_ = redRi18n.get_(package = 'base')
class RedRscale(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["scale"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.dataType = 1
        self.inputs.addInput('id0', _('Input Data'), [redRDataFrame, redRRMatrix], self.processx)

        self.outputs.addOutput('id0', _('scale Output'), redRDataFrame)
        self.outputs.addOutput('id1', _('scale Output (Matrix)'), redRRMatrix)

        
        self.roworcol = radioButtons(self.controlArea, label = _('Apply Scaling To:'), buttons = [_('Rows'), _('Columns')], setChecked = _('Columns'), orientation = 'horizontal')
        self.RFunctionParamscale_radioButtons =  radioButtons(self.controlArea,  label = _("Scale:"), buttons = [_('Yes'), _('No')], setChecked = _('No'), orientation = 'horizontal')
        self.RFunctionParamcenter_radioButtons =  radioButtons(self.controlArea,  label = _("Center:"), buttons = [_('Yes'), _('No')], setChecked = _('No'), orientation = 'horizontal')
        self.label = widgetLabel(self.controlArea)
        redRCommitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction)
    def processx(self, data):
        if not self.require_librarys(["base"]):
            self.status.setText(_('R Libraries Not Loaded.'))
            return
        if data:
            self.RFunctionParam_x=data.getData()
            if self.R('is.data.frame(%s)' % self.RFunctionParam_x):
                self.dataType = 1
            else:
                self.dataType = 2
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': return
        injection = []
        if unicode(self.RFunctionParamscale_radioButtons.getChecked()) == _('Yes'):
            string = 'scale = TRUE'
            injection.append(string)
        else:
            string = 'scale = FALSE'
            injection.append(string)
        if unicode(self.RFunctionParamcenter_radioButtons.getChecked()) != _('Yes'):
            string = 'center = TRUE'
            injection.append(string)
        else:
            string = 'center = FALSE'
            injection.append(string)
        inj = ','.join(injection)
        if self.dataType == 1:
            self.label.setText('Sending data frame')
        
            if unicode(self.roworcol.getChecked()) == _('Columns'):
                self.R(self.Rvariables['scale']+'<-as.data.frame(scale(x=data.matrix('+str(self.RFunctionParam_x)+'),'+inj+'))', wantType = 'NoConversion')
            else:
                self.R(self.Rvariables['scale']+'<-t(as.data.frame(scale(x=t(data.matrix('+str(self.RFunctionParam_x)+')),'+inj+')))', wantType = 'NoConversion')
            self.R('rownames('+self.Rvariables['scale']+')<-rownames('+self.RFunctionParam_x+')', wantType = 'NoConversion')
            self.R('colnames('+self.Rvariables['scale']+')<-colnames('+self.RFunctionParam_x+')', wantType = 'NoConversion')
            newData = redRDataFrame(self, data = self.Rvariables["scale"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
            #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
            self.rSend("id0", newData)
        else:
            self.label.setText('Sending matrix')
            if unicode(self.roworcol.getChecked()) == _('Columns'):
                self.R(self.Rvariables['scale']+'<-scale(x=data.matrix('+str(self.RFunctionParam_x)+'),'+inj+')', wantType = 'NoConversion')
            else:
                self.R(self.Rvariables['scale']+'<-t(scale(x=t(data.matrix('+str(self.RFunctionParam_x)+')),'+inj+'))', wantType = 'NoConversion')
            self.R('rownames('+self.Rvariables['scale']+')<-rownames('+self.RFunctionParam_x+')', wantType = 'NoConversion')
            self.R('colnames('+self.Rvariables['scale']+')<-colnames('+self.RFunctionParam_x+')', wantType = 'NoConversion')
            newData = redRRMatrix(self, data = self.Rvariables["scale"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
            #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
            self.rSend("id1", newData)
        

