"""
.. helpdoc::
<p>Click on column headers to see options for sorting and filtering data.</p>
"""

"""
<widgetXML>    
    <name>View Data Table</name>
    <icon>datatable.png</icon>
    <tags> 
        <tag>View Data</tag> 
    </tags>
    <summary>Shows data in a spreadsheet.</summary>
    <citation>
    <!-- [REQUIRED] -->
        <author>
            <name>Red-R Core Team</name>
            <contact>http://www.red-r.org/contact</contact>
        </author>
        <reference>http://www.red-r.org</reference>
    </citation>
</widgetXML>
"""

"""
<name>View Data Table</name>
<tags>View Data</tags>
<icon>datatable.png</icon>
"""

from OWRpy import *
import redRGUI, signals
import globalData
##############################################################################

import redRi18n
_ = redRi18n.get_(package = 'base')
class RDataTable(OWRpy):
    globalSettingsList = ['linksListBox','currentLinks']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, wantGUIDialog = 1, **kwargs)
        
        self.setRvariableNames(['summaryData'])

        self.inputs.addInput('id1', _('Input Data Table'), [signals.base.TableView, signals.base.RDataFrame, signals.base.StructuredDict], self.dataset) 

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
        self.advancedOptions = redRGUI.base.tabWidget(self.GUIDialog, position = QTabWidget.West) #orientation = 'vertical')
        self.GUIDialog.layout().setAlignment(self.advancedOptions,Qt.AlignTop)
        
        diBox = self.advancedOptions.createTabPage(_("Data Information"))
        vbox = redRGUI.base.widgetBox(diBox)
        self.infoBox = redRGUI.base.groupBox(vbox, label=_("Data Information"))
        self.infoBox.setHidden(False)
        redRGUI.base.widgetLabel(self.infoBox, label = _("A summary of your data will be displayed below when data is available."),  wordWrap = True)
        self.rowColCount = redRGUI.base.widgetLabel(self.infoBox)
        summaryBox = redRGUI.base.groupBox(vbox, label=_("Selected Data Summary"))
        
        self.customSummary = redRGUI.base.lineEdit(summaryBox, label = _('Custom Summary:'), toolTip = _('Place a custom summary function in here which will be added to the regular summary, use {Col} for the column number.  Ex. mean({Col})'))
        self.summaryLabel = redRGUI.base.textEdit(summaryBox, label = _('Summary'),displayLabel=False)

        #saveTab = self.tabWidgeta.createTabPage('Save Data')
        sdBox = self.advancedOptions.createTabPage(_("Save Data"))
        saveTab = redRGUI.base.groupBox(sdBox,label=_('Save Data'),orientation='horizontal')
        #redRGUI.base.widgetLabel(saveTab, label=_("Saves the current table to a file."))
        #redRGUI.base.button(saveTab, label=_("Set File"), callback = self.chooseDirectory)
        #self.fileName = redRGUI.base.widgetLabel(saveTab, label="")
        self.separator = redRGUI.base.comboBox(saveTab, label = 'Seperator:', 
        items = [_('Comma'), _('Tab'), _('Space')], orientation = 'horizontal')
        save = redRGUI.base.button(saveTab, label=_("Save As File"), callback=self.writeFile,
        toolTip = _("Write the table to a text file."))
        saveTab.layout().setAlignment(save,Qt.AlignRight)

        #links:
        linkBox = self.advancedOptions.createTabPage(_('Links to Websites'), canScroll = True)
        linksTab = redRGUI.base.groupBox(linkBox, _('Links to Websites'))        
        self.linksListBox = redRGUI.base.listBox(linksTab,label=_('Links to Websites'),displayLabel=False)
        self.linksListBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.customLink = redRGUI.base.lineEdit(linksTab, label = _('Add Link:'), includeInReports=False)
        hbox = redRGUI.base.widgetBox(linksTab,orientation='horizontal')
        b = redRGUI.base.button(hbox, label = _('Add'), toolTip = _('Adds a link to the link section for interactive data exploration.\nThe link must have a marker for the row information in the form\n{column number}\n\nFor example:http://www.google.com/#q=%s, would do a search Google(TM) for whatever was in the cell you clicked.\nYou can test this if you want using the example.'), callback=self.addCustomLink)
        redRGUI.base.button(hbox, label = _('Clear Links'), toolTip = _('Clears the links from the links section'), 
        callback = self.clearLinks)
        hbox.layout().setAlignment(Qt.AlignRight)
        redRGUI.base.widgetLabel(linksTab,label ="""
Creating new links:
http://www.ncbi.nlm.nih.gov/gene/{gene_id}
- Here {gene_id} is a place holder and should be 
  the column name in your table. 
- The value in that column and selected row will 
  replace the place holder. 
          """)
        
        #The table
        self.tableBox = redRGUI.base.widgetBox(self.controlArea)
        self.tableBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #boxSettings = redRGUI.base.groupBox(self.advancedOptions, label = _("Settings"))

        self.table = redRGUI.base.filterTable(self.tableBox,label = _('Data Table'),displayLabel=False, sortable=True,
        filterable=True,selectionBehavior = QAbstractItemView.SelectItems, callback=self.itemClicked,selectionCallback=self.cellSelection)
        # self.table = filterTable2(self.tableBox, sortable=True,
        # filterable=True,selectionBehavior = QAbstractItemView.SelectItems, callback=self.itemClicked)
        ##########################################################
        # self.R('data <- data.frame(a=rnorm(1000),b=c("a","b","c","d","e"))')
        # self.data = 'iris'
        # self.table.setRTable(self.data)
        ##########################################################
        
        globalData.setGlobalData(self, 'links', [('http://www.google.com/search?q=%s', 'Google'), ('http://en.wikipedia.org/w/index.php?title=Special:Search&search=%s', 'Wikipedia')])
        self.setLinks()
    def customWidgetDelete(self):
        try:
            globalData.removeGlobalData(self)
        except Exception as inst:
            self.log(str(inst))

    def reloadWidget(self):
        self.setLinks()
    def refresh(self):
        self.setLinks()
    def setLinks(self):
        gLinks = [v['data'] for v in globalData.getGlobalData(name = 'links')]
        
        links = []
        for l in gLinks: ## l is now an ordered dict used for the 
            if type(l) == dict:
                links += [(k, v) for k, v in l.items()]
            elif type(l) == list:
                links += l
        self.log(links)
        self.linksListBox.update(links)
            
    def dataset(self, dataset):
        """Generates a new table and puts it in the table section.  If no table is present the table section remains hidden."""
        if not dataset:
            self.table.clear()
            return
        #print dataset
        self.supressTabClick = True
        #self.table.show()
        self.data = dataset.getData()
        self.dataParent = dataset
        #print type(dataset)
        #if isinstance(dataset, signals.base.RDataFrame):
            #self.currentData = dataset.getData()
            #dim = dataset.getDims_data()#self.R('dim(' + dataset['data'] + ')')
            #self.rowColCount.setText(_('# Row: %(ROWCOUNT)s \n# Columns: %(COLCOUNT)s') %  {'ROWCOUNT':unicode(dim[0]), 'COLCOUNT':unicode(dim[1])})
            #self.infoBox.setHidden(False)
        self.table.setTable(dataset, filterable = True, sortable = True)

        self.supressTabClick = False
        #elif isinstance(dataset, signals.base.StructuredDict):
            #self.table.setsignals.base.StructuredDictTable(dataset.getData())
    
    def cellSelection(self,selections):
        
        if len(selections) > 1:
            self.R('%s <- NULL' % self.Rvariables['summaryData'],silent=True)
            rows = []
            cols = []
            inds = selections.indexes()
            for ind in inds:
                #print _('new'), ind.row(),ind.column()
                rows.append(str(ind.row()+1))
                cols.append(str(ind.column()+1))

            self.R('rowInd <- c(' + ','.join(rows) + ')',silent=True)
            self.R('colInd <- c(' + ','.join(cols) + ')',silent=True)
            
            self.R('%s <- apply(cbind(rowInd,colInd),1,FUN=function(x) {%s[x[1],x[2]]})' % (
            self.Rvariables['summaryData'],self.table.getFilteredData()), silent=True)
            tmpData = self.Rvariables['summaryData']

        else:
            x = selections[0]
            rstart = min(x.top()+1,x.bottom()+1)
            rend = max(x.top()+1,x.bottom()+1)
            cstart = min(x.right()+1,x.left()+1)
            cend = max(x.right()+1,x.left()+1)
            # print rstart,rend,cstart,cend
            # self.R('%s <- c(%s,((%s[%d:%d,%d:%d])))' % (
                # self.Rvariables['summaryData'],self.Rvariables['summaryData'],self.table.getFilteredData(),
                # rstart,rend,cstart,cend),silent=True)
            tmpData = '%s[%d:%d,%d:%d]' % (self.table.getFilteredData(),rstart,rend,cstart,cend)
        
        # type = self.R('class('+tmpData+')', wantType = 'Convert', silent = True)
        # print 'type:',type
        # if type =='data.frame':
        isNumeric = self.R('sum(sapply(as.data.frame(%s),FUN=function(x) {!(is.numeric(x) | is.complex(x))})) ==0' % tmpData,silent=True)
        # print 'isNumeric', isNumeric
        if isNumeric:
