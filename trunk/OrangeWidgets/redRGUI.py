from PyQt4.QtCore import *
from PyQt4.QtGui import *
import math, glob
from RSession import RSession
import orngEnviron
from numpy import *
#import sys, traceback

YesNo = NoYes = ("No", "Yes")
groupBoxMargin = 7

import os.path

        
enter_icon = None
class widgetState:
    def getState(self):
        r = {'enabled': self.isEnabled(),'hidden': self.isHidden()}
        return r
    def setState(self,data):
        self.setEnabled(data['enabled'])
        self.setHidden(data['hidden'])

def forname(modname, classname):
    ''' Returns a class of "classname" from module "modname". '''
    module = __import__(modname)
    classobj = getattr(module, classname)
    return classobj

qtWidgets = []
current_module = __import__(__name__)


for filename in glob.iglob(os.path.join(orngEnviron.directoryNames['widgetDir'] + '/qtWidgets', "*.py")):
    if os.path.isdir(filename) or os.path.islink(filename):
        continue
    
    
    guiClass = os.path.basename(filename).split('.')[0]
    qtWidgets.append(guiClass)
    setattr(current_module, guiClass,forname(guiClass,guiClass))

    
#--------------------------------------------------------------------------------


def getdeepattr(obj, attr, **argkw):
    if type(obj) == dict:
        return obj.get(attr)
    try:
        return reduce(lambda o, n: getattr(o, n),  attr.split("."), obj)
    except:
# I (JD) commented this out. This is ugly and dangerous.
# If any widget wants this behavour, it should redefine its __getattr__ to return defaults. 
#        if argkw.has_key("default"):
#            return argkw["default"]
#        else:
            raise AttributeError, "'%s' has no attribute '%s'" % (obj, attr)


def getEnterIcon():
    global enter_icon
    if not enter_icon:
        enter_icon = QIcon(os.path.dirname(__file__) + "/icons/Dlg_enter.png")
    return enter_icon


# constructs a box (frame) if not none, and returns the right master widget
def indentedBox(widget, sep=20, orientation = True, addSpace=False):
    r = widgetBox(widget, orientation = "horizontal")
    separator(r, sep, 0)

    if isinstance(addSpace, int):
        separator(widget, 0, addSpace)
    elif addSpace:
        separator(widget)

    return widgetBox(r, orientation = orientation)

# def widgetLabel(widget, label=None, labelWidth=None, addToLayout = 1):
    # if label is not None:
        # lbl = QLabel(label, widget)
        # if labelWidth:
            # lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
        # if widget.layout() and addToLayout: widget.layout().addWidget(lbl)
    # else:
        # lbl = None

    # return lbl


import re
__re_frmt = re.compile(r"(^|[^%])%\((?P<value>[a-zA-Z]\w*)\)")

class SpinBoxWFocusOut(QSpinBox):
    def __init__(self, min, max, step, bi):
        QSpinBox.__init__(self, bi)
        self.setRange(min, max)
        self.setSingleStep(step)
        self.inSetValue = False
        self.enterButton = None

    def onChange(self, value):
        if not self.inSetValue:
            self.placeHolder.hide()
            self.enterButton.show()

    def onEnter(self):
        if self.enterButton.isVisible():
            self.enterButton.hide()
            self.placeHolder.show()
            if self.cback:
                self.cback(int(str(self.text())))
            if self.cfunc:
                self.cfunc()

    # doesn't work: it's probably LineEdit's focusOut that we should (and can't) catch
    def focusOutEvent(self, *e):
        QSpinBox.focusOutEvent(self, *e)
        if self.enterButton and self.enterButton.isVisible():
            self.onEnter()

    def setValue(self, value):
        self.inSetValue = True
        QSpinBox.setValue(self, value)
        self.inSetValue = False


def checkWithSpin(widget, master, label, min, max, checked, value, posttext = None, step = 1, tooltip=None,
                  checkCallback=None, spinCallback=None, getwidget=None,
                  labelWidth=None, debuggingEnabled = 1, controlWidth=55,
                  callbackOnReturn = False):
    return spin(widget, master, value, min, max, step, None, label, labelWidth, 0, tooltip,
                spinCallback, debuggingEnabled, controlWidth, callbackOnReturn, checked, checkCallback, posttext)



def spin(widget, master, value, min, max, step=1,
         box=None, label=None, labelWidth=None, orientation=None, tooltip=None,
         callback=None, debuggingEnabled = 1, controlWidth = None, callbackOnReturn = False,
         checked = "", checkCallback = None, posttext = None):
    if box or label and not checked:
        b = widgetBox(widget, box, orientation)
        hasHBox = orientation == 'horizontal' or not orientation
    else:
        b = widget
        hasHBox = False

    if not hasHBox and (checked or callback and callbackOnReturn or posttext):
        bi = widgetBox(b, "", 0)
    else:
        bi = b

    if checked:
        wb = checkBox(bi, master, checked, label, labelWidth = labelWidth, callback=checkCallback, debuggingEnabled = debuggingEnabled)
    elif label:
        widgetLabel(b, label, labelWidth)


    wa = bi.control = SpinBoxWFocusOut(min, max, step, bi)
    if bi.layout(): bi.layout().addWidget(wa)
    # must be defined because of the setText below
    if controlWidth:
        wa.setFixedWidth(controlWidth)
    if tooltip:
        wa.setToolTip(tooltip)
    if value:
        wa.setValue(getdeepattr(master, value))

    cfront, wa.cback, wa.cfunc = connectControl(wa, master, value, callback, not (callback and callbackOnReturn) and "valueChanged(int)", CallFrontSpin(wa))

    if checked:
        wb.disables = [wa]
        wb.makeConsistent()

    if callback and callbackOnReturn:
        wa.enterButton, wa.placeHolder = enterButton(bi, wa.sizeHint().height())
        QObject.connect(wa, SIGNAL("valueChanged(const QString &)"), wa.onChange)
        QObject.connect(wa, SIGNAL("editingFinished()"), wa.onEnter)
        QObject.connect(wa.enterButton, SIGNAL("clicked()"), wa.onEnter)
        if hasattr(wa, "upButton"):
            QObject.connect(wa.upButton(), SIGNAL("clicked()"), lambda c=wa.editor(): c.setFocus())
            QObject.connect(wa.downButton(), SIGNAL("clicked()"), lambda c=wa.editor(): c.setFocus())

    if posttext:
        widgetLabel(bi, posttext)

    if debuggingEnabled and hasattr(master, "_guiElements"):
        master._guiElements = getattr(master, "_guiElements", []) + [("spin", wa, value, min, max, step, callback)]

    if checked:
        return wb, wa
    else:
        return b


