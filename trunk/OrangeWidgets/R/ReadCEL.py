"""
<name>Read CEL Files</name>
<description>Allows the user to pick CEL files either individually or through a .txt file and outputs the eSet as an R.object</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

from OWWidget import *
import OWGUI
import orngIO
from OWRpy import *


class ReadCEL( OWRpy):
    settingsList = ['variable_suffix','recentFiles']
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        OWRpy.__init__(self)

        #default values        
        self.recentFiles = ['(none)']
        self.loadSettings()
        
        #required librarys
        self.require_librarys(['affy'])
        
        
        #set R variable names
        self.Rvariables = self.setRvariableNames(['eset','folder'])
        
        #signals
        self.inputs = None 
        self.outputs = [("Affybatch Expression Matrix", orange.Variable)]


        #GUI
        box = OWGUI.widgetBox(self.controlArea, "Select Folder", addSpace = True, orientation=0)
        self.filecombo = QComboBox(box)
        self.filecombo.setMinimumWidth(150)
        box.layout().addWidget(self.filecombo)
        button = OWGUI.button(box, self, '...', callback = self.browseFile, width = 25, disabled=0)
        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.infoc = OWGUI.widgetLabel(box, '')
        self.infod = OWGUI.widgetLabel(box, '')
        self.setFileList()
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)

        
        #initialize previous sessions
        if self.rsession('exists("' + self.Rvariables['eset'] + '")'):
            self.procesS(False)

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
        self.rsession(self.Rvariables['folder'] + ' = "' + self.recentFiles[0].replace('\\', '\\\\') + '"')
        self.procesS(True)
        
        
    def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
        folder = self.rsession(self.Rvariables['folder'] +'<-choose.dir()')
        if self.rsession('length(' + self.Rvariables['folder'] +')') != 0:
            if folder in self.recentFiles: self.recentFiles.remove(folder)
            self.recentFiles.insert(0, folder)
            self.setFileList()
            self.procesS(True)
        
    def procesS(self,load):
        
        self.infoa.setText("Your data is processing")
        if load:
            self.rsession(self.Rvariables['eset']+'<-ReadAffy(celfile.path='+self.Rvariables['folder']+')',True)
        
        self.out = {'data':'exprs('+self.Rvariables['eset']+')', 'eset':self.Rvariables['eset']}
        self.infoa.setText("Your data has been processed.")
    
        self.send("Affybatch Expression Matrix", self.out)