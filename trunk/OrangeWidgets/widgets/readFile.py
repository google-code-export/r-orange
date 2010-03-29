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
import cPickle
import pickle
class readFile(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=['Select File']
        self.delim = 0
        self.path = os.path.abspath('/')
        self.colClasses = []
        self.colNames = []
        self.dataTypes = []
        self.useheader = 1
        self.loadSettings()
        
        #set R variable names        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'cm', 'parent'])
        
        #signals
        self.inputs = None
        self.outputs = [("data.frame", RvarClasses.RDataFrame)]
        
        #GUI
        
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.MinimumExpanding))
        area.layout().setAlignment(Qt.AlignTop)
        options = redRGUI.widgetBox(area,orientation='vertical')
        options.setMaximumWidth(300)
        # options.setMinimumWidth(300)
        #options.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
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

        
        self.hasHeader = redRGUI.checkBox(box, buttons = ['Column Headers'],setChecked=['Column Headers'],toolTips=['a logical value indicating whether the file contains the names of the variables as its first line. If missing, the value is determined from the file format: header is set to TRUE if and only if the first row contains one fewer field than the number of columns.'],
        orientation='vertical',callback=self.scanNewFile)
        
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
        orientation='vertical',callback=self.scanFile)
        box.layout().addWidget(self.otherOptions,1,1)
        
        #self.quote = redRGUI.lineEdit(box,'')
        
        
        holder = redRGUI.widgetBox(options,orientation='horizontal')
        rescan = redRGUI.button(holder, label = 'Rescan File', callback = self.scanNewFile)
        load = redRGUI.button(holder, label = 'Load File', callback = self.loadFile)
        holder.layout().setAlignment(Qt.AlignRight)

        self.FileInfoBox = redRGUI.groupBox(options, label = "File Info", addSpace = True)       
        self.infob = redRGUI.widgetLabel(self.FileInfoBox, label='')
        self.infob.setWordWrap(True)
        self.infoc = redRGUI.widgetLabel(self.FileInfoBox, label='')
        self.FileInfoBox.setHidden(True)
        
        
        self.tableArea = redRGUI.groupBox(area)
        self.tableArea.setMinimumWidth(200)
        #self.tableArea.setHidden(True)
        self.tableArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

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

       
    def loadDynamicData(self,settings):
        print 'loadDynamicData readfile'
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(settings['dataTypes'])
        if 'dataTypes' not in settings.keys():
            return
        for k,l,c in zip(range(len(self.colNames)),self.colNames,settings['dataTypes']['list']):
            s = redRGUI.comboBox(self.columnTypes,items=[],orientation='horizontal',callback=self.updateColClasses)
            s.loadSettings(c['redRGUIObject'])
            s.setMinimumWidth(100)
            q = redRGUI.widgetLabel(self.columnTypes,label=l)
            self.columnTypes.layout().addWidget(s,k,1)
            self.columnTypes.layout().addWidget(q,k,0)
            self.dataTypes.append(s)

        
        
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
          
        self.rowNamesCombo.clear()
        self.colClasses = []
        self.colNames = []
        self.dataTypes = []
        self.loadFile(scan=True)
    
    def updateColClasses(self):

        self.colClasses = []
        for i in self.dataTypes:
            self.colClasses.append(str(i.currentText()))
        # print 'colClasses' , self.colClasses
        self.loadFile(scan=True)
    def scanFile(self):
        self.loadFile(scan=True)
        
        
    def loadFile(self,scan=False):
        if len(self.recentFiles) ==0 or self.filecombo.currentIndex() == 0: 
            self.scanarea.clear()
            return
        
        self.R(self.Rvariables['filename'] + ' = "' 
        + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"') # should protext if R can't find this file


        if self.delimiter.getChecked() == 'Tab': #'tab'
            sep = '\t'
        elif self.delimiter.getChecked() == 'Space':
            sep = ' '
        elif self.delimiter.getChecked() == 'Comma':
            sep = ','
        otherOptions = ''
        for i in self.otherOptions.getChecked():
            otherOptions += str(i) + '=TRUE,' 
        
        if 'Column Headers' in self.hasHeader.getChecked():
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
        
        
        if len(self.colClasses) > 0:
            ccl = 'c("' + '","'.join(self.colClasses) + '")'
        else:
            ccl = 'NA'
        try:
            self.R(self.Rvariables['dataframe_org'] + '<- read.table(' + self.Rvariables['filename'] 
            + ', header = '+header
            +', sep = "'+sep
            +'", colClasses = '+ ccl
            +', row.names = '+param_name
            +', nrows = '+nrows
            +',' + otherOptions + ')','setRData',True)
        except:
            self.rowNamesCombo.setCurrentIndex(0)
            self.updateScan()
            return
        
        
        if scan:
            self.updateScan()
        else:
            self.commit()

    def updateScan(self):
        if self.rowNamesCombo.count() == 0:
            self.colNames = self.R('colnames(' + self.Rvariables['dataframe_org'] + ')')
            if type(self.colNames) is str:
                #colNames = [str(c) for c in range(1, int(self.R('length('+self.Rvariables['dataframe_org']+'[1,])')))]
                self.colNames = [self.colNames]
            self.rowNamesCombo.clear()
            self.rowNamesCombo.addItem('NULL')
            self.rowNamesCombo.addItems(self.colNames)

        self.scanarea.clear()

        data = self.R('rbind(colnames(' + self.Rvariables['dataframe_org'] 
        + '), as.matrix(' + self.Rvariables['dataframe_org'] + '))')
        # print data
        txt = self.html_table(data)
        self.scanarea.setText(txt)
        
        if len(self.colClasses) ==0:
            self.colClasses = self.R('as.vector(sapply(' + self.Rvariables['dataframe_org'] + ',class))')
            if type(self.colClasses) is str:
                self.colClasses = [self.colClasses]
        
        if len(self.dataTypes) ==0:
            types = ['factor','numeric','character','integer','logical']
            self.dataTypes = []
            
            for k,i,v in zip(range(len(self.colNames)),self.colNames,self.colClasses):
                s = redRGUI.comboBox(self.columnTypes,items=types,orientation='horizontal',callback=self.updateColClasses)
                
                # print k,i,str(v)
                if str(v) in types:
                    s.setCurrentIndex(types.index(str(v)))
                else:
                    s.addItem(str(v))
                    s.setCurrentIndex(s.count()-1)
                s.setMinimumWidth(100)
                q = redRGUI.widgetLabel(self.columnTypes,label=i)
                self.columnTypes.layout().addWidget(s,k,1)
                self.columnTypes.layout().addWidget(q,k,0)
                self.dataTypes.append(s)
            
    
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
        self.rowNamesCombo.update(col_names)
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
        
        
    
        