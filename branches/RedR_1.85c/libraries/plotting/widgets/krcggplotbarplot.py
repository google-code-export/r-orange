"""
<name>Barplot (GGPLOT)</name>
<tags>Plotting</tags>
<icon>plot.png</icon>
"""
from OWRpy import * 
import redRGUI, signals
import redRGUI 
import libraries.plotting.signalClasses as plotSignals


import redRi18n
_ = redRi18n.get_(package = 'plotting')
class krcggplotbarplot(OWRpy):
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        self.require_librarys(["ggplot2", "hexbin"])
        self.RFunctionParam_y = ''
        self.RFunctionParam_x = ''
        self.setRvariableNames(["boxplot", "boxplotData"])
        self.inputs.addInput('id0', 'Data Table', signals.base.RDataFrame, self.processy)
        #self.errorBarTypes = [('none', _('None')), ('se', _('Standard Error')), ('sem', _('Standard Error of Mean')), ('95per', _('95% Confidence Interval'))]
        self.colours = [(0, _('Two Color Gradient')), (1, _('Three Color Gradient')), (2, _('Sequential Brewer Colors')), (3, _('Diverging Brewer Colors')), (4, _('Qualitative Brewer Colors')), (5, _('Greyscale'))]
        self.colourScaleWidgets = []
        mainBox = redRGUI.base.widgetBox(self.controlArea, orientation = 'horizontal')
        leftBox = redRGUI.base.widgetBox(mainBox)
        leftBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        topBox = redRGUI.base.widgetBox(leftBox, orientation = 'horizontal')
        aestheticsBox = redRGUI.base.groupBox(topBox, label = _('Aesthetics'), orientation = 'horizontal')
        aestheticsBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        aboxLeft = redRGUI.base.widgetBox(aestheticsBox, orientation = 'vertical')
        aboxMid = redRGUI.base.widgetBox(aestheticsBox, orientation = 'vertical')
        aboxRight = redRGUI.base.widgetBox(aestheticsBox, orientation = 'vertical')
        self.xGroup = redRGUI.base.comboBox(aboxLeft, label = _('X Groupings'), callback = self.xGroupChanged)
        self.yData = redRGUI.base.comboBox(aboxLeft, label = _('Y Values'))
        self.fillData = redRGUI.base.comboBox(aboxMid, label = _('Fill Data'), callback = self.fillDataChanged)
        self.colourScale = redRGUI.base.comboBox(aboxMid, label = _('Color Scale'), items = self.colours, callback = self.colourScaleChanged)
        ## make the scale selector
        self.colourSelectorStack = redRGUI.base.stackedWidget(aboxRight)
        
        
        
        ## vlaue stack 0; gradient selector
        gradientBox = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(gradientBox)
        self.gradientFrom = redRGUI.base.colorButton(gradientBox, label = _('From'), startColor = '#000000')
        self.gradientTo = redRGUI.base.colorButton(gradientBox, label = _('To'), startColor = '#FFFFFF')
        
        ## value stack 1; gradient2 selector
        gradient2Box = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(gradient2Box)
        self.gradient2From = redRGUI.base.colorButton(gradient2Box, label = _('From'), startColor = '#FF0000')
        self.gradient2To = redRGUI.base.colorButton(gradient2Box, label = _('To'), startColor = '#00FF00')
        self.gradient2Via = redRGUI.base.colorButton(gradient2Box, label = _('Via'), startColor = '#FFFFFF')
        
        ## value stack 2; sequential brewer colors
        sequentialBox = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(sequentialBox)
        self.sequentialPalettes = redRGUI.base.comboBox(sequentialBox, label = _('Palette'), items = [('Blues', _('Blues')), ('BuGn', _('Blue Green')), ('BuPu', _('Blue Purple')), ('GnBu', _('Green Blue')), ('Greens', _('Greens')), ('Greys', _('Greys')), ('Oranges', _('Oranges')), ('OrRd', _('Orange Red')), ('PuBu', _('Purple Blue')), ('PuBuGn', _('Purple Blue Green')), ('PuRd', _('Purple Red')), ('Purples', _('Purples')), ('RdPu', _('Red Purple')), ('Reds', _('Reds')), ('YlGn', _('Yellow Green')), ('YlGnBu', _('Yellow Green Blue')), ('YlOrBr', _('Yellow Orange Brown')), ('YlOrRd', _('Yellow Orange Red'))])
        self.sequentialVariations = redRGUI.base.spinBox(sequentialBox, label = _('Variations'), decimals = 0, min = 3, max = 9, value = 5)
        
        ## value stack 3; diverging brewer colors
        divergingBox = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(divergingBox)
        paletteItems = [('BrBG', _('Brown Blue Green')), ('PiYG', _('Pink Yellow Green')), ('PRGn', _('Pink Red Green')), ('PuOr', _('Purple Orange')), ('RdBu', _('Red Blue')), ('RdGy', _('Red Grey')), ('RdYlBu', _('Red Yellow Blue')), ('RdYlGn', _('Red Yellow Green')), ('Spectral', _('Spectral'))]
        self.divergingPalettes = redRGUI.base.comboBox(divergingBox, label = _('Palette'), items = paletteItems)
        self.divergingVariations = redRGUI.base.spinBox(divergingBox, label = _('Variations'), decimals = 0, min = 3, max = 11, value = 5)
        
        ## value stack 4; qualitative brewer colors
        qualitativeBox = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(qualitativeBox)
        self.qualitativePalettes = redRGUI.base.comboBox(qualitativeBox, label = _('Palette'), items = [('Accent', _('Accent')), ('Dark2', _('Dark2')), ('Paired', _('Paired')), ('Pastel1', _('Pastel1')), ('Pastel2', _('Pastel2')), ('Set1', _('Set1')), ('Set2', _('Set2')), ('Set3', _('Set3'))])
        self.qualitativeVariations = redRGUI.base.spinBox(qualitativeBox, label = _('Variations'), decimals = 0, min = 3, max = 8, value = 5)
        
        greyScaleBox = self.colourSelectorStack.createWidgetBox()
        self.colourScaleWidgets.append(greyScaleBox)
        
        ## error bars
        errorBox = redRGUI.base.groupBox(leftBox, label = _('Error Bar Options'), orientation = 'horizontal')
        #self.errorType = redRGUI.base.comboBox(errorBox, label = _('Error Bar Type'), items = self.errorBarTypes)
        self.errorBarData = redRGUI.base.comboBox(errorBox, label = _('Error Bar Data'))
        
        
        self.colourSelectorStack.setCurrentIndex(0)
        
        self.graphicsView = redRGUI.plotting.redRGGPlot(leftBox,label='Box Plot',displayLabel=False,
        name = self.captionTitle)
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, _("Commit"), callback = self.commitFunction,
        processOnInput=True)
        
        rightBox = redRGUI.base.widgetBox(mainBox)
        rightBox.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.fillShuffle = redRGUI.base.shuffleBox(rightBox, label = 'Column Order')
        self.groupShuffle = redRGUI.base.shuffleBox(rightBox, label = 'Grouping Order')
        self.colourScaleChanged()
    def fillDataChanged(self):
        if self.RFunctionParam_y != '' and self.fillData.currentText() != 'None' and self.R('is.factor(%s$%s)' % (self.RFunctionParam_y, self.fillData.currentText())):
            self.fillShuffle.update(self.R('levels(%s$%s)' % (self.RFunctionParam_y, self.fillData.currentText())))
        else:
            self.fillShuffle.clear()
    def xGroupChanged(self):
        if self.RFunctionParam_y != '' and self.xGroup.currentText() != 'None' and self.R('is.factor(%s$%s)' % (self.RFunctionParam_y, self.xGroup.currentText())):
            self.groupShuffle.update(self.R('levels(%s$%s)' % (self.RFunctionParam_y, self.xGroup.currentText())))
        else:
            self.groupShuffle.clear()
    def colourScaleChanged(self):
        print self.colourScale.currentId()
        self.colourSelectorStack.setCurrentWidget(self.colourScaleWidgets[self.colourScale.currentId()])
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
            self.yData.update(names) # = redRGUI.base.comboBox(aestheticsBox, label = _('Y Values'))
            self.fillData.update(['None'] + names) # = redRGUI.base.comboBox(aestheticsBox, label = _('Fill Data'), callback = self.fillDataChanged)
            self.errorBarData.update(['None'] + names)
            if self.commit.processOnInput():
                self.commitFunction()
        else:
            self.graphicsView.clear()
            self.RFunctionParam_y=''
            
    def _getXData(self): # called in the commitFunction to return the X groupings
        # if self.xGroup.currentText() == unicode('Rownames'):
            # return 'rownames(%s)' % unicode(self.RFunctionParam_y)
        # else:
        return 'as.factor(%s)' % self.xGroup.currentText()
    def commitFunction(self):
        if unicode(self.RFunctionParam_y) == '': return
        if self.xGroup.currentText() == self.yData.currentText(): 
            self.status.setText(_("X and Y data can't be the same"))
            return
        ## need to make a temp variable for our plot data and set some parameters such as the level order, this seems to help ggplot set orders properly
        self.R('%s<-%s' % (self.Rvariables['boxplotData'], self.RFunctionParam_y), wantType = 'NoConversion')
        # set the order of the levels of the xGroup
        self.R('%(DATA)s$%(COL)s<-factor(%(DATA)s$%(COL)s, levels = c(\'%(LEV)s\'))' % {'DATA':self.Rvariables['boxplotData'], 'COL':self.xGroup.currentText(), 'LEV': '\',\''.join([i for i in self.groupShuffle.getItems()])})
        
        if self.fillData.currentText() != 'None':
            self.R('%(DATA)s$%(COL)s<-factor(%(DATA)s$%(COL)s, levels = c(\'%(LEV)s\'))' % {'DATA':self.Rvariables['boxplotData'], 'COL':self.fillData.currentText(), 'LEV': '\',\''.join([i for i in self.fillShuffle.getItems()])})
            self.R('%(VAR)s<-ggplot(%(DATA)s, aes(x = %(XDATA)s, y = %(YDATA)s, fill = as.factor(%(ZDATA)s)))' % {'DATA':self.Rvariables['boxplotData'], 'VAR':self.Rvariables['boxplot'], 'XDATA':self._getXData(), 'YDATA':self.yData.currentText(), 'ZDATA':self.fillData.currentText()}, wantType = 'NoConversion')
        else:
            self.R('%(VAR)s<-ggplot(%(DATA)s, aes(x = as.factor(%(XDATA)s), y = %(YDATA)s))' % {'DATA':self.Rvariables['boxplotData'], 'VAR':self.Rvariables['boxplot'], 'XDATA':self.xGroup.currentText(), 'YDATA':self.yData.currentText(), 'ZDATA':self.fillData.currentText()}, wantType = 'NoConversion')
        self.R('%(VAR)s<-%(VAR)s + geom_bar(position = position_dodge(width = 0.9), stat = "identity", weight = 10, colour = "#000000", linetype = "solid") + geom_hline(aes(yintercept = 0), size = 1)' % {'VAR':self.Rvariables['boxplot']}, wantType = 'NoConversion')
        if self.errorBarData.currentText() != 'None':
            self.R('%(VAR)s<-%(VAR)s + geom_errorbar(aes(ymax = %(YDATA)s + %(ERROR)s, ymin = %(YDATA)s - %(ERROR)s), position = position_dodge(width = 0.9), width = 0.25)' % {'VAR':self.Rvariables['boxplot'], 'YDATA':self.yData.currentText(), 'ERROR':self.errorBarData.currentId()})
        scale = self.colourScale.currentId()
        if scale == 0:
            self.R('%(VAR)s<-%(VAR)s + scale_fill_continuous(low = "%(LOW)s", high = "%(HIGH)s")' % {'VAR':self.Rvariables['boxplot'], 'LOW':self.gradientFrom.color, 'HIGH':self.gradientTo.color}, wantType = 'NoConversion')
        elif scale == 1:# scale_fill_gradient2
            self.R('%(VAR)s<-%(VAR)s + scale_fill_gradient2(low = "%(LOW)s", high = "%(HIGH)s", mid = "%(VIA)s")' % {'VAR':self.Rvariables['boxplot'], 'LOW':self.gradient2From.color, 'HIGH':self.gradient2To.color, 'VIA':self.gradient2Via.color}, wantType = 'NoConversion')
        elif scale == 2:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.sequentialPalettes.currentId()}, wantType = 'NoConversion')
        elif scale == 3:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.divergingPalettes.currentId()}, wantType = 'NoConversion')
        elif scale == 4:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_brewer(palette = "%(PALETTE)s")' % {'VAR':self.Rvariables['boxplot'], 'PALETTE':self.qualitativePalettes.currentId()}, wantType = 'NoConversion')
        elif scale == 5:
            self.R('%(VAR)s<- %(VAR)s + scale_fill_grey(end = 1)' % {'VAR':self.Rvariables['boxplot']}, wantType = 'NoConversion')
        
        self.graphicsView.plot(query = self.Rvariables['boxplot'], function = 'print')
    
    