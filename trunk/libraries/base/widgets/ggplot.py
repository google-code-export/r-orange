"""
<name>Grammar of Graphics Plotter</name>
<author>Generates sophisticated plots using the garmmar of graphics orriginally written by Hadley Wickham.  This plot takes a data frame of data and uses multiple graphics parameters to construct a plot.  These parameters can be added to generate ever more complicated plotts.</author>
<RFunctions>ggplot2:ggplot</RFunctions>
<tags>Plotting</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class ggplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "GGPlot2 Plotter", wantMainArea = 0, resizingEnabled = 1)
        
        # defines
        self.setRvariableNames(["ggplot"])
        self.plotAtts = {} # a collection of dicts, these contain the parameters that can be set for any particular function.  The aes attribut will also be a dict, however, other parameters will be contained within this dictionary.  This essentially represents all of the data that this widget will contain.
        
        self.require_librarys(["ggplot2", "hexbin"])

        self.inputs = [('Input Data Frame', signals.RDataFrame, self.addDataFrame)]
        self.outputs = [('Plot colleciton', signals.RGGPlotPlot)]
        
        ## GUI
        
        #####  Set up ####
        
        # we need to add Geoms, with or without aesthetics, and stats (also with aesthetics).  We need to know what kinds of aesthetics can be used with each kind of plot.  While this may better be done with a series of widgets (and I don't see why we couldn't allow other ggplot widgets to modify the product of a plot) it would make more sense to do this in a single widget.  So it looks like this will be a long one.
        tBox = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        lBox = redRGUI.widgetBox(tBox)
        rBox = redRGUI.widgetBox(tBox)
        
        self.plotBox = redRGUI.listBox(rBox, label = 'Plotting Attributes', toolTip = 'Contains plot attributes, these can be modified or deleted by clicking on the attribute', callback = self.setAttributeArea)
        attsBox = redRGUI.widgetBox(lBox) # where the attributes are set, may include aesthetic parameters, etc
        
        
        self.plotAttsComboBox = redRGUI.comboBox(attsBox, label = 'Plotting Layers:', items = ['Global', 'geom_abline, Line Geometry', 'geom_area, Area Geometry', 'geom_bar, Bar Geometry', 'geom_bin2d, 2D Heatmap Geometry', 'geom_boxplot, Box Plot Geometry', 'geom_contour, Contour Geometry', 'geom_crossbar, Crossbar Boxplot Geometry', 'geom_density, Density Geometry', 'geom_density2d, 2D Density Geometry', 'geom_errorbar, Vertical Error Bars', 'geom_errorbarh, Horizontal Error Bars', 'geom_freqpoly, Frequency Polygon Geometry', 'geom_hex, Tile Using Hexagons', 'geom_histogram, Histogram Geometry', 'geom_hline, Horizontal Line', 'geom_jitter, Jittered Points', 'geom_line, Connect Observations With Line', 'geom_linerange, Lines At Intervals', 'geom_path, Connect Observations In Order', 'geom_point, Scatterplot Geometry', 'geom_pointrange, Interval With Point', 'geom_polygon, Polygon Geometry', 'geom_quantile, Add Quantile Lines', 'geom_rect, 2D Rectangles', 'geom_ribbon, Ribbons Geometry', 'geom_rug, Rug Plots Geometry', 'geom_segment, Line Segments', 'geom_smooth, Smooth Mean Geometry', 'geom_step, Observations As Steps', 'geom_text, Add Text', 'geom_tile, Dense Tile Plots', 'geom_vline, Vertical Line', 'stat_abline, Line', 'stat_bin, Bin Data', 'stat_bin2d, Bin 2D Data In Rectangles', 'stat_binhex, Bin 2D Data In Hexagons', 'stat_boxplot, Box and Wisker Plots', 'stat_contour, 3D Data Contours', 'stat_density, Density Estimation', 'stat_density2d, 2D Density Estimation', 'stat_hline, Horizontal Line', 'stat_qq, Quantile-Quantile Plot', 'stat_quantile, Continuous Quantiles', 'stat_smooth, Add Smoother', 'stat_spoke, Convert Angle and Radious to x and y', 'stat_sum, Sum Unique Values', 'stat_summary, Summarise y at x', 'stat_unique, Remove Duplicates', 'stat_vline, Vertical Line', 'scale_alpha, Alpha Scale', 'scale_brewer, Brewer Scales', 'scale_continuous, Continuous Scales', 'scale_date, Date Scale', 'scale_datetime, Date Time Scale', 'scale_gradient, Smooth Gradient', 'scale_gradient2, Smooth Gradient 3 Colors', 'scale_gradientn, N Color Scale', 'scale_grey, Grey Color Scale', 'scale_hue, Evenly Spaced Hues', 'scale_identity, No Scaling', 'scale_linetype, Scale For Lines', 'scale_shape, Scale for Shapes', 'scale_size, Size Scale', 'coord_cartesian, Cartesian Coordinates', 'coord_equal, Equal Scale Cartesian', 'coord_flip, Flip Coordinates', 'coord_map, Map Projections', 'coord_polar, Polar Coordinates', 'coord_trans, Transform Cartesian Coordinates', 'facet_grid, Show Pannels In Grid', 'facet_wrap, Wrap Plots', 'position_dodge, Dodge Overlaps', 'position_fill, Stack Overlapping Objects and Standardize', 'position_identity, Don\'t Adjust Position', 'position_jitter, Jitter Points', 'position_stack, Stack Overlapping Objects'], toolTip = 'Adds a plotting layer to the plot, these can be geoms, stats, coordinates, etc.', callback = self.changedPlotAttsComboBox)
        ##### -------------  #####
        #####  A bunch of atts that can be set, each plot type or stat or geom will be able to set these  #####
        
        self.isSubAtt = redRGUI.checkBox(lBox, buttons = ['Sub Attribute'], toolTips = ['Places the item as a sub-attribute, this\n means that the attribute will not be added to\n the layers itself, but will be available to add to other layers.'])
        
        self.aesX = redRGUI.comboBox(lBox, label = 'X Data:', items = [])
        self.aesY = redRGUI.comboBox(lBox, label = 'Y Data:', items = [])
        self.aesZ = redRGUI.comboBox(lBox, label = 'Z Data:', items = [])
        self.aesZ.hide()
        self.aesGroup = redRGUI.comboBox(lBox, label = 'Grouping:')
        self.aesSize = redRGUI.comboBox(lBox, label = 'Size Variable:', items = [])

        self.aesSizeLineEdit = redRGUI.lineEdit(lBox, label = 'Override Size:')
        self.aesColour = redRGUI.comboBox(lBox, label = 'Color:', items = ['', '\'red\'', '\'green\'', '\'blue\'', '\'orange\'', '\'black\'', '\'white\'', '\'yellow\'', '\'purple\''], toolTip = 'Set a color for the plotting')
        self.aesLineType = redRGUI.lineEdit(lBox, label = 'Line type:')
        self.aesLineType.hide()
        self.aesIntercept = redRGUI.lineEdit(lBox, label = 'Intercept:', toolTip = 'A single or group or intercepts separated by commas.')
        self.aesIntercept.hide()  #used with line geom
        
        self.aesSlope = redRGUI.lineEdit(lBox, label = 'Slope:', toolTip = 'A single or group of slopes separated by commas.')
        self.aesSlope.hide()    #used with line geom
        self.statSmoothMethod = redRGUI.comboBox(lBox, label = 'Smooth Method:', items = ['lm', 'glm', 'gam', 'loess', 'rlm'])
        self.statSmoothFormula = redRGUI.lineEdit(lBox, label = 'Smoothing Function:')
        self.statSmoothSE = redRGUI.comboBox(lBox, label = 'Show Confidence Interval:', items = ['TRUE', 'FALSE'])
        self.statSmoothConfLevel = redRGUI.lineEdit(lBox, label = 'Confidence Level:', text = '0.95')
        self.statSmoothFullrange = redRGUI.comboBox(lBox, label = 'Show Full Range:', items = ['FALSE', 'TRUE'])
        self.statSmoothConfLevel.hide()
        self.statSmoothFormula.hide()
        self.statSmoothFullrange.hide()
        self.statSmoothMethod.hide()
        self.statSmoothSE.hide()
        
        self.scaleFrom = redRGUI.lineEdit(lBox, label = 'Scale from:')
        self.scaleTo = redRGUI.lineEdit(lBox, label = 'Scale To:')
        self.scaleFrom.hide()
        self.scaleTo.hide()
        
        self.aesFill = redRGUI.comboBox(lBox, label = 'Fill Color:', items = ['', '\'red\'', '\'green\'', '\'blue\'', '\'orange\'', '\'black\'', '\'white\'', '\'yellow\'', '\'purple\''], toolTip = 'Color or attribute to place on the data')
        self.aesFill.hide()
        
        
        self.plotAttLineEdit = redRGUI.lineEdit(self.controlArea, label = 'Attribute Data:', toolTip = 'Change the plot attribute data, this is an advanced function and there is no gurantee that you will be able to plot using the data that you input.', width = -1)
        self.acceptPlotLineEdit = redRGUI.button(self.controlArea, 'Accept Attribute Data', callback = self.acceptPlotLineEditChanges)
        self.plotAttLineEdit.hide()
        self.acceptPlotLineEdit.hide()
        button = redRGUI.button(lBox, 'Add Layer', callback = self.addLayer)
        buttonCommit = redRGUI.button(rBox, 'Plot', callback = self.plotGGPlot)
    def setAttributeArea(self):
        # populate a line Edit with the data that is in the plotAtts for this selection.  Also give the user the option to delete the attribute
        item = self.plotBox.selectedItems()[0]
        name = str(item.text())
        
        plotItemData = self.plotAtts[name]['data']
        self.plotAttLineEdit.show()
        self.acceptPlotLineEdit.show()
        self.plotAttLineEdit.setText(plotItemData)
        
    def acceptPlotLineEditChanges(self):
        item = self.plotBox.selectedItems()[0]
        name = str(item.text())
        
        self.plotAtts[name]['data'] = str(self.plotAttLineEdit.text())
    def addDataFrame(self, data):
        if data:
            self.data = data
            self.dataNames = self.R('names('+self.data.getData()+')')
            self.addGlobal()
            self.aesX.update(([''] + self.dataNames))
            self.aesY.update(([''] + self.dataNames))
            self.aesZ.update(([''] + self.dataNames))
            self.aesColour.update((['', '\'red\'', '\'green\'', '\'blue\'', '\'orange\'', '\'black\'', '\'white\'', '\'yellow\'', '\'purple\''] + self.dataNames))
            self.aesGroup.update(([''] + self.dataNames))
        else:
            pass
    def addLayer(self):
        name = str(self.plotAttsComboBox.currentText()).split(',')[0]
        injection = []
        if str(self.aesX.currentText()) != '':
            string = 'x ='+str(self.aesX.currentText())
            injection.append(string)
        if str(self.aesY.currentText()) != '':
            string = 'y ='+str(self.aesY.currentText())
            injection.append(string)
        if str(self.aesZ.currentText()) != '':
            string = 'z ='+str(self.aesZ.currentText())
            injection.append(string)
        if str(self.aesSize.currentText()) != '' and str(self.aesSizeLineEdit) == '':
            string = 'size ='+str(self.aesX.currentText())
            injection.append(string)
        elif str(self.aesSizeLineEdit.text()) != '':
            string = 'size ='+str(self.aesSizeLineEdit.text())
            injection.append(string)
        
        if str(self.aesLineType.text()) != '' and self.aesLineType.isVisible():
            string = 'linetype ='+str(self.aesLineType.text())
            injection.append(string)
        if str(self.aesSlope.text()) != '' and self.Slope.isVisible():
            string = 'slope = c('+str(self.Slope.text())+')'
            injection.append(string)
        if str(self.aesLineType.text()) != '' and self.aesLineType.isVisible():
            string = 'linetype ='+str(self.aesLineType.text())
            injection.append(string)
        if str(self.aesColour.currentText()) != '' and self.aesColour.isVisible():# and name in ['Global', 'geom_point', 'geom_jitter', 'stat_smooth', 'geom_hex']:
            string = 'colour = '+str(self.aesColour.currentText())
            injection.append(string)
        if str(self.aesGroup.currentText()) != '' and self.aesGroup.isVisible():
            string = 'group='+str(self.aesGroup.currentText())
            injection.append(string)
        
        functionInjection = []
        # if str(self.aesColour.currentText()) != '' and self.aesColour.isVisible() and name not in ['Global', 'geom_point', 'geom_jitter', 'stat_smooth', 'geom_hex']:
            # string = 'colour ='+str(self.aesColour.currentText())
            # functionInjection.append(string)
        if str(self.aesFill.currentText()) != '' and self.aesFill.isVisible():
            string = 'fill = '+str(self.aesFill.currentText())
            functionInjection.append(string)
        if name == 'stat_smooth':
            
            if str(self.statSmoothMethod.currentText()) != '' and self.statSmoothMethod.isVisible():
                string = 'method ='+str(self.statSmoothMethod.currentText())
                functionInjection.append(string)
            if str(self.statSmoothConfLevel.text()) != '' and self.statSmoothConfLevel.isVisible():
                string = 'conf.level = '+str(self.statSmoothConfLevel.text())
                functionInjection.append(string)
            if str(self.statSmoothFormula.text()) != '' and self.statSmoothFormula.isVisible():
                string = 'formula = '+str(self.statSmoothFormula.text())
                functionInjection.append(string)
            if name == 'stat_smooth':
                string = 'fulllength = '+str(self.statSmoothFullrange.currentText())
                functionInjection.append(string)
            if name == 'stat_smooth':
                string = 'se = '+str(self.statSmoothSE.currentText())
                functionInjection.append(string)
        if 'scale' in name:
            if str(self.scaleFrom.text()) != '':
                string = 'from = '+str(self.scaleFrom.text())
                functionInjection.append(string)
            if str(self.scaleTo.text()) != '':
                string = 'to ='+str(self.scaleTo.text())
                functionInjection.append(string)
                
        if name == 'Global':
            isGlobal = True
            name = 'ggplot'
        else:
            isGlobal = False
        self.plotAtts[name] = {'Global': isGlobal, 'data':name+'(aes('+','.join(injection)+'),'+','.join(functionInjection)+')', 'subAtt': ('Sub Attribute' in self.isSubAtt.getChecked())}
        self.plotBox.addItem(name)
    def addGlobal(self):
        self.plotAtts['Global'] = {'Global':True, 'data':'ggplot(data = '+self.data.data+')', 'subAtt':False}
        self.plotBox.addItem('Global')
        
    def changedPlotAttsComboBox(self):
        
        att = str(self.plotAttsComboBox.currentText()).split(',')[0]
        print att
        self.aesFill.hide()
        self.aesIntercept.hide()
        self.aesSlope.hide()
        self.aesLineType.hide()
        self.statSmoothConfLevel.hide()
        self.statSmoothFormula.hide()
        self.statSmoothFullrange.hide()
        self.statSmoothMethod.hide()
        self.statSmoothSE.hide()
        self.scaleFrom.hide()
        self.scaleTo.hide()
        self.aesZ.hide()
        self.aesGroup.hide()
        
        if att in ['geom_abline', 'stat_abline']:
            self.aesIntercept.show()
            self.aesSlope.show()
        elif att == 'stat_contour':
            self.aesZ.show()
        elif att in ['geom_point', 'geom_jitter']:
            self.aesGroup.show()
        elif att == 'stat_smooth':
            self.statSmoothConfLevel.show()
            self.statSmoothFormula.show()
            self.statSmoothFullrange.show()
            self.statSmoothMethod.show()
            self.statSmoothSE.show()
            self.aesGroup.show()
        elif att == 'geom_area':
            self.aesFill.show()
        elif att == 'geom_bar':
            self.aesFill.show()
        elif att in ['geom_boxplot', 'geom_point']:
            self.aesFill.show()
        elif att == 'geom_contour':
            self.aesLineType.show()
        elif att in ['geom_tile', 'geom_smooth', 'geom_crossbar', 'geom_pointrange', 'geom_polygon', 'geom_rect', 'geom_ribbon', ]:
            self.aesGroup.show()
            self.aesFill.show()
            self.aesLineType.show()
        elif att == 'geom_density':
            self.aesLineType.show()
            self.aesFill.show()
        elif att == 'geom_density2d':
            self.aesLineType.show()
        elif att in ['geom_step', 'geom_vline', 'geom_errorbar', 'geom_errorbarh', 'geom_freqpoly', 'geom_hline', 'geom_line', 'geom_linerange', 'geom_path', 'geom_quantile', 'geom_rug', 'geom_segment']:
            self.aesLineType.show()
        elif att == 'geom_histogram':
            self.aesLineType.show()
            self.aesFill.show()
        elif att in ['scale_gradient', 'scale_alpha']:
            self.scaleFrom.show()
            self.scaleTo.show()
        
    def plotGGPlot(self):
        command = []
        for item in self.plotAtts.keys():
            if self.plotAtts[item]['subAtt']: continue #this is a sub att so we should have already added it.
            if self.plotAtts[item]['Global']: 
                self.R(self.Rvariables['ggplot']+'<-'+self.plotAtts[item]['data']) 
                continue
            command.append(self.plotAtts[item]['data'])
        fullCommand = ' + '.join(command)
        
        self.R(self.Rvariables['ggplot']+'<-'+self.Rvariables['ggplot']+'+'+fullCommand)
        self.R('capture.output('+self.Rvariables['ggplot']+')')
        
        newData = signals.RGGPlotPlot(data = self.Rvariables['ggplot'])
        #newData.setOptionalData(
        self.rSend('Plot colleciton', newData)