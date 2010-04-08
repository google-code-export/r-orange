"""
<name>View Data Table</name>
<description>Shows data in a spreadsheet.</description>
<tags>Data Exploration and Visualization</tags>
<RFunctions>base:data.frame,base:matrix</RFunctions>
<icon>icons/datatable.png</icon>
<priority>1010</priority>
<author>Peter Juvan (peter.juvan@fri.uni-lj.si) modifications by Kyle R Covington and Anup Parikh</author>
"""

# OWDataTable.py
#
# wishes:
# ignore attributes, filter examples by attribute values, do
# all sorts of preprocessing (including discretization) on the table,
# output a new table and export it in variety of formats.
from OWRpy import *
import OWGUI, redRGUI
import math
#from orngDataCaching import *

##############################################################################

OrangeValueRole = Qt.UserRole + 1

class RDataTable(OWRpy):
    #settingsList = ["mylink", "showDistributions", "showMeta", "distColorRgb", "showAttributeLabels", 'linkData']

    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self, parent, signalManager, "Data Table", wantGUIDialog = 1, wantMainArea = 0)
        #OWRpy.__init__(self)
        
        self.inputs = [("Examples", RvarClasses.RDataFrame, self.dataset)]
        self.outputs = []

        self.data = {}          # dict containing the table infromation
        self.showMetas = {}     # key: id, value: (True/False, columnList)
        self.showMeta = 1
        self.showAttributeLabels = 1
        self.showDistributions = 1
        self.distColorRgb = (220,220,220, 255)
        self.distColor = QColor(*self.distColorRgb)
        self.locale = QLocale()
        self.currentLinks = {}
        #R modifications
        
        self.currentData = None
        self.dataTableIndex = {}
        self.supressTabClick = False
        self.mylink = ''
        self.link = {}
        self.loadSettings()

        #The settings
        

        self.advancedOptions = redRGUI.widgetBox(self.GUIDialog)
        self.GUIDialog.layout().setAlignment(self.advancedOptions,Qt.AlignTop)
        
        
        self.infoBox = redRGUI.groupBox(self.advancedOptions, label="Data Information")
        self.infoBox.setHidden(True)

        self.rowColCount = redRGUI.widgetLabel(self.infoBox)
        #saveTab = self.tabWidgeta.createTabPage('Save Data')
        saveTab = redRGUI.groupBox(self.advancedOptions,label='Save Data',orientation='horizontal')
        #redRGUI.widgetLabel(saveTab, label="Saves the current table to a file.")
        #redRGUI.button(saveTab, label="Set File", callback = self.chooseDirectory)
        #self.fileName = redRGUI.widgetLabel(saveTab, label="")
        self.separator = redRGUI.comboBox(saveTab, label = 'Seperator:', 
        items = ['Tab', 'Space', 'Comma'], orientation = 'horizontal')
        save = redRGUI.button(saveTab, label="Save As File", callback=self.writeFile,
        tooltip = "Write the table to a text file.")
        saveTab.layout().setAlignment(save,Qt.AlignRight)

        #links:
        linksTab = redRGUI.groupBox(self.advancedOptions, 'Links to Websites')        
        self.linkListBox = redRGUI.listBox(linksTab)
        self.linkListBox.setSelectionMode(QAbstractItemView.MultiSelection)
        self.customLink = redRGUI.lineEdit(linksTab, label = 'Add Link:')
        b = redRGUI.button(linksTab, label = 'Add',callback=self.addCustomLink)
        linksTab.layout().setAlignment(b,Qt.AlignRight)
        
        resizeColsBox = redRGUI.groupBox(self.advancedOptions, orientation="horizontal")
        redRGUI.widgetLabel(resizeColsBox, label = "Resize columns: ")
        redRGUI.button(resizeColsBox, label = "+", callback=self.increaseColWidth, 
        tooltip = "Increase the width of the columns", width=30)
        redRGUI.button(resizeColsBox, label = "-", callback=self.decreaseColWidth, 
        tooltip = "Decrease the width of the columns", width=30)
        redRGUI.rubber(resizeColsBox)

        #The table
        self.tableBox = redRGUI.groupBox(self.controlArea, label = 'Data Table')
        self.tableBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #boxSettings = redRGUI.groupBox(self.advancedOptions, label = "Settings")
        

        # self.btnResetSort = redRGUI.button(boxSettings, label = "Restore Order of Examples", 
        # callback = self.btnResetSortClicked, tooltip = "Show examples in the same order as they appear in the file")

        self.table = redRGUI.Rtable(self.tableBox)
        #self.resize(700,500)
        #self.move(300, 25)

    def dataset(self, dataset, id=None):
        """Generates a new table and puts it in the table section.  If no table is present the table section remains hidden."""
        #print 'got data'
        #print data
        self.supressTabClick = True
        if dataset != None:  # can be an empty table!
            self.table.show()
            data = {}
            self.data = data
            tableData = dataset['data']
            if 'link' in dataset:
                #self.link[str(id)] = dataset['link']
                print 'setting link as '+str(self.link[str(id)])
                self.linkListBox.clear()
                if str(id) in self.link:
                    for key in self.link[str(id)].keys():
                        self.linkListBox.addItem(key)
                    self.currentLinks = self.link[str(id)]
            
            else: 
                linkData = None
                print 'no link data detected'
            #self.showMetas[id] = (True, [])
            #self.dataTableIndex[id] = dataset
            self.currentData = dataset['data']
            dim = self.R('dim(' + dataset['data'] + ')')
            self.rowColCount.setText('# Row: ' + str(dim[0]) + "\n# Columns: " + str(dim[1]))
            self.infoBox.setHidden(False)

            #if id in self.link: #start the block for assignment of link data attributes
            self.connect(self.table, SIGNAL("itemClicked(QTableWidgetItem*)"), lambda val, tableData = tableData: self.itemClicked(val, tableData))
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

            self.table.setRTable(dataset['data'])

            self.needsProcessingHandler(self, 0)

        self.supressTabClick = False
            
    def itemClicked(self, val, table):
        print 'item clicked'
        
        RclickedRow = int(val.row())+1
        
        for item in self.linkListBox.selectedItems():
            #print item.text()
            #print str(self.currentLinks)
            url = self.currentLinks[str(item.text())]
            col = url[url.find('{')+1:url.find('}')]
            if col == 0 or col == 'row': #special cases for looking into rownames
                cellVal = self.R('rownames('+table+')['+str(RclickedRow)+']')
            else:
                cellVal = self.R(table+'['+str(RclickedRow)+','+col+']')
            url = url.replace('{'+col+'}', str(cellVal))
            #print url
            import webbrowser
            webbrowser.open_new_tab(url)
        
        
        # if self.mylink != '': #the user put in a link
            # col = self.mylink[self.mylink.find('{')+1:self.mylink.find('}')]
            # cellVal = self.R(table+'['+str(RclickedRow)+','+col+']')
            # self.rsession('shell.exec("'+self.mylink.replace('{'+col+'}', str(cellVal))+'")')
            # pass


    def addCustomLink(self):
        url = str(self.customLink.text())
        self.linkListBox.addItem(url)
        self.currentLinks[url] = url
        self.customLink.clear()
        
    def writeFile(self):
    
        if not self.currentData: return;
        name = QFileDialog.getSaveFileName(self, "Save File", os.path.abspath('/'),
        "Text file (*.txt *.csv *.tab);; All Files (*.*)")
        if name.isEmpty(): return

        if self.separator.currentText() == 'Tab': #'tab'
            sep = '\t'
        elif self.separator.currentText() == 'Space':
            sep = ' '
        elif self.separator.currentText() == 'Comma':
            sep = ','
        self.R('write.table('+self.currentData+',file="'+str(name)+'", quote = FALSE, sep="'+sep+'")')
    def changeColor(self):
        color = QColorDialog.getColor(self.distColor, self)
        if color.isValid():
            self.distColorRgb = color.getRgb()
            self.updateColor()

    def updateColor(self):
        self.distColor = QColor(*self.distColorRgb)
        w = self.colButton.width()-8
        h = self.colButton.height()-8
        pixmap = QPixmap(w, h)
        painter = QPainter()
        painter.begin(pixmap)
        painter.fillRect(0,0,w,h, QBrush(self.distColor))
        painter.end()
        self.colButton.setIcon(QIcon(pixmap))

    def increaseColWidth(self):
        table = self.table
        for col in range(table.columnCount()):
            w = table.columnWidth(col)
            table.setColumnWidth(col, w + 10)

    def decreaseColWidth(self):
        table = self.table
        for col in range(table.columnCount()):
            w = table.columnWidth(col)
            minW = table.sizeHintForColumn(col)
            table.setColumnWidth(col, max(w - 10, minW))

    def RWidgetReload(self):
        print 'on load data table'
        self.processSignals()
   
    # Writes data into table, adjusts the column width.
    def setTable(self, table, data):
        if data==None:
            return
        qApp.setOverrideCursor(Qt.WaitCursor)
        vars = data.domain.variables
        m = data.domain.getmetas(False)
        ml = [(k, m[k]) for k in m]
        ml.sort(lambda x,y: cmp(y[0], x[0]))
        metas = [x[1] for x in ml]
        metaKeys = [x[0] for x in ml]

        mo = data.domain.getmetas(True).items()
        if mo:
            mo.sort(lambda x,y: cmp(x[1].name.lower(),y[1].name.lower()))
