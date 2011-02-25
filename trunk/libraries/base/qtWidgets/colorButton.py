## colorButton, a special button that shows a color, clicking the button shows a color dialog and sets the color to that selected.  The button will return the displayed color.


from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox as redRWidgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')

class colorButton(QPushButton, widgetState):
    def __init__(self, widget, label = None, displayLabel = True, startColor = '#000000', callback = None, toolTip=None, width = 15, height = 15):
        widgetState.__init__(self,widget, label, includeInReports=True)
        
        QToolButton.__init__(self, self.controlArea)
        
        
        if label and displayLabel:
            self.hb = redRWidgetBox(self.controlArea,orientation='horizontal')
            lb = widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
            self.hasLabel = True
            self.hb.layout().setAlignment(lb,Qt.AlignRight)
            lb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            self.controlArea.layout().addWidget(self)
            self.hasLabel = False
            
        self.label = label
        self.w = width
        self.h = height
        self.setMinimumSize(width, height)
        self.callback = callback
        self.color = '#000000'
        self.setMaximumSize(self.w + 5, self.h + 5)
        self.connect(self, SIGNAL("clicked()"), self.showColorDialog)
        self.updateColor()

    def updateColor(self):
        pixmap = QPixmap(self.w,self.h)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(QPen(QColor(self.color)))
        painter.setBrush(QBrush(QColor(self.color)))
        painter.drawRect(0, 0, self.w+1, self.h+1);
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(self.w+1,self.h+1))


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
        if self.callback:
            self.callback()