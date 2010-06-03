## matplotlib contour.  Uses the matplotlib library to plot a contour plot.

"""
<name>Matplotlib Contour Plot</name>
<author>Written by Kyle R. Covington</author>
<RFunctions>None</RFunctions>
<tags>Matplotlib Plotting</tags>
<icon>icons/plot.png</icon>
"""
from OWRpy import * 
import redRGUI
import numpy

class matplotlibContourPlot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "contourPlot", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        
        self.data = None
        self.Ydata = None
        self.Xdata = None
        self.inputs = [('Matrix', signals.RMatrix, self.gotData), ('X levels', signals.RMatrix, self.gotX), ('Y levels', signals.RMatrix, self.gotY)]
        
        ### GUI ###
        
        optArea = redRGUI.groupBox(self.GUIDialog, label = 'Options')
        
        self.lineWidths = redRGUI.lineEdit(optArea, label = 'Line Widths', toolTip = 'An optional list of line widths.  Separate by comma.', callback = self.makePlot)
        
        self.plot = redRGUI.RedRmatplotlib.mplContour(self.controlArea)
        redRGUI.button(self.bottomAreaRight, 'Replot', callback = self.makePlot)
        
    def gotData(self, data):
        if data:
            self.data = data.getData()
            self.makePlot()
        else:
            self.data = None
    def gotX(self, data):
        if data:
            self.Xdata = data.getData()
        else:
            self.Xdata = None
            
    def gotY(self, data):
        if data:
            self.Ydata = data.getData()
        else:
            self.Ydata = None
            
    def makePlot(self):
        if not self.data:
            self.status.setText('No data connected')
            return
        if not self.Xdata or not self.Ydata:
            args = numpy.array(self.R('as.matrix('+self.data+')', wantType = 'array'))
        else:
            args = (self.R('as.matrix('+self.Xdata+')', wantType = 'array'), self.R('as.matrix('+self.Ydata+')', wantType = 'array'), self.R('as.matrix('+self.data+')', wantType = 'array'))
        
        kwargs = {}
        if str(self.lineWidths.text()) != '':
            kwargs['linewidths'] = tuple(str(self.lineWidths.text()).split(','))
            
            try:
                self.plot.makePlot(args, kwargs)
            except Exception as inst:
                print inst
                print args
                print kwargs
                

        else:
            try:
                self.plot.makePlot(args)
            except Exception as inst:
                print inst
                print args
                print kwargs
                
        