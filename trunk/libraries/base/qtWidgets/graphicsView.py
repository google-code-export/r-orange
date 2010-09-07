## redRGUI Graphics View.  A graphics view used for graphing R graphs, this should be as general as possible with an eye to some degree of automation in assignment of items.  

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *
from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.lineEdit import lineEdit 
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.spinBox import spinBox
import RSession, redREnviron, datetime, os, time
class graphicsView(QGraphicsView, widgetState):
    def __init__(self, parent, name = ''):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        QGraphicsView.__init__(self, parent)
        self.controlArea = widgetBox(parent)
        self.topArea = widgetBox(self.controlArea)
        self.middleArea = widgetBox(self.controlArea)
        self.bottomArea = widgetBox(self.controlArea)
        self.middleArea.layout().addWidget(self)  # place the widget into the parent widget
        scene = QGraphicsScene()
        self.setScene(scene)
        self.parent = parent
        self.widgetSelectionRect = None
        self.mainItem = None
        self.query = ''
        self.function = 'plot'
        self.layers = []
        self._bg = None
        self._cex = None
        self._cexAxis = None
        self._cexLab = None
        self._cexMain = None
        self._cexSub = 1
        self._col = None
        self._colAxis = None
        self._colMain = None
        self._colSub = None
        self._family = None
        self._fg = None
        self._lty = None
        self._lwd = None
        self._replotAfterChange = True
        self._dheight = 6
        self._dwidth = 6
        self.image = 'plot'+str(time.time()) # the base file name without an extension
        self.imageFileName = ''
        self.currentScale = 1
        
        ## bottom menu bar
        self.menuBar = QMenuBar(self.bottomArea)
        self.bottomArea.layout().addWidget(self.menuBar)
        
        self.menuParameters = QMenu('Parameters', self)
        colors = self.menuParameters.addMenu('Colors')
        colors.addAction('Set Plotting Colors', self.setPlotColors)
        colors.addAction('Set Axis Colors', self.setAxisColors)
        colors.addAction('Set Label Colors', self.setLabelColors)
        colors.addAction('Set Main Title Color', self.setTitleColors)
        colors.addAction('Set Subtitle Color', self.setSubtitleColors)
        colors.addAction('Set Forground Color', self.setForgroundColors)
        colors.addAction('Set Background Color', self.setBackgroundColors)
        font = self.menuParameters.addMenu('Font')
        ffa = font.addMenu('Set Font Family')
        
        fontComboAction = QWidgetAction(font)
        self.fontCombo = comboBox(None, items = ['serif', 'sans', 'mono'], 
            #'HersheySerif', 'HersheySans', 'HersheyScript',
            #'HersheyGothicEnglish', 'HersheyGothicGerman', 'HersheyGothicItalian', 'HersheySymbol', 'HersheySansSymbol'], 
            callback = self.setFontFamily)
        fontComboAction.setDefaultWidget(self.fontCombo)
        ffa.addAction(fontComboAction)
        #font.addAction('Set Font Magnification', self.setFontMagnification)
        wb = widgetBox(None)
        self.fontMag = spinBox(wb, label = 'Font Magnification:', min = 0, max = 500, value = 100) #, callback = self.setFontMagnification)
        QObject.connect(self.fontMag, SIGNAL('editingFinished ()'), self.setFontMagnification) ## must define ourselves because the function calls the attribute and this causes an error in Qt
        magAction = QWidgetAction(font)
        magAction.setDefaultWidget(wb)
        font.addAction(magAction)
        
        self.menuParameters.setToolTip('Set the parameters of the rendered image.\nThese parameters are standard graphics parameters which may or may not be applicable or rendered\ndepending on the image type and the settings of the plotting widget.')
        fa = font.addMenu('Font Attributes')
        lines = self.menuParameters.addMenu('Lines')
        lines.addAction('Set Line Type', self.setLineType)
        lines.addAction('Set Line Width', self.setLineWidth)
        points = self.menuParameters.addMenu('Points')
        points.addAction('Set Point Characters', self.setPointCharacters)
        
        self.imageParameters = QMenu('Image', self)
        type = self.imageParameters.addMenu('Type')
        type.addAction('Set Image Vector Graphics', self.setImageSVG).setToolTip('Renders the image using vector graphics which are scaleable and zoomable,\nbut may not show all graphical options such as forground color changes.')
        type.addAction('Set Image Bitmap Graphics', self.setImagePNG).setToolTip('Redners the image using bitmap graphics which will become distorted on zooming,\nbut will show all graphical options.')
        #type.addAction('Set Image JPEG', self.setImageJPEG)
        type.setToolTip('Changes the plotting type of the rendered image.\nDifferent image types may enable or disable certain graphics parameters.')
        
        self.fileParameters = QMenu('File', self)
        save = self.fileParameters.addMenu('Save')
        save.addAction('Bitmap', self.saveAsBitmap)
        save.addAction('PDF', self.saveAsPDF)
        save.addAction('Post Script', self.saveAsPostScript)
        save.addAction('JPEG', self.saveAsJPEG)
        
        self.menuBar.addMenu(self.fileParameters)
        self.menuBar.addMenu(self.menuParameters)
        self.menuBar.addMenu(self.imageParameters)
        
        ### lower Line Edit
        self.extrasLineEdit = lineEdit(self.bottomArea, label = 'Advanced plotting parameters', 
            toolTip = 'Add extra parameters to the main plot.\nPlease see documentation for more details about parameters.', callback = self.replot)
        
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
        
    ################################
    ####  Menu Actions         #####
    ################################
    def setImageSVG(self):
        self.setStandardImageType('svg')
    def setImagePNG(self):
        self.setStandardImageType('png')
    def setImageJPEG(self):
        self.setStandardImageType('jpeg')
    def setStandardImageType(self, it):
        self.standardImageType = it
    def setPlotColors(self):
        colorDialog = colorListDialog()
        colorDialog.exec_()
        colorDialog.processColors() ## we process one last time to get all of the colors in case we missed some.
        self._col = 'c("'+'","'.join(colorDialog.listOfColors)+'")'
        if self._col == 'c("")':
            self._col = 'c("#FFFFFF")'
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setAxisColors(self):
        colorDialog = QColorDialog(self)
        self._colAxis = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setBackgroundColors(self):
        colorDialog = QColorDialog(self)
        self._bg = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setExtrasLineEditEnabled(self, enabled):
        if enabled:
            self.extrasLineEdit.show()
        else:
            self.extrasLineEdit.hide()
    def setFontFamily(self):
        self._family = str(self.fontCombo.currentText())
        if self._replotAfterChange:
            self.replot()
    def setFontMagnification(self):
        print self.fontMag.value()
        print float(self.fontMag.value())/100
        if float(self.fontMag.value())/100 > 0:
            self._cex = float(self.fontMag.value())/100
        else:
            self._cex = 1
        if self._replotAfterChange:
            self.replot()
    def setForgroundColors(self):
        colorDialog = QColorDialog(self)
        self._forgroundColor = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setLabelColors(self):
        colorDialog = QColorDialog(self)
        self._labelColors = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setTitleColors(self):
        colorDialog = QColorDialog(self)
        self._titleColors = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setSubtitleColors(self):
        colorDialog = QColorDialog(self)
        self._subtitleColors = str(colorDialog.getColor().name())
        colorDialog.hide()
        if self._replotAfterChange:
            self.replot()
    def setLineType(self):
        pass
        if self._replotAfterChange:
            self.replot()
    def setLineWidth(self):
        pass
        if self._replotAfterChange:
            self.replot()
    def setPointCharacters(self):
        ### set a list of point characters to be plotted.  these should be of the form of either a character or an integer for plotting
        
        if self._replotAfterChange:
            self.replot()
            
    #########################
    ## R session functions ##
    #########################
    def R(self, query):
        RSession.Rcommand(query = query)
    def require_librarys(self, libraries):
        return RSession.require_librarys(libraries)
        
    ##########################
    ## Interaction Functions #
    ##########################
    def clear(self):
        self.scene().clear()
        
    def toClipboard(self):
        QApplication.clipboard().setImage(self.returnImage())
    def saveAsPDF(self):
        print 'save as pdf'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".pdf", "PDF Document (.pdf)")
        if qname.isEmpty(): return
        self.saveAs(str(qname), 'pdf')
    def saveAsPostScript(self):
        print 'save as post script'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".eps", "Post Script (.eps)")
        if qname.isEmpty(): return
        self.saveAs(str(qname), 'ps')
    def saveAsBitmap(self):
        print 'save as bitmap'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".bmp", "Bitmap (.bmp)")
        if qname.isEmpty(): return
        self.saveAs(str(qname), 'bmp')
    def saveAsJPEG(self):
        print 'save as jpeg'
        qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".jpg", "JPEG Image (.jpg)")
        if qname.isEmpty(): return
        self.saveAs(str(qname), 'jpeg')
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
            mainItem = QGraphicsSvgItem(os.path.join(redREnviron.directoryNames['tempDir'], image.replace('\\', '/')))
        elif imageType in ['png', 'jpeg']:
            mainItem = QGraphicsPixmapItem(QPixmap(os.path.join(redREnviron.directoryNames['tempDir'], image.replace('\\', '/'))))
        else:
            raise Exception, 'Image type %s not specified in a plotting method' % imageType
            #mainItem = QGraphicsPixmapItem(QPixmap(image))
        print mainItem
        self.scene().addItem(mainItem)
        self.mainItem = mainItem
        
        
    def getSettings(self):
        
        r = {'image':self.imageFileName, 'query':self.query, 'function':self.function, 'addSettings':self.extrasLineEdit.getSettings()}
        
        # print r
        return r
    def loadSettings(self,data):
        print data
        
        self.query = data['query']
        self.function = data['function']
        self.extrasLineEdit.loadSettings(data['addSettings'])
        self.addImage(data['image'])
    def getReportText(self, fileDir):
        #return ''
        pass
        
    def saveAs(self, fileName, imageType):
        if self.query == '': return
        if imageType == 'pdf':
            self.R('pdf(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'ps':
            self.R('postscript(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'bit':
            self.R('bmp(file = \'%s\')' % fileName.replace('\\', '/'))
        elif imageType == 'jpeg':
            self.R('jpeg(file = \'%s\')' % fileName.replace('\\', '/'))
        
        query = '%s(%s, %s)' % (self.function, self.query, self.extras)
        self.R(query)
        for l in self.layers:
            self.R(l)
        
        self.R('dev.off()')
    ##############################
    ### Plotting #################\
    ##############################
    def _setParameters(self):
        inj = ''
        injection = []
        if self._bg:
            injection.append('bg = \'%s\'' % self._bg)
        if self._cex:
            injection.append('cex = %s' % self._cex)
        if self._cexAxis:
            injection.append('cex.axis = %s' % self._cexAxis)
        if self._cexLab:
            injection.append('cex.lab = %s' % self._cexLab)
        if self._cexMain:
            injection.append('cex.main = %s' % self._cexMain)
        if self._cexSub:
            injection.append('cex.sub = %s' % self._cexSub)
        if self._col:
            injection.append('col = %s' % self._col)
        if self._colAxis:
            injection.append('col.axis = \'%s\'' % self._colAxis)
        if self._colMain:
            injection.append('col.main = \'%s\'' % self._colMain)
        if self._colSub:
            injection.append('col.sub = \'%s\'' % self._colSub)
        if self._family:
            injection.append('family = \'%s\'' % self._family)
        if self._fg:
            injection.append('fg = \'%s\'' % self._fg)
        if self._lty:
            injection.append('lty = %s' % self._lty)
        if self._lwd:
            injection.append('lwd = %s' % self._lwd)
        inj = ','.join(injection)
        print inj
        #self.R('par('+inj+')')
        return inj
    def _startRDevice(self, dwidth, dheight, imageType):
        if imageType not in ['svg', 'png', 'jpeg']:
            imageType = 'svg'
        
        # fileName = redREnviron.directoryNames['tempDir']+'/plot'+str(self.widgetID).replace('.', '_')+'.'+imageType
        # fileName = fileName.replace('\\', '/')
        self.imageFileName = str(self.image).replace('\\', '/')+'.'+str(imageType)
        if imageType == 'svg':
            self.require_librarys(['RSvgDevice'])
            self.R('devSVG(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight)+', height = '+str(dheight)
                +')')
        elif imageType == 'png':
            self.require_librarys(['RSvgDevice'])
            self.R('png(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight*100)+', height = '+str(dheight*100)
                +')')
        elif imageType == 'jpeg':
            self.require_librarys(['RSvgDevice'])
            self.R('jpeg(file=\''+str(os.path.join(redREnviron.directoryNames['tempDir'], self.imageFileName).replace('\\', '/'))+'\', width = '
                +str(dheight*100)+', height = '+str(dheight*100)
                +')')
                
    def plot(self, query, function = 'plot', dwidth=6, dheight=6):
        ## performs a quick plot given a query and an imageType
        self.plotMultiple(query, function = function, dwidth = dwidth, dheight = dheight, layers = [])
            

    def plotMultiple(self, query, function = 'plot', dwidth = 6, dheight = 6, layers = []):
        ## performs plotting using multiple layers, each layer should be a query to be executed in RSession
        self.function = function
        self.query = query
        self._startRDevice(dwidth, dheight, self.standardImageType)
        self.extras = self._setParameters()
        if str(self.extrasLineEdit.text()) != '':
            self.extras += ', '+str(self.extrasLineEdit.text())
        
        fullquery = '%s(%s, %s)' % (function, query, self.extras)
        self.R(fullquery)
        
        if len(layers) > 0:
            for l in layers:
                self.R(l)
                
        self.R('dev.off()')
        self.clear()
        fileName = str(self.imageFileName)
        self.addImage(fileName)
        self.layers = layers
        self._dwidth = dwidth
        self._dheight = dheight
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
        self._startRDevice(self._dwidth, self._dheight, self.standardImageType)
        self.extras = self._setParameters()
        if str(self.extrasLineEdit.text()) != '':
            self.extras += ', '+str(self.extrasLineEdit.text())
        self.R('%s(%s, %s)' % (self.function, self.query, self.extras))
        if len(self.layers) > 0:
            for l in self.layers:
                self.R(l)
        self.R('dev.off()')
        self.clear()
        fileName = str(self.imageFileName)
        self.addImage(fileName)
class colorListDialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical', title = 'Color List Dialog'):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        
        self.listOfColors = []
        self.controlArea = widgetBox(self)
        
        ## GUI
        
        # color list
        self.colorList = listBox(self.controlArea, label = 'Color List')
        button(self.controlArea, label = 'Add Color', callback = self.addColor)
        button(self.controlArea, label = 'Remove Color', callback = self.removeColor)
        
    def addColor(self):
        colorDialog = QColorDialog(self)
        colorDialog.exec_()
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
        
    def processColors(self):
        self.listOfColors = []
        for item in self.colorList.items():
            self.listOfColors.append(str(item.backgroundColor().name()))
        
class dialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical',title=None):
        QDialog.__init__(self,parent)
        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())