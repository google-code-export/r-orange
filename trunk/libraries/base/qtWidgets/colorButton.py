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
        
        QPushButton.__init__(self,self.controlArea)
        
        if label:
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
        self.setMinimumSize(width, height)
        
        self.color = QColor()
        self.color.setNamedColor(startColor)
        self.setButtonColor()
        QObject.connect(self, SIGNAL("clicked()"), self.colorButtonPressed)
        self.callback = callback
    def setButtonColor(self):
        palette = QPalette()
        palette.setColor(QPalette.Button, self.color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    def colorButtonPressed(self):
        newColor = QColorDialog.getColor(self.color)
        if (newColor.isValid()):
            self.color = newColor
            self.setButtonColor()
        if self.callback:
            self.callback()
    def getColor(self):
        print self.color.name()
        return self.color.name()