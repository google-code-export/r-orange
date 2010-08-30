


class OutputHandler:
    def __init__(self, parent):                         ## set up the outputHandler, this will take care of sending signals to 
        self.outputSignals = {}
        self.connections = {}
        self.parent = parent # the parent that owns the OutputHandler
    def getAllOutputs(self):
        return self.outputSignals
    def addOutput(self, id, name, signalClass):
        self.outputSignals[id] = {'name':name, 'signalClass':signalClass, 'connections':{}, 'value':None, 'parent':self.parent, 'sid':id}   # set up an 'empty' signal
        
    def connectSignal(self, signal, id, enabled = 1, process = True):
        if id not in self.outputSignals.keys():
            raise Exception, 'ID %s does not exist in the outputs of this widget' % (id)
            
        self.outputSignals[id]['connections'][signal['id']] = {'signal':signal, 'enabled':enabled}
        # now send data through
        signal['parent'].inputs.addLink(signal['sid'], self.getSignal(id))
        if process:
            print 'processing signal'
            self._processSingle(self.outputSignals[id], self.outputSignals[id]['connections'][signal['id']])
        return True
    def outputIDs(self):
        return self.outputSignals.keys()
    def outputNames(self):
        out = {}
        for key, value in self.outputSignals.items():
            out[key] = value['name']
        return out
    def outputValues(self):
        out = {}
        for key, value in self.outputSignals.items():
            out[key] = value['value']
        return out
    def removeSignal(self, signal, id):
        ## send None through the signal to the handler before we disconnect it.
        if signal['id'] in self.outputSignals[id]['connections'].keys():                                 # check if the signal is there to begin with otherwise we don't do anything
            if self.outputSignals[id]['connections'][signal['id']]['signal']['multiple']:
                self.outputSignals[id]['connections'][signal['id']]['signal']['handler'](
                    #self.outputSignals[signalName]['value'],
                    None,
                    self.parent.widgetID
                    )
            else:
                self.outputSignals[id]['connections'][signal['id']]['signal']['handler'](
                    #self.outputSignals[signalName]['value']
                    None
                    )
            ## remove the signal from the outputSignals
            del self.outputSignals[id]['connections'][signal['id']]
            signal['parent'].inputs.removeLink(signal['sid'], self.getSignal(id))
    def setOutputData(self, signalName, value):
        self.outputSignals[signalName]['value'] = value
        
    def signalLinkExists(self, widget):
        ## move across the signals and determine if there is a link to the specified widget
        for id in self.outputSignals.keys():
            for con in self.outputSignals[id]['connections'].keys():
                if self.outputSignals[id]['connections'][con]['signal']['parent'] == widget:
                    return True
                    
        return False
        
    def getLinkPairs(self, widget):
        pairs = []
        for id in self.outputSignals.keys():
            for con in self.outputSignals[id]['connections'].keys():
                if self.outputSignals[id]['connections'][con]['signal']['parent'] == widget:
                    pairs.append((id, self.outputSignals[id]['connections'][con]['signal']['sid']))
        return pairs
    def getSignalLinks(self, widget):
        ## move across the signals and determine if there is a link to the specified widget
        links = []
        for id in self.outputSignals.keys():
            for con in self.outputSignals[id]['connections'].keys():
                if self.outputSignals[id]['connections'][con]['signal']['parent'] == widget:
                    links.append((id, self.outputSignals[id]['connections'][con]['signal']['sid']))
                    
        return links
    def getSignal(self, id):
        if id in self.outputSignals.keys():
            return self.outputSignals[id]
        else:
            return None
    def setSignalEnabled(self, inWidget, enabled):
        for (name, value) in self.outputSignals.items():
            for (conName, conValue) in value['connections'].items():
                if inWidget == conValue['signal']['parent']:
                    conValue['enabled'] = enabled
    def isSignalEnabled(self, inWidget):
        for (name, value) in self.outputSignals.items():
            for (conName, conValue) in value['connections'].items():
                if inWidget == conValue['signal']['parent'] and conValue['enabled']:
                    return True
        return False
    def _processSingle(self, signal, connection):
        print signal
        if not connection['enabled']: return 0
        handler = connection['signal']['handler']
        multiple = connection['signal']['multiple']
        if signal['value'] == None: # if there is no data then it doesn't matter what the signal class is, becase none will be sent anyway
            self._handleSignal(signal['value'], handler, multiple) 
        elif signal['signalClass'] in connection['signal']['signalClass']:
            self._handleSignal(signal['value'], handler, multiple)
        else:
            for sig in connection['signal']['signalClass']:
                if sig in signal['signalClass'].convertToList:
                    newVal = signal['value'].convertToClass(sig)
                    self._handleSignal(newVal, handler, multiple)
                    connection['signal']['value'] = newVal
                    break
                elif signal['signalClass'] in sig.convertFromList:
                    tempSignal = sig(data = '', checkVal = False)                       ## make a temp holder to handle the processing.
                    newVal = tempSignal.convertFromClass(signal['value'])
                    self._handleSignal(newVal, handler, multiple)
                    connection['signal']['value'] = newVal
                    break
                
    def processData(self, id):
        # collect the signal ID
        signal = self.getSignal(id)
        
        # collect the connections
        connections = signal['connections']
        
        ## handle conversions and send data.
        for cKey in connections.keys():
            self._processSingle(signal, connections[cKey])

                    
    def _handleSignal(self, value, handler, multiple):
        if multiple:
            handler(value, self.parent.widgetID)
        else:   
            handler(value)
    def hasOutputName(self, name):
        return name in self.outputSignals.keys()
    
    ########  Loading and Saving ##############
    
    def returnOutputs(self):
        ## move through the outputs and return a list of outputs and connections.  these connections should be reconnected on reloading of the widget, ideally we will only put atomics into this outputHandler
        data = {}
        for (key, value) in self.outputSignals.items():
            
            data[key] = {'name':value['name'], 'signalClass':str(value['signalClass']), 'connections':{}}
            if value['value']:
                data[key]['value'] = value['value'].saveSettings()
            else:
                data[key]['value'] = None
            for (vKey, vValue) in value['connections'].items():
                data[key]['connections'][vKey] = {'id':vValue['signal']['sid'], 'parentID':vValue['signal']['parent'].widgetID, 'enabled':vValue['enabled']} ## now we know the widgetId and the signalID (sid) used for connecting widgets in the future.
                
            
        return data
    def setOutputs(self, data):
        for (key, value) in data.items():
            if key not in self.outputSignals.keys():
                print 'Signal does not exist'
                continue
            ## find the signal from the widget and connect it
            for (vKey, vValue) in value['connections'].items():
                ### find the widget
                for widget in self.parent.signalManager.widgets():
                    if widget.widgetID == vValue['parentID']:
                        widget = widget
                        break
                        
                inputSignal = widget.inputs.getSignal(vValue['id'])
                self.connectSignal(inputSignal, key, vValue['enabled'], process = False)  # connect the signal but don't send data through it.
            
    
