"""Red-R qtWidget Core.  This is the core location of qtWidgets.  These should be used only by core for setting up qt functionality"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, re, string, numpy
import redRi18n, redREnviron
from redRGUI import widgetState
_ = redRi18n.Coreget_()

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

class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None, displayLabel=True, includeInReports=True,
    id=None, orientation='horizontal', toolTip = None,  width = 0, callback = None, textChangedCallBack=None,
    sp='shrinking', **args):

        widgetState.__init__(self,widget,label,includeInReports)
        QLineEdit.__init__(self,widget)
        
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