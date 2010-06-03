## mplContour.  makes a contour plot using matplotlib.

from mplPlot import *

class mplContour(mplPlot):
    def __init__(self, parent):
        mplPlot.__init__(self, parent)
        
    def makePlot(self, *args, **kwargs):
        self.subPlot.contour(*args, **kwargs)
        self.canvas.draw()
        #self.data = (*args, **kwargs)
        
    # def getSettings(self):
        # r = {}
        # r['data'] = self.data
        # return r
    # def loadSettings(self,data): 
        # if data['data']:
            # self.makePlot(data['data'][0], data['data'][1])