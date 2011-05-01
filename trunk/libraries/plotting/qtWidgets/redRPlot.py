## redRGUI Graphics View.  A graphics view used for graphing R graphs, this should be as general as possible with an eye to some degree of automation in assignment of items.  

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *
from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit 
from libraries.base.qtWidgets.widgetLabel import widgetLabel 
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.spinBox import spinBox
from libraries.base.qtWidgets.textEdit import textEdit
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.graphicsView import graphicsView
import RSession, redREnviron, datetime, os, time, sys, redRi18n
_ = redRi18n.get_(package = 'base')
    

class redRPlot(graphicsView):
    def __init__(self, parent,label=None, displayLabel=True,includeInReports=True, name = '', data = None, prePlottingCallback = None):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        graphicsView.__init__(self, parent, label = label, displayLabel = displayLabel, includeInReports = includeInReports,
            name = name, data = data)
        ## __init__(self, parent,label=_('Graph'), displayLabel=True,includeInReports=True, name = '', data = None)
        
    ################################
    ####   Themes              #####
    ################################
        
        self.prePlottingCallback = prePlottingCallback
        self.options = {
            'device': {
                'imageType':'svg',
                'dpi':'75',
                'bgColor':'#FFFFFF',
                'dheight':400,
                'dwidth':400,
                'units':'px'},
            'main':{
                'col':None,
                'lty':None,
                'lwd':None,
                'pch':None,},
            'title':{
                'main':'',
                'xlab':'',
                'ylab':'',
                'col.main':'#000000',
                'col.sub':'#000000',
                'col.lab':'#000000'},
            'par':{
                'cex.axis':1,
                'cex.lab':1,
                'cex.main':1,
                'cex.sub':1,
                'cex':1,
                'col.axis':'#000000'}
            }
        
        
        self.optionWidgets = {}
        self.colorList = ['#000000', '#ff0000', '#00ff00', '#0000ff']       


    ################################
    ####   Setup Tabs          #####
    ################################
        self.graphicOptionsButton = button(self.topArea,label='Graphic Options',
        toggleButton = True,callback=self.displayGraphicOptions)
        self.graphicOptionsWidget = widgetBox(self.topArea)
        self.graphicOptions = tabWidget(self.graphicOptionsWidget)
        self.graphicOptions.setFixedHeight(180)
        hbox = widgetBox(self.graphicOptionsWidget,orientation='horizontal',alignment= Qt.AlignLeft)
        self.resizeCheck = checkBox(hbox,label='resize',displayLabel=False,buttons={'true':'Resize Image'},setChecked='true')
        button(hbox,label='Update Graphic', alignment=Qt.AlignLeft, callback=self.plotMultiple)
        

        self.labels = self.graphicOptions.createTabPage('Main')
        self.points = self.graphicOptions.createTabPage('Points/Lines')
        self.advanced = self.graphicOptions.createTabPage('Advanced')
        #self.graphicOptions.hide()
        
        firstTab = widgetBox(self.labels,orientation='horizontal',alignment=Qt.AlignLeft | Qt.AlignTop)
        secondTab = widgetBox(self.points,orientation='horizontal',alignment=Qt.AlignLeft | Qt.AlignTop)
        advancedTab = widgetBox(self.advanced,orientation='vertical',alignment=Qt.AlignLeft | Qt.AlignTop)
    ################################
    ####   Advanced Tabs       #####
    ################################
        
        self.optionWidgets['extrasLineEdit'] = lineEdit(advancedTab, label = 'Advanced plotting parameters', 
        toolTip = 'Add extra parameters to the main plot.\nPlease see documentation for more details about parameters.')
        
        self.optionWidgets['onlyAdvanced'] = checkBox(advancedTab,
        buttons=[(1, 'Only use the advanced options here')],
        label='advancedOnly',displayLabel=False)

    ################################
    ####   First Tabs          #####
    ################################
        imageBox = groupBox(firstTab,label='Image Properties', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        self.optionWidgets['imageType'] = comboBox(imageBox,label='Image Type',items=['svg','png'])
        self.optionWidgets['imageType'].setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        
        hbox = widgetBox(imageBox,orientation='horizontal')
        self.optionWidgets['dheight'] = spinBox(hbox, label = 'Height', min = 1, max = 5000, value = 400)
        self.optionWidgets['dwidth'] = spinBox(hbox, label = 'Width', min = 1, max = 5000, value = 400)
        hbox = widgetBox(imageBox,orientation='horizontal')
        self.optionWidgets['units'] = comboBox(hbox,label='units',items=[('px','Pixel'),('in','Inches')])
        self.optionWidgets['dpi'] = comboBox(hbox,label='DPI',items=['75','100','150','auto'],editable=True)
        
        
        labelBox = groupBox(firstTab,label='Labels', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        self.optionWidgets['mainTitle'] = lineEdit(labelBox,label='Main Title')
        self.optionWidgets['xLab'] = lineEdit(labelBox,label='X Axis Label')        
        self.optionWidgets['yLab'] = lineEdit(labelBox,label='Y Axis Label')

        
        fontBox = groupBox(firstTab,label='Sizes', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        fontColumnBox = widgetBox(fontBox,orientation='horizontal')
        fontColumn1 = widgetBox(fontColumnBox,orientation='vertical')
        fontColumn2 = widgetBox(fontColumnBox,orientation='vertical')
        
        #self.optionWidgets['fontCombo'] = comboBox(fontColumn1, items = ['serif', 'sans', 'mono'], label='Font Family')
        
        self.optionWidgets['lineWidth'] = spinBox(fontColumn1,label='Point/Line Size',decimals=2,min=1,max=50)
        self.optionWidgets['plotFont'] = spinBox(fontColumn1, label = 'Plot Text Size',decimals=2, min = 1, max = 50)
        self.optionWidgets['axisFont'] = spinBox(fontColumn1, label = 'Axis Text Size',decimals=2, min = 1, max = 50)
        self.optionWidgets['mainFont'] = spinBox(fontColumn2, label = 'Title Text Size',decimals=2, min = 1, max = 50)
        self.optionWidgets['subFont'] = spinBox(fontColumn2, label = 'Subtitle Text Size',decimals=2, min = 1, max = 50)
        self.optionWidgets['labFont'] = spinBox(fontColumn2, label = ' XY Label Text Size',decimals=2, min = 1, max = 50)
        
        colorBox = groupBox(firstTab,label='Colors', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        hbox = widgetBox(colorBox,orientation='horizontal')

        self.optionWidgets['colorSeries'] = comboBox(hbox,label='Generate Colors Series',orientation='vertical',
        items = ['select','rainbow','heat.colors','terrain.colors','topo.colors','cm.colors'])
        self.optionWidgets['colorSeriesLen'] = spinBox(hbox,label='Length of Series',displayLabel=False, min=0, max=500)
        hbox.layout().setAlignment(self.optionWidgets['colorSeriesLen'].controlArea, Qt.AlignBottom)
        
        self.optionWidgets['bgColor'] = ColorIcon(colorBox,label='Background')

        #self.optionWidgets['customColors'] = button(colorBox,label='Custom Plot Colors',callback=self.setPlotColors)

    
    ################################
    ####   Second Tabs         #####
    ################################
        colorBox2 = groupBox(secondTab,label='Colors', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        # colorColumnBox = widgetBox(colorBox2,orientation='horizontal')
        # colorColumn1 = widgetBox(colorColumnBox,orientation='vertical')
        # colorColumn2 = widgetBox(colorColumnBox,orientation='vertical')
      
         
        self.optionWidgets['titleColor'] = ColorIcon(colorBox2,label='Title')
        self.optionWidgets['subColor'] = ColorIcon(colorBox2,label='Subtitle')
        self.optionWidgets['labColor'] = ColorIcon(colorBox2,label='Subtitle')
        self.optionWidgets['axisColor'] = ColorIcon(colorBox2,label='Axis')
        
        lineBox = groupBox(secondTab,label='Lines', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
       
        self.optionWidgets['linesListBox'] = listBox(lineBox, label = 'Line types', displayLabel=False,
        selectionMode = QAbstractItemView.ExtendedSelection,
        items = [(1,'________'), (2,'- - - -'), (3,'........'), (4,'_._._._.'), 
        (5,'__ __ __'), (6,'__.__.__.')])
        
        
        
        pointBox = groupBox(secondTab,label='Points', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        items = []
        for i in range(1,26):
            items.append((i-1,QListWidgetItem(QIcon(os.path.join(redREnviron.directoryNames['picsDir'],
            'R icon (%d).png' %i)),'')))
        
        for i in range(32,128):
            items.append((i-1,'%s' % (chr(i))))
            
        self.optionWidgets['pointListBox'] = listBox(pointBox, label = 'Line types', displayLabel=False,
        selectionMode = QAbstractItemView.ExtendedSelection, items = items)
        


        self.setTheme(self.options)
    ################################
    ### right click menu     #######
    ################################
        self.menu = QMenu(self)
        save = self.menu.addMenu('Save As')
        save.addAction('Bitmap')
        save.addAction('PDF')
        save.addAction('Post Script')
        save.addAction('JPEG')
        if sys.platform == 'win32':
            save.addAction('WMF')
        self.menu.addAction('Copy')
        self.menu.addAction('Fit In Window')
        self.menu.addAction('Zoom Out')
        self.menu.addAction('Zoom In')
        #self.menu.addAction('Undock')
        #self.menu.addAction('Redock')
        
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Red-R Graphics View' + name)
        self.dialog.setLayout(QHBoxLayout())
        
        self.standardImageType = 'svg'
        QObject.connect(self.dialog, SIGNAL('finished(int)'), self.dialogClosed)




    ################################
    #### Plot Option Widgets   #####
    ################################
    
    def displayGraphicOptions(self):
        if self.graphicOptionsButton.isChecked():
            self.graphicOptionsWidget.show()
        else:
            self.graphicOptionsWidget.hide()
    
    def setTheme(self,options = None):
        if options != None:
            self.options = options
        
        ## device options
        dos = self.options['device']
        if 'imageType' in dos.keys():
            self.optionWidgets['imageType'].setCurrentId(dos['imageType'])
        if 'dpi' in dos.keys():
            self.optionWidgets['dpi'].setCurrentId(dos['dpi'])
        if 'bgColor' in dos.keys():
            self.optionWidgets['bgColor'].setColor(dos['bgColor'])
        if 'dheight' in dos.keys():
            self.optionWidgets['dheight'].setValue(dos['dheight'])
        if 'dwidth' in dos.keys():
            self.optionWidgets['dwidth'].setValue(dos['dwidth'])
        if 'units' in dow.keys():
            self.optionWidgets['units'].setCurrentId(dos['units'])
        
        ## main options
        mos = self.options['main']
        if 'colorSeries' in mos.keys():
            self.optionWidgets['colorSeries'].setCurrentId(mos['col'])
        if 'lty' in mos.keys():
            self.optionWidgets['linesListBox'].setSelectedIds(mos['lty'])
        if 'lwd' in mos.keys() and mos['lwd']:
            self.optionWidgets['lineWidth'].setValue(mos['lwd'])
        if 'pch' in mos.keys():
            self.optionWidgets['pointListBox'].setSelectedIds(mos['pch'])
            
        ## title options
        
        tos = self.options['title']
        if 'main' in tos.keys():
            self.optionWidgets['mainTitle'].setText(tos['main'])
        if 'xlab' in tos.keys():
            self.optionWidgets['xLab'].setText(tos['xlab'])
        if 'ylab' in tos.keys():
            self.optionWidgets['yLab'].setText(tos['ylab'])
        if 'col.main' in tos.keys():
            self.optionWidgets['titleColor'].setColor(tos['col.main'])
        if 'col.sub' in tos.keys():
            self.optionWidgets['subColor'].setColor(tos['col.sub'])
        if 'col.lab' in tos.keys():
            self.optionWidgets['labColor'].setColor(tos['col.lab'])
        
        ## par options
        pos = self.options['par']
        if 'cex.axis' in pos.keys():
            self.optionWidgets['axisFont'].setValue(pos['cex.axis'])
        if 'cex.lab' in pos.keys():
            self.optionWidgets['labFont'].setValue(pos['cex.lab'])
        if 'cex' in pos.keys():
            self.optionWidgets['plotFont'].setValue(pos['cex'])
        if 'cex.main' in pos.keys():
            self.optionWidgets['mainFont'].setValue(pos['cex.main'])
        if 'cex.sub' in pos.keys():
            self.optionWidgets['subFont'].setValue(pos['cex.sub'])
        if 'col.axis' in pos.keys():
            self.optionWidgets['axisColor'].setColor(pos['col.axis'])
        
        
        
    ################################
    ####  Tab Actions         #####
    ################################
    
    def setPlotColors(self):
        colorDialog = colorListDialog(data = self.data)
        colorDialog.setColors(self.colorList)
        colorDialog.exec_()
        self.options['col']['value'] = 'c('+','.join([unicode(a) for a in colorDialog.listOfColors])+')'
        self.colorList = colorDialog.listOfColors
        if self.options['col']['value'] == 'c()':
           self.options['col']['value'] = 'c("#FFFFFF")'
        colorDialog.hide()

    def setColorSeries(self,options):
        self.optionWidgets['colorSeries'].setCurrentId(options['series'])
        self.optionWidgets['colorSeriesLen'].setValue(options['seriesLen'])
        
    def getColorSeries(self,options):
        #print options
        if self.optionWidgets['colorSeries'].currentId() == 'select':
            options['value'] = None
        else:
            series = self.optionWidgets['colorSeries'].currentId()
            options['value'] = '%s(%d)' % (series,self.optionWidgets['colorSeriesLen'].value())
    
    def setOptions(self,options):
        if 'default' not in options.keys() or options['default'] == None: return
        
        qtWidget = self.optionWidgets[options['qtWidget']]
        if isinstance(qtWidget,ColorIcon):
            qtWidget.color = options['default']
            qtWidget.updateColor()
        elif isinstance(qtWidget,lineEdit):
            qtWidget.setText(options['default'])
        elif isinstance(qtWidget,comboBox):
            qtWidget.setCurrentId(options['default'])
        elif isinstance(qtWidget,spinBox):
            qtWidget.setValue(options['default'])
            
    def updateOptions(self,options):
        qtWidget = self.optionWidgets[options['qtWidget']]
        
        if isinstance(qtWidget,ColorIcon):
            options['value'] = "'%s'" % self.optionWidgets[options['qtWidget']].color
        if isinstance(qtWidget,lineEdit):
            #if qtWidget.text() =='': return
            try:
                options['value'] = "%f" % float(qtWidget.text())
            except:
                options['value'] = "'%s'" % qtWidget.text()
        elif isinstance(qtWidget,comboBox):
            if qtWidget.currentId() =='': 
                options['value'] = None
                return 
            try:
                options['value'] = "%f" % float(qtWidget.currentId())
            except:
                options['value'] = "'%s'" % qtWidget.currentId()
                
        elif isinstance(qtWidget,spinBox):
            if qtWidget.value() =='':
                options['value'] = None
                return 

            options['value'] = qtWidget.value()
    
    def getLineTypes(self):
        qtWidget = self.optionWidgets['linesListBox']
        return 'c('+','.join([unicode(x) for x in qtWidget.selectedIds()])+')'
        
    def setLineTypes(self):
        if 'default' not in options.keys() or options['default'] == None: return
        qtWidget = self.optionWidgets[options['qtWidget']]
        qtWidget.setSelectedIds(options['default'])
        
    ##############################
    ### Plotting #################\
    ##############################
    def _setLegend(self):
        ## we want to make a legend that will appear on the plot.  legend(x, y = NULL, legend, fill = NULL, col = par("col"),
                   # border="black", lty, lwd, pch,
                   # angle = 45, density = NULL, bty = "o", bg = par("bg"),
                   # box.lwd = par("lwd"), box.lty = par("lty"), box.col = par("fg"),
                   # pt.bg = NA, cex = 1, pt.cex = cex, pt.lwd = lwd,
                   # xjust = 0, yjust = 1, x.intersp = 1, y.intersp = 1,
                   # adj = c(0, 0.5), text.width = NULL, text.col = par("col"),
                   # merge = do.lines && has.pch, trace = FALSE,
                   # plot = TRUE, ncol = 1, horiz = FALSE, title = NULL,
                   # inset = 0, xpd, title.col = text.col)
        if not self._legendNames:
            self.parent.status.setText('No legend names specified. Can\'t make the legend')
        function = 'legend(x=\''+self._legendLocation+'\', legend = '+self._legendNames
        if self._col:
            function += ', col = '+self._col
        if self._lty:
            function += ', lty = '+self._lty
        if self._lwd:
            function += ', lwd = '+self._lwd
        if self._pch:
            function += ', pch = '+self._pch
        function += ')'
        self.R(function)
    def setLegendNames(self, parameter):
        ## sets the legend to plot the names as the set parameter.  This can come from either a call to the widget through it's own interface or through the widget.
        self._legendNames = parameter
    def _setLegendLocation(self, location):
        self._legendLocation = location
    def _getParameters(self):
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.options)

        injection = {'title':[
            '%s = \'%s\'' % ('main', self.optionWidgets['mainTitle'].text()),
            '%s = \'%s\'' % ('xlab', self.optionWidgets['xLab'].text()),
            '%s = \'%s\'' % ('ylab', self.optionWidgets['yLab'].text()),
            '%s = \'%s\'' % ('col.main', self.optionWidgets['titleColor'].color),
            '%s = \'%s\'' % ('col.sub', self.optionWidgets['subColor'].color),
            '%s = \'%s\'' % ('col.lab', self.optionWidgets['labColor'].color)
            ],
                    'par':[
            '%s = %s' % ('cex.axis', self.optionWidgets['axisFont'].value()),
            '%s = %s' % ('cex.lab', self.optionWidgets['labFont'].value()),
            '%s = %s' % ('cex', self.optionWidgets['plotFont'].value()),
            '%s = %s' % ('cex.main', self.optionWidgets['mainFont'].value()),
            '%s = %s' % ('cex.sub', self.optionWidgets['subFont'].value()),
            '%s = \'%s\'' % ('col.axis', self.optionWidgets['axisColor'].color)
            ]}
         
        return injection            
    def prePlottingCommands(self):
        if 1 in self.optionWidgets['onlyAdvanced'].getCheckedIds():
            return
        if self.prePlottingCallback:
            self.prePlottingCallback()
            return
        parOpts = [
            '%s = %s' % ('cex.axis', self.optionWidgets['axisFont'].value()),
            '%s = %s' % ('cex.lab', self.optionWidgets['labFont'].value()),
            '%s = %s' % ('cex', self.optionWidgets['plotFont'].value()),
            '%s = %s' % ('cex.main', self.optionWidgets['mainFont'].value()),
            '%s = %s' % ('cex.sub', self.optionWidgets['subFont'].value()),
            '%s = \'%s\'' % ('col.axis', self.optionWidgets['axisColor'].color)
            ]
        self.R('par(%s)' % ','.join(parOpts))
    def processQuery(self, query):
        if 1 in self.optionWidgets['onlyAdvanced'].getCheckedIds():
            return query
        widgetPars = []
        if self.getLineTypes() != 'c()':
            widgetPars.append('%s = %s' % ('lty', self.getLineTypes()))
        
        widgetPars.append('%s = %s' % ('lwd', self.optionWidgets['lineWidth'].value()))
        if len(self.optionWidgets['pointListBox'].selectedIds()) > 0:
            widgetPars.append('%s = c(%s)' % ('pch', ','.join([str(i) for i in self.optionWidgets['pointListBox'].selectedIds()])))
        # color series temporarily disabled...
        return '%s, %s' % (query, ','.join(widgetPars))
    def plot(self, query, function = 'plot', parameters=None,data=None):
        ## performs a quick plot given a query and an imageType
        self.data = data
        self.function = function
        self.layers = []
        self.plotMultiple(self, self.processQuery(query), function = function, dwidth = self.optionWidgets['dwidth'].value(), dheight = self.optionWidgets['dheight'].value(), layers = [], data = None, legend = False)
    
    def plotMultiple(self, query, function = 'plot', dwidth = 5, dheight = 5, layers = [], data = None, legend = False):
        self.data = data
        self.function = function
        self.query = self.processQuery(query)
        
        self._dwidth = self.optionWidgets['dwidth'].value()
        
        self._dheight = self.optionWidgets['dheight'].value()
        self._startRDevice(self.optionWidgets['imageType'].currentId())
        self.prePlottingCommands() ## reimplemented in child classes
        self._plot(self.query, function)
        titleOpts = [
            '%s = \'%s\'' % ('main', self.optionWidgets['mainTitle'].text()),
            '%s = \'%s\'' % ('xlab', self.optionWidgets['xLab'].text()),
            '%s = \'%s\'' % ('ylab', self.optionWidgets['yLab'].text()),
            '%s = \'%s\'' % ('col.main', self.optionWidgets['titleColor'].color),
            '%s = \'%s\'' % ('col.sub', self.optionWidgets['subColor'].color),
            '%s = \'%s\'' % ('col.lab', self.optionWidgets['labColor'].color)
            ]
        self._plotLayers(layers + ['title(%s)' % ','.join(titleOpts)])
        self._plotLegend(legend)
        self.R('dev.off()', wantType = 'NoConversion')
        self.clear()
        fileName = unicode(self.imageFileName)
        self.addImage(fileName)
        self.layers = layers
        self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
        
        
    def resizeEvent(self,ev):
        if self.mainItem and 'true' in self.resizeCheck.getCheckedIds():
            self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
        
    def printMe(self):
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print 'Printing Rejected'
            return
        painter = QPainter(printer)
        self.scene().render(painter)
        painter.end()    
    
    ##########################
    ## Interaction Functions #
    ##########################
    def clear(self):
        if self.scene():
            self.scene().clear()
        else:
            print 'loading scene'
            scene = QGraphicsScene()
            self.setScene(scene)
    def dialogClosed(self, int):
        self.backToParent()

    def toClipboard(self):
        QApplication.clipboard().setImage(self.returnImage())
    
    def backToParent(self):
        self.parent.layout().addWidget(self.controlArea)
        self.dialog.hide()

    def returnImage(self):
        ## generate a rendering of the graphicsView and return the image
        
        size = self.scene().sceneRect().size()
        image = QImage(int(self.scene().width()), int(self.scene().height()), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        self.scene().render(painter)
        painter.end()
        return image

        
    def getSettings(self):
        #print '#################in getSettings'
        r = {'image':self.imageFileName, 'query':self.query, 'function':self.function}
        
        #print r
        return r
    def loadSettings(self,data):
        self.query = self.safeLoad(data, 'query', '')
        self.function = self.safeLoad(data, 'function', 'plot')
        self.addImage(self.safeLoad(data, 'image', self.imageFileName))
    def getReportText(self, fileDir):
        
        image = self.returnImage()
        image = image.scaled(1000,1000, Qt.KeepAspectRatio)
        imageFile = os.path.join(fileDir, self.image + '.png').replace('\\', '/')
        if not image.save(imageFile):
            print 'Error in saving image in graphicsView'
            return ''
        
        text = '.. image:: %s\n    :scale: 50%%\n\n' % imageFile
        
        return {self.widgetName:{'includeInReports':self.includeInReports,'text':text}}  
        

    
class colorListDialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical', title = 'Color List Dialog', data = ''):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        
        self.listOfColors = []
        self.controlArea = widgetBox(self)
        mainArea = widgetBox(self.controlArea, 'horizontal')
        leftBox = widgetBox(mainArea)
        rightBox = widgetBox(mainArea)
        ## GUI
        
        # color list
        self.colorList = listBox(leftBox, label = 'Color List')
        button(leftBox, label = 'Add Color', callback = self.addColor)
        button(leftBox, label = 'Remove Color', callback = self.removeColor)
        button(leftBox, label = 'Clear Colors', callback = self.colorList.clear)
        button(mainArea, label = 'Finished', callback = self.accept)
        # attribute list
        self.attsList = listBox(rightBox, label = 'Data Parameters', callback = self.attsListSelected)
        if data:
            names = self.R('names('+data+')')
            print names
            self.attsList.update(names)
        self.data = data
    def attsListSelected(self):
        ## return a list of numbers coresponding to the levels of the data selected.
        self.listOfColors = self.R('as.numeric(as.factor('+self.data+'$'+unicode(self.attsList.selectedItems()[0])+'))')
        
    def addColor(self):
        colorDialog = QColorDialog(self)
        color = colorDialog.getColor()
        colorDialog.hide()
        newItem = QListWidgetItem()
        newItem.setBackgroundColor(color)
        self.colorList.addItem(newItem)
        
        self.processColors()
    def removeColor(self):
        for item in self.colorList.selectedItems():
            self.colorList.removeItemWidget(item)
            
        self.processColors()
    def setColors(self, colorList):
        self.colorList.clear()
        try:
            for c in colorList:
                col = QColor()
                col.setNamedColor(unicode(c))
                newItem = QListWidgetItem()
                newItem.setBackgroundColor(col)
                self.colorList.addItem(newItem)
        except:
            pass # it might happen that we can't show the colors that's not good but also not disasterous either.
    def processColors(self):
        self.listOfColors = []
        for item in self.colorList.items():
            self.listOfColors.append('"'+unicode(item.backgroundColor().name())+'"')
    def R(self, query):
        return RSession.Rcommand(query = query)

class dialog(QDialog):
    def __init__(self, parent, layout = 'vertical',title=None):
        QDialog.__init__(self,parent)
        self.ltys = []
        self.parent = parent
        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())


class ColorIcon(QToolButton):
    def __init__(self, parent, label):
        box = widgetBox(parent,orientation='horizontal')       
        a = widgetLabel(box,label=label)
        QToolButton.__init__(self, box)
        box.layout().addWidget(self)
        # if not color:
        self.color = '#000000'
        # else:
            # self.color = color
            
        self.setMaximumSize(20,20)
        self.connect(self, SIGNAL("clicked()"), self.showColorDialog)
        # self.updateColor()

    def updateColor(self):
        pixmap = QPixmap(16,16)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(QPen(QColor(self.color)))
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(0, 0, 16, 16);
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(16,16))

    def setColor(self, color):
        self.color = color
        self.updateColor()
    def drawButtonLabel(self, painter):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(QColor(self.color)))
        painter.drawRect(3, 3, self.width()-6, self.height()-6)

    def showColorDialog(self):
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.updateColor()
            self.repaint()
