## DynamicComboBox, a widgetBox that dynamically generates comboBoxes, users must set a key, label, and OrderedDict of values for each comboBox.  Boxes are referenced by their key.  There are abilities to add and remove keys as well as updating keys.

from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.groupBox import groupBox
from PyQt4.QtCore import *
from PyQt4.QtGui import *
class DynamicComboBox(groupBox):
    def __init__(self,widget, label = None, values = None, displayLabel=True, includeInReports=True,
            orientation='vertical', addSpace=False, 
            sizePolicy = None, margin = -1, spacing = -1, flat = 0,alignment=Qt.AlignTop, callback = None, toolTip = None):
        groupBox.__init__(self, widget, label = label, displayLabel = displayLabel, includeInReports = includeInReports, orientation=orientation, addSpace=addSpace,
            sizePolicy = sizePolicy, margin = margin, spacing = spacing, alignment=alignment)
        
        self.comboBoxes = {}
        if callback:
            self.callback = callback
        else:
            self.callback = None
        self.orientation = orientation
        self.toolTip = toolTip
        if values:  # values are a tuple-dict [((key, label), [(comboKey, comboValue), (comboKey, comboValue)]), ...}
            for k, v in values:
                self.addComboBox(k[0], k[1], v)
    def getComboIDs(self):
        return self.comboBoxes.keys()
    def getComboBox(self, id):
        return self.comboBoxes[id]
    def addComboBox(self, key, name, items):
        if key in self.comboBoxes.keys():
            if items:
                self.comboBoxes[key].update(items)
        else:
            self.comboBoxes[key] = comboBox(self, label = name, items = items, orientation = self.orientation, callback = self.callback, toolTip = self.toolTip)
    def removeComboBox(self, id):
        self.comboBoxes[id].hide()
        del self.comboBoxes[id]
    def getSettings(self):            
        r = []
        for i in self.comboBoxes:
            r.append(((i, self.comboBoxes[i].label), self.comboBoxes[i].getSettings()))
        return r
    
    def loadSettings(self,data):
        print data
        for i, d in data:
            self.addComboBox(i[0], i[1], None)
            self.comboBoxes[i[0]].loadSettings(d)