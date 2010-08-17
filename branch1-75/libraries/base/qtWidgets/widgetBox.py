from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

        
class widgetBox(QWidget,widgetState):
    def __init__(self,widget, orientation='vertical', addSpace=False, 
    sizePolicy = None, margin = -1, spacing = -1, addToLayout = 1, alignment=Qt.AlignTop):

        QWidget.__init__(self,widget)
            
        if margin == -1: margin = 0
        # self.setFlat(flat)
        if widget and widget.layout():
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

        if sizePolicy:
            self.setSizePolicy(sizePolicy)
        # else:
            # self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
        self.layout().setAlignment(alignment)            

        if spacing == -1: spacing = 8
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)

        if addSpace and isinstance(addSpace, int):
            separator(widget, 0, addSpace)
        elif addSpace:
            separator(widget)
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
        children = self.children()
        text = ''
        for i in children:
            try:
                text += i.getReportText(fileDir)
            except Exception as inst:
                print inst
                continue
        return text
        