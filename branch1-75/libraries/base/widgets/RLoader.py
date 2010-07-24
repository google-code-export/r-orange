"""
<name>Load R Session</name>
<author>Kyle R. Covington</author>
<description>Loads a previously saved Rdata session and allows the user to connect to a separator to send previously saved variables.  Should be used in conjunction with the R variable separator.</description>
<tags>R</tags>
<RFunctions>base:new.env,base:load</RFunctions>
<icon>rexecutor.png</icon>
<priority>10</priority>
"""
from OWRpy import * 
import redRGUI
import libraries.base.signalClasses.REnvironment as renv

class RLoader(OWRpy): 
    globalSettingsList = ['filecombo','path']

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.inputs = None
        self.outputs = [('R Session', renv.REnvironment)]
        print os.path.abspath('/')
        self.path = os.path.abspath('/')
        self.setRvariableNames(['sessionEnviron'])
        
        
        gbox = redRGUI.groupBox(self.controlArea,orientation='vertical',label='Select R session')
        
        box = redRGUI.widgetBox(gbox,orientation='horizontal')
        self.filecombo = redRGUI.fileNamesComboBox(box, orientation='vertical')
        self.filecombo.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)

        redRGUI.button(box, label='Browse', callback = self.browseFile)
        loadButton = redRGUI.button(gbox, label='Load Session', callback = self.loadSession)
        gbox.layout().setAlignment(loadButton,Qt.AlignRight)
        
        self.infoa = redRGUI.widgetLabel(self.controlArea, '')
        self.varBox = redRGUI.listBox(self.controlArea, label = 'Variables')
        self.varBox.hide()
        self.infob = redRGUI.widgetLabel(self.controlArea, '')
    
    def browseFile(self): 
        fn = QFileDialog.getOpenFileName(self, "Open File", self.path, "R save file (*.RData *.rda);; All Files (*.*)")
        if fn.isEmpty(): return
        self.path = os.path.split(str(fn))[0]
        self.filecombo.addFile(fn)
        self.saveGlobalSettings()
        
    def loadSession(self, file = None):
        # open a dialog to pick a file and load it.
        self.R(self.Rvariables['sessionEnviron']+'<-new.env()') # make a new environment for the data
        file = self.filecombo.getCurrentFile()
        
        if not file: return
        self.R('load(\''+file+'\', '+self.Rvariables['sessionEnviron']+')') #load the saved session into a protective environment
        
        
        self.infoa.setText('Data loaded from '+str(file))
        self.varBox.show()
        dataList = self.R('local(ls(), '+self.Rvariables['sessionEnviron']+')', wantType = 'list')
        self.varBox.update(dataList)
        self.infob.setText('Please use the R Variable Separator widget to extract your data.')
        newData = renv.REnvironment(data = self.Rvariables['sessionEnviron'])
        self.rSend('R Session', newData)
        #self.status.setText('Data sent.')
        
    def customWidgetDelete(self):
        self.R('if(exists("' + self.Rvariables['sessionEnviron'] + '")) { local(rm(ls()), envir = ' + self.Rvariables['sessionEnviron'] + ')}')