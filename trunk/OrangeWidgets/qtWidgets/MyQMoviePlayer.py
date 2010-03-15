from PyQt4.QtCore import *
from PyQt4.QtGui import *
import orngEnviron, os

class MyQMoviePlayer(QWidget):
    def __init__(self, parent = None, file = None, title = None):
        QWidget.__init__(self, parent)
        self.setGeometry(200, 200, 400, 400)
        if not title:
            self.setWindowTitle('Movie')
        else: self.setWindowTitle(title)
        
        self.movie_screen = QLabel()
        self.movie_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.movie_screen.setAlignment(Qt.AlignCenter)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.movie_screen)
        self.setLayout(main_layout)
        
        if not file:
            self.movie = QMovie(os.path.abspath(orngEnviron.directoryNames['canvasDir'] + '/ajax-loader.GIF'), QByteArray(), self)
        else: self.movie = QMovie(file, QByteArray(), self)
        
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.show()
        self.movie.start()
        
    