## redRGUI.RFormula; provides a toolkit for editing R formulas where an R funciton may need a formulas

from redRGUI import widgetState
import redRGUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class RFormulaEntry(QWidget, widgetState):
    def __init__(self, parent, label = 'Formula Entry'):
        # make a widgetBox to hold everything
        box = redRGUI.groupBox(parent, label = label)
        
        ## add the elements to the box
        
        #place the command keys
        buttonsBox = redRGUI.groupBox(box, label = "Formula Commands")
        self.plusButton = redRGUI.button(buttonsBox, "And (+)", callback = self.plusButtonClicked)
        self.plusButton.setEnabled(False)
        self.colonButton = redRGUI.button(buttonsBox, "Interacting With (:)", callback = self.colonButtonClicked)
        self.colonButton.setEnabled(False)
        self.starButton = redRGUI.button(buttonsBox, "Together and Interacting (*)", callback = self.starButtonClicked)
        self.starButton.setEnabled(False)
        redRGUI.button(buttonsBox, 'Clear', self.clearFormula)
        self.elementsListBox = redRGUI.listBox(buttonsBox, label = 'Elements', callback = self.FormulaEntryElementSelected)
        self.elementsListBox.setEnabled(True)
        
        # place the formula line edit
        modelBox = redRGUI.groupBox(box, label = "Model Formula", orientation = 'horizontal')
        self.outcomeVariable = redRGUI.comboBox(modelBox, label = 'Outcome (f(x)):')
        redRGUI.widgetLabel(modelBox, ' = ')
        self.modelLineEdit = redRGUI.lineEdit(modelBox, label = None)
    
    def clearFormula(self):
        self.modelLineEdit.clear()
        #self.elementsListBox.clear()
        self.outcomeVariable.clear()
        self.updateEnabled(1)
    def addItems(self, items):
        self.clearFormula()
        self.elementsListBox.clear()
        self.outcomeVariable.addItem('')
        for item in items:
            self.outcomeVariable.addItem(item)
        self.elementsListBox.addItems(items)
        
    def updateEnabled(self, pos):
        # 1 is the beginning state of the widget, 0 is the state after an element is selected
        self.elementsListBox.setEnabled(pos)
        self.plusButton.setEnabled(not pos)
        self.colonButton.setEnabled(not pos)
        self.starButton.setEnabled(not pos)
    def FormulaEntryElementSelected(self):
        self.modelLineEdit.setText(str(self.modelLineEdit.text()) + str(self.elementsListBox.currentItem().text()))
        self.updateEnabled(0)
        
    def plusButtonClicked(self):
        self.modelLineEdit.setText(str(self.modelLineEdit.text()) + ' + ')
        self.updateEnabled(1)
        
    def colonButtonClicked(self):
        self.modelLineEdit.setText(str(self.modelLineEdit.text()) + ' : ')
        self.updateEnabled(1)
        
    def starButtonClicked(self):
        self.modelLineEdit.setText(str(self.modelLineEdit.text()) + ' * ')
        self.updateEnabled(1)
        
    def Formula(self):
        if str(self.outcomeVariable.currentText()) in str(self.modelLineEdit.text()):
            return None
        else:
            return (str(self.outcomeVariable.currentText()), str(self.modelLineEdit.text())) # returns the left and right of the formula.  Users are expected to insert the ~ where appropriate.
    def getSettings(self):
        r = {'items': 'nothing'}
        print 'Formula entry get settings called'
        #r.update(self.getState())
        #print 'r.update in getSettings called and functioning.'
        return {'items': 'nothing'} # complete
        #items = []
        #for item in self.elementsListBox.items():
    def loadSettings(self, data):
        self.setState(data)
        pass # complete
        