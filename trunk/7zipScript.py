import os, sys
os.chdir('C:/Program Files/7-zip')
libDir = 'C:/Python26/Lib/site-packages/RedRTrunk/libraries'
packages = os.listdir(libDir)

for p in packages:
    if not os.path.isdir(os.path.join(libDir, p)): continue
    print p
    call = '7z a -tzip -xr!*.svn* -xr!*.pyc -xr!*.pyo C:\Python26\Lib\site-packages\RedRTrunk\libraries\%s\%s.zip C:\Python26\Lib\site-packages\RedRTrunk\libraries\%s\*' % (p,p,p)
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

#7z a -tzip -xr!*.svn* -xr!*.pyc -xr!*.pyo -xr!*strawberryPerl* -xr!*RedRmatplotlib* C:\Python26\Lib\site-packages\R.zip C:\Python26\Lib\site-packages\R\R-2.11.1\*