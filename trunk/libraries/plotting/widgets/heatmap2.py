"""
<name>Heatmap2</name>
<description>Makes heatmaps of data.  This data should be in the form of a data table and should contain only numeric data, no text.  </description>
<tags>Plotting</tags>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<RFunctions>stats:heatmap</RFunctions>
<icon>heatmap.png</icon>
"""

from OWRpy import *
from libraries.base.signalClasses.RMatrix import RMatrix as redRRMatrix

from libraries.base.qtWidgets.separator import separator
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.comboBox import comboBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.spinBox import spinBox
from libraries.base.qtWidgets.radioButtons import radioButtons
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.widgetBox import widgetBox

class heatmap2(OWRpy):
    globalSettingsList = ['plotOnConnect','imageWidth','imageHeight']
    
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, wantGUIDialog = 1)
        
        self.setRvariableNames(['heatsubset'])
        self.plotOnConnect = 0
        self.plotdata = ''
        self.rowvChoice = None
        
        self.inputs.addInput('id0', 'Expression Matrix', redRRMatrix, self.processMatrix)

        
        #GUI
        mainArea = widgetBox(self.controlArea,orientation='vertical')
        mainArea.setMaximumWidth(300)
        
        dendrogramsBox = groupBox(mainArea, label='Calculate dendrogram ', orientation='vertical')
        self.notice = widgetLabel(dendrogramsBox,label='The data set has > 1000 rows.\nClustering on rows will likely fail.')
        self.notice.setHidden(True)
        self.dendrogramOptions = checkBox(dendrogramsBox,
        buttons = ['Rows', 'Columns'], setChecked=['Rows', 'Columns'], orientation='horizontal',
        callback=self.dendrogramChanged)
        
        functions = widgetBox(dendrogramsBox,orientation='vertical')
        self.distOptions = lineEdit(functions,label='Distance Function:', text='dist')
        self.hclustOptions = lineEdit(functions,label='Clustering Function:',text='hclust')
        #self.reorderOptions = lineEdit(functions,label='Reorder Function:', text='reorder.dendrogram')
        
        
        self.scaleOptions = radioButtons(mainArea,label='Scale',  buttons=['row','column','none'],
        setChecked='row',orientation='horizontal')
        
        otherOptions = groupBox(mainArea,label='Other Options')
        self.narmOptions = checkBox(otherOptions, buttons = ['Remove NAs'], setChecked=['Remove NAs'])
        self.showDendroOptions = checkBox(otherOptions,buttons=['Show dendrogram '], setChecked=['Show dendrogram '])
        
        
        
        self.notice2 = widgetLabel(mainArea,label='The input matrix is not numeric.')
        self.notice2.setHidden(True)
        self.buttonsBox = widgetBox(mainArea,orientation='horizontal')
        self.buttonsBox.layout().setAlignment(Qt.AlignRight)
        self.plotOnConnect = checkBox(self.buttonsBox, buttons=['Plot on Connect'])
        button(self.buttonsBox, label = "Plot", callback=self.makePlot)
        
        
        advancedOptions = widgetBox(self.GUIDialog)
        self.colorTypeCombo = comboBox(advancedOptions, label = 'Color Type:', 
        items = ['rainbow', 'heat.colors', 'terrain.colors', 'topo.colors', 'cm.colors'],callback=self.colorTypeChange)
        self.startSaturation = spinBox(advancedOptions, label = 'Starting Saturation', min = 0, max = 100)
        self.endSaturation = spinBox(advancedOptions, label = 'Ending Saturation', min = 0, max = 100)
        self.endSaturation.setValue(30)
        separator(advancedOptions,height=10)

        self.imageWidth = spinBox(advancedOptions, label = 'Image Widget', min = 1, max = 1000)
        self.imageWidth.setValue(4)
        self.imageHeight = spinBox(advancedOptions, label = 'Image Height', min = 1, max = 1000)
        self.imageHeight.setValue(4)
    def dendrogramChanged(self):
        if len(self.dendrogramOptions.getChecked()) > 0:
            self.hclustOptions.setEnabled(True)
            self.distOptions.setEnabled(True)
        else:
            self.hclustOptions.setDisabled(True)
            self.distOptions.setDisabled(True)
           
    def colorTypeChange(self):
        if self.colorTypeCombo.currentText() =='rainbow':
            self.startSaturation.setEnabled(True)
            self.endSaturation.setEnabled(True)
        else:
            self.startSaturation.setDisabled(True)
            self.endSaturation.setDisabled(True)
        
    def processMatrix(self, data):
        if not data:
            return 
        self.plotdata = data.getData()
        
        if not self.R('is.numeric(%s)' % self.plotdata):
            self.buttonsBox.setDisabled(True)
            self.notice2.setHidden(False)
        else:
            self.buttonsBox.setEnabled(True)
            self.notice2.setHidden(True)
            
        if self.R('nrow(%s)' % self.plotdata)  >1000:
            self.notice.setHidden(False)
            
            self.dendrogramOptions.setChecked(['Columns']) 
        else:
            self.notice.setHidden(True)
        if 'Plot on Connect'  in self.plotOnConnect.getChecked():
            self.makePlot()
    def makePlot(self):
        if self.plotdata == '': return
        options = {}

        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            # print start, end
            col = 'rev(rainbow(50, start = '+str(start)+', end = '+str(end)+'))'
        else:
            col = colorType+'(50)'
        
        options['col'] = col    
        
        if 'Rows' in self.dendrogramOptions.getChecked():
            options['Rowv'] = 'NULL'
        else:
            options['Rowv'] = 'NA'
        if 'Columns' in self.dendrogramOptions.getChecked():
            options['Colv'] = 'NULL'
        else:
            options['Colv'] = 'NA'
            
        options['hclustfun'] = self.hclustOptions.text()
        #options['reorderfun'] = self.reorderOptions.text()
        options['distfun'] = self.distOptions.text()
        
        options['scale'] = '"%s"' % self.scaleOptions.getChecked()
        
        if 'Remove NAs' in self.narmOptions.getChecked():
            options['na.rm'] = 'TRUE'
        else:
            options['na.rm'] = 'FALSE'
        if 'Show dendrogram' in self.showDendroOptions.getChecked():
            options['keep.dendro'] = 'TRUE'
        else:
            options['keep.dendro'] = 'FALSE'
            
        text = ''
        for k,v in options.items():
            text += '%s=%s,' % (k,v)
            
        self.Rplot('heatmap(%s, %s)' % (self.plotdata,text), self.imageHeight.value(), self.imageWidth.value())
        
    def getReportText(self, fileDir):
        ## print the plot to the fileDir and then send a text for an image of the plot
        if self.plotdata != '':
            self.R('png(file="'+fileDir+'/heatmap'+str(self.widgetID)+'.png")')
            if str(self.classesDropdown.currentText()) != '':
                self.classes = self.classesData+'$'+str(self.classesDropdown.currentText())
            if self.classes and ('Show Classes' in self.showClasses.getChecked()):
                colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
            else:
                colClasses = ''
            colorType = str(self.colorTypeCombo.currentText())
            if colorType == 'rainbow':
                start = float(float(self.startSaturation.value())/100)
                end = float(float(self.endSaturation.value())/100)
                print start, end
                col = 'rev(rainbow(50, start = '+str(start)+', end = '+str(end)+'))'
            else:
                col = colorType+'(50)'
            self.R('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')')
            self.R('dev.off()')
            # for making the pie plot
            self.R('png(file="'+fileDir+'/pie'+str(self.widgetID)+'.png")')
            if colorType == 'rainbow':
                start = float(float(self.startSaturation.value())/100)
                end = float(float(self.endSaturation.value())/100)
                print start, end
                col = 'rev(rainbow(10, start = '+str(start)+', end = '+str(end)+'))'
            else:
                col = colorType+'(10)'
            self.R('pie(rep(1, 10), labels = c(\'Low\', 2:9, \'High\'), col = '+col+')')
            self.R('dev.off()')
            self.R('png(file="'+fileDir+'/identify'+str(self.widgetID)+'.png")')
            self.R('plot(hclust(dist(t('+self.plotdata+'))))')
            self.R('dev.off()')
            text = 'The following plot was generated in the Heatmap Widget:\n\n'
            text += '.. image:: '+fileDir+'/heatmap'+str(self.widgetID)+'.png\n     :scale: 50%%\n\n'
            #text += '<strong>Figure Heatmap:</strong> A heatmap of the incoming data.  Columns are along the X axis and rows along the right</br>'
            text += '.. image:: '+fileDir+'/pie'+str(self.widgetID)+'.png\n     :scale: 30%%\n\n'
            text += '**Intensity Chart:** Intensity levels are shown in this pie chart from low values to high.\n\n'
            text += '.. image:: '+fileDir+'/identify'+str(self.widgetID)+'.png\n   :scale: 50%%\n\n\n'
            text += '**Clustering:** A cluster dendrogram of the column data.\n\n'
        else:
            text = 'Nothing to plot from this widget'
            
        return text
