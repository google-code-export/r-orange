"""Row or Column Names
.. helpdoc::
"""

"""
<widgetXML>    
    <name>Row or Column Names</name>
    <icon>readfile.png</icon>
    <tags> 
        <tag>Subsetting</tag> 
    </tags>
    <summary>Return Rownames</summary>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
</widgetXML>
"""

"""
<name>Row or Column Names</name>
<tags>Subsetting</tags>
<icon>readfile.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class rownames(OWRpy): 
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["rownames", "renamedRowColData"])
        self.data = {}
         
        self.RFunctionParam_x = ''
        
        """.. rrsignals::"""
        self.inputs.addInput('id0', _('Input Data'), signals.base.RDataFrame, self.processx)

        """.. rrsignals::"""
        self.outputs.addOutput('id0', _('Row or Column Names'), signals.base.RVector)
        
        """.. rrsignals::"""
        self.outputs.addOutput('renamedDF', _("Renamed Data Table"), signals.base.RDataFrame)

        
        box = redRGUI.base.groupBox(self.controlArea, label = _("Get Row or Column Names"))
        self.controlArea.layout().setAlignment(box,Qt.AlignTop | Qt.AlignLeft)
        redRGUI.base.widgetLabel(box,_('Get row or column names from input object.'))
        redRGUI.base.separator(box,height=10)
        self.function =  redRGUI.base.radioButtons(box, label=_('Row or Column'),displayLabel=False,
        buttons=[_('Row Names'),_('Column Names')],setChecked=_('Row Names'), orientation='horizontal')
        redRGUI.base.separator(box,height=10)

        self.RFunctionParamprefix_lineEdit =  redRGUI.base.lineEdit(box,  label = _("prefix:"), 
        toolTip=_('Prepend prefix to simple numbers when creating names.'))
        redRGUI.base.separator(box,height=10)
        
        self.doNullButton =  redRGUI.base.radioButtons(box,  label = _("do.NULL:"),
        toolTips=[_('logical. Should this create names if they are NULL?')]*2,
        buttons=[_('TRUE'),_('FALSE')],setChecked=_('TRUE'), orientation='horizontal')
        buttonBox = redRGUI.base.widgetBox(box,orientation='horizontal')
        
        redRGUI.base.commitButton(buttonBox, _("Commit"), callback = self.commitFunction)
        
        self.autoCommit = redRGUI.base.checkBox(buttonBox,label=_('commit'), displayLabel=False,
        buttons=[_('Commit on Input')],setChecked=[_('Commit on Input')])
        
        box2 = redRGUI.base.groupBox(self.controlArea, label = _("Set Row or Column Names"))
        self.rcrename =  redRGUI.base.radioButtons(box2, label=_('Row or Column'),displayLabel=False,
        buttons=[('row', _('Row Names')),('col', _('Column Names'))],setChecked=_('row'), orientation='horizontal', callback = self.resetrcrename)
        self.attsList = redRGUI.base.listBox(box2, label = _("Row or Column Choices"), toolTip = _("Select the Row or Column to use for the new Column or Row names, you choose a Row name to set column names and vice versa."))
        
        redRGUI.base.commitButton(box2, _("Commit"), callback = self.setNames)
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            self.data = data
            self.commitFunction(userClick=False)
            self.resetrcrename()
        else:
            self.RFunctionParam_x = ''
    def resetrcrename(self):
        if self.rcrename.getCheckedId() == 'row':
            self.attsList.update(self.R('colnames(%s)' % self.RFunctionParam_x, wantType = 'list'))
        else:
            self.attsList.update(self.R('rownames(%s)' % self.RFunctionParam_x, wantType = 'list'))
    def commitFunction(self,userClick=True):
        if not userClick and _('Commit on Input') not in self.autoCommit.getChecked():
            return
        if unicode(self.RFunctionParam_x) == '': 
            self.status.setText(_('No data'))
            return
            
        injection = []
        if self.function.getChecked() == _('Row Names'):
            function = 'rownames'
        else:
            function = 'colnames'

        if unicode(self.RFunctionParamprefix_lineEdit.text()) != '':
            string = 'prefix="'+unicode(self.RFunctionParamprefix_lineEdit.text())+'"'
            injection.append(string)
        if unicode(self.doNullButton.getChecked()):
            string = 'do.NULL='+unicode(self.doNullButton.getChecked())
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['rownames']+'<-'+function+'(x='+unicode(self.RFunctionParam_x)+','+inj+')', wantType = 'NoConversion')
        
        newData = signals.base.RVector(self, data = self.Rvariables["rownames"])

        self.rSend("id0", newData)
    def setNames(self):
        # want to use the selected row or column as the column or row names
        if self.rcrename.getCheckedId() == 'row':
            self.R("%(renamedRowColData)s<-%(RFunctionParam_x)s; rownames(%(renamedRowColData)s)<-make.names(%(RFunctionParam_x)s$%(selectedColumn)s, unique = TRUE)" % 
            {'renamedRowColData':self.Rvariables['renamedRowColData'],
            'RFunctionParam_x':self.RFunctionParam_x,
            'selectedColumn':self.attsList.currentSelection()[0]}
            , wantType = 'NoConversion')
        else:
            self.R("%(renamedRowColData)s<-%(RFunctionParam_x)s; colnames(%(renamedRowColData)s)<-make.names(%(RFunctionParam_x)s[,\"%(selectedColumn)s\"], unique = TRUE)" % 
            {'renamedRowColData':self.Rvariables['renamedRowColData'],
            'RFunctionParam_x':self.RFunctionParam_x,
            'selectedColumn':self.attsList.currentSelection()[0]}
            , wantType = 'NoConversion')
        newData = signals.base.RDataFrame(self, data = self.Rvariables['renamedRowColData'])
        self.rSend('renamedDF', newData)
    def getReportText(self, fileDir):
        text = _('%s were sent from this widget.\n\n') % unicode(self.function.getChecked())
        return text
