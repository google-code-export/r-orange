import re, sys, os.path, glob

test = sys.argv[2]
test = test == 'True'
if os.path.isdir(sys.argv[1]):
    files = glob.glob(sys.argv[1]+'/*.py')
else:
    files = [sys.argv[1]]

for n in files:
    print '\n\n####################%s######################\n\n' % n
    file = open(n,'r').readlines()

    
    findQTwidgets = 'from libraries.(\w+).qtWidgets.(\w+) import (\w+)( as (\w+))?'
    findsignals = 'from libraries.(\w+).signalClasses.(\w+) import (\w+)( as (\w+))?'
    qtWidgets = {}
    signals = {}
    for line in file:
        # print line
        m = re.search(findQTwidgets,line)
        # if m: 
            # print m.group(1)
            # print m.group(2)
            # print m.group(3)
            # print m.group(4)
            # print m.group(5)
            
        if m and not re.search('^\s*#',line):
            if m.group(5):
                qtWidgets[m.group(5)] = 'redRGUI.%s.%s' % (m.group(1),m.group(2))
            else:
                qtWidgets[m.group(3)] = 'redRGUI.%s.%s' % (m.group(1),m.group(2))
            
        m = re.search(findsignals,line)
        # if m: 
            # print m.group(1)
            # print m.group(2)
            # print m.group(3)
            # print m.group(4)
            # print m.group(5)
            
        if m and not re.search('^\s*#',line):
            if m.group(5):
                signals[m.group(5)] = 'signals.%s.%s' % (m.group(1),m.group(2))
            else:
                signals[m.group(3)] = 'signals.%s.%s' % (m.group(1),m.group(2))
            
    #print widgets
    #print test
    if not test:
        # print '#############open'
        f=open(n,'w')
    otherQTWidgets = {'redRButton':'redRGUI.base.button',
'redRCheckBox':'redRGUI.base.checkBox',
'redRComboBox':'redRGUI.base.comboBox',
'redRCommitButton':'redRGUI.base.commitButton',
'redRDialog':'redRGUI.base.dialog',
'redRFileNamesComboBox':'redRGUI.base.fileNamesComboBox',
'redRFilterTable':'redRGUI.base.filterTable',
'redRGraphicsView':'redRGUI.base.graphicsView',
'redRGroupBox':'redRGUI.base.groupBox',
'redRLineEdit':'redRGUI.base.lineEdit',
'redRLineEditHint':'redRGUI.base.lineEditHint',
'redRListBox':'redRGUI.base.listBox',
'redRRadioButtons':'redRGUI.base.radioButtons',
'redRRFormulaEntry':'redRGUI.base.RFormulaEntry',
'redRRtable':'redRGUI.base.Rtable',
'redRScrollArea':'redRGUI.base.scrollArea',
'redRSearchDialog':'redRGUI.base.SearchDialog',
'redRSeparator':'redRGUI.base.separator',
'redRSpinBox':'redRGUI.base.spinBox',
'redRSplitter':'redRGUI.base.splitter',
'redRStatusLabel':'redRGUI.base.statusLabel',
'redRTable':'redRGUI.base.table',
'redRTabWidget':'redRGUI.base.tabWidget',
'redRTextEdit':'redRGUI.base.textEdit',
'redRTreeWidget':'redRGUI.base.treeWidget',
'redRTreeWidgetItem':'redRGUI.base.treeWidgetItem',
'redRWebViewBox':'redRGUI.base.webViewBox',
'redRWidgetBox':'redRGUI.base.widgetBox',
'redRWidgetLabel':'redRGUI.base.widgetLabel',
'redRZoomSelectToolbar':'redRGUI.base.zoomSelectToolbar'}
    for line in file:
        #import redRGUI|import redRGUI, signals|import signals|
        if re.search(r'%s|%s|import libraries.base.signalClasses as signals' %(
        findQTwidgets,findsignals),line): continue
        if re.search(r'from OWRpy import \*',line):
            line += 'import redRGUI, signals\n'
            
        for s,r in qtWidgets.items():
            # print s,r
            if re.search(r'%s\s*\(' % s,line):
                line = re.sub(r'%s\s*\(' % s, '%s(' % r,line)

        for s,r in signals.items():
            # print s,r
            if re.search(r'%s' % s,line):
                line = re.sub(r'%s' % s, '%s' % r,line)
        
        for s,r in otherQTWidgets.items():
            if re.search(r'%s\s*\(' % s,line,re.IGNORECASE):
                line = re.sub('(?i)%s\s*\(' % s, '%s(' % r,line,re.IGNORECASE)
        
        m = re.search(r'signals\.(\w+)\.(\w+)',line)
        if m and m.group(1) == m.group(2):
            line = re.sub(r'signals\.(\w+)\.(\w+)', 'signals.base.%s' % m.group(1),line)
        
        if test:
            print line.rstrip()
        else:
            f.write(line)
    if not test:
        f.close()
        







