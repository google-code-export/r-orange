"""
<name>Plot Affy Image</name>
<description>Obtains an affybatch and plots the images of the files</description>
<icon>icons/plotAffy.png</icon>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI
import RAffyClasses

class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        
        self.inputs = None
        self.outputs = None
        
        self.image = QPixmap()
        self.image.load("C:\\Python25\\Lib\\site-packages\\orange\\OrangeWidgets\\icons\\plotAffy.png")
        
        self.label = QLabel("click to see picture")
        self.label.setGeometry(50,50,300,300)
        #GUI
        
        self.box = OWGUI.widgetBox(self.controlArea, "Box")
        OWGUI.button(self.box, self, "Show", callback = self.showMe)
        
        self.thistext = QTextEdit(self)
        self.mainArea.layout().addWidget(self.thistext)
        self.require_librarys(['simpleaffy'])
        self.rsession('png(file="result.png", bg="transparent")')
        self.rsession('plot(rnorm(10), rnorm(10))')
        self.rsession('dev.off()')
        
        pictureHtml = '<img src="result.png"/>'
        
        self.thistext.setHtml(pictureHtml)
        #self.picture = OWGUI.widgetLabel(self.box)
        #self.picture.setPixmap(OWGUI.QPixmap("C:\\Python25\\Lib\\site-packages\\orange\\OrangeWidgets\\icons\\plotAffy.png"))
    def showMe(self):
        self.label.setPixmap(self.image)
        # window = QMainWindow()
        #
        # scene = QGraphicsScene(window)
        # pmi = scene.addPixmap(image)
        # pmi.setZValue(1)
        #gv = QGraphicsView(scene)
        #window.setCentralWidget(gv)
        #window.show()
        #self.imageBox = QCanvas(image)
        #self.controlArea.layout().addWidget(self.imageBox)
        
        #self.image.load("C:/Python25/Lib/site-packages/orange/OrangeWidgets/icons/plotAffy.png")
        #self.imageBox.show()