"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp, time
import redRGUI
import signals
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.webViewBox import webViewBox
from PyQt4.QtWebKit import *
QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)

class SandBox(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.lineEditText = ''
        self.require_librarys(['BARD'])
        ### GUI ###
        self.shuffle = shuffleBox(self.controlArea, label = 'Shuffle', items = [(1, 'apple'), (2, 'banana'), (3, 'cranberry')])
        self.textEdit = redRTextEdit(self.controlArea, label = 'output')
        #self.webBox = webViewBox(self.controlArea, label = 'Web Box')
        #self.webBox.setHtml('This is a simple test. <object type="application/x-pdf" data="file:///home/covingto/Documents/DNA%20Gel.pdf" width = "500" height = "400"></object>')
        
class shuffleBox(listBox):
    def __init__(self, widget, value = None, label = None, displayLabel = True, includeInReports = True, orientation = 'vertical', selectionMode = QAbstractItemView.SingleSelection,
         enableDragDrop = True, dragDropCallback = None, dataValidityCallback = None, sizeHint = None, callback = None, toolTip = None, items = None, *args, **kwargs):
         listBox.__init__(self, widget = widget, value = value, label = label, displayLabel = displayLabel, includeInReports = includeInReports, orientation = orientation, selectionMode = selectionMode, enableDragDrop = enableDragDrop, dragDropCallback = dragDropCallback, dataValidityCallback = dataValidityCallback, sizeHint = sizeHint, callback = callback, toolTip = toolTip, items = items, *args, **kwargs)

    def dropEvent(self, ev):
        if not self.enableDragDrop: return
        if ev.mimeData().hasText():
            item = self.itemAt(ev.pos())
            if item:
                index = self.indexFromItem(item).row()
            else:
                index = self.count()

            source = ev.mimeData().source
            selectedItemIndices = eval(unicode(ev.mimeData().text()))

            if self.ogLabels != None and self.ogValue != None:
                allSourceItems = getdeepattr(source.widget, source.ogLabels, default = [])
                selectedItems = [allSourceItems[i] for i in selectedItemIndices]
                allDestItems = getdeepattr(self.widget, self.ogLabels, default = [])
                items = [item for item in allSourceItems if item not in selectedItems]
                if index < len(allDestItems):
                    while index > 0 and index in getdeepattr(self.widget, self.ogValue, default = []):      # if we are dropping items on a selected item, we have to select some previous unselected item as the drop target
                        index -= 1
                    destItem = allDestItems[index]
                    index = items.index(destItem)
                else:
                    index = max(0, index - len(selectedItems))
                setattr(self.widget, self.ogLabels, items[:index] + selectedItems + items[index:])
                setattr(self.widget, self.ogValue, range(index, index+len(selectedItems)))
            else:       # if we don't have variables ogValue and ogLabel
                if index < self.count():
                    while index > 0 and self.item(index).isSelected():      # if we are dropping items on a selected item, we have to select some previous unselected item as the drop target
                        index -= 1
                items = [source.item(i) for i in selectedItemIndices]
                for ind in selectedItemIndices[::-1]:
                    source.takeItem(ind)
                    if ind <= index: index-= 1
                for item in items[::-1]:
                    self.insertItem(index, item)
                self.clearSelection()
                for i in range(index, index+len(items)):
                    self.item(i).setSelected(1)

            if self.dragDopCallback:        # call the callback
                self.dragDopCallback()
            ev.setDropAction(Qt.MoveAction)
            ev.accept()
            
            ## whatever all of this does we need to execute the function to update the items
            self.updateRedRItems()
        else:
            ev.ignore()
    #def __init__(self, widget, value=None, label=None, displayLabel=True, includeInReports=True, 
    #orientation='vertical', selectionMode=QAbstractItemView.SingleSelection,
    #enableDragDrop = 0, dragDropCallback = None, dataValidityCallback = None, sizeHint = None, 
    #callback=None, toolTip = None, items = None, *args):