#            metas.append(None)
#            metaKeys.append(None)

        varsMetas = vars + metas

        numVars = len(data.domain.variables)
        numMetas = len(metas)
        numVarsMetas = numVars + numMetas
        numEx = len(data)
        numSpaces = int(math.log(max(numEx,1), 10))+1

        table.clear()
        table.oldSortingIndex = -1
        table.oldSortingOrder = 1
        table.setColumnCount(numVarsMetas)
        table.setRowCount(numEx)

        table.dist = getCached(data, orange.DomainBasicAttrStat, (data,))
        
        table.setItemDelegate(TableItemDelegate(self, table))
        table.variableNames = [var.name for var in varsMetas]
        table.data = data
        id = self.table2id.get(table, None)

        # set the header (attribute names)
        table.setHorizontalHeaderLabels(table.variableNames)
        if self.currentData:
            rowNames = self.R('rownames('+self.currentData+')')
            if rowNames != 'NULL':
                table.setVerticalHeaderLabels(rowNames)
        if self.showAttributeLabels:
            labelnames = set()
            for a in data.domain:
                labelnames.update(a.attributes.keys())
            labelnames = sorted(list(labelnames))
            if len(labelnames):
                table.setHorizontalHeaderLabels([table.variableNames[i] + "\n" + "\n".join(["%s" % a.attributes.get(lab, "") for lab in labelnames]) for (i, a) in enumerate(table.data.domain.attributes)])
            else:
                table.setHorizontalHeaderLabels([table.variableNames[i] for (i, a) in enumerate(table.data.domain.attributes)])
                

        #table.hide()
        clsColor = QColor(160,160,160)
        metaColor = QColor(220,220,200)
        white = QColor(Qt.white)
        for j,(key,attr) in enumerate(zip(range(numVars) + metaKeys, varsMetas)):
            self.progressBarSet(j*100.0/numVarsMetas)
            if attr == data.domain.classVar:
                bgColor = clsColor
            elif attr in metas or attr is None:
                bgColor = metaColor
                self.showMetas[id][1].append(j) # store indices of meta attributes
            else:
                bgColor = white

            for i in range(numEx):
