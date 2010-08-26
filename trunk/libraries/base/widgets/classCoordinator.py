"""
<name>Class Coordinator</name>
<author>Appends a class manager to a data table or matrix.  This wll allow classificaiton widgets to work on the data and share those manipulations across all of the downstream widgets.  These widgets will create the class manager themselves if none exists, but using the Class Coordinator is generally better.</author>
<RFunctions>None</RFunctions>
<tags>Data Classification</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.qtWidgets.textEdit import textEdit
class classCoordinator(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.setRvariableNames(["cm"])
        self.inputs.addInput('id0', 'In Data', redRRDataFrame, self.gotData)

        self.outputs.addOutput('id0', 'Out Data', redRRDataFrame)

        self.outputWindow = textEdit(self.controlArea, label = 'Class Manager Output')
    def gotData(self, data):
        if data:
            newData = data.copy()
            self.R(self.Rvariables['cm']+'<-list()')
            newData.setOptionalData('cm', self, self.Rvariables['cm'], 'Data added by the Class Coordinator so that class data can be shared across multiple widgets.')
            self.rSend('Out Data', newData)
        else:
            self.rSend('Out Data', None)
            
    def refresh(self):
        text = self.R('paste(capture.output('+self.Rvariables['cm']+'), collapse = "\n")')
        self.outputWindow.setHtml('<pre>'+text+'</pre>')