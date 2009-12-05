from redRGUI import widgetState
from widgetBox import widgetBox
from widgetLabel import widgetLabel

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class listBox(QListWidget,widgetState):
    def __init__(self, widget,label=None,orientation='vertical', enableDragDrop = 0, dragDropCallback = None, dataValidityCallback = None, sizeHint = None, *args):
        self.widget = widget
        QListWidget.__init__(self, *args)
        if label:
            hb = widgetBox(widget,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            widget.layout().addWidget(self)

        self.enableDragDrop = enableDragDrop
        self.dragDopCallback = dragDropCallback
        self.dataValidityCallback = dataValidityCallback
        if not sizeHint:
            self.defaultSizeHint = QSize(150,100)
        else:
            self.defaultSizeHint = sizeHint
        if enableDragDrop:
            self.setDragEnabled(1)
            self.setAcceptDrops(1)
            self.setDropIndicatorShown(1)
            #self.setDragDropMode(QAbstractItemView.DragDrop)
            self.dragStartPosition = 0

    def sizeHint(self):
        return self.defaultSizeHint
    def startDrag(self, supportedActions):
        if not self.enableDragDrop: return

        drag = QDrag(self)
        mime = QMimeData()

        if not self.ogValue:
            selectedItems = [i for i in range(self.count()) if self.item(i).isSelected()]
        else:
            selectedItems = getdeepattr(self.widget, self.ogValue, default = [])

        mime.setText(str(selectedItems))
        mime.source = self
        drag.setMimeData(mime)
        drag.start(Qt.MoveAction)

    def dragEnterEvent(self, ev):
        if not self.enableDragDrop: return
        if self.dataValidityCallback: return self.dataValidityCallback(ev)

        if ev.mimeData().hasText():
            ev.accept()
        else:
            ev.ignore()


    def dragMoveEvent(self, ev):
        if not self.enableDragDrop: return
        if self.dataValidityCallback: return self.dataValidityCallback(ev)

        if ev.mimeData().hasText():
            ev.setDropAction(Qt.MoveAction)
            ev.accept()
        else:
            ev.ignore()

    def dropEvent(self, ev):
        if not self.enableDragDrop: return
        if ev.mimeData().hasText():
            item = self.itemAt(ev.pos())
            if item:
                index = self.indexFromItem(item).row()
            else:
                index = self.count()

            source = ev.mimeData().source
            selectedItemIndices = eval(str(ev.mimeData().text()))

            if self.ogLabels != None and self.ogValue != None:
                allSourceItems = getdeepattr(source.widget, source.ogLabels, default = [])
                selectedItems = [allSourceItems[i] for i in selectedItemIndices]
                allDestItems = getdeepattr(self.widget, self.ogLabels, default = [])

                if source != self:
                    setattr(source.widget, source.ogLabels, [item for item in allSourceItems if item not in selectedItems])   # TODO: optimize this code. use the fact that the selectedItemIndices is a sorted list
                    setattr(self.widget, self.ogLabels, allDestItems[:index] + selectedItems + allDestItems[index:])
                    setattr(source.widget, source.ogValue, [])  # clear selection in the source widget
                else:
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
                if source != self:
                    self.insertItems(source.selectedItems())
                    for index in selectedItemIndices[::-1]:
                        source.takeItem(index)
                else:
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
        else:
            ev.ignore()

    def getSettings(self):
        # print 'saving list box'
        items = []
        for i in range(0,self.count()):
            items.append(self.item(i).text())
        
        selected = [self.indexFromItem(i).row() for i in self.selectedItems()]
        r = {'items':items,'selected':selected}
        r.update(self.getState())
        # print r
        return r
    def loadSettings(self,data):
        print 'loading list box'
        print data
        self.clear()
        self.addItems([unicode(i) for i in data['items']])
        
        for i in data['selected']:
            self.setItemSelected(self.item(i), True)
        
        #self.setEnabled(data['enabled'])
        self.setState(data)
        