class DoubleSpinBoxWFocusOut(QDoubleSpinBox):
    def __init__(self, min, max, step, bi):
        QDoubleSpinBox.__init__(self, bi)
        self.setDecimals(math.ceil(-math.log10(step)))
        self.setRange(min, max)
        self.setSingleStep(step)
        self.inSetValue = False
        self.enterButton = None

    def onChange(self, value):
        if not self.inSetValue:
            self.placeHolder.hide()
            self.enterButton.show()

    def onEnter(self):
        if self.enterButton.isVisible():
            self.enterButton.hide()
            self.placeHolder.show()
            if self.cback:
                self.cback(float(str(self.text()).replace(",", ".")))
            if self.cfunc:
                self.cfunc()

    # doesn't work: it's probably LineEdit's focusOut that we should (and can't) catch
    def focusOutEvent(self, *e):
        QDoubleSpinBox.focusOutEvent(self, *e)
        if self.enterButton and self.enterButton.isVisible():
            self.onEnter()

    def setValue(self, value):
        self.inSetValue = True
        QDoubleSpinBox.setValue(self, value)
        self.inSetValue = False
        
def doubleSpin(widget, master, value, min, max, step=1,
         box=None, label=None, labelWidth=None, orientation=None, tooltip=None,
         callback=None, debuggingEnabled = 1, controlWidth = None, callbackOnReturn = False,
         checked = "", checkCallback = None, posttext = None): #widget, master, value, min, max, step=1, box=None, label=None, labelWidth=None, orientation=None, tooltip=None, callback=None, controlWidth=None):
    if box or label and not checked:
        b = widgetBox(widget, box, orientation)
        hasHBox = orientation == 'horizontal' or not orientation
    else:
        b = widget
        hasHBox = False

    if not hasHBox and (checked or callback and callbackOnReturn or posttext):
        bi = widgetBox(b, "", 0)
    else:
        bi = b

    if checked:
        wb = checkBox(bi, master, checked, label, labelWidth = labelWidth, callback=checkCallback, debuggingEnabled = debuggingEnabled)
    elif label:
        widgetLabel(b, label, labelWidth)


    wa = bi.control = DoubleSpinBoxWFocusOut(min, max, step, bi)
    if bi.layout(): bi.layout().addWidget(wa)
    # must be defined because of the setText below
    if controlWidth:
        wa.setFixedWidth(controlWidth)
    if tooltip:
        wa.setToolTip(tooltip)
    if value:
        wa.setValue(getdeepattr(master, value))

    cfront, wa.cback, wa.cfunc = connectControl(wa, master, value, callback, not (callback and callbackOnReturn) and "valueChanged(double)", CallFrontDoubleSpin(wa))

    if checked:
        wb.disables = [wa]
        wb.makeConsistent()

    if callback and callbackOnReturn:
        wa.enterButton, wa.placeHolder = enterButton(bi, wa.sizeHint().height())
        QObject.connect(wa, SIGNAL("valueChanged(const QString &)"), wa.onChange)
        QObject.connect(wa, SIGNAL("editingFinished()"), wa.onEnter)
        QObject.connect(wa.enterButton, SIGNAL("clicked()"), wa.onEnter)
        if hasattr(wa, "upButton"):
            QObject.connect(wa.upButton(), SIGNAL("clicked()"), lambda c=wa.editor(): c.setFocus())
            QObject.connect(wa.downButton(), SIGNAL("clicked()"), lambda c=wa.editor(): c.setFocus())

    if posttext:
        widgetLabel(bi, posttext)

##    if debuggingEnabled and hasattr(master, "_guiElements"):
##        master._guiElements = getattr(master, "_guiElements", []) + [("spin", wa, value, min, max, step, callback)]

    if checked:
        return wb, wa
    else:
        return b



def enterButton(parent, height, placeholder = True):
    button = QPushButton(parent)
    button.setFixedSize(height, height)
    button.setIcon(getEnterIcon())
    if parent.layout(): parent.layout().addWidget(button)
    if not placeholder:
        return button

    button.hide()
    holder = QWidget(parent)
    holder.setFixedSize(height, height)
    return button, holder


