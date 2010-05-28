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
import signals, globalData


class ReadCEL(OWRpy):
    globalSettingsList = ['filecombo', 'recentFiles','path']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "ReadCEL", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['recentFiles'])
        #default values        
        # self.recentFiles = ['Select Directory']
        self.path = os.path.abspath('/')
        self.methodcombo = 0
        self.saveSettingsList.append(['recentFiles', 'path', 'methodcombo'])
        
        #set R variable names
        self.setRvariableNames(['affyBatch','folder', 'cm'])
        #signals
        self.inputs = None 
        self.outputs = [("affyBatch", signals.affy.RAffyBatch)]
        
        #GUI
        box = redRGUI.groupBox(self.controlArea, "Select Folder",orientation='horizontal')
        #sizePolicy=QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed))
        
        self.filecombo = redRGUI.fileNamesComboBox(box)
        #self.filecombo.setCurrentIndex(0)
        button = redRGUI.button(box, 'Browse', callback = self.browseFile)
        
        self.numArrays = redRGUI.radioButtons(self.controlArea, label = 'Number of arrays', 
        buttons = ['Less than 40', 'More than 40'],setChecked='Less than 40', orientation='horizontal')

        button2 = redRGUI.button(self.bottomAreaRight, 'Process Folder', callback = self.process)
        
        # self.setFileList()
        
    # def setFileList(self):
        # if self.recentFiles == None: self.recentFiles = ['Select Directory']
        
        # self.filecombo.clear()
        # for file in self.recentFiles:
            # self.filecombo.addItem(os.path.basename(file))

        # self.filecombo.setCurrentIndex(data['current'])
        # self.scanFile()
    
    def browseFile(self): 
        fn = QFileDialog.getExistingDirectory(self, "CEL Directory", self.path)
        
        #print str(fn)
        if fn.isEmpty(): return
        self.filecombo.addFile(fn)
        self.saveGlobalSettings()

        # self.path = os.path.split(str(fn))[0]
        # if fn in self.recentFiles:
            # self.recentFiles.remove(str(fn))
        # self.recentFiles.append(str(fn))
        # self.filecombo.addItem(os.path.basename(str(fn)))
        # self.filecombo.setCurrentIndex(len(self.recentFiles)-1)
        
        # self.saveGlobalSettings()
        
    def process(self):
        dir = self.filecombo.getCurrentFile()
        if not dir:
            return
        self.status.setText("Your data is processing")
        #required librarys
        if not self.require_librarys(['affy']):
            self.status.setText('R Libraries Not Loaded.')
            return
        if self.numArrays.getChecked() == 'Less than 40':
            self.R(self.Rvariables['affyBatch']+'<-ReadAffy(celfile.path="'+dir+'")','setRData',True)
            self.status.setText("Your data has been processed with ReadAffy.")
        else:
            self.status.setText("This may take several minutes")
            self.R(self.Rvariables['affyBatch']+'<-justRMA(celfile.path='+self.Rvariables['folder']+')','setRData',True)
            self.status.setText("Data preprocessed with justRMA.")
        self.R(self.Rvariables['cm']+'<-list()') # in this case the cm should be the colnames, not the rownames as is usual
        self.sendMe()
        
    
    def sendMe(self):
        chipType = self.R('annotation('+self.Rvariables['affyBatch']+')')
        globalData.setGlobalData(self,'chipType',chipType,description='Chip Type')
        out2 = signals.affy.RAffyBatch(data = str(self.Rvariables['affyBatch']))
        self.rSend("affyBatch", out2)
