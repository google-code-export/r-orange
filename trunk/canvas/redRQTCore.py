"""Red-R qtWidget Core.  This is the core location of qtWidgets.  These should be used only by core for setting up qt functionality"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4 import QtWebKit

import math, re, string, numpy, os
import redRi18n, redREnviron

from redRGUI import widgetState

from OrderedDict import OrderedDict
_ = redRi18n.Coreget_()


class dialog(QDialog,widgetState):
    def __init__(self, parent = None, 
    layout = 'vertical',title=None, callback = None):
        QDialog.__init__(self,parent)
        widgetState.__init__(self, self, 'dialog',includeInReports=True)
        
        
        if title:
            self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        if callback:
            QObject.connect(self, SIGNAL('accepted()'), callback)
            QObject.connect(self, SIGNAL('rejected()'), callback)

class spinBox(QDoubleSpinBox ,widgetState):
    def __init__(self, widget, label=None, displayLabel=True, includeInReports=True, value=None, 
    orientation='horizontal', decimals=0, max = None, min = None, callback=None, toolTip = None, *args):
        
        self.widget = widget
        
        widgetState.__init__(self,widget,label,includeInReports)
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
        if toolTip:
            self.setToolTip(unicode(toolTip))
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
            self.setDecimals(data['decimals'])
            self.setMaximum(float(data['max']))
            self.setMinimum(float(data['min']))
            self.setValue(float(data['value']))
            self.setPrefix(data['prefix'])
            self.setSuffix(data['suffix'])
            self.setSingleStep(data['singleStep'])
            
            print self.value(), data['value']
            print self.minimum(), data['min']
            print self.maximum(), data['max']
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
        
class treeWidget(QTreeWidget, widgetState):
    def __init__(self, widget, label = None, displayLabel=False, includeInReports=True, sortable=True,
    orientation='vertical', toolTip = None, callback = None):
        
        widgetState.__init__(self,widget,label,includeInReports)

        QTreeWidget.__init__(self, self.controlArea)
        self.setSortingEnabled(sortable)
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            widgetLabel(self.hb, label)
            if width != -1:
                sb = widgetBox(self.hb)
                sb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.hb.layout().addWidget(self)
        else:
            self.controlArea.layout().addWidget(self)

        if toolTip: self.setToolTip(toolTip)
        if callback:
            QObject.connect(self, SIGNAL('currentItemChanged(QTreeWidgetItem*, QTreeWidgetItem*)'), callback)
    def setHeaderLabels(self, labels):
        """Sets the header labels that will appear above the separated items in the tree"""
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

    def loadSettings(self,data):
        try:
            self.setHeaderLabels(data['headerLabels'])
            for item in data['itemSettings']:
                try:
                    newItem = treeWidgetItem()
                    newItem.loadSettings(item)
                    self.addTopLevelItem(newItem)
                except:
                    continue
        except:
            print _('Exception during setting assignment.')
            
class treeWidgetItem(QTreeWidgetItem):
    def __init__(self, widget = None, stringList = None, toolTip = None,bgcolor=None, flags=None):
        #widgetState.__init__(self,widget, _('treeWidgetItem'),includeInReports=False)
        if stringList:
            QTreeWidgetItem.__init__(self, stringList)
        else:
            QTreeWidgetItem.__init__(self)
            
        if widget:
            widget.addTopLevelItem(self)
            
        if toolTip:
            self.setToolTip(toolTip)
        if flags:
            self.setFlags(flags);
        if bgcolor:
            for x in range(len(stringList)):
                self.setBackground(x,QBrush(bgcolor))
            
    def text(self,col):
        return str(QTreeWidgetItem.text(self,col))
    
    # def setData(self,col,role,val):
        # print col,role,val
        # QTreeWidgetItem.setData(self,col,role,val)
        
    def getSettings(self):
        r = {}
        r['text'] = []
        for i in range(self.columnCount()):
            try:
                r['text'].append(self.text(i))
            except:
                r['text'].append(None)
            
        r['childSettings'] = []
        for i in range(self.childCount()):
            r['childSettings'].append(self.child(i).getSettings())
        return r
    def loadSettings(self, data):
        try:
            ## set the text
            for i in range(len(data['text'])):
                try:
                    if data['text'][i]:
                        self.setText(i, data['text'][i])
                except:
                    continue
        except Exception as inst:
            print inst, _('Error setting text')
        ## load the child items
        try:
            if len(data['childSettings']) > 0:
                for i in range(len(data['childSettings'])):
                    try:    
                        newItem = treeWidgetItem()
                        newItem.loadSettings(data['childSettings'][i])
                        self.addChild(newItem)
                    except:
                        continue
        except Exception as inst:
            print inst, _('Exception occured in loading child items.')
            

class webViewBox(QtWebKit.QWebView,widgetState):
    def __init__(self,widget,label=None, displayLabel=True,includeInReports=True, 
    url=None,orientation='vertical', followHere = False):
        
        widgetState.__init__(self,widget,label,includeInReports)
        QtWebKit.QWebView.__init__(self,self.controlArea)
        # factory = QtWebKit.QWebPluginFactory()
        # self.page().setPluginFactory(factory)
        self.controlArea.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        if displayLabel:
            hb = widgetBox(self.controlArea,orientation=orientation)
            widgetLabel(hb, label)
            hb.layout().addWidget(self)
        else:
            self.controlArea.layout().addWidget(self)
    
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        if not followHere:
            self.connect(self, SIGNAL('linkClicked(QUrl)'), self.followLink)
        if url:
            try:
                self.load(QUrl(url))
            except: pass 
    
    def followLink(self, url):
        import webbrowser
        #print unicode(url)
        #print url.toString()
        webbrowser.open_new_tab(url.toString())

class checkBox(widgetState,QWidget):
    def __init__(self,widget,label = None, displayLabel= True, includeInReports=True,
    buttons = None,toolTips = None, setChecked=None,
    orientation='vertical',callback = None):
        """Constructor, common parameters will be widget, label, buttons (a list or list-tuple of key values for buttons), toolTips (a list of toolTips for the buttons), and setChecked (a list of keys to check from the buttons)"""
        if toolTips and len(toolTips) != len(buttons):
            raise RuntimeError(_('Number of buttons and toolTips must be equal'))
 
        QWidget.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports)
        

        self.controlArea.layout().addWidget(self)

        if displayLabel:
            self.box = groupBox(self.controlArea,label=label,orientation=orientation)
            # self.layout().addWidget(self.box)
        else:
            self.box = widgetBox(self.controlArea,orientation=orientation)
        
        self.controlArea.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
        QSizePolicy.Preferred))
        
        # if orientation=='vertical':
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
            # QSizePolicy.MinimumExpanding))
        # else:
            # self.box.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,
            # QSizePolicy.Preferred))
            
        self.label = label
        self.items = OrderedDict()
        self.buttons = QButtonGroup(self.box)
        self.buttons.setExclusive(False)
        if buttons:
            self.addButtons(buttons)


        if callback:
            QObject.connect(self.buttons, SIGNAL('buttonClicked(int)'), callback)
        if setChecked:
            self.setChecked(setChecked)

    def addButtons(self,buttons):
        """Internal function to add buttons.  Can be called by end developer but should be extensively tested to ensure the desired functionality"""
        if type(buttons) in [dict,OrderedDict]:
            for k,v in buttons.items():
                self.addButton(k,v)
        elif type(buttons) in [list]:
            if len(buttons) > 0 and type(buttons[0]) is tuple:
                for k,v in buttons:
                    self.addButton(k,v)
            else:
                for v in buttons:
                    self.addButton(v,v)

            # redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,_('In radioButtons should not use list'))
        else:
            raise Exception(_('In radioButtons, addButtons takes a list, dict or OrderedDict'))

    def addButton(self,id, text,toolTip=None):
        """Internal function called by addButtons"""
        self.items[id] = text
        w = QCheckBox(text)
        if toolTip:
            w.setToolTip(toolTip)
        self.buttons.addButton(w,self.items.keys().index(id))
        self.box.layout().addWidget(w)
                    
    def setSizePolicy(self, h,w):
        # self.controlArea.setSizePolicy(h,w)
        # QWidget.setSizePolicy(self,h,w)
        self.box.setSizePolicy(h,w)
            
    def setChecked(self,ids):
        """Sets the keys listed in ids to checked"""
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if unicode(self.items.keys()[id]) in ids: i.setChecked(True)
            else: i.setChecked(False)
    
    def checkAll(self):
        """Checks all of the buttons"""
        for i in self.buttons.buttons():
            i.setChecked(True)
    def uncheckAll(self):
        """Unchecks all of the buttons"""
        for i in self.buttons.buttons():
            i.setChecked(False)
    def clear(self):
        """Removes all buttons from the widget.  Should be called before an end developer calls addButtons"""
        self.items = {}
        for i in self.buttons.buttons():
            self.removeButton(i)
    def getChecked(self):
        """Returns a list of checked button's labels"""
        return self.getCheckedItems().values()
        
    def getCheckedIds(self):
        """Returns a list of checked button's IDs"""
        return self.getCheckedItems().keys()
        
    def getCheckedItems(self):
        """Returns a dict of checked keys and labels"""
        checked = {}
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if i.isChecked(): checked[self.items.keys()[id]] = self.items[self.items.keys()[id]]
        return checked
    def getUncheckedItems(self):
        """Returns a dict of unchecked keys and labels"""
        checked = {}
        for i in self.buttons.buttons():
            id = self.buttons.id(i)
            if not i.isChecked(): checked[self.items.keys()[id]] = self.items[self.items.keys()[id]]
        return checked
    def getUnchecked(self):
        """Same as getChecked but reversed"""
        return self.getUncheckedItems.values()
    def getUncheckedIds(self):
        """Same as getCheckedIds but reversed"""
        return self.getUncheckedItems.keys()
    
    def buttonAt(self,ind):
        """Returns the button at a given index"""
        return unicode(self.buttons.button(ind).text())
                
    def getSettings(self):
        """Called by :mod:`widgetSettings` to get settings"""
        #print _('radioButtons getSettings') + self.getChecked()
        r = {'items':self.items, 'checked': self.getCheckedIds()}
        return r
    def loadSettings(self,data):
        """Called by :mod:`widgetSettings` to set settings"""
        #print _('radioButtons loadSettings') + data
        #self.addButtons(data['items'])
        self.setChecked(data['checked'])
        
    def getReportText(self, fileDir):
        """Returns report text for report generator"""
        selected = self.getChecked()

        if len(selected):
            text='Checked: ' + ', '.join(selected)
        else:
            text= _('Nothing Checked')
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': text}}
        # print '@@@@@@@@@@@@@@@@@@@@@@@', r
        #t = 'The following items were checked in %s:\n\n%s\n\n' % (self.label, self.getChecked())
        return r
        
