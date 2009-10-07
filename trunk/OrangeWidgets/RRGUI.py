#RRGUI class refference 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math
#import sys, traceback

YesNo = NoYes = ("No", "Yes")
groupBoxMargin = 7

import os.path

enter_icon = None

import OWGUI    #we inherit most of our classes either from OWGUI or from base QT

def widgetBox(widget, widgetattr, master, box=None, orientation='vertical', addSpace=False, sizePolicy = None, margin = -1, spacing = -1, flat = 0, addToLayout = 1):
    b = OWGUI.widgetBox(widget, box, orientation, addSpace, sizePolicy, margin, spacing, flat, addToLayout)
    if widgetattr != None:
        master.RGUIElements.append((widgetattr, 'widgetBox'))
    return b
    
# def indentedBox(widget, widgetattr, sep=20, orientation = True, addSpace=False):
    # r = widgetBox(widget, orientation = "horizontal")
    
def widgetLabel(widget, widgetattr, master, label=None, labelWidth=None, addToLayout = 1):
    lbl = OWGUI.widgetLabel(widget, label, labelWidth, addToLayout)
    master.RGUIElements.append((widgetattr, 'widgetLabel'))
    return lbl
    

def checkBox(widget, widgetattr, master, value, label, box=None, tooltip=None, callback=None, getwidget=None, id=None, disabled=0, labelWidth=None, disables = [], addToLayout = 1, debuggingEnabled = 1):
    wa = OWGUI.checkBox(widget, master, value, label, box, tooltip, callback, getwidget, id, disabled, labelWidth, disables, addToLayout, debuggingEnabled)
    master.RGUIElements.append((widgetattr, 'checkBox'))
    return wa
    
def lineEdit(widget, widgetattr, master, value,
             label=None, labelWidth=None, orientation='vertical', box=None, tooltip=None,
             callback=None, valueType = unicode, validator=None, controlWidth = None, callbackOnType = False, focusInCallback = None, **args):
             
    wa = OWGUI.lineEdit(widget, master, value, label, labelWidth, orientation, box, tooltip, callback, valueType, validator, controlWidth, callbackOnType, focusInCallback)
    master.RGUIElements.append((widgetattr, 'lineEdit'))
    return wa
    
def button(widget, widgetattr, master, label, callback = None, disabled=0, tooltip=None, debuggingEnabled = 1, width = None, height = None, toggleButton = False, value = "", addToLayout = 1):
    bu = OWGUI.button(widget, master, label, callback, disabled, tooltip, debuggingEnabled, width, height, toggleButton, value, addToLayout)
    if widgetattr != None:
        master.RGUIElements.append((widgetattr, 'button'))
    return bu
    
def listBox(widget, widgetattr, master, value = None, labels = None, box = None, tooltip = None, callback = None, selectionMode = QListWidget.SingleSelection, enableDragDrop = 0, dragDropCallback = None, dataValidityCallback = None, sizeHint = None, debuggingEnabled = 1):
    lb = OWGUI.listBox(widget, master, value, labels, box, tooltip, callback, selectionMode, enableDragDrop, dragDropCallback, dataValidityCallback, sizeHint, debuggingEnabled)
    master.RGUIElements.append((widgetattr, 'listBox'))
    return lb
    
def radioButtonsInBox(widget, widgetattr, master, value, btnLabels, box=None, tooltips=None, callback=None, debuggingEnabled = 1, addSpace = False, orientation = 'vertical', label = None):
    rbib = OWGUI.radioButtonsInBox(widget, master, value, btnLabels, box, tooltips, callback, debuggingEnabled, addSpace, orientation, label)
    master.RGUIElements.append((widgetattr, 'radioButtonsInBox'))
    return rbib
    
def comboBox(widget, widgetattr, master, value, box=None, label=None, labelWidth=None, orientation='vertical', items=None, tooltip=None, callback=None, sendSelectedValue = 0, valueType = unicode, control2attributeDict = {}, emptyString = None, editable = 0, searchAttr = False, indent = 0, addSpace = False, debuggingEnabled = 1):
    cb = OWGUI.comboBox(widget, master, value, box, label, labelWidth, orientation, items, tooltip, callback, sendSelectedValue, valueType, control2attributeDict, emptyString, editable, searchAttr, indent, addSpace, debuggingEnabled)
    master.RGUIElements.append((widgetattr, 'comboBox'))
    return cb
    
def comboBoxWithCaption(widget, widgetattr, master, value, label, box=None, items=None, tooltip=None, callback = None, sendSelectedValue=0, valueType = int, labelWidth = None, debuggingEnabled = 1):
    cb = OWGUI.comboBoxWithCaption(widget, master, value, label, box, items, tooltip, callback, sendSelectedValue, valueType, labelWidth, debuggingEnabled)
    master.RGUIElements.append((widgetattr, 'comboBoxWithCaption'))
    return cb
    
def tabWidget(widget, widgetattr, master):
    tw = OWGUI.tabWidget(widget)
    master.RGUIElements.append((widgetattr, 'tabWidget'))
    return tw
    
def createTabPage(tabWidget, widgetattr, master, name, widgetToAdd = None, canScroll = False):
    tp = OWGUI.createTabPage(tabWidget, name, widgetToAdd, canScroll)
    master.RGUIElements.append((widgetattr, 'createTabPage'))
    return tp
    
def table(widget, widgetattr, master, rows = 0, columns = 0, selectionMode = -1, addToLayout = 1):
    ta = OWGUI.table(widget, rows, columns, selectionMode, addToLayout)
    master.RGUIElements.append((widgetattr, 'table'))
    return ta
    