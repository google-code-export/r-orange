import os, cPickle, numpy, pprint, re, sys
import redREnviron
import signals
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redRGUI 
import signals 
from SQLiteSession import *


class widgetSession():
    def __init__(self,dontSaveList):
        #collect the sent items
        
        #dont save these variables
        self.requiredAtts = ['notes', 'ROutput']
        self.loaded = False
        self.dontSaveList = dontSaveList
        self.defaultGlobalSettingsList = ['windowState']
        self.dontSaveList.extend(self.defaultGlobalSettingsList)
        self.dontSaveList.extend(['outputs','inputs', 'dontSaveList','redRGUIObjects','defaultGlobalSettingsList','globalSettingsList', 'loaded'])
        self.sqlite = SQLiteHandler()


    def getSettings(self):  # collects settings for the save function, these will be included in the output file.  Called in orngDoc during save.
        print '|##| moving to save'+str(self.captionTitle)
        import re
        settings = {}
        if self.saveSettingsList:  ## if there is a saveSettingsList then we just append the required elements to it.
            allAtts = self.saveSettingsList + self.requiredAtts
        else:
            allAtts = self.__dict__
        self.progressBarInit()
        i = 0
        for att in allAtts:
            print att
            try:
                if att in self.dontSaveList or re.search('^_', att):
                    continue
                i += 1
                self.progressBarAdvance(i)
                #print 'frist att: ' + att
                var = getattr(self, att)
                settings[att] = self.returnSettings(var)
            except Exception as inst:
                print str(inst)
                print 'Exception occured in saving', att,
        settings['_customSettings'] = self.saveCustomSettings()
        tempSentItems = self.processSentItems()
        settings['sentItems'] = {'sentItemsList':tempSentItems}
        
        
        
        #settingsID = self.sqlite.saveObject(settings)
        self.progressBarFinished()
        return settings
    def saveCustomSettings(self): # dummy function that should be overwritten in child classes if they want the function
        pass
        
    def getInputs(self):
        if self.inputs and len(self.inputs) != 0:
            ainputs = []
            print self.inputs
            for input in self.inputs:
                ainputs.append((input[0], input[1]))
            return ainputs
        else: 
            return None
        
    def getOutputs(self):
        if self.outputs and len(self.outputs) != 0:
            aoutputs = []
            ## move across the outputs and get their type
            print self.outputs
            for output in self.outputs:
                aoutputs.append((output[0], output[1]))
            return aoutputs
        else: 
            return None

    def isPickleable(self,d):  # check to see if the object can be included in the pickle file
        import re
        #if isinstance(d,QObject):
        # print str(type(d))
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
            print '|#|  Saving signalsObject '#, settings['signalsObject']
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
        print '|##| in processSentItems %s' % str(self.linksOut)
        sentItemsList = []
        for sentDataName, sentDataObject in self.linksOut.items():
            s = {}
            for k,v in sentDataObject.items():
                if v == None: 
                    sentItemsList.append((sentDataName, None))
                else:
                    try:
                        s[k] = v.saveSettings()
                    ### problem with getting the settings, print and inform the developers.                 
                    except:
                        import orngOutput 
                        orngOutput.printException()
                        print '|###| problem getting data for '+str(sentDataObject)
                        
                sentItemsList.append((sentDataName,s))
                
        return sentItemsList
        
    def setSettings(self,settings):
        print 'on set settings'
        #settings = self.sqlite.setObject(settingsID)
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(settings)
        for k,v in settings.iteritems():
            try:
                #print k
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
                        for kk,vv in sentItemDict.items():
                            var = self.setSignalClass(vv)
                            self.send(sentItemName, var,id=kk)
    #############################################
                elif not hasattr(self,k):
                    continue
                elif 'redRGUIObject' in v.keys():
                    #print getattr(self, k)
                    try:
                        getattr(self, k).loadSettings(v['redRGUIObject'])
                        getattr(self, k).setDefaultState(v['redRGUIObject'])
                    except Exception as inst:
                        import orngOutput
                        print 'Exception occured during loading of settings.  These settings may not be the same as when the widget was closed.'
                        orngOutput.printException()
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
        print '|##| setSentRvarClass' #% str(d)
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
        file = os.path.join(redREnviron.directoryNames['widgetSettingsDir'], self._widgetInfo.fileName + ".ini")
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
        #print '%s' % str(settings)
        if settings:
            #settingsID = self.sqlite.saveObject(settings)
            file = self.getGlobalSettingsFile()
            file = open(file, "w")
            cPickle.dump(settings, file)
        
        print '|#| owrpy global save settings done'