class widgetLabel(QLabel,widgetState):
    def __init__(self,widget,label = '', icon=None, wordWrap=False,sizePolicy=QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)):
        widgetState.__init__(self,widget, _('widgetLabel'),includeInReports=False)
        QLabel.__init__(self,self.controlArea)
        self.controlArea.layout().addWidget(self)
        if icon:
            label = "<img style='margin-left:5px' src=\"%s\" /> %s" % (icon, label)
        self.setText(label)
        self.setWordWrap(wordWrap)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        if not sizePolicy:
            self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
        else:
            self.setSizePolicy(sizePolicy)
        #self.connect(self, SIGNAL('linkActivated (const QString&)'), self.followLink)
    def text(self):
        """Returns the text of the label"""
        return unicode(QLabel.text(self))
    def getSettings(self):
        # print _('in widgetLabel getSettings')
        r = {'text':self.text()}
        # print r
        return r
    def loadSettings(self,data):
        # print _('in widgetLabel loadSettings')
        # print data
        self.setText(data['text'])
        
    #def followLink(self, link):
        #import webbrowser
        #webbrowser.open_new(unicode(link))
        
class statusLabel(QLabel,widgetState):
    def __init__(self,widget,label = '', wordWrap=True):
        widgetState.__init__(self, widget, 'statusLabel',includeInReports=False)
        QLabel.__init__(self,self.controlArea)
        # if icon:
            # icon = QIcon(icon)
            # box = redRWidgetBox(widget,orientation='horizontal')
            # box.layout().addWidget(icon)
            # box.layout().addWidget(self)
        # else:
        #widget.layout().addWidget(self)
        
        box = widgetBox(self.controlArea,orientation='horizontal')
        
        self.controlArea.layout().addWidget(box)
        box.layout().addWidget(self)
        
        #self.statusIndicator = redRwidgetLabel(box,label='aaaaa  ')
        #widget.layout().addWidget(self.statusIndicator)
        self.status = 0
        self.setText(label)
        self.setWordWrap(wordWrap)
        
    def getSettings(self):
        """Standard getSettings functions"""
        # print _('in widgetLabel getSettings')
        r = {'text':self.text(),'status':self.status}
        print r
        return r
    def loadSettings(self,data):
        """Standard loadSettings functions"""
        # print _('in widgetLabel loadSettings')
        print data
        self.setText(data['text'])
        self.setStatus(data['status'])
    def getReportText(self, fileDir):
        """Returns current status"""
        return uncode(self.text())
        
    def setText(self, string,color=None):
        """Sets the text of the label, color can be specified to change the background color"""
        # self.setStyleSheet("QLabel { background-color: #ffff00 }")
        #string = '<table><tr><td class="indicator">aaaaa</td><td>%s</td></tr></table>' % string
        if color:
            self.setStyleSheet("QLabel { background-color: %s }" % color)
            
        QLabel.setText(self, string)
        qApp.processEvents()    
    def setStatus(self, statusInt):
        """Sets the status to one of several prespecified status values, see source code for a list and explaination"""
        self.status = statusInt
        if statusInt == 0: ## No valid data
            self.setText(_('No Data To Process'))
        elif statusInt == 1: ## New data not processed
            self.setText(_('New Data Received, Not Processed'),'#ffff00')
        elif statusInt == 2: ## data sent
            self.setText(_('Data Processed And Sent'),'#00ff00')
        elif statusInt == 3: ## Error
            self.setText(_('Error'),'#ff0000')
        elif statusInt == 4: ## Data Processing    
            self.setText(_('Data Processing...'),'#ffff00')
        elif statusInt == 5: ## Data Processing Complete
            self.setText(_('Data Processing Complete'),'#ffff00')
        

        qApp.processEvents()    
        
        
