from table import table
from RSession import RSession

class Rtable(table):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0,sortable=True, selectionMode = -1, addToLayout = 1):
        self.R = RSession()
        table.__init__(self,widget,sortable=sortable,selectionMode = selectionMode,addToLayout=addToLayout)

        if Rdata:
            self.setRTable(Rdata)
    
    def setRTable(self,Rdata):
        print 'in Rtable set'
        data = self.R.R('as.data.frame(' + Rdata + ')')
        self.Rdata = Rdata
        self.setTable(data)
        self.setHorizontalHeaderLabels(self.R.R('colnames(' +self.Rdata+ ')'))
        self.setVerticalHeaderLabels(self.R.R('rownames(' +self.Rdata+')'))
    def getSettings(self):
        r = table.getSettings(self)
        del r['data']
        r['Rdata'] = self.Rdata
        print r
        return r
    def loadSettings(self,data):
        print data
        if data['Rdata']:
            d = self.R.R('as.data.frame(' + data['Rdata'] + ')')
        else:
            d = None
        data['data'] = d;
        table.loadSettings(self,data)
  