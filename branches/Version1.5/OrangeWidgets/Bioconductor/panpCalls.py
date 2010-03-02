"""
<name>Present calls with panp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<tags>microarray</tags>
<RFunctions>panp:pa.calls</RFunctions>
<icon>icons/readcel.png</icon>
<priority>2010</priority>
"""
from OWRpy import *
import redRGUI
import RAffyClasses

class panpCalls(OWRpy):
    settingsList = ['Rvariables','panpinfo', 'senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset'])

        self.senddata = {}
        self.data = {}
        self.eset = ''
        self.panpinfo = '' #used to communicate info after session reload.
        
        self.looseCut = '0.02'
        self.tightCut = '0.01'
        self.percentA = '20'
        
        self.setRvariableNames(['PA','PAcalls','PAcalls_sum','Present','peset'])
        self.loadSettings()

        


        
        self.inputs = [("Normalized Affybatch", RAffyClasses.RAffyBatch, self.process)]
        self.outputs = [("Present Gene Signal Matrix", RvarClasses.RDataFrame)]
        
        
        #GUI
        box = redRGUI.widgetBox(self.controlArea, "Options")
        
        redRGUI.lineEdit(box, self, "looseCut", "Loose Cut", orientation = "horizontal")
        redRGUI.lineEdit(box, self, "tightCut", "Tight Cut", orientation = "horizontal")
        redRGUI.lineEdit(box, self, "percentA", "Percent Absent", orientation = "horizontal")
        processbutton = redRGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
        self.infoa = redRGUI.widgetLabel(box, "Widget Initialized")
        

    def onLoadSavedSession(self):
        # may want to check if the Rvariable exists
        print 'onload panp'
        if self.R('exists("'+self.Rvariables['peset']+'")'):
            self.infoa.setText('Processed')
            self.senddata = self.data.copy()
            self.senddata['data'] = self.Rvariables['peset']
            self.senddata['eset'] = self.eset
            self.rSend('Present Gene Signal Matrix', self.senddata)
        
    def process(self, dataset):
        print 'on procress panp'
        self.require_librarys(['affy','gcrma','limma','matchprobes','panp'])
        for output in self.outputs:
            self.rSend(output[0], None, 0)
        if dataset == None: 
            self.infoa.setText("Blank data recieved")
        if dataset:
            self.data = dataset.copy()
            if 'data' in self.data:
                self.eset = self.data['data']
                self.infoa.setText("Data Received")
            else:
                self.infoa.setText("Processing imposible, not of eset or affybatch type")
        else:
            self.infoa.setText("Processing imposible, not of eset or affybatch type")
            
    def processEset(self):
        self.infoa.setText("Processing Started!!!")
        self.R(self.Rvariables['PA'] + '<-pa.calls('+self.eset+', looseCutoff='+self.looseCut+', tightCutoff='+self.tightCut+')','setRData', True)
        self.infoa.setText('PA calls have been calculated')
        self.R(self.Rvariables['PAcalls'] + '<-' + self.Rvariables['PA'] + '$Pcalls == "A"','setRData', True)
        self.R(self.Rvariables['PAcalls_sum'] + '<-apply(' + self.Rvariables['PAcalls'] + ', 1, sum)','setRData', True)
        self.R(self.Rvariables['Present'] + '<- ' + self.Rvariables['PAcalls_sum'] + '/length(' + self.Rvariables['PAcalls'] + '[1,]) > '+self.percentA+'/100','setRData', True)
        self.R(self.Rvariables['peset']+'<-as.data.frame(exprs('+self.eset+')[' + self.Rvariables['Present'] + ',])','setRData',True)
        self.R('colnames('+self.Rvariables['peset']+') <- colnames(exprs('+self.eset+'))')
        self.panpinfo = 'Processed with loose cut off = '+self.looseCut+', tight cut off ='+self.tightCut+', and percent absent = '+self.percentA
        self.infoa.setText('Processed')
        self.senddata = self.data.copy()
        self.senddata['data'] = self.Rvariables['peset']
        self.senddata['eset'] = self.eset
        self.rSend('Present Gene Signal Matrix', self.senddata)
    

    
        