class widgetBox(QWidget,widgetState):
    def __init__(self,widget, orientation='vertical', addSpace=False, includeInReports=True,
    sizePolicy = None, margin = -1, spacing = -1, addToLayout = 1, alignment=Qt.AlignTop, helpButton = False):

        widgetState.__init__(self,widget, _('WidgetBox'),includeInReports)
        QWidget.__init__(self,self.controlArea)
            
        self.controlArea.layout().addWidget(self)
        # self.setFlat(flat)
        # if widget and widget.layout():
            # widget.layout().addWidget(self)
        
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            elif orientation == 'grid':
                self.setLayout(QGridLayout())
            else:
               self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
            
        if self.layout() == 0 or self.layout() == None:
            self.setLayout(QVBoxLayout())
        if helpButton:
            icon = QPixmap(os.path.join(redREnviron.directoryNames['redRDir'], 'canvas', 'icons', 'information.png'))
            tlabel = QLabel()
            tlabel.setPixmap(icon)
            self.layout().addWidget(tlabel)

            
        self.controlArea.layout().setAlignment(alignment)            

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin == -1: margin = 0
        if margin != -1:
            self.layout().setMargin(margin)
        if widget:
            if addSpace and isinstance(addSpace, int):
                separator(self.controlArea, 0, addSpace)
            elif addSpace:
                separator(self.controlArea)
        if sizePolicy:
            self.setSizePolicy(sizePolicy)
    
    def layout(self):
        return QWidget.layout(self)
    
    def delete(self):
        # itemRange = self.layout().count()
        # for i in range(0, itemRange):
            # item = self.layout().itemAt(i)
            # if item.widget:
                # try:
                    # item.widget.delete()
                # except: pass
            # sip.delete(item)
        sip.delete(self)

