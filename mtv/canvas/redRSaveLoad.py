## <redRSaveLoad Module.  This module (not a class) will contain and provide functions for loading and saving of objects.  The module will make great use of the redRObjects module to access and instantiate objects.>
    # Copyright (C) 2010 Kyle R Covington

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
# def loadDocument(

# def save(

# def 

import os, sys, redRObjects, cPickle

def saveInstances(instances, widgets, doc, progressBar):
        settingsDict = {}
        requireRedRLibraries = {}
        progress = 0
        for k, widget in instances.items():
            temp = doc.createElement("widget")
            
            temp.setAttribute("widgetName", widget.widgetInfo.fileName)
            temp.setAttribute("packageName", widget.widgetInfo.package['Name'])
            temp.setAttribute("packageVersion", widget.widgetInfo.package['Version']['Number'])
            temp.setAttribute("widgetFileName", os.path.basename(widget.widgetInfo.fullName))
            temp.setAttribute('widgetID', widget.widgetID)
            print 'save in orngDoc ' + str(widget.captionTitle)
            progress += 1
            progressBar.setValue(progress)
            
            s = widget.getSettings()
            i = widget.getInputs()
            o = widget.getOutputs()
            
            #map(requiredRLibraries.__setitem__, s['requiredRLibraries']['pythonObject'], []) 
            #requiredRLibraries.extend()
            #del s['requiredRLibraries']
            settingsDict[widget.widgetID] = {}
            settingsDict[widget.widgetID]['settings'] = cPickle.dumps(s,2)
            settingsDict[widget.widgetID]['inputs'] = cPickle.dumps(i,2)
            settingsDict[widget.widgetID]['outputs'] = cPickle.dumps(o,2)
            
            if widget.widgetInfo.package['Name'] != 'base' and widget.widgetInfo.package['Name'] not in requireRedRLibraries.keys():
                requireRedRLibraries[widget.widgetInfo.package['Name']] = widget.widgetInfo.package
        
            widgets.appendChild(temp)
        return (widgets, settingsDict, requireRedRLibraries)