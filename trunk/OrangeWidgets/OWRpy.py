#
# An Orange-Rpy class
# 
# Should include all the functionally need to connect Orange to R 
#

from OWWidget import *
from RSession import *
import redRGUI 
import inspect, os
import time
import numpy
import RvarClasses
import RAffyClasses
import threading, sys
import pprint
import cPickle
import re

pp = pprint.PrettyPrinter(indent=4)


class OWRpy(OWWidget,RSession):   
    
    def __init__(self,parent=None, signalManager=None, 
    title="R Widget", wantGUIDialog = 0, **args):
        
        OWWidget.__init__(self, parent=parent, signalManager=signalManager, title=title,wantGUIDialog=wantGUIDialog, **args)
        RSession.__init__(self)
        
        #The class variable is used to create the unique names in R
        
        
        self.redRGUIObjects = {}
        #collect the sent items
        self.sentItems = []
        
        #dont save these variables
        
        self.defaultGlobalSettingsList = ['windowState']
        self.dontSaveList.extend(self.defaultGlobalSettingsList)
        self.dontSaveList.extend(['dontSaveList','redRGUIObjects','defaultGlobalSettingsList'])
        
    def rSend(self, name, variable, updateSignalProcessingManager = 1):
        print 'send'
        # funciton for upclassing variables that are send as dictionaries
        for i in self.outputs:
            if i[0] == name: # this is the channel that you are sending from 
                if type(variable) == dict: # if we havent converted this already
                    if issubclass(i[1], RvarClasses.RDataFrame): 
                        newvariable = i[1](data = variable['data'], parent = variable['parent'], cm = variable['cm'])
                        newvariable['dictAttrs'] = variable
                    else:
                        newvariable = i[1](data = variable['data'], parent = variable['parent'])
                        newvariable['dictAttrs'] = variable
                    variable = newvariable
        try:
            self.send(name, variable)
            # if updateSignalProcessingManager:
                #try:
            self.removeInformation(id = 'dataNotSent')
            self.sentItems.append((name, variable))
            self.status.setText('Data sent.')
                #except: 
                #    print 'Failed to remove information', self.widgetState
        except:
            self.setError(id = 'dataNotSent', text = 'Failed to send data')
    
    def getSettings(self, alsoContexts = True):
        print 'moving to save'
        import re
        settings = {}
        allAtts = self.__dict__
        self.dontSaveList.extend(RSession().__dict__.keys())
        #self.dontSaveList.extend(OWWidget().__dict__.keys())
        # print 'all atts:', allAtts
        print 'dontSaveList', self.dontSaveList
        # try:
        self.progressBarInit()
        i = 0
        for att in allAtts:
            if att in self.dontSaveList:
                continue
            i += 1
            self.progressBarAdvance(i)
            print 'frist att: ' + att
            if re.search('^_', att):
                continue
            var = getattr(self, att)
            settings[att] = self.returnSettings(var)
        # except:
            # print 'Exception occured in saving settings'
            # print sys.exc_info()[0]
        settings['_customSettings'] = self.saveCustomSettings()
        
        #try:
        if self.inputs and len(self.inputs) != 0:
            ainputs = []
            for (a, b, c) in [input for input in self.inputs]:
                
                if issubclass(b, RvarClasses.RDataFrame):
                    bc = 'Data Frame'
                elif issubclass(b, RvarClasses.RVector):
                    bc = 'Vector'
                elif issubclass(b, RvarClasses.RList):
                    bc = 'List'
                else:
                    bc = 'Variable'
                ainputs.append((a, bc))
            settings['inputs'] = ainputs
        else: settings['inputs'] = None
        if self.outputs and len(self.outputs) != 0:
            aoutputs = []
            for (a,b) in [output for output in self.outputs]:
                print 'Output type', type(b)
                if issubclass(b, RvarClasses.RDataFrame):
                    bc = 'Data Frame'
                elif issubclass(b, RvarClasses.RVector):
                    bc = 'Vector'
                elif issubclass(b, RvarClasses.RList):
                    bc = 'List'
                else:
                    bc = 'Variable'
                aoutputs.append((a, bc))
            settings['outputs'] = aoutputs
        else: settings['outputs'] = None
        #except:
            #print 'Saving inputs and outputs failed.  This widget will not be reloaded by a dummyWidget!'
        #print str(settings) + ' (OWRpy.py)'
        #print 'My settings are ' + str(settings)
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
        else: 
            print 'This type is not supported at the moment, if you would like it to be and think that this is a mistake contact the developers so they can add it to the list.'
            print str(d)
            return False
        
            
    def returnSettings(self,var):
        settings = {}
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
                import traceback
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60        

            settings['redRGUIObject'] = {}
            if v: settings['redRGUIObject'] = v
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
    def setSettings(self,settings):
        # print 'on set settings'
        self.redRGUIObjects = {}
        for k,v in settings.iteritems():
            if k in ['inputs', 'outputs']: continue
            if v == None:
                continue
            # elif k =='_customSettings':
                # self.__setattr__(k, v)
            elif 'pythonObject' in v.keys(): 
                # print k
                self.__setattr__(k, v['pythonObject'])
            else:
                self.redRGUIObjects[k] = v;
        
    def onLoadSavedSession(self):
        # print 'in onLoadSavedSession'
        qApp.setOverrideCursor(Qt.WaitCursor)
        self.progressBarInit()
        i = 0
        for k,v in self.redRGUIObjects.iteritems():
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
            except:
                print 'Error occured in loading data self.'+str(k)
                
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
        
        for (name, data) in self.sentItems:
            self.send(name, data)
        
        qApp.restoreOverrideCursor()
        self.progressBarFinished()

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
            self.setSettings(settings)

    
        
#############widget specific settings#####################

    def getGlobalSettingsFile(self, file=None):
        # print 'getSettingsFile in owbasewidget'
        if file==None:
            file = os.path.join(self.widgetSettingsDir, self._widgetInfo['fileName'] + ".ini")
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

#############widget specific settings#####################

    def onDeleteWidget(self, suppress = 0):
        if suppress == 1: # instantiated in orngDoc.py, will fail if orngDoc has not initialized it.
            return

        for k in self.Rvariables:
            #print self.Rvariables[k]
            self.R('if(exists("' + self.Rvariables[k] + '")) { rm(' + self.Rvariables[k] + ') }')
        try:
            #if self.device != []: #  if this is true then this widget made an R device and we would like to shut it down
            for device in self.device.keys():
                dev = self.device[device]
                #key = device.keys()[0]
                self.R('dev.set('+str(dev)+')', 'setRData')
                self.R('dev.off() # shut down device for widget '+ str(OWRpy.uniqueWidgetNumber), 'setRData') 
                
        except: pass
        self.customWidgetDelete()
    
    def customWidgetDelete(self):
        pass #holder function for other widgets

    def reloadWidget(self):
        pass
    def sendRefresh(self):
        self.signalManager.refresh()
            
    def refresh(self):
        pass # function that listens for a refresh signal.  This function should be overloaded in widgets that need to listen.

        
###########################################
