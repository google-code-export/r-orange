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
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix

from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.checkBox import checkBox as redRCheckBox

class RedRfft(OWRpy): 
    globalSettingsList = ['commitOnInput']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["fft"])
        self.data = {}
        self.RFunctionParam_z = ''
        self.isNumeric = False
        self.inputs.addInput('id0', 'z', redRRMatrix, self.processz)

        self.outputs.addOutput('id0', 'fft Output', redRRMatrix)

        
        self.RFunctionParaminverse_radioBox = radioButtons(self.controlArea, 
        label = "inverse:", buttons = ["Yes","No"], setChecked = "No")
        self.commitOnInput = redRCheckBox(self.bottomAreaRight, buttons = ['Commit on Input'],
        toolTips = ['On data input, process and send data forward.'])

        self.commitButton = button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        
    def processz(self, data):
        if data:
            self.RFunctionParam_z=data.getData()
            if not self.R('is.numeric(%s)' % self.RFunctionParam_z, silent=True):
                self.status.setText('Data Must be Numeric')
                self.commitButton.setDisabled(True)
                return
            else:
                self.commitButton.setEnabled(True)
                self.status.setText('')
            if 'Commit on Selection' in self.commitOnInput.getChecked():
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
        self.rSend("id0", newData)
