# zipPackage.py,  requires that the function zip is enabled on the machine

import sys, os, zipfile, glob

packageName = sys.argv[1]

thisZip = zipfile.ZipFile(os.path.join('../libraries', '%s.zip' % packageName), 'w')
#for f in glob.glob(os.path.join('../libraries', packageName, '*', '*.py')):
    #thisZip.write(f)

#for f in glob.glob(os.path.join('../libraries', packageName, '*', '*.xml')):
    #thisZip.write(f)
    
def zipdir(path, arch, exclude):
    paths = os.listdir(path)
    for p in paths:
        p = os.path.join(path, p)
        if os.path.isdir(p) and ('.svn' not in p):
            zipdir(p, arch, exclude)
        elif os.path.splitext(p)[1] not in exclude:
            archName = os.path.relpath(p, os.path.join('../libraries', packageName))
            arch.write(p, archName)
            print "Wrote to archive: %s as %s" % (p, archName)

def zippackage(path, outpath, exclude):
    # Create a ZipFile Object primed to write
    archive = zipfile.ZipFile(outpath, 'w')
    # Recurse or not, depending on what path is
    if os.path.isdir(path):
        zipdir(path, archive, exclude)
    else:
        archName = os.path.relpath(path, os.path.join('../libraries', packageName))
        archive.write(path, archName)
        print "Wrote to archive: %s as %s" % (path, archName)
    archive.close()
    
outpath = os.path.join('../libraries', '%s.zip' % packageName)
packagePath = os.path.join('../libraries', packageName)

zippackage(packagePath, outpath, ['.pyc', '.svn'])
print 'Your file is writen to %s' % os.path.join('..', 'libraries', '%s.zip' % packageName)