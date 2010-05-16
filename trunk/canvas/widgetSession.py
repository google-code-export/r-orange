import os, cPickle, numpy, pprint, re, sys
import redREnviron
import signals
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRGUI 
import signals 


class widgetSession():
    def __init__(self):
        self.redRGUIObjects = {}
        #collect the sent items
        
        #dont save these variables
        self.loaded = False
        self.defaultGlobalSettingsList = ['windowState']
        self.dontSaveList.extend(self.defaultGlobalSettingsList)
        self.dontSaveList.extend(['outputs','inputs', 'dontSaveList','redRGUIObjects','defaultGlobalSettingsList', 'loaded'])


    def getSettings(self):  # collects settings for the save function, these will be included in the output file.  Called in orngDoc during save.
        print '|##| moving to save'+str(self.captionTitle)
        import re
        settings = {}
        allAtts = self.__dict__
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
        
        if self.inputs and len(self.inputs) != 0:
            ainputs = []
            for (a, b, c) in [input for input in self.inputs]:
                ainputs.append((a, b))
            settings['inputs'] = ainputs
        else: settings['inputs'] = None
        if self.outputs and len(self.outputs) != 0:
            aoutputs = []
            ## move across the outputs and get their type
            for (a,b) in [output for output in self.outputs]:
                aoutputs.append((a, b))
            settings['outputs'] = aoutputs
        else: settings['outputs'] = None
        
        self.progressBarFinished()
        return settings
    def saveCustomSettings(self): # dummy function that should be overwritten in child classes if they want the function
        pass
    def isPickleable(self,d):  # check to see if the object can be included in the pickle file
        import re
        #if isinstance(d,QObject):
        print str(type(d))
        if re.search('PyQt4|OWGUIEx|OWToolbars',str(type(d))) or d.__class__.__name__ in redRGUI.qtWidgets:
            print 'QT object NOT Pickleable'
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
        elif type(d) in [type(None), str, int, float, bool, numpy.float64]:  # list of allowed save types, may epand in the future considerably
            return True
        elif isinstance(d, signals.BaseRedRVariable):
            return True
        else: 
            
            print '|##| Type ' + str(d) + ' is not supported at the moment..'  # notify the developer that the class that they are using is not saveable.
            print '|##|   '
            return False
        
            
    def returnSettings(self,var, checkIfPickleable=True): ## parses through objects returning if they can be saved or not and collecting their settings.
        settings = {}
        # print 'var class', var.__class__.__name__
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
            print '|#|  Saving signalsObject ', settings['signalsObject']
        elif not checkIfPickleable: 
            settings['pythonObject'] =  var
        elif self.isPickleable(var):
            settings['pythonObject'] =  var
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
        print '|##| in processSentItems %s' % str(self.sentItems)
        sentItemsList = []
        for (sentDataName, sentDataObject) in self.sentItems:
            if sentDataObject == None: 
                sentItemsList.append((sentDataName, None))
            elif type(sentDataObject) == dict:
                raise Exception, str(sentDataName)+' still set to a dict, change this!!!'
                
            else:
                try:
                    sentItemsList.append((sentDataName,sentDataObject.saveSettings()))
                except:
                    ### problem with getting the settings, print and inform the developers.
                    print '|###| problem getting data for '+str(sentDataObject)
                    raise Exception, 'Setting save exception'
        return sentItemsList
    def setSettings(self,settings):
        print 'on set settings'
        # self.redRGUIObjects = {}
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(settings)
        for k,v in settings.iteritems():
            try:
                print k
                if k in ['inputs', 'outputs']: continue
                if v == None:
                    continue
                elif 'pythonObject' in v.keys():
                    print '|#| Setting pythonObject %s to %s' % (k,str(v['pythonObject']))
                    self.__setattr__(k, v['pythonObject'])
                elif 'signalsObject' in v.keys():
                    print '|#| Setting signalsObject'
                    varClass = self.setSignalClass(v['signalsObject'])
                    self.__setattr__(k, varClass)
                elif 'sentItemsList' in v.keys():
                    #self.setSentItemsList(v['sentItemsList'])        
                    for (sentItemName, sentItemDict) in v['sentItemsList']:
                        print '|#| setting sent items %s to %s' % (sentItemName, str(sentItemDict))
                        var = self.setSignalClass(sentItemDict)
                        self.send(sentItemName, var)
    #############################################
                elif not hasattr(self,k):
                    continue
                elif 'redRGUIObject' in v.keys():
                    print getattr(self, k)
                    getattr(self, k).loadSettings(v['redRGUIObject'])
                    getattr(self, k).setDefaultState(v['redRGUIObject'])
                # elif template: continue                                         ### continue the cycling if this is a template, we don't need to set any of the settings since the schema doesn't have any special settings in it.  Only the widget gui settings are important as they may represent settings that are specific to the template.
                elif 'dict' in v.keys():
                    var = getattr(self, k)
                    print 'dict',len(var),len(v['dict'])
                    if len(var) != len(v['dict']): continue
                    self.recursiveSetSetting(var,v['dict'])
                elif 'list' in v.keys():
                    var = getattr(self, k)
                    # print 'list',len(var),len(v['list'])
                    if len(var) != len(v['list']): continue
                    self.recursiveSetSetting(var,v['list'])
            except Exception as inst:
                print inst
                print 'Exception occured during loading in the setting of an attribute.  This will not halt loading but the widget maker shoudl be made aware of this.'
