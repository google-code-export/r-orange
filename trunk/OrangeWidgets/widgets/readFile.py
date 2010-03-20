"""
<name>Read Files</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Data Input</tags>
<RFunctions>utils:read.table</RFunctions>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import redRGUI 

import re
import textwrap

class readFile(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=['Select File']
        self.delim = 0
        self.path = os.path.abspath('/')
        self.userowNamesCombo = ''
        self.useheader = 1
        self.loadSettings()
        
        # self.recentFiles.insert(0, 'Select File')
        
        #set R variable names        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'cm', 'parent'])
        
        #signals
        self.inputs = None
        self.outputs = [("data.frame", RvarClasses.RDataFrame)]
        
        #GUI
        
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        #area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.MinimumExpanding))
        #area.layout().setAlignment(Qt.AlignTop)
        options = redRGUI.widgetBox(area,orientation='vertical')
        options.setMaximumWidth(300)
        # options.setMinimumWidth(300)
        #options.setSizePolicy(QSizePolicy(QSizePolicy.Maximum,QSizePolicy.Maximum))
        options.layout().setAlignment(Qt.AlignTop)
        
        
        #options.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.MinimumExpanding))
        
        box = redRGUI.groupBox(options, label="Load File", 
        addSpace = True, orientation='horizontal')
        

        self.filecombo = redRGUI.comboBox(box, 
        items=self.recentFiles,orientation='horizontal',callback=self.scanNewFile)
        self.filecombo.setCurrentIndex(0)
        # self.filecombo.setMinimumWidth(200)
        # self.filecombo.setMaximumWidth(200)
        button = redRGUI.button(box, label = 'Browse', callback = self.browseFile)
        
        
        self.delimiter = redRGUI.radioButtons(options, label='Column Seperator',
        buttons = ['Tab', 'Space', 'Comma'], setChecked='Tab',callback=self.scanNewFile,
        orientation='horizontal')

        box = redRGUI.groupBox(options, label="Row and Column Names", 
        addSpace = True, orientation ='horizontal')

        
        self.hasHeader = redRGUI.checkBox(box, buttons = ['Use Row Headers'],setChecked=['Use Row Headers'],
        orientation='vertical',callback=self.scanFile)
        
        self.rowNamesCombo = redRGUI.comboBox(box,label='Select Row Names', items=[],
        orientation='vertical',callback=self.scanFile)
        #self.rowNamesCombo.setMaximumWidth(250)        
        
        box = redRGUI.groupBox(options, label="Other Options", 
        addSpace = True, orientation =QGridLayout())
        #split = redRGUI.widgetBox(box,orientation='horizontal')
        self.otherOptions = redRGUI.checkBox(box,buttons=['fill','strip.white','blank.lines.skip',
        'allowEscapes','stringsAsFactors'],
        setChecked = ['blank.lines.skip'],
        toolTips = ['logical. If TRUE then in case the rows have unequal length, blank fields are implicitly added.',
        'logical. Used only when sep has been specified, and allows the stripping of leading and trailing white space from character fields (numeric fields are always stripped). ',
        'logical: if TRUE blank lines in the input are ignored.',
        'logical. Should C-style escapes such as \n be processed or read verbatim (the default)? ',
        'logical: should character vectors be converted to factors?'],
        orientation='vertical')
        box.layout().addWidget(self.otherOptions,1,1)
        
        #self.quote = redRGUI.lineEdit(box,'')
        
        
        holder = redRGUI.widgetBox(options)
        load = redRGUI.button(holder, label = 'Load File', callback = self.loadFile)
        holder.layout().setAlignment(Qt.AlignRight)

        self.FileInfoBox = redRGUI.groupBox(options, label = "File Info", addSpace = True)       
        self.infob = redRGUI.widgetLabel(self.FileInfoBox, label='')
        self.infob.setWordWrap(True)
        self.infoc = redRGUI.widgetLabel(self.FileInfoBox, label='')
        self.FileInfoBox.setHidden(True)
        
        
        self.tableArea = redRGUI.groupBox(area)
        #self.tableArea.setMinimumWidth(350)
        self.tableArea.setHidden(True)
        self.tableArea.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))

        self.scanarea = redRGUI.textEdit(self.tableArea)
        self.scanarea.setLineWrapMode(QTextEdit.NoWrap)
        self.scroll = redRGUI.scrollArea(self.tableArea);
        
        self.columnTypes = redRGUI.widgetBox(self,orientation=QGridLayout(),margin=10);
        self.scroll.setWidget(self.columnTypes)
        #self.columnTypes.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.columnTypes.layout().setSizeConstraint(QLayout.SetMinimumSize)
        self.columnTypes.setSizePolicy(QSizePolicy(QSizePolicy.Preferred ,QSizePolicy.Preferred ))
        self.columnTypes.layout().setAlignment(Qt.AlignTop)
        self.setFileList()

        
    def setFileList(self):
        if self.recentFiles == None: self.recentFiles = []
        
        self.filecombo.clear()
        for file in self.recentFiles:
            self.filecombo.addItem(os.path.basename(file))
    
    def browseFile(self): 
        fn = QFileDialog.getOpenFileName(self, "Open File", self.path,
        "Text file (*.txt *.csv *.tab);; All Files (*.*)")
        print str(fn)
        if fn.isEmpty(): return
        self.path = os.path.split(str(fn))[0]

        if fn in self.recentFiles:
            self.recentFiles.remove(str(fn))
        self.recentFiles.append(str(fn))
        self.filecombo.addItem(os.path.basename(str(fn)))
        self.filecombo.setCurrentIndex(len(self.recentFiles)-1)
        #self.setFileList()
        self.saveSettings()
        self.scanNewFile()

    def scanNewFile(self):
        for i in self.columnTypes.findChildren(QWidget):
            i.setHidden(True)
        redRGUI.widgetBox(self.columnTypes)
        self.columnTypes.adjustSize()
        self.columnTypes.adjustSize()
        self.loadFile(scan=True)
    
    def scanFile(self):
        for i in self.columnTypes.findChildren(QWidget):
            i.setHidden(True)
        redRGUI.widgetBox(self.columnTypes)

        self.columnTypes.adjustSize()
        self.columnTypes.adjustSize()
        self.loadFile(scan=True)
        
        
    def loadFile(self,scan=False):
        if len(self.recentFiles) ==0 or 'Select File' == self.filecombo.currentText(): 
            self.scanarea.clear()
            #self.tableArea.setHidden(True)
            return
        
        self.R(self.Rvariables['filename'] + ' = "' 
        + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"')

        if self.tableArea.isHidden():
            self.tableArea.setHidden(False)
            self.resize(750,500)

        if self.delimiter.getChecked() == 'Tab': #'tab'
            sep = '\t'
        elif self.delimiter.getChecked() == 'Space':
            sep = ' '
        elif self.delimiter.getChecked() == 'Comma':
            sep = ','
        
        if 'Use Row Headers' in self.hasHeader.getChecked():
            header = 'TRUE'
        else:
            header = 'FALSE'
        
        if 'Use Row Headers' in self.hasHeader.getChecked():
            header = 'TRUE'
        else:
            header = 'FALSE'
        
        if scan:
            nrows = '10'
        else:
            nrows = '-1'
        
        if self.rowNamesCombo.currentIndex() not in [0,-1]:
            self.rownames = str(self.rowNamesCombo.currentText())
            param_name = '"' + self.rownames + '"'
        else:
            param_name = 'NULL' 
            self.rownames = 'NULL'
        
        #if len(self.columnTypes.findChildren(QComboBox))
        self.colClasses = []
        labels = self.columnTypes.findChildren(QLabel)
        types = self.columnTypes.findChildren(QComboBox)
        #print labels
        for l,c in zip(labels,types):
            if not c.isHidden():
                self.colClasses.append(str(c.currentText()))

        if len(self.colClasses) > 0:
            ccl = 'c("' + '","'.join(self.colClasses) + '")'
        else:
            ccl = 'NA'
            
        self.R(self.Rvariables['dataframe_org'] + '<- read.table(' + self.Rvariables['filename'] 
        + ', header = '+header
        +', sep = "'+sep
        +'", colClasses = '+ ccl
        #+'", row.names = '+param_name
        +', nrows = '+nrows
        +', fill = T)','setRData',True)

        
        #self.R(self.Rvariables['dataframe_final'] + ' = ' + self.Rvariables['dataframe_org'])
        
        if scan:
            self.updateScan()
        else:
            self.commit()

    def updateScan(self):
        colNames = self.R('colnames(' + self.Rvariables['dataframe_org'] + ')')
        if type(colNames) is str:
            colNames = range(1, int(self.R('length('+self.Rvariables['dataframe_org']+'[1,])')))

        self.rowNamesCombo.update(colNames.insert(0, 'No Row Names'))
        if self.rownames != 'NULL' and self.rownames in colNames:
            self.rowNamesCombo.setCurrentIndex(colNames.index(self.rownames)+1)
            
        self.scanarea.setHidden(False)
        self.scanarea.clear()

        data = self.R('rbind(colnames(' + self.Rvariables['dataframe_org'] 
        + '), as.matrix(' + self.Rvariables['dataframe_org'] + '))')
        # print data
        txt = self.html_table(data)
        self.scanarea.setText(txt)
        
        if(len(self.colClasses) ==0):
            self.colClasses = self.R('as.vector(sapply(' + self.Rvariables['dataframe_org'] + ',class))')
            if type(self.colClasses) is str:
                self.colClasses = [self.colClasses]
        
        for i in self.columnTypes.findChildren(QWidget):
            i.setHidden(True)
        self.columnTypes.adjustSize()
        types = ['factor','numeric','character','integer','logical']
        #k=0
        for k,i,v in zip(range(len(colNames)),colNames,self.colClasses):
            s = redRGUI.comboBox(self.columnTypes,items=types,orientation='horizontal',callback=self.scanFile)
            
            if str(v) in types:
                s.setCurrentIndex(types.index(str(v)))
            else:
                s.addItem(str(v))
                s.setCurrentIndex(s.count()-1)
            s.setMinimumWidth(100)
            q = redRGUI.widgetLabel(self.columnTypes,label=i)
            #q.setText(i)
            self.columnTypes.layout().addWidget(s,k,1)
            self.columnTypes.layout().addWidget(q,k,0)
            self.__setattr__('typeCombo' + str(k), s)
            #k+=1
            
    def updateRowNames(self):
        
        self.R('rownames(' + self.Rvariables['dataframe_final'] + ') <- ' 
        + self.Rvariables['dataframe_org'] + '[,' + str(self.rowNamesCombo.currentIndex()+1)  + ']')
        
        self.R(self.Rvariables['dataframe_final'] + ' <- ' 
        +  self.Rvariables['dataframe_org'] + '[,-' + str(self.rowNamesCombo.currentIndex()+1)  + ']')
        #print self.rowNamesCombo.currentIndex()
        self.updateScan()
        
    def html_table(self,lol):
        s = '<table border="1" cellpadding="3">'
        for sublist in lol:
            s+= '  <tr><td>'
            s+= '    </td><td>'.join(sublist)
            s+= '  </td></tr>'
        s+= '</table>'
        return s
        
    def updateGUI(self):
        dfsummary = self.R(self.Rvariables['dataframe_org'], 'getRSummary')
        
        col_names = dfsummary['colNames']

        self.infob.setText(self.R(self.Rvariables['filename']))
        self.infoc.setText("Number of rows: " + str(len(dfsummary['rowNames'])))
        self.FileInfoBox.setHidden(False)
    def commit(self, kill = True):
        self.R(self.Rvariables['cm'] + '<- data.frame(row.names = rownames('
        +self.Rvariables['dataframe_org']+'))')
        self.updateGUI()
        sendData = {'data':self.Rvariables['dataframe_org'], 
        'parent':self.Rvariables['dataframe_org'], 'cm':self.Rvariables['cm']}
        self.rSend("data.frame", sendData)
        
    def compileReport(self):
        self.reportSettings("File Name", [(self.Rvariables['filename'], self.R(self.Rvariables['filename']))])
        
        self.reportRaw(self.fileInfo.toHtml())
        #self.finishReport()
        
    def sendReport(self):
        self.compileReport()
        self.showReport()
        
        
    
        