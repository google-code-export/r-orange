"""
<name>Data Table</name>
<description>Shows data in a spreadsheet.</description>
<tags>R</tags>
<icon>icons/DataTable.png</icon>
<priority>1010</priority>
<contact>Peter Juvan (peter.juvan@fri.uni-lj.si)</contact>
"""

# OWDataTable.py
#
# wishes:
# ignore attributes, filter examples by attribute values, do
# all sorts of preprocessing (including discretization) on the table,
# output a new table and export it in variety of formats.
from OWRpy import *
import OWGUI, RRGUI
import math
from orngDataCaching import *

##############################################################################

OrangeValueRole = Qt.UserRole + 1

class RDataTable(OWRpy):
    settingsList = ["mylink", "showDistributions", "showMeta", "distColorRgb", "showAttributeLabels", 'linkData']

    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self, parent, signalManager, "Data Table")
        #OWRpy.__init__(self)
        
        self.inputs = [("Examples", RvarClasses.RDataFrame, self.dataset, Multiple + Default)]
        self.outputs = []

        self.data = {}          # key: id, value: ExampleTable
        self.showMetas = {}     # key: id, value: (True/False, columnList)
        self.showMeta = 1
        self.showAttributeLabels = 1
        self.showDistributions = 1
        self.distColorRgb = (220,220,220, 255)
        self.distColor = QColor(*self.distColorRgb)
        self.locale = QLocale()
        
        #R modifications
        
        self.fileName = ''
        self.delim = 0
        self.currentData = ''
        self.dataTableIndex = {}
        self.supressTabClick = False
        self.mylink = ''
        self.link = {}
        self.loadSettings()

        # info box
        infoBox = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoEx = OWGUI.widgetLabel(infoBox, 'No data on input.')
        self.infoMiss = OWGUI.widgetLabel(infoBox, ' ')
        OWGUI.widgetLabel(infoBox, ' ')
        self.infoAttr = OWGUI.widgetLabel(infoBox, ' ')
        self.infoMeta = OWGUI.widgetLabel(infoBox, ' ')
        OWGUI.widgetLabel(infoBox, ' ')
        self.infoClass = OWGUI.widgetLabel(infoBox, ' ')
        
        
        #tabs
        tabWidgeta = RRGUI.tabWidget(self.controlArea, None, self)
        
        
        #links:
        linksTab = RRGUI.createTabPage(tabWidgeta, None, self, 'Link Data:')
                #OWGUI.widgetLabel(infoBox, "Links:")
        self.linkListBox = OWGUI.listBox(linksTab, self)
        OWGUI.lineEdit(linksTab, self, 'mylink', label = 'Custom Link:')
        
        #save box
        
                #infoBox = OWGUI.widgetBox(self.controlArea, "Save Table")
        saveTab = RRGUI.createTabPage(tabWidgeta, None, self, 'Save Data:')
        OWGUI.widgetLabel(saveTab, "Saves the current table to a file.")
        OWGUI.button(saveTab, self, "Choose Directory", callback = self.chooseDirectory)
        OWGUI.lineEdit(saveTab, self, 'fileName', label = "File:", width = 50)
        OWGUI.comboBox(saveTab, self, 'delim', label = 'Seperator:', items = ['Tab', 'Space', 'Comma'], orientation = 0)
        OWGUI.button(saveTab, self, "Write To File", self.writeFile, tooltip = "Write the table to a text file")
        infoBox.setMinimumWidth(200)
        OWGUI.separator(self.controlArea)

        # settings box
        boxSettings = OWGUI.widgetBox(self.controlArea, "Settings")
        self.cbShowMeta = OWGUI.checkBox(boxSettings, self, "showMeta", 'Show meta attributes', callback = self.cbShowMetaClicked)
        self.cbShowMeta.setEnabled(False)
        self.cbShowAttLbls = OWGUI.checkBox(boxSettings, self, "showAttributeLabels", 'Show attribute labels (if any)', callback = self.cbShowAttLabelsClicked)
        self.cbShowAttLbls.setEnabled(True)
        self.cbShowDistributions = OWGUI.checkBox(boxSettings, self, "showDistributions", 'Visualize continuous values', callback = self.cbShowDistributions)
        colBox = OWGUI.indentedBox(boxSettings, orientation = "horizontal")
        OWGUI.widgetLabel(colBox, "Color: ")
        self.colButton = OWGUI.toolButton(colBox, self, self.changeColor, width=20, height=20, debuggingEnabled = 0)
        OWGUI.rubber(colBox)

        resizeColsBox = OWGUI.widgetBox(boxSettings, 0, "horizontal", 0)
        OWGUI.label(resizeColsBox, self, "Resize columns: ")
        OWGUI.button(resizeColsBox, self, "+", self.increaseColWidth, tooltip = "Increase the width of the columns", width=30)
        OWGUI.button(resizeColsBox, self, "-", self.decreaseColWidth, tooltip = "Decrease the width of the columns", width=30)
        OWGUI.rubber(resizeColsBox)

        self.btnResetSort = OWGUI.button(boxSettings, self, "Restore Order of Examples", callback = self.btnResetSortClicked, tooltip = "Show examples in the same order as they appear in the file")

        OWGUI.rubber(self.controlArea)

        # GUI with tabs
        self.tabs = OWGUI.tabWidget(self.mainArea)
        self.id2table = {}  # key: widget id, value: table
        self.table2id = {}  # key: table, value: widget id
        self.connect(self.tabs,SIGNAL("currentChanged(QWidget*)"),self.tabClicked)

        self.updateColor()
        
    def chooseDirectory(self):
        self.R('setwd(choose.dir())')
    def writeFile(self):
        if self.delim == 0: #'tab'
            sep = '\t'
        elif self.delim == 1:
            sep = ' '
        elif self.delim == 2:
            sep = ','
        self.R('write.table('+self.currentData+',file="'+self.fileName+'", quote = FALSE, sep="'+sep+'")')
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
        table = self.tabs.currentWidget()
        for col in range(table.columnCount()):
            w = table.columnWidth(col)
            table.setColumnWidth(col, w + 10)

    def decreaseColWidth(self):
        table = self.tabs.currentWidget()
        for col in range(table.columnCount()):
            w = table.columnWidth(col)
            minW = table.sizeHintForColumn(col)
            table.setColumnWidth(col, max(w - 10, minW))

    def onLoadSavedSession(self):
        print 'on load data table'
        self.processSignals()
    def dataset(self, dataset, id=None):
        """Generates a new table and adds it to a new tab when new data arrives;
        or hides the table and removes a tab when data==None;
        or replaces the table when new data arrives together with already existing id."""
        #print 'got data'
        #print data
        self.supressTabClick = True
        if dataset != None:  # can be an empty table!
            
            data = self.convertDataframeToExampleTable(dataset['data'])

            if self.data.has_key(id):
                # remove existing table
                table = self.id2table[id]
                self.data.pop(id)
                self.showMetas.pop(id)
                table.hide()
                self.tabs.removeTab(self.tabs.indexOf(table))
                self.table2id.pop(self.id2table.pop(id))
                self.setInfo(self.data.get(self.table2id.get(self.tabs.currentWidget(),None),None))
            self.data[id] = data
            tableData = dataset['data']
            if 'link' in dataset:
                self.link[str(id)] = dataset['link']
                print 'setting link as '+str(self.link[str(id)])
            
            else: 
                linkData = None
                print 'no link data detected'
            self.showMetas[id] = (True, [])
            self.dataTableIndex[id] = dataset
            self.currentData = dataset['data']
            table = OWGUI.table(None, 0,0)
            #if id in self.link: #start the block for assignment of link data attributes
            self.connect(table, SIGNAL("itemClicked(QTableWidgetItem*)"), lambda val, tableData = tableData: self.itemClicked(val, tableData))
            table.setSelectionBehavior(QAbstractItemView.SelectRows)

            self.id2table[id] = table
            self.table2id[table] = id
            if data.name:
                tabName = "%s " % data.name
            else:
                tabName = ""
            tabName += "(" + str(id[1]) + ")"
            if id[2] != None:
                tabName += " [" + str(id[2]) + "]"
            self.tabs.addTab(table, tabName)

            self.progressBarInit()
            self.setTable(table, data)
            self.progressBarFinished()
            self.needsProcessingHandler(self, 0)
            self.tabs.setCurrentIndex(self.tabs.indexOf(table))
            self.setInfo(data)
            self.cbShowMeta.setEnabled(len(self.showMetas[id][1])>0)        # enable showMetas checkbox only if metas exist

        elif self.data.has_key(id):
            table = self.id2table[id]
            self.data.pop(id)
            self.showMetas.pop(id)
            table.hide()
            self.tabs.removeTab(self.tabs.indexOf(table))
            self.table2id.pop(self.id2table.pop(id))
            self.setInfo(self.data.get(self.table2id.get(self.tabs.currentWidget(),None),None))

        # disable showMetas checkbox if there is no data on input
        if len(self.data) == 0:
            self.cbShowMeta.setEnabled(False)
        
        self.supressTabClick = False
            
    def itemClicked(self, val, table):
        print 'item clicked'
        
        RclickedRow = int(val.row())+1
        
        for item in self.linkListBox.selectedItems():
            text = self.currentLinks[item.text()]
            col = text[text.find('{')+1:text.find('}')]
            if col == 0 or col == 'row': #special cases for looking into rownames
                cellVal = self.R('rownames('+table+')['+str(RclickedRow)+']')
            else:
                cellVal = self.R(table+'['+str(RclickedRow)+','+col+']')
            self.rsession('shell.exec("'+text.replace('{'+col+'}', str(cellVal))+'")')
        
        
        if self.mylink != '': #the user put in a link
            col = self.mylink[self.mylink.find('{')+1:self.mylink.find('}')]
            cellVal = self.R(table+'['+str(RclickedRow)+','+col+']')
            self.rsession('shell.exec("'+self.mylink.replace('{'+col+'}', str(cellVal))+'")')
            pass
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
        table = self.tabs.currentWidget()
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
            self.infoEx.setText("%s example%s," % sp(data))
            missData = orange.Preprocessor_takeMissing(data)
            self.infoMiss.setText('%s (%.1f%s) with missing values.' % (len(missData), len(data) and 100.*len(missData)/len(data), "%"))
            #self.infoAttr.setText("%s attribute%s," % sp(data.domain.attributes,True))
            #self.infoMeta.setText("%s meta attribute%s." % sp(data.domain.getmetas()))
            if data.domain.classVar:
                if data.domain.classVar.varType == orange.VarTypes.Discrete:
                    self.infoClass.setText('Discrete class with %s value%s.' % sp(data.domain.classVar.values))
                elif data.domain.classVar.varType == orange.VarTypes.Continuous:
                    self.infoClass.setText('Continuous class.')
                else:
                    self.infoClass.setText("Class is neither discrete nor continuous.")
            else:
                self.infoClass.setText('Classless domain.')
                

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




if __name__=="__main__":
    a = QApplication(sys.argv)
    ow = OWDataTable()

    #d1 = orange.ExampleTable(r'..\..\doc\datasets\auto-mpg')
    #d2 = orange.ExampleTable('test-labels')
    #d3 = orange.ExampleTable(r'..\..\doc\datasets\sponge.tab')
    #d4 = orange.ExampleTable(r'..\..\doc\datasets\wpbc.csv')
    #d5 = orange.ExampleTable(r'..\..\doc\datasets\adult_sample.tab')
    d5 = orange.ExampleTable(r"E:\Development\Orange Datasets\UCI\wine.tab")
    #d5 = orange.ExampleTable(r"e:\Development\Orange Datasets\Cancer\SRBCT.tab")
    ow.show()
    #ow.dataset(d1,"auto-mpg")
    #ow.dataset(d2,"voting")
    #ow.dataset(d4,"wpbc")
    ow.dataset(d5,"adult_sample")
    a.exec_()
    ow.saveSettings()