class button(QPushButton,widgetState):
    """Basic button and checkbutton class.
    
    This is the base class for buttons.  By buttons we mean pushbuttons.  The button can also act as a checkbutton.  Checkbuttons remain checked or unchecked when clicked.
    """
    
    def __init__(self,widget,label, callback = None, disabled=0, icon=None, 
    toolTip=None, width = None, height = None,alignment=Qt.AlignLeft, toggleButton = False, setChecked = False):

        if icon and (not label or label == ''):
            widgetState.__init__(self,widget,os.path.basename(icon),includeInReports=False)
        else:
            widgetState.__init__(self,widget,label,includeInReports=False)
            
        if icon:
            QPushButton.__init__(self,QIcon(icon), label,self.controlArea)
        else:
            QPushButton.__init__(self,label,self.controlArea)

        self.controlArea.layout().addWidget(self)
        if alignment:
            self.controlArea.layout().setAlignment(self, alignment)
        
        if icon or width == -1:
            pass
        elif width: 
            self.setFixedWidth(width)
#        elif len(label)*7+5 < 50:
#            self.setFixedWidth(50)
#        else:
#            self.setFixedWidth(len(label)*7+5)
            
        if height:
            self.setFixedHeight(height)
        self.setDisabled(disabled)
        
        if toolTip:
            self.setToolTip(toolTip)
            
        if toggleButton:
            self.setCheckable(True)
            if setChecked:
                self.setChecked(True)
        if callback:
            QObject.connect(self, SIGNAL("clicked()"), callback)
            
            
    def getSettings(self):
        """Returns settings for checked state, applicable only if this is a checkbutton"""
        return {'checked': self.isChecked()}
    def loadSettings(self,data):
        """Sets the button to checked or not.  Only applicable if the button is a checkbutton."""
        if self.checkable():
            if 'checked' in data.keys():
                self.setChecked(data['checked'])
                
def startProgressBar(title,text,max):
    """Starts a progress bar.  This helps the user to know how long addition of items will take"""
    progressBar = QProgressDialog()
    progressBar.setCancelButtonText(QString())
    progressBar.setWindowTitle(title)
    progressBar.setLabelText(text)
    progressBar.setMaximum(max)
    progressBar.setValue(0)
    progressBar.show()
    return progressBar
    
