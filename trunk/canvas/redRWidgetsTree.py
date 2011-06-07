# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modifications by Kyle R Covington and Anup Parikh
# Description:
#    tab for showing widgets and widget button class
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os.path, sys
from string import strip, count, replace
import orngDoc, orngRegistry, redRObjects
import OWGUIEx, redRSaveLoad, redRStyle
import redREnviron, redRLog
import xml.dom.minidom

# we have to use a custom class since QLabel by default ignores the mouse
# events if it is showing text (it does not ignore events if it's showing an icon)
import redRi18n
# def _(a):
    # return a
_ = redRi18n.Coreget_()

class OrangeLabel(QLabel):
    """Class for the tree view labels, reimplements mouse events"""
    def mousePressEvent(self, e):
        pos = self.mapToParent(e.pos())
        ev = QMouseEvent(e.type(), pos, e.button(), e.buttons(), e.modifiers())
        self.parent().mousePressEvent(ev)

    def mouseMoveEvent(self, e):
        pos = self.mapToParent(e.pos())
        ev = QMouseEvent(e.type(), pos, e.button(), e.buttons(), e.modifiers())
        self.parent().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, e):
        pos = self.mapToParent(e.pos())
        ev = QMouseEvent(e.type(), pos, e.button(), e.buttons(), e.modifiers())
        self.parent().mouseReleaseEvent(ev)



class WidgetButtonBase():
    """Base class for widget buttons"""
    def __init__(self, name, widgetInfo, widgetTabs, canvasDlg):
        self.shiftPressed = 0
        self.name = name
        self.widgetInfo = widgetInfo
        self.widgetTabs = widgetTabs
        self.canvasDlg = canvasDlg
        self.REDRCORE_working = 0
    def clicked(self, rightClick = False, pos = None):
        """Adds the widget in the event of a button click.
        
        Protection feature added to prevent multiple widget loading when the user doubleclicks.
        """
        if self.REDRCORE_working: return
        self.REDRCORE_working = 1
        win = self.canvasDlg.schema
        if pos:
            pos = win.mapFromGlobal(pos)
            win.addWidget(self.widgetInfo, pos.x(), pos.y())
        else:
            win.addWidget(self.widgetInfo)
        if (rightClick or self.shiftPressed):
            import orngCanvasItems
            if isinstance(rightClick, orngCanvasItems.CanvasWidget):
                win.addLine(rightClick, win.widgets[-1])
            elif len(win.widgets) > 1:
                win.addLine(win.widgets[-2], win.widgets[-1])
        self.REDRCORE_working = 0
        #return win.widgets[-1]
    def setCompatible(self, widget):
        """the goal of this is to set the background to a color (light blue?) if the selected canvas widget has connected to the canvas widget before.
        """
        connectingWidgets = log.getHistory(widget.widgetInfo.fileName)
        if self.widgetInfo.fileName in connectingWidgets:
            self.setBackgroundColor(Qt.blue)
        else:
            self.setBackgroundColor(Qt.white)
      
class WidgetTreeItem(QTreeWidgetItem, WidgetButtonBase):
    """Class for items in the widget tree"""
    def __init__(self, parent, name, widgetInfo, tabs, canvasDlg):
        QTreeWidgetItem.__init__(self, parent)
        WidgetButtonBase.__init__(self, name, widgetInfo, tabs, canvasDlg)
        
        self.setIcon(0, QIcon(widgetInfo.icon))
        self.setText(0, name)
        self.setToolTip(0, widgetInfo.tooltipText)
    
    def adjustSize(self):
        pass


       
class WidgetScrollArea(QScrollArea):
    """Scroll area container for the widget tree"""
    def wheelEvent(self, ev):
        hs = self.horizontalScrollBar()
        hs.setValue(min(max(hs.minimum(), hs.value()-ev.delta()), hs.maximum()))