class LineEditWFocusOut(QLineEdit):
    def __init__(self, parent, master, callback, focusInCallback=None):
        QLineEdit.__init__(self, parent)
        self.callback = callback
        self.focusInCallback = focusInCallback
        self.enterButton, self.placeHolder = enterButton(parent, self.sizeHint().height())
        QObject.connect(self.enterButton, SIGNAL("clicked()"), self.returnPressed)
        QObject.connect(self, SIGNAL("textChanged(const QString &)"), self.markChanged)
        QObject.connect(self, SIGNAL("returnPressed()"), self.returnPressed)

    def markChanged(self, *e):
        self.placeHolder.hide()
        self.enterButton.show()

    def markUnchanged(self, *e):
        self.enterButton.hide()
        self.placeHolder.show()

    def returnPressed(self):
        if self.enterButton.isVisible():
            self.markUnchanged()
            if hasattr(self, "cback") and self.cback:
                self.cback(self.text())
            if self.callback:
                self.callback()

    def setText(self, t):
        QLineEdit.setText(self, t)
        if self.enterButton:
            self.markUnchanged()

    def focusOutEvent(self, *e):
        QLineEdit.focusOutEvent(self, *e)
        self.returnPressed()

    def focusInEvent(self, *e):
        if self.focusInCallback:
            self.focusInCallback()
        return QLineEdit.focusInEvent(self, *e)



def button(widget,  label, callback = None, disabled=0, tooltip=None, width = None, height = None, toggleButton = False, addToLayout = 1):
    btn = QPushButton(label, widget)
    if addToLayout and widget.layout():
        widget.layout().addWidget(btn)
    
    if width:
        btn.setFixedWidth(width)
    else:
        btn.setFixedWidth(len(label)*7+5)
    if height:
        btn.setFixedHeight(height)
    btn.setDisabled(disabled)
    
    if tooltip:
        btn.setToolTip(tooltip)
        
    if toggleButton:
        btn.setCheckable(True)
        
    if callback:
        QObject.connect(btn, SIGNAL("clicked()"), callback)
        
    return btn

def toolButton(widget, master, callback = None, width = None, height = None, tooltip = None, addToLayout = 1, debuggingEnabled = 1):
    btn = QToolButton(widget)
    if addToLayout and widget.layout(): widget.layout().addWidget(btn)
    if width != None: btn.setFixedWidth(width)
    if height!= None: btn.setFixedHeight(height)
    if tooltip != None: btn.setToolTip(tooltip)
    if callback:
        QObject.connect(btn, SIGNAL("clicked()"), callback)
    if debuggingEnabled and hasattr(master, "_guiElements"):
        master._guiElements = getattr(master, "_guiElements", []) + [("button", btn, callback)]
    return btn


def separator(widget, width=8, height=8):
    sep = QWidget(widget)
    if widget.layout(): widget.layout().addWidget(sep)
    sep.setFixedSize(width, height)
    return sep

def rubber(widget):
    widget.layout().addStretch(100)

def createAttributePixmap(char, color = Qt.black):
    pixmap = QPixmap(13,13)
    painter = QPainter()
    painter.begin(pixmap)
    painter.setPen( color );
    painter.setBrush( color );
    painter.drawRect( 0, 0, 13, 13 );
    painter.setPen( QColor(Qt.white))
    painter.drawText(3, 11, char)
    painter.end()
    return QIcon(pixmap)


attributeIconDict = None

def getAttributeIcons():
    import orange
    global attributeIconDict
    if not attributeIconDict:
        attributeIconDict = {orange.VarTypes.Continuous: createAttributePixmap("C", QColor(202,0,32)),
                     orange.VarTypes.Discrete: createAttributePixmap("D", QColor(26,150,65)),
                     orange.VarTypes.String: createAttributePixmap("S", Qt.black),
                     -1: createAttributePixmap("?", QColor(128, 128, 128))}
    return attributeIconDict


# btnLabels is a list of either char strings or pixmaps
def radioButtonsInBox(widget, master, value, btnLabels, box=None, tooltips=None, callback=None, debuggingEnabled = 1, addSpace = False, orientation = 'vertical', label = None):
    if box:
        bg = widgetBox(widget, box, orientation)
    else:
        bg = widget

    bg.group = QButtonGroup(bg)

    if addSpace:
        separator(widget)

    if not label is None:
        widgetLabel(bg, label)

    bg.buttons = []
    bg.ogValue = value
    for i in range(len(btnLabels)):
        appendRadioButton(bg, master, value, btnLabels[i], tooltips and tooltips[i], callback = callback)

    connectControl(bg.group, master, value, callback, "buttonClicked (int)", CallFrontRadioButtons(bg), CallBackRadioButton(bg, master))

    if debuggingEnabled and hasattr(master, "_guiElements"):
        master._guiElements = getattr(master, "_guiElements", []) + [("radioButtonsInBox", bg, value, callback)]
    return bg


def appendRadioButton(bg, master, value, label, tooltip = None, insertInto = None, callback = None):
    dest = insertInto or bg

    if not hasattr(bg, "buttons"):
        bg.buttons = []
    i = len(bg.buttons)

    if type(label) in (str, unicode):
        w = QRadioButton(label)
    else:
        w = QRadioButton(unicode(i))
        w.setIcon(QIcon(label))
    #w.ogValue = value
    if dest.layout(): dest.layout().addWidget(w)
    if not hasattr(bg, "group"):
        bg.group = QButtonGroup(bg)
    bg.group.addButton(w)

    w.setChecked(getdeepattr(master, value) == i)
    bg.buttons.append(w)
#    if callback == None and hasattr(bg, "callback"):
#        callback = bg.callback
#    if callback != None:
#        connectControl(w, master, value, callback, "clicked()", CallFrontRadioButtons(bg), CallBackRadioButton(w, master, bg))
    if tooltip:
        w.setToolTip(tooltip)
    return w