class InputHandler:
    def __init__(self, parent):
        self.inputs = {}
        self.links = {}
        self.parent = parent # the parent widget that owns the InputHandler
    def getAllInputs(self):
        return self.inputs
    def addInput(self, id, name, signalClass, handler, multiple = False):
        if type(signalClass) not in [list]:
            signalClass = [signalClass]
        self.inputs[id] = {
            'value': None,                                      ## should only be set by an outputHandler 
            'name':name,
            'signalClass':signalClass,
            'handler':handler,
            'multiple':multiple,
            'sid':id, 
            'id':str(id)+'_'+self.parent.widgetID, 
            'parent':self.parent}
    def signalIDs(self):
        return self.inputs.keys()

    def getSignal(self, id):
        return self.inputs[id]
    def matchConnections(self, outputHandler):
        ## determine if there are any valid matches between the signal handlers
        for outputKey in outputHandler.outputSignals.keys():
            for inputKey in self.inputs.keys():
                OSignalClass = outputHandler.outputSignals[outputKey]['signalClass']
                for ISignalClass in self.inputs[inputKey]['signalClass']:
                    if OSignalClass == 'All' or ISignalClass == 'All':
                        return True
                    elif OSignalClass == ISignalClass:
                        return True
                    elif 'convertToList' in dir(OSignalClass) and ISignalClass in OSignalClass.convertToList:
                        return True
                    elif 'convertFromList' in dir(ISignalClass) and OSignalClass in ISignalClass.convertFromList:
                        return True
        return False
        
    def getPossibleConnections(self, outputHandler):
        ## determine if there are any valid matches between the signal handlers
        connections = []
        for outputKey in outputHandler.outputSignals.keys():
            for inputKey in self.inputs.keys():
                OSignalClass = outputHandler.outputSignals[outputKey]['signalClass']
                for ISignalClass in self.inputs[inputKey]['signalClass']:
                    if OSignalClass == 'All' or ISignalClass == 'All':
                        connections.append((outputKey, inputKey))
                        break
                    elif OSignalClass == ISignalClass:
                        connections.append((outputKey, inputKey))
                        break
                    elif 'convertToList' in dir(OSignalClass) and ISignalClass in OSignalClass.convertToList:
                        connections.append((outputKey, inputKey))
                        break
                    elif 'convertFromList' in dir(ISignalClass) and OSignalClass in ISignalClass.convertFromList:
                        connections.append((outputKey, inputKey))
                        break
        return connections
    def doesSignalMatch(self, id, signalClass):
        if signalClass == 'All': return True
        elif 'All' in self.getSignal(id)['signalClass']: return True
        elif signalClass in self.getSignal(id)['signalClass']: return True
        for s in self.getSignal(id)['signalClass']:
            if s in signalClass.convertToList:
                return True
            else:
                if signalClass in s.convertFromList:
                    return True
                    
        return False
    def addLink(self, sid, signal):
        if sid not in self.links.keys():
            self.links[sid] = []
        if self.getSignal(sid)['multiple']:
            self.links[sid].append(signal)
        else:
            for link in self.links[sid]:
                link['parent'].removeSignal(self.getSignal(sid), link['sid'])
            self.links[sid].append(signal)
    def removeLink(self, sid, signal):
        if sid not in self.links.keys(): return
        self.links[sid].remove(signal)
    def getLinks(self, sid):
        if sid not in self.links.keys():
            self.links[sid] = []
        return self.links[sid]
    ######### Loading and Saving ##############
    def returnInputs(self):
        return None  ## no real reason to return any of this becasue the outputHandler does all the signal work
        