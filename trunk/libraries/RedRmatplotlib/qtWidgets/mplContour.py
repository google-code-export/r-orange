## mplContour.  makes a contour plot using matplotlib.

from mplPlot import *

class mplContour(mplPlot):
    def __init__(self, parent):
        mplPlot.__init__(self, parent)
        
    def makePlot(self, *args, **kwargs):
        self.subPlot.contour(*args, **kwargs)
        self.canvas.draw()
        
    