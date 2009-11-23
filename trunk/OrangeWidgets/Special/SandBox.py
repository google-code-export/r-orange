"""
<name>SandBox</name>
<description></description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI
import redRGUI
import RAffyClasses

class table(QTableWidget,redRGUI.widgetState):
    def __init__(self,widget,data=None, rows = 0, columns = 0, selectionMode = -1, addToLayout = 1):
        QTableWidget.__init__(self,rows,columns,widget)
        #w = QTableWidget(rows, columns, widget)
        #self.RdataVariable = data
        if widget and addToLayout and widget.layout():
            widget.layout().addWidget(self)
        if selectionMode != -1:
            w.setSelectionMode(selectionMode)
        if data:
            self.data = data
            self.setTable(data)
    def setTable(self, data):
        if data==None:
            return
        qApp.setOverrideCursor(Qt.WaitCursor)
        #print data
        
        self.setRowCount(len(data[data.keys()[0]]))
        self.setColumnCount(len(data.keys()))

        n = 0
        for key in data:
            m = 0
            for item in data[key]:
                newitem = QTableWidgetItem(str(item))
                self.setItem(m, n, newitem)
                m += 1
            n += 1
        
        qApp.restoreOverrideCursor()

    def getSettings(self):
        #print 'in get settings' + self.text()
        r = {'data': self.data}
        r.update(self.getState())
        # print r
        return r
    def loadSettings(self,data):
        #print 'called load' + str(value)     
        self.setTable(data['data'])
        #self.setEnabled(data['enabled'])
        self.setState(data)

class Rtable(table):
    def __init__(self,widget,Rdata=None, rows = 0, columns = 0, selectionMode = -1, addToLayout = 1):
        #table.__init__(self,rows,columns,widget)
        import OWRpy
        R = OWRpy.OWRpy()
        if Rdata:
            data = R.R('as.data.frame(' + Rdata + ')')
        else:
            data = None
        
        table.__init__(self,widget,data=data)
        # if widget and addToLayout and widget.layout():
            # widget.layout().addWidget(self)
        # if selectionMode != -1:
            # w.setSelectionMode(selectionMode)
        # if Rdata:
            # self.setTable(Rdata)
    # def setTable(self, Rdata):
        # if Rdata==None or Rdata == '':
            # return
        # qApp.setOverrideCursor(Qt.WaitCursor)
        # data = self.R('as.data.frame(' + Rdata + ')')
        # headers = self.R('colnames('+Rdata+')')
        # dims = self.R('dim('+Rdata+')')
        
        # self.setColumnCount(dims[1])
        # self.setRowCount(dims[0])
        # self.setHorizontalHeaderLabels(headers)
        # n = 0
        # for key in data:
            # m = 0
            # for item in data[key]:
                # newitem = QTableWidgetItem(str(item))
                # self.setItem(m, n, newitem)
                # m += 1
            # n += 1

        
        # qApp.restoreOverrideCursor()

    
class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        self.lineEditText = ''
        self.loadSettings()
        self.inputs = None
        self.outputs = None
        self.R('data <- data.frame(a=c(1,2),b=c(3,4))')
        data = {'a':[1,2],'b':[3,4]}
        #self.table = Rtable(self.controlArea,Rdata = 'data')
        #self.table = table(self.controlArea,data = data)
        self.table2 = Rtable(self.controlArea,Rdata = 'data')