class listBox(QListWidget,widgetState):
    def __init__(self, widget, value=None, label=None, displayLabel=True, includeInReports=True, 
    orientation='vertical', selectionMode=QAbstractItemView.SingleSelection,
    enableDragDrop = 0, dragDropCallback = None, dataValidityCallback = None, sizeHint = None, 
    callback=None, toolTip = None, items = None, *args):
        
        widgetState.__init__(self,widget,label,includeInReports)
        QListWidget.__init__(self, *args)
        self.label = label
        self.widget = self.controlArea
        if displayLabel:
            self.hb = groupBox(self.controlArea,label=label,orientation=orientation)
            
        else:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            
        self.hb.layout().addWidget(self)
        self.ogValue = value
        self.ogLabels = label
        self.enableDragDrop = enableDragDrop
        self.dragDopCallback = dragDropCallback
        self.dataValidityCallback = dataValidityCallback
        if not sizeHint:
            self.defaultSizeHint = QSize(150,100)
        else:
            self.defaultSizeHint = sizeHint
        self.setSelectionMode(selectionMode)
        if enableDragDrop:
            self.setDragEnabled(1)
            self.setAcceptDrops(1)
            self.setDropIndicatorShown(1)
            #self.setDragDropMode(QAbstractItemView.DragDrop)
            
            self.dragStartPosition = 0
        if toolTip:
            self.setToolTip(toolTip)
        
        self.listItems = OrderedDict()
        if items:
            self.addItems(items)
        
        if callback:
            QObject.connect(self, SIGNAL('itemClicked(QListWidgetItem*)'), callback)



    def getItems(self):
        """Returns an OrderedDict of the items (key, value) in the listBox, this can be treated as a dict also."""
        return self.listItems

    def addItem(self,id,item):
        QListWidget.addItem(self,item)
        self.listItems[id] = item
    def addItems(self,items):
        progressBar = startProgressBar('Setting List Items', '', len(items))
        progress = 0
        if type(items) in [dict,OrderedDict]:
            
            for k,v in items.items():
                self.addItem(k,v)
                progress += 1
                progressBar.setValue(progress)
            
        elif type(items) in [list]:
            progressBar = startProgressBar('Setting List Items', '', len(items))
            if len(items) > 0 and type(items[0]) is tuple:
                for k,v in items:
                    self.addItem(k,v)
                    progress += 1
                    progressBar.setValue(progress)
            else:
                for v in items:
                    self.addItem(v,v)
                    progress += 1
                    progressBar.setValue(progress)
            # redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,_('In listBox should not use list'))
        else:
            progressBar.hide()
            raise Exception(_('In listBox, addItems takes a list, dict or OrderedDict'))
        progressBar.hide()
    def setSelectedIds(self,ids):
        """Sets a list of ids (ids) to be selected."""
        if ids == None: return
        progressBar = startProgressBar('Setting Selected Items', '', len(ids))
        progress = 0
        for x in ids:
            try:
                self.item(self.listItems.keys().index(x)).setSelected(True)
            except:
                pass
            progress += 1
            progressBar.setValue(progress)
    def update(self, items):
        """Clears the list, adds new items, and sets any selected items in the old list to being selected in the new list (if they exist of course)."""
        current = self.selectedIds()
        self.clear()
        self.addItems(items)
        self.setSelectedIds(current)
        

    def clear(self):
        """Clears the list"""
        QListWidget.clear(self)
        self.listItems = OrderedDict()

    def invertSelection(self):
        for i in range(self.count()):
            if self.isItemSelected(self.item(i)):
                self.item(i).setSelected(False)
            else:
                self.item(i).setSelected(True)
    
    def selectionCount(self):
        return len(self.selectedIndexes())
    def currentSelection(self):
        """Returns a list of selected values (the text in the list)"""
        return self.selectedItems().values()
    def selectedItems(self):
        """Returns a dict of selected items."""
        items = {}
        for x in self.selectedIndexes():
            items[self.listItems.keys()[x.row()]] = self.listItems.values()[x.row()]
        return items
    def selectedIds(self):
        """Returns a list of selected ids"""
        ids = []
        for x in self.selectedIndexes():
            ids.append(self.listItems.keys()[x.row()])
        return ids
        
    #def setSelectedIds(self, ids):
        #if ids == None: return
        #for i in range(self.count()):
            #if self.listItems.keys()[i] in ids:
                #self.item(i).setSelect(True)
    
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

        mime.setText(unicode(selectedItems))
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
            selectedItemIndices = eval(unicode(ev.mimeData().text()))

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
            
            ## whatever all of this does we need to execute the function to update the items
            self.updateRedRItems()
        else:
            ev.ignore()

    def updateRedRItems(self):
        """Updates the items in the list to a new order."""
        ## we go through all of the items and remake the items OrderedDict
        newDict = OrderedDict()
        for r in range(self.count()):
            t = unicode(self.item(r).text())  # get the text of the item
            if t not in self.listItems.values():
                newDict[t] = t
            else:
                for i, ov in self.listItems.items():
                    if ov == t:
                        newDict[i] = ov
        self.listItems = newDict
    def getSettings(self):
        print 'saving list box'
        r = {'items':self.listItems, 'selected':self.selectedIds()}
        print r
        return r
    def loadSettings(self,data):
        self.clear()
        self.addItems(data.get('items', []))
        self.setSelectedIds(data.get('selected', None))
    def getReportText(self, fileDir):
        items = self.getItems()
        selected = self.currentSelection()
        new = []
        
        for x in items:
            if x in selected:
                new.append([_('Selected'), x])
            else:
                new.append([_('Not Selected'),x])
        #print new
        text = redRReports.createTable(new,columnNames=[_('Selection'),_('Option')])
        # if text != '':
            # text += '\nSelected text has * in front'
        
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': text}}

        return r
        
