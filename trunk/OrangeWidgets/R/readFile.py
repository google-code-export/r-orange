"""
<name>Read Files</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Data Entry</tags>
<icon>icons/ReadFile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import OWGUI
import redRGUI 

import re
import textwrap

class readFile(OWRpy):
    
    globalSettingsList = ['recentFiles']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=[]
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
        box = redRGUI.groupBox(self.controlArea, label="Data File", addSpace = True, orientation='horizontal')
        
        self.filecombo = redRGUI.comboBox(box,items=self.recentFiles)
        
        button = redRGUI.button(box, self, 'Browse', callback = self.browseFile, disabled=0)
        self.filecombo.setMinimumWidth(150)
        box.layout().addWidget(self.filecombo)
        redRGUI.button(box, self, 'Report', callback = self.sendReport, disabled = 0)
        
        
        box = redRGUI.groupBox(self.controlArea, label="File Options", addSpace = True, orientation ='horizontal')
        
        self.delimiter = redRGUI.comboBox(box, items = ['Tab', 'Space', 'Comma'])
        self.hasHeader = redRGUI.checkBox(box, buttons = ['header'])
        
        self.userowNames = redRGUI.lineEdit(box, label = 'Rowname Column:')
        redRGUI.button(box, self, 'Scan', callback = self.scanfile, width = 30, disabled = 0)
        redRGUI.button(box, self, 'Load File', callback = self.loadFile)
        box = redRGUI.groupBox(self.controlArea, "Info", addSpace = True)
        self.infoa = redRGUI.widgetLabel(box, 'No data loaded.')
        self.infob = redRGUI.widgetLabel(box, '')
        self.infoc = redRGUI.widgetLabel(box, '')
        self.fileInfo = redRGUI.textEdit(box)
        self.fileInfo.setHidden(True)
        self.scanarea = redRGUI.textEdit(self.controlArea)
        
        #self.recentFiles=filter(os.path.exists, self.recentFiles)
        self.setFileList()
        # self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)
        #print 'on init :' + str(self.loadingSavedSession)
        
        #self.controlArea.layout().addWidget(self.scanarea)
        
    def setFileList(self):
        if self.recentFiles == None: self.recentFiles = []
        self.filecombo.clear()
        # if not self.recentFiles:
            # self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            # if file == "(none)":
                # self.filecombo.addItem("(none)")
            # else:
            self.filecombo.addItem(os.path.split(file)[1])
        

    # def selectFile(self, n):
        # if n < len(self.recentFiles) :
            # name = self.recentFiles[n]
            # self.recentFiles.remove(name)
            # self.recentFiles.insert(0, name)

        # if len(self.recentFiles) > 0:
            # self.setFileList()
        # self.R(self.Rvariables['filename'] + ' = "' + self.recentFiles[0].replace('\\', '/') + '"')
        # self.scanfile()
    
    def browseFile(self): 
        fn = self.R(self.Rvariables['filename'] + ' <- choose.files()')
        if self.R('length(' + self.Rvariables['filename'] +')') != 0:
            if fn in self.recentFiles:
                self.recentFiles.remove(fn)
            self.recentFiles.insert(0, fn)
            self.setFileList()
            self.saveSettings()

    def scanfile(self):
        if len(self.recentFiles) ==0: return
        self.scanarea.clear()
        print self.Rvariables['filename'] + ' = "' + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"'
        self.R(self.Rvariables['filename'] + ' = "' + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"')
        if self.R('length(' + self.Rvariables['filename'] +')') == 0: self.browseFile
        if self.R('length(' + self.Rvariables['filename'] +')') == 0: return
        if self.delimiter.currentText() == 'Tab': #'tab'
            sep = '\t'
        elif self.delimiter.currentText() == 'Space':
            sep = ' '
        elif self.delimiter.currentText() == 'Comma':
            sep = ','
        self.R('txt<-capture.output(read.table('+self.Rvariables['filename']+', nrows = 5, sep = "'+sep+'", fill = T))')
        pasted = self.R('paste(txt, collapse = " \n")')
        self.scanarea.setText('If this table does not make sense, you may want to change the seperator.<br><pre>'+pasted+'<\pre>')
        
            
    def loadFile(self):
        if len(self.recentFiles) ==0: return
        self.R(self.Rvariables['filename'] + ' = "' + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"')

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
        if self.userowNames.text() != '':
            rownames = str(self.userowNames.text())
        else:
            rownames = 'NULL' #force numbering
        self.R(self.Rvariables['dataframe'] + '<- read.table(' + self.Rvariables['filename'] + ', header = '+header+', sep = "'+sep+'", row.names = '+rownames+', fill = T)','setRData',True)
        self.updateGUI()
        self.sendMe()
        
    def html_table(self,lol):
        s = '<table>'
        for sublist in lol:
            s+= '  <tr><td>'
            s+= '    </td><td>'.join(sublist)
            s+= '  </td></tr>'
        s+= '</table>'
        return s
        
    def updateGUI(self):
        dfsummary = self.R(self.Rvariables['dataframe'], 'getRSummary')
        
        col_names = dfsummary['colNames']
        self.infoa.setText("data loaded")
        self.infob.setText(self.R(self.Rvariables['filename']))
        self.infoc.setText("Number of rows: " + str(len(dfsummary['rowNames'])))
        col_def = self.R('sapply(' + self.Rvariables['dataframe'] + ',class)')
        s = [['Column Name','Column Type']]
        for i,v in col_def.iteritems():
            s.append([i,v])  
            #self.fileInfo.addItem(str(i + ': ' + v))
        self.fileInfo.setText('File Info:' + self.html_table(s))
        self.fileInfo.setHidden(False)
    def sendMe(self, kill = True):
        sendData = {'data':self.Rvariables['dataframe']}
        self.rSend("data.frame", sendData)
        
    def compileReport(self):
        self.reportSettings("File Name", [(self.Rvariables['filename'], self.R(self.Rvariables['filename']))])
        
        self.reportRaw(self.fileInfo.toHtml())
        #self.finishReport()
        
    def sendReport(self):
        self.compileReport()
        self.showReport()
        
        
    
        