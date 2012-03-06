"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>Load R Session</name>
    <icon>default.png</icon>
    <tags> 
        <tag>R</tag> 
    </tags>
    <summary></summary>
    <author>
        <authorname>Red-R Core Development Team</authorname>
        <authorcontact>www.red-r.org</authorcontact>
    </author>
</widgetXML>
"""

"""
<name>Load R Session</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI

import redRi18n
_ = redRi18n.get_(package = 'base')
class RLoader(OWRpy): 
    globalSettingsList = ['filecombo','path']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        """.. rrsignals::"""
        self.outputs.addOutput('id0', _('R Session'), signals.base.REnvironment)

        # print os.path.abspath('/')
        self.path = os.path.abspath('/')
        self.setRvariableNames(['sessionEnviron'])
        
        
        gbox = redRGUI.base.groupBox(self.controlArea,orientation='vertical',label=_('Select R session'))
        
        box = redRGUI.base.widgetBox(gbox,orientation='horizontal')
        self.filecombo = redRGUI.base.fileNamesComboBox(box,label=_('Session File'), displayLabel=False,
        orientation='vertical')
        self.filecombo.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)

        redRGUI.base.button(box, label=_('Browse'), callback = self.browseFile)
        self.commit = redRGUI.base.commitButton(gbox, label=_('Load Session'), callback = self.loadSession,
        alignment=Qt.AlignRight)
        #gbox.layout().setAlignment(self.commit,Qt.AlignRight)
        
        self.infoa = redRGUI.base.widgetLabel(self.controlArea, '')
        self.varBox = redRGUI.base.listBox(self.controlArea, label = _('Variables'))
        self.varBox.hide()
        self.infob = redRGUI.base.widgetLabel(self.controlArea, '')
    
    def browseFile(self): 
        fn = QFileDialog.getOpenFileName(self, _("Open File"), self.path, "R save file (*.RData *.rda);; All Files (*.*)")
        if fn.isEmpty(): return
        fn = unicode(fn)
        self.path = os.path.split(unicode(fn))[0]
        self.filecombo.addFile(fn)
        self.saveGlobalSettings()
        
    def loadSession(self, file = None):
        # open a dialog to pick a file and load it.
        self.R(self.Rvariables['sessionEnviron']+'<-new.env()', wantType = 'NoConversion') # make a new environment for the data
        file = self.filecombo.getCurrentFile()
        
        if not file: return
        self.R('load(\''+file+'\', '+self.Rvariables['sessionEnviron']+')', wantType = 'NoConversion') #load the saved session into a protective environment
        
        
        self.infoa.setText(_('Data loaded from %s') % unicode(file))
        self.varBox.show()
        dataList = self.R('local(ls(), '+self.Rvariables['sessionEnviron']+')', wantType = 'list')
        self.varBox.update(dataList)
        self.infob.setText(_('Please use the R Variable Separator widget to extract your data.'))
        newData = signals.base.REnvironment(self, data = self.Rvariables['sessionEnviron'])
        self.rSend('id0', newData)
        #self.status.setText('Data sent.')
        
    def customWidgetDelete(self):
        self.R('if(exists("' + self.Rvariables['sessionEnviron'] + '")) { local(rm(ls()), envir = ' + self.Rvariables['sessionEnviron'] + ')}', wantType = 'NoConversion')