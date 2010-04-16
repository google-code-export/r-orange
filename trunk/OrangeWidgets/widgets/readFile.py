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
import types
class readFile(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=['Select File']
        self.delim = 0
        self.path = os.path.abspath('/')
        self.colClasses = []
        self.myColClasses = []
        self.colNames = []
        self.dataTypes = []
        self.useheader = 1
        self.loadSettings()
        #set R variable names        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'cm', 'parent'])
        
        # raise Exception('asdf')
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
        options.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        area.layout().setAlignment(options,Qt.AlignTop)
        
        
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
        addSpace = True, orientation ='vertical')
        # box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        split = redRGUI.widgetBox(box,orientation='horizontal')
        # split.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.otherOptions = redRGUI.checkBox(split,buttons=['fill','strip.white','blank.lines.skip',
        'allowEscapes','stringsAsFactors'],
        setChecked = ['blank.lines.skip'],
        toolTips = ['logical. If TRUE then in case the rows have unequal length, blank fields are implicitly added.',
        'logical. Used only when sep has been specified, and allows the stripping of leading and trailing white space from character fields (numeric fields are always stripped). ',
        'logical: if TRUE blank lines in the input are ignored.',
        'logical. Should C-style escapes such as \n be processed or read verbatim (the default)? ',
        'logical: should character vectors be converted to factors?'],
        orientation='vertical',callback=self.scanFile)
        # box.layout().addWidget(self.otherOptions,1,1)
        box2 = redRGUI.widgetBox(split,orientation='vertical')
        #box2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        split.layout().setAlignment(box2,Qt.AlignTop)
        self.quote = redRGUI.lineEdit(box2,text='"',label='Quote:', width=50, orientation='horizontal')
        # self.quote.setMaximumWidth(50)
        # self.quote.setMinimumWidth(50)
        
        self.numLinesScan = redRGUI.lineEdit(box2,text='10',label='# Lines to Scan:',width=50,orientation='horizontal')
        # self.numLinesScan.setMaximumWidth(50)
        # self.numLinesScan.setMinimumWidth(50)

        self.numLinesSkip = redRGUI.lineEdit(box2,text='0',label='# Lines to Skip:',width=50,orientation='horizontal')
        # self.numLinesSkip.setMaximumWidth(50)
        # self.numLinesSkip.setMinimumWidth(50)


        
        # box.layout().addWidget(self.otherOptions,2,1)
        
        
        
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
        self.scanarea.setReadOnly(True)
        self.scroll = redRGUI.scrollArea(self.tableArea);
        
        self.columnTypes = redRGUI.widgetBox(self,orientation=QGridLayout(),margin=10);
        self.scroll.setWidget(self.columnTypes)
        #self.columnTypes.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.columnTypes.layout().setSizeConstraint(QLayout.SetMinimumSize)
        self.columnTypes.setSizePolicy(QSizePolicy(QSizePolicy.Minimum ,QSizePolicy.Preferred ))
        self.columnTypes.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setFileList()

    def loadCustomSettings(self,settings):
        print 'loadCustomSettings readfile'
        for i in range(len(self.myColClasses)):
            s = redRGUI.comboBox(self.columnTypes, items = ['factor','numeric','character','integer','logical'], orientation = 'horizontal', callback = self.updateColClasses)
            index = s.findText(self.myColClasses[i])
            if index != -1:
                s.setCurrentIndex(index)
            s.setEnabled(False)
            q = redRGUI.widgetLabel(self.columnTypes,label=self.colNames[i])
            self.columnTypes.layout().addWidget(s, i, 1)
            self.columnTypes.layout().addWidget(q, i, 0)
        
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
        self.saveGlobalSettings()
        self.scanNewFile()

    def scanNewFile(self):
        self.removeInformation()
        self.removeWarning()

        for i in self.columnTypes.findChildren(QWidget):
            i.setHidden(True)
          
        self.rowNamesCombo.clear()
        self.colClasses = []
        self.colNames = []
        self.dataTypes = []
        self.loadFile(scan=True)
    
    def updateColClasses(self):

        self.myColClasses = []
        for i in self.dataTypes:
            self.myColClasses.append(str(i[1].currentText()))
        # print 'colClasses' , self.colClasses
        self.loadFile(scan=True)
    def scanFile(self):
        self.loadFile(scan=True)

        
    def loadFile(self,scan=False):
        
        if len(self.recentFiles) ==0 or self.filecombo.currentIndex() == 0:
            self.scanarea.clear()
            return
        if not os.path.isfile(self.recentFiles[self.filecombo.currentIndex()]):
            del self.recentFiles[self.filecombo.currentIndex()]
            self.setFileList()
            QMessageBox.information(self,'Error', "File does not exist.", 
            QMessageBox.Ok + QMessageBox.Default)

            return
            
        self.R(self.Rvariables['filename'] + ' = "' 
        + self.recentFiles[self.filecombo.currentIndex()].replace('\\', '/') + '"') # should protext if R can't find this file
        # if os.path.basename(self.recentFiles[self.filecombo.currentIndex()]).split('.')[1] == 'tab':
            # self.delimiter.setChecked('Tab')
        # elif os.path.basename(self.recentFiles[self.filecombo.currentIndex()]).split('.')[1] == 'csv':
            # self.delimiter.setChecked('Comma')

        if self.delimiter.getChecked() == 'Tab': #'tab'
            sep = '\\t'
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
            nrows = str(self.numLinesScan.text())
        else:
            nrows = '-1'
        
        
        if self.rowNamesCombo.currentIndex() not in [0,-1]:
            self.rownames = str(self.rowNamesCombo.currentText())
            param_name = '"' + self.rownames + '"'
        else:
            param_name = 'NULL' 
            self.rownames = 'NULL'
        
        cls = []
        for i,new,old in zip(xrange(len(self.myColClasses)),self.myColClasses,self.colClasses):
            if new != old:
                cls.append(self.dataTypes[i][0] + '="' + new + '"')
        
        if len(cls) > 0:
            ccl = 'c(' + ','.join(cls) + ')'
        else:
            ccl = 'NA'
        try:
        # +', quote='+self.quote.text()
            RStr = self.Rvariables['dataframe_org'] + '<- read.table(' + self.Rvariables['filename'] + ', header = '+header +', sep = "'+sep +'",quote="' + str(self.quote.text()).replace('"','\\"') + '", colClasses = '+ ccl +', row.names = '+param_name +',skip='+str(self.numLinesSkip.text())+', nrows = '+nrows +',' + otherOptions + ')'
            # print RStr
            self.R(RStr, processingNotice=True)
        except:
            # print sys.exc_info() 
            # print RStr
            self.rowNamesCombo.setCurrentIndex(0)
            self.updateScan()
            return
        
        if scan:
            self.updateScan()
        else:
            self.commit()

    def updateScan(self):
        if self.rowNamesCombo.count() == 0:
            self.colNames = self.R('colnames(' + self.Rvariables['dataframe_org'] + ')',wantType='list')
            self.rowNamesCombo.clear()
            self.rowNamesCombo.addItem('NULL')
            self.rowNamesCombo.addItems(self.colNames)
        self.scanarea.clear()
        # print self.R(self.Rvariables['dataframe_org'])
        # return
        
        data = self.R('rbind(colnames(' + self.Rvariables['dataframe_org'] 
        + '), as.matrix(' + self.Rvariables['dataframe_org'] + '))',wantType='list')
        rownames = self.R('rownames(' + self.Rvariables['dataframe_org'] + ')',wantType='list')
        #print data
        txt = self.html_table(data,rownames)
        # print 'paste(capture.output(' + self.Rvariables['dataframe_org'] +'),collapse="\n")'
        # try:
            #txt = self.R('paste(capture.output(' + self.Rvariables['dataframe_org'] +'),collapse="\n")',processingNotice=True, showException=False)
        # txt = self.R(self.Rvariables['dataframe_org'],processingNotice=True, showException=False)
        
        self.scanarea.setText(txt)
        # except:
            # QMessageBox.information(self,'R Error', "Try selected a different Column Seperator.", 
            # QMessageBox.Ok + QMessageBox.Default)
            # return
            
        
        
        if len(self.colClasses) ==0:
            self.colClasses = self.R('as.vector(sapply(' + self.Rvariables['dataframe_org'] + ',class))',wantType='list')
            self.myColClasses = self.colClasses
        
        if len(self.dataTypes) ==0:
            types = ['factor','numeric','character','integer','logical']
            self.dataTypes = []
            
            for k,i,v in zip(range(len(self.colNames)),self.colNames,self.myColClasses):
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
                self.dataTypes.append([i,s])
            
    
    def updateRowNames(self):
        
        self.R('rownames(' + self.Rvariables['dataframe_final'] + ') <- ' 
        + self.Rvariables['dataframe_org'] + '[,' + str(self.rowNamesCombo.currentIndex()+1)  + ']')
        
        self.R(self.Rvariables['dataframe_final'] + ' <- ' 
        +  self.Rvariables['dataframe_org'] + '[,-' + str(self.rowNamesCombo.currentIndex()+1)  + ']')
        #print self.rowNamesCombo.currentIndex()
        self.updateScan()
        
    def html_table(self,lol,rownames):
        s = '<table border="1" cellpadding="3">'
        s+= '  <tr><td>Rownames</td><td><b>'
        s+= '    </b></td><td><b>'.join(lol[0])
        s+= '  </b></td></tr>'
        
        for row, sublist in zip(rownames,lol[1:]):
            s+= '  <tr><td><b>' +row + '</b></td><td>'
            s+= '    </td><td>'.join(sublist)
            s+= '  </td></tr>'
        s+= '</table>'
        return s
        
    def updateGUI(self):
        dfsummary = self.R('dim('+self.Rvariables['dataframe_org'] + ')', 'getRData')
        self.infob.setText(self.R(self.Rvariables['filename']))
        self.infoc.setText("Rows: " + str(dfsummary[0]) + '\nColumns: ' + str(dfsummary[1]))
        self.FileInfoBox.setHidden(False)
    def commit(self):
        self.R(self.Rvariables['cm'] + '<- data.frame(row.names = rownames('
        +self.Rvariables['dataframe_org']+'))')
        self.updateGUI()
        sendData = RvarClasses.RDataFrame(data = self.Rvariables['dataframe_org'], parent = self.Rvariables['dataframe_org'], cm = self.Rvariables['cm'])
        #sendData = RvarClasses.RDataFrame(data = self.Rvariables['dataframe_org'], parent = self.Rvariables['dataframe_org'], cm = self.Rvariables['cm'])
        self.rSend("data.frame", sendData)
        
    def compileReport(self):
        self.reportSettings("File Name", [(self.Rvariables['filename'], self.R(self.Rvariables['filename']))])
        
        self.reportRaw(self.fileInfo.toHtml())
        #self.finishReport()
        
    # def sendReport(self):
        # self.compileReport()
        # self.showReport()
        
        
    
        