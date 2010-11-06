# Author: Gregor Leban (gregor.leban@fri.uni-lj.si)
# Description:
#    two main objects that are shown in the canvas; Line and Widget
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, math, sip
import orngSignalManager
import signals, redREnviron, redRObjects, log
ERROR = 0
WARNING = 1

class TempCanvasLine(QGraphicsLineItem):
    def __init__(self, canvasDlg, canvas):
        QGraphicsLineItem.__init__(self, None, canvas)
        self.setZValue(-10)
        self.canvasDlg = canvasDlg
        self.setPen(QPen(canvasDlg.lineColor, 1, Qt.SolidLine, Qt.RoundCap))
        self.startWidget = None
        self.endWidget = None
        self.widget = None
        
    def setStartWidget(self, widget):
        self.startWidget = widget
        pos = widget.getRightEdgePoint()
        self.setLine(pos.x(), pos.y(), pos.x(), pos.y())
        
    def setEndWidget(self, widget):
        self.endWidget = widget
        pos = widget.getLeftEdgePoint()
        self.setLine(pos.x(), pos.y(), pos.x(), pos.y())
        
    def updateLinePos(self, newPos):
        if self.startWidget == None and self.endWidget == None: return
        
        if self.startWidget != None:   func = "getDistToLeftEdgePoint"
        else:                          func = "getDistToRightEdgePoint"
        
        schema = self.canvasDlg.schema
        view = schema.activeTab()
        
        self.widget = None
        widgets = view.getItemsAtPos(newPos, CanvasWidget)
        if widgets:
            self.widget = widgets[0]
        else:
            dists = [(getattr(w, func)(newPos), w) for w in redRObjects.getIconsByTab([redRObjects.activeTabName()])[redRObjects.activeTabName()]]
            dists.sort()
            if dists and dists[0][0] < 20:
                self.widget = dists[0][1]
        
        if self.startWidget: pos = self.startWidget.getRightEdgePoint()
        else:                pos = self.endWidget.getLeftEdgePoint()

        if self.widget not in [self.startWidget, self.endWidget]: 
            if self.startWidget == None and self.widget.instance().outputs: newPos = self.widget.getRightEdgePoint()
            elif self.endWidget == None and self.widget.instance().inputs:  newPos = self.widget.getLeftEdgePoint()
        
        self.setLine(pos.x(), pos.y(), newPos.x(), newPos.y())
        
    def remove(self):
        self.hide()

    # draw the line
    def drawShape(self, painter):
        (startX, startY) = (self.startPoint().x(), self.startPoint().y())
        (endX, endY)  = (self.endPoint().x(), self.endPoint().y())

        painter.setPen(QPen(self.canvasDlg.lineColor, 1, Qt.SolidLine))
        painter.drawLine(QPoint(startX, startY), QPoint(endX, endY))


    # we don't print temp lines
    def printShape(self, painter):
        pass


    # redraw the line
##    def repaintLine(self, canvasView):
##        p1 = self.startPoint()
##        p2 = self.endPoint()
##        #canvasView.repaint(QRect(min(p1.x(), p2.x())-5, min(p1.y(), p2.y())-5, abs(p1.x()-p2.x())+10,abs(p1.y()-p2.y())+10))
##        #canvasView.repaint(QRect(min(p1.x(), p2.x()), min(p1.y(), p2.y()), abs(p1.x()-p2.x()),abs(p1.y()-p2.y())))

