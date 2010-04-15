import RvarClasses
import RSession
class RAffyBatch(RvarClasses.RVariable):

    def __init__(self, data, parent):
        RvarClasses.RVariable.__init__(self, data = data, parent = parent)
    
class Eset(RvarClasses.RVariable):
    def __init__(self, data, parent):
        RvarClasses.RVariable.__init__(self, data = data, parent = parent)
    