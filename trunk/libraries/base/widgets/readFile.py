"""
<name>Read Files</name>
<description>Reads files from a text file and brings them into RedR.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.</description>
<tags>Data Input</tags>
<RFunctions>utils:read.table</RFunctions>
<icon>readfile.png</icon>
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
    
    globalSettingsList = ['filecombo','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "ReadFile", wantMainArea = 0, resizingEnabled = 1)
        self.path = os.path.abspath('/')
        self.colClasses = []
        self.myColClasses = []
        self.colNames = []
        self.dataTypes = []
        self.useheader = 1
        
        
        #set R variable names        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'parent'])
        
        #signals
        self.inputs = None
        self.outputs = [("data.frame", signals.RDataFrame)]
        #GUI
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        #area.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.MinimumExpanding))
        #area.layout().setAlignment(Qt.AlignTop)
        options = redRGUI.widgetBox(area,orientation='vertical')
        options.setMaximumWidth(300)
        # options.setMinimumWidth(300)
        options.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        area.layout().setAlignment(options,Qt.AlignTop)
        
        
        box = redRGUI.groupBox(options, label="Load File", 
        addSpace = True, orientation='horizontal')
        self.filecombo = redRGUI.fileNamesComboBox(box, 
        orientation='horizontal',callback=self.scanNewFile)
        
        button = redRGUI.button(box, label = 'Browse', callback = self.browseFile)
        
        self.fileType = redRGUI.radioButtons(options, label='File Type',
        buttons = ['Text', 'Excel'], setChecked='Text',callback=self.scanNewFile,
        orientation='horizontal')
        self.fileType.hide()

        
        self.delimiter = redRGUI.radioButtons(options, label='Column Seperator',
        buttons = ['Tab', 'Space', 'Comma', 'Other'], setChecked='Tab',callback=self.scanNewFile,
        orientation='horizontal')
        self.otherSepText = redRGUI.lineEdit(self.delimiter.box,text=';',width=20,orientation='horizontal')
        QObject.connect(self.otherSepText, SIGNAL('textChanged(const QString &)'), self.otherSep)
        
        self.headersBox = redRGUI.groupBox(options, label="Row and Column Names", 
        addSpace = True, orientation ='horizontal')

        self.hasHeader = redRGUI.checkBox(self.headersBox, buttons = ['Column Headers'],setChecked=['Column Headers'],toolTips=['a logical value indicating whether the file contains the names of the variables as its first line. If missing, the value is determined from the file format: header is set to TRUE if and only if the first row contains one fewer field than the number of columns.'],
        orientation='vertical',callback=self.scanNewFile)
        
        self.rowNamesCombo = redRGUI.comboBox(self.headersBox,label='Select Row Names', items=[],
        orientation='vertical',callback=self.scanFile)
        #self.rowNamesCombo.setMaximumWidth(250)        
        
        self.otherOptionsBox = redRGUI.groupBox(options, label="Other Options", 
        addSpace = True, orientation ='vertical')
        # box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        split = redRGUI.widgetBox(self.otherOptionsBox,orientation='horizontal')
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
        self.decimal = redRGUI.lineEdit(box2, text = '.', label = 'Decimal:', width = 50, orientation = 'horizontal', toolTip = 'Decimal sign, some countries may want to use the \'.\'')
        
        self.numLinesScan = redRGUI.lineEdit(box2,text='10',label='# Lines to Scan:',width=50,orientation='horizontal')

        self.numLinesSkip = redRGUI.lineEdit(box2,text='0',label='# Lines to Skip:',width=50,orientation='horizontal')
        
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
        self.tableArea.setMinimumWidth(500)
        #self.tableArea.setHidden(True)
        self.tableArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

        self.scanarea = redRGUI.textEdit(self.tableArea)
        self.scanarea.setLineWrapMode(QTextEdit.NoWrap)
        self.scanarea.setReadOnly(True)
        self.scroll = redRGUI.scrollArea(self.tableArea);
        
        self.columnTypes = redRGUI.widgetBox(self,orientation=QGridLayout(),margin=10);
        self.scroll.setWidget(self.columnTypes)
        #self.columnTypes.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.columnTypes.setMinimumWidth(460)
        self.columnTypes.layout().setSizeConstraint(QLayout.SetMinimumSize)
        self.columnTypes.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding ,QSizePolicy.MinimumExpanding ))
        self.columnTypes.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        #self.setFileList()
        import sys
        if sys.platform=="win32":
            self.require_librarys(['RODBC'])
            self.setForExcel()
    def setForExcel(self):
        self.fileType.show()
    def otherSep(self,text):
        self.delimiter.setChecked('Other')
        
    def loadCustomSettings(self,settings):
        print 'loadCustomSettings readfile'
        for i in range(len(self.myColClasses)):
            s = redRGUI.radioButtons(self.columnTypes, buttons = ['factor','numeric','character','integer','logical'], 
            orientation = 'horizontal', callback = self.updateColClasses)
            s.setChecked(self.myColClasses[i])
            # index = s.findText(self.myColClasses[i])
            # if index != -1:
                # s.setCurrentIndex(index)
            s.setEnabled(False)
            q = redRGUI.widgetLabel(self.columnTypes,label=self.colNames[i])
            self.columnTypes.layout().addWidget(s, i, 1)
            self.columnTypes.layout().addWidget(q, i, 0)
        
    
    def browseFile(self): 
        fn = QFileDialog.getOpenFileName(self, "Open File", self.path,
        "Text file (*.txt *.csv *.tab *.xls);; All Files (*.*)")
        print str(fn)
        if fn.isEmpty(): return
        self.path = os.path.split(str(fn))[0]
        self.filecombo.addFile(fn)
        self.saveGlobalSettings()
        self.scanNewFile()

    def scanNewFile(self):
        self.removeInformation()
        self.removeWarning()
        
        if self.fileType.getChecked() == 'Excel':
            self.delimiter.setDisabled(True)
            self.otherOptionsBox.setDisabled(True)
            self.headersBox.setDisabled(True)
            self.columnTypes.setDisabled(True)
        else:
            self.delimiter.setEnabled(True)
            self.otherOptionsBox.setEnabled(True)
            self.headersBox.setEnabled(True)
            self.columnTypes.setEnabled(True)
        
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
        fn = self.filecombo.getCurrentFile()
        if not fn:
            return

        self.R(self.Rvariables['filename'] + ' = "' + fn + '"') # should protext if R can't find this file
        
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
        elif self.delimiter.getChecked() == 'Other':
            sep = str(self.otherSepText.text())
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
            if self.fileType.getChecked() == 'Excel':
                self.R('channel <- odbcConnectExcel(%s)' %(self.Rvariables['filename']))
                table = self.R('sqlTables(channel)$TABLE_NAME[1]')
                if not scan:
                    nrows = '0'
               
                self.R('%s <- sqlQuery(channel, "select * from [%s]",max=%s)' % (self.Rvariables['dataframe_org'], table,nrows),
                processingNotice=True)
            else:
                RStr = self.Rvariables['dataframe_org'] + '<- read.table(' + self.Rvariables['filename'] + ', header = '+header +', sep = "'+sep +'",quote="' + str(self.quote.text()).replace('"','\\"') + '", colClasses = '+ ccl +', row.names = '+param_name +',skip='+str(self.numLinesSkip.text())+', nrows = '+nrows +',' + otherOptions + 'dec = \''+str(self.decimal.text())+'\')'
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
                s = redRGUI.radioButtons(self.columnTypes,buttons=types,orientation='horizontal',callback=self.updateColClasses)
                
                # print k,i,str(v)
                if str(v) in types:
                    s.setChecked(str(v))
                else:
                    s.addButton(str(v))
                    s.setChecked(str(v))
                s.setMinimumWidth(100)
                q = redRGUI.widgetLabel(self.columnTypes,label=i)
                self.columnTypes.layout().addWidget(s,k,1)
                self.columnTypes.layout().addWidget(q,k,0)
                self.dataTypes.append([i,s])
            
          
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
        self.updateGUI()
        
        # import globalData
        # globalData.setGlobalData(self,'urls',{'dictybase':'http://www.dictybase.org/gene/{db_gene_id}'},description='url')
        sendData = signals.RDataFrame(data = self.Rvariables['dataframe_org'], parent = self.Rvariables['dataframe_org'])
        self.rSend("data.frame", sendData)
        
    def compileReport(self):
        self.reportSettings("File Name", [(self.Rvariables['filename'], self.R(self.Rvariables['filename']))])
        
        self.reportRaw(self.fileInfo.toHtml())
        #self.finishReport()
        
        
        
    
        