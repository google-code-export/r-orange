## redRGUI Graphics View.  A graphics view used for graphing R graphs, this should be as general as possible with an eye to some degree of automation in assignment of items.  

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *
from redRGUI import widgetState
import RSession, redREnviron, datetime, os
class graphicsView(QGraphicsView, widgetState):
    def __init__(self, parent, image = None, imageType = None):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        QGraphicsView.__init__(self, parent)
        parent.layout().addWidget(self)  # place the widget into the parent widget
        self.parent = parent
        self.widgetSelectionRect = None
        self.mainItem = None
        self.query = ''
        if image:
            ## there is an image and we should set that into the graphics scene
            self.addImage(image, imageType)
        self.currentScale = 1
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
        self.dialog.setWindowTitle('Red-R Graphics View')
        self.dialog.setLayout(QHBoxLayout())
        
        #self.menu.addAction('Un Zoom')
        # self.setMinimumWidth(25)
        # self.setMinimumHeight(25)
        #self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    def R(self, query):
        RSession.Rcommand(query = query)
    def clear(self):
        self.scene().clear()
        
    def toClipboard(self):
        QApplication.clipboard().setImage(self.returnImage())
        
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
                    self.dialog.layout().addWidget(self)
                    self.dialog.show()
                elif str(action.text()) == 'Redock':
                    self.parent.layout().addWidget(self)
                    self.dialog.hide()
                elif str(action.text()) == 'Fit In Window':
                    print self.mainItem.boundingRect()
                    self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
                elif str(action.text()) == 'Bitmap':
                    print 'save as bitmap'
                    qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".bmp", "Bitmap (.bmp)")
                    if qname.isEmpty(): return
                    self.saveAs(str(qname), 'bmp')
                elif str(action.text()) == 'PDF':
                    print 'save as pdf'
                    qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".pdf", "PDF Document (.pdf)")
                    if qname.isEmpty(): return
                    self.saveAs(str(qname), 'pdf')
                elif str(action.text()) == 'Post Script':
                    print 'save as post script'
                    qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".eps", "Post Script (.eps)")
                    if qname.isEmpty(): return
                    self.saveAs(str(qname), 'ps')
                elif str(action.text()) == 'JPEG':
                    print 'save as jpeg'
                    qname = QFileDialog.getSaveFileName(self, "Save Image", redREnviron.directoryNames['documentsDir'] + "/Image-"+str(datetime.date.today())+".jpg", "JPEG Image (.jpg)")
                    if qname.isEmpty(): return
                    self.saveAs(str(qname), 'jpeg')
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
        self.image = os.path.abspath(image)
        #print self.image
        if not self.scene():
            print 'loading scene'
            scene = QGraphicsScene()
            self.setScene(scene)
            print self.image
        if imageType == None:
            imageType = os.path.split(image)[1].split('.')[-1]
        if imageType not in ['svg', 'png', 'jpeg']:
            self.clear()
            raise Exception, 'Image type specified is not a valid type for this widget.'
        if imageType == 'svg':
            mainItem = QGraphicsSvgItem(image)
        elif imageType in ['png', 'jpeg']:
            mainItem = QGraphicsPixmapItem(QPixmap(image))
        else:
            raise Exception, 'Image type %s not specified in a plotting method' % imageType
            #mainItem = QGraphicsPixmapItem(QPixmap(image))
        self.scene().addItem(mainItem)
        self.mainItem = mainItem
        
        
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        import os
        if os.path.split(self.image)[0] == redREnviron.directoryNames['tempDir']:
            ## the image is in the tempDir so we should go there in the future
            directory = 'temp'
        else:
            directory = os.path.split(self.image)[0]
            
        r = {'image':os.path.split(self.image)[1], 'directory':directory}
        # print r
        return r
    def loadSettings(self,data):
        import os
        if data['directory'] == 'temp':
            directory = redREnviron.directoryNames['tempDir']
        else:
            directory = data['directory']
        self.addImage(os.path.join(directory, data['image']))
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
        self.R(self.query)
        self.R('dev.off()')
        
class dialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical',title=None):
        QDialog.__init__(self,parent)
        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())