class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None, displayLabel=True, includeInReports=True,
    id=None, orientation='horizontal', toolTip = None,  width = 0, callback = None, textChangedCallBack=None,
    sp='shrinking', **args):

        QLineEdit.__init__(self,widget)
        widgetState.__init__(self,widget,label,includeInReports)
        
        
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation, spacing=2)
            if sp == 'shrinking':
                self.hb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            lb = widgetLabel(self.hb, label)
            if width != -1:
                sb = widgetBox(self.hb)
                sb.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            self.hb.layout().addWidget(self)
            self.hb.layout().setAlignment(lb,Qt.AlignRight)
        else:
            self.controlArea.layout().addWidget(self)
        
        if toolTip and displayLabel: 
            self.hb.setToolTip(toolTip)
        elif toolTip:
            self.setToolTip(toolTip)
            
        if width == 0:
            self.setMaximumWidth(175)
            self.setMinimumWidth(175)
        elif width == -1:
            pass
        else:
            self.setMaximumWidth(width)
            self.setMinimumWidth(width)
        self.setText(text)
        self.id = id
        self.label = label
        # self.setText('asdf')
        if callback:
            QObject.connect(self, SIGNAL('returnPressed()'), callback)
        
        if textChangedCallBack:
            QObject.connect(self, SIGNAL('textEdited(QString)'), textChangedCallBack)
            
    def hide(self):
        ##print 'hiding in qtcore'
        self.controlArea.hide()
    def showToolTip(self):
        return
    def text(self):
        return unicode(QLineEdit.text(self))
    def widgetId(self):
        return self.id
    def widgetLabel(self):
        return self.label
    def getSettings(self):
        #print 'in get settings' + self.text()
        r = {'text': self.text(),'id': self.id}
        # print r
        return r
    def loadSettings(self,data):
        try:
            #print 'called load' + unicode(value)     
            self.setText(data['text'])
            if 'id' in data.keys():
                self.id = data['id']
            #self.setEnabled(data['enabled'])
        except:
            print _('Loading of lineEdit encountered an error.')
            
    def getReportText(self, fileDir):
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.text()}}
        return r

class groupBox(QGroupBox,widgetState):
    def __init__(self,widget, label = None, displayLabel=True, includeInReports=True,
    orientation='vertical', addSpace=False, 
    sizePolicy = None, margin = -1, spacing = -1, flat = 0,alignment=Qt.AlignTop):        
        if label:
            widgetState.__init__(self,widget,label,includeInReports)
        else:
            widgetState.__init__(self,widget,_('Group Box'),includeInReports)
        
        if displayLabel:
            QGroupBox.__init__(self,label)
        else:
            QGroupBox.__init__(self)
       
        self.label = label
        self.controlArea.layout().addWidget(self)
        
        self.controlArea.layout().setAlignment(alignment)            

        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            else:
                self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
            
        if self.layout() == 0 or self.layout() == None:
            self.setLayout(QVBoxLayout())

        if spacing == -1: spacing = 8
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)
        if widget:
            if addSpace and isinstance(addSpace, int):
                separator(self.controlArea, 0, addSpace)
            elif addSpace:
                separator(self.controlArea)
        
        if sizePolicy:
            self.setSizePolicy(sizePolicy)
        

    def layout(self):
        return QGroupBox.layout(self)
    
    def delete(self):
        
        # itemRange = self.layout().count()
        # for i in range(0, itemRange):
            # item = self.layout().itemAt(i)
            # if item.widget:
                # try:
                    # item.widget.delete()
                # except: pass
            # sip.delete(item)
        sip.delete(self)
        
        
