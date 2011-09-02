"""
.. helpdoc::

"""

"""
<widgetXML>    
    <name>R Variable Selection</name>
    <icon>rexecutor.png</icon>
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
<name>R Variable Selection</name>
<tags>R</tags>
<icon>rexecutor.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import libraries.base.signalClasses.REnvironment as renv
import libraries.base.signalClasses.RVariable as rvar
import libraries.base.signalClasses.RVector as rvec
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RMatrix as rmat
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RArbitraryList as ral

import redRi18n
_ = redRi18n.get_(package = 'base')

class RVarSeparator(OWRpy): 
    globalSettingsList = ['commitButton']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(['savedvar'])
        """.. rrsignals::"""
        self.inputs.addInput('id0', _('R Environment'), renv.REnvironment, self.process)

        """.. rrsignals::"""
        self.outputs.addOutput('id0', _('R Session'), renv.REnvironment)
        
        """.. rrsignals::"""
        self.outputs.addOutput('id1', _('Non-Standard R Variable'), rvar.RVariable)
        
        """.. rrsignals::"""
        self.outputs.addOutput('id2', _('R Data Frame (Data Table)'), rdf.RDataFrame)
        
        """.. rrsignals::"""
        self.outputs.addOutput('id3', _('R List'), rlist.RList)
        
        """.. rrsignals::"""
        self.outputs.addOutput('id4', _('R Vector'), rvec.RVector)
        
        """.. rrsignals::"""
        self.outputs.addOutput('ral', _('R Arbitrary List'), ral.RArbitraryList)

       
        # self.help.setHtml('The R Variable Separator is used to separate variables from a loaded R session.  Connecting the R Loader widget to this widget will display a list of available variables in the local environment to which the session was loaded.  Clicking on an element in the list will send that element on to downstream widgets.  One should take note of the class of the element that is sent as this will specify the output connection of the data.  More infromation is available on the <a href="http://www.red-r.org/?cat=10">RedR website</a>.')

        self.controlArea.setMinimumWidth(300)
        self.varBox = redRGUI.base.listBox(self.controlArea, label = _('Variables'), callback = self.select)
        
        box = redRGUI.base.widgetBox(self.controlArea, orientation='horizontal') 
        #self.filecombo.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.controlArea.layout().setAlignment(box,Qt.AlignRight)
        
        self.commitButton = redRGUI.base.commitButton(box,label=_('Commit'),callback=self.commit,
        processOnInput=True,processOnChange=True)

    def process(self, data):
        if not data: return
        self.envName = data.getData()

        dataList = self.R('local(ls(), '+self.envName+')', wantType = 'list')
        
        if not dataList:
            self.status.setText(_('No data in the R session'))
            return 
        
        self.varBox.update(dataList)
        if self.commitButton.processOnInput():
            self.commit()
           
        
    def select(self):
        if self.commitButton.processOnChange():
            self.commit()
            
    def commit(self):
        #must declare explilcitly as a string or an error will occur.  We remove NA's just in case they are in the data
        self.sendThis = unicode('local('+self.varBox.selectedItems().values()[0]+', '+self.envName+')') 
        self.R('%s<-%s' % (self.Rvariables['savedvar'], self.sendThis), wantType = 'NoConversion') 
        
        #put logic for finding the type of variable that the object is and sending it from that channel of the output
        
        dataClass = self.R('class('+self.sendThis+')')
            
        if type(dataClass) is str:
            if dataClass in ['numeric', 'character', 'real', 'complex', 'factor']: # we have a numeric vector as the object
                newData = rvec.RVector(self, data = self.Rvariables['savedvar'])
                self.rSend('id4', newData)
                self.status.setText(_('Data sent through the R Vector channel'))
            elif dataClass == 'character': #we have a character vector as the object
                newData = rvec.RVector(self, data = self.Rvariables['savedvar'])
                self.rSend('id4', newData)
                self.status.setText(_('Data sent through the R Vector channel'))
            elif dataClass == 'data.frame': # the object is a data.frame
                newData = rdf.RDataFrame(self, data = self.Rvariables['savedvar'])
                self.rSend('id2', newData)
                self.status.setText(_('Data sent through the R Data Frame channel'))
            elif dataClass == 'matrix': # the object is a matrix
                
                newData = rmat.RMatrix(self, data = self.Rvariables['savedvar'])
                
                self.rSend('id2', newData)
                self.status.setText(_('Data sent through the R Data Frame channel'))
            elif dataClass == 'list': # the object is a list
                for i in range(self.R('length('+self.Rvariables['savedvar']+')')):
                    if self.R('class(%s[[%s]])' % (self.Rvariables['savedvar'], i), silent = True) not in ['numeric', 'character', 'real', 'complex', 'factor']:
                        newData = ral.RArbitraryList(self, data = self.Rvariables['savedvar'])
                        self.status.setText(_('Data sent through the R Arbitrary List channel'))
                        self.rSend('ral', newData)
                        return
                newData = rlist.RList(self, data = self.Rvariables['savedvar'])
                self.rSend('id3', newData)
                self.status.setText(_('Data sent through the R List channel'))
            else:    # the data is of a non-normal type send anyway as generic  
                newData = rvar.RVariable(self, data = self.Rvariables['savedvar'])
                self.rSend('id1', newData)
                self.status.setText(_('Data sent through the R Object channel'))
        else:
            newData = rvar.RVariable(self, data = self.Rvariables['savedvar'])
            self.rSend('id1', newData)
            self.status.setText(_('Data sent through the R Object channel'))
