# Author: Gregor Leban (gregor.leban@fri.uni-lj.si) modified by Kyle R Covington
# Description:
#    signal dialog, canvas options dialog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import OWGUI,redRQTCore, sys, os 
import RSession
import redREnviron, re, redRStyle, redRObjects
import redRLog
import redRi18n
# def _(a):
    # return a
_ = redRi18n.Coreget_()
class MetaDialog(QDialog):
    def __init__(self, filename):
        QDialog.__init__(self)
        ## GUI
        
        self.setLayout(QVBoxLayout())
        self.layout().setMargin(2)
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.setMinimumSize(QSize(500, 400))
        topWidgetPart = redRQTCore.widgetBox(self, orientation="vertical", margin=0)
        topWidgetPart.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.layout().addWidget(topWidgetPart)
        self.controlArea = redRQTCore.widgetBox(topWidgetPart, orientation="vertical", margin=4)
        
        label = redRQTCore.widgetLabel(self.controlArea, label = _('Meta data for %s not found you can add it now since you appear to be a developer.') % filename)
        
        self.text = redRQTCore.textEdit(self.controlArea, label = _('Widget Meta Data'))
        with open(os.path.join(redREnviron.directoryNames['widgetDir'], 'blank', 'meta', 'widgets', 'widgetTemplate.xml'), 'r') as f:
            g = f.read()
        self.text.insertPlainText(g)
        self.notNow = False
        buttonBox = redRQTCore.widgetBox(self.controlArea, orientation = 'horizontal')
        acceptButton = redRQTCore.button(buttonBox, label = _('OK'), callback = self.accept)
        rejectButton = redRQTCore.button(buttonBox, label = _('Cancel'), callback = self.reject)
        doneButton = redRQTCore.button(buttonBox, label = _('Not Now'), callback = self.notNowCallback)
    def notNowCallback(self):
        self.notNow = True
        self.reject()
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
    def __init__(self, canvasDlg):
        QDialog.__init__(self,canvasDlg)
        self.canvasDlg = canvasDlg
        self.settings = dict(redREnviron.settings)        # create a copy of the settings dict. in case we accept the dialog, we update the redREnviron.settings with this dict
        if sys.platform == "darwin":
            self.setWindowTitle(_("Preferences"))
        else:
            self.setWindowTitle(_("Canvas Options"))
        self.topLayout = QVBoxLayout(self)
        self.topLayout.setSpacing(10)
        self.resize(450,300)
        self.toAdd = []
        self.toRemove = []

        self.tabs = QTabWidget(self)
        GeneralTab = OWGUI.widgetBox(self.tabs, margin = 4)
        GeneralTab.layout().setAlignment(Qt.AlignTop)
        # lookandFeel = OWGUI.widgetBox(self.tabs, margin = 4)
        # lookandFeel.layout().setAlignment(Qt.AlignTop)
        UnderHood = OWGUI.widgetBox(self.tabs, margin = 4)
        UnderHood.layout().setAlignment(Qt.AlignTop)
        ExceptionsTab = OWGUI.widgetBox(self.tabs, margin = 4)
        ExceptionsTab.layout().setAlignment(Qt.AlignTop)
        RSettings = OWGUI.widgetBox(self.tabs, margin = 4)
        RSettings.layout().setAlignment(Qt.AlignTop)
        
        self.tabs.addTab(GeneralTab, "General")
        # self.tabs.addTab(lookandFeel, "Look and Feel")
        self.tabs.addTab(UnderHood, "Under the Hood")
        self.tabs.addTab(ExceptionsTab, "Exceptions & Logging")
        self.tabs.addTab(RSettings, _('R Settings'))
        QObject.connect(self.tabs, SIGNAL('currentChanged(int)'), self.onTabChange)
        #GeneralTab.layout().addStretch(1)
        
        # #################################################################
        # GENERAL TAB
        generalBox = OWGUI.widgetBox(GeneralTab, _('General Options'))
        
        self.emailEdit = OWGUI.lineEdit(generalBox, self.settings, "email", _("Email Address:"), orientation = 'horizontal')
        
        # self.helpModeSelection = OWGUI.checkBox(generalBox,self.settings,'helpMode',
        # _('Show help icons'))

        
        self.checkForUpdates = redRQTCore.checkBox(generalBox, label = 'checkForUpdates', displayLabel = 0, buttons = [('checkForUpdates',_("Periodically Check For Updates"))])
        if redREnviron.settings['checkForUpdates']:
            self.checkForUpdates.setChecked('checkForUpdates')
        
        self.checkForPackageUpdates = redRQTCore.checkBox(generalBox, label = 'checkForPackageUpdates', displayLabel = 0, buttons = [('checkForPackageUpdates',_("Periodically Check For Package Updates"))])
        if redREnviron.settings['checkForPackageUpdates']:
            self.checkForPackageUpdates.setChecked('checkForPackageUpdates')

        self.dontAskBeforeCloseCB= OWGUI.checkBox(generalBox, self.settings, "dontAskBeforeClose", 
        _("Don't ask to save schema before closing"), debuggingEnabled = 0)
            
        self.dontAskBeforeDeleting = redRQTCore.checkBox(generalBox, label = 'askbeforedelete', displayLabel = 0, buttons = [('ask',_("Ask Before Deleting Widget"))])
        
        if redREnviron.settings['askBeforeWidgetDelete']:
            self.dontAskBeforeDeleting.setChecked('ask')
        
        
        # #################################################################
        # LOOK AND FEEL TAB
        
        # validator = QIntValidator(self)
        # validator.setRange(0,10000)
        lookFeelBox = OWGUI.widgetBox(GeneralTab, _("Look and Feel Options"))

        self.snapToGridCB = OWGUI.checkBox(lookFeelBox, self.settings, "snapToGrid", 
        _("Snap widgets to grid"), debuggingEnabled = 0)
        self.showSignalNamesCB = OWGUI.checkBox(lookFeelBox, self.settings, "showSignalNames", 
        _("Show signal names between widgets"), debuggingEnabled = 0)
        self.saveWidgetsPositionCB = OWGUI.checkBox(lookFeelBox, self.settings, "saveWidgetsPosition", 
        _("Save size and position of widgets"), debuggingEnabled = 0)
        
        items = ["%d x %d" % (v,v) for v in redRStyle.iconSizeList]
        # val = min(len(items)-1, self.settings['schemeIconSize'])
        self.schemeIconSizeCombo = OWGUI.comboBoxWithCaption(lookFeelBox, self.settings, 'schemeIconSize', 
        _("Scheme icon size:"), items = items, tooltip = _("Set the size of the widget icons on the scheme"), 
        debuggingEnabled = 0)

        # redREnviron.settings["toolbarIconSize"] = min(len(items)-1, redREnviron.settings["toolbarIconSize"])
        
        self.toolbarIconSizeCombo = OWGUI.comboBoxWithCaption(lookFeelBox, self.settings, "toolbarIconSize", 
        _("Widget Tree Icon size:"), items = items, 
        tooltip = _("Set the size of the widget icons in the toolbar, tool box, and tree view area"), 
        debuggingEnabled = 0)

        # hbox1 = OWGUI.widgetBox(GeneralTab, orientation = "horizontal")
        
        # canvasDlgSettings = OWGUI.widgetBox(hbox1, "Canvas Dialog Settings")
        # schemeSettings = OWGUI.widgetBox(hbox1, "Scheme Settings") 
         
        # self.widthSlider = OWGUI.qwtHSlider(canvasDlgSettings, self.settings, "canvasWidth", 
        # minValue = 300, maxValue = 1200, label = "Canvas width:  ", step = 50, precision = " %.0f px", debuggingEnabled = 0)
        
        # self.heightSlider = OWGUI.qwtHSlider(canvasDlgSettings, self.settings, "canvasHeight", 
        # minValue = 300, maxValue = 1200, label = "Canvas height:  ", step = 50, precision = " %.0f px", debuggingEnabled = 0)
        
        # OWGUI.separator(canvasDlgSettings)
        

        OWGUI.comboBox(lookFeelBox, self.settings, "style", label = _("Window style:"), orientation = "horizontal", 
        items = redRStyle.QtStyles, sendSelectedValue = 1, debuggingEnabled = 0)
        #OWGUI.checkBox(lookFeelBox, self.settings, "useDefaultPalette", _("Use style's standard palette"), debuggingEnabled = 0)
        
        self.language = redRQTCore.listBox(lookFeelBox, label = _('Language'), items = self.settings['language'], enableDragDrop = 1)
        # selectedWidgetBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
        # self.selectedWidgetIcon = ColorIcon(selectedWidgetBox, redRStyle.widgetSelectedColor)
        # selectedWidgetBox.layout().addWidget(self.selectedWidgetIcon)
        # selectedWidgetLabel = OWGUI.widgetLabel(selectedWidgetBox, " Selected widget")

        # activeWidgetBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
        # self.activeWidgetIcon = ColorIcon(activeWidgetBox, redRStyle.widgetActiveColor)
        # activeWidgetBox.layout().addWidget(self.activeWidgetIcon)
        # selectedWidgetLabel = OWGUI.widgetLabel(activeWidgetBox, " Active widget")

        # activeLineBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
        # self.activeLineIcon = ColorIcon(activeLineBox, redRStyle.lineColor)
        # activeLineBox.layout().addWidget(self.activeLineIcon)
        # selectedWidgetLabel = OWGUI.widgetLabel(activeLineBox, " Active Lines")

        # inactiveLineBox = OWGUI.widgetBox(schemeSettings, orientation = "horizontal")
        # self.inactiveLineIcon = ColorIcon(inactiveLineBox, redRStyle.lineColor)
        # inactiveLineBox.layout().addWidget(self.inactiveLineIcon)
        # selectedWidgetLabel = OWGUI.widgetLabel(inactiveLineBox, " Inactive Lines")
        
        # #################################################################
        # UNDER THE HOOD TAB
        templates = OWGUI.widgetBox(UnderHood, _("Templates Add On Dirs"))
        self.templateDirsListBox = redRQTCore.listBox(templates, label = _("Template Directories"), items = redREnviron.settings['templateDirectories'])
        templateButtons = redRQTCore.widgetBox(templates, orientation = 'horizontal')
        redRQTCore.button(templateButtons, label = _('Add Directory'), callback = self.addTemplateDirectory)
        redRQTCore.button(templateButtons, label = _('Remove Selected'), callback = self.removeTemplateDirectory)
        
        redRQTCore.button(UnderHood, label = _('Regression Test (Core Developers Only)'), callback = lambda val = 1:self.regressionTest(val))
        redRQTCore.button(UnderHood, label = _('Test Packages (Core Developers Only)'), callback = lambda val = 2:self.regressionTest(val))
        redRQTCore.button(UnderHood, label = _('Create help index.'), callback = self.createHelpIndex)
        #redRQTCore.button(UnderHood, label = _('Create Red-R Documentation'), callback = self.createPackageDocs)
        
        

        # #################################################################
        # EXCEPTION TAB
        
        debug = OWGUI.widgetBox(ExceptionsTab, _("Debug"))
        # self.setDebugModeCheckBox = OWGUI.checkBox(debug, self.settings, "debugMode", "Set to debug mode") # sets the debug mode of the canvas.
        
        
        self.verbosityCombo = OWGUI.comboBox(debug, self.settings, "outputVerbosity", label = _("Set level of widget output: "), 
        orientation='horizontal', items=redRLog.logLevelsName)
        self.displayTraceback = OWGUI.checkBox(debug, self.settings, "displayTraceback", _('Display Traceback'))
        
        # self.exceptionLevel = redRQTCore.spinBox(debug, label = 'Exception Print Level:', toolTip = 'Select the level of exception that will be printed to the Red-R general output', min = 0, max = 9, value = redREnviron.settings['exceptionLevel'])
        # self.otherLevel = redRQTCore.spinBox(debug, label = 'General Print Level:', toolTip = _('Select the level of general logging that will be output to the general output'), min = 0, max = 9, value = redREnviron.settings['minSeverity'])
        
        exceptions = OWGUI.widgetBox(ExceptionsTab, _("Exceptions"))
        #self.catchExceptionCB = QCheckBox(_('Catch exceptions'), exceptions)
        self.focusOnCatchExceptionCB = OWGUI.checkBox(exceptions, self.settings, "focusOnCatchException", _('Show output window on exception'))
        # self.printExceptionInStatusBarCB = OWGUI.checkBox(exceptions, self.settings, "printExceptionInStatusBar", _('Print last exception in status bar'))
        self.printExceptionInStatusBarCB = OWGUI.checkBox(exceptions, self.settings, "uploadError", _('Submit Error Report'))
        self.printExceptionInStatusBarCB = OWGUI.checkBox(exceptions, self.settings, "askToUploadError", _('Always ask before submitting error report'))

        output = OWGUI.widgetBox(ExceptionsTab, _("Log File"))
        #self.catchOutputCB = QCheckBox(_('Catch system output'), output)
        self.writeLogFileCB  = OWGUI.checkBox(output, self.settings, "writeLogFile", 
        _("Save content of the Output window to a log file"))
        hbox = OWGUI.widgetBox(output, orientation = "horizontal")
        
        self.logFile = redRQTCore.lineEdit(hbox, label= _("Log Dir:"), orientation = 'horizontal',
        text=self.settings['logsDir'])
        self.okButton = OWGUI.button(hbox, self, _("Browse"), callback = self.browseLogFile)
        #self.showOutputLog = redRQTCore.button(output, label = _('Show Log File'), callback = self.showLogFile)
        self.numberOfDays = redRQTCore.spinBox(output, label = 'Keep Log Files for X days:', min = -1, value = self.settings['keepForXDays'], callback = self.numberOfDaysChanged)
        
        # self.focusOnCatchOutputCB = OWGUI.checkBox(output, self.settings, "focusOnCatchOutput", _('Focus output window on system output'))
        # self.printOutputInStatusBarCB = OWGUI.checkBox(output, self.settings, "printOutputInStatusBar", _('Print last system output in status bar'))

        ExceptionsTab.layout().addStretch(1)

        #####################################
        # R Settings Tab
        self.rlibrariesBox = OWGUI.widgetBox(RSettings, _('R Libraries'))
        redRQTCore.button(RSettings, label = _('Update R Libraries'), callback = self.updatePackages)
        self.libInfo = redRQTCore.widgetLabel(self.rlibrariesBox, label='Repository URL:\n '+ self.settings['CRANrepos'])
        self.libListBox = redRQTCore.listBox(self.rlibrariesBox, label = _('Mirrors'), 
        callback = self.setMirror)

        
        ################################ Global buttons  ######################
        # OK, Cancel buttons
        hbox = OWGUI.widgetBox(self, orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        hbox.layout().addStretch(1)
        self.okButton = OWGUI.button(hbox, self, _("OK"), callback = self.accept)
        self.cancelButton = OWGUI.button(hbox, self, _("Cancel"), callback = self.reject)
        #self.connect(self.tabOrderList, SIGNAL("currentRowChanged(int)"), self.enableDisableButtons)

        self.topLayout.addWidget(self.tabs)
        self.topLayout.addWidget(hbox)
    # def createPackageDocs(self):
        # import doc.createDoc as createDoc
        # createDoc.makeDoc(redREnviron.directoryNames['redRDir'])
    def createHelpIndex(self):
        import docSearcher
        docSearcher.createIndex(redREnviron.directoryNames['redRDir'])
        
    def regressionTest(self, val):
        import redRRegressionTest
        redRRegressionTest.test(val)
        
    def addTemplateDirectory(self):
        """This function is called to add a directory to the list of template directories.  This will repopulate the list box and update redREnviron."""
        dn = QFileDialog.getExistingDirectory(self, "Template Directory", redREnviron.directoryNames['documentsDir'])
        if dn.isEmpty(): return
        dn = unicode(dn)
        
        if dn in redREnviron.settings['templateDirectories']:
            return
        else:
            redREnviron.settings['templateDirectories'] += [dn]
        self.templateDirsListBox.update(redREnviron.settings['templateDirectories'])
        
    def removeTemplateDirectory(self):
        mb = QMessageBox(QMessageBox.Question, _('Remove Template Directories'), _('Are you sure that you want to remove the selected template directories?'), QMessageBox.Yes | QMessageBox.No)
        if mb.exec_() == QMessageBox.No: return
        selections = self.templateDirsListBox.selectedIds()
        for s in selections:
            redREnviron.settings['templateDirectories'].remove(s)
            
        self.templateDirsListBox.update(redREnviron.settings['templateDirectories'])
        
        
    def updatePackages(self):
        url = redREnviron.settings['CRANrepos']
        RSession.Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + url + '"; options(repos=r)})',silent=True)
        RSession.updatePackages(repository = url)
    def numberOfDaysChanged(self):
        redRLog.log(redRLog.DEBUG, redRLog.ERROR, 'changing day value to %s' % int(self.numberOfDays.value()))
        self.settings['keepForXDays'] = int(self.numberOfDays.value())
    
    def browseLogFile(self):
        fn = QFileDialog.getExistingDirectory(self, _("Save Logs To"), redREnviron.settings['logsDir'])
        #print unicode(fn)
        if fn.isEmpty(): return
        self.logFile.setText(fn)
        
        
    def onTabChange(self,index):
        # print 'onTabChange',index
        # get a data frame (dict) of r libraries
        if self.tabs.tabText(index) != _('R Settings'):
            return
        self.libs = RSession.Rcommand('getCRANmirrors()')
        #print self.libs
        self.libListBox.clear()
        self.libListBox.addItems(zip(self.libs['URL'],self.libs['Name']))
        self.libListBox.setSelectedIds([self.settings['CRANrepos']])
        
    def setMirror(self):
        # print 'setMirror'
        url = self.libListBox.selectedIds()[0]
        self.settings['CRANrepos'] = url #unicode(self.libs['URL'][item])
        RSession.Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + url + '"; options(repos=r)})',silent=True)
        #print self.settings['CRANrepos']
        self.libInfo.setText('Repository URL changed to:\n %s'%url)
    def accept(self):
        # self.settings["widgetSelectedColor"] = self.selectedWidgetIcon.color.getRgb()
        # self.settings["widgetActiveColor"]   = self.activeWidgetIcon.color.getRgb()
        # self.settings["lineColor"]           = self.activeLineIcon.color.getRgb()
        
        # self.settings["exceptionLevel"] = int(self.exceptionLevel.value())
        # self.settings["minSeverity"] = int(self.otherLevel.value())
        
        # self.settings['helpMode'] = (str(self.helpModeSelection.getChecked()) in _('Show Help Icons'))
        # print self.settings
        
        self.settings['keepForXDays'] = int(self.numberOfDays.value())
        
        #redREnviron.settings['language'] != self.settings['language']
        self.settings['language'] = self.language.getItems()
        if redREnviron.settings['language'] != self.settings['language']: 
            mb = QMessageBox(_("Options"), _("You must restart Red-R for all the changes to take effect."), QMessageBox.Information, 
            QMessageBox.Ok | QMessageBox.Default,
            QMessageBox.NoButton, 
            QMessageBox.NoButton, 
            qApp.canvasDlg)
            mb.exec_()
        
        if 'ask' in self.dontAskBeforeDeleting.getCheckedIds():
          self.settings['askBeforeWidgetDelete'] = 1
        else:
          self.settings['askBeforeWidgetDelete'] = 0
        
        self.settings['checkForUpdates'] =  'checkForUpdates' in self.checkForUpdates.getCheckedIds()
        self.settings['checkForPackageUpdates'] =  'checkForPackageUpdates' in self.checkForPackageUpdates.getCheckedIds()
        
        self.settings['logsDir'] = self.logFile.text()
        if redREnviron.settings['logsDir'] != self.settings['logsDir']:
            redRLog.fileLogger.moveLogFile(redREnviron.settings['logsDir'],self.settings['logsDir'])
        
        redREnviron.settings.update(self.settings)
        redREnviron.saveSettings()
        
        #print redREnviron.settings['logsDir']
        # redRStyle.widgetSelectedColor = self.settings["widgetSelectedColor"]
        # redRStyle.widgetActiveColor   = self.settings["widgetActiveColor"]  
        # redRStyle.lineColor           = self.settings["lineColor"]          
        
        # update settings in widgets in current documents
        for widget in self.canvasDlg.schema.widgets():
            widget.instance()._owInfo      = redREnviron.settings["owInfo"]
            widget.instance()._owWarning   = redREnviron.settings["owWarning"]
            widget.instance()._owError     = redREnviron.settings["owError"]
            widget.instance()._owShowStatus= redREnviron.settings["owShow"]
            # widget.instance.updateStatusBarState()
            widget.resetWidgetSize()
            widget.updateWidgetState()
            widget.update()
        # update tooltips for lines in all documents
        for line in self.canvasDlg.schema.lines():
            line.showSignalNames = redREnviron.settings["showSignalNames"]
            line.updateTooltip()

        redRObjects.activeTab().repaint()
        qApp.canvasDlg.update()
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
        catName = unicode(self.tabOrderList.currentItem().text())
        if not self.canvasDlg.widgetRegistry.has_key(catName): return
        self.removeButton.setEnabled(os.path.normpath(redREnviron.directoryNames['widgetDir']) not in os.path.normpath(self.canvasDlg.widgetRegistry[catName].directory))
        #self.removeButton.setEnabled(1)

    def addCategory(self):
        dir = unicode(QFileDialog.getExistingDirectory(self, _("Select the folder that contains the add-on:")))
        if dir != "":
            if os.path.split(dir)[1] == "widgets":     # register a dir above the dir that contains the widget folder
                dir = os.path.split(dir)[0]
            if os.path.exists(os.path.join(dir, "widgets")):
                name = os.path.split(dir)[1]
                self.toAdd.append((name, dir))
                self.tabOrderList.addItem(name)
                self.tabOrderList.item(self.tabOrderList.count()-1).setCheckState(Qt.Checked)
            else:
                QMessageBox.information( None, _("Information"), _('The specified folder does not seem to contain a Red-R add-on.'), QMessageBox.Ok + QMessageBox.Default)
            
        
    def removeCategory(self):
        curCat = unicode(self.tabOrderList.item(self.tabOrderList.currentRow()).text())
        if QMessageBox.warning(self,_('Red-R Canvas'), _("Unregister widget category '%s' from Red-R canvas?\nThis will not remove any files.") % curCat, QMessageBox.Ok , QMessageBox.Cancel | QMessageBox.Default | QMessageBox.Escape) == QMessageBox.Ok:
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
        if assigned and assigned != self and QMessageBox.question(self, _("Confirmation"), _("'%(pressed)s' is already assigned to '%(assigned)s'. Override?") % {"pressed": pressed, "assigned": assigned.widget.name}, QMessageBox.Yes | QMessageBox.Default, QMessageBox.No | QMessageBox.Escape) == QMessageBox.No:
            return
        
        if assigned:
            assigned.setText("<none>")
            del self.invdict[assigned.widget]
        self.setText(pressed)
        self.invdict[self.widget] = pressed
        self.invInvDict[pressed] = self
        
class TemplateDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        
        self.setWindowTitle(_('Save as template'))
        
        self.setLayout(QVBoxLayout())
        layout = self.layout()
        
        mainWidgetBox = QWidget(self)
        mainWidgetBox.setLayout(QVBoxLayout())
        layout.addWidget(mainWidgetBox)
        
        mainWidgetBox.layout().addWidget(QLabel(_('Set tags as comma ( , ) delimited list'), mainWidgetBox))
        
        
        topWidgetBox = QWidget(mainWidgetBox)
        topWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(topWidgetBox)
        
        topWidgetBox.layout().addWidget(QLabel(_('Template Name:'), topWidgetBox))
        self.nameEdit = QLineEdit(topWidgetBox)
        topWidgetBox.layout().addWidget(self.nameEdit)
        
        topWidgetBox.layout().addWidget(QLabel(_('Tags:'), topWidgetBox))
        self.tagsList = QLineEdit(topWidgetBox)
        topWidgetBox.layout().addWidget(self.tagsList)
        
        bottomWidgetBox = QWidget(mainWidgetBox)
        bottomWidgetBox.setLayout(QVBoxLayout())
        mainWidgetBox.layout().addWidget(bottomWidgetBox)
        
        bottomWidgetBox.layout().addWidget(QLabel(_('Description:'), bottomWidgetBox))
        self.descriptionEdit = QTextEdit(bottomWidgetBox)
        bottomWidgetBox.layout().addWidget(self.descriptionEdit)
        
        buttonWidgetBox = QWidget(mainWidgetBox)
        buttonWidgetBox.setLayout(QHBoxLayout())
        mainWidgetBox.layout().addWidget(buttonWidgetBox)
        
        acceptButton = QPushButton(_('Accept'), buttonWidgetBox)
        cancelButton = QPushButton(_('Cancel'), buttonWidgetBox)
        buttonWidgetBox.layout().addWidget(acceptButton)
        buttonWidgetBox.layout().addWidget(cancelButton)
        QObject.connect(acceptButton, SIGNAL("clicked()"), self.accept)
        QObject.connect(cancelButton, SIGNAL("clicked()"), self.reject)
        
