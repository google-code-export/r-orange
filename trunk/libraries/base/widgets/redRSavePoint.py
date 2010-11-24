### RedR-Savepoint Widget.  Allows the user to connect data and treat this as a save point.  the outputs will not be removed even if the upstream widgets are deleted.

"""
<name>Red-R Save Point</name>
<tags>R</tags>
"""

from OWRpy import * 
import OWGUI 
import redRGUI
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
class redRSavePoint(OWRpy): 
    settingsList = ['RFunctionParam_object']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.inputObject = None
        self.outputObject = None
        self.inputs.addInput('id0', 'Input Object', 'All', self.processobject)
        self.outputs = SavepointOutputHandler(self)
        self.outputs.addOutput('id0', 'Output Object', 'All')
        widgetLabel(self.controlArea, 'This widget acts as a save point for analyses so that data is not lost when upstream widgets are removed.  You can use this to help manage memory in your schemas by deleting upstream data (making the schema smaller) yet retaining the analyses.', wordWrap = True)
        redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = textEdit(self.controlArea, label = 'Input Object')
        self.RoutputWindow2 = textEdit(self.controlArea, label = 'Output Object')
        #box.layout().addWidget(self.RoutputWindow)
    def onLoadSavedSession(self):
        self.commitFunction()
    def processobject(self, data):
        if data:
            self.inputObject=data
        else: self.inputObject = None
        
        self.RoutputWindow.setText(unicode(self.inputObject))
    def commitFunction(self):
        self.outputObject = self.inputObject.copy()
        self.RoutputWindow2.setText(unicode(self.outputObject))
        self.rSend('id0', self.outputObject)    
    def getReportText(self, fileDir):
        text = 'ANOVA-LM analysis performted.  The following is a summary of the results:\n\n'
        text += unicode(self.RoutputWindow.toPlainText())+'\n\n'
        return text
        
class SavepointOutputHandler(OutputHandler):
    def __init__(self, parent):
        OutputHandler.__init__(self, parent)
    def propogateNone(self, ask = True):
        pass  # disable the effect of None propogation
