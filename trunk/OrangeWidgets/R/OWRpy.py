#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
from rpy_options import set_options
set_options(RHOME=os.environ['RPATH'])
import rpy

class OWRpy():
    #a class variable which is incremented every time OWRpy is instantiated.
    
    num_widgets = 0
    def __init__(self):	
        #The class variable is used to create the unique names in R
        OWRpy.num_widgets += 1
        #this should be appended to every R variable
        self.variable_suffix = '_' + str(OWRpy.num_widgets)
        #keep all R variable name in this dict
        self.Rvariables = {}
    
    def rsession(self,query):
        print query
        output  = rpy.r(query)
        return output
        
    def require_librarys(self,librarys):
        for library in librarys:
            print self.rsession("library('"+ library +"',logical.return=T)") == False
            if not self.rsession("library('"+ library +"',logical.return=T)"): 
                self.rsession('setRepositories(ind=1:7)')
                self.rsession('chooseCRANmirror()')
                self.rsession('install.packages("' + library + '")')
                
            self.rsession('require('  + library + ')')
    
    def setRvariableNames(self,names):
        dict = {}
        for x in names:
            dict[x] = x + self.variable_suffix
        return dict
            
    #convert R data.frames to Orange exampleTables
    def convertDataframeToExampleTable(self, dataFrame_name):
        #set_default_mode(CLASS_CONVERSION)

        dataFrame = self.rsession(dataFrame_name)	
        col_names = self.rsession('colnames(' + dataFrame_name + ')')
        if self.rsession("class(" + dataFrame_name + ")") == 'matrix':
            col_def = self.rsession("apply(" + dataFrame_name + ",2,class)")
        else:
            col_def = self.rsession("sapply(" + dataFrame_name + ",class)")
        colClasses = []
        for i in col_names:
            if col_def[i] == 'numeric' or col_def[i] == 'integer':
                colClasses.append(orange.FloatVariable(i))
            elif col_def[i] == 'factor':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'character':
                colClasses.append(orange.StringVariable(i))
            elif col_def[i] == 'logical':
                colClasses.append(orange.StringVariable(i))
            else:
                colClasses.append(orange.StringVariable(i))
                
        self.rsession('exampleTable_data' + self.variable_suffix + '<- '+ dataFrame_name)
        self.rsession('exampleTable_data' + self.variable_suffix + '[is.na(' + dataFrame_name + ')] <- "?"')

        d = self.rsession('as.matrix(exampleTable_data' + self.variable_suffix + ')')
        domain = orange.Domain(colClasses)
        data = orange.ExampleTable(domain, d)
        self.rsession('rm(exampleTable_data' + self.variable_suffix + ')')
        return data
        
        
        