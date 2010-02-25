"""
<name>Write eSet</name>
<description>Writes an eSet to a tab delimited file.</description>
<tags>microarray</tags>
<RFunctions>affy:write.exprs</RFunctions>
<icon>icons/readcel.png</icon>
<priority>80</priority>
"""

from rpy_options import set_options
set_options(RHOME='c:/progra~1/r/R-2.6.2/')
from rpy import *
from OWWidget import *
import redRGUI
r.require('affy')

class writeEset(OWWidget):
    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, "Sample Data")
        
        self.inputs = [("Affybatch", orange.Variable, self.nothingb)]
        self.outputs = None
        
        self.data = None
        self.fileName = ""
        
        #GUI
        box = redRGUI.widgetBox(self.controlArea, "Write to file.")
        redRGUI.lineEdit(box, self, "fileName", "File Name", orientation = "horizontal") 
        writeButton = redRGUI.button(box, self, "Write to file", callback = self.write, width=200)
        self.infoa = redRGUI.widgetLabel(box, "No output yet")
        
    def nothingb(self,data):
        if 'data' in data:
            self.data = data['data']
        else: return
            
    def write(self):
        if self.fileName == "":
            self.infoa.setText("You must input a valid file name.")
        elif self.data == None:
            self.infoa.setText("Data has not been loaded yet")
        else:
            r('write.exprs('+self.data+',file="'+self.fileName+'.txt", sep="\t")')
            self.infoa.setText("Data was writen to "+self.fileName+" successfully!")
        