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
version.update({'AppDir':AppDir})
cmd = 'tar cvfz /Users/anupparikh/redr/installers/%(NAME)s.%(TYPE)s-%(DATE)s.r%(SVNVERSION)s.tar.gz Red-R.app' % version
print cmd
os.system(cmd)
#os.system ('/Users/anupparikh/redr/installIncludes/googlecode_update.py ')