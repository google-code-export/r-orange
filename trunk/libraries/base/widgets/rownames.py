"""
<name>Row or Column Names</name>
<tags>Subsetting</tags>
<icon>readfile.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.listBox import listBox
import redRi18n
_ = redRi18n.get_(package = 'base')
class rownames(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["rownames", "renamedRowColData"])
        self.data = {}
         
        self.RFunctionParam_x = ''
        self.inputs.addInput('id0', _('Input Data'), redRRDataFrame, self.processx)

        self.outputs.addOutput('id0', _('Row or Column Names'), redRRVector)
        self.outputs.addOutput('renamedDF', _("Renamed Data Table"), redRRDataFrame)

        
        box = groupBox(self.controlArea, label = _("Get Row or Column Names"))
        self.controlArea.layout().setAlignment(box,Qt.AlignTop | Qt.AlignLeft)
        widgetLabel(box,_('Get row or column names from input object.'))
        separator(box,height=10)
        self.function =  radioButtons(box, label=_('Row or Column'),displayLabel=False,
        buttons=[_('Row Names'),_('Column Names')],setChecked=_('Row Names'), orientation='horizontal')
        separator(box,height=10)

        self.RFunctionParamprefix_lineEdit =  lineEdit(box,  label = _("prefix:"), 
        toolTip=_('Prepend prefix to simple numbers when creating names.'))
        separator(box,height=10)
        
        self.doNullButton =  radioButtons(box,  label = _("do.NULL:"),
        toolTips=[_('logical. Should this create names if they are NULL?')]*2,
        buttons=[_('TRUE'),_('FALSE')],setChecked=_('TRUE'), orientation='horizontal')
        buttonBox = widgetBox(box,orientation='horizontal')
        redRCommitButton(buttonBox, _("Commit"), callback = self.commitFunction)
        self.autoCommit = checkBox(buttonBox,label=_('commit'), displayLabel=False,
        buttons=[_('Commit on Input')],setChecked=[_('Commit on Input')])
        
        box2 = groupBox(self.controlArea, label = _("Set Row or Column Names"))
        self.rcrename =  radioButtons(box2, label=_('Row or Column'),displayLabel=False,
        buttons=[('row', _('Row Names')),('col', _('Column Names'))],setChecked=_('row'), orientation='horizontal', callback = self.resetrcrename)
        self.attsList = listBox(box2, label = _("Row or Column Choices"), toolTip = _("Select the Row or Column to use for the new Column or Row names, you choose a Row name to set column names and vice versa."))
        redRCommitButton(box2, _("Commit"), callback = self.setNames)
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
        
        newData = redRRVector(data = self.Rvariables["rownames"])

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
        newData = redRRDataFrame(data = self.Rvariables['renamedRowColData'])
        self.rSend('renamedDF', newData)
    def getReportText(self, fileDir):
        text = _('%s were sent from this widget.\n\n') % unicode(self.function.getChecked())
        return text