# #######################################
# # CANVAS LINE
# #######################################
class CanvasLine(QGraphicsLineItem):
    def __init__(self, signalManager, canvasDlg, view, outWidget, inWidget, canvas, tabName, *args):
        QGraphicsLineItem.__init__(self, None, canvas)
        self.dirty = False
        self.noData = False
        self.tab = tabName
        self.signalManager = signalManager
        self.canvasDlg = canvasDlg
        self.outWidget = outWidget
        self.inWidget = inWidget
        self.view = view
        self.setZValue(-10)
        self.caption = ""
        #self.updateTooltip()
        self.refreshToolTip()

        # this might seem unnecessary, but the pen size 20 is used for collision detection, when we want to see whether to to show the line menu or not 
        self.setPen(QPen(self.canvasDlg.lineColor, 20, Qt.SolidLine))        
    def setNoData(self, noData):
        self.noData = noData
    def refreshToolTip(self):
        #  first we need to get the signals that are sent through the line, there might be more than one so we do it here.
        outinstance = self.outWidget.instance()
        #log.log(1, 9, 3, 'orngCanvasItems in refreshToolTip; outWidget %s, outinstance %s, inInstance %s, signals %s' % (self.outWidget, outinstance, self.inWidget.instance(), outinstance.outputs.outputSignals))
        outSignalIDs = [i[0] for i in outinstance.outputs.getLinkPairs(self.inWidget.instance())]
        #log.log(1, 9, 3, 'orngCanvasItems in refreshToolTip; outSignalIDs' % outSignalIDs)
        tip = 'Signal Data Summary:\n'
        for id in outSignalIDs:
            #log.log(1, 9, 3, 'orngCanvasItems in refreshToolTip; setting tooltip from %s' % id)
            s = outinstance.outputs.getSignal(id)
            #if s:
            tip += s['value'].summary()+'\n'
        log.log(1, 2, 3, 'orngCanvasItems in refreshToolTip; setting tooltip to %s' % tip)
        self.setToolTip(tip)
    def getNoData(self):
        return self.noData
    def remove(self):
        self.hide()
        self.setToolTip("")
        #self.view.repaint(QRect(min(self.startPoint().x(), self.endPoint().x())-55, min(self.startPoint().y(), self.endPoint().y())-55, abs(self.startPoint().x()-self.endPoint().x())+100,abs(self.startPoint().y()-self.endPoint().y())+100))

    def getEnabled(self):
        
        return self.outWidget.instance().outputs.isSignalEnabled(self.inWidget.instance())##    int(self.signalManager.isSignalEnabled(self.outWidget.instance, self.inWidget.instance, signals[0][0], signals[0][1]))

    def getSignals(self):
        signals = []
        for (inWidgetInstance, outName, inName, X) in self.signalManager.links.get(self.outWidget.instance(), []):
            if inWidgetInstance == self.inWidget.instance:
                
                signals.append((outName, inName))
        #print 'Signals collected, ', signals
        return signals

    def paint(self, painter, option, widget = None):
        p1 = self.outWidget.getRightEdgePoint()
        p2 = self.inWidget.getLeftEdgePoint()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        if self.dirty:
            color = QColor('#999999')
        elif self.noData:
            color = QColor('#990000')
        else:
            color = self.canvasDlg.lineColor
        painter.setPen(QPen(color, 5 , self.getEnabled() and Qt.SolidLine or Qt.DashLine, Qt.RoundCap))
        painter.drawLine(p1, p2)

        if redREnviron.settings["showSignalNames"]:
            painter.setPen(QColor(80, 80, 80))
            mid = (p1+p2-QPointF(200, 30))/2 
            painter.drawText(mid.x(), mid.y(), 200, 50, Qt.AlignTop | Qt.AlignHCenter, self.caption)

    def updateTooltip(self):
        self.refreshToolTip()
        
