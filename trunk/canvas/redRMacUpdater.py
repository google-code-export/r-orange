import tarfile, sys,os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
app = QApplication(sys.argv)

try:
    zfile = tarfile.open(sys.argv[1], "r:gz" )
    zfile.extractall(sys.argv[2])
    zfile.close()
    
    mb = QMessageBox('Red-R Updated', "Red-R has been updated'", 
                    QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                    QMessageBox.NoButton, QMessageBox.NoButton)

except:
    mb = QMessageBox('Red-R Updated', "There was an Error in updating Red-R.\n\n%s" % sys.exc_info()[0], 
                    QMessageBox.Information, QMessageBox.Ok | QMessageBox.Default, 
                    QMessageBox.NoButton, QMessageBox.NoButton)

app.setActiveWindow(mb)
mb.setFocus()
mb.show()
app.exit(0)
#mb.exec_()



sys.exit(app.exec_())

os.remove(sys.argv[1])