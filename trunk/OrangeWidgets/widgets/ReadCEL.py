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
import redRGUI, os
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
        # make sure that there is an escape option for the file selection 
        if '' not in self.recentFiles:
            self.recentFiles.insert(0, '')
        
        #set R variable names
        self.setRvariableNames(['eset','folder'])
        
        #signals
        self.inputs = None 
        self.outputs = [("Expression Matrix", RvarClasses.RDataFrame), ("Eset", RAffyClasses.Eset)]
        


        #GUI
        box = redRGUI.groupBox(self.controlArea, "Select Folder",
        sizePolicy=QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        
        self.numArrays = redRGUI.radioButtons(box, label = 'Number of arrays', 
        buttons = ['Less than 40', 'More than 40'])
        
        self.filecombo = redRGUI.comboBox(box, items = self.recentFiles, 
        callback=self.selectFile)
        
        
        buttonsBox = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        button = redRGUI.button(buttonsBox, 'Add Folder', callback = self.browseFile, disabled=0)
        button2 = redRGUI.button(buttonsBox, 'Process File', callback = self.process)
        
        # box = redRGUI.groupBox(self.controlArea, "Info", addSpace = True)
        # self.status = redRGUI.widgetLabel(box, 'No data loaded.')
        self.setFileList()
        
                
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
        #self.R(self.Rvariables['folder'] + ' = "' + str(self.filecombo.currentText()).replace('\\', '\\\\') + '"', 'setRData')
        #self.process()
        
        
    def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
        fn = QFileDialog.getExistingDirectory(None, 'CEL File Directory', os.path.abspath('/'))
        print str(fn)
        if fn.isEmpty(): return
        #self.R(self.Rvariables['folder'] + '<-"' + str(os.path.abspath(str(fn))).replace('\\', '\\\\') + '"')
        folder = str(os.path.abspath(fn))
        if folder in self.recentFiles: self.recentFiles.remove(folder)
        self.recentFiles.insert(0, folder)
        self.setFileList()
        #self.process()
        
    def process(self):
        self.status.setText("Your data is processing")
        #required librarys
        self.require_librarys(['affy'])
        if self.methodcombo == 0:
            self.R(self.Rvariables['eset']+'<-ReadAffy(celfile.path="'+str(self.filecombo.currentText()).replace('\\', '\\\\')+'")','setRData',True)
        if self.methodcombo == 1:
            self.status.setText("This may take several minutes")
            self.R(self.Rvariables['eset']+'<-justRMA(celfile.path='+self.Rvariables['folder']+')','setRData',True)
            self.status.setText("Data preprocessed with RMA normalization")
        self.status.setText("Your data has been processed.")
        self.sendMe()
        
    
    def sendMe(self):
        out = {'data':'exprs('+self.Rvariables['eset']+')', 'eset':self.Rvariables['eset'], 'cm':'cm_'+self.Rvariables['eset'], 'parent':'exprs('+self.Rvariables['eset']+')'}
        self.rSend("Expression Matrix", out)
        out2 = out.copy()
        out2['data'] = str(self.Rvariables['eset'])
        self.rSend("Eset", out2)
