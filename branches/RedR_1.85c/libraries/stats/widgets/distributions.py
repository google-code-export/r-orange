"""Generate Distributions widget


.. helpdoc::
Generates vectors of distributions for a variety of preset distributions.
"""


"""<widgetXML>
    <name>
        Generate Distributions
    </name>
    <icon>
        defualt.png
    </icon>
    <summary>
        Generates vectors of distributions for a variety of preset distributions.
    </summary>
    <tags>
        <tag priority="70">
            Stats
        </tag>
    </tags>
    <author>
        <authorname>Anup Parikh</authorname>
        <authorcontact>anup@red-r.org</authorcontact>
    </author>
    </widgetXML>
"""

"""
<name>Generate Distributions</name>
<author>Anup Parikh anup@red-r.org</author>
<RFunctions>stats:rnorm, stats:rbeta, stats:rbinom, stats:rcauchy, stats:rchisq</RFunctions>
<tags>Stats</tags>
<icon>rexecutor.png</icon>
"""

#OWRpy is the parent of all widgets. 
#Contains all the functionality for connecting the widget to the underlying R session.
from OWRpy import *
import redRGUI, signals
import os.path, redREnviron
# signalClasses classes contain the data that is passed between widgets. 
# In this case we are using the RDataFrame and RMatrix signals



# redRGUI contains all the QT gui elements. 
# These elements all have special functions for saving and loading state. 

