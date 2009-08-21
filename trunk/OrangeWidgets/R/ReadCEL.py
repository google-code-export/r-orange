"""
<name>Read CEL Files</name>
<description>Allows the user to pick CEL files either individually or through a .txt file and outputs the eSet as an R.object</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI

class ReadCEL(OWRpy):
    
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "ReadCEL", wantMainArea = 0, resizingEnabled = 1)
        self.setStateVariables(['recentFiles'])
        #default values        
        self.recentFiles = ['(none)']
        self.loadSettings()
        
        #required librarys
        self.require_librarys(['affy'])
        
        
        #set R variable names
        self.setRvariableNames(['eset','folder'])
        
        #signals
        self.inputs = None 
        self.outputs = [("Affybatch Expression Matrix", RvarClasses.RDataFrame)]


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

        
        if self.rsession('exists("' + self.Rvariables['loadSavedSession'] + '")'):
            self.loadSavedSession = True
            self.procesS()
        
        

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
        self.procesS()
        
        
    def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
        folder = self.rsession(self.Rvariables['folder'] +'<-choose.dir()')
        if not self.rsession('is.na(' + self.Rvariables['folder'] +')'):
            if folder in self.recentFiles: self.recentFiles.remove(folder)
            self.recentFiles.insert(0, folder)
            self.setFileList()
            self.procesS()
        
    def procesS(self):
        self.infoa.setText("Your data is processing")
        if not self.loadSavedSession:
            self.rsession(self.Rvariables['eset']+'<-ReadAffy(celfile.path='+self.Rvariables['folder']+')',True)
        self.infoa.setText("Your data has been processed.")
        self.out = {'data':'exprs('+self.Rvariables['eset']+')', 'eset':self.Rvariables['eset']}
        self.rSend("Affybatch Expression Matrix", self.out)

        
    
