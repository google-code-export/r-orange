"""
<name>Fast Discrete Fourier Transform</name>
<tags>Stats</tags>
<icon></icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 


class RedRfft(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["fft"])
        self.data = {}
        self.RFunctionParam_z = ''
        self.isNumeric = False
        self.inputs.addInput('id0', 'z', signals.base.RMatrix, self.processz)

        self.outputs.addOutput('id0', 'fft Output', signals.base.RMatrix)

        
        self.RFunctionParaminverse_radioBox = redRGUI.base.radioButtons(self.controlArea, 
        label = "inverse:", buttons = ["Yes","No"], setChecked = "No")
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)

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
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_z=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_z) == '': return
        injection = []
        if unicode(self.RFunctionParaminverse_radioBox.getChecked()) == 'Yes':
            injection.append('inverse = TRUE')
        else:
            injection.append('inverse = FALSE')
        inj = ','.join(injection)
        self.R(self.Rvariables['fft']+'<-fft(z='+unicode(self.RFunctionParam_z)+','+inj+')')
        newData = signals.base.RMatrix(self, data = self.Rvariables["fft"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("id0", newData)
