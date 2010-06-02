## matplotlib boxplot.  Uses the matplotlib library to plot a boxplot.

"""
<name>Matplotlib Boxplot</name>
<author>Written by Kyle R. Covington</author>
<RFunctions>None</RFunctions>
<tags>Matplotlib Plotting</tags>
<icon>icons/plot.png</icon>
"""
from OWRpy import * 
import redRGUI
import sys, redREnviron, os
import matplotlib.pyplot as plt
import numpy as np
class matplotlibBoxplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "mplBoxplot", wantMainArea = 0, resizingEnabled = 1)
        
        self.data = None
        self.inputs = [('Vector List', signals.UnstructuredDict, self.gotData)]
        
        
        ### GUI ###
        self.plotNotch = redRGUI.radioButtons(self.controlArea, label = 'Notch?', buttons = ['True', 'False'], callback = self.replot)
        self.plotNotch.setChecked('True')
        self.symbol = redRGUI.lineEdit(self.controlArea, label = 'Flier Symbol', callback = self.replot)
        self.vertical = redRGUI.radioButtons(self.controlArea, label = 'Orientation:', buttons = ['Vertical', 'Horizontal'], callback = self.replot)
        self.vertical.setChecked('Vertical')
        
        self.myPlot = redRGUI.RedRmatplotlib.mplPlot(self.controlArea)
        
    def gotData(self, data):
        if data:
            self.data = data.getData()
            self.replot()
        else:
            self.data = None
            
    def replot(self):
        if self.data:
            items = []
            for name in self.data.keys():
                items.append(self.data[name])
            plt.boxplot(items, notch = (str(self.plotNotch.getChecked()) == 'True'), sym = str(self.symbol.text()), vert = (str(self.vertical.getChecked()) == 'Vertical'))