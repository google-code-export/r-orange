#update the orange canvas and installed widget packages


import pysvn
import os, urllib, sys
import md5, cPickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#import orange, user, orngMisc
import orngEnviron

#QMessageBox.question(None, 'RedR Update','Do you wish to update RedR?', QMessageBox.Yes, QMessageBox.No)

#class RedRUpdate():
def start(lastRevproplist):

    
    
    versionNumber = 'Version1.0'

    svnLoc = 'http://r-orange.googlecode.com/svn/trunk/'

    client = pysvn.Client()
    newRevproplist = client.revproplist(svnLoc)[1]

    
    canvasDirName = os.path.realpath(orngEnviron.directoryNames["canvasDir"])
    widgetDirName = os.path.realpath(orngEnviron.directoryNames["widgetDir"])
    
    
    if lastRevproplist != newRevproplist:
        res = QMessageBox.question(None, 'RedR Update','Do you wish to update RedR?', QMessageBox.Yes, QMessageBox.No)
    

        if res == QMessageBox.Yes:
            #trySVNUpdate(svnLoc, os.path.realpath(orngEnviron.directoryNames["orangeDir"]))
            CanvasSuccess = trySVNUpdate(svnLoc + 'OrangeCanvas/', canvasDirName)
            


        res2 = QMessageBox.question(None, 'RedR Update', 'Do you wish to update your packages?', QMessageBox.Yes, QMessageBox.No)
        if res2 == QMessageBox.Yes:
            #define the package folders
            movie = MoviePlayer()
            movie.start()
            client = pysvn.Client()
            client.export(svnLoc+'OrangeWidgets/', widgetDirName, force = True, recurse = False)
            failed = []
            somethingFailed = 0
            for package in os.listdir(widgetDirName):
                if '.py' in package or '.svn' in package: pass
                else:
                    try:
                        client.export(svnLoc+'OrangeWidgets/%s' % package, widgetDirName+'\%s' % package, force = True)
                    except:
                        failed.append(package)
                        somethingFailed = 1
            movie.stop()
            if somethingFailed == 1:
                QMessageBox.information(None, 'RedR Update', 'The following widgets or packages failed: \n%s' % '\n  '.join(failed), QMessageBox.Ok + QMessageBox.Default)
                        
        #else: return
    return newRevproplist

def trySVNUpdate(loc, canDir, useSubdir = False):
    movie = MoviePlayer()
    movie.start()
    try:
        client = pysvn.Client()
        client.export(loc, canDir, force = True, recurse = useSubdir)
        return 1
    except:
        movie.stop()
        res = QMessageBox.question(None, 'RedR Update', 'There was a problem connecting to the server,\n please check that you have a working internet connection and can connect to\n %s. \n\n Would you like to try again?' % loc, QMessageBox.Yes, QMessageBox.No)
        
        if res == QMessageBox.Yes:
            trySNVUpdate(loc, canDir)
        else: return
    movie.stop()
    



class MoviePlayer(QWidget): 
    def __init__(self, parent=None): 
        QWidget.__init__(self, parent) 
        # setGeometry(x_pos, y_pos, width, height)
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle("QMovie to show animated gif")
        
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
        movie = QMovie("C:\\Python25\\Lib\\site-packages\\orange\\OrangeCanvas\\ajax-loader.gif", QByteArray(), self)
        label = QLabel()
        label.setMovie(movie)
        #QMessageBox.information(None, 'RedR', , QMessageBox.Ok)
        self.movie = QMovie("C:\\Python25\\Lib\\site-packages\\orange\\OrangeCanvas\\ajax-loader.gif", QByteArray(), self) 
        self.movie.setCacheMode(QMovie.CacheAll) 
        self.movie.setSpeed(100) 
        self.movie_screen.setMovie(self.movie) 
        self.movie.start()
        
    def start(self):
        """sart animnation"""
        self.movie.start()
        
    def stop(self):
        """stop the animation"""
        self.movie.stop()
        