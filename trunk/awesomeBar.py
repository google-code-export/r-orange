## Awesome bar.  sends and retrieves AJAX queries from a specified URL

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, re, string, numpy
from lineEdit import lineEdit


class lineEditHint(lineEdit):        
    def __init__(self, widget, label=None,orientation='horizontal', items = [], toolTip = None,  width = 0, callback = None, **args):
        lineEdit.__init__(self, widget = widget, label = label, orientation = orientation, toolTip = toolTip, width = width, **args)
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
        self.webView = QWebView()
        self.webView.setMouseTracking(1)
        self.webView.installEventFilter(self)
        self.webView.setWindowFlags(Qt.Popup)
        self.webView.setFocusPolicy(Qt.NoFocus)
        QObject.connect(self.webView, SIGNAL("itemClicked (QListWidgetItem *)"), self.doneCompletion)
        
    def setItems(self, items):
        if type(items) == numpy.ndarray:
            items = list(items) # need to correct for the case that we get a numpy object
        
        elif type(items) in [str, numpy.string_, numpy.float64]:
            items = [str(items)]
        
        if items:
            self.itemsAsItems = items
            if (type(items[0]) == str) or (type(items[0]) == numpy.string_):
                self.itemsAsStrings = items
            elif type(items[0]) in [numpy.float64]:
                self.itemsAsStrings = [str(item) for item in items]
            elif type(items[0]) == QListWidgetItem:     self.itemsAsStrings = [str(item.text()) for item in items]
            else:                                       print "SuggestLineEdit error: unsupported type for the items: "+str(type(items[0]))
        else:
            self.itemsAsItems = []
            self.itemsAsStrings = [] 
    def addItems(self, items):
        if type(items) == numpy.ndarray:
            items = list(items) # need to correct for the case that we get a numpy object
        
        elif type(items) in [str, numpy.string_, numpy.float64]:
            items = [str(items)]
        
        if items:
            self.itemsAsItems += items
            if (type(items[0]) == str) or (type(items[0]) == numpy.string_):
                self.itemsAsStrings += items
            elif type(items[0]) in [numpy.float64]:
                self.itemsAsStrings += [str(item) for item in items]
            elif type(items[0]) == QListWidgetItem:
                self.itemsAsStrings += [str(item.text()) for item in items]
            else:
                print "SuggestLineEdit error: unsupported type for the items: "+str(type(items[0]))
         
    def setDelimiters(self, delimiters):
        self.delimiters = delimiters
        if delimiters:
            self.translation = string.maketrans(self.delimiters, self.delimiters[0] * len(self.delimiters))
        
    def eventFilter(self, object, ev):
        try: # a wrapper that prevents problems for the listbox debigging should remove this
            if object != self.webView:
                return 0
            
            if ev.type() == QEvent.MouseButtonPress:
                self.webView.hide()
                return 1
                    
            consumed = 0
            if ev.type() == QEvent.KeyPress:
                consumed = 1
                if ev.key() in [Qt.Key_Enter, Qt.Key_Return]:
                    self.doneCompletion()
                elif ev.key() == Qt.Key_Escape:
                    self.webView.hide()
                    #self.setFocus()
                elif ev.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown]:
                    self.webView.setFocus()
                    self.webView.event(ev)
                else:
                    #self.setFocus()
                    self.event(ev)
            return consumed
        except: return 0
        
    def doneCompletion(self, *args):
        if self.webView.isVisible():
            if len(args) == 1:  itemText = str(args[0].text())
            else:               itemText = str(self.webView.currentItem().text())
            last = self.getLastTextItem()
            self.setText(str(self.text()).rstrip(last) + itemText)
            self.webView.hide()
            self.setFocus()
        if self.callbackOnComplete:
            QTimer.singleShot(0, self.callbackOnComplete)
            #self.callbackOnComplete()

    
    def textEdited(self):
        # if we haven't typed anything yet we hide the list widget
        if self.getLastTextItem() == "" or len(str(self.text())) < self.minTextLength:
            self.webView.hide()
        else:
            self.updateSuggestedItems()
    
    def getLastTextItem(self):
        text = str(self.text())
        if len(text) == 0: return ""
        if not self.delimiters: return str(self.text())     # if no delimiters, return full text
        if text[-1] in self.delimiters: return ""
        return text.translate(self.translation).split(self.delimiters[0])[-1]       # last word that we want to help to complete
    
    def updateSuggestedItems(self):
        #  run the query to the specified URL

        pass
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
            print 'Loading of lineEditHint encountered an error.'
            
    def setHtml(self, string):
        return 
"""
<html>
<head>
<script type="text/javascript">
function runQuery(str)
{
if (str=="")
  {
  document.getElementById("txtHint").innerHTML="Your Search Results Will Appear Hear";
  return;
  }  
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
xmlhttp.onreadystatechange=function()
  {
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
    document.getElementById("txtHint").innerHTML=xmlhttp.responseText;
    }
  }
xmlhttp.open("GET","http://www.red-r.org?s="+str+"t=" + Math.random(),true);
xmlhttp.send();
}

</script>
</head>
<body>

<br />
<div id="txtHint">Your Search Results Will Appear Hear</div>

</body>
onload="runQuery(\'%s\')"
</html>
"""