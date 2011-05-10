"""
<name>Remove NA</name>
<tags>R</tags>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import libraries.base.signalClasses.RMatrix as rmat
import redRi18n
_ = redRi18n.get_(package = 'base')
class na_omit(OWRpy): 
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.setRvariableNames(["na.omit"])
        self.data = {}
         
        self.RFunctionParam_object = ''
        self.inputs.addInput('id0', _('object'), signals.base.RVariable, self.processobject)

        self.outputs.addOutput('id0', _('R Data Frame'), signals.base.RDataFrame)
        self.outputs.addOutput('id1', _('R List'), signals.base.RList)
        self.outputs.addOutput('id2', _('R Vector'), signals.base.RVector)
        self.outputs.addOutput('id3', _('R.object'), signals.base.RVariable)

        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,
        processOnInput=True)
        
    def processobject(self, data):
        # if not self.require_librarys(["base"]):
            # self.status.setText('R Libraries Not Loaded.')
            # return
        if data:
            self.RFunctionParam_object=data.getData()
            self.data = data
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.RFunctionParam_object=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_object) == '': return
        
        self.R(self.Rvariables['na.omit']+'<-na.omit(object='+unicode(self.RFunctionParam_object)+')', wantType = 'NoConversion')
        thisdataclass = self.R('class('+self.Rvariables['na.omit']+')')
        if type(thisdataclass) == list: #this is a special R type so just send as generic
            self.rSend("id3", self.data)
        elif type(thisdataclass) == str:
            if thisdataclass == 'numeric': # we have a numeric vector as the object
                newData = signals.base.RVector(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id2", newData)
                self.status.setText(_('Data  sent through the R Vector channel'))
            elif thisdataclass == 'character': #we have a character vector as the object
                newData = signals.base.RVector(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id2", newData)
                self.status.setText(_('Data  sent through the R Vector channel'))
            elif thisdataclass == 'data.frame': # the object is a data.frame
                newData = signals.base.RDataFrame(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id0", newData)
                self.status.setText(_('Data  sent through the R Data Frame channel'))
            elif thisdataclass == 'matrix': # the object is a matrix
                newData = rmat.RMatrix(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id0", newData)
                self.status.setText(_('Data  sent through the R Data Frame channel'))
            elif thisdataclass == 'list': # the object is a list
                newData = signals.base.RList(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id1", newData)
                self.status.setText(_('Data  sent through the R List channel'))
            else:    # the data is of a non-normal type send anyway as generic
                newData = signals.base.RVariable(self, data = self.Rvariables['na.omit'])
                newData.dictAttrs = self.data.dictAttrs.copy()
                self.rSend("id3", newData)
                self.status.setText(_('Data  sent through the R Object channel'))
        else:
            newData = signals.base.RVariable(self, data = self.Rvariables['na.omit'])
            newData.dictAttrs = self.data.dictAttrs.copy()
            self.rSend("id3", newData)
            self.status.setText(_('Data  sent through the R Object channel'))
        
        