def hSlider(widget, master, value, box=None, minValue=0, maxValue=10, step=1, callback=None, label=None, labelFormat=" %d", ticks=0, divideFactor = 1.0, debuggingEnabled = 1, vertical = False, createLabel = 1, tooltip = None, width = None):
    sliderBox = widgetBox(widget, box, orientation = "horizontal")
    if label:
        lbl = widgetLabel(sliderBox, label)

    if vertical:
        sliderOrient = Qt.Vertical
    else:
        sliderOrient = Qt.Horizontal

    slider = QSlider(sliderOrient, sliderBox)
    slider.setRange(minValue, maxValue)
    slider.setSingleStep(step)
    slider.setPageStep(step)
    slider.setTickInterval(step)
    slider.setValue(getdeepattr(master, value))

    if tooltip:
        slider.setToolTip(tooltip)

    if width != None:
        slider.setFixedWidth(width)

    if sliderBox.layout(): sliderBox.layout().addWidget(slider)

    if ticks:
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(ticks)

    if createLabel:
        label = QLabel(sliderBox)
        if sliderBox.layout(): sliderBox.layout().addWidget(label)
        label.setText(labelFormat % minValue)
        width1 = label.sizeHint().width()
        label.setText(labelFormat % maxValue)
        width2 = label.sizeHint().width()
        label.setFixedSize(max(width1, width2), label.sizeHint().height())
        txt = labelFormat % (getdeepattr(master, value)/divideFactor)
        label.setText(txt)
        label.setLbl = lambda x, l=label, f=labelFormat: l.setText(f % (x/divideFactor))
        QObject.connect(slider, SIGNAL("valueChanged(int)"), label.setLbl)

    connectControl(slider, master, value, callback, "valueChanged(int)", CallFrontHSlider(slider))

    if debuggingEnabled and hasattr(master, "_guiElements"):
        master._guiElements = getattr(master, "_guiElements", []) + [("hSlider", slider, value, minValue, maxValue, step, callback)]
    return slider


def qwtHSlider(widget, master, value, box=None, label=None, labelWidth=None, minValue=1, maxValue=10, step=0.1, precision=1, callback=None, logarithmic=0, ticks=0, maxWidth=80, tooltip = None, showValueLabel = 1, debuggingEnabled = 1, addSpace=False, orientation=0):
    import PyQt4.Qwt5 as qwt

    init = getdeepattr(master, value)

    if label:
        hb = widgetBox(widget, box, orientation) 
        lbl = widgetLabel(hb, label)
        if labelWidth:
            lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
        if orientation and orientation!="horizontal":
            separator(hb, height=2)
            hb = widgetBox(hb, 0)
    else:
        hb = widgetBox(widget, box, 0)

    if ticks:
        slider = qwt.QwtSlider(hb, Qt.Horizontal, qwt.QwtSlider.Bottom, qwt.QwtSlider.BgSlot)
    else:
        slider = qwt.QwtSlider(hb, Qt.Horizontal, qwt.QwtSlider.NoScale, qwt.QwtSlider.BgSlot)
    hb.layout().addWidget(slider)

    slider.setScale(minValue, maxValue, logarithmic) # the third parameter for logaritmic scale
    slider.setScaleMaxMinor(10)
    slider.setThumbWidth(20)
    slider.setThumbLength(12)
    if maxWidth:
        slider.setMaximumSize(maxWidth,40)
    if logarithmic:
        slider.setRange(math.log10(minValue), math.log10(maxValue), step)
        slider.setValue(math.log10(init))
    else:
        slider.setRange(minValue, maxValue, step)
        slider.setValue(init)
    if tooltip:
        hb.setToolTip(tooltip)

##    format = "%s%d.%df" % ("%", precision+3, precision)
#    format = " %s.%df" % ("%", precision)
    if type(precision) == str:  format = precision
    else:                       format = " %s.%df" % ("%", precision)

    if showValueLabel:
        lbl = widgetLabel(hb, format % minValue)
        width1 = lbl.sizeHint().width()
        lbl.setText(format % maxValue)
        width2 = lbl.sizeHint().width()
        lbl.setFixedSize(max(width1, width2), lbl.sizeHint().height())
        lbl.setText(format % init)

    if logarithmic:
        cfront = CallFrontLogSlider(slider)
        cback = ValueCallback(master, value, f=lambda x: 10**x)
        if showValueLabel: QObject.connect(slider, SIGNAL("valueChanged(double)"), SetLabelCallback(master, lbl, format=format, f=lambda x: 10**x))
    else:
        cfront = CallFrontHSlider(slider)
        cback = ValueCallback(master, value)
        if showValueLabel: QObject.connect(slider, SIGNAL("valueChanged(double)"), SetLabelCallback(master, lbl, format=format))
    connectControl(slider, master, value, callback, "valueChanged(double)", cfront, cback)
    slider.box = hb

    if debuggingEnabled and hasattr(master, "_guiElements"):
        master._guiElements = getattr(master, "_guiElements", []) + [("qwtHSlider", slider, value, minValue, maxValue, step, callback)]
    return slider


# list box where we can use drag and drop

