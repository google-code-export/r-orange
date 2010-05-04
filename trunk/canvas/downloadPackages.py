# download new packages for the RedR canvasDir
#Kyle R Covington


import pysvn
import os, urllib, sys
import md5, cPickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import redREnviron

#QMessageBox.question(None, 'RedR Update','Do you wish to update RedR?', QMessageBox.Yes, QMessageBox.No)

#class RedRUpdate():
def start(lastRevproplist, versionNumber, silent = True):

    
    svnLoc = 'http://r-orange.googlecode.com/svn/branches/' + versionNumber +'/OrangeWidgets/'
    
    try:
        client = pysvn.Client()
        
        #if 'trunk' not in svnLoc:
        lists = client.ls(svnLoc)
        newPackageList = []
        tfile = redREnviron.directoryNames['redRDir'] + '\\tagsSystem\\tabsList.txt'
        f = open(tfile, 'r')
        mainTabs = f.read().split('\n')
        f.close()
        for item in lists:
            if '.py' in item: pass
            elif item in mainTabs: pass
            else:
                newPackageList.append(item)
                
        
        if newPackageList != []:
            np = QMessageBox(None, 'New Package Download', 'The following packages are available for download.\nPleas select desired packages and press OK', QMessageBox.Cancel, QMessageBox.Ok)
            packageList = QListWidget(None)
            packageList.addItems(newPackageList)
            packageList.setSelectionMode(QAbstractItemView.ExtendedSelection)
            np.layout().addWidget(packageList)
            
            if np = QMessageBox.Ok:
                for item in packageList.selectedItems():
                    text = item.text()
                    client.export(svnLoc+'/OrangeWidgets/'+text+'/', widgetDirName, force = True, recurse = True)
                    f = open(redREnviron["tagsDir"]+'/tabsList.txt', 'a')
                    f.write('\n'+text)
        
    except:
        return

    
    canvasDirName = os.path.realpath(redREnviron.directoryNames["canvasDir"])
    widgetDirName = os.path.realpath(redREnviron.directoryNames["widgetDir"])
    
    
    if lastRevproplist != newRevproplist:
        res = QMessageBox.question(None, 'RedR Update','New updates are available.\nDo you wish to update RedR?', QMessageBox.Yes, QMessageBox.No)
    

        if res == QMessageBox.Yes:
            #trySVNUpdate(svnLoc, os.path.realpath(redREnviron.directoryNames["redRDir"]))
            CanvasSuccess = trySVNUpdate(svnLoc + '/OrangeCanvas/', canvasDirName)
        else:
            res3 = QMessageBox.question(None, 'RedR Update', 'Do you wish to apply these updates in the future?', QMessageBox.Yes, QMessageBox.No)
            if res3 == QMessageBox.No:
                return newRevproplist, versionNumber
            else:
                return lastRevproplist, versionNumber
            


        res2 = QMessageBox.question(None, 'RedR Update', 'Do you wish to update your packages?', QMessageBox.Yes, QMessageBox.No)
        if res2 == QMessageBox.Yes:
            #define the package folders
            movie = MoviePlayer()
            movie.show()
            movie.start()
            client = pysvn.Client()
            client.export(svnLoc+'/OrangeWidgets/', widgetDirName, force = True, recurse = False)
            failed = []
            somethingFailed = 0
            for package in os.listdir(widgetDirName):
                if '.py' in package or '.svn' in package: pass
                else:
                    try:
                        client.export(svnLoc+'/OrangeWidgets/%s' % package, widgetDirName+'\%s' % package, force = True)
                    except:
                        failed.append(package)
                        somethingFailed = 1
            movie.stop()
            movie.hide()
            if somethingFailed == 1:
                QMessageBox.information(None, 'RedR Update', 'The following widgets or packages failed: \n%s' % '\n  '.join(failed), QMessageBox.Ok + QMessageBox.Default)
                        
        else: 
            res3 = QMessageBox.question(None, 'RedR Update', 'Do you wish to apply these updates in the future?', QMessageBox.Yes, QMessageBox.No)
            if res3 == QMessageBox.No:
                return newRevproplist, versionNumber
                
            else:
                return lastRevproplist, versionNumber
    else:
        if not silent:
            QMessageBox.information(None, 'RedR Update', 'No updates are available since your last update.', QMessageBox.Ok)
    return newRevproplist, versionNumber

def trySVNUpdate(loc, canDir, useSubdir = False):
    movie = MoviePlayer()
    movie.show()
    movie.start()
    try:
        client = pysvn.Client()
        client.export(loc, canDir, force = True, recurse = useSubdir)
        return 1
    except:
        movie.stop()
        movie.hide()
        # res = QMessageBox.question(None, 'RedR Update', 'There was a problem connecting to the server,\n please check that you have a working internet connection and can connect to\n %s. \n\n Would you like to try again?' % loc, QMessageBox.Yes, QMessageBox.No)
        
        # if res == QMessageBox.Yes:
            # trySNVUpdate(loc, canDir)
        # else: return
    movie.stop()
    movie.hide()



class MoviePlayer(QWidget): 
    def __init__(self, parent=None): 
        QWidget.__init__(self, parent) 
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(20, 20, 20, 20)
        self.setWindowTitle("Please wait while RedR processes.")
        
        # set up the movie screen on a label
        self.movie_screen = QLabel()
        # expand and center the label 
        self.movie_screen.setSizePolicy(QSizePolicy.Expanding, 
            QSizePolicy.Expanding)        
        self.movie_screen.setAlignment(Qt.AlignCenter) 

        main_layout = QVBoxLayout() 
        main_layout.addWidget(self.movie_screen)
        self.setLayout(main_layout) 
                
        # use an animated gif file you have in the working folder
        # or give the full file path
        #movie = QMovie("C:\\Python25\\Lib\\site-packages\\orange\\OrangeCanvas\\ajax-loader.gif", QByteArray(), self)
        #label = QLabel()
        #label.setMovie(movie)
        #QMessageBox.information(None, 'RedR', , QMessageBox.Ok)
        self.movie = QMovie("C:\\Python25\\Lib\\site-packages\\orange\\OrangeCanvas\\ajax-loader.gif", QByteArray(), self) 
        self.movie.setCacheMode(QMovie.CacheAll) 
        self.movie.setSpeed(150) 
        self.movie_screen.setMovie(self.movie) 
        self.movie.start()
        
    def start(self):
        """sart animnation"""
        self.movie.start()
        
    def stop(self):
        """stop the animation"""
        self.movie.stop()
        