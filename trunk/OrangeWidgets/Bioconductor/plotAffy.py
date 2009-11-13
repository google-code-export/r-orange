"""
<name>Plot Affy Image</name>
<description>Obtains an affybatch and plots the images of the files</description>
<tags>Bioconductor</tags>
<icon>icons/plotAffy.png</icon>
<priority>70</priority>
"""

from OWRpy import *
import OWGUI
import RAffyClasses

class plotAffy(OWRpy):
    settingsList = ['irows', 'icols', 'qcsProcessed']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        
        #default values        
        self.irows = 1 #this sets the variable for the rows
        self.icols = 1 #this sets the variable for the cols
        self.setRvariableNames(['qcs'])
        self.qcsProcessed = 0
        self.data = ''
        self.loadSettings()

        #set R variable names
        #self.setRvariableNames()

        self.inputs = [("Affybatch", RAffyClasses.Eset, self.init)]
        self.outputs = None
        
        self.testLineEdit = ""

        
        #the GUI
        info = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(info, 'No data loaded.')
        OWGUI.button(info, self, "Show Image", callback = self.process, width = 200)
        OWGUI.button(info, self, "Show Box plot", callback = self.myboxplot, width = 200)
        OWGUI.button(info, self, "Process and Show QC", callback = self.RAffyQC, width = 200)
        
        optionsa = OWGUI.widgetBox(self.controlArea, "Options")
        self.infob = OWGUI.widgetLabel(optionsa, 'Button not pressed')
        #OWGUI.lineEdit(optionsa, self, "testLineEdit", "Test Line Edit", orientation = "horizontal")
        OWGUI.lineEdit(optionsa, self, "irows", "Number of rows:", orientation="horizontal") #make line edits that will set the values of the irows and icols variables, this seems to happen automatically.  Only need to include variable name where the "irows" is in this example
        OWGUI.lineEdit(optionsa, self, "icols", "Number of columns:", orientation="horizontal")
        #testlineButton = OWGUI.button(optionsa, self, "test line edit", callback = self.test, width = 200)
        
        
    def onLoadSavedSession(self):
        print 'load affy plot'
        self.processSignals()
        
    def init(self, dataset):
        if dataset and 'data' in dataset:
            self.data = dataset['data']
            self.infoa.setText("Data Connected")
            self.qcsProcessed == 0
        else:
            self.infoa.setText("No data loaded or not of appropriate type.")
            self.data = ''
    
    def process(self):
        #required librarys
        self.require_librarys(['affy'])
        if self.data != '':
            
            #try: 
            self.Rplot('') # make a false call to the plot window just to initialize
            self.rsession('par(mfrow=c('+str(self.irows)+','+str(self.icols)+'))') #get the values that are in the irows and icols and put them into the par(mfrow...) function in r
            self.R('image('+self.data+')')
        else:
            self.infoa.setText("No data connected.")
        #except: 
        #    self.infob.setText("Data not able to be processed")
    
    def myboxplot(self):
        #required librarys
        self.require_librarys(['affy'])
        #try:
        self.Rplot('boxplot('+self.data+')')
        #except:     
        #    self.infob.setText("Data not able to be processed")
        
    def RAffyQC(self):
        self.require_librarys(['simpleaffy'])
        if self.qcsProcessed == 0:
            self.rsession(self.Rvariables['qcs']+'<-qc('+self.data+')')
        self.R('plot('+self.Rvariables['qcs']+')')
        self.qcsProcessed = 1
        