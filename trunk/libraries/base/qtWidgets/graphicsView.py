## redRGUI Graphics View.  A graphics view used for graphing R graphs, this should be as general as possible with an eye to some degree of automation in assignment of items.  

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *
from redRGUI import widgetState
class graphicsView(QGraphicsView, widgetState):
    def __init__(self, parent, image = None, imageType = 'svg'):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        QGraphicsView.__init__(self, parent)
        parent.layout().addWidget(self)  # place the widget into the parent widget
        self.parent = parent
        self.widgetSelectionRect = None
        self.mainItem = None
        if image:
            ## there is an image and we should set that into the graphics scene
            self.addImage(image, imageType)
        self.currentScale = 1
        self.menu = QMenu(self)
        self.menu.addAction('Copy')
        self.menu.addAction('Fit View')
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
                elif str(action.text()) == 'Fit View':
                    print self.mainItem.boundingRect()
                    self.fitInView(self.mainItem.boundingRect(), Qt.KeepAspectRatio)
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
        if not self.scene():
            scene = QGraphicsScene()
            self.setScene(scene)
        if not imageType:
            imageType = image.split('.')[-1]
        if imageType not in ['svg', 'png', 'jpeg']:
            raise Exception, 'Image type specified is not a valid type for this widget.'
        if imageType == 'svg':
            mainItem = QGraphicsSvgItem(image)
        elif imageType in ['png', 'jpeg']:
            mainItem = QGraphicsPixmapItem(QPixmap(image))
        self.scene().addItem(mainItem)
        self.mainItem = mainItem
        
        
    def getSettings(self):
        # print 'in widgetLabel getSettings'
        r = {'text':None}
        # print r
        return r
    def loadSettings(self,data):
        # print 'in widgetLabel loadSettings'
        # print data
        #self.setText(data['text'])
        pass
    def getReportText(self, fileDir):
        #return ''
        pass
        
class dialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical',title=None):
        QDialog.__init__(self,parent)
        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())