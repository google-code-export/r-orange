import os, subprocess, sys
baseDir = 'C:/Users/anup/Documents/red/develop/makeInstallers/installerCode'
redRDir = 'C:/Users/anup/Documents/red/develop/makeInstallers/code/Version1.85_gold'

runCompile = sys.argv[1]
runInstaller = sys.argv[2]
# runupload = sys.argv[3]

cmd = 'python createCompiledCode.py py2exe %s' % redRDir 
if runCompile == '1':
    print 'Running: ' + cmd
    os.system(cmd)


makensisw = "C:/Program Files (x86)/NSIS/makensis.exe"
##########compiled version
defines = {}
defines['REDRVERSION1'] =  "1.85b"
defines['Red-RDIR']=       redRDir
defines['RDIRECTORY'] =    "C:/Users/anup/Documents/red/develop/makeInstallers/includes/R-2.11.1"
defines['RVER']=           "R-2.11.1"
defines['OUTPUTDIR'] =     "C:/Users/anup/Documents/red/develop/makeInstallers/installer"

params = ''
for k,v in defines.items():
    params+= '/D"%s=%s" ' % (k,v)


if runInstaller =='1':

    cmd = '"%s" /X"SetCompressor /FINAL /SOLID lzma" %s Red-R-compiled.nsi' % (makensisw,params)
    print 'Running installer: ' + cmd
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
    print p
    cmd = '"%s" /X"SetCompressor /FINAL /SOLID lzma" %s Red-R-compiled-updater.nsi' % (makensisw,params)
    print 'Running updated: ' + cmd
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
    print p

    # cmd = 'python %s/googlecode_upload.py -s "Compiled version" -p r-orange -u anup.parikh -w VF6NG8Mr3Nc6 %s' % (baseDir, compiledVersion.replace('\\','/'))
    # if runupload== '1':
        # print 'Running: ' + cmd
        # subprocess.call(cmd)

