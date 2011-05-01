from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import string
import time as ti
from datetime import tzinfo, timedelta, datetime, time
import traceback
import os.path, os
import redREnviron, redRLog, SQLiteSession
from libraries.base.qtWidgets.button import button as redRbutton
from libraries.base.qtWidgets.checkBox import checkBox as redRcheckBox
from libraries.base.qtWidgets.widgetBox import widgetBox as redRwidgetBox
from libraries.base.qtWidgets.dialog import dialog as redRdialog
from libraries.base.qtWidgets.widgetLabel import widgetLabel as redRwidgetLabel
from libraries.base.qtWidgets.comboBox import comboBox as redRComboBox
from libraries.base.qtWidgets.radioButtons import radioButtons as redRradiobuttons
from libraries.base.qtWidgets.tabWidget import tabWidget as redRTabWidget
from libraries.base.qtWidgets.textEdit import textEdit as redRTextEdit
from libraries.base.qtWidgets.lineEdit import lineEdit as redRLineEdit
import redRi18n
_ = redRi18n.Coreget_()

import httplib,urllib
import sys,pickle,os, re
def errorSubmitter(table, level, string, html):
    a = redRSubmitErrors()
    a.uploadException({'errorType':'%s.%s' % (redRLog.tables[table],redRLog.logLevelsByLevel[level]),'traceback':string})
    
class redRSubmitErrors():
    def __init__(self):
        pass
        
    def uploadYes(self):
        self.msg.done(1)

    def uploadNo(self):
        self.msg.done(0)
    def rememberResponse(self):
        if _('Remember my Response') in self.remember.getChecked():
            self.checked = True
            redREnviron.settings['askToUploadError'] = 0

        else:
            self.checked = False
        
    def uploadException(self,err):
        try:
            import httplib,urllib
            import sys,pickle,os, re
            #print redREnviron.settings['askToUploadError'], 'askToUploadError'
            #print redREnviron.settings['uploadError'], 'uploadError'
            if not redREnviron.settings['askToUploadError']:
                res = redREnviron.settings['uploadError']
            else:
                self.msg = redRdialog(parent=qApp.canvasDlg,title='Red-R Error')
                
                error = redRwidgetBox(self.msg,orientation='vertical')
                redRwidgetLabel(error, label='Do you wish to report the Error Log?')
                buttons = redRwidgetBox(error,orientation='horizontal')

                redRbutton(buttons, label = _('Yes'), callback = self.uploadYes)
                redRbutton(buttons, label = _('No'), callback = self.uploadNo)
                self.checked = False
                self.remember = redRcheckBox(error,label='response', displayLabel=None,
                buttons=[_('Remember my Response')],callback=self.rememberResponse)
                res = self.msg.exec_()
                redREnviron.settings['uploadError'] = res
            
            # redRLog.log(redRLog.REDRCORE, redRLog.ERROR, 'aaa')
            if res == 1:
                # print 'in res'
                err['version'] = redREnviron.version['SVNVERSION']
                err['type'] = redREnviron.version['TYPE']
                err['redRversion'] = redREnviron.version['REDRVERSION']
                #print err['traceback']
                
                
                ##err['output'] = self.allOutput
                if os.name == 'nt':
                    err['os'] = 'Windows'
                # else:
                    # err['os'] = 'Not Specified'
                if redREnviron.settings['canContact']:
                    err['email'] = redREnviron.settings['email']
                # else:
                    # err['email'] = 'None; no contact'
                #err['id'] = redREnviron.settings['id']
                # print err.keys()
                params = urllib.urlencode(err)
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                conn = httplib.HTTPConnection("red-r.org",80)
                conn.request("POST", "/errorReport.php", params,headers)
                # r1 = conn.getresponse()
                # data1 = r1.read()
                # print type(data1),data1
                # print r1.status, r1.reason
            else:
                return
        except: 
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
            pass
    
"""        
class redRSubmitErrors():
    def __init__(self, ):
        redRdialog.__init__(self,parent=qApp.canvasDlg,title='Red-R Error')
        error = redRwidgetBox(self,orientation='vertical')
        redRwidgetLabel(error, label='Do you wish to report the Error Log?')
        buttons = redRwidgetBox(error,orientation='horizontal')
        redRbutton(buttons, label = _('Yes'), callback = self.uploadYes)
        redRbutton(buttons, label = _('No'), callback = self.uploadNo)
        self.remember = redRcheckBox(error,label='remember response',displayLabel=False,
        buttons=[_('Remember my Response')],callback=self.rememberResponse)
        
        self.err = err
        if not redREnviron.settings['askToUploadError']:
            res = redREnviron.settings['uploadError']
        else:
            self.checked = False
            res = self.exec_()
            redREnviron.settings['uploadError'] = res



    def uploadYes(self):
        print 'adfasdfaaaaaaaaaaaaaaaaaa'
        self.uploadException(self.err)
        self.close()

    def uploadNo(self):
        self.close()
        
    def rememberResponse(self):
        if _('Remember my Response') in self.remember.getChecked():
            self.checked = True
            redREnviron.settings['askToUploadError'] = 0
        else:
            self.checked = False
        
    def uploadException(self,err):
        print 'adfadfasd'
        try:
            err['version'] = redREnviron.version['SVNVERSION']
            err['type'] = redREnviron.version['TYPE']
            err['redRversion'] = redREnviron.version['REDRVERSION']
            # print err['traceback']
            
            
            ##err['output'] = self.allOutput
            if os.name == 'nt':
                err['os'] = 'Windows'
            # else:
                # err['os'] = 'Not Specified'
            if redREnviron.settings['canContact']:
                err['email'] = redREnviron.settings['email']
            # else:
                # err['email'] = 'None; no contact'
            #err['id'] = redREnviron.settings['id']
            print err
            params = urllib.urlencode(err)
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            conn = httplib.HTTPConnection("localhost",80)
            conn.request("POST", "/errorReport.php", params,headers)
        except: 
            redRLog.log(redRLog.REDRCORE, redRLog.ERROR, redRLog.formatException())
"""