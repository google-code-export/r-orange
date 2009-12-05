from table import table
from RSession import RSession

class Rtable(table):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0,sortable=True, selectionMode = -1, addToLayout = 1):
        self.Rdata = Rdata
        self.R = RSession()
        
        if Rdata:
            data = self.R.R('as.data.frame(' + Rdata + ')')
        else:
            data = None
        
        table.__init__(self,widget,data=data,sortable=True,selectionMode = -1,addToLayout=addToLayout)
    
    def getSettings(self):
        r = table.getSettings(self)
        del r['data']
        r['Rdata'] = self.Rdata
        print r
        return r
    def loadSettings(self,data):
        if data['Rdata']:
            d = self.R.R('as.data.frame(' + data['Rdata'] + ')')
        else:
            d = None
        data['data'] = d;
        table.loadSettings(self,data)
  