##                table.setItem(i, j, TableWidgetItem(data[i][key]
##                OWGUI.tableItem(table, i,j, str(data[i][key]), backColor = bgColor)
                if data.domain[key].varType == orange.VarTypes.Continuous and not data[i][key].isSpecial():
                    item = OWGUI.tableItem(table, i,j, float(str(data[i][key])), backColor = bgColor)
                else:
                    item = OWGUI.tableItem(table, i,j, str(data[i][key]), backColor = bgColor)
##                item.setData(OrangeValueRole, QVariant(str(data[i][key])))

        table.resizeRowsToContents()
        table.resizeColumnsToContents()

        self.connect(table.horizontalHeader(), SIGNAL("sectionClicked(int)"), self.sortByColumn)
        #table.verticalHeader().setMovable(False)

        qApp.restoreOverrideCursor()
        #table.setCurrentCell(-1,-1)
        #table.show()
 

    def sortByColumn(self, index):
        table = self.tabs.currentWidget()
        table.horizontalHeader().setSortIndicatorShown(1)
        header = table.horizontalHeader()
        if index == table.oldSortingIndex:
            order = table.oldSortingOrder == Qt.AscendingOrder and Qt.DescendingOrder or Qt.AscendingOrder
        else:
            order = Qt.AscendingOrder
        table.sortByColumn(index, order)
        table.oldSortingIndex = index
        table.oldSortingOrder = order
        #header.setSortIndicator(index, order)

    def tabClicked(self, qTableInstance):
        """Updates the info box and showMetas checkbox when a tab is clicked.
        """
        if not self.supressTabClick:
            id = self.table2id.get(qTableInstance,None)
            dataset = self.dataTableIndex[id]
            self.currentData = dataset['data']
            print str(id)
            self.setInfo(self.data.get(id,None))
            show_col = self.showMetas.get(id,None)
            if show_col:
                self.cbShowMeta.setChecked(show_col[0])
                self.cbShowMeta.setEnabled(len(show_col[1])>0)
            self.linkListBox.clear()
            if str(id) in self.link:
                for key in self.link[str(id)].keys():
                    self.linkListBox.addItem(key)
                self.currentLinks = self.link[str(id)]
    def cbShowMetaClicked(self):
        table = self.tabs.currentWidget()
        id = self.table2id.get(table, None)
        if self.showMetas.has_key(id):
            show,col = self.showMetas[id]
            self.showMetas[id] = (not show,col)
        if show:
            for c in col:
                table.hideColumn(c)
        else:
            for c in col:
                table.showColumn(c)
                table.resizeColumnToContents(c)

    def cbShowAttLabelsClicked(self):
        for table in self.table2id.keys():
            if self.showAttributeLabels:
                labelnames = set()
                for a in table.data.domain:
                    labelnames.update(a.attributes.keys())
                labelnames = sorted(list(labelnames))
                if len(labelnames):
                    table.setHorizontalHeaderLabels([table.variableNames[i] + "\n" + "\n".join(["%s" % a.attributes.get(lab, "") for lab in labelnames]) for (i, a) in enumerate(table.data.domain.attributes)])
                else:
                    table.setHorizontalHeaderLabels([table.variableNames[i] for (i, a) in enumerate(table.data.domain.attributes)])
            else:
                table.setHorizontalHeaderLabels(table.variableNames)
            # h = table.horizontalHeader().adjustSize()

    def cbShowDistributions(self):
        table = self.table
        # print self.tabs.currentWidget
        # print table
        table.reset()

    # show data in the default order
    def btnResetSortClicked(self):
        table = self.tabs.currentWidget()
        id = self.table2id[table]
        data = self.data[id]
        self.progressBarInit()
        self.setTable(table, data)
        self.progressBarFinished()

    def setInfo(self, data):
        """Updates data info.
        """
        def sp(l, capitalize=False):
            n = len(l)
            if n == 0:
                if capitalize:
                    return "No", "s"
                else:
                    return "no", "s"
            elif n == 1:
                return str(n), ''
            else:
                return str(n), 's'

        if data == None:
            self.infoEx.setText('No data on input.')
            self.infoMiss.setText('')
            self.infoAttr.setText('')
            self.infoMeta.setText('')
            self.infoClass.setText('')
        else:
            #(row, col) = data['matrix'].shape
            row = len(data[data.keys()[0]])
            col = len(data.keys())

            self.processingBox.setHtml('%i rows and %i columns.' % (row, col))

class TableItemDelegate(QItemDelegate):
    def __init__(self, widget = None, table = None):
        QItemDelegate.__init__(self, widget)
        self.table = table
        self.widget = widget

    def paint(self, painter, option, index):
        painter.save()
        self.drawBackground(painter, option, index)
        value, ok = index.data(Qt.DisplayRole).toDouble()

        if ok:        # in case we get "?" it is not ok
            if self.widget.showDistributions:
                col = index.column()
                if col < len(self.table.dist) and self.table.dist[col]:        # meta attributes and discrete attributes don't have a key
                    dist = self.table.dist[col]
                    smallerWidth = option.rect.width() * (dist.max - value) / (dist.max-dist.min or 1)
                    painter.fillRect(option.rect.adjusted(0,0,-smallerWidth,0), self.widget.distColor)
##            text = self.widget.locale.toString(value)    # we need this to convert doubles like 1.39999999909909 into 1.4
##        else:
        text = index.data(Qt.DisplayRole).toString()
        ##text = index.data(OrangeValueRole).toString()

        self.drawDisplay(painter, option, option.rect, text)
        painter.restore()