class SmallWidgetButton(QPushButton):
    def __init__(self, widget, text = "", pixmap = None, box = None, orientation='vertical', tooltip = None, autoHideWidget = None):
        #self.parent = parent
        if pixmap != None:
            import os
            iconDir = os.path.join(os.path.dirname(__file__), "icons")
            if type(pixmap) == str:
                if os.path.exists(pixmap):
                    name = pixmap
                elif os.path.exists(os.path.join(iconDir, pixmap)):
                    name = os.path.join(iconDir, pixmap)
            elif type(pixmap) == QPixmap or type(pixmap) == QIcon:
                name = pixmap
            else:
                name = os.path.join(iconDir, "arrow_down.png")
            QPushButton.__init__(self, QIcon(name), text, widget)
        else:
            QPushButton.__init__(self, text, widget)
        if widget.layout():
            widget.layout().addWidget(self)
        if tooltip != None:
            self.setToolTip(tooltip)
        # create autohide widget and set a layout
        if autoHideWidget != None:
            self.autohideWidget = autoHideWidget(None, Qt.Popup)
        else:            
            self.autohideWidget = AutoHideWidget(None, Qt.Popup)
        self.widget = self.autohideWidget 

        if isinstance(orientation, QLayout):
            self.widget.setLayout(orientation)
        elif orientation == 'horizontal' or not orientation:
            self.widget.setLayout(QHBoxLayout())
        else:
            self.widget.setLayout(QVBoxLayout())
        #self.widget.layout().setMargin(groupBoxMargin)

        if box:
            self.widget = widgetBox(self.widget, box, orientation)
        #self.setStyleSheet("QPushButton:hover { background-color: #F4F2F0; }")

        self.autohideWidget.hide()

    def mousePressEvent(self, ev):
        QWidget.mousePressEvent(self, ev)
        if self.autohideWidget.isVisible():
            self.autohideWidget.hide()
        else:
            #self.widget.move(self.parent.mapToGlobal(QPoint(0, 0)).x(), self.mapToGlobal(QPoint(0, self.height())).y())
            self.autohideWidget.move(self.mapToGlobal(QPoint(0, self.height())))
            self.autohideWidget.show()


class SmallWidgetLabel(QLabel):
    def __init__(self, widget, text = "", pixmap = None, box = None, orientation='vertical', tooltip = None):
        QLabel.__init__(self, widget)
        if text != "":
            self.setText("<font color=\"#C10004\">" + text + "</font>")
        elif pixmap != None:
            import os
            iconDir = os.path.join(os.path.dirname(__file__), "icons")
            if type(pixmap) == str:
                if os.path.exists(pixmap):
                    name = pixmap
                elif os.path.exists(os.path.join(iconDir, pixmap)):
                    name = os.path.join(iconDir, pixmap)
            elif type(pixmap) == QPixmap or type(pixmap) == QIcon:
                name = pixmap
            else:
                name = os.path.join(iconDir, "arrow_down.png")
            self.setPixmap(QPixmap(name))
        if widget.layout():
            widget.layout().addWidget(self)
        if tooltip != None:
            self.setToolTip(tooltip)
        self.autohideWidget = self.widget = AutoHideWidget(None, Qt.Popup)

        if isinstance(orientation, QLayout):
            self.widget.setLayout(orientation)
        elif orientation == 'horizontal' or not orientation:
            self.widget.setLayout(QHBoxLayout())
        else:
            self.widget.setLayout(QVBoxLayout())

        if box:
            self.widget = widgetBox(self.widget, box, orientation)

        self.autohideWidget.hide()

    def mousePressEvent(self, ev):
        QLabel.mousePressEvent(self, ev)
        if self.autohideWidget.isVisible():
            self.autohideWidget.hide()
        else:
            #self.widget.move(self.parent.mapToGlobal(QPoint(0, 0)).x(), self.mapToGlobal(QPoint(0, self.height())).y())
            self.autohideWidget.move(self.mapToGlobal(QPoint(0, self.height())))
            self.autohideWidget.show()


class AutoHideWidget(QWidget):
#    def __init__(self, parent = None):
#        QWidget.__init__(self, parent, Qt.Popup)

    def leaveEvent(self, ev):
        self.hide()



class SearchLineEdit(QLineEdit):
    def __init__(self, t, searcher):
        QLineEdit.__init__(self, t)
        self.searcher = searcher

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Down:
            curItem = self.searcher.lb.currentItem()
            if curItem+1 < self.searcher.lb.count():
                self.searcher.lb.setCurrentItem(curItem+1)
        elif k == Qt.Key_Up:
            curItem = self.searcher.lb.currentItem()
            if curItem:
                self.searcher.lb.setCurrentItem(curItem-1)
        elif k == Qt.Key_Escape:
            self.searcher.window.hide()
        else:
            return QLineEdit.keyPressEvent(self, e)

class Searcher:
    def __init__(self, control, master):
        self.control = control
        self.master = master

    def __call__(self):
        self.window = t = QFrame(self.master, "", QStyle.WStyle_Dialog + QStyle.WStyle_Tool + QStyle.WStyle_Customize + QStyle.WStyle_NormalBorder)
        la = QVBoxLayout(t).setAutoAdd(1)
        gs = self.master.mapToGlobal(QPoint(0, 0))
        gl = self.control.mapToGlobal(QPoint(0, 0))
        t.move(gl.x()-gs.x(), gl.y()-gs.y())
        self.allItems = [str(self.control.text(i)) for i in range(self.control.count())]
        le = SearchLineEdit(t, self)
        self.lb = QListBox(t)
        for i in self.allItems:
            self.lb.insertItem(i)
        t.setFixedSize(self.control.width(), 200)
        t.show()
        le.setFocus()

        QObject.connect(le, SIGNAL("textChanged(const QString &)"), self.textChanged)
        QObject.connect(le, SIGNAL("returnPressed()"), self.returnPressed)
        QObject.connect(self.lb, SIGNAL("clicked(QListBoxItem *)"), self.mouseClicked)

    def textChanged(self, s):
        s = str(s)
        self.lb.clear()
        for i in self.allItems:
            if s.lower() in i.lower():
                self.lb.insertItem(i)

    def returnPressed(self):
        if self.lb.count():
            self.conclude(self.lb.text(max(0, self.lb.currentItem())))
        else:
            self.window.hide()

    def mouseClicked(self, item):
        self.conclude(item.text())

    def conclude(self, valueQStr):
        value = str(valueQStr)
        index = self.allItems.index(value)
        self.control.setCurrentItem(index)
        if self.control.cback:
            if self.control.sendSelectedValue:
                self.control.cback(value)
            else:
                self.control.cback(index)
        if self.control.cfunc:
            self.control.cfunc()

        self.window.hide()





