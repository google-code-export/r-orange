"""
<name>Size Plot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>plotrix:sizeplot</RFunctions>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RVector as rvec
class sizeplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.inputs = [("y", rvec.RVector, self.processy),("x", rvec.RVector, self.processx)]
        
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.RFunctionParamy_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "y:", text = '')
        self.RFunctionParamx_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "x:", text = '')
        self.RFunctionParamscale_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "scale:", text = '1')
        self.RFunctionParamsize_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "size:", text = 'c(1,4)')
        self.RFunctionParampow_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "pow:", text = '0.5')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processy(self, data):
        if not self.require_librarys(["plotrix"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_y=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_y=''
    def processx(self, data):
        if not self.require_librarys(["plotrix"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.RFunctionParam_x=data.getData()
            #self.data = data
            self.commitFunction()
        else:
            self.RFunctionParam_x=''
    def commitFunction(self):
        if str(self.RFunctionParam_y) == '': return
        if str(self.RFunctionParam_x) == '': return
        injection = []
        if str(self.RFunctionParamy_lineEdit.text()) != '':
            string = 'y='+str(self.RFunctionParamy_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamx_lineEdit.text()) != '':
            string = 'x='+str(self.RFunctionParamx_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamscale_lineEdit.text()) != '':
            string = 'scale='+str(self.RFunctionParamscale_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamsize_lineEdit.text()) != '':
            string = 'size='+str(self.RFunctionParamsize_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParampow_lineEdit.text()) != '':
            string = 'pow='+str(self.RFunctionParampow_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.Rplot('sizeplot(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        
    def getReportText(self, fileDir):
        if str(self.RFunctionParam_y) == '': return 'Nothing to plot from this widget'
        if str(self.RFunctionParam_x) == '': return 'Nothing to plot from this widget'
        
        self.R('png(file="'+fileDir+'/plot'+str(self.widgetID)+'.png")')
            
        injection = []
        if str(self.RFunctionParamy_lineEdit.text()) != '':
            string = 'y='+str(self.RFunctionParamy_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamx_lineEdit.text()) != '':
            string = 'x='+str(self.RFunctionParamx_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamscale_lineEdit.text()) != '':
            string = 'scale='+str(self.RFunctionParamscale_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamsize_lineEdit.text()) != '':
            string = 'size='+str(self.RFunctionParamsize_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParampow_lineEdit.text()) != '':
            string = 'pow='+str(self.RFunctionParampow_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R('sizeplot(y='+str(self.RFunctionParam_y)+',x='+str(self.RFunctionParam_x)+','+inj+')')
        self.R('dev.off()')
        text = 'The following plot was generated:\n\n'
        #text += '<img src="plot'+str(self.widgetID)+'.png" alt="Red-R R Plot" style="align:center"/></br>'
        text += '.. image:: '+fileDir+'/plot'+str(self.widgetID)+'.png\n    :scale: 50%%\n\n'
            
        return text
