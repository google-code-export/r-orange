import os, sys
#os.chdir('C:/Program Files/7-zip')
libDir = sys.argv[1]
packages = os.listdir(libDir)
currentPath = os.getcwd()
print packages
for p in packages: 
    print p
    os.chdir(currentPath)
    if not os.path.isdir(os.path.join(libDir, p)): 
        continue 
    if not os.path.exists(os.path.join(libDir, p, 'package.xml')): 
        continue 
        
    
    os.chdir(os.path.join(libDir,p))
    zipName = '%s.zip' % p
    try:
        os.remove(zipName)
    except:
        pass
    call = '7z a -tzip -xr!*.svn* -xr!*.pyc -xr!*.pyo %s *' % p
    print call
    os.system(call)

# affy
# doseResponse
# maptools
# NeuralNet
# pls
# RedRLME4
# RedRmatplotlib
# ROCCurves
# rsqlitedataframe
# survival

## http://www.red-r.org/packages/Red-R-1.75/upload.php