def comboBoxWithCaption(widget, master, value, label, box=None, items=None, tooltip=None, callback = None, sendSelectedValue=0, valueType = int, labelWidth = None, debuggingEnabled = 1):
    hbox = widgetBox(widget, box = box, orientation="horizontal")
    lab = widgetLabel(hbox, label + "  ", labelWidth)
    combo = comboBox(hbox, master, value, items = items, tooltip = tooltip, callback = callback, sendSelectedValue = sendSelectedValue, valueType = valueType, debuggingEnabled = debuggingEnabled)
    return combo

# creates a widget box with a button in the top right edge, that allows you to hide all the widgets in the box and collapse the box to its minimum height
# creates an icon that allows you to show/hide the widgets in the widgets list
class widgetHider(QWidget):
    def __init__(self, widget, master, value, size = (19,19), widgets = [], tooltip = None):
        QWidget.__init__(self, widget)
        if widget.layout():
            widget.layout().addWidget(self)
        self.value = value
        self.master = master

        if tooltip:
            self.setToolTip(tooltip)

        import os
        iconDir = os.path.join(os.path.dirname(__file__), "icons")
        icon1 = os.path.join(iconDir, "arrow_down.png")
        icon2 = os.path.join(iconDir, "arrow_up.png")
        self.pixmaps = []

        self.pixmaps = [QPixmap(icon1), QPixmap(icon2)]
        self.setFixedSize(self.pixmaps[0].size())

        self.disables = widgets or [] # need to create a new instance of list (in case someone would want to append...)
        self.makeConsistent = Disabler(self, master, value, type = HIDER)
        if widgets != []:
            self.setWidgets(widgets)

    def mousePressEvent(self, ev):
        self.master.__setattr__(self.value, not getdeepattr(self.master, self.value))
        self.makeConsistent.__call__()


    def setWidgets(self, widgets):
        self.disables = widgets or []
        self.makeConsistent.__call__()

    def paintEvent(self, ev):
        QWidget.paintEvent(self, ev)

        if self.pixmaps != []:
            pix = self.pixmaps[getdeepattr(self.master, self.value)]
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pix)


##############################################################################
# callback handlers

def setStopper(master, sendButton, stopCheckbox, changedFlag, callback):
    stopCheckbox.disables.append((-1, sendButton))
    sendButton.setDisabled(stopCheckbox.isChecked())
    QObject.connect(stopCheckbox, SIGNAL("toggled(bool)"),
                   lambda x, master=master, changedFlag=changedFlag, callback=callback: x and getdeepattr(master, changedFlag, default=True) and callback())


class ControlledList(list):
    def __init__(self, content, listBox = None):
        list.__init__(self, content)
        self.listBox = listBox

    def __reduce__(self):
        # cannot pickle self.listBox, but can't discard it (ControlledList may live on)
        import copy_reg
        return copy_reg._reconstructor, (list, list, ()), None, self.__iter__()

    def item2name(self, item):
        item = self.listBox.labels[item]
        if type(item) == tuple:
            return item[1]
        else:
            return item

    def __setitem__(self, index, item):
        self.listBox.item(list.__getitem__(self, index)).setSelected(0)
        item.setSelected(1)
        list.__setitem__(self, index, item)

    def __delitem__(self, index):
        self.listBox.item(__getitem__(self, index)).setSelected(0)
        list.__delitem__(self, index)

    def __setslice__(self, start, end, slice):
        for i in list.__getslice__(self, start, end):
            self.listBox.item(i).setSelected(0)
        for i in slice:
            self.listBox.item(i).setSelected(1)
        list.__setslice__(self, start, end, slice)

    def __delslice__(self, start, end):
        if not start and end==len(self):
            for i in range(self.listBox.count()):
                self.listBox.item(i).setSelected(0)
        else:
            for i in list.__getslice__(self, start, end):
                self.listBox.item(i).setSelected(0)
        list.__delslice__(self, start, end)

    def append(self, item):
        list.append(self, item)
        item.setSelected(1)

    def extend(self, slice):
        list.extend(self, slice)
        for i in slice:
            self.listBox.item(i).setSelected(1)

    def insert(self, index, item):
        item.setSelected(1)
        list.insert(self, index, item)

    def pop(self, index=-1):
        self.listBox.item(list.__getitem__(self, index)).setSelected(0)
        list.pop(self, index)

    def remove(self, item):
        item.setSelected(0)
        list.remove(self, item)


def connectControlSignal(control, signal, f):
    if type(signal) == tuple:
        control, signal = signal
    QObject.connect(control, SIGNAL(signal), f)


def connectControl(control, master, value, f, signal, cfront, cback = None, cfunc = None, fvcb = None):
    cback = cback or value and ValueCallback(master, value, fvcb)
    if cback:
        if signal:
            connectControlSignal(control, signal, cback)
        cback.opposite = cfront
        if value and cfront and hasattr(master, "controlledAttributes"):
            master.controlledAttributes[value] = cfront

    cfunc = cfunc or f and FunctionCallback(master, f)
    if cfunc:
        if signal:
            connectControlSignal(control, signal, cfunc)
        cfront.opposite = cback, cfunc
    else:
        cfront.opposite = (cback,)

    return cfront, cback, cfunc


