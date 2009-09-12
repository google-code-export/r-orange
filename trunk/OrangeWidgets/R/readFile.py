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
    
    settingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=["(none)"]
        self.delim = 0
        self.userowNames = ''
        self.useheader = 1
        self.loadSettings()
        
        
        #set R variable names        
        self.setRvariableNames(['dataframe','filename'])
        
        #signals
        self.inputs = None
        self.outputs = [("data.frame", RvarClasses.RDataFrame)]
        
        #GUI
        box = OWGUI.widgetBox(self.controlArea, "Data File", addSpace = True, orientation=0)
        self.filecombo = QComboBox(box)
        button = OWGUI.button(box, self, '...', callback = self.browseFile, width = 25, disabled=0)
        self.filecombo.setMinimumWidth(150)
        box.layout().addWidget(self.filecombo)
        box = OWGUI.widgetBox(self.controlArea, "File Options", addSpace = True, orientation = 0)
        OWGUI.comboBox(box, self, 'delim', items = ['Tab', 'Space', 'Comma'], orientation = 0)
        OWGUI.comboBox(box, self, 'useheader', items = ['No Header', 'Header'])
        OWGUI.lineEdit(box, self, 'userowNames', 'Rowname Column:')
        OWGUI.button(box, self, 'Scan', callback = self.scanfile, width = 30, disabled = 0)
        OWGUI.button(box, self, 'Load File', callback = self.loadFile)
        box = OWGUI.widgetBox(self.controlArea, "Info", addSpace = True)
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')
        self.infoc = OWGUI.widgetLabel(box, '')
        self.infod = OWGUI.listBox(box, self)
        self.infod.hide()
        
        #self.recentFiles=filter(os.path.exists, self.recentFiles)
        self.setFileList()
        self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)
        #print 'on init :' + str(self.loadingSavedSession)
        
        self.scanarea = QTextEdit()
        self.controlArea.layout().addWidget(self.scanarea)
        
        
        # try:
            # varexists = self.R('exists("'+self.Rvariables['dataframe']+'")')
            # var2exists = self.R('exists("'+self.Rvariables['filename']+'")')
            # if varexists:
                # self.sendMe(kill = False)
                # self.infoa.setText("Data loaded from previous session.")
                # self.infob.setText("Check data with data viewer.")
        # except:
            # pass
        # if self.loadingSavedSession:
            # print 'onloading save :' + str(self.loadingSavedSession)
            # self.loadFile()
            
    def onLoadSavedSession(self):
        if self.R('exists("'+self.Rvariables['dataframe']+'")'):
            self.updateGUI()
            self.sendMe()
        
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
        self.R(self.Rvariables['filename'] + ' = "' + self.recentFiles[0].replace('\\', '/') + '"')
        #self.loadFile()
    
    def browseFile(self): 
        fn = self.R(self.Rvariables['filename'] + ' <- choose.files()')
        if self.R('length(' + self.Rvariables['filename'] +')') != 0:
            if fn in self.recentFiles: self.recentFiles.remove(fn)
            self.recentFiles.insert(0, fn)
            self.setFileList()
        #    self.loadFile()

    def scanfile(self):
        self.scanarea.clear()
        if self.delim == 0: #'tab'
            sep = '\t'
        elif self.delim == 1:
            sep = ' '
        elif self.delim == 2:
            sep = ','
        self.R('txt<-capture.output(read.table('+self.Rvariables['filename']+', nrows = 5, sep = "'+sep+'", fill = T))')
        pasted = self.rsession('paste(txt, collapse = " \n")')
        self.scanarea.insertHtml('<br><pre>'+pasted+'<\pre><br> If this table does not make sense, you may want to change the seperator.')
        
            
    def loadFile(self):
        #print 'on load :' + str(self.loadingSavedSession)
        #if not self.loadingSavedSession:
        print 'read file'
        if self.delim == 0: #'tab'
            sep = '\t'
        elif self.delim == 1:
            sep = ' '
        elif self.delim == 2:
            sep = ','
        if self.useheader == 0:
            header = 'FALSE'
        elif self.useheader == 1:
            header = 'TRUE'
        if self.userowNames != '':
            rownames = self.userowNames
        else:
            rownames = 'NULL' #force numbering
            self.R(self.Rvariables['dataframe'] + '<- read.table(' + self.Rvariables['filename'] + ', header = '+header+', sep = "'+sep+'", row.names = '+rownames+', fill = T)','setRData',True)
        self.updateGUI()
        self.sendMe()
        
        
        
    def updateGUI(self):
        dfsummary = self.R(self.Rvariables['dataframe'], 'getRSummary')
        
        col_names = dfsummary['colNames']
        self.infoa.setText("data loaded")
        self.infob.setText(self.R(self.Rvariables['filename']))
        self.infoc.setText("Number of rows: " + str(len(dfsummary['rowNames'])))
        col_def = self.R('sapply(' + self.Rvariables['dataframe'] + ',class)')
        self.infod.show()
        self.infod.clear()
        for i,v in col_def.iteritems():
            self.infod.addItem(str(i + ': ' + v))
        
    def sendMe(self, kill = True):
        sendData = {'data':self.Rvariables['dataframe']}
        self.rSend("data.frame", sendData)
        
        
        
        
        