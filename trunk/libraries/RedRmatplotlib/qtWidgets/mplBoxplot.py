## mplBoxplot.  a boxplot made in matplotlib

from mplPlot import *

class mplBoxplot(mplPlot):
    def __init__(self, parent, notch = 0, sym = '+', vert = 1, whis = 1.5, positions = None, widths = None):
        mplPlot.__init__(self, parent)
        
        self.notch = notch
        self.whis = whis
        self.positions = positions
        self.widths = widths
        self.vert = vert
        self.sym = sym
        
    def makePlot(self, data, notch = None, sym = None, vert = None, whis = None, positions = None, widths = None):
        if not notch:
            notch = self.notch
        if not sym:
            sym = self.sym
        if not vert:
            vert = self.vert
        if not whis:
            whis = self.whis
        if not positions:
            positions = self.positions
        if not widths:
            widths = self.widths
            
        self.subPlot.boxplot(x = data,
            sym = sym,
            vert = vert, 
            whis = whis,
            positions = positions,
            widths = widths)
        self.canvas.draw()