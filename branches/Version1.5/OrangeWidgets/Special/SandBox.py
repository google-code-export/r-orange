"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp
import redRGUI
import RAffyClasses

class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        self.lineEditText = ''
        self.loadSettings()
        self.inputs = None
        self.outputs = None
        self.R('data <- data.frame(a=rnorm(100),b=rnorm(100))')
        data = {'a':[1,2],'b':[3,4]}
        #self.table = Rtable(self.controlArea,Rdata = 'data')
        
        # self.table = table(self.controlArea,data = data)
        self.table2 = redRGUI.Rtable(self.controlArea,Rdata = 'data')        
        self.table2.setSelectionBehavior(QAbstractItemView.SelectRows)
