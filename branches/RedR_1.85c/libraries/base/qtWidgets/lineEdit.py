"""Line Edit

Allows user to enter text into a single line.  Really the only functions that should be called are text().
"""

from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
import redREnviron
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')

class lineEdit(QLineEdit,widgetState):
    def __init__(self,widget,text='', label=None, displayLabel=True, id=None, orientation='horizontal', width = 0, callback = None, textChangedCallBack=None, sp='shrinking', **kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        widgetState.__init__(self,widget,label,**kwargs)
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
        """Returns the current text as unicode"""
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
            self.setText(data.get('text', ''))
            self.id = data.get('id', self.id)
        except:
            print _('Loading of lineEdit encountered an error.')
            
    def getReportText(self, fileDir):
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.text()}}
        return r