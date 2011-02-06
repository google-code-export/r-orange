"""

############ R INSTALL#################
cp -R /Library/Frameworks/R.framework.bak /Applications/Red-R.app/R

find ./ -name *.dylib -or -name *.so  -exec install_name_tool -change /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libgfortran.2.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libgfortran.2.dylib {} \;
find ./ -name *.dylib -or -name *.so  -exec install_name_tool -change /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libreadline.5.2.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libreadline.5.2.dylib {} \;
find ./ -name *.dylib -or -name *.so  -exec install_name_tool -change /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libRblas.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.dylib {} \;
find ./ -name *.dylib -or -name *.so -exec install_name_tool -change /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libR.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libR.dylib {} \;
find ./ -name *.dylib -or -name *.so -exec install_name_tool -change /Library/Frameworks/R.framework/Versions/2.11/Resources/lib/libRlapack.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRlapack.dylib {} \;

install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libR.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libR.dylib
install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.0.dylib
install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.dylib
install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRblas.vecLib.dylib
install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libRlapack.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libRlapack.dylib

install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libgcc_s.1.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libgcc_s.1.dylib
install_name_tool -id  /Applications/Red-R.app/R/R.framework/Resources/lib/libgfortran.2.dylib /Applications/Red-R.app/R/R.framework/Resources/lib/libgfortran.2.dylib
##########################Python INSTALL###################################
python2.6 setup.py build --r-home=/Applications/Red-R.app/R/R.framework/Resources/
import os
os.environ['R_HOME'] = '/Applications/Red-R.app/R/R.framework/Resources'
import rpy3.robjects

rm -rf /Users/anupparikh/redr/trunk/mac/rpy3
cp -R /Users/anupparikh/redr/trunk/rpy3-setup/build/lib.macosx-10.5-i386-2.6/rpy3 /Users/anupparikh/redr/trunk/mac/

"""
import os, sys, shutil, re

#print sys.argv
#base = 'C:/Users/anup/Documents/red/develop/makeInstallers/code/red-trunk'
base = sys.argv[1]


sys.argv = ['createCompiledCode.py','py2app']
from distutils.core import setup
import py2app,shutil


##cleanup
shutil.rmtree('build',True)
shutil.rmtree(os.path.join(base,'dist'),True)


#sys.path.insert(0, '/Users/anup/redr/trunk')
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base,'canvas'))
# sys.path.insert(0, os.path.join(base,'canvas','rpy'))
#print sys.path
info = {}

import glob
files = [os.path.basename(x).split('.')[0] for x in glob.glob(os.path.join(base,'canvas','*.py'))]
#print files
setup(name="Red-R",
      version="0.1",
      author="Anup  Parikh",
      author_email="anup.parikh@gmail.com",
      url="http://www.red-r.org",
      license="GNU General Public License (GPL)",
      app=[os.path.join(base,"canvas","red-RCanvas.pyw")],
      #data_files = dataFiles,
      options={"py2app": {
      "argv_emulation":1,
      "iconfile": '/Users/anupparikh/redr/trunk/canvas/icons/redR.icns',
      #"prefer_ppc":1,
      "dist_dir": os.path.join(base,'dist'),
      "site_packages":1,
      "excludes": ['libraries'],
      "includes": ["sip",'PyQt4', 'OWColorPalette','docutils','Image', 'OWGraphTools','PyQt4.QtNetwork','PyQt4', 'PyQt4.Qwt5','PyQt4.QtSvg','PyQt4.Qwt5'] + files
      #
      }})

#shutil.rmtree(os.path.join(base,'dist','docutils'),True)
shutil.copytree('/Users/anupparikh/redr/R/',os.path.join(base,'dist','Red-R.app','R'))
shutil.copytree(os.path.join(base,'libraries'),
os.path.join(base,'dist','Red-R.app','Contents','libraries')) 

shutil.copytree(os.path.join(base,'canvas','icons'),
os.path.join(base,'dist','Red-R.app','Contents','canvas','icons')) 

shutil.copytree(os.path.join(base,'mac'),
os.path.join(base,'dist','Red-R.app','Contents','mac')) 

shutil.copytree(os.path.join(base,'includes'),
os.path.join(base,'dist','Red-R.app','Contents','includes')) 

import datetime
d = datetime.datetime.now()
svn = os.popen("svnversion %s" % base).read()
m = re.match('(\d+)M',svn)
svnVersion =  m.group(1)
fh = open(os.path.join(base,'dist','Red-R.app','Contents','version.txt'),'w')
fh.write("""!define DATE "%s"
!define SVNVERSION "%s"
!define NAME "Red-R"
!define REDRVERSION "%s"
!define TYPE "mac"
!define RVERSION "R-2.11.1"
""" % (d.strftime('%Y.%m.%d'), svnVersion,'1.85'))
fh.close()

shutil.copyfile(os.path.join(base,'licence.txt'),os.path.join(base,'dist','Red-R.app','Contents','licence.txt'))



shutil.copytree('/Users/anupparikh/redr/installIncludes/qt_menu.nib',
os.path.join(base,'dist','Red-R.app','Contents','Resources','qt_menu.nib')) 

shutil.copyfile('/Users/anupparikh/redr/installIncludes/redR.icns',
os.path.join(base,'dist','Red-R.app','Contents','Resources','PythonApplet.icns')) 



os.system('rm -rf /Applications/Red-R.app/Contents')
os.system('cp -R /Users/anupparikh/redr/trunk/dist/Red-R.app/Contents /Applications/Red-R.app/')
os.system('ln -s /Users/anupparikh/redr/trunk/dist/Red-R.app/Contents/libraries /Users/anupparikh/redr/trunk/dist/Red-R.app/Contents/Resources/libraries')
os.system('cp /usr/local/lib/libgcc_s.1.dylib /Applications/Red-R.app/Contents/Frameworks/libgcc_s.1.dylib')


