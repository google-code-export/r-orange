"""
<name>SandBox</name>
<description>a playground for widgets</description>
<tags>Prototypes</tags>
<priority>9010</priority>
"""

from OWRpy import *
import OWGUI,glob,imp
import redRGUI
import signals

class SandBox(OWRpy):
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "plotAffy")
        self.lineEditText = ''
        
        self.inputs = None
        self.outputs = None
        self.R('data <- data.frame(a=rnorm(100),b=rnorm(100))')
        data = {'a':[1,2],'b':[3,4]}
        import cPickle
        
        #self.table = Rtable(self.controlArea,Rdata = 'data')
        
        # self.table = table(self.controlArea,data = data)
        self.table2 = redRGUI.Rtable(self.controlArea,Rdata = 'data')        
        self.table2.setSelectionBehavior(QAbstractItemView.SelectRows)

        if not os.path.isfile(os.path.join(redREnviron.directoryNames['canvasDir'], 'SandBoxTest.pickle')):
        
            f = open(os.path.join(redREnviron.directoryNames['canvasDir'], 'SandBoxTest.pickle'), 'wb')
            cPickle.dump(self.table2, f, 2)
            f.close()
            
        else:
            f = open(os.path.join(redREnviron.directoryNames['canvasDir'], 'SandBoxTest.pickle'), 'rb')
            c = cPickle.load(f)
            f.close()
            
            print 'Class C', c.__class__
        