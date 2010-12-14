import os
import redREnviron
from PyQt4.QtCore import *
from PyQt4.QtGui import *

canvasPicsDir  = os.path.join(redREnviron.directoryNames["canvasDir"], "icons")

#Red-R icons
canvasIconName  = os.path.join(canvasPicsDir, "CanvasIcon.png")
redRLogo = os.path.join(redREnviron.directoryNames["canvasDir"], "icons", "splash.png")

#toolbar icons
fileNewIcon  = os.path.join(canvasPicsDir, "doc.png")
outputIcon = os.path.join(canvasPicsDir, "output.png")
openFileIcon = os.path.join(canvasPicsDir, "open.png")
saveFileIcon = os.path.join(canvasPicsDir, "save.png")
reloadIcon = os.path.join(canvasPicsDir, "update1.png")
showAllIcon = os.path.join(canvasPicsDir, "upgreenarrow.png")
closeAllIcon = os.path.join(canvasPicsDir, "downgreenarrow.png")
textIcon = os.path.join(canvasPicsDir, "text.png")
printIcon= os.path.join(canvasPicsDir, "print.png")
updateIcon= os.path.join(canvasPicsDir, "update.png")
exitIcon = os.path.join(canvasPicsDir, "exit.png")

#widget icons
defaultPic = os.path.join(redREnviron.directoryNames['picsDir'], "Unknown.png")
defaultBackground = os.path.join(redREnviron.directoryNames['picsDir'], "frame.png")
iconSizeList = [16, 32, 40]

errorIcon = os.path.join(canvasPicsDir, "information.png")
warningIcon = os.path.join(canvasPicsDir, "warning.png")
informationIcon = os.path.join(canvasPicsDir, "error.png")
widgetIcons = {"Info": informationIcon, "Warning": warningIcon, "Error": errorIcon}

#Colors
widgetSelectedColor = QColor(0, 255, 0)
widgetActiveColor   = QColor(0, 0, 255)
lineColor           = QColor('#009929')
dirtyLineColor = QColor('#990000')
noDataLineColor = QColor('#999999')
#QT Style

QtStyles = [unicode(n) for n in QStyleFactory.keys()]

