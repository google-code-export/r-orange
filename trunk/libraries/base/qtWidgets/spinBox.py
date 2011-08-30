"""Spin Box.

A spin box is used to select an integer or float value.  Values can be typed directly or changed using the up and down arrows.

Use the function value() to get the current value (as a float! so 2 is returned as 2.0).
"""

import redRGUI
from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
import redRLog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class spinBox(QDoubleSpinBox ,widgetState):
    def __init__(self, widget, label=None, displayLabel=True, value=None, orientation='horizontal', decimals=0, max = None, min = None, callback=None, *args, **kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.widget = widget
        
        widgetState.__init__(self,widget,label,**kwargs)
        QDoubleSpinBox.__init__(self)
        self.setDecimals(decimals)
        self.label = label
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            
            widgetLabel(self.hb, label,sizePolicy=QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum))
            
            self.hb.layout().addWidget(self)
        else:
            self.controlArea.layout().addWidget(self)
        
        if max:
            self.setMaximum(int(max))
        if min:
            self.setMinimum(int(min))
        self.setWrapping(True) # we always allow the spin box to wrap around
        if value:
            self.setValue(value)
        if callback:
            QObject.connect(self, SIGNAL('valueChanged(double)'), callback)
        
    def getSettings(self):
        value = self.value()
        prefix = self.prefix()
        suffix = self.suffix()
        singleStep = self.singleStep()
        min = self.minimum()
        max = self.maximum()
        r = {'value':value, 'prefix':prefix, 'suffix':suffix, 'singleStep':singleStep, 'max':max, 'min':min, 'decimals':self.decimals()}
        return r
    def loadSettings(self,data):
        print data
        try:
            self.setDecimals(data.get('decimals', 0))
            if data.get('max', None):
                self.setMaximum(float(data.get('max')))
            if data.get('min', None):
                self.setMinimum(float(data.get('min')))
            self.setValue(float(data.get('value', 0)))
            if data.get('prefix', None):
                self.setPrefix(data.get('prefix'))
            if data.get('suffix', None):
                self.setSuffix(data.get('suffix'))
            if data.get('singleStep', None):
                self.setSingleStep(data.get('singleStep'))
            
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, redRLog.formatException())
    def update(self, min, max):
        value = self.value()
        self.setMaximum(max)
        self.setMinimum(min)
        if value >= min and value <= max:
            self.setValue(value)
    def getReportText(self, fileDir):
        return {self.widgetName:{'includeInReports': self.includeInReports, 'text': str(self.value())}}
        
        
