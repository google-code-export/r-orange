"""
<name>Read Files</name>
<description>Read files</description>
<icon>icons/ReadFile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI
import re
import textwrap

class readFile(OWRpy):
    
    
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setStateVariables(['recentFiles'])
        self.recentFiles=["(none)"]
        self.loadSettings()
        
        
        #set R variable names        
        self.setRvariableNames(['dataframe','filename'])
        
        #signals
        self.inputs = None
        self.outputs = [("data.frame", RvarClasses.RDataFrame)]
        
        #GUI
        box = OWGUI.widgetBox(self.controlArea, "Data File", addSpace = True, orientation=0)
        self.filecombo = QComboBox(box)
        self.filecombo.setMinimumWidth(150)
        box.layout().addWidget(self.filecombo)
        button = OWGUI.button(box, self, '...', callback = self.browseFile, width = 25, disabled=0)
        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.infoc = OWGUI.widgetLabel(box, '')
        self.infod = OWGUI.widgetLabel(box, '')
        
        #self.recentFiles=filter(os.path.exists, self.recentFiles)
        self.setFileList()
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)
        print 'on init :' + str(self.loadingSavedSession)
        if self.loadingSavedSession:
            print 'onloading save :' + str(self.loadingSavedSession)
            self.loadFile()
            
                
    def setFileList(self):
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(os.path.split(file)[1])
        

    def selectFile(self, n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(1)
        if len(self.recentFiles) > 0:
            self.setFileList()
        self.rsession(self.Rvariables['filename'] + ' = "' + self.recentFiles[0].replace('\\', '/') + '"')
        self.loadFile()
    
    def browseFile(self): 
        fn = self.rsession(self.Rvariables['filename'] + ' <- choose.files()')
        if self.rsession('length(' + self.Rvariables['filename'] +')') != 0:
            if fn in self.recentFiles: self.recentFiles.remove(fn)
            self.recentFiles.insert(0, fn)
            self.setFileList()
            self.loadFile()

    def loadFile(self):
        print 'on load :' + str(self.loadingSavedSession)
        if not self.loadingSavedSession:
            print 'read file'
            self.rsession(self.Rvariables['dataframe'] + '= read.delim(' + self.Rvariables['filename'] + ')',True)
        self.updateGUI()
        self.rSend("data.frame", {'data':self.Rvariables['dataframe']})
        
        
    def updateGUI(self):
        col_names = self.rsession('colnames(' + self.Rvariables['dataframe'] + ')')
        self.infoa.setText("data loaded")
        self.infob.setText(self.rsession(self.Rvariables['filename']))
        self.infoc.setText("Number of rows: " + str(self.rsession('nrow(' + self.Rvariables['dataframe'] + ')')))
        col_def = self.rsession('sapply(' + self.Rvariables['dataframe'] + ',class)')
        l = []
        for i,v in col_def.iteritems():
            l.append(i + ': ' + v)
        self.infod.setText("\n".join(l))
        
        
        
        
        
        
        