# #######################################
# # CANVAS WIDGET
# #######################################
class CanvasWidget(QGraphicsRectItem): # not really the widget itself but a graphical representation of it
    def __init__(self, signalManager, canvas, view, widgetInfo, defaultPic, canvasDlg, instanceID, tabName):        
        # print widgetSettings
        self.signalManager = signalManager
        self.widgetInfo = widgetInfo
        self.tab = tabName
        #self.widgetSettings = widgetSettings
        # if not clone:
            # m = __import__(widgetInfo.fileName)
        
            
            # self.instance = m.__dict__[widgetInfo.widgetName].__new__(m.__dict__[widgetInfo.widgetName],
            # _owInfo = redREnviron.settings["owInfo"],
            # _owWarning = redREnviron.settings["owWarning"],
            # _owError = redREnviron.settings["owError"],
            # _owShowStatus = redREnviron.settings["owShow"],
            # _packageName = widgetInfo.packageName)
        
            # self.instance.__dict__['_widgetInfo'] = widgetInfo
            
            # if widgetInfo.name == 'Dummy': 
                # print 'Loading dummy step 3'
                # self.instance.__init__(signalManager = signalManager,
                # forceInSignals = forceInSignals, forceOutSignals = forceOutSignals)
            # else: self.instance.__init__(signalManager = signalManager)
            

            # self.instance.loadGlobalSettings()
            # if widgetSettings:
                # self.instance.setSettings(widgetSettings)
                # if '_customSettings' in widgetSettings.keys():
                    # self.instance.loadCustomSettings(widgetSettings['_customSettings'])
                # else:
                    # self.instance.loadCustomSettings(widgetSettings)

            
            # self.instance.ghost = False
            # self.instance.setProgressBarHandler(view.progressBarHandler)   # set progress bar event handler
            # self.instance.setProcessingHandler(view.processingHandler)
            # self.instance.setWidgetStateHandler(self.updateWidgetState)
            # self.instance.setEventHandler(canvasDlg.output.widgetEvents)
            # self.instance.setWidgetWindowIcon(widgetInfo.icon)
            # self.instance.canvasWidget = self
        # else:
        self.instanceID = instanceID
            
            
        #self.setForces(forceInSignals, forceOutSignals) # a patch for dummywidget
        self.isProcessing = 0   # is this widget currently processing signals
        self.needsProcessing = 0 # is this widget in need of processing data
        self.progressBarShown = 0
        self.progressBarValue = -1
        self.widgetSize = QSizeF(0, 0)
        self.widgetState = {}
        self.caption = widgetInfo.name
        self.selected = False
        self.inLines = []               # list of connected lines on input
        self.outLines = []              # list of connected lines on output
        self.ghostWidgets = []          # list of ghost widgets that this widget could connect to
        self.ghost = False
        self.icon = QIcon(widgetInfo.icon)
        self.tab = canvasDlg.schema.activeTabName()
        #self.instance.updateStatusBarState()

        QGraphicsRectItem.__init__(self, None, canvas)
        
        
        # if widgetInfo.fileName == 'dummy': # we need to add the inputs and outputs
            # print widgetInfo.__dict__['inputs']
            # try:
                # i = 0
                # for (a, b, c) in self.instance.inputs:
                    # b = forceInSignals[i][1]
                    # print b
                    # if b == 'Data Frame': bc = 'signals.RDataFrame'
                    # elif b == 'List': bc = 'signals.RList'
                    # elif b == 'Vector': bc = 'signals.RVector'
                    # else: bc = 'signals.RVariable'
                    # sig = InputSignal(a, bc, None)
                    # widgetInfo.__dict__['inputs'].append(sig)
                    # i += 1
                # o = 0
                # for (a, b) in self.instance.outputs:
                    # b = forceOutSignals[o][1]
                    # print b
                    # if b == 'Data Frame': bc = 'signals.RDataFrame'
                    # elif b == 'List': bc = 'signals.RList'
                    # elif b == 'Vector': bc = 'signals.RVector'
                    # else: bc = 'signals.RVariable'
                    # sig = OutputSignal(a, bc)
                    # widgetInfo.__dict__['outputs'].append()
                # print widgetInfo.__dict__['inputs']
                # print widgetInfo.__dict__['outputs']
            # except:
                # print 'There was an error loading the inputs and outputs'
        self.widgetInfo = widgetInfo
        self.canvas = canvas
        self.view = view
        self.canvasDlg = canvasDlg
        canvasPicsDir  = os.path.join(redREnviron.directoryNames['canvasDir'], "icons")
        self.imageLeftEdge = QPixmap(os.path.join(canvasPicsDir,"leftEdge.png"))
        self.imageRightEdge = QPixmap(os.path.join(canvasPicsDir,"rightEdge.png"))
        self.imageLeftEdgeG = QPixmap(os.path.join(canvasPicsDir,"leftEdgeG.png"))
        self.imageRightEdgeG = QPixmap(os.path.join(canvasPicsDir,"rightEdgeG.png"))
        self.imageLeftEdgeR = QPixmap(os.path.join(canvasPicsDir,"leftEdgeR.png"))
        self.imageRightEdgeR = QPixmap(os.path.join(canvasPicsDir,"rightEdgeR.png"))
        self.shownLeftEdge, self.shownRightEdge = self.imageLeftEdge, self.imageRightEdge
        self.imageFrame = QIcon(QPixmap(os.path.join(canvasPicsDir, "frame.png")))
        self.edgeSize = QSizeF(self.imageLeftEdge.size())
        self.resetWidgetSize()
        
        self.oldPos = self.pos()
        
        self.infoIcon = QGraphicsPixmapItem(self.canvasDlg.widgetIcons["Info"], None, canvas)
        self.warningIcon = QGraphicsPixmapItem(self.canvasDlg.widgetIcons["Warning"], None, canvas)
        self.errorIcon = QGraphicsPixmapItem(self.canvasDlg.widgetIcons["Error"], None, canvas)
        self.infoIcon.hide()
        self.warningIcon.hide()
        self.errorIcon.hide()

    def instance(self):
        return self.canvasDlg.schema.returnInstance(self.instanceID)
    def resetWidgetSize(self):
        size = self.canvasDlg.schemeIconSizeList[redREnviron.settings['schemeIconSize']]
        self.setRect(0,0, size, size)
        self.widgetSize = QSizeF(size, size)
    def getWidgetInfo(self):
        return self.widgetInfo
    # get the list of connected signal names
    def getInConnectedSignalNames(self):
        signals = []
        for line in self.inLines:
            for (outSignal, inSignal) in line.getSignals():
                if inSignal not in signals: signals.append(inSignal)
        return signals

    # get the list of connected signal names
    def getOutConnectedSignalNames(self):
        signals = []
        for line in self.outLines:
            for (outSignal, inSignal) in line.getSignals():
                if outSignal not in signals: signals.append(outSignal)
        return signals
    
    def remove(self):
        self.hide()
        self.errorIcon.hide()
        self.warningIcon.hide()
        self.infoIcon.hide()

        # save settings
        if (self.instance() != None):
            try:
                if self.canvasDlg.menuSaveSettings == 1:        # save settings only if checked in the main menu
                    try:
                        self.instance().saveGlobalSettings()
                    except:
                        log.log(1, 9, 1, "Unable to successfully save settings for %s widget" % (self.instance().captionTitle))
                        type, val, traceback = sys.exc_info()
                        sys.excepthook(type, val, traceback)  # we pretend that we handled the exception, so that it doesn't crash canvas
                self.instance().close()
                self.instance().linksOut.clear()      # this helps python to more quickly delete the unused objects
                self.instance().linksIn.clear()
                self.instance().onDeleteWidget()      # this is a cleanup function that can take care of deleting some unused objects
                # for x in self.instance().findChildren(QAbstractTableModel):
                    # print 'in canvasItems', x
                # print 'delete instance' 
                # sip.delete(self.instance())
                # for x in self.canvasDlg.findChildren(QAbstractTableModel):
                    # print x
                # import gc
                # gc.collect()
                # print 'Remaining references to '+str(gc.get_referrers(self.instance()))
                # print 'Remaining references from '+str(gc.get_referents(self.instance()))


            except: 
                import redRExceptionHandling
                log.log(1, 9, 1, redRExceptionHandling.formatException())

    def savePosition(self):
        self.oldPos = self.pos()

    def restorePosition(self):
        self.setPos(self.oldPos)

    def updateText(self, text):
        self.caption = str(text)
        self.updateTooltip()

    def updateWidgetState(self):
        if not self.ghost:
            widgetState = self.instance().widgetState

            self.infoIcon.hide()
            self.warningIcon.hide()
            self.errorIcon.hide()

            yPos = self.y() - 21 - self.progressBarShown * 20
            iconNum = sum([widgetState.get("Info", {}).values() != [],  widgetState.get("Warning", {}).values() != [], widgetState.get("Error", {}).values() != []])

            if redREnviron.settings["ocShow"]:        # if show icons is enabled in canvas options dialog
                startX = self.x() + (self.rect().width()/2) - ((iconNum*(self.canvasDlg.widgetIcons["Info"].width()+2))/2)
                off  = 0
                if len(widgetState.get("Info", {}).values()) > 0 and redREnviron.settings["ocInfo"]:
                    off  = self.updateWidgetStateIcon(self.infoIcon, startX, yPos, widgetState["Info"])
                if len(widgetState.get("Warning", {}).values()) > 0 and redREnviron.settings["ocWarning"]:
                    off += self.updateWidgetStateIcon(self.warningIcon, startX+off, yPos, widgetState["Warning"])
                if len(widgetState.get("Error", {}).values()) > 0 and redREnviron.settings["ocError"]:
                    off += self.updateWidgetStateIcon(self.errorIcon, startX+off, yPos, widgetState["Error"])


    def updateWidgetStateIcon(self, icon, x, y, stateDict):
        icon.setPos(x,y)
        icon.show()
        icon.setToolTip(reduce(lambda x,y: x+'<br>'+y, stateDict.values()))
        return icon.pixmap().width() + 3

    def isSelected(self):
        return self.selected

    def setSelected(self, selected):
        self.selected = selected
        self.canvasDlg.tabs.suggestButtonsList.hide()
        if self.selected:
            self.canvasDlg.tabs.suggestButtonsList.clear()
            newActions = self.canvasDlg.schema.getSuggestWidgets(self)
            if len(newActions) > 0:
                self.canvasDlg.tabs.suggestButtonsList.show()
                self.canvasDlg.tabs.suggestButtonsList.addTopLevelItems(newActions)
                self.canvasDlg.tabs.suggestButtonsList.suggestingWidget = self
                self.canvasDlg.tabs.suggestButtonsList.setHeaderLabels(['Suggested Widgets for '+str(self.widgetInfo.name)])
            else:
                self.canvasDlg.tabs.suggestButtonsList.hide()
            
        
    # set coordinates of the widget
    def setCoords(self, x, y):
        if redREnviron.settings["snapToGrid"]:
            x = round(x/10)*10
            y = round(y/10)*10
        self.setPos(x, y)
        self.updateWidgetState()

    # we have to increase the default bounding rect so that we also repaint the name of the widget and input/output boxes
    def boundingRect(self):
        # get the width of the widget's caption
        pixmap = QPixmap(200,40)
        painter = QPainter()
        painter.begin(pixmap)
        width = max(0, painter.boundingRect(QRectF(0,0,200,40), Qt.AlignLeft, self.caption).width() - 60) / 2
        painter.end()
        
        #rect = QRectF(-10-width, -4, +10+width, +25)
        rect = QRectF(QPointF(0, 0), self.widgetSize).adjusted(-10-width, -4, +10+width, +25)
        if not self.ghost:
            try:
                if self.progressBarShown:
                    rect.setTop(rect.top()-20)
                widgetState = self.instance().widgetState
                if widgetState.get("Info", {}).values() + widgetState.get("Warning", {}).values() + widgetState.get("Error", {}).values() != []:
                    rect.setTop(rect.top()-21)
            except: pass
        return rect

    # is mouse position inside the left signal channel
    def mouseInsideLeftChannel(self, pos):
        if self.ghost: return
        if len(self.instance().inputs.getAllInputs()) == 0: return False

        boxRect = QRectF(self.x()-self.edgeSize.width(), self.y() + (self.widgetSize.height()-self.edgeSize.height())/2, self.edgeSize.width(), self.edgeSize.height())
        boxRect.adjust(-10,-10,5,10)       # enlarge the rectangle
        if isinstance(pos, QPointF) and boxRect.contains(pos): return True
        elif isinstance(pos, QRectF) and boxRect.intersects(pos): return True
        else: return False

    # is mouse position inside the right signal channel
    def mouseInsideRightChannel(self, pos):
        if self.ghost: return
        if len(self.instance().outputs.getAllOutputs()) == 0: return False

        boxRect = QRectF(self.x()+self.widgetSize.width(), self.y() + (self.widgetSize.height()-self.edgeSize.height())/2, self.edgeSize.width(), self.edgeSize.height())
        boxRect.adjust(-5,-10,10,10)       # enlarge the rectangle
        if isinstance(pos, QPointF) and boxRect.contains(pos): return True
        elif isinstance(pos, QRectF) and boxRect.intersects(pos): return True
        else: return False
        
    def canConnect(self, outWidget, inWidget):  ## returns a list of what can and can't connect, this should be handled by signal manager.
        if outWidget == inWidget: return
       
        signalManager = orngSignalManager.SignalManager()
        canConnect = inWidget.instance().inputs.matchConnections(outWidget.instance().outputs) #signalManager.canConnect(outWidget, inWidget)
        
        if outWidget == self:
            self.shownRightEdge = canConnect and self.imageRightEdgeG or self.imageRightEdgeR
        else:
            self.shownLeftEdge = canConnect and self.imageLeftEdgeG or self.imageLeftEdgeR

    def resetLeftRightEdges(self):
        self.shownLeftEdge = self.imageLeftEdge
        self.shownRightEdge = self.imageRightEdge
    
    
    # we know that the mouse was pressed inside a channel box. We only need to find
    # inside which one it was
    def getEdgePoint(self, pos):
        if self.mouseInsideLeftChannel(pos):
            return self.getLeftEdgePoint()
        elif self.mouseInsideRightChannel(pos):
            return self.getRightEdgePoint()

    def getLeftEdgePoint(self):
        return QPointF(self.x()- self.edgeSize.width(), self.y() + self.widgetSize.height()/2)

    def getRightEdgePoint(self):
        return QPointF(self.x()+ self.widgetSize.width() + self.edgeSize.width(), self.y() + self.widgetSize.height()/2)

    def getDistToLeftEdgePoint(self, point):
        p = self.getLeftEdgePoint()
        diff = point-p
        return math.sqrt(diff.x()**2 + diff.y()**2)
    
    def getDistToRightEdgePoint(self, point):
        p = self.getRightEdgePoint()
        diff = point-p
        return math.sqrt(diff.x()**2 + diff.y()**2)


    # draw the widget
    def paint(self, painter, option, widget = None):
        if self.isProcessing:
            color = self.canvasDlg.widgetActiveColor
        # elif self.needsProcessing == True:
            # color = Qt.red
        elif self.selected:
            if (self.view.findItemTypeCount(self.canvas.collidingItems(self), CanvasWidget) > 0):       # the position is invalid if it is already occupied by a widget 
                color = Qt.red
            else:                    color = self.canvasDlg.widgetSelectedColor
        

        if self.isProcessing or self.selected:
            painter.setPen(QPen(color))
            painter.drawRect(-3, -3, self.widgetSize.width()+6, self.widgetSize.height()+6)

        painter.drawPixmap(0,0, self.icon.pixmap(self.widgetSize.width(), self.widgetSize.height()))
        # where the edges are painted
        if not self.ghost:
            try:
                if len(self.instance().inputs.getAllInputs()) != 0:    painter.drawPixmap(-self.edgeSize.width(), (self.widgetSize.height()-self.edgeSize.height())/2, self.shownLeftEdge)
                if len(self.instance().outputs.getAllOutputs()) != 0:   painter.drawPixmap(self.widgetSize.width(), (self.widgetSize.height()-self.edgeSize.height())/2, self.shownRightEdge)
            except:
                pass
        # draw the label
        painter.setPen(QPen(QColor(0,0,0)))
        midX, midY = self.widgetSize.width()/2., self.widgetSize.height() + 5
        painter.drawText(midX-200/2, midY, 200, 20, Qt.AlignTop | Qt.AlignHCenter, self.caption)

        yPos = -22
        if self.progressBarValue >= 0 and self.progressBarValue <= 100:
            rect = QRectF(0, yPos, self.widgetSize.width(), 16)
            painter.setPen(QPen(QColor(0,0,0)))
            painter.setBrush(QBrush(QColor(255,255,255)))
            painter.drawRect(rect)

            painter.setBrush(QBrush(QColor(0,128,255)))
            painter.drawRect(QRectF(0, yPos, self.widgetSize.width()*self.progressBarValue/100., 16))
            painter.drawText(rect, Qt.AlignCenter, "%d %%" % (self.progressBarValue))
        
    def addOutLine(self, line):
        self.outLines.append(line)

    def addInLine(self,line):
        self.inLines.append(line)

    def removeLine(self, line):
        if line in self.inLines:
            self.inLines.remove(line)
        elif line in self.outLines:
            self.outLines.remove(line)
        else:
            log.log(1, 9, 1, "Red-R Canvas: Erorr. Unable to remove line")

        self.updateTooltip()


    def setAllLinesFinished(self, finished):
        for line in self.inLines: line.finished = finished
        for line in self.outLines: line.finished = finished


    def updateTooltip(self):
        return
        if self.ghost: return
        string = "<nobr><b>" + self.caption + "</b></nobr><hr>Inputs:<br>"

        # if self.instance.inputs == [] or self.instance.inputs == None: string += "&nbsp; &nbsp; None<br>"
        # else:
            # for signal in self.instance.inputs:
                
                # widgets = self.signalManager.getLinkWidgetsIn(self.instance, signal[0])
                # if len(widgets) > 0:
                    # string += "<nobr> &nbsp; &nbsp; - <b>" + signal[0] + "</b> (from "
                    # for i in range(len(widgets)-1):
                        # string += self.view.doc.getWidgetCaption(widgets[i]) + ", "
                    # string += self.view.doc.getWidgetCaption(widgets[-1]) + ")</nobr><br>"
                # else:
                    # string += "<nobr> &nbsp; &nbsp; - " + signal[0] + "</nobr><br>"

        string = string[:-4]
        string += "<hr>Outputs:<br>"
        # if self.instance.outputs == [] or self.instance.outputs == None: string += "&nbsp; &nbsp; None<br>"
        # else:
            # for signal in self.instance.outputs:
                # widgets = self.signalManager.getLinkWidgetsOut(self.instance, signal[0])
                # if len(widgets) > 0:
                    # string += "<nobr> &nbsp; &nbsp; - <b>" + signal[0] + "</b> (to "
                    # for i in range(len(widgets)-1):
                        # string += self.view.doc.getWidgetCaption(widgets[i]) + ", "
                    # string += self.view.doc.getWidgetCaption(widgets[-1]) + ")</nobr><br>"
                # else:
                    # string += "<nobr> &nbsp; &nbsp; - " + signal[0] + "</nobr><br>"
        string = string[:-4]
        self.setToolTip(string)

    def setProgressBarValue(self, value):
        self.progressBarValue = value
        if value < 0 or value > 100:
            self.updateWidgetState()
        self.canvas.update()
        
    def setNeedsProcessing(self, value):
        if value == True:
            self.needsProcessing = True
        elif value == False:
            self.needsProcessing = False
        self.canvas.update()

    def setProcessing(self, value):
        self.isProcessing = value
        self.canvas.update()
        qApp.processEvents()
