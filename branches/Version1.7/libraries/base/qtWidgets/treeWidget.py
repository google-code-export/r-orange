# treeWidget.  implementation of a QTreeWidget for redRGUI

from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRGUI

class treeWidget(QTreeWidget, widgetState):
    def __init__(self, widget, label = None, toolTip = None, callback = None):
        QTreeWidget.__init__(self, widget)
        
        if widget:
            if label:
                self.hb = widgetBox(widget,orientation=orientation)
                widgetLabel(self.hb, label)
                if width != -1:
                    sb = widgetBox(self.hb)
                    sb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.hb.layout().addWidget(self)
                self.hasLabel = True
            else:
                widget.layout().addWidget(self)
                self.hasLabel = False
        if toolTip: self.setToolTip(toolTip)
        if callback:
            QObject.connect(self, SIGNAL('currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)'), callback)
    def setHeaderLabels(self, labels):
        self.labels = labels
        QTreeWidget.setHeaderLabels(self, labels)
    def getSettings(self):
        r = {}
        r['headerLabels'] = self.labels
        r['itemSettings'] = []
        for item in self.items():
            try:
                r.append(item.getSettings())
            except:
                continue
        return r
    def hide(self):
        if self.hasLabel:
            self.hb.hide()
        else:
            QLineEdit.hide(self)
    def show(self):
        if self.hasLabel:
            self.hb.show()
        else:
            QLineEdit.show(self)
    def loadSettings(self,data):
        try:
            self.setHeaderLabels(data['headerLabels'])
            for item in data['itemSettings']:
                try:
                    newItem = redRGUI.treeWidgetItem()
                    newItem.loadSettings(item)
                    self.addTopLevelItem(newItem)
                except:
                    continue
        except:
            print 'Exception during setting assignment.'