from table import table
from RSession import RSession

class Rtable(table):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0,sortable=False, selectionMode = -1, addToLayout = 1):
        self.R = RSession()
        table.__init__(self,widget,sortable=sortable,selectionMode = selectionMode,addToLayout=addToLayout)

        if Rdata:
            self.setRTable(Rdata)
    
    def setRTable(self,Rdata, setRowHeaders = 1, setColHeaders = 1):
        print 'in Rtable set'
        data = self.R.R('as.data.frame(' + Rdata + ')')
        self.Rdata = Rdata
        self.setTable(data)
        if setColHeaders: self.setHorizontalHeaderLabels(self.R.R('colnames(' +self.Rdata+ ')'))
        if setRowHeaders: self.setVerticalHeaderLabels(self.R.R('rownames(' +self.Rdata+')'))
    def getSettings(self):
        r = table.getSettings(self)
        del r['data']
        r['Rdata'] = self.Rdata
        return r
    def loadSettings(self,data):
        #print data
        self.setRTable(data['Rdata'])
        
        if 'sortIndex' in data.keys():
            # print 'aaaaaaaaa###############'
            self.sortByColumn(data['sortIndex'],data['order'])
        #print 'aaaaaaaaatable#########################'
        if 'selection' in data.keys() and len(data['selection']):
            # print 'table#########################'
            for i in data['selection']:
                # print i
                self.setItemSelected(self.item(i[0],i[1]),True)
            
                #self.selectRow(i[0])
            
        
  