class lineEditHint(lineEdit):        
    def __init__(self, widget, label=None, displayLabel=True,includeInReports=True,orientation='horizontal', 
    items = [], toolTip = None,  width = 0, callback = None, **args):
        
        
        #widgetState.__init__(self,label,includeInReports)
        lineEdit.__init__(self, widget = widget, label = label, displayLabel=displayLabel,
        orientation = orientation, toolTip = toolTip, width = width, **args)
        
        QObject.connect(self, SIGNAL("textEdited(const QString &)"), self.textEdited)
        self.enteredText = ""
        self.itemList = []
        self.useRE = 0
        if callback:
            self.callbackOnComplete = callback
        self.listUpdateCallback = None
        self.autoSizeListWidget = 0
        self.caseSensitive = 1
        self.matchAnywhere = 1
        self.nrOfSuggestions = 50
        self.minTextLength = 1
        #self.setDelimiters(",; ")
        self.delimiters = None          # by default, we only allow selection of one element
        self.itemsAsStrings = []        # a list of strings that appear in the list widget
        self.itemsAsItems = items          # can be a list of QListWidgetItems or a list of strings (the same as self.itemsAsStrings)
        self.listWidget = QListWidget()
        self.listWidget.setMouseTracking(1)
        self.listWidget.installEventFilter(self)
        self.listWidget.setWindowFlags(Qt.Popup)
        self.listWidget.setFocusPolicy(Qt.NoFocus)
        QObject.connect(self.listWidget, SIGNAL("itemClicked (QListWidgetItem *)"), self.doneCompletion)
        
    def setItems(self, items):
        if type(items) == numpy.ndarray:
            items = list(items) # need to correct for the case that we get a numpy object
        
        elif type(items) in [str, numpy.string_, numpy.float64]:
            items = [unicode(items)]
        
        if items:
            self.itemsAsItems = items
            if (type(items[0]) in [str, unicode]) or (type(items[0]) == numpy.string_):
                self.itemsAsStrings = items
            elif type(items[0]) in [numpy.float64]:
                self.itemsAsStrings = [unicode(item) for item in items]
            elif type(items[0]) == QListWidgetItem:     self.itemsAsStrings = [unicode(item.text()) for item in items]
            else:                                       print _("SuggestLineEdit error: unsupported type for the items: ")+unicode(type(items[0]))
        else:
            self.itemsAsItems = []
            self.itemsAsStrings = [] 
    def addItems(self, items):
        if type(items) == numpy.ndarray:
            items = list(items) # need to correct for the case that we get a numpy object
        
        elif type(items) in [str, numpy.string_, numpy.float64]:
            items = [unicode(items)]
        
        if items:
            self.itemsAsItems += items
            if (type(items[0]) == str) or (type(items[0]) == numpy.string_):
                self.itemsAsStrings += items
            elif type(items[0]) in [numpy.float64]:
                self.itemsAsStrings += [unicode(item) for item in items]
            elif type(items[0]) == QListWidgetItem:
                self.itemsAsStrings += [unicode(item.text()) for item in items]
            else:
                print _("SuggestLineEdit error: unsupported type for the items: ")+unicode(type(items[0]))
         
    def setDelimiters(self, delimiters):
        self.delimiters = delimiters
        if delimiters:
            self.translation = string.maketrans(self.delimiters, self.delimiters[0] * len(self.delimiters))
        
    def eventFilter(self, object, ev):
        try: # a wrapper that prevents problems for the listbox debigging should remove this
            if object != self.listWidget:
                return 0
            
            if ev.type() == QEvent.MouseButtonPress:
                self.listWidget.hide()
                return 1
                    
            consumed = 0
            if ev.type() == QEvent.KeyPress:
                consumed = 1
                if ev.key() in [Qt.Key_Enter, Qt.Key_Return]:
                    self.doneCompletion()
                elif ev.key() == Qt.Key_Escape:
                    self.listWidget.hide()
                    #self.setFocus()
                elif ev.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown]:
                    self.listWidget.setFocus()
                    self.listWidget.event(ev)
                else:
                    #self.setFocus()
                    self.event(ev)
            return consumed
        except: return 0
        
    def doneCompletion(self, *args):
        if self.listWidget.isVisible():
            if len(args) == 1:  itemText = unicode(args[0].text())
            else:               itemText = unicode(self.listWidget.currentItem().text())
            last = self.getLastTextItem()
            self.setText(unicode(self.text()).rstrip(last) + itemText)
            self.listWidget.hide()
            self.setFocus()
        if self.callbackOnComplete:
            QTimer.singleShot(0, self.callbackOnComplete)
            #self.callbackOnComplete()

    
    def textEdited(self):
        # if we haven't typed anything yet we hide the list widget
        if self.getLastTextItem() == "" or len(unicode(self.text())) < self.minTextLength:
            self.listWidget.hide()
        else:
            self.updateSuggestedItems()
    
    def getLastTextItem(self):
        text = unicode(self.text())
        if len(text) == 0: return ""
        if not self.delimiters: return unicode(self.text())     # if no delimiters, return full text
        if text[-1] in self.delimiters: return ""
        return text.translate(self.translation).split(self.delimiters[0])[-1]       # last word that we want to help to complete
    
    def updateSuggestedItems(self):
        self.listWidget.setUpdatesEnabled(0)
        self.listWidget.clear()
        
        last = self.getLastTextItem()
        tuples = zip(self.itemsAsStrings, self.itemsAsItems)
        if not self.caseSensitive:
            tuples = [(text.lower(), item) for (text, item) in tuples]
            last = last.lower()
            
        if self.useRE:
            try:
                pattern = re.compile(last)
                tuples = [(text, item) for (text, item) in tuples if pattern.match(text)]
            except:
                tuples = zip(self.itemsAsStrings, self.itemsAsItems)        # in case we make regular expressions crash we show all items
        else:
            if self.matchAnywhere:  tuples = [(text, item) for (text, item) in tuples if last in text]
            else:                   tuples = [(text, item) for (text, item) in tuples if text.startswith(last)]
        
        items = [tup[1] for tup in tuples]
        if items:
            if type(items[0]) == str:
                self.listWidget.addItems(items)
            else:
                for item in items:
                    self.listWidget.addItem(QListWidgetItem(item))
            self.listWidget.setCurrentRow(0)

            self.listWidget.setUpdatesEnabled(1)
            width = max(self.width(), self.autoSizeListWidget and self.listWidget.sizeHintForColumn(0)+10)
            if self.autoSizeListWidget:
                self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
            self.listWidget.resize(width, self.listWidget.sizeHintForRow(0) * (min(self.nrOfSuggestions, len(items)))+5)
            self.listWidget.move(self.mapToGlobal(QPoint(0, self.height())))
            self.listWidget.show()
