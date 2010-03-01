"""
<name>Dummy</name>
<discription>A dummy widget to act as a placeholder if widget load fails</discription>
<author>Kyle R. Covington</author>
<tags>Special</tags>
<icon>icons/RExecutor.PNG</icon>
<priority>4010</priority>
"""
from OWRpy import * 
import OWGUI 
class dummy(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None, forceInSignals = None, forceOutSignals = None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = []
        self.outputs = []
        print str(forceInSignals) +' and ' + str(forceOutSignals) + ' appending to dummy'
        if forceInSignals: 
            import RvarClasses
            for a in forceInSignals:
                print 'Appending ' + str(a) + ' in dummy'
                
                self.inputs.append((a, RvarClasses.RVariable, None))
        if forceOutSignals:
            import RvarClasses
            for a in forceOutSignals:
                print 'Appending ' +str(a)+' in dummy'
                self.outputs.append((a, RvarClasses.RVariable))
        print self.inputs
        print self.outputs
            
        self.loadSettings()
        
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, "A widget failed to load this was put in it's place.")
        self.infob = OWGUI.widgetLabel(box, "The variables that were saved with this widget are %s .\n You can use R Executor to retrieve these variables and incorporate them into your schema." % str(self.sentItems))
        
    