# our first widget. Must be a child of OWRpy class
# The wiget class name must be the same as the file name
class distributions(OWRpy):
    
    # Python init statement is the class constructor 
    # Here you put all the code that will run as soon as the widget is put on the canvas
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        
        #create a R variable cor in the R session.
        #the output variable will not conflict with some other widgets variables
        
        """.. rrvnames::""" ## left blank so no description
        self.setRvariableNames(["distri"])

        # Define the outputs of this widget
        
        """.. rrsignals::
            :description: `A resulting distribution as a vector.`"""
        self.outputs.addOutput('id0', 'Results', signals.base.RVector)

        
        #START THE GUI LAYOUT
        area = redRGUI.base.widgetBox(self.controlArea,orientation='horizontal')       
        options = redRGUI.base.widgetBox(area,orientation='vertical')
        area.layout().setAlignment(options,Qt.AlignTop)
        self.count = redRGUI.base.spinBox(options, label='# Observations to Generate', min = 0,max=60000000, value = 10)
        
        """.. rrgui::""" 
        self.methodButtons = redRGUI.base.comboBox(options,  label = "Distributions", 
        items = [("rnorm", "Normal"),
        ('rbeta','Beta'),
        ('rbinom','Binomial'),
        ('rcauchy','Cauchy'),
        ('rchisq','Chi Square'),
        ('rexp','Exponential'),
        ('rf','F'),
        ('rgamma','Gamma') ],
        editable=True, callback = self.onDistChange)
        
        textBoxWidth = 70
        self.distOptions = redRGUI.base.widgetBox(options)
        self.normalDist = redRGUI.base.groupBox(self.distOptions,label='Normal Distribution')
        
        """.. rrgui::"""
        self.normMean = redRGUI.base.lineEdit(self.normalDist, label='Mean',id='mean', text='0', width=textBoxWidth)
        
        """.. rrgui::"""
        self.normSD = redRGUI.base.lineEdit(self.normalDist, label='Standard Deviations',id='sd', text='1',width=textBoxWidth)
        
        """.. rrgui::"""
        self.betaDist = redRGUI.base.groupBox(self.distOptions,label='Beta Distribution')
        
        """.. rrgui::"""
        self.betaShape1 = redRGUI.base.lineEdit(self.betaDist, label='Shape 1', id='shape1', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.betaShape2 = redRGUI.base.lineEdit(self.betaDist, label='Shape 2', id='shape2', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.betaNCP = redRGUI.base.lineEdit(self.betaDist, label='Non-centrality', id='ncp', width=textBoxWidth,text='0')
        self.betaDist.hide()

        
        self.binomDist = redRGUI.base.groupBox(self.distOptions,label='Binomial Distribution')
        
        """.. rrgui::"""
        self.binomSize = redRGUI.base.lineEdit(self.binomDist, label='Size', id='size', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.binomProb = redRGUI.base.lineEdit(self.binomDist, label='Probability', id='prob', width=textBoxWidth,text='.5')
        self.binomDist.hide()
        
        
        self.cauchyDist = redRGUI.base.groupBox(self.distOptions,label='Cauchy Distribution')
        
        """.. rrgui::"""
        self.cauchyLocation = redRGUI.base.lineEdit(self.cauchyDist, label='Location', id='location', width=textBoxWidth,text='0')
        
        """.. rrgui::"""
        self.cauchyScale = redRGUI.base.lineEdit(self.cauchyDist, label='Scale', id='scale', width=textBoxWidth,text='1')
        self.cauchyDist.hide()
        
        self.gammaDist = redRGUI.base.groupBox(self.distOptions,label='Gamma Distribution')
        
        """.. rrgui::"""
        self.gammaShape = redRGUI.base.lineEdit(self.gammaDist, label='Shape', id='location', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.gammaRate = redRGUI.base.lineEdit(self.gammaDist, label='Rate', id='scale', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.gammaScale = redRGUI.base.lineEdit(self.gammaDist, label='Scale', id='scale', width=textBoxWidth,text='.5')
        self.gammaDist.hide()
        
        self.chiDist = redRGUI.base.groupBox(self.distOptions,label='Chi Square Distribution')
        
        """.. rrgui::"""
        self.chiDF = redRGUI.base.lineEdit(self.chiDist, label='Degrees of Freedom', id='df', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.chiNCP = redRGUI.base.lineEdit(self.chiDist, label='Non-centrality', id='ncp', width=textBoxWidth,text='0')
        self.chiDist.hide()
        
        self.fDist = redRGUI.base.groupBox(self.distOptions,label='F Distribution')
        
        """.. rrgui::"""
        self.fDF1 = redRGUI.base.lineEdit(self.fDist, label='Degrees of Freedom 1', id='df1', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.fDF2 = redRGUI.base.lineEdit(self.fDist, label='Degrees of Freedom 2', id='df2', width=textBoxWidth,text='1')
        
        """.. rrgui::"""
        self.fNCP = redRGUI.base.lineEdit(self.fDist, label='Non-centrality', id='ncp', width=textBoxWidth,text='0')
        self.fDist.hide()
        
        self.expDist = redRGUI.base.groupBox(self.distOptions,label='Exponential Distribution')
        
        """.. rrgui::"""
        self.expRate = redRGUI.base.lineEdit(self.expDist, label='Rate ', id='rate', width=textBoxWidth,text='1')
        self.expDist.hide()
        
        """.. rrgui::"""
        commit = redRGUI.base.commitButton(options, "Commit", toolTip='Calculate values', callback = self.commitFunction)
        options.layout().setAlignment(commit, Qt.AlignRight)
        
    # Based on the user selections some parameters is not valid. This is all documented in the R help for cor/var/cov
    # Here we are instructing the GUI to disable those parameters that are invalid. 
    def onDistChange(self):
        for i in self.distOptions.findChildren(groupBox):
            i.setHidden(True)
        # print self.distOptions.findChild(self.methodButtons.currentId(),widgetBox)
        # self.distOptions.findChild(widgetBox,self.methodButtons.currentId()).show()
        
        if self.methodButtons.currentId() == 'rnorm':
            self.normalDist.show()
        elif self.methodButtons.currentId() == 'rbeta':
            self.betaDist.show()
        elif self.methodButtons.currentId() == 'rbinom':
            self.binomDist.show()
        elif self.methodButtons.currentId() == 'rcauchy':
            self.cauchyDist.show()
        elif self.methodButtons.currentId() == 'rchisq':
            self.chiDist.show()
        elif self.methodButtons.currentId() == 'rexp':
            self.expDist.show()
        elif self.methodButtons.currentId() == 'rf':
            self.fDist.show()
        elif self.methodButtons.currentId() == 'rgamma':
            self.gammaDist.show()
                
    # this function actually does the work in R 
    # its call by clicking the Commit button
    # or when data is received, if the checkbox is checked.
    def collectParameters(self):
        self.injection = []
        dist = unicode(self.methodButtons.currentId())
        if dist =='rnorm':
            self.injection.append('%s=%s' % (self.normMean.widgetId(), self.normMean.text()))
            self.injection.append('%s=%s' % (self.normSD.widgetId(), self.normSD.text()))
        elif dist =='rbeta':
            self.injection.append('%s=%s' % (self.betaShape1.widgetId(), self.betaShape1.text()))
            self.injection.append('%s=%s' % (self.betaShape2.widgetId(), self.betaShape2.text()))
            self.injection.append('%s=%s' % (self.betaNCP.widgetId(), self.betaNCP.text()))
        elif dist == 'rbinom':
            self.injection.append('%s=%s' % (self.binomSize.widgetId(), self.binomSize.text()))
            self.injection.append('%s=%s' % (self.binomProb.widgetId(), self.binomProb.text()))
        elif dist == 'rcauchy':
            self.injection.append('%s=%s' % (self.cauchyLocation.widgetId(), self.cauchyLocation.text()))
            self.injection.append('%s=%s' % (self.cauchyScale.widgetId(), self.cauchyScale.text()))
        elif dist == 'rchisq':
            self.injection.append('%s=%s' % (self.chiDF.widgetId(), self.chiDF.text()))
            self.injection.append('%s=%s' % (self.chiNCP.widgetId(), self.chiNCP.text()))
        elif dist == 'rexp':
            self.injection.append('%s=%s' % (self.expRate.widgetId(), self.expRate.text()))
        elif dist == 'rf':
            self.injection.append('%s=%s' % (self.fDF1.widgetId(), self.fDF1.text()))
            self.injection.append('%s=%s' % (self.fDF2.widgetId(), self.fDF2.text()))
            self.injection.append('%s=%s' % (self.fNCP.widgetId(), self.fNCP.text()))
        elif dist == 'rgamma':
            self.injection.append('%s=%s' % (self.gammaRate.widgetId(), self.gammaRate.text()))
            self.injection.append('%s=%s' % (self.gammaScale.widgetId(), self.gammaScale.text()))
            self.injection.append('%s=%s' % (self.gammaShape.widgetId(), self.gammaShape.text()))
        
        return self.injection
        
    def commitFunction(self):        
        # START COLLECTION THE R PARAMETERS THAT WILL CREATE THE R CODE TO EXECUTE
        dist = unicode(self.methodButtons.currentId())
        self.injection = self.collectParameters()
        

        # combine all the parameters in the a string    
        inj = ','.join(self.injection)
        
        # make the R call. The results will be saved in the 'cor' variable we declared earlier
        self.R('%s <- %s(%s,%s)' % (self.Rvariables['distri'], dist, self.count.value(),inj), wantType = 'NoConversion')
        
        # create a new signal of type RMatrix and load the results 
        newData = signals.base.RVector(self, data = '%s' % self.Rvariables["distri"]) 
        # send the signal forward
        self.rSend("id0", newData)