class widgetSuggestions(QTreeWidget):
    """Tree widget for holding suggested widgets, this pops up when a widget with a history is selected on the canvas."""
    def __init__(self, parent,canvasDlg):
        
        self.canvasDlg = canvasDlg
        QTreeWidget.__init__(self, parent)
        parent.layout().addWidget(self)
        self.setHeaderLabels([_('Suggested Widgets')])
        QObject.connect(self, SIGNAL('itemClicked (QTreeWidgetItem *,int)'), lambda action: self.activateSuggestWidget(action))
        self.hide()
        
    def activateSuggestWidget(self, action):
        newwidget = redRObjects.schemaDoc.addWidget(action.widgetInfo)
        #if self.suggestingWidget:
            #redrObjects.schemaDlg.addLine(self.suggestingWidget, redRObjects.getWidgetByIDActiveTabOnly(newwidget))
            #self.canvasDlg.schema.addLine(self.suggestingWidget, redRObjects.getWidgetByIDActiveTabOnly(newwidget))
        

class WidgetTree(QTreeWidget):
    """The widget tree"""
    def __init__(self, parent, canvasDlg, widgetRegistry, *args):
        self.canvasDlg = canvasDlg
        self.widgetInfo = widgetRegistry
        self.allWidgets = []
        self.tabDict = {}
        self.tabs = []

        QTreeWidget.__init__(self, parent)
        parent.layout().addWidget(self)
        
        self.setMouseTracking(1)
        self.setHeaderHidden(1)
        self.mousePressed = 0
        self.mouseRightClick = 0
        self.connect(self, SIGNAL("itemClicked (QTreeWidgetItem *,int)"), self.itemClicked)
        self.setStyleSheet(""" QTreeView::item {padding: 2px 0px 2px 0px} """)          # show items a little bit apart from each other

        # this is needed otherwise the document window will sometimes strangely lose focus and the output window will be focused
        self.setFocusPolicy(Qt.ClickFocus)   
        self.createWidgetTabs(widgetRegistry)            
        
        
    def mousePressEvent(self, e):
        QTreeWidget.mousePressEvent(self, e)
        self.mousePressed = 1
        self.shiftPressed = bool(e.modifiers() & Qt.ShiftModifier)
        self.mouseRightClick = e.button() == Qt.RightButton
        
    def mouseReleaseEvent(self, e):
        QTreeWidget.mouseReleaseEvent(self, e)
        dinwin, widget = getattr(self, "widgetDragging", (None, None))
        self.shiftPressed = bool(e.modifiers() & Qt.ShiftModifier)
        if widget:
            if widget.invalidPosition:
                dinwin.removeWidget(widget)
                dinwin.canvasView.scene().update()
            elif self.shiftPressed and len(dinwin.widgets) > 1:
                dinwin.addLine(dinwin.widgets[-2], dinwin.widgets[-1])
            delattr(self, "widgetDragging")
           
        self.mousePressed = 0
        
    def itemClicked(self, item, column):
        """Adds the widget to the schema.  If shift is heald and only one widget is selected on the canvas then the new widget is connected to the selected widget."""
        if isinstance(item, WidgetTreeFolder):
            return
        
        if hasattr(self, 'busy'): return
        
        self.busy = 1
        newwidget = redRObjects.addWidget(item.widgetInfo)
        if (self.mouseRightClick or self.shiftPressed):
            if len(redRObjects.activeTab().getSelectedWidgets()) == 1:
                redRObjects.schemaDlg.addLine(redRObjects.activeTab().getSelectedWidgets()[0], redRObjects.getWidgetByIDActiveTabOnly(newwidget))
        delattr(self, 'busy')
    
    def clear(self):
        """Clears the widget tree"""
        self.allWidgets = []
        self.tabDict = {}
        self.tabs = []
        QTreeWidget.clear(self)
        
    def createWidgetTabs(self, widgetRegistry):
        """Creates a tab to add widget or other tabs to"""
        iconSize = redRStyle.iconSizeList[redREnviron.settings["toolbarIconSize"]]
        self.setIconSize(QSize(iconSize, iconSize))

        mainTabs = widgetRegistry['tags']
        treeXML = mainTabs.childNodes[0]
        #print treeXML.childNodes
        redREnviron.settings['widgetXML'] = mainTabs
        for itab in treeXML.childNodes:
            if itab.nodeName == 'group': #picked a group element
                
                tab = self.insertWidgetTab(unicode(itab.getAttribute('name')), 1) # a QTreeWidgetItem
                
                #print _('inserted tab ')+unicode(itab.getAttribute('name'))
                self.insertChildTabs(itab, tab, widgetRegistry)
                
                self.insertWidgets(itab.getAttribute('name'), tab, widgetRegistry)

                if hasattr(tab, "adjustSize"):
                    tab.adjustSize()
        
        # return the list of tabs and their status (shown/hidden)
    
    def insertChildTabs(self, itab, tab, widgetRegistry):
        """Recursively inserts child tabs into the named tab."""
        try:
            
            if itab.hasChildNodes(): subTabs = itab.childNodes
            else: return
            
            for child in subTabs:
                if child.nodeName == 'group': # we found another group
                    childTab = WidgetTreeFolder(tab, unicode(child.getAttribute('name')))
                    
                    childTab.widgets = []
                    childTab.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicatorWhenChildless)
                    self.insertChildTabs(child, childTab, widgetRegistry)
                    self.insertWidgets(child.getAttribute('name'), childTab, widgetRegistry)
                    
        except Exception as inst: #subtabs don't exist
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            # debugging print inst
            return
                
    def insertWidgets(self, itab, tab, widgetRegistry):
        """Inserts widgt icons into the named tab"""
        
        try:
            addingWidgets = []
            for widgetInfo in widgetRegistry['widgets'].values():
                for t in widgetInfo.tags:
                    if type(t) == tuple:
                        if t[0] == unicode(itab):
                            addingWidgets.append((widgetInfo, t[1]))
                    else:
                        # debugging print t
                        if t == unicode(itab):
                            addingWidgets.append((widgetInfo, 0))
            # debugging print addingWidgets
            addingWidget = sorted(addingWidgets, key = lambda info: info[1]) ## now things are sorted on the widget values.
            for widgetInfo, val in addingWidget:
                try:
                    button = WidgetTreeItem(tab, widgetInfo.name, widgetInfo, self, self.canvasDlg)
                    if button not in tab.widgets:
                        tab.widgets.append(button)
                    self.allWidgets.append(button)
                            
                except Exception as inst: 
                    redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
                    # debugging print inst
                    pass
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass

        
    def insertWidgetTab(self, name, show = 1):
        if self.tabDict.has_key(name):
            self.tabDict[name].setHidden(not show)
            return self.tabDict[name]
        
        item = WidgetTreeFolder(self, name)
        item.widgets = []
        self.tabDict[name] = item

        if not show:
            item.setHidden(1)
        if redREnviron.settings.has_key("treeItemsOpenness") and redREnviron.settings["treeItemsOpenness"].has_key(name):
             item.setExpanded(redREnviron.settings["treeItemsOpenness"][name])
        elif not redREnviron.settings.has_key("treeItemsOpenness") and self.topLevelItemCount() == 1:
            item.setExpanded(1)
        self.tabs.append((name, 2*int(show), item))

        return item

    def callback(self):
        text = unicode(self.widgetSuggestEdit.text())
        if '.rrts' in text: ## this is a template, we should load this and not add the widget
            for action in self.templateActions:
                if action.templateInfo.name == text:
                    redRSaveLoad.loadTemplate(action.templateInfo.file)
                    return
        else: ## if there isn't a .rrts in the filename then we should proceed as normal
            for action in self.actions: # move through all of the actions in the actions list
                if action.widgetInfo.name == text: # find the widget (action) that has the correct name, note this finds the first instance.  Widget names must be unique   ??? should we allow multiple widgets with the same name ??? probably not.
                    self.widgetInfo = action.widgetInfo
                    #print action.widgetInfo, _('Widget info')
                    self.canvasDlg.schema.addWidget(action.widgetInfo) # add the correct widget to the schema
                    
                    self.widgetSuggestEdit.clear()  # clear the line edit for the next widget
                    return

class WidgetTreeFolder(QTreeWidgetItem):
    def __init__(self, parent, name):
        QTreeWidgetItem.__init__(self, parent, [name])
#        item.setChildIndicatorPolicy(item.ShowIndicator)
    
    def mousePressEvent(self, e):
        self.treeItem.setExpanded(not self.treeItem.isExpanded())
         
                

