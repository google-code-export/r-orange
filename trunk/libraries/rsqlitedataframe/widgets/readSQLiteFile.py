###  The SQLite read file should read in data from a file and convert it into an SQLite structure.  This will normally scan for column names and will assume that the column names are rectangular.  This can be modified using a line edit.  Will emit a class of SQLite Data which will have as a metaclass the RDataFrame R Variable type.  


"""
<name>Convert Table to SQLite</name>
<description>Reads files from a text file and brings them into RedR in the form of an SQLite structure.  These files should be like a table and should have values that are separated either by a tab, space, or comma.  You can use the scan feature to scan a small part of your data and make sure that it is in the correct format.  You can also set a column to represent the row names of your data.  This is encouraged if you have row names as some widgets rely on row names to help them function.  By specifying a column as a rownames column that column will have the reserved word of Rownames no matter what the column name is in the data table that you are reading.  SQLite tables can be connected to any RDataFrame or RList accepting widget.</description>
<tags>Data Input, SQLite</tags>
<RFunctions>utils:read.table</RFunctions>
<icon>icons/readfile.png</icon>
<priority>10</priority>
"""

from OWRpy import *
import redRGUI 

import re, os
import textwrap
import cPickle
import pickle
import types
import sqlite3
class readSQLiteFile(OWRpy):
    
    globalSettingsList = ['recentFiles','path']
    def __init__(self, parent=None, signalManager=None):

        OWRpy.__init__(self,parent, signalManager, "SQLite File Reader", wantMainArea = 0, resizingEnabled = 1)

        self.recentFiles=['Select File']
        self.path = os.path.abspath('/')
        self.colClasses = []
        self.myColClasses = []
        self.colNames = []
        self.dataTypes = []
        self.useheader = 1
        self.loadSettings()
        #set R variable names        
        self.database = 'local|temp.db'
        
        self.setRvariableNames(['dataframe_org','dataframe_final','filename', 'parent'])
        self.inputs = None
        self.outputs = [("data.frame", signals.rsqlitedataframe.SQLiteTable)]
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
        box2 = redRGUI.widgetBox(options)
        self.dbinfo = redRGUI.widgetLabel(box2, label = 'Database File: local directory')
        button2 = redRGUI.button(box2, 'Change File', callback = self.changeDirectory)
        
        
        self.delimiter = redRGUI.radioButtons(options, label='Column Seperator',
        buttons = ['Tab', 'Space', 'Comma'], setChecked='Tab',callback=self.scanNewFile,
        orientation='horizontal')

        box = redRGUI.groupBox(options, label="Row and Column Names", 
        addSpace = True, orientation ='horizontal')

        self.hasHeader = redRGUI.checkBox(box, buttons = ['Column Headers'],setChecked=['Column Headers'],toolTips=['a logical value indicating whether the file contains the names of the variables as its first line. If missing, the value is determined from the file format: header is set to TRUE if and only if the first row contains one fewer field than the number of columns.'],
        orientation='vertical',callback=self.scanNewFile)
        
        # self.rowNamesCombo = redRGUI.comboBox(box,label='Select Row Names', items=[],
        # orientation='vertical',callback=self.scanFile)
        #self.rowNamesCombo.setMaximumWidth(250)        
        
        box = redRGUI.groupBox(options, label="Other Options", 
        addSpace = True, orientation ='vertical')
        # box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        split = redRGUI.widgetBox(box,orientation='horizontal')
        box2 = redRGUI.widgetBox(split,orientation='vertical')
        #box2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        split.layout().setAlignment(box2,Qt.AlignTop)
        #self.quote = redRGUI.lineEdit(box2,text='"',label='Quote:', width=50, orientation='horizontal')
        self.decimal = redRGUI.lineEdit(box2, text = '.', label = 'Decimal:', width = 50, orientation = 'horizontal', toolTip = 'Decimal sign, some countries may want to use the \'.\'')
        self.numLinesScan = redRGUI.lineEdit(box2,text='10',label='# Lines to Scan:',width=50,orientation='horizontal')
        
        
        holder = redRGUI.widgetBox(options,orientation='horizontal')
        rescan = redRGUI.button(holder, label = 'Rescan File', callback = self.scanNewFile)
        load = redRGUI.button(holder, label = 'Load File', callback = self.loadFile)
        holder.layout().setAlignment(Qt.AlignRight)

        self.tableArea = redRGUI.groupBox(area)
        self.tableArea.setMinimumWidth(200)
        #self.tableArea.setHidden(True)
        self.tableArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)

        self.scanarea = redRGUI.textEdit(self.tableArea)
        self.scanarea.setLineWrapMode(QTextEdit.NoWrap)
        self.scanarea.setReadOnly(True)
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

    def changeDirectory(self):
        ### set a new file name to save the directory to.
        fn = QFileDialog.getSaveFileName(self, "Set Database", os.path.abspath('/'), "Database (*.db)")
        if fn.isEmpty(): return
        self.dbinfo.setText('Database File:'+str(fn))
        self.database = os.path.abspath(str(fn))
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

        # for i in self.columnTypes.findChildren(QWidget):
            # i.setHidden(True)
          
        # self.rowNamesCombo.clear()
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
        
        if len(self.recentFiles) ==0 or self.filecombo.currentIndex() == 0: # clear the scan area because there is no file to work on.
            self.scanarea.clear()
            return
        if not os.path.isfile(self.recentFiles[self.filecombo.currentIndex()]): # check if the file exists and can be read
            del self.recentFiles[self.filecombo.currentIndex()]
            self.setFileList()
            QMessageBox.information(self,'Error', "File does not exist.", 
            QMessageBox.Ok + QMessageBox.Default)

            return
            
        
        if self.delimiter.getChecked() == 'Tab': #'tab'
            sep = '\t'
        elif self.delimiter.getChecked() == 'Space':
            sep = ' '
        elif self.delimiter.getChecked() == 'Comma':
            sep = ','
        
        if scan:
            nrows = str(self.numLinesScan.text())
        else:
            nrows = '-1'
        
        
        # if self.rowNamesCombo.currentIndex() not in [0,-1]:
            # self.rownames = str(self.rowNamesCombo.currentText())
            # param_name = '"' + self.rownames + '"'
        # else:
            # param_name = 'NULL' 
            # self.rownames = 'NULL'
        
        cls = []
        for i,new,old in zip(xrange(len(self.myColClasses)),self.myColClasses,self.colClasses):
            if new != old:
                cls.append(self.dataTypes[i][0] + '="' + new + '"')
        
        if len(cls) > 0:
            ccl = 'c(' + ','.join(cls) + ')'
        else:
            ccl = 'NA'
        
        ## connect to the file and read it 
        i = 0
        tableName = str(self.filecombo.currentText()).split('.')[0]
        
        ## make a fake read of the file and get the second line of data, this will give us the data types
        f2 = open(self.recentFiles[self.filecombo.currentIndex()], 'r')
        f2.readline() # make s single call to get to the second line
        dtl = f2.readline()
        f2.close()
        dtl = dtl.split(sep)
        print dtl
        f = open(self.recentFiles[self.filecombo.currentIndex()], 'r')
        if 'local|' in self.database:
            database = os.path.join(qApp.canvasDlg.tempDir, self.database.split('|')[1])
        else:
            database = self.database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS '+tableName)  # we drop the previous table to remove any reference to it from this database.  we must do this so there is no conflict with the new data.
        
        #try:
        for line in f:  # itterate over the lines and convert to the sqlite database
            # line 0 is the column names
            if str(self.decimal.text()) != '.':
                line = line.replace(str(self.decimal.text()), '.') # replace the decimal place specified by the uesr with the '.' in files where the decimal place is not '.'
            if i == 0:
                line = line.replace('.', '_')  # must convert from the annoying habbit of placing '.' in the names of r variables that is not accepted by any other programming languagre
                lineData = line.split(sep)
                for j in range(len(lineData)): # move across the columns and set the data type to the type of data in the columns.  This might be hard because we don't know about the data yet.
                    try:
                        float(dtl[j])
                        lineData[j] = str(lineData[j])+' real'
                    except:
                        lineData[j] = str(lineData[j])+' text'
                print "create table "+tableName+" ("+','.join(lineData)+")"
                cursor.execute("create table "+tableName+" ("+','.join(lineData)+")")  # insert the column names into the table, this is the command that also makes the table
            else:
                lineData = line.split(sep)
                for i in range(len(lineData)):
                    if lineData[i] == '' or lineData[i] == None:
                        lineData[i] = '\'NA\''
                    if type(lineData[i]) not in [int, float, bool]:
                        lineData[i] = '\''+str(lineData[i])+'\''
                cursor.execute("insert into "+tableName+" values ("+','.join(lineData)+")")  # insert the data into the table
            i += 1
        #except:
            #print 'Error occured in reading file'
        conn.commit()
        conn.close()
        f.close()
        
        if scan:
            self.updateScan()
        else:
            self.commit()

    def updateScan(self):
        #if self.rowNamesCombo.count() == 0:
        if 'local|' in self.database:
            database = os.path.join(qApp.canvasDlg.tempDir, self.database.split('|')[1])
        else:
            database = self.database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        print 'PRAGMA table_info('+str(self.filecombo.currentText()).split('.')[0]+')'
        cursor.execute('PRAGMA table_info('+str(self.filecombo.currentText()).split('.')[0]+')')
        colnames = cursor.fetchall()
        print colnames
        
        self.scanarea.clear()
        # print self.R(self.Rvariables['dataframe_org'])
        # return
        
        
        cursor.execute("SELECT * from "+str(self.filecombo.currentText()).split('.')[0]+" LIMIT "+str(self.numLinesScan.text()))
        data = cursor.fetchall()  # collect the first N lines of the data so that we can put it into the scan area.

        txt = self.html_table(colnames,data)
        
        self.scanarea.setText(txt)
        # if len(self.colClasses) ==0:
            # self.colClasses = self.R('as.vector(sapply(' + self.Rvariables['dataframe_org'] + ',class))',wantType='list')
            # self.myColClasses = self.colClasses
        
        # if len(self.dataTypes) ==0:
            # types = ['factor','numeric','character','integer','logical']
            # self.dataTypes = []
            
            # for k,i,v in zip(range(len(self.colNames)),self.colNames,self.myColClasses):
                # s = redRGUI.comboBox(self.columnTypes,items=types,orientation='horizontal',callback=self.updateColClasses)
                
                # if str(v) in types:
                    # s.setCurrentIndex(types.index(str(v)))
                # else:
                    # s.addItem(str(v))
                    # s.setCurrentIndex(s.count()-1)
                # s.setMinimumWidth(100)
                # q = redRGUI.widgetLabel(self.columnTypes,label=i)
                # self.columnTypes.layout().addWidget(s,k,1)
                # self.columnTypes.layout().addWidget(q,k,0)
                # self.dataTypes.append([i,s])
            
    
        
    def html_table(self,colnames,data):
        s = '<table border="1" cellpadding="3">'
        s+= '  <tr>'
        for c in colnames:
            s += '<td><b>'+str(c[1])+'</b></td>'
        s+= '</tr>'
        
        for r in data:
            s += '<tr>'
            for d in r:
                s += '<td>'+str(d)+'</td>'
            s += '</tr>'
        s+= '</table>'
        return s
        
    def updateGUI(self):
        pass
    def commit(self):
        self.updateGUI()
        
        sendData = signals.rsqlitedataframe.SQLiteTable(data = str(self.filecombo.currentText()).split('.')[0], database = self.database.replace('\\','/'))
        self.rSend("data.frame", sendData)
        
        
        
    
        