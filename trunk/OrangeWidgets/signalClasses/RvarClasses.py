# Kyle R Covington
from RSession import RSession

class RVariable: # parent class of all RvarClasses.  This class holds base functions such as assignment and item setting
    def __init__(self, data, parent = None):
        # set the variables
        if not data:
            raise Exception()
        self.data = data
        if not parent:
            parent = data
        self.parent = parent
        self.dictAttrs = {}
        
        # import R
        self.R = RSession()
    def __getitem__(self, item):
        try:
            attr = getattr(self, item)
        except:
            try:
                attr = self.dictAttrs[item]
            except:
                attr = None
        return attr
    
    def __setitem__(self, item, value):
        self.dictAttrs[item] = value
        
    def class_call(self):
        return 'class('+self.data+')'
        
    def class_data(self):
        return self.R(self.class_call(), silent = True)
        
    def plotObject(self, dwidth=8, dheight=8, devNumber = 0, mfrow = None):
        try:
            query = 'plot('+self.data+')'
            self.Rplot(query = query, dwidth = dwidth, dheight = dheight, devNumber = devNumber, mfrow = mfrow)
        except:
            print 'Exception occured'
    def copy(self):
        return RVariable(self.data, self.parent)
class RList(RVariable):
    def __init__(self, data, parent = None):
        RVariable.__init__(self, data = data, parent = parent)
        
    def copy(self):
        return RList(self.data, self.parent)
    def names_call(self):
        return 'names('+self.data+')'
    def names_data(self):
        return self.R(self.names_call(), silent = True)
    def length_call(self):
        return 'length('+self.data+')'
    def length_data(self):
        return self.R(self.length_call(), silent = True)
    def getItem_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'[['+str(item)+']]'
        elif type(item) in [str]:
            return self.data+'[[\''+str(item)+'\']]'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(str(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+str(i)+'\"')
            return self.data+'[[c('+str(newItemList)[1:-1]+')]]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getItem_data(self, item):
        call = self.getItem_call(item)
        if call != None:
            return self.R(call, silent = True) # should return a subsetted dictionary (dict)
        else:
            print 'No data to return'
            return {}
            
    def getDims_call(self):
        return 'dim('+self.data+')'
        
    def getDims_data(self):
        output = self.R(self.getDims_call(), wantType = 'list', silent = True)
        if output != None:
            return output
        else: return []
    def getNames_call(self):
        return 'names('+self.data+')'
    def getNames_data(self):
        output = self.R(self.getNames_call(), wantType = 'list', silent = True)
        if output != None:
            return output
        else:
            return []
class RDataFrame(RList):
    def __init__(self, data, parent = None, cm = None):
        RList.__init__(self, data = data, parent = parent)
        if cm: 
            self.cm = cm
        else: # we only need to do this if a cm was not provided for us.
            rownames = self.R('rownames('+self.data+')')
            if rownames != None:
                self.R('cm_'+self.data+'<-data.frame(row.names = rownames('+self.data+'))')
            else:
                thisClass = self.R('class('+self.data+')')
                if thisClass not in ['data.frame', 'matrix', 'array']: # arrays are technically not allowed but there is the possibility of a two dimentional array that is not coerced to a matrix.
                    self.R('cm_'+self.data+'<-data.frame(row.names = make.names(rep(1, length('+self.data+'))))')
                else:
                    self.R('cm_'+self.data+'<-data.frame(row.names = make.names(rep(1, length('+self.data+'[1,]))))')
        self.cm = 'cm_'+self.data
    def copy(self):
        return RDataFrame(self.data, self.parent, self.cm)
    def getRownames_call(self):
        return 'rownames('+self.data+')'
    def getRownames_data(self):
        return self.R(self.getRownames_call(), wantType = 'list', silent = True)
    def getItem_call(self, item):
        if type(item) in [int, float, long]:
            item = int(item)
            return self.data+'[,'+str(item)+']'
        elif type(item) in [str]:
            return self.data+'[,\''+str(item)+'\']'
        elif type(item) in [list]:
            newItemList = []
            for i in item:
                if type(i) in [int, float, long]:
                    newItemList.append(str(int(i)))
                elif type(i) in [str]:
                    newItemList.append('\"'+str(i)+'\"')
            return self.data+'[,c('+str(newItemList)[1:-1]+')]'
        else:
            return self.data #just return all of the data and hope the widget picks up from there
    def getItem_data(self, item, wantType = 'dict'): # native functionality is to return a dict (this is what lists do)
        call = self.getItem_call(item)
        if call != None:
            if type(item) in [int, str, long, float]:
                return self.R(call, wantType = wantType, silent = True) # returns a single column
            elif type(item) in [list] and wantType not in ['array', 'list']: # returns a dict
                return self.R(call, wantType = wantType, silent = True)
                
            elif type(item) in [list] and wantType in  ['array', 'list']: # returns a list of lists
                return self.R('as.matrix('+call+')', wantType = wantType, silent = True)
        else:
            print 'No data to return'
            return {}
    def getColumnnames_call(self):
        return self.getNames_call()
    def getColumnnames_data(self):
        return self.getNames_data()
    def getRange_call(self, rowRange = None, colRange = None):
        if rowRange == None and colRange == None:
            return self.data
        if rowRange:
            rr = str(rowRange)
        else:
            rr = ''
        if colRange:
            cr = str(colRange)
        else:
            cr = ''
        return self.data+'['+rr+','+cr+']'
class RVector(RDataFrame):
    def __init__(self, data, parent = None, cm = None):
        #if not cm: # we should give a cm to the 
            #cm = self.R('cm_'+data+'<-data.frame(row.names = make.names(rep(1, length('+data+'))))')
        RDataFrame.__init__(self, data = data, parent = parent, cm = cm)
    def copy(self):
        return RVector(self.data, self.parent, self.cm)
    def getColumnnames_call(self):
        return self.getNames_call()
    def getColumnnames_data(self):
        return self.getNames_data()
    def getNames_call(self):
        return self.data
    def getNames_data(self):
        return self.data # the only name to speek of the name of the variable

    def getRange_call(self, rowRange = None, colRange = None):
        if rowRange == None: return self.data
        else: return self.data+'['+str(rowRange)+']'
        
        
class REnvironment(RVariable): # R environment class points to an environment within R
    pass
