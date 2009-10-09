"""
<name>SandBox</name>
<description></description>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI
import RRGUI
import RAffyClasses

class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        self.lineEditText = ''
        self.loadSettings()
        self.inputs = None
        self.outputs = None
        
        # self.image = QPixmap()
        # self.image.load("C:\\Python25\\Lib\\site-packages\\orange\\OrangeWidgets\\icons\\plotAffy.png")
        
        # self.label = QLabel("click to see picture")
        # self.label.setGeometry(50,50,300,300)
        #GUI
        self.myTab = RRGUI.tabWidget(self.controlArea, 'myTab', self)
        self.firstTab = RRGUI.createTabPage(self.myTab, 'firstTab', self, 'First Page')
        #self.box = OWGUI.widgetBox(self.controlArea, "Box")
        self.mytable = RRGUI.table(self.firstTab, 'mytable', self)
        self.secondTab  = RRGUI.createTabPage(self.myTab, 'secondTab', self, 'Second Page')
        self.mylineEdit = RRGUI.lineEdit(self.secondTab, 'mylineEdit', self, 'lineEditText')
        RRGUI.button(self.firstTab, None, self, 'Add Row', callback = self.AddRow)
        RRGUI.button(self.firstTab, None, self, 'Add Col', callback = self.AddCol)
        
    def AddCol(self):   
        self.mytable.setColumnCount(self.mytable.columnCount()+1)
        
    def AddRow(self):
        self.mytable.setRowCount(self.mytable.rowCount()+1)
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