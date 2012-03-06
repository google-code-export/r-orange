"""File Names Combo Box

Display the names of files in a comboBox.

"""
from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.comboBox import comboBox
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRi18n
_ = redRi18n.get_(package = 'base')
class fileNamesComboBox(comboBox,widgetState):
    def __init__(self,widget,label=None, displayLabel=True,files=None, editable=False,orientation='horizontal',callback = None, **kwargs):
        kwargs.setdefault('includeInReports', True)
        kwargs.setdefault('sizePolicy', QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        
        comboBox.__init__(self,widget,label=label,displayLabel=displayLabel,
        items=None, orientation=orientation,editable=editable,
        callback=callback, **kwargs)
        
        self.setAcceptDrops(True)
        self.label = label
        
        if files:
            self.files = files
        else:
            self.files=[_('Select File')]
        if 'fileFilterString' in kwargs:
            self.fileFilterString = kwargs['fileFilterString']
        else:
            self.fileFilterString = ''
        self.setFileList()
        QObject.connect(self, SIGNAL('activated(const QString&)'), self.openFile)
        
    def getSettings(self):
        r = {'files':self.files,'current':self.currentText()}
        # print r
        return r
        
    def openFile(self, string):
        print string
        if str(string) == _('Select File'):
            
            
            fn = QFileDialog.getOpenFileName(self, _("Open File"), redREnviron.settings['workingDir'], self.fileFilterString)
            #print unicode(fn)
            if fn.isEmpty(): return
            self.addFile(fn)
            
    def loadSettings(self,data):
        # print _('in comboBox load')
        # print data
        try:
            self.clear()
            self.files = [i for i in data['files']]
            self.setFileList()
            # self.addItems(self.files)
            ind = self.findText(data['current'])
            #print _('aaaaaaaaaaa'), ind
            if ind != -1:
                self.setCurrentIndex(ind)
            else:
                self.setCurrentIndex(0)
        except:
            print _('Loading of comboBox encountered an error.')
            import traceback,sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        

    def setFileList(self):
        """Sets a list of files."""
        #import copy
        if self.files == None: self.files = [_('Select File')]
        self.clear()
        #newFiles = []
        for file in self.files:
            #print type(file), file
            
            if os.path.exists(file) or file ==_('Select File'):
                self.addItem(file, os.path.basename(file))
                # newFiles.append(file)
            else:
                self.addItem(file, _('Not Found - ') + os.path.basename(file))
                #newFiles.append(file)
        #self.files = newFiles
        # print self.files
        # print len(self.files)
        if len(self.files) > 1:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)
            
        
    def addFile(self,fn):
        """Adds a file to the file list."""
        # print '@##############', type(fn), fn
        # for x in self.files:
            # print type(x),x
        
        import redREnviron, os
        fn = unicode(fn)
        redREnviron.settings['workingDir'] = os.path.split(fn)[0]
            
        if fn in self.files:
            self.files.remove(fn)
        self.files.insert(1,fn)
        self.setFileList()

        
    def getCurrentFile(self):
        if len(self.files) ==0 or self.currentIndex() == 0:
            return False
        return unicode(self.files[self.currentIndex()])
        
    def getReportText(self, fileDir):
        
        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.getCurrentFile()}}
        #return '%s set to %s' % (self.label, self.currentText())
        return r
        
    

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.addFile(links[0])
        else:
            event.ignore()
