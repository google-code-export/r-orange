"""
<name>R Loader</name>
<author>Kyle R. Covington</author>
<description>Loads a previously saved Rdata session and allows the user to connect to a separator to send previously saved variables.  Should be used in conjunction with the R variable separator.</description>
<tags>R</tags>
<icon>icons/RExecutor.PNG</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import RRGUI 
class RLoader(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self,parent, signalManager, "RLoader", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = None
        self.outputs = [('R Session', RvarClasses.RSession)]
        self.setRvariableNames(['sessionEnviron'])
        OWGUI.button(self.controlArea, self, 'Load Session', callback = self.loadSession)
    def loadSession(self):
        # open a dialog to pick a file and load it.
        self.R(self.Rvariables['sessionEnviron']+'<-new.env()') # make a new environment for the data
        self.R('load(choose.files(), '+self.Rvariables['sessionEnviron']+')') #load the saved session into a protective environment
        
        # logic to handle exceptions to loading
        self.rSend('R Session', {'data':self.Rvariables['sessionEnviron']})