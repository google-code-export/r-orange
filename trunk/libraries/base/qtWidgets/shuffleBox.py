"""Shuffle Box

This is a Red-R specific widget.  The shuffleBox inherits from the listBox with the added ability that the order of items can be changed using the drag/drop feature (so they are shuffled).  This is useful for setting the order in which items appear.
"""

from redRGUI import widgetState
from libraries.base.qtWidgets.listBox import listBox
import redRReports,redRLog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OrderedDict import OrderedDict
import redRi18n
_ = redRi18n.get_(package = 'base')

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