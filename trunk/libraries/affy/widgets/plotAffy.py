"""
<name>Plot Affy Image</name>
<description>Obtains an affybatch and plots the images of the files</description>
<tags>Microarray</tags>
<RFunctions>affy:image</RFunctions>
<icon>icons/plotaffy.png</icon>
"""

from OWRpy import *
import redRGUI
import signals

class plotAffy(OWRpy):
    settingsList = ['irows', 'icols', 'qcsProcessed']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, 'Plot Affy')
        
        #default values        
        #self.irows = 1 #this sets the variable for the rows
        #self.icols = 1 #this sets the variable for the cols
        self.setRvariableNames(['qcs'])
        self.qcsProcessed = 0
        self.data = ''
        
        self.saveSettingsList.append(['qcsProcessed', 'data'])

        self.inputs = [("Affybatch", signals.affy.RAffyBatch, self.init)]
        
        #the GUI
        info = redRGUI.widgetBox(self.controlArea, "Info")
        #self.infoa = redRGUI.widgetLabel(info, 'No data loaded.')
        redRGUI.button(info, "Show Image", callback = self.process, width = 150)
        redRGUI.button(info,"Show Box plot", callback = self.myboxplot, width = 150)
        redRGUI.button(info, "Process and Show QC", callback = self.RAffyQC, width = 150)
        
        optionsa = redRGUI.groupBox(self.controlArea, "Options")
        self.irows = redRGUI.lineEdit(optionsa, text = '1', label = "Number of rows:", orientation="horizontal") #make line edits that will set the values of the irows and icols variables, this seems to happen automatically.  Only need to include variable name where the "irows" is in this example
        self.icols = redRGUI.lineEdit(optionsa, text = '1', label = "Number of columns:", orientation="horizontal")
        #testlineButton = redRGUI.button(optionsa, self, "test line edit", callback = self.test, width = 200)
        
        
    def loadCustomSettings(self,settings=None):
        print 'load affy plot'
        self.processSignals()
        
    def init(self, dataset):
        if dataset:
            self.data = dataset.getData()
            self.status.setText("Data Connected")
            self.qcsProcessed == 0
        else:
            self.status.setText("No data loaded or not of appropriate type.")
            self.data = ''
    
    def process(self):
        #required librarys
        if not self.require_librarys(['affy']):
            self.status.setText('R Libraries Not Loaded.')
            return
        if self.data != '':
            
            #try: 
            self.Rplot('') # make a false call to the plot window just to initialize
            self.R('par(mfrow=c('+str(self.irows.text())+','+str(self.icols.text())+'))') #get the values that are in the irows and icols and put them into the par(mfrow...) function in r
            self.R('image('+self.data+')')
        else:
            self.status.setText("No data connected.")
        #except: 
        #    self.infob.setText("Data not able to be processed")
    
    def myboxplot(self):
        #required librarys
        if not self.require_librarys(['affy']):
            self.status.setText('R Libraries Not Loaded.')
            return
        if self.data == '':return
        #try:
        self.Rplot('boxplot('+self.data+')')
        #except:     
        #    self.infob.setText("Data not able to be processed")
        
    def RAffyQC(self):
        if not self.require_librarys(['simpleaffy']):
            self.status.setText('R Libraries Not Loaded.')
            return
        if self.data =='': return
        if self.qcsProcessed == 0:
            self.R(self.Rvariables['qcs']+'<-qc('+self.data+')')
        self.R('plot('+self.Rvariables['qcs']+')')
        self.qcsProcessed = 1
        