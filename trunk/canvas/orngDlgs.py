# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington
# Description:
#    signal dialog, canvas options dialog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from orngCanvasItems import MyCanvasText
import OWGUI, sys, os 
import RSession
import redRGUI


class ColorIcon(QToolButton):
    def __init__(self, parent, color):
        QToolButton.__init__(self, parent)
        self.color = color
        self.setMaximumSize(20,20)
        self.connect(self, SIGNAL("clicked()"), self.showColorDialog)
        self.updateColor()

    def updateColor(self):
        pixmap = QPixmap(16,16)
        painter = QPainter()
        painter.begin(pixmap)
        painter.setPen(QPen(self.color))
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0, 0, 16, 16);
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(16,16))


    def drawButtonLabel(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(self.color))
        painter.drawRect(3, 3, self.width()-6, self.height()-6)

    def showColorDialog(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.updateColor()
            self.repaint()

# canvas dialog
class CanvasOptionsDlg(QDialog):
    def __init__(self, canvasDlg, *args):
        apply(QDialog.__init__,(self,) + args)
        self.canvasDlg = canvasDlg
        self.settings = dict(canvasDlg.settings)        # create a copy of the settings dict. in case we accept the dialog, we update the canvasDlg.settings with this dict
        if sys.platform == "darwin":
            self.setWindowTitle("Preferences")
        else:
            self.setWindowTitle("Canvas Options")
        self.topLayout = QVBoxLayout(self)
        self.topLayout.setSpacing(0)
        self.resize(300,300)
        self.toAdd = []
        self.toRemove = []

        self.tabs = QTabWidget(self)
        GeneralTab = OWGUI.widgetBox(self.tabs, margin = 4)
        ExceptionsTab = OWGUI.widgetBox(self.tabs, margin = 4)
        TabOrderTab = OWGUI.widgetBox(self.tabs, margin = 4)
        RSettings = OWGUI.widgetBox(self.tabs, margin = 4)

        self.tabs.addTab(GeneralTab, "General")
        self.tabs.addTab(ExceptionsTab, "Exception handling")
        self.tabs.addTab(TabOrderTab, "Widget tab order")
        self.tabs.addTab(RSettings, 'R Settings')

        # #################################################################
        # GENERAL TAB
        generalBox = OWGUI.widgetBox(GeneralTab, "General Options")
        self.snapToGridCB = OWGUI.checkBox(generalBox, self.settings, "snapToGrid", "Snap widgets to grid", debuggingEnabled = 0)
        self.writeLogFileCB  = OWGUI.checkBox(generalBox, self.settings, "writeLogFile", "Save content of the Output window to a log file", debuggingEnabled = 0)
        self.showSignalNamesCB = OWGUI.checkBox(generalBox, self.settings, "showSignalNames", "Show signal names between widgets", debuggingEnabled = 0)
        self.dontAskBeforeCloseCB= OWGUI.checkBox(generalBox, self.settings, "dontAskBeforeClose", "Don't ask to save schema before closing", debuggingEnabled = 0)
        self.saveWidgetsPositionCB = OWGUI.checkBox(generalBox, self.settings, "saveWidgetsPosition", "Save size and position of widgets", debuggingEnabled = 0)
        self.useContextsCB = OWGUI.checkBox(generalBox, self.settings, "useContexts", "Use context settings")
        self.setDebugModeCheckBox = OWGUI.checkBox(generalBox, self.canvasDlg.output, "debugMode", "Set to debug mode")
        validator = QIntValidator(self)
        validator.setRange(0,10000)

        hbox1 = OWGUI.widgetBox(GeneralTab, orientation = "horizontal")
        hbox2 = OWGUI.widgetBox(GeneralTab, orientation = "horizontal")
        canvasDlgSettings = OWGUI.widgetBox(hbox1, "Canvas Dialog Settings")
        schemeSettings = OWGUI.widgetBox(hbox1, "Scheme Settings") 
         
        self.widthSlider = OWGUI.qwtHSlider(canvasDlgSettings, self.settings, "canvasWidth", minValue = 300, maxValue = 1200, label = "Canvas width:  ", step = 50, precision = " %.0f px", debuggingEnabled = 0)
        self.heightSlider = OWGUI.qwtHSlider(canvasDlgSettings, self.settings, "canvasHeight", minValue = 300, maxValue = 1200, label = "Canvas height:  ", step = 50, precision = " %.0f px", debuggingEnabled = 0)
        OWGUI.separator(canvasDlgSettings)
        
        items = [str(n) for n in QStyleFactory.keys()]
        ind = items.index(self.settings.get("style", "WindowsXP"))
        OWGUI.comboBox(canvasDlgSettings, self.settings, "style", label = "Window style:", orientation = "horizontal", items = [str(n) for n in QStyleFactory.keys()], sendSelectedValue = 1, debuggingEnabled = 0)
        OWGUI.checkBox(canvasDlgSettings, self.settings, "useDefaultPalette", "Use style's standard palette", debuggingEnabled = 0)
        
        if canvasDlg:
            selectedWidgetBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
            self.selectedWidgetIcon = ColorIcon(selectedWidgetBox, canvasDlg.widgetSelectedColor)
            selectedWidgetBox.layout().addWidget(self.selectedWidgetIcon)
            selectedWidgetLabel = OWGUI.widgetLabel(selectedWidgetBox, " Selected widget")

            activeWidgetBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
            self.activeWidgetIcon = ColorIcon(activeWidgetBox, canvasDlg.widgetActiveColor)
            activeWidgetBox.layout().addWidget(self.activeWidgetIcon)
            selectedWidgetLabel = OWGUI.widgetLabel(activeWidgetBox, " Active widget")

            lineBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
            self.lineIcon = ColorIcon(lineBox, canvasDlg.lineColor)
            lineBox.layout().addWidget(self.lineIcon)
            selectedWidgetLabel = OWGUI.widgetLabel(lineBox, " Lines")
            
        OWGUI.separator(schemeSettings)
        items = ["%d x %d" % (v,v) for v in self.canvasDlg.schemeIconSizeList]
        val = min(len(items)-1, self.settings['schemeIconSize'])
        self.schemeIconSizeCombo = OWGUI.comboBoxWithCaption(schemeSettings, self.settings, 'schemeIconSize', "Scheme icon size:", items = items, tooltip = "Set the size of the widget icons on the scheme", debuggingEnabled = 0)
        
        GeneralTab.layout().addStretch(1)

        # #################################################################
        # EXCEPTION TAB
        exceptions = OWGUI.widgetBox(ExceptionsTab, "Exceptions")
        #self.catchExceptionCB = QCheckBox('Catch exceptions', exceptions)
        self.focusOnCatchExceptionCB = OWGUI.checkBox(exceptions, self.settings, "focusOnCatchException", 'Show output window on exception')
        self.printExceptionInStatusBarCB = OWGUI.checkBox(exceptions, self.settings, "printExceptionInStatusBar", 'Print last exception in status bar')

        output = OWGUI.widgetBox(ExceptionsTab, "System output")
        #self.catchOutputCB = QCheckBox('Catch system output', output)
        self.focusOnCatchOutputCB = OWGUI.checkBox(output, self.settings, "focusOnCatchOutput", 'Focus output window on system output')
        self.printOutputInStatusBarCB = OWGUI.checkBox(output, self.settings, "printOutputInStatusBar", 'Print last system output in status bar')

        hboxExc = OWGUI.widgetBox(ExceptionsTab, orientation="horizontal")
        outputCanvas = OWGUI.widgetBox(hboxExc, "Canvas Info Handling")
        outputWidgets = OWGUI.widgetBox(hboxExc, "Widget Info Handling")
        self.ocShow = OWGUI.checkBox(outputCanvas, self.settings, "ocShow", 'Show icon above widget for...')
        self.ocInfo = OWGUI.checkBox(OWGUI.indentedBox(outputCanvas, 10), self.settings, "ocInfo", 'Information')
        self.ocWarning = OWGUI.checkBox(OWGUI.indentedBox(outputCanvas, 10), self.settings, "ocWarning", 'Warnings')
        self.ocError = OWGUI.checkBox(OWGUI.indentedBox(outputCanvas, 10), self.settings, "ocError", 'Errors')

        self.rrshow = OWGUI.checkBox(outputWidgets, self.settings, "owShow", 'Show statusbar info for...')
        self.owInfo = OWGUI.checkBox(OWGUI.indentedBox(outputWidgets, 10), self.settings, "owInfo", 'Information')
        self.owWarning = OWGUI.checkBox(OWGUI.indentedBox(outputWidgets, 10), self.settings, "owWarning", 'Warnings')
        self.owError = OWGUI.checkBox(OWGUI.indentedBox(outputWidgets, 10), self.settings, "owError", 'Errors')

        verbosityBox = OWGUI.widgetBox(ExceptionsTab, "Verbosity", orientation = "horizontal")
        verbosityBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.verbosityCombo = OWGUI.comboBox(verbosityBox, self.settings, "outputVerbosity", label = "Set level of widget output: ", orientation='horizontal', items=["Small", "Medium", "High"])
        ExceptionsTab.layout().addStretch(1)

        # #################################################################
        # TAB ORDER TAB
        tabOrderBox = OWGUI.widgetBox(TabOrderTab, "Set Order of Widget Categories", orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.tabOrderList = QListWidget(tabOrderBox)
        self.tabOrderList.setAcceptDrops(True)

        tabOrderBox.layout().addWidget(self.tabOrderList)
        self.tabOrderList.setSelectionMode(QListWidget.SingleSelection)
        
        ind = 0
        for (name, show) in self.settings["WidgetTabs"]:
            if self.canvasDlg.widgetRegistry.has_key(name):
                self.tabOrderList.addItem(name)
                self.tabOrderList.item(ind).setCheckState(show and Qt.Checked or Qt.Unchecked)
                ind+=1

        w = OWGUI.widgetBox(tabOrderBox, sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.upButton = OWGUI.button(w, self, "Up", callback = self.moveUp)
        self.downButton = OWGUI.button(w, self, "Down", callback = self.moveDown)
        w.layout().addSpacing(20)
        self.addButton = OWGUI.button(w, self, "Add", callback = self.addCategory)
        self.removeButton = OWGUI.button(w, self, "Remove", callback = self.removeCategory)
        self.removeButton.setEnabled(0)
        w.layout().addStretch(1)

        # OK, Cancel buttons
        hbox = OWGUI.widgetBox(self, orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        hbox.layout().addStretch(1)
        self.okButton = OWGUI.button(hbox, self, "OK", callback = self.accept)
        self.cancelButton = OWGUI.button(hbox, self, "Cancel", callback = self.reject)
        self.connect(self.tabOrderList, SIGNAL("currentRowChanged(int)"), self.enableDisableButtons)

        self.topLayout.addWidget(self.tabs)
        self.topLayout.addWidget(hbox)

        #####################################
        # R Settings Tab
        rlibrariesBox = OWGUI.widgetBox(RSettings, 'R Libraries')
        # get a data frame (dict) of r libraries

        self.libs = RSession.Rcommand('getCRANmirrors()')
        # place a listBox in the widget and fill it with a list of mirrors
        self.libListBox = redRGUI.listBox(rlibrariesBox, label = 'Mirrors', items = self.libs['Name'], callback = self.setMirror)
        self.libInfo = redRGUI.widgetLabel(rlibrariesBox, '')
        self.libInfo.setText('Repository URL: '+ self.settings['CRANrepos'])
        
    def setMirror(self):
        # print 'setMirror'
        item = self.libListBox.currentRow()
        self.settings['CRANrepos'] = str(self.libs['URL'][item])
        RSession.Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + str(self.libs['URL'][item]) + '"; options(repos=r)})')
        print self.settings['CRANrepos']
        self.libInfo.setText('Repository URL changed to: '+str(self.libs['URL'][item]))
    def accept(self):
        self.settings["widgetSelectedColor"] = self.selectedWidgetIcon.color.getRgb()
        self.settings["widgetActiveColor"]   = self.activeWidgetIcon.color.getRgb()
        self.settings["lineColor"]           = self.lineIcon.color.getRgb()
        QDialog.accept(self)
        
        

    # move selected widget category up
    def moveUp(self):
        for i in range(1, self.tabOrderList.count()):
            if self.tabOrderList.item(i).isSelected():
                item = self.tabOrderList.takeItem(i)
                for j in range(self.tabOrderList.count()): self.tabOrderList.item(j).setSelected(0)
                self.tabOrderList.insertItem(i-1, item)
                item.setSelected(1)

    # move selected widget category down
    def moveDown(self):
        for i in range(self.tabOrderList.count()-2,-1,-1):
            if self.tabOrderList.item(i).isSelected():
                item = self.tabOrderList.takeItem(i)
                for j in range(self.tabOrderList.count()): self.tabOrderList.item(j).setSelected(0)
                self.tabOrderList.insertItem(i+1, item)
                item.setSelected(1)

    def enableDisableButtons(self, itemIndex):
        self.upButton.setEnabled(itemIndex > 0)
        self.downButton.setEnabled(itemIndex < self.tabOrderList.count()-1)
        catName = str(self.tabOrderList.currentItem().text())
        if not self.canvasDlg.widgetRegistry.has_key(catName): return
        self.removeButton.setEnabled(os.path.normpath(self.canvasDlg.widgetDir) not in os.path.normpath(self.canvasDlg.widgetRegistry[catName].directory))
        #self.removeButton.setEnabled(1)

    def addCategory(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select the folder that contains the add-on:"))
        if dir != "":
            if os.path.split(dir)[1] == "widgets":     # register a dir above the dir that contains the widget folder
                dir = os.path.split(dir)[0]
            if os.path.exists(os.path.join(dir, "widgets")):
                name = os.path.split(dir)[1]
                self.toAdd.append((name, dir))
                self.tabOrderList.addItem(name)
                self.tabOrderList.item(self.tabOrderList.count()-1).setCheckState(Qt.Checked)
            else:
                QMessageBox.information( None, "Information", 'The specified folder does not seem to contain an Orange add-on.', QMessageBox.Ok + QMessageBox.Default)
            
        
    def removeCategory(self):
        curCat = str(self.tabOrderList.item(self.tabOrderList.currentRow()).text())
        if QMessageBox.warning(self,'Orange Canvas', "Unregister widget category '%s' from Orange canvas?\nThis will not remove any files." % curCat, QMessageBox.Ok , QMessageBox.Cancel | QMessageBox.Default | QMessageBox.Escape) == QMessageBox.Ok:
            self.toRemove.append((curCat, self.canvasDlg.widgetRegistry[curCat].directory))
            item = self.tabOrderList.takeItem(self.tabOrderList.row(self.tabOrderList.currentItem()))
            #if item: item.setHidden(1)


class KeyEdit(QLineEdit):
    def __init__(self, parent, key, invdict, widget, invInvDict):
        QLineEdit.__init__(self, parent)
        self.setText(key)
        #self.setReadOnly(True)
        self.invdict = invdict
        self.widget = widget
        self.invInvDict = invInvDict

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete or e.key() == Qt.Key_Backspace:
            pressed = "<none>"
            self.setText(pressed)
            prevkey = self.invdict.get(self.widget)
            if prevkey:
                del self.invdict[self.widget]
                del self.invInvDict[prevkey]
            return

        if e.key() not in range(32, 128): # + range(Qt.Key_F1, Qt.Key_F35+1): -- this wouldn't work, see the line below, and also writing to file etc.
            e.ignore()
            return

        pressed = "-".join(filter(None, [e.modifiers() & x and y for x, y in [(Qt.ControlModifier, "Ctrl"), (Qt.AltModifier, "Alt")]]) + [chr(e.key())])

        assigned = self.invInvDict.get(pressed, None)
        if assigned and assigned != self and QMessageBox.question(self, "Confirmation", "'%(pressed)s' is already assigned to '%(assigned)s'. Override?" % {"pressed": pressed, "assigned": assigned.widget.name}, QMessageBox.Yes | QMessageBox.Default, QMessageBox.No | QMessageBox.Escape) == QMessageBox.No:
            return
        
        if assigned:
            assigned.setText("<none>")
            del self.invdict[assigned.widget]
        self.setText(pressed)
        self.invdict[self.widget] = pressed
        self.invInvDict[pressed] = self
        

# widget shortcuts dialog
class WidgetShortcutDlg(QDialog):
    def __init__(self, canvasDlg, *args):
        import orngTabs

        apply(QDialog.__init__,(self,) + args)
        self.canvasDlg = canvasDlg
        self.setWindowTitle("Widget Shortcuts")
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)
        self.resize(700,500)

        self.invDict = dict([(y, x) for x, y in canvasDlg.widgetShortcuts.items()])
        invInvDict = {}

        self.tabs = QTabWidget(self)
        
        extraTabs = [(name, 1) for name in canvasDlg.widgetRegistry.keys() if name not in [tab for (tab, s) in canvasDlg.settings["WidgetTabs"]]]
        for tabName, show in canvasDlg.settings["WidgetTabs"] + extraTabs:
            if not canvasDlg.widgetRegistry.has_key(tabName):
                continue
            scrollArea = QScrollArea()
            self.tabs.addTab(scrollArea, tabName)
            #scrollArea.setWidgetResizable(1)       # you have to use this or set size to wtab manually - otherwise nothing gets shown

            wtab = QWidget(self.tabs)
            scrollArea.setWidget(wtab)

            widgets = [(int(widgetInfo.priority), name, widgetInfo) for (name, widgetInfo) in canvasDlg.widgetRegistry[tabName].items()]
            widgets.sort()
            rows = (len(widgets)+2) / 3
            layout = QGridLayout(wtab)

            for i, (priority, name, widgetInfo) in enumerate(widgets):
                x = i / rows
                y = i % rows

                hlayout = QHBoxLayout()
                mainBox = QWidget(wtab)
                mainBox.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
                mainBox.setLayout(hlayout)
                layout.addWidget(mainBox, y, x, Qt.AlignTop | Qt.AlignLeft)
                label = QLabel(wtab)
                label.setPixmap(canvasDlg.getWidgetIcon(widgetInfo).pixmap(40))
                hlayout.addWidget(label)

                optionsw = QWidget(self)
                optionsw.setLayout(QVBoxLayout())
                hlayout.addWidget(optionsw)
                optionsw.layout().addStretch(1)

                OWGUI.widgetLabel(optionsw, name)
                key = self.invDict.get(widgetInfo, "<none>")
                le = KeyEdit(optionsw, key, self.invDict, widgetInfo, invInvDict)
                optionsw.layout().addWidget(le)
                invInvDict[key] = le
                le.setFixedWidth(60)

            wtab.resize(wtab.sizeHint())

        # OK, Cancel buttons
        hbox = OWGUI.widgetBox(self, orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        hbox.layout().addStretch(1)
        self.okButton = OWGUI.button(hbox, self, "OK", callback = self.accept)
        self.cancelButton = OWGUI.button(hbox, self, "Cancel", callback = self.reject)
        self.okButton.setDefault(True)

        self.layout().addWidget(self.tabs)
        self.layout().addWidget(hbox)


class AboutDlg(QDialog):
    def __init__(self, *args):
        apply(QDialog.__init__,(self,) + args)
        self.topLayout = QVBoxLayout(self)
        self.setWindowFlags(Qt.Popup)
        
        import redREnviron
        logoImage = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
        logo = OWGUI.widgetLabel(self, "")
        logo.setPixmap(logoImage)
        
        OWGUI.widgetLabel(self, '<p align="center"><h2>Red-R Version 1.7 beta</h2></p>')
        OWGUI.widgetLabel(self, '<p align="center"><h3>Kyle R Covington and Anup Parikh 2010</h3></p>')

        OWGUI.widgetLabel(self, "" )
        #OWGUI.button(self, self, "Close", callback = self.accept)
        b = QDialogButtonBox(self)
        b.setCenterButtons(1)
        self.layout().addWidget(b)
        butt = b.addButton(QDialogButtonBox.Close)
        self.connect(butt, SIGNAL("clicked()"), self.accept)
        
        
if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    dlg = AboutDlg(None)
    dlg.show()
    app.exec_()

