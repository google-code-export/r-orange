#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#


import rpy2.robjects as robjects

class OWRpy():
	#a class variable which is incremented every time OWRpy is instantiated.
	
	num_widgets = 0
	def __init__(self):	
		#The class variable is used to create the unique names in R
		OWRpy.num_widgets += 1
		#this should be appended to every R variable
		self.variable_suffix = '_' + str(OWRpy.num_widgets)
		#create easy access to the R object
		self.r = robjects.r
		
	#convert R data.frames to Orange exampleTables
	def convertDataframeToExampleTable(dataFrame):
		#converter
		pass