class ControlledCallback:
    def __init__(self, widget, attribute, f = None):
        self.widget = widget
        self.attribute = attribute
        self.f = f
        self.disabled = 0
        if type(widget) == dict: return     # we can't assign attributes to dict
        if not hasattr(widget, "callbackDeposit"):
            widget.callbackDeposit = []
        widget.callbackDeposit.append(self)
        

    def acyclic_setattr(self, value):
        if self.disabled:
            return

        if isinstance(value, QString):
            value = unicode(value)
        if self.f:
            if self.f in [int, float] and (not value or type(value) in [str, unicode] and value in "+-"):
                value = self.f(0)
            else:
                value = self.f(value)

        opposite = getattr(self, "opposite", None)
        if opposite:
            try:
                opposite.disabled += 1
                if type(self.widget) == dict: self.widget[self.attribute] = value
                else:                         setattr(self.widget, self.attribute, value)
            finally:
                opposite.disabled -= 1
        else:
            if type(self.widget) == dict: self.widget[self.attribute] = value
            else:                         setattr(self.widget, self.attribute, value)


class ValueCallback(ControlledCallback):
    def __call__(self, value):
        if value is not None:
            try:
                self.acyclic_setattr(value)
            except:
                print "OWGUI.ValueCallback: %s" % value
                import traceback, sys
                traceback.print_exception(*sys.exc_info())


class ValueCallbackCombo(ValueCallback):
    def __init__(self, widget, attribute, f = None, control2attributeDict = {}):
        ValueCallback.__init__(self, widget, attribute, f)
        self.control2attributeDict = control2attributeDict

    def __call__(self, value):
        value = unicode(value)
        return ValueCallback.__call__(self, self.control2attributeDict.get(value, value))



class ValueCallbackLineEdit(ControlledCallback):
    def __init__(self, control, widget, attribute, f = None):
        ControlledCallback.__init__(self, widget, attribute, f)
        self.control = control

    def __call__(self, value):
        if value is not None:
            try:
                pos = self.control.cursorPosition()
                self.acyclic_setattr(value)
                self.control.setCursorPosition(pos)
            except:
                print "invalid value ", value, type(value)


class SetLabelCallback:
    def __init__(self, widget, label, format = "%5.2f", f = None):
        self.widget = widget
        self.label = label
        self.format = format
        self.f = f
        if hasattr(widget, "callbackDeposit"):
            widget.callbackDeposit.append(self)
        self.disabled = 0

    def __call__(self, value):
        if not self.disabled and value is not None:
            if self.f:
                value = self.f(value)
            self.label.setText(self.format % value)


class FunctionCallback:
    def __init__(self, master, f, widget=None, id=None, getwidget=None):
        self.master = master
        self.widget = widget
        self.f = f
        self.id = id
        self.getwidget = getwidget
        if hasattr(master, "callbackDeposit"):
            master.callbackDeposit.append(self)
        self.disabled = 0

    def __call__(self, *value):
        if not self.disabled and value!=None:
            kwds = {}
            if self.id <> None:
                kwds['id'] = self.id
            if self.getwidget:
                kwds['widget'] = self.widget
            if isinstance(self.f, list):
                for f in self.f:
                    f(**kwds)
            else:
                self.f(**kwds)


class CallBackListBox:
    def __init__(self, control, widget):
        self.control = control
        self.widget = widget
        self.disabled = 0

    def __call__(self, *args): # triggered by selectionChange()
        if not self.disabled and self.control.ogValue != None:
            clist = getdeepattr(self.widget, self.control.ogValue)
            list.__delslice__(clist, 0, len(clist))
            control = self.control
            for i in range(control.count()):
                if control.item(i).isSelected():
                    list.append(clist, i)
            self.widget.__setattr__(self.control.ogValue, clist)


class CallBackRadioButton:
    def __init__(self, control, widget):
        self.control = control
        self.widget = widget
        self.disabled = False

    def __call__(self, *args): # triggered by toggled()
        if not self.disabled and self.control.ogValue != None:
            arr = [butt.isChecked() for butt in self.control.buttons]
            self.widget.__setattr__(self.control.ogValue, arr.index(1))


##############################################################################
# call fronts (through this a change of the attribute value changes the related control)


class ControlledCallFront:
    def __init__(self, control):
        self.control = control
        self.disabled = 0

    def __call__(self, *args):
        if not self.disabled:
            opposite = getattr(self, "opposite", None)
            if opposite:
                try:
                    for op in opposite:
                        op.disabled += 1
                    self.action(*args)
                finally:
                    for op in opposite:
                        op.disabled -= 1
            else:
                self.action(*args)


class CallFrontSpin(ControlledCallFront):
    def action(self, value):
        if value is not None:
            self.control.setValue(value)


class CallFrontDoubleSpin(ControlledCallFront):
    def action(self, value):
        if value is not None:
            self.control.setValue(value)


class CallFrontCheckBox(ControlledCallFront):
    def action(self, value):
        if value != None:
            values = [Qt.Unchecked, Qt.Checked, Qt.PartiallyChecked]
            self.control.setCheckState(values[value])

class CallFrontButton(ControlledCallFront):
    def action(self, value):
        if value != None:
            self.control.setChecked(bool(value))

class CallFrontComboBox(ControlledCallFront):
    def __init__(self, control, valType = None, control2attributeDict = {}):
        ControlledCallFront.__init__(self, control)
        self.valType = valType
        self.attribute2controlDict = dict([(y, x) for x, y in control2attributeDict.items()])

    def action(self, value):
        if value is not None:
            value = self.attribute2controlDict.get(value, value)
            if self.valType:
                for i in range(self.control.count()):
                    if self.valType(str(self.control.itemText(i))) == value:
                        self.control.setCurrentIndex(i)
                        return
                values = ""
                for i in range(self.control.count()):
                    values += str(self.control.itemText(i)) + (i < self.control.count()-1 and ", " or ".")
                print "unable to set %s to value '%s'. Possible values are %s" % (self.control, value, values)
                #import traceback
                #traceback.print_stack()
            else:
                if value < self.control.count():
                    self.control.setCurrentIndex(value)


