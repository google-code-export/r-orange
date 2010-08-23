## redRGUI Graphics View.  A graphics view used for graphing R graphs, this should be as general as possible with an eye to some degree of automation in assignment of items.  

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from redRGUI import widgetState
class graphicsView(QGraphicsView, widgetState):
    def __init__(self, parent, image = None):
        ## want to init a graphics view with a new graphics scene, the scene will be accessable through the widget.
        QGraphicsView.__init__(self, parent)
        parent.layout().addWidget(self)  # place the widget into the parent widget
        
        if image:
            ## there is an image and we should set that into the graphics scene
            print self.scene(), 'The scene, is it 0?'
            if self.scene():
                self.scene().addItem(QGraphicsPixmapItem(QPixmap(image)))
            else:
                scene = QGraphicsScene()
                self.setScene(scene)
                if self.scene():
                    self.scene().addItem(QGraphicsPixmapItem(QPixmap(image)))
                else:
                    print scene
                    print self.scene()
                    print 'Error, no scene initialized'
                    raise Exception
        self.menu = QMenu(self)
        self.menu.addAction('Copy')
    def clear(self):
        self.scene().clear()
        
    def toClipboard(self):
        QApplication.clipboard().setImage(self.returnImage())
        
    def mousePressEvent(self, mouseEvent):
        
        if mouseEvent.button() == Qt.RightButton:
            # show the action menu
            newCoords = QPoint(mouseEvent.globalPos())
            action = self.menu.exec_(newCoords)
            if action:
                if str(action.text()) == 'Copy':
                    self.toClipboard()
    def returnImage(self):
        ## generate a rendering of the graphicsView and return the image
        
        size = self.scene().sceneRect().size()
        image = QImage(int(self.scene().width()), int(self.scene().height()), QImage.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        self.scene().render(painter)
        painter.end()
        return image
        
        
        # image = QImage(1000, 700, QImage.Format_ARGB32_Premultiplied)
        # painter = QPainter(image)
        # self.schema.canvasView.scene().render(painter) #
        # painter.end()
        # imageFile = os.path.join(fileDir2, 'canvas-image.png').replace('\\', '/')
        # if not image.save(imageFile):
            # print 'Error in saving schema'
            # print image
            # print image.width(), 'width'
            
            
    def addImage(self, image):
        ## add an image to the view
        self.scene().addItem(QGraphicsPixmapItem(QPixmap(image)))
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
        