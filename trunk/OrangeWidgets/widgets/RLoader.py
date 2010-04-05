"""
<name>Load R Session</name>
<author>Kyle R. Covington</author>
<description>Loads a previously saved Rdata session and allows the user to connect to a separator to send previously saved variables.  Should be used in conjunction with the R variable separator.</description>
<tags>R</tags>
<RFunctions>base:new.env,base:load</RFunctions>
<icon>icons/rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import OWGUI 
import redRGUI
class RLoader(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self,parent, signalManager, "RLoader", wantMainArea = 0, resizingEnabled = 1)
        self.loadSettings()
        self.inputs = None
        self.outputs = [('R Session', RvarClasses.RSession)]
        self.setRvariableNames(['sessionEnviron'])
        OWGUI.button(self.controlArea, self, 'Load Session', callback = self.loadSession)
        self.infoa = redRGUI.widgetLabel(self.controlArea, '')
    def loadSession(self):
        # open a dialog to pick a file and load it.
        self.R(self.Rvariables['sessionEnviron']+'<-new.env()') # make a new environment for the data
        if file == None and ('HomeFolder' not in qApp.canvasDlg.settings.keys()):
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['saveSchemaDir']), "RData (*.RData)"))
        elif file == None: 
            file = str(QFileDialog.getSaveFileName(self, "Save File", os.path.abspath(qApp.canvasDlg.settings['HomeFolder']), "RData (*.RData)"))
        if file.isEmpty(): return
        self.R('load('+file+', '+self.Rvariables['sessionEnviron']+')') #load the saved session into a protective environment
        
        # logic to handle exceptions to loading
        self.infoa.setText('Data loaded from '+str(file)+'. Please use the R Variable Separator widget to extract your data.')
        self.rSend('R Session', {'data':self.Rvariables['sessionEnviron']})
        self.status.setText('Session loaded from memory, please use the variable separator to parse the widget output.')