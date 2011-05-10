"""
<name>Subset Summary</name>
<description>Very similar to summary except that this function first splits a data table into multiple tables based on the levels of a factor(s) and then performs the summary function on each resulting data table.</description>
<tags>R</tags>
<icon>Subset.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import redRi18n
_ = redRi18n.get_(package = 'base')
class subsetSummary(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["summary"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', _('R Variable Object'), signals.base.RDataFrame, self.processobject)
        self.namesList = redRGUI.base.listBox(self.controlArea, label = _('Splitting Element:'))
        self.namesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), alignment=Qt.AlignLeft, 
        callback = self.commitFunction, processOnInput=True)
        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea, label = _("RoutputWindow"))
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
