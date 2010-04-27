"""
<name>Grammer of Graphics Plotter</name>
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
        self.plotAtts = [] # a collection of dicts, these contain the parameters that can be set for any particular function.  The aes attribut will also be a dict, however, other parameters will be contained within this dictionary.  This essentially represents all of the data that this widget will contain.
        
        
        
        
        self.loadSettings()
        self.inputs = [('Input Data Frame', RvarClasses.RDataFrame, self.addDataFrame)]
        self.outputs = [('Plot colleciton', RvarClasses.RGGPlotPlot)]
        
        ## GUI
        
        #####  Set up ####
        
        # we need to add Geoms, with or without aesthetics, and stats (also with aesthetics).  We need to know what kinds of aesthetics can be used with each kind of plot.  While this may better be done with a series of widgets (and I don't see why we couldn't allow other ggplot widgets to modify the product of a plot) it would make more sense to do this in a single widget.  So it looks like this will be a long one.
        tBox = redRGUI.widgetBox(self.controlArea, orientation = 'horizontal')
        lBox = redRGUI.widgetBox(tBox)
        rBox = redRGUI.widgetBox(tBox)
        
        self.plotBox = redRGUI.listBox(rBox, label = 'Plotting Attributes', toolTip = 'Contains plot attributes, these can be modified or deleted by clicking on the attribute', callback = self.setAttributeArea)
        attsBox = redRGUI.widgetBox(lBox) # where the attributes are set, may include aesthetic parameters, etc
        
        
        self.plotAttsComboBox = redRGUI.comboBox(attsBox, label = 'Plotting Layers:', items = ['Global', 'geom_abline, Line Geometry', 'geom_area, Area Geometry', 'geom_bar, Bar Geometry', 'geom_bin2d, 2D Heatmap Geometry', 'geom_boxplot, Box Plot Geometry', 'geom_contour, Contour Geometry', 'geom_corssbar, Crossbar Boxplot Geometry', 'geom_density, Density Geometry', 'geom_density2d, 2D Density Geometry', 'geom_errorbar, Vertical Error Bars', 'geom_errorbarh, Horizontal Error Bars', 'geom_freqpoly, Frequency Polygon Geometry', 'geom_hex, Tile Using Hexagons', 'geom_histogram, Histogram Geometry', 'geom_hline, Horizontal Line', 'geom_jitter, Jittered Points', 'geom_line, Connect Observations With Line', 'geom_linerange, Lines At Intervals', 'geom_path, Connect Observations In Order', 'geom_point, Scatterplot Geometry', 'geom_pointrange, Interval With Point', 'geom_polygon, Polygon Geometry', 'geom_quantile, Add Quantile Lines', 'geom_rect, 2D Rectangles', 'geom_ribbon, Ribbons Geometry', 'geom_rug, Rug Plots Geometry', 'geom_segment, Line Segments', 'geom_smooth, Smooth Mean Geometry', 'geom_step, Observations As Steps', 'geom_text, Add Text', 'geom_tile, Dense Tile Plots', 'geom_vline, Vertical Line', 'stat_abline, Line', 'stat_bin, Bin Data', 'stat_bin2d, Bin 2D Data In Rectangles', 'stat_binhex, Bin 2D Data In Hexagons', 'stat_boxplot, Box and Wisker Plots', 'stat_contour, 3D Data Contours', 'stat_density, Density Estimation', 'stat_density2d, 2D Density Estimation', 'stat_hline, Horizontal Line', 'stat_qq, Quantile-Quantile Plot', 'stat_quantile, Continuous Quantiles', 'stat_smooth, Add Smoother', 'stat_spoke, Convert Angle and Radious to x and y', 'stat_sum, Sum Unique Values', 'stat_summary, Summarise y at x', 'stat_unique, Remove Duplicates', 'stat_vline, Vertical Line', 'scale_alpha, Alpha Scale', 'scale_brewer, Brewer Scales', 'scale_continuous, Continuous Scales', 'scale_date, Date Scale', 'scale_datetime, Date Time Scale', 'scale_gradient, Smooth Gradient', 'scale_gradient2, Smooth Gradient 3 Colors', 'scale_gradientn, N Color Scale', 'scale_grey, Grey Color Scale', 'scale_hue, Evenly Spaced Hues', 'scale_identity, No Scaling', 'scale_linetype, Scale For Lines', 'scale_shape, Scale for Shapes', 'scale_size, Size Scale', 'coord_cartesian, Cartesian Coordinates', 'coord_equal, Equal Scale Cartesian', 'coord_flip, Flip Coordinates', 'coord_map, Map Projections', 'coord_polar, Polar Coordinates', 'coord_trans, Transform Cartesian Coordinates', 'facet_grid, Show Pannels In Grid', 'facet_wrap, Wrap Plots', 'position_dodge, Dodge Overlaps', 'position_fill, Stack Overlapping Objects and Standardize', 'position_identity, Don\'t Adjust Position', 'position_jitter, Jitter Points', 'position_stack, Stack Overlapping Objects'], toolTip = 'Adds a plotting layer to the plot, these can be geoms, stats, coordinates, etc.')
        ##### -------------  #####
        #####  A bunch of atts that can be set, each plot type or stat or geom will be able to set these  #####
        
    def setAttributeArea(self):
        pass
    def addDataFrame(self, data):
        if data:
            pass
        else:
            pass