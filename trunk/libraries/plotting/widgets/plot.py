"""
<name>aa</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI
from libraries.base.signalClasses.RVariable import RVariable as redRRVariable
from libraries.plotting.signalClasses.RPlotAttribute import RPlotAttribute as redRRPlotAttribute

from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
#from libraries.plotting.qtWidgets.graphicsView2 import graphicsView2 as redRGraphicsView
from libraries.base.qtWidgets.SearchDialog import SearchDialog

class plot(OWRpy): 
    globalSettingsList= ['commit']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.data = None
        self.RFunctionParam_x = ''
        self.plotAttributes = {}
        self.saveSettingsList = ['plotArea', 'data', 'RFunctionParam_x', 'plotAttributes']
        self.inputs.addInput('id0', 'x', redRRVariable, self.processx)

        self.R('data <- data.frame(a=c(1,2,3,4),b=c(3,4,5,6))')
        self.RFunctionParam_x = 'data'
        
        self.plotArea = graphicsView2(self.controlArea,label='Plot', displayLabel=False)
        self.plotArea.plot(query = 'data', data = 'data')
        self.commit = redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
        # b = widgetBox(self.controlArea)
        # widgetLabel(b,label='asdfasdf')
        # childern = self.controlArea.children()
        # for x in childern:
           # if isinstance(x, widgetState):
               # print x, x.__class__
               # print 'aaaa', x.__dict__
               # print x.getReportText('a')
        
    def processx(self, data):
        if data:
            self.data = data
            self.RFunctionParam_x=data.getData()
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.clearPlots()
    def commitFunction(self):
        #if self.RFunctionParam_y == '': return
        if self.RFunctionParam_x == '': return
        # injection = []
        # if str(self.RFunctionParam_main.text()) != '':
            # injection.append('main = "'+str(self.RFunctionParam_main.text())+'"')
        # if injection != []:
            # inj = ','+','.join(injection)
        # else: inj = ''
        
        self.plotArea.plot(query = str(self.RFunctionParam_x), data = self.RFunctionParam_x)
    
    def clearPlots(self):
        self.plotArea.clear()

        
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
import RSession, redREnviron, datetime, os, time
    

class graphicsView2(QGraphicsView, widgetState):
    def __init__(self, parent,label=None, displayLabel=True,includeInReports=True, name = '', data = None):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        widgetState.__init__(self,parent,label,includeInReports)
        
        QGraphicsView.__init__(self, self.controlArea)
        # if displayLabel:
            # self.controlArea = groupBox(parent,label=label, orientation='vertical')
        # else:
            # self.controlArea = widgetBox(parent,orientation='vertical')
        
        #self.controlArea = widgetBox(parent)
        self.topArea = widgetBox(self.controlArea,
        sizePolicy = QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum),includeInReports=False)
        self.middleArea = widgetBox(self.controlArea)
        self.bottomArea = widgetBox(self.controlArea,includeInReports=False)
        
        self.middleArea.layout().addWidget(self)  # place the widget into the parent widget
        scene = QGraphicsScene()
        self.setScene(scene)
        self.parent = parent
        self.data = data
        
        self.widgetSelectionRect = None
        self.mainItem = None
        self.query = ''
        self.function = 'plot'
        self.layers = []
        
        self.options = {
        'main': None
        ,'xlab': None
        ,'ylab': None
        ,'bg': None
        ,'cex.axis' : None
        ,'cex.lab' : None
        ,'cex.main' : None
        ,'cex.sub' : None
        ,'col' : None
        ,'colAxis' : None
        ,'col.main' : None
        ,'colSub' : None
        ,'family' : None
        ,'fg' : None
        ,'lty' : None
        ,'lwd' : None
        ,'legendNames' : None
        ,'legendLocation' : "'bottomleft'"
        ,'pch' : None
        ,'dheight' :4
        ,'dwidth' : 4
        }
        

        self.colorList = ['#000000', '#ff0000', '#00ff00', '#0000ff']
        self._replotAfterChange = True
        
        self.image = 'plot'+str(time.time()) # the base file name without an extension
        self.imageFileName = ''
        self.currentScale = 1

####################################################        
        self.graphicOptionsButton = button(self.topArea,label='Graphic Options',
        toggleButton = True,callback=self.displayGraphicOptions)
        self.graphicOptions = tabWidget(self.topArea)
        self.labels = self.graphicOptions.createTabPage('Labels')
        self.points = self.graphicOptions.createTabPage('Points/Lines')
        self.advanced = self.graphicOptions.createTabPage('Advanced')
        #self.graphicOptions.hide()
        
        firstTab = widgetBox(self.labels,orientation='horizontal')
        secondTab = widgetBox(self.points,orientation='horizontal')
        advancedTab = widgetBox(self.advanced,orientation='vertical')
        
        self.extrasLineEdit = lineEdit(advancedTab, label = 'Advanced plotting parameters', 
        toolTip = 'Add extra parameters to the main plot.\nPlease see documentation for more details about parameters.')
        
        self.onlyAdvanced = checkBox(advancedTab,
        buttons=['Only use the advanced options here'],
        label='advancedOnly',displayLabel=False)

        labelBox = groupBox(firstTab,label='Labels', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        self.mainTitle = lineEdit(labelBox,label='Main Title',
        textChangedCallBack=lambda : self.updateOptions(self.mainTitle,'main'))
        
        self.xLab = lineEdit(labelBox,label='X Axis Label',
        textChangedCallBack=lambda : self.updateOptions(self.xLab,'xlab'))
        
        self.yLab = lineEdit(labelBox,label='Y Axis Label',
        textChangedCallBack=lambda : self.updateOptions(self.yLab,'ylab'))
        
        fontBox = groupBox(firstTab,label='Fonts', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        fontColumnBox = widgetBox(fontBox,orientation='horizontal')
        fontColumn1 = widgetBox(fontColumnBox,orientation='vertical')
        fontColumn2 = widgetBox(fontColumnBox,orientation='vertical')
        self.fontCombo = comboBox(fontColumn1, items = ['serif', 'sans', 'mono'], ids=['serif', 'sans', 'mono'],
        label='Font Family', callback = lambda : self.updateOptions(self.fontCombo,'family'))
        
        self.plotFont = spinBox(fontColumn1, label = 'Plot Text Size', min = 1, max = 500, value = 100, 
        callback = lambda  :self.setFontMagnification(self.plotFont,'cex'))
        
        self.axisFont = spinBox(fontColumn1, label = 'Axis Text Size', min = 1, max = 500, value = 100, 
        callback = lambda  :self.setFontMagnification(self.axisFont,'cex.axis'))
        

        self.mainFont = spinBox(fontColumn2, label = 'Title Text Size', min = 1, max = 500, value = 100, 
        callback = lambda  :self.setFontMagnification(self.mainFont,'cex.main'))
        
        self.subFont = spinBox(fontColumn2, label = 'Subtitle Text Size', min = 1, max = 500, value = 100, 
        callback = lambda  :self.setFontMagnification(self.subFont,'cex.sub'))

        self.labFont = spinBox(fontColumn2, label = ' XY Label Text Size', min = 1, max = 500, value = 100, 
        callback = lambda  :self.setFontMagnification(self.labFont,'cex.lab'))
        

        colorBox = groupBox(firstTab,label='Colors', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        colorColumnBox = widgetBox(colorBox,orientation='horizontal')
        colorColumn1 = widgetBox(colorColumnBox,orientation='vertical')
        colorColumn2 = widgetBox(colorColumnBox,orientation='vertical')
      
        self.colorSeries = comboBox(colorColumn1,label='Generate Colors Series',orientation='vertical',
        items = ['rainbow','heat.colors','terrain.colors','topo.colors','cm.colors'],
        callback=self.generateColors)
        
        self.colorSeriesLen = spinBox(colorColumn1,label='Length of Series',min=1,max=500,value=1,
        callback=self.generateColors)
        self.customColors = button(colorColumn1,label='Custom Plot Colors',callback=self.setPlotColors)
                        
        self.titleColor = self.colorSelector(colorColumn2,label='Title Color',color='000000',
        callback=lambda: self.setColor(self.titleColor,'col.main'))
        
        self.subColor = self.colorSelector(colorColumn2,label='Subtitle Color',color='000000',
        callback=lambda: self.setColor(self.subColor,'col.sub'))
        
        self.labColor = self.colorSelector(colorColumn2,label='Subtitle Color',color='000000',
        callback=lambda: self.setColor(self.labColor,'col.lab'))

        self.axisColor = self.colorSelector(colorColumn2,label='Axis Color',color='000000',
        callback=lambda: self.setColor(self.axisColor,'col.axis'))
        
        lineBox = groupBox(secondTab,label='Lines', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
       
        self.linesListBox = listBox(lineBox, label = 'Line types', displayLabel=False,
        items = ['________', '- - - -', '........', '_._._._.', 
        '__ __ __', '__.__.__.'], callback = self.setLineTypes)
        self.linesListBox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.lineWidth = spinBox(lineBox,label='Line Width',min=1,max=50,value=1,
        callback = lambda  :self.updateOptions(self.lineWidth,'lwd'))
        
        pointBox = groupBox(secondTab,label='Points', orientation='vertical',
        sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        
        items = []
        for i in range(1,26):
            items.append(QListWidgetItem(QIcon(os.path.join(redREnviron.directoryNames['picsDir'],
            'R icon (%d).png' %i)),str(i)))
        
        for i in range(32,128):
            items.append('%s %d' % (chr(i), i))
            
        self.pointListBox = listBox(pointBox, label = 'Line types', displayLabel=False,
        items = items, callback = self.selectPointType)
        self.pointListBox.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # self.setPointType = lineEdit(pointBox,label='Points\n(comma delimited)',callback=self.setPointType)
        
        button(self.points,label='Update Graphic', alignment=Qt.AlignRight, callback=self.replot)
        button(self.labels,label='Update Graphic', alignment=Qt.AlignRight, callback=self.replot)
        

####################################################
        ### right click menu
        self.menu = QMenu(self)
        save = self.menu.addMenu('Save As')
        save.addAction('Bitmap')
        save.addAction('PDF')
        save.addAction('Post Script')
        save.addAction('JPEG')
        self.menu.addAction('Copy')
        self.menu.addAction('Fit In Window')
        self.menu.addAction('Zoom Out')
        self.menu.addAction('Zoom In')
        self.menu.addAction('Undock')
        self.menu.addAction('Redock')
        
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Red-R Graphics View' + name)
        self.dialog.setLayout(QHBoxLayout())
        
        self.standardImageType = 'svg'
        self.plotExactlySwitch = False ## a switch that can be activated to allow plotting exactly as the plot is sent, no function generation will be performed and all attribute alteration will be disabled
        QObject.connect(self.dialog, SIGNAL('finished(int)'), self.dialogClosed)
    

    ################################
    ####  Tab Actions         #####
    ################################
    def colorSelector(self,parent,label,color,callback=None):
        box = widgetBox(parent,orientation='horizontal')
        
        a = widgetLabel(box,label=label)
        a.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        a.setMaximumWidth(70)
        a.setMinimumWidth(70)
        # colorBox = widgetBox(box,sizePolicy = QSizePolicy(QSizePolicy.Maximum ,QSizePolicy.Minimum))
        # colorBox.setFixedSize(QSize(40,30))
        r = button(box,label='  ', callback=callback)
        box.setStyleSheet("QPushButton  { color: %s; background-color: %s }" % (color,color))
        return box
    def setColor(self,qtWidget,var):
        colorDialog = QColorDialog(self)
        self.options[var] = "'%s'" % str(colorDialog.getColor().name())
        colorDialog.hide()
        #print type(qtWidget), self.options[var]
        
        qtWidget.setStyleSheet("QPushButton  { color: %s; background-color: %s }" % (self.options[var],self.options[var]))
        #qtWidget.setStyleSheet("* { color: %s }" % self.options[var])
    
    def setPlotColors(self):
        colorDialog = colorListDialog(data = self.data)
        colorDialog.setColors(self.colorList)
        colorDialog.exec_()
        self.options['col'] = 'c('+','.join([str(a) for a in colorDialog.listOfColors])+')'
        self.colorList = colorDialog.listOfColors
        if self.options['col'] == 'c()':
           self.options['col'] = 'c("#FFFFFF")'
        colorDialog.hide()
        # if self._replotAfterChange:
            # self.replot()

    def generateColors(self):
        series = self.colorSeries.currentText()
        self.options['col'] = '%s(%d)' % (series,self.colorSeriesLen.value())
    
    def displayGraphicOptions(self):
        if self.graphicOptionsButton.isChecked():
            self.graphicOptions.show()
        else:
            self.graphicOptions.hide()
    
    def updateOptions(self,qtWidget,var):
        if isinstance(qtWidget,lineEdit):
            self.options[var] = "'%s'" % qtWidget.text()
        elif isinstance(qtWidget,comboBox):
            self.options[var] = "'%s'" % qtWidget.currentText()
        elif isinstance(qtWidget,spinBox):
            self.options[var] = qtWidget.value()
    
    def setFontMagnification(self,qtWidget,var):
        if float(qtWidget.value())/100 > 0:
            self.options[var] = float(qtWidget.value())/100
        else:
            self.options[var] = 1
    
    def setLineTypes(self):
        numbers = []
        for item in self.linesListBox.selectedItems():
            if item.text() == '________':
                numbers.append('1')
            elif item.text() == '- - - -':
                numbers.append('2')
            elif item.text() == '........':
                numbers.append('3')
            elif item.text() == '_._._._.':
                numbers.append('4')
            elif item.text() == '__ __ __':
                numbers.append('5')
            elif item.text() == '__.__.__.':
                numbers.append('6')
        print numbers
        
        self.options['lty'] = 'c('+','.join(numbers)+')'
    def selectPointType(self):
        points = []
        for item in self.pointListBox.selectedItems():
            a = str(item.text()).split(' ')
            if len(a) == 2:
                points.append(a[1])
            else:
                points.append(str(item.text()))
        
        self.options['pch'] = 'c('+','.join(points)+')'
    
    def setPointType(self):
        points = self.pointTypes.split(',')
        points = [ord(x.strip()) for x in points]
        
        self.options['pch'] = 'c('+','.join(points)+')'
        
        
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
    def _setParameters(self):
        inj = ''
        injection = []
        for k,v in self.options.items():
            if v:
                injection.append('%s = %s' % (k,v))
            

        inj = ','.join(injection)
        print inj

        return inj
    def _startRDevice(self, dwidth, dheight, imageType):
        if imageType not in ['svg', 'png', 'jpeg']:
            imageType = 'png'
        
        # fileName = redREnviron.directoryNames['tempDir']+'/plot'+str(self.widgetID).replace('.', '_')+'.'+imageType
        # fileName = fileName.replace('\\', '/')
        self.imageFileName = str(self.image).replace('\\', '/')+'.'+str(imageType)
        # print '###################### filename' , self.imageFileName
        if imageType == 'svg':
            self.require_librarys(['Cairo'])
            self.R('CairoSVG(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight)+', height = '+str(dheight)
                +')')
            
        if imageType == 'png':
            self.R('png(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight*100)+', height = '+str(dheight*100)
                +')')
        elif imageType == 'jpeg':
            self.R('jpeg(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight*100)+', height = '+str(dheight*100)
                +')')
                
    def plot(self, query, function = 'plot', dwidth=6, dheight=6, data = None, legend = False):
        ## performs a quick plot given a query and an imageType
        self.plotMultiple(query, function = function, dwidth = dwidth, dheight = dheight, layers = [], data = data, legend = legend)
            

    def plotMultiple(self, query, function = 'plot', dwidth = 6, dheight = 6, layers = [], 
    data = None, legend = False):
        ## performs plotting using multiple layers, each layer should be a query to be executed in RSession
        self.data = data
        self.function = function
        self.query = query
        self._startRDevice(dwidth, dheight, self.standardImageType)
        
        if not self.plotExactlySwitch:
            self.extras = self._setParameters()
            if str(self.extrasLineEdit.text()) != '':
                self.extras += ', '+str(self.extrasLineEdit.text())
            if self.extras != '':
                fullquery = '%s(%s, %s)' % (function, query, self.extras)
            else:
                fullquery = '%s(%s)' % (function, query)
        else:
            fullquery = self.query
        
        try:
            self.R(fullquery)
        
            
            print fullquery
            if len(layers) > 0:
                for l in layers:
                    self.R(l)
            if legend:
                self._setLegend()
            fileName = str(self.imageFileName)
            print fileName
        except Exception as inst:
            self.R('dev.off()') ## we still need to turn off the graphics device
            print 'Plotting exception occured'
            raise Exception(str(inst))
        self.R('dev.off()')
        self.clear()
        fileName = str(self.imageFileName)
        print fileName
        self.addImage(fileName)
        self.layers = layers
        self._dwidth = dwidth
        self._dheight = dheight
        self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
        
    def setExtrasLineEditEnabled(self, enabled = True):
        
        self.extrasLineEdit.enabled(enabled)
        if enabled:
            self.extrasLineEdit.show()
        else:
            self.extrasLineEdit.hide()
    def setReplotAfterChange(self, replot = True):
        if replot:
            self._replotAfterChange = True
        else:
            self._replotAfterChange = False
    def replot(self):
        if self.query == '': return ## no plot can be generated.
        self._startRDevice(self._dwidth, self._dheight, self.standardImageType)
        if not self.plotExactlySwitch:
            self.extras = self._setParameters()
            if str(self.extrasLineEdit.text()) != '':
                self.extras += ', '+str(self.extrasLineEdit.text())
            if self.extras != '':
                fullquery = '%s(%s, %s)' % (self.function, self.query, self.extras)
            else:
                fullquery = '%s(%s)' % (self.function, self.query)
        else:
            fullquery = self.query
        
        
        self.R(fullquery)
        if len(self.layers) > 0:
            for l in self.layers:
                self.R(l)
        self.R('dev.off()')
        self.clear()
        fileName = str(self.imageFileName)
        self.addImage(fileName)
    def printMe(self):
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print 'Printing Rejected'
            return
        painter = QPainter(printer)
        self.scene().render(painter)
        painter.end()    
    

    #########################
    ## R session functions ##
    #########################
    def R(self, query):
        return RSession.Rcommand(query = query)
    def require_librarys(self, libraries):
        return RSession.require_librarys(libraries)
        
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
    def saveAsPDF(self):
        print 'save as pdf'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".pdf", "PDF Document (.pdf)")
        if qname.isEmpty(): return
        qname = str(qname.toAscii())
        self.saveAs(str(qname), 'pdf')
    def saveAsPostScript(self):
        print 'save as post script'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".eps", "Post Script (.eps)")
        if qname.isEmpty(): return
        qname = str(qname.toAscii())
        self.saveAs(str(qname), 'ps')
    def saveAsBitmap(self):
        print 'save as bitmap'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".bmp", "Bitmap (.bmp)")
        if qname.isEmpty(): return
        qname = str(qname.toAscii())
        self.saveAs(str(qname), 'bmp')
    def saveAsJPEG(self):
        print 'save as jpeg'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".jpg", "JPEG Image (.jpg)")
        if qname.isEmpty(): return
        qname = str(qname.toAscii())
        self.saveAs(str(qname), 'jpeg')
    def backToParent(self):
        self.parent.layout().addWidget(self.controlArea)
        self.dialog.hide()
    def mousePressEvent(self, mouseEvent):
        
        if mouseEvent.button() == Qt.RightButton:
            # remove the selection rect
            if self.widgetSelectionRect:
                self.widgetSelectionRect.hide()
                self.widgetSelectionRect = None
            
            # show the action menu
            newCoords = QPoint(mouseEvent.globalPos())
            action = self.menu.exec_(newCoords)
            if action:
                if str(action.text()) == 'Copy':
                    self.toClipboard()
                elif str(action.text()) == 'Zoom Out':
                    self.scale(0.80, 0.80)
                elif str(action.text()) == 'Zoom In':
                    self.scale(1.50, 1.50)
                elif str(action.text()) == 'Undock':
                    ## want to undock from the widget and make an independent viewing dialog.
                    self.dialog.layout().addWidget(self.controlArea)
                    self.dialog.show()
                elif str(action.text()) == 'Redock':
                    self.parent.layout().addWidget(self.controlArea)
                    self.dialog.hide()
                elif str(action.text()) == 'Fit In Window':
                    print self.mainItem.boundingRect()
                    self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
                elif str(action.text()) == 'Bitmap':
                    self.saveAsBitmap()
                elif str(action.text()) == 'PDF':
                    self.saveAsPDF()
                elif str(action.text()) == 'Post Script':
                    self.saveAsPostScript()
                elif str(action.text()) == 'JPEG':
                    self.saveAsJPEG()
        else:
            self.mouseDownPosition = self.mapToScene(mouseEvent.pos())
            self.widgetSelectionRect = QGraphicsRectItem(QRectF(self.mouseDownPosition, self.mouseDownPosition), None, self.scene())
            self.widgetSelectionRect.setZValue(-100)
            self.widgetSelectionRect.show()
    def mouseMoveEvent(self, ev):
        point = self.mapToScene(ev.pos())

        if self.widgetSelectionRect:
            self.widgetSelectionRect.setRect(QRectF(self.mouseDownPosition, point))            

        self.scene().update()
    def mouseReleaseEvent(self, ev):
        point = self.mapToScene(ev.pos())
        if self.widgetSelectionRect:
            self.fitInView(self.widgetSelectionRect.rect(), Qt.KeepAspectRatio)
            self.widgetSelectionRect.hide()
            self.widgetSelectionRect = None
            
        self.scene().update()

    def returnImage(self):
        ## generate a rendering of the graphicsView and return the image
        
        size = self.scene().sceneRect().size()
        image = QImage(int(self.scene().width()), int(self.scene().height()), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        self.scene().render(painter)
        painter.end()
        return image
        
    def addImage(self, image, imageType = None):
        ## add an image to the view
        #self.image = os.path.abspath(image)
        #print self.image
        print 'Addign Image'
        if not self.scene():
            print 'loading scene'
            scene = QGraphicsScene()
            self.setScene(scene)
            print self.image
        if imageType == None:
            imageType = image.split('.')[-1]
        if imageType not in ['svg', 'png', 'jpeg']:
            self.clear()
            print imageType, 'Error occured'
            raise Exception, 'Image type specified is not a valid type for this widget.'
        if imageType == 'svg':
            self.convertSVG(str(os.path.join(redREnviron.directoryNames['tempDir'], image)).replace('\\', '/')) ## handle the conversion to glyph free svg
            mainItem = QGraphicsSvgItem(str(os.path.join(redREnviron.directoryNames['tempDir'], image)).replace('\\', '/'))
        elif imageType in ['png', 'jpeg']:
            mainItem = QGraphicsPixmapItem(QPixmap(os.path.join(redREnviron.directoryNames['tempDir'], image.replace('\\', '/'))))
        else:
            raise Exception, 'Image type %s not specified in a plotting method' % imageType
            #mainItem = QGraphicsPixmapItem(QPixmap(image))
        print mainItem
        self.scene().addItem(mainItem)
        self.mainItem = mainItem
        
        
    def getSettings(self):
        print '#################in getSettings'
        r = {'image':self.imageFileName, 'query':self.query, 'function':self.function, 'addSettings':self.extrasLineEdit.getSettings()}
        
        print r
        return r
    def loadSettings(self,data):
        # print '@@@@@@@@@@@@@@@@@in loadSettings'
        # print data
        
        self.query = data['query']
        self.function = data['function']
        self.extrasLineEdit.loadSettings(data['addSettings'])
        self.addImage(data['image'])
    def getReportText(self, fileDir):
        
        image = self.returnImage()
        image = image.scaled(1000,1000, Qt.KeepAspectRatio)
        imageFile = os.path.join(fileDir, self.image + '.png').replace('\\', '/')
        if not image.save(imageFile):
            print 'Error in saving image in graphicsView'
            return ''
        
        text = '.. image:: %s\n    :scale: 50%%\n\n' % imageFile
        
        return {self.widgetName:{'includeInReports':self.includeInReports,'text':text}}  
        
    def saveAs(self, fileName, imageType):
        if self.query == '': return
        if imageType == 'pdf':
            self.R('pdf(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'ps':
            self.R('postscript(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'bmp':
            self.R('bmp(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'jpeg':
            self.R('jpeg(file = \'%s\')' % fileName.replace('\\', '/'))
        
        if not self.plotExactlySwitch:
            self.extras = self._setParameters()
            if str(self.extrasLineEdit.text()) != '':
                self.extras += ', '+str(self.extrasLineEdit.text())
            if self.extras != '':
                fullquery = '%s(%s, %s)' % (self.function, self.query, self.extras)
            else:
                fullquery = '%s(%s)' % (self.function, self.query)
        else:
            fullquery = self.query
        self.R(fullquery)
        for l in self.layers:
            self.R(l)
        
        self.R('dev.off()')

    ###########
    ## Convert an SVG for pyqt
    ###########
    def convertSVG(self, file):
        print file
        dom = self._getsvgdom(file)
        #print dom
        self._switchGlyphsForPaths(dom)
        self._commitSVG(file, dom)
    def _commitSVG(self, file, dom):
        f = open(file, 'w')
        dom.writexml(f)
        f.close()
    def _getsvgdom(self, file):
        print 'getting DOM model'
        import xml.dom
        import xml.dom.minidom as mini
        f = open(file, 'r')
        svg = f.read()
        f.close()
        dom = mini.parseString(svg)
        return dom
    def _getGlyphPaths(self, dom):
        symbols = dom.getElementsByTagName('symbol')
        glyphPaths = {}
        for s in symbols:
            pathNode = [p for p in s.childNodes if 'tagName' in dir(p) and p.tagName == 'path']
            glyphPaths[s.getAttribute('id')] = pathNode[0].getAttribute('d')
        return glyphPaths
    def _switchGlyphsForPaths(self, dom):
        glyphs = self._getGlyphPaths(dom)
        use = self._getUseTags(dom)
        for glyph in glyphs.keys():
            #print glyph
            nl = self.makeNewList(glyphs[glyph].split(' '))
            u = self._matchUseGlyphs(use, glyph)
            for u2 in u:
                #print u2, 'brefore'
                self._convertUseToPath(u2, nl)
                #print u2, 'after'
            
    def _getUseTags(self, dom):
        return dom.getElementsByTagName('use')
    def _matchUseGlyphs(self, use, glyph):
        matches = []
        for i in use:
            #print i.getAttribute('xlink:href')
            if i.getAttribute('xlink:href') == '#'+glyph:
                matches.append(i)
        #print matches
        return matches
    def _convertUseToPath(self, use, strokeD):
        ## strokeD is a list of lists of strokes to make the glyph
        newD = self.nltostring(self.resetStrokeD(strokeD, use.getAttribute('x'), use.getAttribute('y')))
        use.tagName = 'path'
        use.removeAttribute('xlink:href')
        use.removeAttribute('x')
        use.removeAttribute('y')
        use.setAttribute('style', 'fill: rgb(0%,0%,0%); stroke-width: 0.5; stroke-linecap: round; stroke-linejoin: round; stroke: rgb(0%,0%,0%); stroke-opacity: 1;stroke-miterlimit: 10; ')
        use.setAttribute('d', newD)
    def makeNewList(self, inList):
        i = 0
        nt = []
        while i < len(inList):
            start = i + self.listFind(inList[i:], ['M', 'L', 'C', 'Z'])
            end = start + self.listFind(inList[start+1:], ['M', 'L', 'C', 'Z', '', ' '])
            nt.append(inList[start:end+1])
            i = end + 1
        return nt
    def listFind(self, x, query):
        for i in range(len(x)):
            if x[i] in query:
                return i
        return len(x)
    def resetStrokeD(self, strokeD, x, y):
        nsd = []
        for i in strokeD:
            nsd.append(self.resetXY(i, x, y))
        return nsd
    def resetXY(self, nl, x, y): # convert a list of strokes to xy coords
        nl2 = []
        for i in range(len(nl)):
            if i == 0:
                nl2.append(nl[i])
            elif i%2: # it's odd
                nl2.append(float(nl[i]) + float(x))
            elif not i%2: # it's even
                nl2.append(float(nl[i]) + float(y))
            else:
                print i, nl[i], 'error'
        return nl2
    def nltostring(self, nl): # convert a colection of nl's to a string
        col = []
        for l in nl:
            templ = []
            for c in l:
                templ.append(str(c))
            templ = ' '.join(templ)
            col.append(templ)
        return ' '.join(col)
        
    
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
        self.listOfColors = self.R('as.numeric(as.factor('+self.data+'$'+str(self.attsList.selectedItems()[0].text())+'))')
        
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
                col.setNamedColor(str(c))
                newItem = QListWidgetItem()
                newItem.setBackgroundColor(col)
                self.colorList.addItem(newItem)
        except:
            pass # it might happen that we can't show the colors that's not good but also not disasterous either.
    def processColors(self):
        self.listOfColors = []
        for item in self.colorList.items():
            self.listOfColors.append('"'+str(item.backgroundColor().name())+'"')
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

