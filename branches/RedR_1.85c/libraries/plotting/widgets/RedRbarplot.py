"""
<name>Bar Plot</name>
<tags>Plotting</tags>
<icon>histogram.png</icon>
"""
from OWRpy import * 
import redRGUI, signals

class RedRbarplot(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.RFunctionParam_height = ''
        self.inputs.addInput("height", "Plotting Vector", signals.base.RList, self.processheight)
        
        self.RFunctionParammain_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "main:", text = '')
        self.RFunctionParamhoriz_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "horiz:", text = '')
        self.namesBox = redRGUI.base.comboBox(self.controlArea, label = 'Data Element:', callback = self.commitFunction)
        self.RFunctionParamspace_lineEdit = redRGUI.base.spinBox(self.controlArea, label = "Space:", 
        min = 0, max = 99, value = 5)
        self.RFunctionParamxlab_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "xlab:", text = '')
        self.plotArea = redRGUI.base.graphicsView(self.controlArea,label='Bar Plot', displayLabel=False)
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
    def processheight(self, data):
        if not self.require_librarys(["graphics"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_height=data.getData()
            self.namesBox.update(self.R('names('+self.RFunctionParam_height+')',wantType='list'))
            #self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_height=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_height) == '': return
        
        injection = []
        if unicode(self.RFunctionParammain_lineEdit.text()) != '':
            string = 'main='+unicode(self.RFunctionParammain_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamhoriz_lineEdit.text()) != '':
            string = 'horiz='+unicode(self.RFunctionParamhoriz_lineEdit.text())+''
            injection.append(string)
        if unicode(self.RFunctionParamspace_lineEdit.text()) != '':
            string = 'space='+unicode(int(self.RFunctionParamspace_lineEdit.value())/100)+''
            injection.append(string)
        if unicode(self.RFunctionParamxlab_lineEdit.text()) != '':
            string = 'xlab='+unicode(self.RFunctionParamxlab_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.plotArea.plot('height=table('+unicode(self.RFunctionParam_height)+'$'+unicode(self.namesBox.currentText())+')[unique('+unicode(self.RFunctionParam_height)+'$'+unicode(self.namesBox.currentText())+')],'+inj, function = 'barplot', dwidth = int(self.R('length(names('+self.RFunctionParam_height+'))'))* 20)