# widget shortcuts dialog
class WidgetShortcutDlg(QDialog):
    def __init__(self, canvasDlg, *args):
        apply(QDialog.__init__,(self,) + args)
        self.canvasDlg = canvasDlg
        self.setWindowTitle(_("Widget Shortcuts"))
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)
        self.resize(700,500)

        self.invDict = dict([(y, x) for x, y in canvasDlg.widgetShortcuts.items()])
        invInvDict = {}

        self.tabs = QTabWidget(self)
        
        extraTabs = [(name, 1) for name in canvasDlg.widgetRegistry.keys() if name not in [tab for (tab, s) in redREnviron.settings["WidgetTabs"]]]
        for tabName, show in redREnviron.settings["WidgetTabs"] + extraTabs:
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
                label.setPixmap(QIcon(widgetInfo.icon).pixmap(40))
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
        self.okButton = OWGUI.button(hbox, self, _("OK"), callback = self.accept)
        self.cancelButton = OWGUI.button(hbox, self, _("Cancel"), callback = self.reject)
        self.okButton.setDefault(True)

        self.layout().addWidget(self.tabs)
        self.layout().addWidget(hbox)


class AboutDlg(QDialog):
    def __init__(self, *args):
        apply(QDialog.__init__,(self,) + args)
        self.topLayout = QVBoxLayout(self)
        self.setWindowFlags(Qt.Popup)
        
        logoImage = QPixmap(os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png"))
        logo = redRQTCore.widgetLabel(self, "")
        logo.setPixmap(logoImage)
        info = redREnviron.version
        self.about = redRQTCore.webViewBox(self,label=_('About Info'),displayLabel=False)
        self.about.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.about.setMinimumHeight(190)

        self.about.setHtml('<h2>%(NAME)s %(REDRVERSION)s</h2>Type: %(TYPE)s <br> Revision: %(SVNVERSION)s <br> Build Time: %(DATE)s <br> R Version: %(RVERSION)s <br><h3>Red-R Core Development Team (<a href="http://www.red-r.org">Red-R.org</a>)</h3>' % info)
        self.licenceButton = redRQTCore.button(self, _('Licence'), callback = self.showLicence)
        b = QDialogButtonBox(self)
        b.setCenterButtons(1)
        self.layout().addWidget(b)
        butt = b.addButton(QDialogButtonBox.Close)
        self.connect(butt, SIGNAL("clicked()"), self.accept)
    def showLicence(self):
        ## show the Red-R licence
        
        file = open(os.path.join(redREnviron.directoryNames['redRDir'], 'licence.txt'), 'r')
        text = file.read()
        file.close()
        
        self.about.setHtml('<pre>'+text+'</pre>')
        
class MyCanvasText(QGraphicsSimpleTextItem):
    def __init__(self, canvas, text, x, y, flags=Qt.AlignLeft, bold=0, show=1):
        QGraphicsSimpleTextItem.__init__(self, text, None, canvas)
        self.setPos(x,y)
        self.setPen(QPen(Qt.black))
        self.flags = flags
        if bold:
            font = self.font();
            font.setBold(1);
            self.setFont(font)
        if show:
            self.show()

    def paint(self, painter, option, widget = None):
        #painter.resetMatrix()
        painter.setPen(self.pen())
        painter.setFont(self.font())

        xOff = 0; yOff = 0
        rect = painter.boundingRect(QRectF(0,0,2000,2000), self.flags, self.text())
        if self.flags & Qt.AlignHCenter: xOff = rect.width()/2.
        elif self.flags & Qt.AlignRight: xOff = rect.width()
        if self.flags & Qt.AlignVCenter: yOff = rect.height()/2.
        elif self.flags & Qt.AlignBottom:yOff = rect.height()
        #painter.drawText(self.pos().x()-xOff, self.pos().y()-yOff, rect.width(), rect.height(), self.flags, self.text())
        painter.drawText(-xOff, -yOff, rect.width(), rect.height(), self.flags, self.text())
        
# #######################################
# # Signal dialog - let the user select active signals between two widgets, this is called when the connections are ambiguous.
# #######################################
class SignalDialog(QDialog):
    def __init__(self, canvasDlg, *args):
        #apply(QDialog.__init__,(self,) + args)
        QDialog.__init__(self,canvasDlg)
        self.canvasDlg = canvasDlg

        self.signals = []
        self._links = []
        self.allSignalsTaken = 0

        # GUI    ### canvas dialog that is shown when there are multiple possible connections.
        self.setWindowTitle(_('Connect Signals'))
        self.setLayout(QVBoxLayout())

        self.canvasGroup = OWGUI.widgetBox(self, 1)
        self.canvas = QGraphicsScene(0,0,1000,1000)
        self.canvasView = SignalCanvasView(self, self.canvasDlg, self.canvas, self.canvasGroup)
        self.canvasGroup.layout().addWidget(self.canvasView)

        buttons = OWGUI.widgetBox(self, orientation = "horizontal", sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.buttonHelp = OWGUI.button(buttons, self, "&Help")
        buttons.layout().addStretch(1)
        self.buttonClearAll = OWGUI.button(buttons, self, "Clear &All", callback = self.clearAll)
        self.buttonOk = OWGUI.button(buttons, self, "&OK", callback = self.accept)
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        self.buttonCancel = OWGUI.button(buttons, self, "&Cancel", callback = self.reject)

    def clearAll(self):
        while self._links != []:
            self.removeLink(self._links[0][0], self._links[0][1])

    def setOutInWidgets(self, outWidget, inWidget):
        self.outWidget = outWidget
        self.inWidget = inWidget
        (width, height) = self.canvasView.addSignalList(outWidget, inWidget)
        self.canvas.setSceneRect(0, 0, width, height)
        self.resize(width+50, height+80)
        
        ## process the signals so that active connections are show.
        #links = outWidget.instance().outputs.getSignalLinks(inWidget.instance())
        import redRSignalManager
        links = redRSignalManager.getLinksByWidgetInstance(outWidget.instance(), inWidget.instance())
        for o, i, e, n in links:
            self.addLink(o.wid, i.wid)
        #print _('Output Handler Returned the following links'), links

    def countCompatibleConnections(self, outputs, inputs, outInstance, inInstance, outType, inType):
        count = 0
        for outS in outputs:
            if outInstance.getOutputType(outS.name) == None: continue  # ignore if some signals don't exist any more, since we will report error somewhere else
            if outInstance.getOutputType(outS.name) == 'All': pass
            elif not issubclass(outInstance.getOutputType(outS.name), outType): continue
            for inS in inputs:
                if inInstance.getOutputType(inS.name) == None: continue  # ignore if some signals don't exist any more, since we will report error somewhere else
                if inInstance.getOutputType(inS.name) == 'All': 
                    count += 1
                    continue
                if type(inInstance.getOutputType(inS.name)) not in [list]:
                    if not issubclass(inType, inInstance.getInputType(inS.name)): continue
                    if issubclass(outInstance.getOutputType(outS.name), inInstance.getInputType(inS.name)): count+= 1
                else:
                    for i in type(inInstance.getOutputType(inS.name)):
                        if not issubclass(inType, i): continue
                        if issubclass(outInstance.getOutputType(outS.name), i): count+= 1
        return count

    def addLink(self, outName, inName):
        if (outName, inName) in self._links: 
            #print _('signal already in the links')
            return 1
        #print outName, inName, _('Names')
        # check if correct types
        outType = self.outWidget.instance().outputs.getSignal(outName).signalClass
        inType = self.inWidget.instance().inputs.getSignal(inName).signalClass
        if not outType or not inType:
            raise Exception, _('None sent as signal type')
            
            
        if not self.inWidget.instance().inputs.doesSignalMatch(inName, outType): 
            mb = QMessageBox("Failed to Connect", "Not valid connection.\nWould you like to force this connection anyway?\n\nTHIS MIGHT CAUSE ERRORS AND EVEN CRASH RED-R!!!", 
                QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                QMessageBox.No | QMessageBox.Escape, QMessageBox.NoButton)
            if mb.exec_() == QMessageBox.No:
                return 0
            
        inSignal = None
        inputs = self.inWidget.instance().inputs.getAllInputs()
        for wid, signal in inputs.items():
            if wid == inName: inSignal = wid

        # if inName is a single signal and connection already exists -> delete it
        for (outN, inN) in self._links:
            #print inSignal, inN, inName, self.inWidget.instance().inputs.getSignal(inSignal)['multiple']
            if inSignal and inN == inName and not self.inWidget.instance().inputs.getSignal(inSignal).multiple:
                self.removeLink(outN, inN)

        self._links.append((outName, inName))
        self.canvasView.addLink(outName, inName)
        return 1


    def removeLink(self, outName, inName): #removes from the list of instances
        res = QMessageBox.question(self.canvasView, 'Red-R Connections', 'Are you sure you want to remove that signal?\n\nThe downstream widget will recieve empty data.', QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.outWidget.instance().outputs.removeSignal(self.inWidget.instance().inputs.getSignal(inName), outName)
            self.canvasView.removeLink(outName, inName)
            self._links.remove((outName, inName))

    def getLinks(self):
        return self._links
# this class is needed by signalDialog to show widgets and lines
class SignalCanvasView(QGraphicsView):
    def __init__(self, dlg, canvasDlg, *args):
        apply(QGraphicsView.__init__,(self,) + args)
        self.dlg = dlg
        self.canvasDlg = canvasDlg
        self.bMouseDown = False
        self.tempLine = None
        self.inWidget = None
        self.outWidget = None
        self.inWidgetIcon = None
        self.outWidgetIcon = None
        self.lines = []
        self.outBoxes = []
        self.inBoxes = []
        self.texts = []
        self.ensureVisible(0,0,1,1)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setRenderHint(QPainter.Antialiasing)

    def addSignalList(self, outWidget, inWidget):
        self.scene().clear()
        outputs, inputs = outWidget.instance().outputs.getAllOutputs(), inWidget.instance().inputs.getAllInputs()
        outIcon, inIcon = QIcon(outWidget.widgetInfo.icon), QIcon(inWidget.widgetInfo.icon)
        self.lines = []
        self.outBoxes = []
        self.inBoxes = []
        self.texts = []
        xSpaceBetweenWidgets = 100  # space between widgets
        xWidgetOff = 10             # offset for widget position
        yWidgetOffTop = 10          # offset for widget position
        yWidgetOffBottom = 30       # offset for widget position
        ySignalOff = 10             # space between the top of the widget and first signal
        ySignalSpace = 50           # space between two neighbouring signals
        ySignalSize = 20            # height of the signal box
        xSignalSize = 20            # width of the signal box
        xIconOff = 10
        iconSize = 48

        count = max(len(inputs), len(outputs))
        height = max ((count)*ySignalSpace, 70)

        # calculate needed sizes of boxes to show text
        maxLeft = 0
        for i in inputs.keys():
            maxLeft = max(maxLeft, self.getTextWidth("("+inputs[i].name+")", 1))
            maxLeft = max(maxLeft, self.getTextWidth(unicode([unicode(a).split('.')[-1] for a in inputs[i].signalClass])))

        maxRight = 0
        for i in outputs.keys():
            maxRight = max(maxRight, self.getTextWidth("("+outputs[i].name+")", 1))
            maxRight = max(maxRight, self.getTextWidth(unicode(outputs[i].signalClass).split('.')[-1]))

        width = max(maxLeft, maxRight) + 70 # we add 70 to show icons beside signal names

        # show boxes
        brush = QBrush(QColor(60,150,255))
        self.outWidget = QGraphicsRectItem(xWidgetOff, yWidgetOffTop, width, height, None, self.dlg.canvas)
        self.outWidget.setBrush(brush)
        self.outWidget.setZValue(-100)

        self.inWidget = QGraphicsRectItem(xWidgetOff + width + xSpaceBetweenWidgets, yWidgetOffTop, width, height, None, self.dlg.canvas)
        self.inWidget.setBrush(brush)
        self.inWidget.setZValue(-100)
        
        canvasPicsDir  = os.path.join(redREnviron.directoryNames['canvasDir'], "icons")
        if os.path.exists(os.path.join(canvasPicsDir, "frame.png")):
            widgetBack = QPixmap(os.path.join(canvasPicsDir, "frame.png"))
        else:
            widgetBack = outWidget.imageFrame

        # if icons -> show them
        if outIcon:
            frame = QGraphicsPixmapItem(widgetBack, None, self.dlg.canvas)
            frame.setPos(xWidgetOff + xIconOff, yWidgetOffTop + height/2.0 - frame.pixmap().width()/2.0)
            self.outWidgetIcon = QGraphicsPixmapItem(outIcon.pixmap(iconSize, iconSize), None, self.dlg.canvas)
            self.outWidgetIcon.setPos(xWidgetOff + xIconOff, yWidgetOffTop + height/2.0 - self.outWidgetIcon.pixmap().width()/2.0)
        
        if inIcon:
            frame = QGraphicsPixmapItem(widgetBack, None, self.dlg.canvas)
            frame.setPos(xWidgetOff + xSpaceBetweenWidgets + 2*width - xIconOff - frame.pixmap().width(), yWidgetOffTop + height/2.0 - frame.pixmap().width()/2.0)
            self.inWidgetIcon = QGraphicsPixmapItem(inIcon.pixmap(iconSize, iconSize), None, self.dlg.canvas)
            self.inWidgetIcon.setPos(xWidgetOff + xSpaceBetweenWidgets + 2*width - xIconOff - self.inWidgetIcon.pixmap().width(), yWidgetOffTop + height/2.0 - self.inWidgetIcon.pixmap().width()/2.0)

        # show signal boxes and text labels
        #signalSpace = (count)*ySignalSpace
        signalSpace = height
        j = 0
        #self.outBoxesList = []
        for i in outputs.keys():
            y = yWidgetOffTop + ((j+1)*signalSpace)/float(len(outputs)+1)
            box = QGraphicsRectItem(xWidgetOff + width, y - ySignalSize/2.0, xSignalSize, ySignalSize, None, self.dlg.canvas)
            if outputs[i].value == None:
                box.setBrush(QBrush(QColor(255,0,0)))
            else:
                box.setBrush(QBrush(QColor(0,0,255)))
            box.setZValue(200)
            self.outBoxes.append((outputs[i].name, box, i))

            self.texts.append(MyCanvasText(self.dlg.canvas, outputs[i].name, xWidgetOff + width - 5, y - 7, Qt.AlignRight | Qt.AlignVCenter, bold =1, show=1))
            self.texts.append(MyCanvasText(self.dlg.canvas, unicode(outputs[i].signalClass).split('.')[-1], xWidgetOff + width - 5, y + 7, Qt.AlignRight | Qt.AlignVCenter, bold =0, show=1))
            j += 1
        j = 0
        for i in inputs.keys():
            y = yWidgetOffTop + ((j+1)*signalSpace)/float(len(inputs)+1)
            box = QGraphicsRectItem(xWidgetOff + width + xSpaceBetweenWidgets - xSignalSize, y - ySignalSize/2.0, xSignalSize, ySignalSize, None, self.dlg.canvas)
            box.setBrush(QBrush(QColor(0,0,255)))
            box.setZValue(200)
            self.inBoxes.append((inputs[i].name, box, i))

            self.texts.append(MyCanvasText(self.dlg.canvas, inputs[i].name, xWidgetOff + width + xSpaceBetweenWidgets + 5, y - 7, Qt.AlignLeft | Qt.AlignVCenter, bold =1, show=1))
            self.texts.append(MyCanvasText(self.dlg.canvas, unicode([unicode(a).split('.')[-1] for a in inputs[i].signalClass]), xWidgetOff + width + xSpaceBetweenWidgets + 5, y + 7, Qt.AlignLeft | Qt.AlignVCenter, bold =0, show=1))
            j += 1
        self.texts.append(MyCanvasText(self.dlg.canvas, outWidget.caption, xWidgetOff + width/2.0, yWidgetOffTop + height + 5, Qt.AlignHCenter | Qt.AlignTop, bold =1, show=1))
        self.texts.append(MyCanvasText(self.dlg.canvas, inWidget.caption, xWidgetOff + width* 1.5 + xSpaceBetweenWidgets, yWidgetOffTop + height + 5, Qt.AlignHCenter | Qt.AlignTop, bold =1, show=1))

        return (2*xWidgetOff + 2*width + xSpaceBetweenWidgets, yWidgetOffTop + height + yWidgetOffBottom)

    def getTextWidth(self, text, bold = 0):
        temp = QGraphicsSimpleTextItem(text, None, self.dlg.canvas)
        if bold:
            font = temp.font()
            font.setBold(1)
            temp.setFont(font)
        temp.hide()
        return temp.boundingRect().width()

    # ###################################################################
    # mouse button was pressed
    def mousePressEvent(self, ev):
        #print _(' SignalCanvasView mousePressEvent')
        self.bMouseDown = 1
        point = self.mapToScene(ev.pos())
        activeItem = self.scene().itemAt(QPointF(ev.pos()))
        if type(activeItem) == QGraphicsRectItem and activeItem not in [self.outWidget, self.inWidget]:
            self.tempLine = QGraphicsLineItem(None, self.dlg.canvas)
            self.tempLine.setLine(point.x(), point.y(), point.x(), point.y())
            self.tempLine.setPen(QPen(QColor(0,255,0), 1))
            self.tempLine.setZValue(-300)
            
        elif type(activeItem) == QGraphicsLineItem:
            for (line, outName, inName, outBox, inBox) in self.lines:
                if line == activeItem:
                    self.dlg.removeLink(outName, inName)
                    return

    # ###################################################################
    # mouse button was released #########################################
    def mouseMoveEvent(self, ev):
        if self.tempLine:
            curr = self.mapToScene(ev.pos())
            start = self.tempLine.line().p1()
            self.tempLine.setLine(start.x(), start.y(), curr.x(), curr.y())
            self.scene().update()

    # ###################################################################
    # mouse button was released #########################################
    def mouseReleaseEvent(self, ev):
        if self.tempLine:  ## a line is on
            activeItem = self.scene().itemAt(QPointF(ev.pos()))  # what is the item at the active position??
            if type(activeItem) == QGraphicsRectItem:
                activeItem2 = self.scene().itemAt(self.tempLine.line().p1()) ## active item 2 is the item at the beginning of the line.

                if self.tempLine.line().x2() < self.tempLine.line().x1():
                    print 'x > x2'
                    outBox = activeItem; inBox = activeItem2
                else:
                    print 'x2 > x'
                    outBox = activeItem2; inBox = activeItem
                outName = None; inName = None
                for (name, box, id) in self.outBoxes:
                    if box == outBox: 
                        print 'match name outBox %s' % id
                        outName = id
                        break
                for (name, box, id) in self.inBoxes:
                    if box == inBox: 
                        print 'match name inBox %s' % id
                        inName = id
                        break
                print outName, inName
                if outName != None and inName != None:
                    print _('adding link')
                    self.dlg.addLink(outName, inName)

            self.tempLine.hide()
            self.tempLine = None
            self.scene().update()


    def addLink(self, outName, inName):  ## makes the line that goes from one widget to the other on the canvas, outName and inName are the id's for the links
        #print _('Adding link in the canvas'), outName, inName
        outBox = None; inBox = None
        for (name, box, id) in self.outBoxes:
            if id == outName: outBox = box
        for (name, box, id) in self.inBoxes:
            if id == inName : inBox  = box
        if outBox == None or inBox == None:
            #print "error adding link. Data = ", outName, inName
            return
        line = QGraphicsLineItem(None, self.dlg.canvas)
        outRect = outBox.rect()
        inRect = inBox.rect()
        line.setLine(outRect.x() + outRect.width()-2, outRect.y() + outRect.height()/2.0, inRect.x()+2, inRect.y() + inRect.height()/2.0)
        line.setPen(QPen(QColor(0,255,0), 6))
        line.setZValue(100)
        self.scene().update()
        self.lines.append((line, outName, inName, outBox, inBox))


    def removeLink(self, outName, inName):  # removes the line on the canvas
        # res = QMessageBox.question(None, 'Red-R Connections', 'Are you sure you want to remove that link?\nThe downmtream widget will recieve No data.', QMessageBox.Yes, QMessageBox.No)
        
        # if res == QMessageBox.Yes:
            # self.dlg.
        for (line, outN, inN, outBox, inBox) in self.lines:
            if outN == outName and inN == inName:
                line.hide()
                self.lines.remove((line, outN, inN, outBox, inBox))
                self.scene().update()
                return

import re

class DocumentSearcherQListView(QListView):
    def __init__(self, parent=None, *args):
        QListView .__init__(self, parent, *args)
    def keyPressEvent(self, event):
        oldIdx = self.currentIndex();
        QListView.keyPressEvent(self,event);
        newIdx = self.currentIndex();
        if(oldIdx.row() != newIdx.row()):
            self.emit(SIGNAL("clicked (QModelIndex)"), newIdx)
    
    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            print _('invalid index')
        QListView.mousePressEvent(self, event)
        self.emit(SIGNAL("activated (QModelIndex)"), self.indexAt(event.pos()))
    

class DocumentSearcherHTMLDelegate(QItemDelegate):
    def __init__(self, parent=None, *args):
        QItemDelegate .__init__(self, parent, *args)
    def paint(self, painter, option, index):
        painter.save()
        #QStyledItemDelegate.paint(self,painter, option, index)
        # highlight selected items
        #if option.state & QStyle.State_Selected:  
        if index.row()%2: painter.fillRect(option.rect, QBrush(QColor(255, 255, 255)))
        else: painter.fillRect(option.rect, QBrush(QColor(255, 240, 240)))


        model = index.model()
        record = model.listdata[index.row()]

        doc = QTextDocument(self)
        enterText = re.sub(r'[\(\)\{\}=]{3,}', ', ', record[1])
        #print enterText
        doc.setHtml("%s" % enterText)
        doc.setTextWidth(option.rect.width()-40)
        ctx = QAbstractTextDocumentLayout.PaintContext()
       
        painter.translate(option.rect.topLeft());
        # try:
            # icon = QIcon(record[1].icon)
        # except:
            # icon = record[1]['icon']
        #self.drawDecoration(painter, option, QRect(5,5,32,32), icon.pixmap(QSize(32,32)))
        painter.translate(QPointF(40,4));
        painter.setClipRect(option.rect.translated(-option.rect.topLeft()))
        dl = doc.documentLayout()
        dl.draw(painter, ctx)
        # painter.resetTransform()
        # painter.translate(option.rect.topLeft());
        
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(100,75)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable 
        
class helpSearchDlg(QDialog):
    def __init__(self, parent, term = ''):
        QDialog.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.setWindowTitle(_('Local Documentation Search'))
        self.setWindowIcon(QIcon(os.path.join(redREnviron.directoryNames['canvasIconsDir'], 'help.png')))
        mainBox = redRQTCore.widgetBox(self)
        
        self.searchEdit = redRQTCore.lineEdit(mainBox, label = 'Search Terms', text = term, callback = self.searchDocumentation)
        self.helpList = DocumentSearcherQListView(mainBox)#, label = 'Help Search Matches', callback = self.openDocumentation)
        mainBox.layout().addWidget(self.helpList)
        
        de = DocumentSearcherHTMLDelegate(self)
        self.model = QStandardItemModel(self)
        
        self.helpList.setModel(self.model)
        self.helpList.setItemDelegate(de)
        self.helpList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.helpList.setSelectionBehavior(QAbstractItemView.SelectItems)
        
        QObject.connect(self.helpList, SIGNAL("activated ( QModelIndex )"), self.openDocumentation)
        
        self.searchDocumentation()
        
        self.show()
    
    def sizeHint(self):
        return QSize(700, 400)
        
    def searchDocumentation(self):
        if self.searchEdit.text() == '': return
        import docSearcher
        res = docSearcher.searchIndex(self.searchEdit.text(), redREnviron.directoryNames['redRDir'])
        self.model.clear()
        self.model.listdata = []
        for r in res:
            theText = unicode('%s <br>%s' % (r['title'],r['highlight']))
            self.model.listdata.append((r, theText))
            x = QStandardItem(theText)
            #x.info = (info, c)
            self.model.appendRow(x)
        
        #self.helpList.update([(r['path'], r['title']) for r in res])
        
    def openDocumentation(self):
        import webbrowser
        target = self.model.listdata[self.helpList.selectedIndexes()[0].row()][0]['path']
        print target
        webbrowser.open(target)
        self.accept()
if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    dlg = AboutDlg(None)
    dlg.show()
    app.exec_()

