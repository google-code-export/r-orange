"""
<name>Read Files</name>
<description>Read files</description>
<icon>icons/readcel.png</icons>
<priority>10</priority>
"""

from OWRpy import *
from OWWidget import *
import OWGUI
import textwrap

class readFile(OWWidget,OWRpy):
    settingsList = ['recentFiles', 'variable_suffix']
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        OWRpy.__init__(self)
        
        self.recentFiles=["(none)"]
        self.loadSettings()
        self.inputs = None
        self.outputs = [("data.frame", orange.Variable),("Examples", ExampleTable)]
        self.Rdataframe = 'data' + self.variable_suffix
        self.Rfilename = 'filename' + self.variable_suffix
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
        self.recentFiles=filter(os.path.exists, self.recentFiles)
        self.setFileList()
        if r.exists(self.Rdataframe):
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
        self.filecombo.addItem("Browse documentation data sets...")

    def selectFile(self, n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)
        elif n:
            self.browseFile(1)

        if len(self.recentFiles) > 0:
            self.setFileList()
    
    
    def browseFile(self): #should open a dialog to choose a file that will be parsed to set the wd
        #something to handle the conversion
        
        fn = r(self.Rfilename + ' <- choose.files()')
        if r('length(' + self.Rfilename +')') != 0:
            self.recentFiles.insert(0, fn)
            self.setFileList()
            self.loadFile(self.Rfilename)

    def loadFile(self,fn=None):
        print 'asdfasdf'
        if fn != None:
            data = r(self.Rdataframe + '= read.delim(' + self.Rfilename + ')')
        else:
            data = r(self.Rdataframe)
        col_names = r('colnames(' + self.Rdataframe + ')')
        self.infoa.setText("data loaded")
        self.infob.setText(r(self.Rfilename))
        self.infoc.setText("Number of rows: " + str(r('nrow(data' + self.variable_suffix + ')')))
        col_def = r.sapply(data,'class')
        l = []
        for i,v in col_def.iteritems():
            l.append(i + ': ' + v)
        self.infod.setText("\n".join(l))

        self.send("data.frame", 'data' + self.variable_suffix)
        self.send("Examples", self.convertDataframeToExampleTable(self.Rdataframe))
    
        
        
        
        
        