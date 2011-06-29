# zipPackage.py,  requires that the function zip is enabled on the machine

import sys, os, zipfile, glob

packageName = sys.argv[1]

thisZip = zipfile.ZipFile(os.path.join('../libraries', '%s.zip' % packageName), 'w')
#for f in glob.glob(os.path.join('../libraries', packageName, '*', '*.py')):
    #thisZip.write(f)

#for f in glob.glob(os.path.join('../libraries', packageName, '*', '*.xml')):
    #thisZip.write(f)

for f in glob.glob(os.path.join('../libraries', packageName, '*')):
    if os.path.splitext(f)[1] in ['.pyc']: continue
    thisZip.write(f, f.replace('../libraries/%s'%packageName, ''))
    
print 'Your file is writen to %s' % os.path.join('../libraries', '%s.zip' % packageName)