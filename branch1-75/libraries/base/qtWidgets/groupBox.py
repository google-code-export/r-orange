from redRGUI import widgetState
import redRGUI

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class groupBox(QGroupBox,widgetState):
    def __init__(self,widget, label = None, orientation='vertical', addSpace=False, sizePolicy = None, margin = -1, spacing = -1, flat = 0):
        if label:
            QGroupBox.__init__(self,label)
        else:
            QGroupBox.__init__(self)
       
        
        widget.layout().addWidget(self)

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

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)
        else:
            self.layout().setMargin(4)
        if addSpace and isinstance(addSpace, int):
            redRGUI.separator(widget, 0, addSpace)
        elif addSpace:
            redRGUI.separator(widget)
        
        if sizePolicy:
            self.setSizePolicy(sizePolicy)

    # def getSettings(self):
        # return self.getState()
    # def loadSettings(self,data):
        # self.setState(data)
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
    def getReportText(self, fileDir):
        print 'getting report for widgetBox'
        children = self.children()
        print children
        text = ''
        for i in children:
            try:
                text += i.getReportText(fileDir)
            except Exception as inst:
                print inst
                continue
        print text
        return text

        

