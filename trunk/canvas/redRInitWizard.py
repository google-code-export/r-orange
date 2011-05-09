## redR-IntroWizard.  a wizard that is shown on first load that guides the user through the setup of Red-R.  The user will be encouraged to register Red-R (e-mail address), set canvas options (error reporting, output level, showing the output on error), R options (R mirror)

import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRGUI
import RSession, redREnviron, redRSaveLoad
import redRi18n
_ = redRi18n.Coreget_()
class RedRInitWizard(QWizard):
    def __init__(self, parent = None):
        QWizard.__init__(self, parent)
        self.libs = {}
        #layout = [QWizard.BackButton, QWizard.NextButton, QWizard.FinishButton]
        #self.setButtonLayout(layout)
        
        self.connect(self,SIGNAL('currentIdChanged ( int )'),self.pageChanged)

        self.setWindowTitle(_('Red-R Setup'))
        self.settings = dict(redREnviron.settings)
        
        self.registerPage = QWizardPage()
        self.registerPage.setLayout(QVBoxLayout())
        self.registerPage.setTitle(_('Please Register Red-R'))
        self.registerPage.setSubTitle(_('Registration will help us track errors to make Red-R better.'))
        
        self.email = redRGUI.base.lineEdit(self.registerPage, label = _('Email Address (Optional):'), width = -1)
        hbox = redRGUI.base.widgetBox(self.registerPage);

        # self.allowContact = redRGUI.base.radioButtons(self.registerPage, label = _('Red-R can contact me to ask about errors:'), buttons = [_('Yes'), _('No')])
        # self.allowContact.setChecked(_('Yes'))
        
        # self.errorReportingPage = QWizardPage()
        # self.errorReportingPage.setLayout(QVBoxLayout())
        # self.errorReportingPage.setTitle(_('Error Reporting'))
        # self.errorReportingPage.setSubTitle(_('How would you like errors to be reported to Red-R.'))
        self.redRExceptionHandling = redRGUI.base.checkBox(self.registerPage, label='Error Handling', 
        buttons = [
        ('showErrorWindow',_('Show output window on error')), 
        ('submitError',_('Submit Error Report')), 
        ('askToSubmit',_('Always ask before submitting error report'))], 
        toolTips = [_('Check this if you want to see the output when an error happens.'), 
        _('Check this if you want to send errors to Red-R.\nWe will only show the errors to Red-R or package maintainers.'), 
        _('Check this if you want to be asked before a report is sent to Red-R.\nOtherwise a report will be sent automatically to Red-R.')])
        self.redRExceptionHandling.setChecked(['submitError','showErrorWindow'])
        
        
        self.RSetupPage = QWizardPage()
        self.RSetupPage.setLayout(QVBoxLayout())
        self.RSetupPage.setTitle(_('R Repository'))
        self.RSetupPage.setSubTitle(_('Please set the repository closest to you.  This will help you get R packages faster.'))
        self.rlibrariesBox = redRGUI.base.widgetBox(self.RSetupPage)
        self.libInfo = redRGUI.base.widgetLabel(self.rlibrariesBox, label=_('Repository URL: ')+ self.settings['CRANrepos'])
        

        # place a listBox in the widget and fill it with a list of mirrors
        #redRGUI.base.button(self.rlibrariesBox, _('Get Libraries'), callback = self.loadMirrors)
        self.libListBox = redRGUI.base.listBox(self.rlibrariesBox, label = _('Mirrors'),displayLabel=False,
        callback = self.setMirror)
        self.libMessageBox = redRGUI.base.widgetLabel(self.rlibrariesBox)
        
        self.RLibraryPage = QWizardPage()
        self.RLibraryPage.setLayout(QVBoxLayout())
        self.RLibraryPage.setTitle(_('Load R Libraries'))
        redRGUI.base.widgetLabel(self.RLibraryPage, 
'''Red-R needs to install these R libraries on this machine:
    'RSvgDevice', 'reshape', 'lattice', 'hexbin', 'ggplot2', 
    'graph', 'grid', 'limma', 'gregmisc', 'MASS', 'Matrix', 
    'RSQLite', 'splines'
    \n\nPlease click the Next Button''')
        
        self.runExamplePage = QWizardPage()
        self.runExamplePage.setLayout(QVBoxLayout())
        self.runExamplePage.setTitle(_('Finished'))
        #self.runExamplePage.setSubTitle(_('<a href="http://red-r.org"> Red-R</a>.<br>Thanks for setting up Red-R.\n\nIf you want to start an example schema to help you get started then check the "Start Example" box.'))
        a = redRGUI.base.widgetLabel(self.runExamplePage,_(
"""Thanks for setting up Red-R.<br>
<ul>
<li>Whats new in Red-R 1.85: <a href="http://red-r.org/downloads/changelog">Change Log</a></li>
<li>Take a tour with the Red-R 1.85 <a href="http://red-r.org/downloads/changelog">screencast</a></li>
<li><a href="http://red-r.org/documentation">Red-R Documentation</a></li>
<li>Additional functionality: <a href="http://red-r.org/redrpackages">Red-R Packages</a></li>
</ul>
"""))
        a.setOpenExternalLinks(True)
        a.setWordWrap(True)
        a.setFixedWidth(350)
        self.showExample = redRGUI.base.checkBox(self.runExamplePage,label=_('Show Example'),displayLabel=False,
        buttons = [('start',_('Start Example'))], setChecked=['start'])
        
        self.addPage(self.RLibraryPage)
        self.addPage(self.registerPage)
        # self.addPage(self.errorReportingPage)
        self.addPage(self.RSetupPage)
        
        self.addPage(self.runExamplePage)
        self.loadBaseLibs()
        
        
    def pageChanged(self,id):
        if id ==2:
            self.loadMirrors()
    def loadMirrors(self):
        self.libMessageBox.clear()
        if not redREnviron.checkInternetConnection():
            self.libMessageBox.setText(_('No Internet Connection, please try again'))
            return
        self.libs = RSession.Rcommand('getCRANmirrors()')
        self.libListBox.update(self.libs['Name'])
    def setMirror(self):
        if len(self.libs) == 0: return
        item = self.libListBox.currentRow()
        self.settings['CRANrepos'] = unicode(self.libs['URL'][item])
        RSession.Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + unicode(self.libs['URL'][item]) + '"; options(repos=r)})')
        #print self.settings['CRANrepos']
        self.libInfo.setText('Repository URL changed to: '+unicode(self.libs['URL'][item]))
    def loadBaseLibs(self):
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            RSession.updatePackages(repository = self.settings['CRANrepos'])
            RSession.install_libraries(['RSvgDevice', 'reshape', 'lattice', 'hexbin', 'ggplot2', 'graph', 'grid', 'limma', 'gregmisc', 'MASS', 'Matrix', 'RSQLite', 'splines'], repository = self.settings['CRANrepos'])
        finally:
            QApplication.restoreOverrideCursor()
def startSetupWizard():
    setupWizard = RedRInitWizard()
    if setupWizard.exec_() == QDialog.Accepted:
        redREnviron.settings['email'] = unicode(setupWizard.email.text())
        # redREnviron.settings['canContact'] = unicode(setupWizard.allowContact.getChecked()) == _('Yes')
        try:
            redREnviron.settings['CRANrepos'] = setupWizard.settings['CRANrepos']
        except:
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass
        redREnviron.settings['focusOnCatchException'] = 'showErrorWindow' in setupWizard.redRExceptionHandling.getCheckedIds()
        
        redREnviron.settings['uploadError'] = 'submitError' in setupWizard.redRExceptionHandling.getCheckedIds()
        redREnviron.settings['askToUploadError'] = 'askToSubmit' in setupWizard.redRExceptionHandling.getCheckedIds()
    
        if _('Start Example') in setupWizard.showExample.getChecked():
            redRSaveLoad.loadDocument(os.path.join(redREnviron.directoryNames['examplesDir'], 'firstSchema.rrs'))
        
    #print redREnviron.settings
    redREnviron.settings['firstLoad'] = False
    redREnviron.saveSettings()