class CallFrontHSlider(ControlledCallFront):
    def action(self, value):
        if value is not None:
            self.control.setValue(value)


class CallFrontLogSlider(ControlledCallFront):
    def action(self, value):
        if value is not None:
            if value < 1e-30:
                print "unable to set ", self.control, "to value ", value, " (value too small)"
            else:
                self.control.setValue(math.log10(value))


class CallFrontLineEdit(ControlledCallFront):
    def action(self, value):
        self.control.setText(unicode(value))


class CallFrontRadioButtons(ControlledCallFront):
    def action(self, value):
        if value < 0 or value >= len(self.control.buttons):
            value = 0
        self.control.buttons[value].setChecked(1)


class CallFrontListBox(ControlledCallFront):
    def action(self, value):
        if value is not None:
            if not isinstance(value, ControlledList):
                setattr(self.control.ogMaster, self.control.ogValue, ControlledList(value, self.control))
            for i in range(self.control.count()):
                shouldBe = i in value
                if shouldBe != self.control.item(i).isSelected():
                    self.control.item(i).setSelected(shouldBe)


class CallFrontListBoxLabels(ControlledCallFront):
    def action(self, value):
        icons = getAttributeIcons()
        self.control.clear()
        if value:
            for i in value:
                if type(i) == tuple:
                    if isinstance(i[1], int):
                        self.control.addItem(QListWidgetItem(icons.get(i[1], icons[-1]), i[0]))
                    else:
                        self.control.addItem( QListWidgetItem(i[0],i[1]) )
                else:
                    self.control.addItem(i)


class CallFrontLabel:
    def __init__(self, control, label, master):
        self.control = control
        self.label = label
        self.master = master

    def __call__(self, *args):
        self.control.setText(self.label % self.master.__dict__)

##############################################################################
## Disabler is a call-back class for check box that can disable/enable other
## widgets according to state (checked/unchecked, enabled/disable) of the
## given check box
##
## Tricky: if self.propagateState is True (default), then if check box is
## disabled, the related widgets will be disabled (even if the checkbox is
## checked). If self.propagateState is False, the related widgets will be
## disabled/enabled if check box is checked/clear, disregarding whether the
## check box itself is enabled or not. (If you don't understand, see the code :-)
DISABLER = 1
HIDER = 2

class Disabler:
    def __init__(self, widget, master, valueName, propagateState = 1, type = DISABLER):
        self.widget = widget
        self.master = master
        self.valueName = valueName
        self.propagateState = propagateState
        self.type = type

    def __call__(self, *value):
        currState = self.widget.isEnabled()

        if currState or not self.propagateState:
            if len(value):
                disabled = not value[0]
            else:
                disabled = not getdeepattr(self.master, self.valueName)
        else:
            disabled = 1

        for w in self.widget.disables:
            if type(w) == tuple:
                if isinstance(w[0], int):
                    i = 1
                    if w[0] == -1:
                        disabled = not disabled
                else:
                    i = 0
                if self.type == DISABLER:
                    w[i].setDisabled(disabled)
                elif self.type == HIDER:
                    if disabled: w[i].hide()
                    else:        w[i].show()

                if hasattr(w[i], "makeConsistent"):
                    w[i].makeConsistent()
            else:
                if self.type == DISABLER:
                    w.setDisabled(disabled)
                elif self.type == HIDER:
                    if disabled: w.hide()
                    else:        w.show()

##############################################################################
# some table related widgets

class tableItem(QTableWidgetItem):
    def __init__(self, table, x, y, text, editType = None, backColor=None, icon=None, type = QTableWidgetItem.Type):
        QTableWidgetItem.__init__(self, type)
        if icon:
            self.setIcon(QIcon(icon))
        if editType != None:
            self.setFlags(editType)
        else:
            self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
        if backColor != None:
            self.setBackground(QBrush(backColor))
        self.setData(Qt.DisplayRole, QVariant(text))        # we add it this way so that text can also be int and sorting will be done properly (as integers and not as text)

        table.setItem(x, y, self)



class TableBarItem(QItemDelegate):
    def __init__(self, widget, table = None, color = QColor(255, 170, 127)):
        QItemDelegate.__init__(self, widget)
        self.color = color
        self.widget = widget
        self.table = table

    def paint(self, painter, option, index):
        painter.save()
        self.drawBackground(painter, option, index)
        value, ok = index.data(Qt.DisplayRole).toDouble()
        if ok and self.widget.showBars:
            col = index.column()
            if col < len(self.table.normalizers):
                max, span = self.table.normalizers[col]
                painter.fillRect(option.rect.adjusted(0, 1, -option.rect.width()*(max - value) / span, -1), self.color)
#                painter.fillRect(option.rect.adjusted(0, option.rect.height()-4, -option.rect.width()*(max - value) / span, 0), self.color)
        text = index.data(Qt.DisplayRole).toString()

        self.drawDisplay(painter, option, option.rect, text)
        painter.restore()

##############################################################################
# progress bar management

class ProgressBar:
    def __init__(self, widget, iterations):
        self.iter = iterations
        self.widget = widget
        self.count = 0
        self.widget.progressBarInit()

    def advance(self):
        self.count += 1
        self.widget.progressBarSet(int(self.count*100/self.iter))

    def finish(self):
        self.widget.progressBarFinished()

##############################################################################