#############################################
        
        ## commented out because already called in loadSettings
        if '_customSettings' in settings.keys():
            self.loadCustomSettings(settings['_customSettings'])
        else:
            self.loadCustomSettings(settings)
        
    def setSignalClass(self, d):
        print '|##| setSentRvarClass %s' % str(d)
        className = d['class'].split('.')[1]
        
        # print 'setting ', className
        try: # try to reload the output class from the signals
            if d['package'] != 'base':
                var = getattr(getattr(signals,d['package']), className)(data = d['data']) 
            else:
                var = getattr(signals, className)(data = d['data'])
            var.loadSettings(d)
        except Exception as inst: # if it doesn't exist we need to set the class something so we look to the outputs. 
            print '############################################'
            print inst
            print '############################################'
            try:
                var = None
                for (name, att) in self.outputs:
                    if name == sentItemName:
                        var = att(data = None, checkVal = False)
                        
                if var == None: raise Exception
                var.loadSettings(d['data'])
            except: # something is really wrong we need to set some kind of data so let's set it to the signals.RVariable
                print 'something is really wrong we need to set some kind of data so let\'s set it to the signals.RVariable'
                try:
                    var = signals.BaseRedRVariable(data = d['data']['data'], checkVal = False)
                except: ## fatal exception, there is no data in the data slot (the signal must not have data) we can't do anything so we except...
                    print 'Fatal exception in loading.  Can\'t assign the signal value'
                    var = None
        
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

#############widget specific settings#####################
        ##########set global settings#############
    def loadGlobalSettings(self):
        file = self.getGlobalSettingsFile()
        try:
            file = open(file, "r")
            settings = cPickle.load(file)
            self.setSettings(settings)
        except:
            pass
        
    
    def getGlobalSettingsFile(self):
        # print 'getSettingsFile in owbasewidget'
        file = os.path.join(redREnviron.widgetSettingsDir, self._widgetInfo['fileName'] + ".ini")
        #print 'getSettingsFile', file
        return file

    
    # save global settings
    def saveGlobalSettings(self):
        print '|#| owrpy global save settings'
        settings = {}
        
        if hasattr(self, "globalSettingsList"):
            self.globalSettingsList.extend(self.defaultGlobalSettingsList)
        else:
            self.globalSettingsList =  self.defaultGlobalSettingsList
            
        for name in self.globalSettingsList:
            try:
                settings[name] = self.returnSettings(getattr(self,name),checkIfPickleable=False)
            except:
                print "Attribute %s not found in %s widget. Remove it from the settings list." % (name, self.captionTitle)
        print '%s' % str(settings)
        if settings:
            file = self.getGlobalSettingsFile()
            file = open(file, "w")
            cPickle.dump(settings, file)
        
        print '|#| owrpy global save settings done'

#############DEPRECIATED######################
#############DEPRECIATED######################
    def loadSettings(self, sessionSettings=None):
        print '|#| in loadSettings '# + str(sessionSettings)
        if sessionSettings:
            self.setSettings(sessionSettings)
  
    def onLoadSavedSession(self, force = False, template = False):
        if self.loaded and not force: return  # prevents a loaded widget from being reloaded this can be overwriten using a call to force if the loader wishes.
        print '|##| in onLoadSavedSession'
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
                elif template: continue                                         ### continue the cycling if this is a template, we don't need to set any of the settings since the schema doesn't have any special settings in it.  Only the widget gui settings are important as they may represent settings that are specific to the template.
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
        
        print '|##| onLoadSavedSession send %s' % self.windowTitle()
        for (name, data) in self.sentItems:
            self.send(name, data)
        
        qApp.restoreOverrideCursor()
        self.progressBarFinished()
        self.loaded = True
    def setSentItemsList(self, d):
        # set the sentItems in the widget
        for (sentItemName, sentItemDict) in d:
            print '|##| setting sent items %s to %s' % (sentItemName, str(sentItemDict))
            self.sentItems.append((sentItemName, self.setSentRvarClass(sentItemDict, sentItemName))) # append a list of sent items to the sent items list, this is the place that we need to place the Red-R data container class into using setSentRvarClass.
    
    def setRvarClass(self, d):
        className = d['class'].split('.')
        #print '|##|', className
        className = className[1]
        print '|##| setting %s' % className
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
            print '|##| setting %s' % key
            subvar = getattr(var, key) 
            subvar = d[key]
        return var

                
    def saveSettingsStr(self): # called from outside of this class, used by orngDoc to collect the settings
        # print 'saveSettingsStr called'
        settings = self.getSettings()
        try:
            return cPickle.dumps(settings)
        except: 
            print "ERROR in Pickle", sys.exc_info()[0] 
            pass
