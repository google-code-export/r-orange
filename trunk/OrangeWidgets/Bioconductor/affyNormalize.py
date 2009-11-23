"""
<name>Normalize</name>
<description>Processes an Affybatch to an eset using RMA</description>
<tags>Bioconductor</tags>
<icon>icons/Normalize.png</icon>
<priority>1010</priority>
"""


from OWRpy import *
# import OWGUI
import RAffyClasses
import redRGUI 


class affyNormalize(OWRpy):
    # settingsList = ['norminfo', 'enableMethBox', 'data','normmeth', 'normoptions', 'bgcorrect', 'bgcorrectmeth', 'pmcorrect', 'summarymeth', 'norm', 'selectMethod']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "Normalization")
        
        #OWRpy.__init__(self)
        #self.setStateVariables(['enableMethBox','data','normmeth', 'normoptions', 'bgcorrect', 'bgcorrectmeth', 'pmcorrect', 'summarymeth', 'norm', 'selectMethod'])
        #default values        
        self.normmeth = 'quantiles'
        self.normoptions = ''
        self.bgcorrect = 'FALSE'
        self.bgcorrectmeth = 'none'
        self.pmcorrect = 'pmonly'
        self.summarymeth = 'liwong'
        self.norm = ['quantiles']
        self.data = ''
        self.enableMethBox = False
        self.norminfo = ''
        self.loadSettings()
        
        self.require_librarys(['affy'])
        
        
        
        #set R variable names
        self.setRvariableNames(['normalized_affybatch','folder'])
        
        #signals		
        self.inputs = [("Eset", RAffyClasses.Eset, self.process)]
        self.outputs = [("Normalized Expression Matrix", RvarClasses.RDataFrame),("Normalized AffyBatch", RAffyClasses.RAffyBatch)]

        
        #the GUI
        status = redRGUI.widgetBox(self.controlArea, "Status")
        self.infoa = redRGUI.widgetLabel(status, 'No data loaded.')
        #normrad = redRGUI.widgetBox(self.controlArea, "Normalization Methods")

        self.selMethBox = redRGUI.radioButtons(self.controlArea, 'Normalization Method', ["RMA", "MAS5", "Custom"], callback=self.selectMethodChanged)
        self.selMethBox.setChecked('RMA')
        # QObject.connect(self.selMethBox.buttons, SIGNAL('buttonClicked(int)'), self.selectMethodChanged)
        
        # self.selMethBox.setEnabled(self.enableMethBox)
        info = redRGUI.widgetBox(self.controlArea, "Normalization Options")
        
        #drop list box
        
        #insert a block to check what type of object is connected.  If nothing connected set the items of the normalize methods objects to 
        self.normselector = redRGUI.comboBox(info, label="Normalization Method", items=self.norm, orientation=0)
        self.normselector.setEnabled(False)
        self.bgcorrectselector = redRGUI.comboBox(info, label="Background Correct Methods", items=['TRUE', 'FALSE'], orientation=0)
        self.bgcorrectselector.setEnabled(False)
        self.bgcmethselector = redRGUI.comboBox(info, label="Background Correct Methods", items=self.rsession('bgcorrect.methods'), orientation=0)
        self.bgcmethselector.setEnabled(False)
        self.pmcorrectselector = redRGUI.comboBox(info, label="Perfect Match Correct Methods", items=self.rsession('pmcorrect.methods'), orientation=0)
        self.pmcorrectselector.setEnabled(False)
        self.summethselector = redRGUI.comboBox(info, label="Summary Methods", items=self.rsession('express.summary.stat.methods'), orientation=0)
        self.summethselector.setEnabled(False)
        
        
        runbutton = redRGUI.button(info, self, "Run Normalization", callback = self.normalize, width=200)
        
    # def onLoadSavedSession(self):
        # print 'load affy norm'
        # self.selectMethodChanged()
        # self.selMethBox.setEnabled(True)
        # if self.Rvariables['normalized_affybatch'] in self.R('ls()'):
            # self.toSend()
            # self.infoa.setText(self.norminfo)

        
    def normalize(self):
        self.infoa.setText('Processing')
        if self.selectMethod == 0:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-rma('+self.data+')',True) #makes the rma normalization
            self.norminfo = 'Normalized with RMA'
        if self.selectMethod == 1:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-mas5('+self.data+')',True) #makes the mas5 normalization
            self.norminfo = 'Normalized with MAS5'
        if self.selectMethod == 2:
            self.rsession(self.Rvariables['normalized_affybatch']+'<-expresso('+self.data+', bg.correct='+self.bgcorrect+', bgcorrect.method="'+self.bgcorrectmeth+'", pmcorrect.method="'+self.pmcorrect+'", summary.method="'+self.summarymeth+'")',True)
            self.norminfo = 'Normalized by: Background Correction:'+self.bgcorrect+', Method:'+self.bgcorrectmeth+', Perfect Match Correct Method: '+self.pmcorrect+', Summary Method: '+self.summarymeth
        self.toSend()
        self.infoa.setText(self.norminfo)
        
    def collectOptions(self):
        if self.normmeth == None: self.normoptions = ""
        elif self.normmeth == "":
            self.normmeth = None
            self.collectOptions()
        else:
            self.normoptions = ',method='+self.normmeth
    
    def process(self, dataset):
        #required librarys
        
        #self.needsProcessingHandler(self, 1)
        
        self.rSend("Normalized Expression Matrix", None) #start the killing cascade because normalization is required
        self.rSend("Normalized AffyBatch", None) #start the killing cascade because normalization is required
                
        try: 
            print str(dataset['data'])
            self.data = str(dataset['data'])
            
            
            if self.rsession('length(exprs('+self.data+')[1,])') > 10:
                self.selectMethod = 2
                self.selectMethodChanged()
                
            else:
                self.selectMethod = 0
                self.selectMethodChanged()
                
            self.selMethBox.setEnabled(True)
            self.infoa.setText('Data Loaded')
            # if dataset['kill'] == True:
                # self.rSend("Normalized DataFrame", {'kill':True, 'data':''})
                # self.rSend("Normalized AffyBatch", {'kill':True, 'data':''})
        except: 
            print 'error'

        
        self.bgcmethselector.addItems(self.rsession('bgcorrect.methods'))
        self.pmcorrectselector.addItems(self.rsession('pmcorrect.methods'))
        self.summethselector.addItems(self.rsession('express.summary.stat.methods'))
        
    
    def selectMethodChanged(self):
        # print 'callback#################################'
        # return
        # print self.__dict__
        # print ev.__dict__
        # print 'asdfasdfasdf'
        # if not 'selMethBox' in self.__dict__.keys(): return;
        # return
        if self.selMethBox.getChecked() == 'RMA':
            self.bgcorrectselector.setEnabled(False)
            self.bgcmethselector.setEnabled(False)
            self.pmcorrectselector.setEnabled(False)
            self.summethselector.setEnabled(False)
            self.normselector.setEnabled(False)
        elif self.selMethBox.getChecked() == 'MAS5':
            self.bgcorrectselector.setEnabled(False)
            self.bgcmethselector.setEnabled(False)
            self.pmcorrectselector.setEnabled(False)
            self.summethselector.setEnabled(False)
            self.normselector.setEnabled(False)
        elif self.selMethBox.getChecked() == 'Custom':
            self.bgcorrectselector.setCurrentIndex(self.bgcorrectselector.findText('FALSE'))
            self.bgcorrectselector.setEnabled(True)
            self.bgcorrectmeth = 'none'
            self.bgcmethselector.setCurrentIndex(self.bgcmethselector.findText('none'))
            self.bgcmethselector.setEnabled(True)
            self.pmcorrect = 'pmonly'
            self.pmcorrectselector.setCurrentIndex(self.pmcorrectselector.findText('pmonly'))
            self.pmcorrectselector.setEnabled(True)
            self.summarymeth = 'liwong'
            self.summethselector.setCurrentIndex(self.summethselector.findText('liwong'))
            self.summethselector.setEnabled(True)
            self.norm = ['quantiles']
            self.normselector.clear()
            self.normselector.addItems(self.rsession('normalize.methods('+self.data+')'))
            self.normselector.setCurrentIndex(self.normselector.findText('invariantset'))
            self.normselector.setEnabled(True)
        
        #self.infoa.setText('Ready to Normalize')

    def toSend(self):
        neset = {'data':'exprs('+self.Rvariables['normalized_affybatch']+')', 'eset':self.Rvariables['normalized_affybatch']}
        self.rSend("Normalized Expression Matrix", neset)
        self.rSend("Normalized AffyBatch", {'data':self.Rvariables['normalized_affybatch']})
    
