"""
<name>Fast Discrete Fourier Transform</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Performs the Fast Fourier Transform of an array.  Takes an RMatrix and returns an RMatrix.  The inverse argument can be used to make the inverse of the transformaiton instead.</description>
<RFunctions>stats:fft</RFunctions>
<tags>Stats</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
class RedRfft(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["fft"])
        self.data = {}
        self.RFunctionParam_z = ''
        self.inputs.addInput('id0', 'z', redRRMatrix, self.processz)

        self.outputs.addOutput('id0', 'fft Output', redRRMatrix)

        
        self.RFunctionParaminverse_radioBox = radioButtons(self.controlArea, label = "inverse:", buttons = ["Yes","No"], setChecked = "No")
        button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processz(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_z=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_z=''
    def commitFunction(self):
        if str(self.RFunctionParam_z) == '': return
        injection = []
        if str(self.RFunctionParaminverse_radioBox.getChecked()) == 'Yes':
            injection.append('inverse = TRUE')
        else:
            injection.append('inverse = FALSE')
        inj = ','.join(injection)
        self.R(self.Rvariables['fft']+'<-fft(z='+str(self.RFunctionParam_z)+','+inj+')')
        newData = redRRMatrix(data = self.Rvariables["fft"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("fft Output", newData)
