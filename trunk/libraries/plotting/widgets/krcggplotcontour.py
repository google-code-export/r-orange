"""
<name>Contour Plot</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import libraries.plotting.signalClasses as plotSignals


import redRi18n
_ = redRi18n.get_(package = 'plotting')
class krcggplotcontour(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.require_librarys(["ggplot2", "hexbin"])
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.setRvariableNames(["contour"])
        #self.dataFrame = ''
        #self.plotAttributes = {}
        #self.RFunctionParam_plotatt = ''
        self.inputs.addInput('id0', 'Data Table', signals.base.RDataFrame, self.processy)
        #self.inputs.addInput('id1', 'x', signals.base.RVector, self.processx)
        #self.inputs.addInput('id2', 'plotatt', redRRPlotAttribute, self.processplotatt, multiple = True)
        self.colours = [('black', _('Black')), ('red', _('Red')), ('white', _('White')), ('blue', _('Blue')), ('green', _('Green')), ('brown', _('Brown')), ('grey50', _('Grey'))]
        
        #self.RFunctionParamxlab_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "X Label:", text = 'X Label')
        #self.RFunctionParamylab_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Y Label:", text = 'Y Label')
        #self.RFunctionParammain_lineEdit = redRGUI.base.lineEdit(self.controlArea, label = "Main Title:", text = 'Main Title')
        topBox = redRGUI.base.widgetBox(self.controlArea, orientation = 'horizontal')
        plotData = redRGUI.base.groupBox(topBox, label = _('Plotting Data'))
        self.namesListX = redRGUI.base.comboBox(plotData, label = 'X Axis Data:')
        #self.namesListX.setEnabled(False)
        self.namesListY = redRGUI.base.comboBox(plotData, label = 'Y Axis Data:')
        #self.namesListY.setEnabled(False)
        self.namesListZ = redRGUI.base.comboBox(plotData, label = 'Z Contours:')
        
        
        contoursBox = redRGUI.base.widgetBox(topBox, orientation = 'horizontal')
        buttonBox = redRGUI.base.widgetBox(contoursBox)
        
        redRGUI.base.button(buttonBox, label = _('Add Contour Lines'), callback = self.addContourLines)
        redRGUI.base.button(buttonBox, label = _('Remove Contour Lines'), callback = self.removeContourLines)
        
        self.binwidth = redRGUI.base.DynamicSpinBox(contoursBox, label = 'Binsizes:', values = [(('spin1', _('Contour Set 1')), (0, None, 5, 0))])
        self.colour = redRGUI.base.DynamicComboBox(contoursBox, label = 'Colours:', values = [(('spin1', _('Colour Set 1')), self.colours)])
        self.size = redRGUI.base.DynamicSpinBox(contoursBox, label = _('Contour Size'), values = [(('spin1', _('Size Set 1')), (0, None, 1, 2))])
        self.spinCounter = 1
        self.graphicsView = redRGUI.plotting.redRGGPlot(self.controlArea,label='Contour Plot',displayLabel=False,
        name = self.captionTitle)
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction,
        processOnInput=True)
        
    def removeContourLines(self):
        key = self.binwidth.getSpinIDs()[-1]
        self.binwidth.removeSpinBox(key)
        self.colour.removeComboBox(key)
        self.size.removeSpinBox(key)
    def addContourLines(self):
        self.spinCounter += 1
        self.binwidth.addSpinBox('spin%s' % self.spinCounter, _('Contour Set %s') % self.spinCounter, (0, None, 5, 0))
        self.colour.addComboBox('spin%s' % self.spinCounter, _('Colour Set %s') % self.spinCounter, self.colours)
        self.size.addSpinBox('spin%s' % self.spinCounter, _('Size Set %s') % self.spinCounter, (0, None, 1, 2))
    def processy(self, data):
        
        if data:
            self.RFunctionParam_y = data.getData()
            self.namesListX.setEnabled(True)
            self.namesListX.update(self.R('names('+data.getData()+')'))
            self.namesListY.setEnabled(True)
            self.namesListY.update(self.R('names('+data.getData()+')'))
            self.namesListZ.setEnabled(True)
            self.namesListZ.update(self.R('names('+data.getData()+')'))
            self.dataFrame = data.getData()
            self.dataFrameAttached = True

            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.graphicsView.clear()
            self.RFunctionParam_y=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if self.namesListY.currentText() == self.namesListX.currentText(): 
            self.status.setText(_("X and Y data can't be the same"))
            return
        #injection = []
        #if unicode(self.RFunctionParamxlab_lineEdit.text()) != '':
            #string = 'xlab=\''+unicode(self.RFunctionParamxlab_lineEdit.text())+'\''
            #injection.append(string)
        #if unicode(self.RFunctionParamylab_lineEdit.text()) != '':
            #string = 'ylab=\''+unicode(self.RFunctionParamylab_lineEdit.text())+'\''
            #injection.append(string)
        #if unicode(self.RFunctionParammain_lineEdit.text()) != '':
            #string = 'main=\''+unicode(self.RFunctionParammain_lineEdit.text())+'\''
            #injection.append(string)
        #inj = ','.join(injection)
        self.R('%(VAR)s<-ggplot(%(DATA)s, aes(x = %(XDATA)s, y = %(YDATA)s, z = %(ZDATA)s))' % {'DATA':self.RFunctionParam_y, 'VAR':self.Rvariables['contour'], 'XDATA':self.namesListX.currentText(), 'YDATA':self.namesListY.currentText(), 'ZDATA':self.namesListZ.currentText()}, wantType = 'NoConversion')
        for spin in self.binwidth.getSpinIDs():
            self.R('%(VAR)s <- %(VAR)s + stat_contour(binwidth = %(BIN)s, colour = \'%(COLOUR)s\', size = %(SIZE)s)' % {'VAR':self.Rvariables['contour'], 'BIN':self.binwidth.getSpinBox(spin).value(), 'COLOUR':self.colour.getComboBox(spin).currentId(), 'SIZE':self.size.getSpinBox(spin).value()}, wantType = 'NoConversion')
        self.graphicsView.plot(query = self.Rvariables['contour'], function = '')
    
    