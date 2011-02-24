"""
<name>Barplot (GGPLOT)</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses as signals
import libraries.plotting.signalClasses as plotSignals
from libraries.base.signalClasses.RVector import RVector as redRRVector
from libraries.base.signalClasses.RList import RList as redRList
from libraries.base.signalClasses.RDataFrame import RDataFrame as redRDataFrame

from libraries.base.qtWidgets.DynamicComboBox import DynamicComboBox
from libraries.base.qtWidgets.DynamicSpinBox import DynamicSpinBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.button import button
#from libraries.base.qtWidgets.graphicsView import graphicsView
from libraries.plotting.qtWidgets.redRGGPlot import redRGGPlot
from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.spinBox import spinBox
from libraries.base.qtWidgets.commitButton import commitButton as redRCommitButton
from libraries.base.qtWidgets.stackedWidget import stackedWidget
from libraries.base.qtWidgets.colorButton import colorButton

import redRi18n
_ = redRi18n.get_(package = 'plotting')
class krcggplotbarplot(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.require_librarys(["ggplot2", "hexbin"])
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.setRvariableNames(["boxplot"])
        self.inputs.addInput('id0', 'Data Table', redRDataFrame, self.processy)
        self.errorBarTypes = [('none', _('None')), ('se', _('Standard Error')), ('sem', _('Standard Error of Mean')), ('95per', _('95% Confidence Interval'))]
        self.colours = [(0, _('Two Color Gradient')), (2, _('Three Color Gradient')), (4, _('Sequential Brewer Colors')), (6, _('Diverging Brewer Colors')), (8, _('Qualitative Brewer Colors'))]
        
        topBox = redRWidgetBox(self.controlArea, orientation = 'horizontal')
        aestheticsBox = redRGroupBox(topBox, label = _('Aesthetics'), orientation = 'horizontal')
        aestheticsBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.xGroup = comboBox(aestheticsBox, label = _('X Groupings'))
        self.yData = comboBox(aestheticsBox, label = _('Y Values'))
        self.fillData = comboBox(aestheticsBox, label = _('Fill Data'), callback = self.fillDataChanged)
        self.colourScale = comboBox(aestheticsBox, label = _('Color Scale'), items = self.colours, callback = self.colourScaleChanged)
        ## make the scale selector
        self.colourSelectorStack = stackedWidget(aestheticsBox)
        
        
        
        ## vlaue stack 0; gradient selector
        gradientBox = self.colourSelectorStack.createWidgetBox()
        self.gradientFrom = colorButton(gradientBox, label = _('From'), startColor = '#000000')
        self.gradientTo = colorButton(gradientBox, label = _('To'), startColor = '#FFFFFF')
        
        ## value stack 1; gradient2 selector
        gradient2Box = self.colourSelectorStack.createWidgetBox()
        self.gradient2From = colorButton(gradient2Box, label = _('From'), startColor = '#FF0000')
        self.gradient2To = colorButton(gradient2Box, label = _('To'), startColor = '#00FF00')
        self.gradient2Via = colorButton(gradient2Box, label = _('Via'), startColor = '#FFFFFF')
        
        ## value stack 2; sequential brewer colors
        sequentialBox = self.colourSelectorStack.createWidgetBox()
        self.sequentialPalettes = comboBox(sequentialBox, label = _('Palette'), items = [('Blues', _('Blues')), ('BuGn', _('Blue Green')), ('BuPu', _('Blue Purple')), ('GnBu', _('Green Blue')), ('Greens', _('Greens')), ('Greys', _('Greys')), ('Oranges', _('Oranges')), ('OrRd', _('Orange Red')), ('PuBu', _('Purple Blue')), ('PuBuGn', _('Purple Blue Green')), ('PuRd', _('Purple Red')), ('Purples', _('Purples')), ('RdPu', _('Red Purple')), ('Reds', _('Reds')), ('YlGn', _('Yellow Green')), ('YlGnBu', _('Yellow Green Blue')), ('YlOrBr', _('Yellow Orange Brown')), ('YlOrRd', _('Yellow Orange Red'))])
        self.sequentialVariations = spinBox(sequentialBox, label = _('Variations'), decimals = 0, min = 3, max = 9, value = 5)
        
        ## value stack 3; diverging brewer colors
        divergingBox = self.colourSelectorStack.createWidgetBox()
        paletteItems = [('BrBG', _('Brown Blue Green')), ('PiYG', _('Pink Yellow Green')), ('PRGn', _('Pink Red Green')), ('PuOr', _('Purple Orange')), ('RdBu', _('Red Blue')), ('RdGy', _('Red Grey')), ('RdYlBu', _('Red Yellow Blue')), ('RdYlGn', _('Red Yellow Green')), ('Spectral', _('Spectral'))]
        self.divergingPalettes = comboBox(divergingBox, label = _('Palette'), items = paletteItems)
        self.divergingVariations = spinBox(divergingBox, label = _('Variations'), decimals = 0, min = 3, max = 11, value = 5)
        
        ## value stack 4; qualitative brewer colors
        qualitativeBox = self.colourSelectorStack.createWidgetBox()
        self.qualitativePalettes = comboBox(qualitativeBox, label = _('Palette'), items = [('Accent', _('Accent')), ('Dark2', _('Dark2')), ('Paired', _('Paired')), ('Pastel1', _('Pastel1')), ('Pastel2', _('Pastel2')), ('Set1', _('Set1')), ('Set2', _('Set2')), ('Set3', _('Set3'))])
        self.qualitativeVariations = spinBox(qualitativeBox, label = _('Variations'), decimals = 0, min = 3, max = 8, value = 5)
        
        ## error bars
        errorBox = redRGroupBox(self.controlArea, label = _('Error Bar Options'), orientation = 'horizontal')
        self.errorType = comboBox(errorBox, label = _('Error Bar Type'), items = self.errorBarTypes)
        self.errorBarData = comboBox(errorBox, label = _('Error Bar Data'))
        
        
        self.colourSelectorStack.setCurrentIndex(0)
        
        self.graphicsView = redRGGPlot(self.controlArea,label='Box Plot',displayLabel=False,
        name = self.captionTitle)
        self.commit = redRCommitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,
        processOnInput=True)
    def fillDataChanged(self): pass
    def colourScaleChanged(self):
        print self.colourScale.currentId()
        self.colourSelectorStack.setCurrentIndex(self.colourScale.currentId())
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
            names = self.R('names(%s)' % self.RFunctionParam_y, wantType = 'list')
            self.xGroup.update(names)
            self.yData.update(names) # = comboBox(aestheticsBox, label = _('Y Values'))
            self.fillData.update(names) # = comboBox(aestheticsBox, label = _('Fill Data'), callback = self.fillDataChanged)
            self.errorBarData.update(names)
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.graphicsView.clear()
            self.RFunctionParam_y=''
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if self.xGroup.currentText() == self.yData.currentText(): 
            self.status.setText(_("X and Y data can't be the same"))
            return
        
        self.R('%(VAR)s<-ggplot(%(DATA)s, aes(x = %(XDATA)s, y = %(YDATA)s, fill = %(ZDATA)s))' % {'DATA':self.RFunctionParam_y, 'VAR':self.Rvariables['boxplot'], 'XDATA':self.xGroup.currentText(), 'YDATA':self.yData.currentText(), 'ZDATA':self.fillData.currentText()}, wantType = 'NoConversion')
        self.R('%(VAR)s<-%(VAR)s + geom_bar(position = position_dodge(width = 0.9), stat = "identity")' % {'VAR':self.Rvariables['boxplot']}, wantType = 'NoConversion')
        if self.errorType.currentId() != 'none':
            self.R('%(VAR)s<-%(VAR)s + geom_errorbar(aes(ymax = %(YDATA)s + %(ERROR)s, ymin = %(YDATA)s - %(ERROR)s), position = position_dodge(width = 0.9), width = 0.25)' % {'VAR':self.Rvariables['boxplot'], 'YDATA':self.yData.currentText(), 'ERROR':self.errorBarData.currentId()})
        scale = self.colourScale.currentId()
        if scale == 0:
            self.R('%(VAR)s<-%(VAR)s + scale_fill_continuous(low = "%(LOW)s", high = "%(HIGH)s")' % {'VAR':self.Rvariables['boxplot'], 'LOW':self.gradientFrom.getColor(), 'HIGH':self.gradientTo.getColor()}, wantType = 'NoConversion')
        elif scale == 2:# scale_fill_gradient2
            self.R('%(VAR)s<-%(VAR)s + scale_fill_gradient2(low = "%(LOW)s", high = "%(HIGH)s", mid = "%(VIA)s")' % {'VAR':self.Rvariables['boxplot'], 'LOW':self.gradient2From.getColor(), 'HIGH':self.gradient2To.getColor(), 'VIA':self.gradient2Via.getColor()}, wantType = 'NoConversion')
        elif scale == 4:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.sequentialPalettes.currentId()}, wantType = 'NoConversion')
        elif scale == 6:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.divergingPalettes.currentId()}, wantType = 'NoConversion')
        elif scale == 8:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.qualitativePalettes.currentId()}, wantType = 'NoConversion')
        
        self.graphicsView.plot(query = self.Rvariables['boxplot'], function = '')
    
    