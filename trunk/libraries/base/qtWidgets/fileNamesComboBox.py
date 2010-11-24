#from redRGUI import widgetState

from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.comboBox import comboBox
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class fileNamesComboBox(comboBox):
    def __init__(self,widget,label=None, displayLabel=True,includeInReports=True, files=None, 
    orientation='horizontal',callback = None, callback2 = None, **args):

        #widgetState.__init__(self, widget, label, includeInReports)
        
        comboBox.__init__(self,widget,label=label,displayLabel=displayLabel,
        items=None, orientation=orientation,
        callback=callback,callback2=callback2, **args)
        
        self.label = label
        
        if files:
            self.files = files
        else:
            self.files=['Select File']
        self.setFileList()
        
        
    def getSettings(self):
        r = {'files':self.files,'current':self.currentText()}
        # print r
        return r
        
    def loadSettings(self,data):
        # print 'in comboBox load'
        # print data
        try:
            self.clear()
            self.files = [i for i in data['files']]
            self.setFileList()
            # self.addItems(self.files)
            ind = self.findText(data['current'])
            #print 'aaaaaaaaaaa', ind
            if ind != -1:
                self.setCurrentIndex(ind)
            else:
                self.setCurrentIndex(0)
        except:
            print 'Loading of comboBox encountered an error.'
            import traceback,sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60        

    def setFileList(self):
        #import copy
        if self.files == None: self.files = ['Select File']
        self.clear()
        #newFiles = []
        for file in self.files:
            #print type(file), file
            
            if os.path.exists(file) or file =='Select File':
                self.addItem(os.path.basename(file))
                # newFiles.append(file)
            else:
                self.addItem('Not Found - ' + os.path.basename(file))
                #newFiles.append(file)
        #self.files = newFiles
        # print self.files
        # print len(self.files)
        if len(self.files) > 1:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)
            
        
    def addFile(self,fn):
        # print '@##############', type(fn), fn
        # for x in self.files:
            # print type(x),x
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
