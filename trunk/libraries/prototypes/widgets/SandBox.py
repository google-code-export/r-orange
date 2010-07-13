"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp
import redRGUI
import signals
from libraries.conversion.signalClasses import *



class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.lineEditText = ''
        
        ### GUI ###
        
        self.lineEdit = redRGUI.lineEdit(self.controlArea, label = 'Line Edit')
        
        self.R('a <- list(b = c(1,2,3), d = c(6,7,8))')
        
        try:
            self.lineEdit.setText(str(signals.conversion.RArray)+' '+str(RArray))
        except:
            try:
                self.lineEdit.setText(str(RArray))
            except:
                try:
                    self.lineEdit.setText(str(signals.conversion.RArray))
                except:
                    self.lineEdit.setText('Not loaded')