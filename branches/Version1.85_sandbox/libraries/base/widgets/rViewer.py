"""
<name>View R Output</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI
import redRi18n
_ = redRi18n.get_(package = 'base')
class rViewer(OWRpy): 
    globalSettingsList = ['commit','showAll']

    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.RFunctionParam_data = None
        self.data = None
        
        self.inputs.addInput('id0', _('R Variable Data'), signals.base.RVariable, self.processdata)

        self.RoutputWindow = redRGUI.base.textEdit(self.controlArea,label=_('Output'), editable=False)
        
        self.showAll = redRGUI.base.checkBox(self.bottomAreaLeft, label=_('showall'), displayLabel=False,
        buttons = [_('String Representation'), _('Show All')],orientation="horizontal", 
        setChecked = _('String Representation'))

        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, label=_("Commit"), callback = self.commitFunction, 
        processOnInput=True)
        
        #redRGUI.base.button(self.bottomAreaLeft, label=_("Print"), callback = self.printViewer)
        
    
    # def printViewer(self):
        # thisPrinter = QPrinter()
        # printer = QPrintDialog(thisPrinter)
        # if printer.exec_() == QDialog.Rejected:
            # print 'Printing Rejected'
            # return
        # self.RoutputWindow.print_(thisPrinter)
    def processdata(self, data):
        #print '######################in processdata', data
        if data:
            self.RFunctionParam_data=data.getData()
            self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_data = ''
            self.data = None
            self.commitFunction()

    
    def commitFunction(self):
        if not self.data: return
        self.RoutputWindow.clear()
        text = ''
        if _('String Representation') in self.showAll.getChecked():
            text += self.R('paste(capture.output(str('+unicode(self.data.getData())+')), collapse = \'\\n\')')
            text += '\n'
        text += '\n'
        if _('Show All') in self.showAll.getChecked():
            text += self.R('paste(capture.output('+unicode(self.data.getData())+'), collapse = \'\\n\')')
        #text = text.replace(' ', "\t")
        self.RoutputWindow.setPlainText(unicode(text))
