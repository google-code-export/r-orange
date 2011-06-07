"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>String Split</name>
    <icon>default.png</icon>
    <tags> 
        <tag>Data Manipulation</tag> 
    </tags>
    <summary>Split strings by some function or string from a vector or list selection (works on data tables too).</summary>
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
<name>String Split</name>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class RedRstrsplit(OWRpy): 
    settingsList = []
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["strsplit", "dataframe"])
        self.data = {}
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', _('Input Data'), [signals.base.RVector, signals.base.RList], self.processx)

        self.outputs.addOutput('id0', _('strsplit Output'), signals.base.RList)
        self.outputs.addOutput('id1', _('strsplit Vector'), signals.base.RVector)
        self.outputs.addOutput('dataframe', _('Data Table'), signals.base.RDataFrame)

        
        self.RFunctionParamsplit_lineEdit =  redRGUI.base.lineEdit(self.controlArea,  label = _("Split Text Using:"), text = '')
        self.RFunctionParamfixed_radioButtons =  redRGUI.base.radioButtons(self.controlArea,  label = _("fixed:"), buttons = [_('Use text exactly'), _('Use text as expression (Advanced)')], setChecked = _('Use text exactly'), orientation = 'horizontal')
        self.RFunctionParamextended_radiButtons =  redRGUI.base.radioButtons(self.controlArea,  label = _("Extend Expressions:"), buttons = [_('Yes'), _('No')], setChecked = _('No'), orientation = 'horizontal')
        self.RFunctionParamperl_radioButtons =  redRGUI.base.radioButtons(self.controlArea,  label = _("Use Perl Expressions:"), buttons = [_('Yes'), _('No')], setChecked = _('No'), orientation = 'horizontal')
        self.RFunctionParamunlist_radioButtons = redRGUI.base.radioButtons(self.controlArea, label = _('Convert to RVector'), buttons = [_('Send only the list'), _('Send list and vector')], setChecked = _('Send list and vector'), orientation = 'horizontal')
        redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction)
    def processx(self, data):
        
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            if type(data) == signals.base.RVector:
                self.dataType = 1
                self.dataSelector.clear()
                self.dataSelector.setEnabled(False)
            elif type(data) == signals.base.RDataFrame:
                self.dataType = 2
                if self.R('names(%s)' % self.RFunctionParam_x, wantType = 'convert') == None:
                    self.R('names(%s)<-c(%s)' % (self.RFunctionParam_x, ','.join(['\'Item_%s\'' % str(i) for i in range(self.R('length(%s)' % self.RFunctionParam_x, wantType = 'convert'))])), wantType = 'NoConversion')
                self.dataSelector.update(self.R('names(%s)' % self.RFunctionParam_x, wantType = 'list'))
                self.dataSelector.setEnabled(True)
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_x) == '': 
            self.status.setText(_('No Data to Split'))
            return
        if unicode(self.RFunctionParamsplit_lineEdit.text()) == '':
            self.status.setText(_('No string to split on'))
            return
        injection = []
        if unicode(self.RFunctionParamfixed_radioButtons.getChecked()) == _('Yes'):
            string = 'fixed=TRUE'
            injection.append(string)
        else:
            string = 'fixed=FALSE'
            injection.append(string)
        if unicode(self.RFunctionParamextended_radiButtons.getChecked()) == _('Yes'):
            string = 'extended=TRUE'
            injection.append(string)
        else:
            string = 'extended=FALSE'
            injection.append(string)
        if unicode(self.RFunctionParamsplit_lineEdit.text()) != '':
            string = 'split='+unicode(self.RFunctionParamsplit_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamperl_radioButtons.getChecked()) == _('Yes'):
            string = 'perl=TRUE'
            injection.append(string)
        else:
            string = 'perl=FALSE'
            injection.append(string)
        inj = ','.join(injection)
        if self.dataType == 1:
            thisData = self.RFunctionParam_x
        elif self.dataType == 2:
            thisData = '%s$%s' % (self.RFunctionParam_x, self.dataSelector.currentText())
        self.R(self.Rvariables['strsplit']+'<-strsplit(x= as.character('+unicode(thisData)+') ,'+inj+')', wantType = 'NoConversion')
        newData = signals.base.RList(self, data = self.Rvariables["strsplit"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
        
        if unicode(self.RFunctionParamunlist_radioButtons.getChecked()) == _('Send list and vector'):
            newData = signals.base.RVector(self, data = 'unlist('+self.Rvariables['strsplit']+')')
            self.rSend("id1", newData)
            
        ## convert to a data frame
        self.R(
        """
        for(i in 1:length(%s)){
            if(length(%s[[i]]) == 0){
                %s[[i]] = c('','')
            }
        }
        """ % (self.Rvariables['strsplit'], self.Rvariables['strsplit'], self.Rvariables['strsplit']),
        wantType = 'NoConversion',
        silent = True)
        self.R(self.Rvariables['dataframe']+'<-t(data.frame('+self.Rvariables['strsplit']+'))', wantType = 'NoConversion')
        newDataFrame = signals.base.RDataFrame(self, data = self.Rvariables['dataframe'], parent = self.Rvariables['dataframe'], checkVal = False)
        self.rSend('dataframe', newDataFrame)
        
