"""
<name>View Data Table</name>
<tags>View Data</tags>
<icon>datatable.png</icon>
"""

from OWRpy import *
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
##############################################################################



from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.filterTable import filterTable
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class RDataTable(OWRpy):
    globalSettingsList = ['linkListBox','currentLinks']
    def __init__(self, parent=None, signalManager = None):
        OWRpy.__init__(self, wantGUIDialog = 1)
        
        self.inputs.addInput('id1', 'Input Data Table', redRRDataFrame, self.dataset) 

        self.data = {}          # dict containing the table infromation
        self.dataParent = None
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
        #The settings
        self.advancedOptions = widgetBox(self.GUIDialog)
        self.GUIDialog.layout().setAlignment(self.advancedOptions,Qt.AlignTop)
        
        
        self.infoBox = groupBox(self.advancedOptions, label="Data Information")
        self.infoBox.setHidden(True)

        self.rowColCount = widgetLabel(self.infoBox)
        #saveTab = self.tabWidgeta.createTabPage('Save Data')
        saveTab = groupBox(self.advancedOptions,label='Save Data',orientation='horizontal')
        #widgetLabel(saveTab, label="Saves the current table to a file.")
        #button(saveTab, label="Set File", callback = self.chooseDirectory)
        #self.fileName = widgetLabel(saveTab, label="")
        self.separator = comboBox(saveTab, label = 'Seperator:', 
        items = ['Comma', 'Tab', 'Space'], orientation = 'horizontal')
        save = button(saveTab, label="Save As File", callback=self.writeFile,
        toolTip = "Write the table to a text file.")
        saveTab.layout().setAlignment(save,Qt.AlignRight)

        #links:
        linksTab = groupBox(self.advancedOptions, 'Links to Websites')        
        self.linkListBox = listBox(linksTab,label='Links to Websites', displayLabel=False,includeInReports=False)
        self.linkListBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.customLink = lineEdit(linksTab, label = 'Add Link:', includeInReports=False)
        b = button(linksTab, label = 'Add', toolTip = 'Adds a link to the link section for interactive data exploration.\nThe link must have a marker for the row information in the form\n{column number}\n\nFor example:http://www.google.com/#q={2}, would do a search Google(TM) for whatever was in column 2 of the row of the cell you clicked.\nYou can test this if you want using the example.', callback=self.addCustomLink)
        button(linksTab, label = 'Clear Links', toolTip = 'Clears the links from the links section', 
        callback = self.clearLinks)
        linksTab.layout().setAlignment(b,Qt.AlignRight)
        widgetLabel(linksTab,label ="""
Creating new links:
http://www.ncbi.nlm.nih.gov/gene/{gene_id}
- Here {gene_id} is a place holder and should be 
  the column name in your table. 
- The value in that column and selected row will 
  replace the place holder. 
          """)
        

        #The table
        self.tableBox = widgetBox(self.controlArea)
        self.tableBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #boxSettings = groupBox(self.advancedOptions, label = "Settings")

        self.table = filterTable(self.tableBox,label = 'Data Table', sortable=True,
        filterable=True,selectionMode = QAbstractItemView.SingleSelection, callback=self.itemClicked)
        
        
    def dataset(self, dataset):
        """Generates a new table and puts it in the table section.  If no table is present the table section remains hidden."""
        print '################################dataset', dataset
        if not dataset:
            self.table.clear()
            return
        #print dataset
        self.supressTabClick = True
        #self.table.show()
        self.data = dataset.getData()
        self.dataParent = dataset
            
        if dataset.optionalDataExists('links'):
            linksData = dataset.getOptionalData('links')['data']
            self.linksListBox.update(linksData.keys())
            self.currentLinks.update(linksData)
        
        #self.currentData = dataset.getData()
        dim = dataset.getDims_data()#self.R('dim(' + dataset['data'] + ')')
        self.rowColCount.setText('# Row: ' + unicode(dim[0]) + "\n# Columns: " + unicode(dim[1]))
        self.infoBox.setHidden(False)
        self.table.setRTable(self.data)

        self.supressTabClick = False
            
    def itemClicked(self, val):
        # print 'item clicked'
        # print self.data
        RclickedRow = int(val.row())+1
        
        for item in self.linkListBox.selectedItems():
            #print item.text()
            #print unicode(self.currentLinks)
            url = self.currentLinks[unicode(item.text())]
            col = url[url.find('{')+1:url.find('}')]
            print 'col', col, type(col)
            if col == 0 or col == 'row': #special cases for looking into rownames
                #cellVal = self.data.getData()['row_names'][val.row()]  
                cellVal = self.R('rownames('+self.data+')['+unicode(RclickedRow)+']')
            else:
                
                #cellVal = self.data.getData()[col][val.row()]  
                cellVal = self.R(self.data+'['+unicode(RclickedRow)+',"'+col+'"]')
            url = url.replace('{'+col+'}', unicode(cellVal))
            #print url
            import webbrowser
            webbrowser.open_new_tab(url)
    def clearLinks(self):
        self.linkListBox.clear()
        self.currentLinks = {}
    def addCustomLink(self):
        url = unicode(self.customLink.text())
        self.linkListBox.addItem(url)
        self.currentLinks[url] = url
        self.customLink.clear()
        self.saveGlobalSettings()
        
    def writeFile(self):
        
        if not self.data: 
            self.status.setText('Data does not exist.')
            return
        name = QFileDialog.getSaveFileName(self, "Save File", os.path.abspath('/'),
        "Text file (*.csv *.tab *.txt );; All Files (*.*)")
        if name.isEmpty(): return
        name = unicode(name.toAscii())
        if self.separator.currentText() == 'Tab': #'tab'
            sep = '\t'
        elif self.separator.currentText() == 'Space':
            sep = ' '
        elif self.separator.currentText() == 'Comma':
            sep = ','
        #use the R function if the parent of the dict is an R object.
        if type(self.data) in [str, unicode]:
            self.R('write.table('+self.data+',file="'+unicode(name)+'", quote = FALSE, sep="'+sep+'")', wantType = 'NoConversion')
        else:  # We write the file ourselves
            if self.dataParent:
                string = ''
                for key in self.dataParent.getData().keys():
                    string += unicode(key)+sep
                string += '\n'
                for i in range(self.dataParent.getItem('length')):
                    for key in self.dataParent.getData().keys():
                        string += self.dataParent.getData()[key][i]+sep
                    string += '\n'
                
                f = open(unicode(name), 'w')
                f.write(string)
                f.close()
            else:
                self.status.setText('Can\'t write to a file')
            
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

    def getReportText(self, fileDir):
        text = self.table.getReportText(fileDir)
        return text

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