##            if not self.delimiters and items and not self.matchAnywhere:
##                self.setText(last + unicode(items[0].text())[len(last):])
##                self.setSelection(len(unicode(self.text())), -(len(unicode(self.text()))-len(last)))            
##            self.setFocus()
        else:
            self.listWidget.hide()
            return
        
        if self.listUpdateCallback:
            self.listUpdateCallback()
            
    def getSettings(self):
        settings = {}
        settings['lesettings'] = lineEditHint.getSettings(self)
        settings['itemsAsStrings'] = self.itemsAsStrings
        return settings
    def loadSettings(self, settings):
        try:
            lineEditHint.loadSettings(self, settings['lesettings'])
            self.itemsAsStrings = settings['itemsAsStrings']
        except:
            print _('Loading of lineEditHint encountered an error.')
            
    def getReportText(self, fileDir):
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.text()}}
        return r

class separator(QWidget,widgetState):
    def __init__(self,widget,width=8, height=8):
        widgetState.__init__(self, widget, 'separator',includeInReports=False)
        QWidget.__init__(self,self.controlArea)
        self.controlArea.layout().addWidget(self)       
        self.setFixedSize(width, height)
        
class textEdit(QTextEdit,widgetState):
    def __init__(self,widget,html='',label=None, displayLabel=True,includeInReports=True, 
    orientation='vertical', alignment=None, editable=True, printable=False,clearable=False,**args):

        widgetState.__init__(self,widget, label,includeInReports)

        QTextEdit.__init__(self,self.controlArea)
        self.label = label
        if displayLabel:
            self.hb = groupBox(self.controlArea,label=label,orientation=orientation)
        else:
            self.hb = widgetBox(self.controlArea,orientation=orientation)

        self.hb.layout().addWidget(self)
        if alignment:
            self.controlArea.layout().setAlignment(self.hb,alignment)
        if printable:
            button(self.hb, _("Print"), self.printMe)
        if clearable:
            button(self.hb, _("Clear"), callback = self.clear)
        if not editable:
            self.setReadOnly(True)
        self.setFontFamily('Courier')
        self.insertHtml(html)
        
        
    def sizeHint(self):
        return QSize(1,1)
    def setCursorToEnd(self):
        """Places the cursor to the end of the document.  Required if you want to add text and there is the possibility that the user moved the cursor somewhere."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
    def getSettings(self):
        # print _('in textEdit getSettings')
        r = {'text': self.toHtml()}
        # print r['text']
        return r
    def loadSettings(self,data):
        self.clear()
        self.insertHtml(data['text'])
        # self.setEnabled(data['enabled'])
    def toPlainText(self):
        return unicode(QTextEdit.toPlainText(self))
    def getReportText(self,fileDir):
        limit = min(100000,len(self.toPlainText()))
        return {self.widgetName:{'includeInReports': self.includeInReports, 'type': 'litralBlock',
        'text': self.toPlainText()[0:limit], 'numChrLimit': limit}}
        
    def printMe(self):
        """Prints the current text in the textEdit to the printer."""
        printer = QPrinter()
        printDialog = QPrintDialog(printer)
        if printDialog.exec_() == QDialog.Rejected: 
            print _('Printing Rejected')
            return
        self.print_(printer)
        


class SearchDialog(QDialog,widgetState):
    def __init__(self, caption = _('Search Dialog'), url = '', icon = None, orientation = 'horizontal'):
        widgetState.__init__(self,None, _('SearchDialog'),includeInReports=False)
        QDialog.__init__(self)
        
        self.setWindowTitle(caption)
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            else:
                self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
        self.thisLayout = self.layout()
        self.webView = webViewBox(self,label=_('Search Dialog'), displayLabel=False)
        self.setMinimumSize(600, 400)
        if url and url != '':
            self.webView.load(QUrl(url))
        
        if icon:
            self.setWindowIcon(icon)
            
    def updateUrl(self, url):
        self.webView.load(QUrl(url))