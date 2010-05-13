"""
<name>Dummy</name>
<discription>A dummy widget to act as a placeholder if widget load fails</discription>
<author>Kyle R. Covington</author>
<tags>R</tags>
<icon>icons/dummy.png</icon>
<priority>4010</priority>
"""
from OWRpy import * 
import OWGUI 
class dummy(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None, forceInSignals = None, forceOutSignals = None):
        OWRpy.__init__(self, parent, signalManager, "Dummy Widget", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = []
        self.outputs = []
        print str(forceInSignals) +' and ' + str(forceOutSignals) + ' appending to dummy'
        if forceInSignals: 
            import signals
            for (a, b) in [signal for signal in forceInSignals]:
                print 'Appending ' + str(a) + ' in dummy to the '+str(b)+' signal'
                self.inputs.append((a, b, None))
        if forceOutSignals:
            import signals
            for (a, b) in [signal for signal in  forceOutSignals]:
                print 'Appending ' +str(a)+' in dummy using the '+str(b)+' signal'
                self.outputs.append((a, b))
        print self.inputs
        print self.outputs
            
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, "A widget failed to load this was put in it's place.")
        self.infob = OWGUI.widgetLabel(box, "The variables that were saved with this widget are %s .\n You can use R Executor to retrieve these variables and incorporate them into your schema." % str(self.sentItems))
        
    