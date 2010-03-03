"""
<name>Read CEL Files</name>
<description>Allows the user to pick CEL files either individually or through a .txt file and outputs the eSet as an R.object</description>
<tags>Microarray</tags>
<RFunctions>affy:ReadAffy,affy:justRMA</RFunctions>
<icon>icons/readcel.png</icon>
<priority>10</priority>
"""

from OWRpy import *
#import OWGUI
import redRGUI 
import RAffyClasses


class ReadCEL(OWRpy):
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "ReadCEL", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['recentFiles'])
        #default values        
        self.recentFiles = []
        self.methodcombo = 0
        self.loadSettings()
        
        
        #set R variable names
        self.setRvariableNames(['eset','folder'])
        
        #signals
        self.inputs = None 
        self.outputs = [("Expression Matrix", RvarClasses.RDataFrame), ("Eset", RAffyClasses.Eset)]
        


        #GUI
        box = redRGUI.groupBox(self.controlArea, "Select Folder", addSpace = True, orientation='vertical')
        self.numArrays = redRGUI.comboBox(box, label = 'Number of arrays', items = ['Less than 40', 'More than 40'])
        self.filecombo = redRGUI.comboBox(box, items = self.recentFiles, callback=self.selectFile)
        
        #self.filecombo = QComboBox(box)
        self.filecombo.setMinimumWidth(150)
        # box.layout().addWidget(self.filecombo)
        button = redRGUI.button(box, self, '...', callback = self.browseFile, width = 25, disabled=0)
        box = redRGUI.groupBox(self.controlArea, "Info", addSpace = True)
        self.infoa = redRGUI.widgetLabel(box, 'No data loaded.')
        self.infob = redRGUI.widgetLabel(box, '')
        self.infoc = redRGUI.widgetLabel(box, '')
        self.infod = redRGUI.widgetLabel(box, '')
        self.setFileList()
        # self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)
        
        
    # def onLoadSavedSession(self):
        # self.infoc.setText("Data reloaded from saved session.")
        # self.infod.setText("You may want to use a data viewer to check the data.")
        # if self.Rvariables['eset'] in self.R('ls()'):
            # self.sendMe()        
    def setFileList(self):
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(file)
        

    def selectFile(self, n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(1)

        if len(self.recentFiles) > 0:
            self.setFileList()
        self.R(self.Rvariables['folder'] + ' = "' + self.recentFiles[0].replace('\\', '\\\\') + '"', 'setRData')
        self.process()
        
        
    def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
        self.R(self.Rvariables['folder'] +'<-choose.dir()', 'setRData')
        if not self.R('is.na(' + self.Rvariables['folder'] +')'):
            folder = self.R(self.Rvariables['folder'])
            if folder in self.recentFiles: self.recentFiles.remove(folder)
            self.recentFiles.insert(0, folder)
            self.setFileList()
            self.process()
        
    def process(self):
        self.infoa.setText("Your data is processing")
        #required librarys
        self.require_librarys(['affy'])
        if self.methodcombo == 0:
            self.R(self.Rvariables['eset']+'<-ReadAffy(celfile.path='+self.Rvariables['folder']+')','setRData',True)
        if self.methodcombo == 1:
            self.infob.setText("This may take several minutes")
            self.R(self.Rvariables['eset']+'<-justRMA(celfile.path='+self.Rvariables['folder']+')','setRData',True)
            self.infoc.setText("Data preprocessed with RMA normalization")
        self.infoa.setText("Your data has been processed.")
        self.sendMe()
        
    
    def sendMe(self):
        out = {'data':'exprs('+self.Rvariables['eset']+')', 'eset':self.Rvariables['eset'], 'cm':'cm_'+self.Rvariables['eset'], 'parent':'exprs('+self.Rvariables['eset']+')'}
        self.rSend("Expression Matrix", out)
        self.rSend("Eset", {'data':self.Rvariables['eset']})
