import redRGUI
from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class spinBox(QSpinBox,widgetState):
    def __init__(self, widget, value=None, label=None,orientation='horizontal', max = None, min = None, callback=None, toolTip = None, *args):
        self.widget = widget
        QSpinBox.__init__(self)
        if label:
            self.hb = widgetBox(widget,orientation=orientation)
            widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)
        if max:
            self.setMaximum(int(max))
        if min:
            self.setMinimum(int(min))
        if toolTip:
            self.setToolTip(str(toolTip))
        if callback:
            QObject.connect(self, SIGNAL('valueChanged(int)'), callback)
        self.setWrapping(True) # we always allow the spin box to wrap around
        
    def hide(self):
        if self.hb:
            self.hb.hide()
        else:
            QSpinBox.hide(self)
    def getSettings(self):
        value = self.value()
        prefix = self.prefix()
        suffix = self.suffix()
        singleStep = self.singleStep()
        min = self.minimum()
        max = self.maximum()
        r = {'value':value, 'prefix':prefix, 'suffix':suffix, 'singleStep':singleStep, 'max':max, 'min':min}
        return r
    def loadSettings(self,data):
        try:
            self.setValue(data['value'])
            self.setPrefix(data['prefix'])
            self.setSuffix(data['suffix'])
            self.setMaximum(data['max'])
            self.setMinimum(data['min'])
            self.setSingleStep(data['singleStep'])
        except:
            print 'Error occured in Spin Box loading'
            import traceback,sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
    def update(self, min, max):
        value = self.value()
        self.setMaximum(max)
        self.setMinimum(min)
        self.setValue(value)
