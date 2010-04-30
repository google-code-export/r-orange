import os, cPickle, numpy, pprint, re, sys
import redREnviron
import signals
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRGUI 
import signals 


class session():
    def __init__(self):
        self.redRGUIObjects = {}
        #collect the sent items
        
        #dont save these variables
        
        self.defaultGlobalSettingsList = ['windowState']
        self.dontSaveList.extend(self.defaultGlobalSettingsList)
        self.dontSaveList.extend(['dontSaveList','redRGUIObjects','defaultGlobalSettingsList'])

    def getSettings(self, alsoContexts = True):
        print 'moving to save'+str(self.captionTitle)
        import re
        settings = {}
        allAtts = self.__dict__
        # self.dontSaveList.extend(RSession().__dict__.keys())
        #self.dontSaveList.extend(OWWidget().__dict__.keys())
        # print 'all atts:', allAtts
        # print 'dontSaveList', self.dontSaveList
        # try:
        self.progressBarInit()
        i = 0
        for att in allAtts:
            if att in self.dontSaveList or re.search('^_', att):
                continue
            i += 1
            self.progressBarAdvance(i)
            print 'frist att: ' + att
            var = getattr(self, att)
            settings[att] = self.returnSettings(var)

        settings['_customSettings'] = self.saveCustomSettings()
        tempSentItems = self.processSentItems()
        settings['sentItems'] = {'sentItemsList':tempSentItems}
        self.progressBarFinished()
        return settings
    def saveCustomSettings(self):
        pass
    def isPickleable(self,d):
        import re
        #if isinstance(d,QObject):
        # print str(type(d))
        if re.search('PyQt4|OWGUIEx|OWToolbars',str(type(d))) or d.__class__.__name__ in redRGUI.qtWidgets:
            # print 'QT object NOT Pickleable'
            return False
        elif type(d) in [list, dict, tuple]:
            #ok = True
            if type(d) in [list, tuple]:
                for i in d:
                    if self.isPickleable(i) == False:
                        #ok = False
                        return False
                return True
            elif type(d) in [dict]:
                for k in d.keys():
                    if self.isPickleable(d[k]) == False:
                        #ok = False
                        return False
                return True
        elif type(d) in [type(None), str, int, float, bool, numpy.float64]:
            return True
        elif isinstance(d, signals.BaseRedRVariable):
            return True
        else: 
            print 'Type ' + str(d) + ' is not supported at the moment..'
            print 
            return False
        
            
    def returnSettings(self,var):
        settings = {}
        print 'var class', var.__class__.__name__
        if var.__class__.__name__ in redRGUI.qtWidgets:
            #print 'getting gui settings for:' + att + '\n\n'
            try:
                v = {}
                v = var.getSettings()
                if v == None:
                    v = var.getDefaultState()
                else:
                    v.update(var.getDefaultState())
            except: 
                v = var.getDefaultState()
                import traceback,sys
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        

            settings['redRGUIObject'] = {}
            if v: settings['redRGUIObject'] = v
        #elif isinstance(var, signals.BaseRedRVariable):
        elif var.__class__.__name__ in signals.RedRSignals:    
            settings['signalsObject'] = var.saveSettings()
            print 'Saving signalsObject ', settings['signalsObject']
        
        elif self.isPickleable(var):
            settings['pythonObject'] =  var
        #elif type(var) in [str, int, float, bool]:
        #   settings = var
        elif type(var) in [list]:
           settings['list'] = []
           for i in var:
               settings['list'].append(self.returnSettings(i))
        elif type(var) is dict:
           #print var
           settings['dict'] = {}
           for k,v in var.iteritems():
               settings['dict'][k] = self.returnSettings(v)
        else:
            settings = None
        return settings
    def processSentItems(self):
        sentItemsList = []
        for (sentDataName, sentDataObject) in self.sentItems:
            if sentDataObject == None: 
                sentItemsList.append((sentDataName, None))
            elif type(sentDataObject) == dict:
                sentItemsList.append((sentDataName, sentDataObject))
                print sentDataName, 'still set to a dict, change this!!!'
            else:
                sentItemsList.append((sentDataName, sentDataObject.saveSettings()))
        return sentItemsList
    def setSettings(self,settings):
        # print 'on set settings'
        self.redRGUIObjects = {}
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(settings)
        for k,v in settings.iteritems():
            if k in ['inputs', 'outputs']: continue
            if v == None:
                continue
            # elif k =='_customSettings':
                # self.__setattr__(k, v)
            elif 'pythonObject' in v.keys(): 
                # print k
                self.__setattr__(k, v['pythonObject'])
            elif 'signalsObject' in v.keys():
                print 'Setting signalsObject'
                varClass = self.setRvarClass(v['signalsObject'])
                self.__setattr__(k, varClass)
                #var = getattr(self, k)
                #self.setRvarClass(var, v['signalsObject'])
            else:
                self.redRGUIObjects[k] = v;
        
    def onLoadSavedSession(self):
        print 'in onLoadSavedSession'
        qApp.setOverrideCursor(Qt.WaitCursor)
        self.progressBarInit()
        i = 0
        for k,v in self.redRGUIObjects.iteritems():
            # pp = pprint.PrettyPrinter(indent=4)
            # print str(k)+ ' in onLoadSavedSession widget attribute'
            # pp.pprint(v)
            i += 1
            self.progressBarAdvance(i)
            if not hasattr(self,k):
                continue
            try:
                if 'redRGUIObject' in v.keys():
                    getattr(self, k).loadSettings(v['redRGUIObject'])
                    getattr(self, k).setDefaultState(v['redRGUIObject'])
                
                elif 'dict' in v.keys():
                    var = getattr(self, k)
                    # print 'dict',len(var),len(v['dict'])
                    if len(var) != len(v['dict']): continue
                    self.recursiveSetSetting(var,v['dict'])
                elif 'list' in v.keys():
                    var = getattr(self, k)
                    # print 'list',len(var),len(v['list'])
                    if len(var) != len(v['list']): continue
                    self.recursiveSetSetting(var,v['list'])
                elif 'sentItemsList' in v.keys():
                    self.setSentItemsList(v['sentItemsList'])
            except:
                print 'Error occured in loading data self.'+str(k)
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(v)
                import traceback,sys
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        
            
        self.progressBarAdvance(i+1)
        if '_customSettings' in self.redRGUIObjects.keys():
            self.loadCustomSettings(self.redRGUIObjects['_customSettings'])
        else:
            self.loadCustomSettings(self.redRGUIObjects)
        
        print 'onLoadSavedSession send', self.windowTitle()
        for (name, data) in self.sentItems:
            self.send(name, data)
        
        qApp.restoreOverrideCursor()
        self.progressBarFinished()
    def setSentItemsList(self, d):
        # set the sentItems in the widget
        for (sentItemName, sentItemDict) in d:
            print 'setting sent items', sentItemName, 'to', sentItemDict
            self.sentItems.append((sentItemName, self.setSentRvarClass(sentItemDict, sentItemName)))
    
    def setSentRvarClass(self, d, sentItemName):
        print 'setSentRvarClass', d
        className = d['class'].split('.')
        className = className[1]
        # print 'setting ', className
        try: # try to reload the output class from the signals
            if d['package'] != 'base':
                var = getattr(getattr(signals,d['package']), className)(data = d['data'])
            else:
                var = getattr(signals, className)(data = d['data'])
        except: # if it doesn't exist we need to set the class something so we look to the outputs. 
            try:
                var = None
                for (name, att) in self.outputs:
                    if name == sentItemName:
                        var = att(data = d['data'])
                if var == None: raise Exception
            except: # something is really wrong we need to set some kind of data so let's set it to the signals.RVariable
                print 'something is really wrong we need to set some kind of data so let\'s set it to the signals.RVariable'
                var = signals.RVariable(data = d['data'])
            
        
        for key in d.keys():
            if key in ['class','package']: continue
            # print 'setting ', key
            subvar = getattr(var, key) 
            subvar = d[key]
        return var
            
    def setRvarClass(self, d):
        className = d['class'].split('.')
        print className
        className = className[1]
        print 'setting ', className
        #try: # try to reload the output class from the signals
        if d['package'] != 'base':
            var = getattr(getattr(signals,d['package']), className)(data = d['data'])
        else:
            var = getattr(signals, className)(data = d['data'])
        # finally: # something is really wrong we need to set some kind of data so let's set it to the signals.RVariable
            # print 'Class name not found, setting to a variable'
            # var = signals.RVariable(data = d['data'])
        for key in d.keys():
            if key in ['class','package']: continue
            print 'setting ', key
            subvar = getattr(var, key) 
            subvar = d[key]
        return var
    def recursiveSetSetting(self,var,d):
        # print 'recursiveSetSetting'
        
        if type(var) in [list,tuple]:
            for k in xrange(len(d)):
                if type(d[k]) is dict and 'redRGUIObject' in d[k].keys():
                    var[k].loadSettings(d[k]['redRGUIObject'])
                    var[k].setDefaultState(d[k]['redRGUIObject'])
                else:
                    self.recursiveSetSetting(var[k],d[k])
        elif type(var) is dict:
            for k,v in d.iteritems():
                if type(v) is dict and 'redRGUIObject' in v.keys():
                    var[k].loadSettings(v['redRGUIObject'])
                    var[k].setDefaultState(v['redRGUIObject'])
                else:
                    self.recursiveSetSetting(var[k],d[k])
        
    def loadCustomSettings(self,settings=None):
        pass

    def saveSettingsStr(self):
        # print 'saveSettingsStr called'
        settings = self.getSettings()
        try:
            return cPickle.dumps(settings)
        except: 
            print "ERROR in Pickle", sys.exc_info()[0] 
            pass

    def loadSettings(self, file = None):
        
        file = self.getGlobalSettingsFile(file)
        settings = {}
        if file:
            try:
                file = open(file, "r")
                settings = cPickle.load(file)
            except:
                settings = None

        if hasattr(self, "_settingsFromSchema"):
            if settings: settings.update(self._settingsFromSchema)
            else:        settings = self._settingsFromSchema

        # can't close everything into one big try-except since this would mask all errors in the below code
        if settings:
            # if hasattr(self, "settingsList"):
            # pp = pprint.PrettyPrinter(indent=3)
            # pp.pprint(settings)
            self.setSettings(settings)

    
        
#############widget specific settings#####################

    def getGlobalSettingsFile(self, file=None):
        # print 'getSettingsFile in owbasewidget'
        if file==None:
            file = os.path.join(redREnviron.widgetSettingsDir, self._widgetInfo['fileName'] + ".ini")
        #print 'getSettingsFile', file
        return file

    
    # save global settings
    def saveGlobalSettings(self, file = None):
        print 'owrpy global save settings'
        settings = {}
        
        if hasattr(self, "globalSettingsList"):
            self.globalSettingsList.extend(self.defaultGlobalSettingsList)
        else:
            self.globalSettingsList =  self.defaultGlobalSettingsList
            
        for name in self.globalSettingsList:
            try:
                settings[name] = {}
                settings[name]['pythonObject'] =  getattr(self,name)
            except:
                print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
        if settings:
            file = self.getGlobalSettingsFile(file)
            file = open(file, "w")
            cPickle.dump(settings, file)

