"""
<name>Present calls with panp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2010</priority>
"""
from OWRpy import *
import OWGUI

class panpCalls(OWRpy):
    #settingsList = ['variable_suffix', 'senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setStateVariables(['senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset'])

        self.senddata = {}
        self.data = {}
        self.eset = ''
        
        self.looseCut = '0.02'
        self.tightCut = '0.01'
        self.percentA = '20'
        
        self.loadSettings()

        
        self.setRvariableNames(['PA','PAcalls','PAcalls_sum','Present','peset'])

        self.require_librarys(['affy','gcrma','limma','panp'])
        
        self.inputs = [("Expression Set", RvarClasses.RVariable, self.process)]
        self.inputs = [("Expression Set", RvarClasses.RVariable, self.process)]
        self.outputs = [("Present Gene Signal Matrix", RvarClasses.RDataFrame)]
        
        
        #GUI
        box = OWGUI.widgetBox(self.controlArea, "Options")
        
        OWGUI.lineEdit(box, self, "looseCut", "Loose Cut", orientation = "horizontal")
        OWGUI.lineEdit(box, self, "tightCut", "Tight Cut", orientation = "horizontal")
        OWGUI.lineEdit(box, self, "percentA", "Percent Absent", orientation = "horizontal")
        processbutton = OWGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
        self.infoa = OWGUI.widgetLabel(box, "Processing not begun")
        if self.loadingSavedSession:
            self.processEset()

        
    def process(self, dataset):
        if dataset:
            self.data = dataset
            if 'eset' in self.data:
                self.eset = self.data['eset']
            else:
                self.infoa.setText("Processing imposible, not of eset or affybatch type")
        else:
            return
            
    def processEset(self):
        
        if not self.loadingSavedSession:
            self.infoa.setText("Processing Started!!!")
            self.rsession(self.Rvariables['PA'] + '<-pa.calls('+self.eset+', looseCutoff='+self.looseCut+', tightCutoff='+self.tightCut+')',True)
            self.infoa.setText('PA calls have been calculated')
            self.rsession(self.Rvariables['PAcalls'] + '<-' + self.Rvariables['PA'] + '$Pcalls == "A"',True)
            self.rsession(self.Rvariables['PAcalls_sum'] + '<-apply(' + self.Rvariables['PAcalls'] + ', 1, sum)',True)
            self.rsession(self.Rvariables['Present'] + '<- ' + self.Rvariables['PAcalls_sum'] + '/length(' + self.Rvariables['PAcalls'] + '[1,]) > '+self.percentA+'/100',True)
            self.rsession(self.Rvariables['peset']+'<-as.data.frame(exprs('+self.eset+')[' + self.Rvariables['Present'] + ',])',True)
        self.infoa.setText('Processed')
        self.senddata = self.data.copy()
        self.senddata['data'] = self.Rvariables['peset']
        self.rSend('Present Gene Signal Matrix', self.senddata)
    

    
        