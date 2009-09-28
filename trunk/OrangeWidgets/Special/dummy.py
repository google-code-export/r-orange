"""
<name>Dummy</name>
<discription>A dummy widget to act as a placeholder if widget load fails</discription>
<author>Kyle R. Covington</author>
<icon>icons/Dummy.png</icon>
<priority>4010</priority>
"""
from OWRpy import * 
import OWGUI 
class dummy(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = []
        self.outputs = []
        self.loadSettings()
        self.setInputs()
        self.setOutputs()
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, "A widget failed to load this was put in it's place")
        
    def setInputs(self):
        temp = self.inputs
        self.inputs = []
        for input in temp:
            self.inputs.append((input[0], input[1]))
    
    def setOutputs(self):
        temp = self.outputs
        self.outputs = []
        for item in temp:
            self.outputs.append((item[0], item[1]))