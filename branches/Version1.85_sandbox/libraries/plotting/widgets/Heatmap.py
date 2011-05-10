"""
<name>Heatmap</name>
<tags>Plotting</tags>
<icon>heatmap.png</icon>
"""

from OWRpy import *
import redRGUI, signals
import libraries.base.signalClasses.RModelFit as rmf
import redRi18n
_ = redRi18n.get_(package = 'plotting')
class Heatmap(OWRpy):
    globalSettingsList = ['commit']
    def __init__(self, **kwargs):
        OWRpy.__init__(self, **kwargs)
        self.require_librarys(["fBasics", "gplots"])
        self.setRvariableNames(['heatsubset', 'hclust', 'heatvect', 'heatmapList'])
        self.plotOnConnect = 0
        self.plotdata = ''
        self.rowvChoice = None
        self.colvChoice = None
        #self.listOfColors = ['"red"', '"white"', '"blue"']  depricated with heatmap.2 limited to a list of color options.
        
        self.inputs.addInput('id0', 'Expression Matrix', signals.base.RDataFrame, self.processMatrix)
        self.inputs.addInput('id1', 'Classes Data', signals.base.RVector, self.processClasses)

        #self.outputs.addOutput('id0', 'Cluster Subset List', signals.base.RVector)
        self.outputs.addOutput('id1', 'Cluster Classes', signals.base.RVector)
        self.outputs.addOutput('heatmapList', _('Heatmap Parameters (List)'), signals.base.RList)

        #GUI
        infobox = redRGUI.base.groupBox(self.controlArea, label = "Options")
        
        self.commit = redRGUI.base.commitButton(self.bottomAreaRight, label = "Replot", 
        callback=self.makePlot, width=200, processOnInput=True)
        identifyBox = redRGUI.base.groupBox(infobox, label = _('Cluster Identification Options'), orientation = 'horizontal')
        redRGUI.base.button(identifyBox, label = 'Identify', callback = self.identify, width=200)
        self.groupOrHeight = redRGUI.base.radioButtons(identifyBox, label = _('Identify by:'), buttons = ['Groups' , 'Height'], setChecked = 'Groups', orientation = 'horizontal')
        self.groupOrHeightSpin = redRGUI.base.spinBox(identifyBox, label = _('Identify Value:'), min = 1, value = 5)
        #self.startSaturation = redRGUI.base.spinBox(infobox, label = 'Starting Saturation:', min = 0, max = 100)
        #self.endSaturation = redRGUI.base.spinBox(infobox, label = 'Ending Saturation:', min = 0, max = 100)
        #self.endSaturation.setValue(30)
        colorbuttonbox = redRGUI.base.widgetBox(self.controlArea, orientation = 'horizontal')
        #redRGUI.base.button(colorbuttonbox, label = _('Reset Colors'), callback = self.resetColors)
        #redRGUI.base.button(colorbuttonbox, label = _('Set class colors'), callback = self.setClassColors)
        self.heatColorFunctionComboBox = redRGUI.base.comboBox(infobox, label = _('Heatmap Colors'), items = [('bluered', _('Blue to Red')), ('redblue', _('Red to Blue')), ('redgreen', _('Red to Green')), ('greenred', _('Green to Red'))])
        #self.classesDropdown = redRGUI.base.comboBox(infobox, label = 'Classes:', toolTip = 'If classes data is connected you may select columns in the data to represent classes of your columns in the plotted data')
        
        self.rowDendrogram = redRGUI.base.checkBox(infobox, label='Dendrogram Options', displayLabel=False,
        buttons = ['Plot Row Dendrogram', 'Plot Column Dendrogram'], 
        setChecked = ['Plot Row Dendrogram', 'Plot Column Dendrogram'], orientation = 'horizontal')
        
        self.showClasses = redRGUI.base.checkBox(infobox, label='Show Classes', displayLabel=False,
        buttons = ['Show Classes'])
        self.showClasses.setEnabled(False)
        #OWGUI.redRGUI.base.checkBox(infobox, self, )
        self.gview1 = redRGUI.base.graphicsView(self.controlArea,label='Heatmap', displayLabel=False)
        self.gview1.image = 'heatmap1_'+self.widgetID
        #self.gview2 = redRGUI.base.graphicsView(self.controlArea)
        #self.gview2.image = 'heatmap2_'+self.widgetID
    def resetColors(self):
        cd = colorListDialog(self)
        if cd.exec_() != QDialog.Accepted:
            return
        self.listOfColors = cd.listOfColors
    def setClassColors(self):
        cd = colorListDialog(self)
        if cd.exec_() != QDialog.Accepted:
            return
        self.classColors = cd.listOfColors
    def onLoadSavedSession(self):
        self.processSignals()
    def processMatrix(self, data =None):
        
        if data:
            self.plotdata = data.getData()
            if data.optionalDataExists('classes'):
                self.classes = data.getOptionalData('classes')
                self.showClasses.setEnabled(True)
            else:
                self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
            if self.R('class('+self.plotdata+')') == "data.frame":
                self.plotdata = 'data.matrix('+self.plotdata+')'
            self.rowvChoiceprocess()
            if not self.R('is.numeric('+self.plotdata+')'):
                self.status.setText(_('Data connected was not numeric'))
                self.plotdata = ''
            if self.commit.processOnInput():
                self.makePlot()
        else: 
            self.plotdata = ''
    def processClasses(self, data):
        if data:
            self.classesData = data.getData()
            #self.classesDropdown.update(self.R('colnames('+data.data+')', wantType = 'list'))
            self.showClasses.setEnabled(True)
        else:
            #self.classesDropdown.clear()
            self.classesData = ''
    def makePlot(self):
        if self.plotdata == '': return
        self.status.setText("You are plotting "+self.plotdata)
        # if unicode(self.classesDropdown.currentText()) != '':
            # self.classes = self.classesData+'[,\''+unicode(self.classesDropdown.currentText()) + '\']'
        if 'Show Classes' in self.showClasses.getChecked() and self.classesData != '':
            
            
            colClasses = ', ColSideColors= c(%s)[%s]' % (','.join(self.classColors), self.classesData)  #divPalette(length(levels(as.factor(%s))), name="RdYlGn")[%s]' % (self.classesData, self.classesData) 
        else:
            colClasses = ''
        # colorType = unicode(self.colorTypeCombo.currentText())
        # if colorType == 'rainbow':
            # start = float(float(self.startSaturation.value())/100)
            # end = float(float(self.endSaturation.value())/100)
            # print start, end
            # col = 'rev(rainbow(50, start = '+unicode(start)+', end = '+unicode(end)+'))'
        # else:
            # col = colorType+'(50)'
        if 'Plot Row Dendrogram' in self.rowDendrogram.getChecked():
            self.rowvChoice = 'TRUE'
        else:
            self.rowvChoice = 'NA'
        if 'Plot Column Dendrogram' in self.rowDendrogram.getChecked():
            self.colvChoice = 'TRUE'
        else:
            self.colvChoice = 'NA'
        #self.R(, wantType = 'NoConverstion') 
        self.R('%(heatmapList)s<-heatmap.2(%(plotdata)s , trace="none", scale = "row", cexRow=0.5, Rowv=%(rc)s, Colv = %(cc)s, col= %(col)s, key = TRUE %(colclasses)s)' % {'plotdata':self.plotdata, 'rc': self.rowvChoice, 'cc': self.colvChoice, 'colclasses':colClasses, 'col':self.heatColorFunctionComboBox.currentId(), 'heatmapList':self.Rvariables['heatmapList']}, wantType = 'NoConverstion')
        #self.gview1.plot(function = 'heatmap.2', query = '%(plotdata)s , trace="none", scale = "row", cexRow=0.5, Rowv=%(rc)s, Colv = %(cc)s, col= %(col)s, key = TRUE %(colclasses)s' % {'plotdata':self.plotdata, 'rc': self.rowvChoice, 'cc': self.colvChoice, 'colclasses':colClasses, 'col':self.heatColorFunctionComboBox.currentId(), 'heatmapList':self.Rvariables['heatmapList']} )
        newData = signals.base.RList(self, data = self.Rvariables['heatmapList'])
        self.rSend('heatmapList', newData)
        
    def rowvChoiceprocess(self):
        if self.plotdata:
            rowlen = self.R('length(rownames('+self.plotdata+'))')
            if rowlen > 1000:
                self.rowvChoice = 'NA'
            else:
                self.rowvChoice = 'NULL'
                
    def identify(self, kill = True):
        if self.plotdata == '': 
            self.status.setText(_('No Data To Identify'))
            return
        ## needs to be rewritten for Red-R 1.85 which uses rpy3.  no interactivity with graphics.
        
        self.R(self.Rvariables['hclust']+'<-hclust(dist(t('+self.plotdata+')))')
        
        
        ## now there is a plot the user must select the number of groups or the height at which to make the slices.
        print unicode(self.groupOrHeight.getChecked())
        if unicode(self.groupOrHeight.getChecked()) == 'Groups':
            inj = 'k = ' + unicode(self.groupOrHeightSpin.value())
        else:
            inj = 'h = ' + unicode(self.groupOrHeightSpin.value())
        self.R(self.Rvariables['heatsubset']+'<-cutree('+self.Rvariables['hclust']+', '+inj+')')       
        self.gview1.plotMultiple(query = self.Rvariables['hclust']+',col = %s' % self.Rvariables['heatsubset'], layers = ['rect.hclust(%s, %s, cluster = %s, which = 1:%s, border = 2:(%s + 1))' % (self.Rvariables['hclust'], inj, self.Rvariables['heatsubset'], self.groupOrHeightSpin.value(), self.groupOrHeightSpin.value())])
        newData = signals.base.RVector(self, data = 'as.vector('+self.Rvariables['heatsubset']+')', parent = self.Rvariables['heatsubset'])
        self.rSend("id1", newData)
        

        
