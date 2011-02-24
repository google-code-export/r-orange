import os,re
AppDir = '/Applications/Red-R.app'
version = {}
f = open(os.path.join(AppDir,'Contents','version.txt'),'r')
file = f.readlines()
f.close()
import re
for i in file:
    m = re.search('!define\s(\S+)\s"(.*)"',i)
    version[m.group(1)] = m.group(2)

os.chdir('/Applications/')

cmd = 'tar cvfz /Users/anupparikh/redr/installers/%(NAME)s.%(TYPE)s-%(DATE)s.r%(SVNVERSION)s.tar.gz Red-R.app' % version
print cmd
#os.system(cmd)

os.chdir('/Applications/Red-R.app')
updateFiles = [
'Contents/MacOS',
'Contents/libraries',
#'Contents/mac',
'Contents/canvas',
'Contents/canvas',
'Contents/version.txt',
'Contents/licence.txt',
'Contents/Resources/red-RCanvas.pyw',
'Contents/Resources/lib/python2.6/site-packages.zip',
]
version.update({'files': ' '.join(updateFiles)})
cmd = 'tar cvfz /Users/anupparikh/redr/installers/%(NAME)s.%(TYPE)s.update-%(DATE)s.r%(SVNVERSION)s.tar.gz %(files)s' % version
print cmd
os.system(cmd)




#os.system ('/Users/anupparikh/redr/installIncludes/googlecode_update.py ')