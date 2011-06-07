"""Dynamic Spin Box

A widgetBox that dynamically generates spinBox, users must set a key, label, and OrderedDict of values for each spinBox.  Boxes are referenced by their key.  There are abilities to add and remove keys as well as updating keys.
"""
import redRLog
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.spinBox import spinBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *
class DynamicSpinBox(groupBox):
    def __init__(self,widget, label = None, values = None, displayLabel=True, includeInReports=True,
            orientation='vertical', addSpace=False, sizePolicy = None, margin = -1, spacing = -1, flat = 0,alignment=Qt.AlignTop, callback = None, toolTip = None,**kwargs):
        groupBox.__init__(self, widget, label = label, displayLabel = displayLabel, includeInReports = includeInReports, orientation=orientation, addSpace=addSpace, sizePolicy = sizePolicy, margin = margin, spacing = spacing, alignment=alignment,**kwargs)
        
        self.spinBoxes = {}
        if callback:
            self.callback = callback
        else: 
            self.callback = None
        self.orientation = orientation
        self.toolTip = toolTip
        if values:  # values are a tuple-dict [((key, label), (max, min, value, decimal), ...}
            for k, v in values:
                self.addSpinBox(k[0], k[1], v)
    def getSpinIDs(self):
        """Returns a list of spinBox ids"""
        return self.spinBoxes.keys()
    def getSpinBox(self, id):
        """Returns the spinBox referenced by id"""
        return self.spinBoxes[id]
    def addSpinBox(self, key, name, items):
        """Adds a new spinBox to the DynamicSpinBox"""
        print 'Adding spinbox %s' % key
        if key in self.spinBoxes.keys():
            redRLog.log(redRLog.REDRCORE, redRLog.DEBUG, 'key exists, loading applying settings')
            self.spinBoxes[key].setMaximum(items[0])
            self.spinBoxes[key].setMinimum(items[1])
            self.spinBoxes[key].setValue(items[2])
            self.spinBoxes[key].setDecimals(items[3])
        else:
            self.spinBoxes[key] = spinBox(self, label = name, max = items[0], min = items[1], value = items[2], decimals = items[3], orientation = self.orientation, callback = self.callback, toolTip = self.toolTip)
    def removeSpinBox(self, id):
        self.spinBoxes[id].hide()
        del self.spinBoxes[id]
    def getSettings(self):            
        r = []
        for i in self.spinBoxes:
            r.append(((i, self.spinBoxes[i].label), self.spinBoxes[i].getSettings()))
        return r
    
    def loadSettings(self,data):
        print data
        for i, d in data:
            self.addSpinBox(i[0], i[1], (0, 0, 0, 0))
            self.spinBoxes[i[0]].loadSettings(d)