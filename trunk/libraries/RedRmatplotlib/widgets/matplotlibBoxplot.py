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

class matplotlibBoxplot(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "mplBoxplot", wantMainArea = 0, resizingEnabled = 1, wantGUIDialog = 1)
        
        self.data = None
        self.inputs = [('Vector List', signals.UnstructuredDict, self.gotData)]
        
        
        ### GUI ###
        topArea = redRGUI.groupBox(self.GUIDialog, label = 'Plotting Attributes')
        self.plotNotch = redRGUI.radioButtons(topArea, label = 'Notch?', buttons = ['True', 'False'], callback = self.replot)
        self.plotNotch.setChecked('True')
        self.symbol = redRGUI.lineEdit(topArea, label = 'Flier Symbol', text = '+', callback = self.replot)
        self.vertical = redRGUI.radioButtons(topArea, label = 'Orientation:', buttons = ['Vertical', 'Horizontal'], callback = self.replot)
        self.vertical.setChecked('Vertical')
        
        self.myPlot = redRGUI.RedRmatplotlib.mplBoxplot(self.controlArea)
        
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
                if name == 'row_names': continue
                items.append(self.data[name])
            try:
                self.myPlot.makePlot(items, notch = str(self.plotNotch.getChecked()) == 'True', sym = str(self.symbol.text()), vert = str(self.vertical.getChecked()) == 'Vertical')
            except Exception as inst:
                print items
                print inst