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
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "ReadCEL", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['recentFiles'])
        #default values        
        self.recentFiles = ['Select Directory']
        self.path = os.path.abspath('/')
        self.methodcombo = 0
        self.loadSettings()
        # make sure that there is an escape option for the file selection 
        # if '' not in self.recentFiles:
            # self.recentFiles.insert(0, '')
        
        #set R variable names
        self.setRvariableNames(['eset','folder'])
        
        #signals
        self.inputs = None 
        self.outputs = [("Expression Matrix", RvarClasses.RDataFrame), ("Eset", RAffyClasses.Eset)]
        


        #GUI
        box = redRGUI.groupBox(self.controlArea, "Select Folder",orientation='horizontal')
        #sizePolicy=QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        
        self.filecombo = redRGUI.comboBox(box, items = self.recentFiles)
        self.filecombo.setCurrentIndex(0)
        button = redRGUI.button(box, 'Browse', callback = self.browseFile)
        
        self.numArrays = redRGUI.radioButtons(self.controlArea, label = 'Number of arrays', 
        buttons = ['Less than 40', 'More than 40'],setChecked='Less than 40', orientation='horizontal')

        button2 = redRGUI.button(self.bottomAreaRight, 'Process Folder', callback = self.process)
        
        self.setFileList()
        
    def setFileList(self):
        if self.recentFiles == None: self.recentFiles = ['Select Directory']
        
        self.filecombo.clear()
        for file in self.recentFiles:
            self.filecombo.addItem(os.path.basename(file))

        # self.filecombo.setCurrentIndex(data['current'])
        # self.scanFile()
    
    def browseFile(self): 
        fn = QFileDialog.getExistingDirectory(self, "CEL Directory", self.path)
        
        #print str(fn)
        if fn.isEmpty(): return
        self.path = os.path.split(str(fn))[0]
        if fn in self.recentFiles:
            self.recentFiles.remove(str(fn))
        self.recentFiles.append(str(fn))
        self.filecombo.addItem(os.path.basename(str(fn)))
        self.filecombo.setCurrentIndex(len(self.recentFiles)-1)
        
        self.saveSettings()
        
    def process(self):
        
        if(self.recentFiles[self.filecombo.currentIndex()] == 'Select Directory'):
            return
        dir = self.recentFiles[self.filecombo.currentIndex()].replace('\\', '\\\\')
        self.status.setText("Your data is processing")
        #required librarys
        self.require_librarys(['affy'])
        if self.numArrays.getChecked() == 'Less than 40':
            self.R(self.Rvariables['eset']+'<-ReadAffy(celfile.path="'+dir+'")','setRData',True)
            self.status.setText("Your data has been processed with ReadAffy.")
        else:
            self.status.setText("This may take several minutes")
            self.R(self.Rvariables['eset']+'<-justRMA(celfile.path='+self.Rvariables['folder']+')','setRData',True)
            self.status.setText("Data preprocessed with justRMA.")
        
        self.sendMe()
        
    
    def sendMe(self):
        out = {'data':'exprs('+self.Rvariables['eset']+')', 'eset':self.Rvariables['eset'], 'cm':'cm_'+self.Rvariables['eset'], 'parent':'exprs('+self.Rvariables['eset']+')'}
        self.rSend("Expression Matrix", out)
        out2 = out.copy()
        out2['data'] = str(self.Rvariables['eset'])
        self.rSend("Eset", out2)
