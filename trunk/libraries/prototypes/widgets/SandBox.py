"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp, time
import redRGUI
import signals



class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.lineEditText = ''
        
        ### GUI ###
        self.textEdit = redRTextEdit(self.controlArea, label = 'output')
        redRCommitButton(self.controlArea, label = 'Commit', callback = self.runBench)
        self.R('a <- list(b = c(1,2,3), d = c(6,7,8))', wantType = 'NoConversion')
        
    def runBench(self):
        self.require_librarys(['compositions'])
        self.R('data(Hydrochem)', wantType = 'NoConversion')
        self.R('MyData<-Hydrochem[1:15, c("Na", "Mg", "Ca"), drop=F]', wantType = 'NoConversion')
        self.R('compData<-acomp(MyData)', wantType = 'NoConversion')
        self.textEdit.clear()
        #self.textEdit.insertPlainText(str(self.R(
        self.R('operVect<-acomp(c(1,2,3))', wantType = 'NoConversion')
        self.textEdit.insertPlainText(self.R('paste(capture.output(perturbe(operVect, compData)), collapse = "\\n")'))
        
        
        