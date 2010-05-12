## a script to install biopython on a distribution of Red-R.  For the moment we shall use the full distribution however, this need not be the case.  First we will need to download the installer if this is a windows machine, otherwise we will place a kind message that the user should install biopython themselves and press the OK button to proceed.  Then we should be done.

import sys, os, redREnviron
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def haveBiopython:
    try:
        import Bio  # doesn't fail if we have biopython
        return True
    except:
        QMessageBox.information(None, 'File Download','It looks like something went wrong.  Please install again.',  QMessageBox.Ok + QMessageBox.Default)
        return False
### check if Biopython already exists  ### will do later
if sys.platform=="win32":

    try:
        import Bio
    except:
    ## we have a windows machine and all is well
        import webbrowser
        webbrowser.open_new_tab('http://biopython.org/DIST/biopython-1.53.win32-py2.6.exe')
        QMessageBox.information(None, 'File Download','Please Download and install the file on this link and click OK to proceed',  QMessageBox.Ok + QMessageBox.Default)
        
        ### if the file is not there we throw an error.
        gotBiopython = haveBiopython()
        if gotBiopython:
            QMessageBox.information(None, 'File Download','Thanks, now that did\'t hurt a bit did it?',  QMessageBox.Ok + QMessageBox.Default)
            return True
            
        else:
            return False
        
else:
    import webbrowser
    webbrowser.open_new_tab('http://biopython.org/wiki/Download')
    QMessageBox.information(None, 'File Download','It doesn\'t look like you have a Windows machine, please get the appropriate version of Biopython to continue.',  QMessageBox.Ok + QMessageBox.Default)
    
    return True
