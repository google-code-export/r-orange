"""
<name>Subset Summary</name>
<description>Very similar to summary except that this function first splits a data table into multiple tables based on the levels of a factor(s) and then performs the summary function on each resulting data table.</description>
<tags>R</tags>
<icon>Subset.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.textEdit import textEdit
import redRi18n
_ = redRi18n.get_(package = 'base')
class subsetSummary(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', _('R Variable Object'), redRRDataFrame, self.processobject)
        self.namesList = redRListBox(self.controlArea, label = _('Splitting Element:'))
        self.namesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.commit = redRCommitButton(self.bottomAreaRight, _("Commit"), alignment=Qt.AlignLeft, 
        callback = self.commitFunction, processOnInput=True)
        self.RoutputWindow = textEdit(self.controlArea, label = _("RoutputWindow"))
    def processobject(self, data):
        if data:
            self.RFunctionParam_object=data.getData()
            self.data = data
            self.namesList.update(self.R('names('+self.RFunctionParam_object+')', wantType = 'list'))
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_object) == '': return
        if len(self.namesList.selectedItems()) == 0: return # must select something to split on.
        listappend = ','.join([self.RFunctionParam_object+'$'+unicode(i) for i in self.namesList.selectedItems()])
        self.R('txt<-capture.output(lapply(split(%s, list(%s), drop=F), summary))' % (self.RFunctionParam_object, listappend))
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