#        if type in ['integer', 'complex', 'float', 'numeric']:
            summaryText = _('<strong>Sum</strong>: %(SUM)s<br/><strong>Mean</strong>: %(MEAN)s<br/> <strong>Median</strong>: %(MEDIAN)s<br/> <strong>Range</strong>: %(RANGE)s<br/> <strong>Standard Deviation</strong>: %(SD)s<br/> <strong>Count</strong>: %(COUNT)s<br/> <strong>Min</strong>: %(MIN)s<br/> <strong>Max</strong>: %(MAX)s<br/>') % {
                'SUM':str(self.R('format(sum(data.matrix(%s),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'MEAN':str(self.R('format(mean(data.matrix(%s),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'MEDIAN':str(self.R('format(median(data.matrix(%s),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'RANGE':str(self.R('format(range(data.matrix(%s),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'SD':str(self.R('format(sd(as.vector(data.matrix(%s)),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'COUNT':str(self.R('length(data.matrix(%s))' % tmpData, 
                wantType = 'Convert', silent = True)), 
                'MIN':str(self.R('format(min(data.matrix(%s),na.rm=T),digits=4)'% tmpData, 
                wantType = 'Convert', silent = True)), 
                'MAX':str(self.R('format(max(data.matrix(%s),na.rm=T),digits=4)' % tmpData, 
                wantType = 'Convert', silent = True))}
        else:
            summaryText = unicode(self.R('summary('+tmpData+')', wantType = 'Convert', silent = True)).replace('\n', '<br/>')        

        self.summaryLabel.setHtml(unicode(summaryText))
        self.working = False
        
    def itemClicked(self, val):
        # print 'item clicked'
        # print self.data
        
        ######## if R data #########
        clickedRow = int(val.row())+1
        clickedCol = int(val.column())+1
        self.log('%s was clicked at row: %s and column %s' % (str(val.data().toString()), int(val.row()), int(val.column())))
        for k, v in self.linksListBox.selectedItems().items():
            #print item.text()
            #print unicode(self.currentLinks)
            url = k % str(val.data().toString())
            import webbrowser
            self.log(url)
            webbrowser.open_new_tab(url)
        return
        ## make the summary of the data.
        type = self.R('class('+self.data+'[,'+str(clickedCol)+'])', wantType = 'Convert', silent = True)
        if type in ['integer', 'complex', 'float', 'numeric']:
            summaryText = _('<strong>Mean</strong>: %(MEAN)s<br/> <strong>Median</strong>: %(MEDIAN)s<br/> <strong>Range</strong>: %(RANGE)s<br/> <strong>Standard Deviation</strong>: %(SD)s<br/> <strong>Count</strong>: %(COUNT)s<br/> <strong>Min</strong>: %(MIN)s<br/> <strong>Max</strong>: %(MAX)s<br/>') % {
                'MEAN':str(self.R('mean(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'MEDIAN':str(self.R('median(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'RANGE':str(self.R('range(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'SD':str(self.R('sd(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'COUNT':str(self.R('length(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'MIN':str(self.R('min(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True)), 
                'MAX':str(self.R('max(%s[,%s])' % (self.data, clickedCol), wantType = 'Convert', silent = True))}
        else:
            summaryText = unicode(self.R('summary('+self.data+'[,'+str(val.column()+1)+'])', wantType = 'Convert', silent = True)).replace('\n', '<br/>')        
        if unicode(self.customSummary.text()) != '':
            summaryText += _('Custom: %s') % unicode(self.R(unicode(self.customSummary.text()).replace('{Col}', '%s[,%s]' % (self.data, val.column()+1)), wantType = 'Convert', silent = True))
        
        self.summaryLabel.setHtml(unicode(summaryText))
        #print summaryText
    
    def clearLinks(self):
        self.linksListBox.clear()
        self.currentLinks = {}
    def addCustomLink(self):
        url = unicode(self.customLink.text())
        self.linksListBox.addItem(url)
        self.currentLinks[url] = url
        self.customLink.clear()
        self.saveGlobalSettings()
        
    def writeFile(self):
        
        if not self.data: 
            self.status.setText('Data does not exist.')
            return
        name = QFileDialog.getSaveFileName(self, _("Save File"), os.path.abspath('/'),
        "Text file (*.csv *.tab *.txt );; All Files (*.*)")
        if name.isEmpty(): return
        name = unicode(name)
        if self.separator.currentId() =='Tab':
            sep  = '\t'
        elif self.separator.currentId() =='Comma':
            sep  = ','
        elif self.separator.currentId() =='Space':
            sep  = ' '
        #use the R function if the parent of the dict is an R object.
        if type(self.data) in [str, unicode]:
            self.R('write.table('+self.data+',file="'+unicode(name)+'", quote = FALSE, col.names = NA, sep="'+sep+'")', wantType = 'NoConversion')
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
                self.status.setText(_('Can\'t write to a file'))
            
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