##        self.repaintWidget()

# ######################################
# # CANVAS GHOST WIDGET
# ######################################
"""
class GhostWidget(CanvasWidget):  # graphical representation of a ghost widget.  Inherits all of the functions as the CanvasWidget and may override some functions.  This should be a widget with a slightly dimmed appearance.  Clicking will activate the wiget and init an addition of the widget to the canvas
    def __init__(self, signalManager, canvas, view, widgetInfo, defaultPic, canvasDlg, widgetSettings = None, forceInSignals = None, forceOutSignals = None, creatingWidget = None):
        CanvasWidget.__init__(self, signalManager, canvas, view, widgetInfo, defaultPic, canvasDlg, widgetSettings, ghost = True)
        self.setOpacity(0.5)
        self.creatingWidget = creatingWidget
        # put the settings to be a ghost.  This will be removed if the widget is clicked.  In which case data will be sent through the widget as though it were just added to the canvas.
        self.ghost = True
    def convertToCanvasWidget(self):
        self.setOpacity(1)
        self.ghost = False
        m = __import__(self.widgetInfo.fileName)
        self.instance = m.__dict__[self.widgetInfo.widgetName].__new__(m.__dict__[self.widgetInfo.widgetName],
        _owInfo = redREnviron.settings["owInfo"],
        _owWarning = redREnviron.settings["owWarning"],
        _owError = redREnviron.settings["owError"],
        _owShowStatus = redREnviron.settings["owShow"],
        _packageName = self.widgetInfo.packageName)
        #_settingsFromSchema = widgetSettings)
        self.instance.__dict__['_widgetInfo'] = self.widgetInfo
        
        self.instance.__init__(signalManager = self.signalManager)
        
        self.instance.ghost = False
        
        self.canvasDlg.schema.signalManager.addWidget(self.instance)
        self.canvasDlg.schema.addLine(self.creatingWidget, self)
        self.instance.setCaption(self.caption)
            """
class MyCanvasText(QGraphicsSimpleTextItem):
    def __init__(self, canvas, text, x, y, flags=Qt.AlignLeft, bold=0, show=1):
        QGraphicsSimpleTextItem.__init__(self, text, None, canvas)
        self.setPos(x,y)
        self.setPen(QPen(Qt.black))
        self.flags = flags
        if bold:
            font = self.font();
            font.setBold(1);
            self.setFont(font)
        if show:
            self.show()

    def paint(self, painter, option, widget = None):
        #painter.resetMatrix()
        painter.setPen(self.pen())
        painter.setFont(self.font())

        xOff = 0; yOff = 0
        rect = painter.boundingRect(QRectF(0,0,2000,2000), self.flags, self.text())
        if self.flags & Qt.AlignHCenter: xOff = rect.width()/2.
        elif self.flags & Qt.AlignRight: xOff = rect.width()
        if self.flags & Qt.AlignVCenter: yOff = rect.height()/2.
        elif self.flags & Qt.AlignBottom:yOff = rect.height()
        #painter.drawText(self.pos().x()-xOff, self.pos().y()-yOff, rect.width(), rect.height(), self.flags, self.text())
        painter.drawText(-xOff, -yOff, rect.width(), rect.height(), self.flags, self.text())
        