"""
<name>Correlation/Variance</name>
<author>Anup Parikh anup@red-r.org</author>
<RFunctions>stats:cor, stats:var, stats:cov</RFunctions>
<tags>Stats</tags>
<icon>RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RMatrix as rmat
class cor(OWRpy): 
    globalSettingsList = ['sendOnSelect']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Correlation", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["cor"])
        self.data = {}
        self.RFunctionParam_y = None
        self.RFunctionParam_x = None
        
        self.inputs = [("x", rdf.RDataFrame, self.processx),("y", rdf.RDataFrame, self.processy)]
        self.outputs = [("cor Output", rmat.RMatrix)]
        
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        
        options = redRGUI.widgetBox(area,orientation='vertical')
        area.layout().setAlignment(options,Qt.AlignTop)
        self.type = redRGUI.radioButtons(options,  label = "Perform", 
        buttons = ['Variance', 'Correlation', 'Covariance'],setChecked='Correlation',
        orientation='vertical',callback=self.changeType)
        
        self.methodButtons = redRGUI.radioButtons(options,  label = "Method", 
        buttons = ['pearson', 'kendall', 'spearman'],setChecked='pearson',
        orientation='vertical')

        self.useButtons =  redRGUI.radioButtons(options, label='Handing Missing Values', setChecked='everything',
        buttons = ["everything","all.obs", "complete.obs", "pairwise.complete.obs"],
        orientation='vertical')

        redRGUI.button(options, "Commit", toolTip='Calculate values', callback = self.commitFunction)
        self.sendOnSelect = redRGUI.checkBox(options,buttons=['Calculate on data Input'], 
        toolTips=['Calculate variance on data input.'])

        self.RoutputWindow = redRGUI.Rtable(area,sortable=True)
        
    def changeType(self):
        if self.type.getChecked() =='Variance':
            self.useButtons.setDisabled(True)
            self.methodButtons.setDisabled(True)
        else:    
            self.useButtons.setEnabled(True)
            self.methodButtons.setEnabled(True)

        if self.type.getChecked() =='Covariance':
            self.useButtons.disable(['pairwise.complete.obs'])
        elif self.type.getChecked() =='Correlation':
            self.useButtons.enable(['pairwise.complete.obs'])
        

    def processy(self, data):
        if data:
            self.RFunctionParam_y=data.getData()
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
    def processx(self, data):
        if data:
            self.RFunctionParam_x=data.getData()
            dims = self.R('dim('+self.RFunctionParam_x+')', silent = True, wantType = 'list')
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
            
    def commitFunction(self):
        if not self.RFunctionParam_x: 
            self.status.setText('X data is missing')
            return

        injection = []
        
        if self.type.getChecked() == 'Correlation':
            test = 'cor'
        elif self.type.getChecked() == 'Variance':
            test = 'var'
        elif self.type.getChecked() == 'Covariance':
            test = 'cov'
            
        if self.useButtons.getChecked():
            string = 'use=\''+str(self.useButtons.getChecked())+'\''
            injection.append(string)
        elif self.type.getChecked() == 'Variance':
            string = 'na.rm=TRUE'
            injection.append(string)
        
        if self.methodButtons.getChecked():
            string = 'method=\''+str(self.methodButtons.getChecked())+'\''
            injection.append(string)
            
        if self.RFunctionParam_y:
            injection.append('y='+str(self.RFunctionParam_y))

            
        inj = ','.join(injection)
        
        self.R(self.Rvariables['cor']+'<-'+test+'(x='+str(self.RFunctionParam_x)+','+inj+')')
        # self.R('txt<-capture.output('+self.Rvariables['cor']+')')
        self.RoutputWindow.clear()
        self.RoutputWindow.setRTable(self.Rvariables['cor'])
        # tmp = self.R('paste(txt, collapse ="\n")')
        # self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        
        newData = rmat.RMatrix(data = self.Rvariables["cor"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        self.rSend("cor Output", newData)
