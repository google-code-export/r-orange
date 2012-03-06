import re, sys, os.path, glob

test = sys.argv[2]
if os.path.isdir(sys.argv[1]):
    files = glob.glob(sys.argv[1]+'/*.py')
else:
    files = [sys.argv[1]]

for n in files:
    print '\n\n####################%s######################\n\n' % n
    file = open(n,'r').readlines()

    findRedR = 'redRGUI.(\w+)(\(|\.)'
    widgets = {}
    for line in file:
        m = re.search(findRedR,line)
        if m and not re.search('^\s+#',line):
            widgets[m.group(1)] = 1
    #print widgets.keys()
    if not test:
        f=open(n,'w')
    for x in widgets.keys():
        toImport = 'from libraries.base.qtWidgets.%s import %s as redR%s\n' % (x,x,x)
        if test:
            print toImport
        else:
            f.write(toImport)

    for line in file:
        m = re.search(findRedR,line)
        if m:
            line = line.replace('redRGUI.','redR')
        
        if test:
            print line.rstrip()
        else:
            f.write(line)
    if not test:
        f.close()
        
