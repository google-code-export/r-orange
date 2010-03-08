"""
<name>Present calls with panp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<tags>Microarray</tags>
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

        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        # self.senddata = {}
        # self.data = {}
        # self.eset = ''
        self.panpinfo = '' #used to communicate info after session reload.
        
        self.setRvariableNames(['PA','PAcalls','PAcalls_sum','Present','peset'])
        self.loadSettings()
        
        self.inputs = [("Normalized Affybatch", RAffyClasses.RAffyBatch, self.process)]
        self.outputs = [("Present Gene Signal Matrix", RvarClasses.RDataFrame)]
        
        
        #GUI
        box = redRGUI.groupBox(self.controlArea, "Options")
        
        self.looseCut = redRGUI.lineEdit(box, text='0.02', label="Loose Cut", orientation = "horizontal")
        self.tightCut = redRGUI.lineEdit(box, text='0.01', label="Tight Cut", orientation = "horizontal")
        self.percentA = redRGUI.lineEdit(box, text='20', label="Percent Absent", orientation = "horizontal")
        processbutton = redRGUI.button(box, label="Process eSet", callback = self.processEset)
        
        

    def onLoadSavedSession(self):
        # may want to check if the Rvariable exists
        print 'onload panp'
        if self.R('exists("'+self.Rvariables['peset']+'")'):
            #self.infoa.setText('Processed')
            self.status.setHtml("Processed")
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
            self.status.setHtml("Blank data recieved")
        if dataset:
            self.data = dataset.copy()
            if 'data' in self.data:
                self.eset = self.data['data']
                self.status.setHtml("Data Received")
            else:
                self.status.setHtml("Processing impossible, not of eset or affybatch type")
        else:
            self.status.setHtml("Processing impossible, not of eset or affybatch type")
            
    def processEset(self):
        try:
            self.eset
        except:
            return
        self.status.setHtml("Processing Started!!!")
        self.R(self.Rvariables['PA'] + '<-pa.calls('+self.eset+', looseCutoff='+self.looseCut.text()+', tightCutoff='+self.tightCut.text()+')','setRData', True)
        self.status.setHtml('PA calls have been calculated')
        self.R(self.Rvariables['PAcalls'] + '<-' + self.Rvariables['PA'] + '$Pcalls == "A"','setRData', True)
        self.R(self.Rvariables['PAcalls_sum'] + '<-apply(' + self.Rvariables['PAcalls'] + ', 1, sum)','setRData', True)
        self.R(self.Rvariables['Present'] + '<- ' + self.Rvariables['PAcalls_sum'] + '/length(' + self.Rvariables['PAcalls'] + '[1,]) > '+self.percentA.text()+'/100','setRData', True)
        self.R(self.Rvariables['peset']+'<-as.data.frame(exprs('+self.eset+')[' + self.Rvariables['Present'] + ',])','setRData',True)
        self.R('colnames('+self.Rvariables['peset']+') <- colnames(exprs('+self.eset+'))')
        self.panpinfo = 'Processed with loose cut off = '+self.looseCut.text()+', tight cut off ='+self.tightCut.text()+', and percent absent = '+self.percentA.text()
        self.status.setHtml('Processed')
        self.senddata = self.data.copy()
        self.senddata['data'] = self.Rvariables['peset']
        self.senddata['eset'] = self.eset
        self.rSend('Present Gene Signal Matrix', self.senddata)
    

    
        