class colorListDialog(QDialog):
    def __init__(self, parent = None, layout = 'vertical', title = 'Color List Dialog', data = ''):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        if layout == 'horizontal':
            self.setLayout(QHBoxLayout())
        else:
            self.setLayout(QVBoxLayout())
        
        self.listOfColors = []
        self.controlArea = redRGUI.base.widgetBox(self)
        mainArea = redRGUI.base.widgetBox(self.controlArea, 'horizontal')
        leftBox = redRGUI.base.widgetBox(mainArea)
        rightBox = redRGUI.base.widgetBox(mainArea)
        ## GUI
        
        # color list
        self.colorList = redRGUI.base.listBox(leftBox, label = 'Color List')
        redRGUI.base.button(leftBox, label = 'Add Color', callback = self.addColor)
        redRGUI.base.button(leftBox, label = 'Remove Color', callback = self.removeColor)
        redRGUI.base.button(leftBox, label = 'Clear Colors', callback = self.colorList.clear)
        redRGUI.base.button(mainArea, label = 'Finished', callback = self.accept)
        # attribute list
        
        if data:
            self.attsList = listBox(rightBox, label = 'Data Parameters', callback = self.attsListSelected)
            names = self.R('names('+data+')')
            print names
            self.attsList.update(names)
        self.data = data
    def attsListSelected(self):
        ## return a list of numbers coresponding to the levels of the data selected.
        self.listOfColors = self.R('as.numeric(as.factor('+self.data+'$'+unicode(self.attsList.selectedItems()[0])+'))')
        
    def addColor(self):
        colorDialog = QColorDialog(self)
        color = colorDialog.getColor()
        colorDialog.hide()
        newItem = QListWidgetItem()
        newItem.setBackgroundColor(color)
        self.colorList.addItem(newItem, newItem)
        
        self.processColors()
    def removeColor(self):
        for item in self.colorList.selectedItems():
            self.colorList.removeItemWidget(item)
            
        self.processColors()
    def setColors(self, colorList):
        self.colorList.clear()
        try:
            for c in colorList:
                col = QColor()
                col.setNamedColor(unicode(c))
                newItem = QListWidgetItem()
                newItem.setBackgroundColor(col)
                self.colorList.addItem(newItem)
        except:
            pass # it might happen that we can't show the colors that's not good but also not disasterous either.
    def processColors(self):
        self.listOfColors = []
        for item in self.colorList.getItems():
            self.listOfColors.append('"'+unicode(item.backgroundColor().name())+'"')
    def R(self, query):
        return RSession.Rcommand(query = query)

