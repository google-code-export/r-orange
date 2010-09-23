; Include section
!include "MUI.nsh"


;General


;--------------------------------
; Defines
!define Red-RDIR C:/Users/anup/Documents/red/develop/makeInstallers/code/Version1.80/
!define OUTPUTDIR C:\Users\anup\Documents\red\develop\makeInstallers\installer 
!define REDRVERSION1 "1.80"

!define RVER "R-2.9.1"
;;; The directory of a blank R so that we don't have to deal with licence terms of R
!define RDIRECTORY C:\Users\anup\Documents\red\develop\makeInstallers\includes\R-2.9.1 

!define LICENSE ${Red-RDIR}\licence.txt 

!define INCLUDES C:\Users\anup\Documents\red\develop\makeInstallers\includes
!define PYFILENAME python-2.6.5.msi
!define PYWINFILENAME pywin32-214.win32-py2.6.exe
!define NUMPYFILE numpy-1.3.0-win32-superpack-python2.6.exe
!define PYQTFILE PyQt-Py2.6-gpl-4.5.4-1.exe
!define PYQWTFILE PyQwt5.2.0-Python2.6-PyQt4.5.4-NumPy1.3.0-1.exe
!define PILFILE PIL-1.1.7.win32-py2.6.exe
!define DOCUTILS docutils ; name of the docutils file that we will run the setup.py file from 


; !define RPYFILENAME C:\Python26\Lib\site-packages

;run revision number script
; get revision number and date
!define SubWCRev "C:\Program Files\TortoiseSVN\bin\SubWCRev.exe"
!system '"${SubWCRev}" "${Red-RDIR}" "${Red-RDIR}\version.tpl" "${Red-RDIR}\version.txt"'

!system 'echo !define NAME "Red-R" >> "${Red-RDIR}\version.txt"'
!system 'echo !define REDRVERSION "${REDRVERSION1}" >> "${Red-RDIR}\version.txt"'
!system 'echo !define TYPE "developers" >> "${Red-RDIR}\version.txt"'




; creates variables ${NAME}-${REDRVERSION}, ${DATE}, ${SVNVERSION}
!include "${Red-RDIR}\version.txt"

;;;; Change this when a new version is made
!define REDRINSTALLDIR "${NAME}-${REDRVERSION}-Dev"

;Name and file
Name "${REDRINSTALLDIR}"

OutFile "${OUTPUTDIR}\${NAME}-${REDRVERSION}-Dev-${DATE}.r${SVNVERSION}.exe"
;---------------------------------
  ;Default installation folder
  InstallDir "$PROGRAMFILES\Red-R" ;"C:\Program Files\Red-R"

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

;---------------------------------

Var PythonDir
Var AdminInstall

!define SHELLFOLDERS \
  "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
!insertmacro MUI_PAGE_LICENSE ${LICENSE}
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; languages
!insertmacro MUI_LANGUAGE "English"
 

Section Uninstall
	MessageBox MB_YESNO "Are you sure you want to remove Red-R?$\r$\n$\r$\nThis won't remove any 3rd party software possibly installed with Red-R, such as Python or Qt.$\r$\nBut make sure you have not left any of your files in Red-R's directories!" /SD IDYES IDNO abort
	
	${If} $AdminInstall = 0
	    SetShellVarContext all
	${Else}
	    SetShellVarContext current	   
	${Endif}
    
    Delete "$INSTDIR\uninst ${REDRINSTALLDIR}.exe"

    RmDir /R /REBOOTOK "$INSTDIR\${REDRINSTALLDIR}"
	RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R\${REDRINSTALLDIR}"

    MessageBox MB_YESNO "Would you like to remove your Red-R settings?" /SD IDYES IDNO remove_keys
    
	ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
	StrCmp $0 "" 0 +2
	  ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
	StrCmp $0 "" +2 0
	  RmDir /R /REBOOTOK "$0\red-r\settings"
	
    remove_keys:

    DeleteRegKey HKCU "SOFTWARE\Red-R\${REDRINSTALLDIR}"
    DeleteRegKey HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\${REDRINSTALLDIR}"
	
	Delete "$DESKTOP\${REDRINSTALLDIR}.lnk"

	DeleteRegKey HKEY_CLASSES_ROOT ".rrs"
    DeleteRegKey HKEY_CLASSES_ROOT ".rrts"
    DeleteRegKey HKEY_CLASSES_ROOT ".rrp"
	DeleteRegKey HKEY_CLASSES_ROOT "Red R Canvas"
    
    MessageBox MB_YESNO "Would you like to remove all previous versions of Red-R?$\r$\nRemoves the entire Red-R directory." /SD IDYES IDNO removed_OK
    
    RmDir /R /REBOOTOK "$INSTDIR"
    RmDir /R /REBOOTOK "$SMPROGRAMS\Red-R"
    
    removed_OK:
    
    ; IfErrors jumpto_iferror 
        IfRebootFlag jumpto_IfRebootFlag jumpto_IfNoRebootFlag
        jumpto_IfRebootFlag:
            MessageBox MB_OK "${REDRINSTALLDIR} has been successfully removed from your system.$\r$\nYou may need to reboot your machine." /SD IDOK
            Goto abort
        jumpto_IfNoRebootFlag:
            MessageBox MB_OK "${REDRINSTALLDIR} has been successfully removed from your system." /SD IDOK
            Goto abort
    
   abort:
SectionEnd


!macro GetPythonDir
    ${If} $AdminInstall == 0
	    ReadRegStr $PythonDir HKCU Software\Python\PythonCore\2.6\InstallPath ""
		StrCmp $PythonDir "" 0 trim_backslash
		ReadRegStr $PythonDir HKLM Software\Python\PythonCore\2.6\InstallPath ""
		StrCmp $PythonDir "" return
		MessageBox MB_OK "Please ask the administrator to install Red-R$\r$\n(this is because Python was installed by her, too)."
		Quit
	${Else}
	    ReadRegStr $PythonDir HKLM Software\Python\PythonCore\2.6\InstallPath ""
		StrCmp $PythonDir "" 0 trim_backslash
		ReadRegStr $PythonDir HKCU Software\Python\PythonCore\2.6\InstallPath ""
		StrCmp $PythonDir "" return
		StrCpy $AdminInstall 0
	${EndIf}

	trim_backslash:
	StrCpy $0 $PythonDir "" -1
    ${If} $0 == "\"
        StrLen $0 $PythonDir
        IntOp $0 $0 - 1
        StrCpy $PythonDir $PythonDir $0 0
    ${EndIf}

	return:
!macroend
		
!define MFC mfc71.dll

Section ""
        MessageBox MB_OK "Red-R is built on many other programs that must be installed in a very particular way. This installer has preset all of the installation information for Red-R to work correctly. Please accept all of the installations the way they are and install all of the packages, unless you have exactly the same version don't skip any installations." 
		;StrCmp $PythonDir "" 0 have_python
		SetOutPath C:\temp # this is the path of the output of the installer and is where the other installers will be called from
    IfFileExists $PythonDir\Doc\python265.chm have_python ; a fairly good indicator that python 2.6.5 is installed.
		; !else
        StrCpy $0 ""
        askpython:
            MessageBox MB_YESNOCANCEL "Red-R installer will first launch installation of Python 2.6.5.$\r$\nPython 2.6.5 may replace an existing version of python 2.6 of some other revision.$\r$\nWould you like it to install automatically?$\r$\n(Press No for Custom installation of Python, Cancel to cancel installation of Red-R." /SD IDYES IDYES installsilently IDNO installpython
                MessageBox MB_YESNO "Red-R cannot run without Python.$\r$\nAbort the installation?" IDNO askpython
                    Quit
        installsilently:
            StrCpy $0 "/Qb-" # not sure how this makes the installer silent but would like to include in other installations
        installpython:
        File "${INCLUDES}\${PYFILENAME}"

        ExecWait 'msiexec.exe /i "C:\temp\${PYFILENAME}" ADDLOCAL=Extensions,Documentation,TclTk ALLUSERS=1 $0' $0

        Delete "C:\temp\${PYFILENAME}"


		!insertMacro GetPythonDir
		StrCmp $PythonDir "" 0 have_python
			MessageBox MB_OK "Python installation failed.$\r$\nRed-R installation cannot continue. Please reinstall."
			Quit
	have_python:


		IfFileExists $PythonDir\Lib\site-packages\pythonwin have_pythonwin
			File "${INCLUDES}\${PYWINFILENAME}"
			ExecWait "C:\temp\${PYWINFILENAME}"
			Delete "C:\temp\${PYWINFILENAME}"
	have_pythonwin:
                

			MessageBox MB_OK "Installation will check for various needed libraries$\r$\nand launch their installers if needed."

				IfFileExists $PythonDir\Lib\site-packages\numpy-1.3.0-py2.6.egg-info have_numpy
				    File "${INCLUDES}\${NUMPYFILE}"
					ExecWait "C:\temp\${NUMPYFILE}"
					Delete "C:\temp\${NUMPYFILE}"
					
			have_numpy:
                
                
            ; IfFileExists $PythonDir\Lib\site-packages\rpy.py have_rpy
                ; SetOutPath $PythonDir\Lib\site-packages # install RPy
                ; File /r *rpy* /x *.pyc /x *.pyo /x *rpy2* ${RPYFILENAME}
            ; have_rpy:
            
            IfFileExists $PythonDir\lib\site-packages\PyQt4\*.* have_pyqt
				    File "${INCLUDES}\${PYQTFILE}"
					ExecWait C:\temp\${PYQTFILE}
					Delete C:\temp\${PYQTFILE}
					
			have_pyqt:
				IfFileExists $PythonDir\lib\site-packages\PyQt4\Qwt5\*.* have_pyqwt
					File "${INCLUDES}\${PYQWTFILE}"
					ExecWait C:\temp\${PYQWTFILE}
					Delete C:\temp\${PYQWTFILE}
					
			have_pyqwt:
				IfFileExists $PythonDir\lib\site-packages\PIL\*.* have_pil
					File "${INCLUDES}\${PILFILE}"
					ExecWait C:\temp\${PILFILE}
					Delete C:\temp\${PILFILE}
					
			have_pil:
            
            IfFileExists $PythonDir\lib\site-packages\docutils\*.* have_docutils
                StrCpy $9 $OUTDIR ; remember the outdir for later use.
                StrCpy $OUTDIR "C:\temp\docutils" ; set the outdir which is where system commands are executed from 
                SetOutPath "C:\temp\docutils" ; sets the outpath to the temp docutils directory
                File /r ${INCLUDES}\${DOCUTILS}\*
                StrCpy $7 ""
                ExecWait '"c:\python26\python.exe" "C:\temp\docutils\setup.py" install' $7 ; run the install script
                DetailPrint "The program returned $7"
                RMDir /r /REBOOTOK "C:\temp\docutils" ; clean up docutils
                StrCpy $OUTDIR $9
            have_docutils:
          
SectionEnd


Section "" ;this is the section that will install Red-R and all of it's files
	ReadRegStr $0 HKCU "${SHELLFOLDERS}" AppData
	StrCmp $0 "" 0 +2
	  ReadRegStr $0 HKLM "${SHELLFOLDERS}" "Common AppData"
	StrCmp $0 "" not_installed_before 0

	IfFileExists "$0\red-r\settings" 0 not_installed_before
		ask_remove_old:
		MessageBox MB_YESNOCANCEL "Another version of Red-R has been found on the computer.$\r$\nDo you want to keep the existing settings for canvas and widgets?$\r$\n$\r$\nYou can usually safely answer 'Yes'; in case of problems, re-run this installation." /SD IDYES IDYES not_installed_before IDNO remove_old_settings
			MessageBox MB_YESNO "Abort the installation?" IDNO ask_remove_old
				Quit

		remove_old_settings:
		RmDir /R "$0\red-r\settings"

	not_installed_before:

    AccessControl::GrantOnFile "$INSTDIR" "Everyone" "FullAccess + GenericRead + GenericWrite" ; required to give those with admin restrictions read write access to the files.
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}"
	File ${Red-RDIR}\version.txt
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}"
	File ${Red-RDIR}\licence.txt
    
    ; SetOutPath "$INSTDIR\${REDRINSTALLDIR}"
	; File ${Red-RDIR}\__init__.py
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\Examples"
    File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\Examples\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\canvas"
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\canvas\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\canvas\rpy"
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\canvas\rpy\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\libraries"
	File ${Red-RDIR}\libraries\__init__.py
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\libraries\base"
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\libraries\base\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\libraries\plotting"
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\libraries\plotting\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\libraries\stats"
	File /r /x .svn /x *.pyc /x .nsi ${Red-RDIR}\libraries\stats\*
    
    SetOutPath "$INSTDIR\${REDRINSTALLDIR}\libraries\blank"
	File /r /x .svn /x *.pyc /x *.py /x .nsi ${Red-RDIR}\libraries\blank\*
    File ${Red-RDIR}\libraries\blank\__init__.py
    File ${Red-RDIR}\libraries\blank\signalClasses\__init__.py
    File ${Red-RDIR}\libraries\blank\qtWidgets\__init__.py

    ; SetOutPath "$INSTDIR\${REDRINSTALLDIR}\Examples"
	; File /r /x .svn /x *.pyc /x .nsi ${EXAMPLES}\*
    
    IfFileExists $INSTDIR\R\README.${RVER}.* has_R
    
        SetOutPath $INSTDIR\R
    File /r /x .svn "${RDIRECTORY}\*"
    has_R:
    
    
    AccessControl::GrantOnFile "$INSTDIR" "Everyone" "FullAccess + GenericRead + GenericWrite" ; required to give those with admin restrictions read write access to the files.
    
    AccessControl::GrantOnFile "$INSTDIR\${REDRINSTALLDIR}\libraries\blank" "Everyone" "FullAccess + GenericRead + GenericWrite" ; required to give those with admin restrictions read write access to the files.
    
    AccessControl::GrantOnFile "$INSTDIR\R" "Everyone" "FullAccess + GenericRead + GenericWrite" ; required to give those with admin restrictions read write access to the files.
    
    AccessControl::GrantOnFile "$INSTDIR\R\library" "Everyone" "FullAccess + GenericRead + GenericWrite" ; required to give those with admin restrictions read write access to the files.
    
    CreateDirectory "$DOCUMENTS\Red-R"
    CreateDirectory "$DOCUMENTS\Red-R\Templates"
    CreateDirectory "$DOCUMENTS\Red-R\Schemas"
	CreateDirectory "$SMPROGRAMS\Red-R\${REDRINSTALLDIR}"
    AccessControl::GrantOnFile "$SMPROGRAMS\Red-R" "(BU)" "FullAccess" ; required to give those with admin restrictions read write access to the files.
    
	CreateShortCut "$SMPROGRAMS\Red-R\${REDRINSTALLDIR}\${REDRINSTALLDIR}.lnk" "$INSTDIR\${REDRINSTALLDIR}\canvas\red-RCanvas.pyw" "" $INSTDIR\${REDRINSTALLDIR}\canvas\icons\orange.ico 0
	CreateShortCut "$SMPROGRAMS\Red-R\${REDRINSTALLDIR}\Uninstall Red-R.lnk" "$INSTDIR\uninst ${REDRINSTALLDIR}.exe"

	;SetOutPath $INSTDIR\canvas
	CreateShortCut "$DESKTOP\${REDRINSTALLDIR}.lnk" "$INSTDIR\${REDRINSTALLDIR}\canvas\red-RCanvas.pyw" "" $INSTDIR\${REDRINSTALLDIR}\canvas\icons\orange.ico 0
	;CreateShortCut "$SMPROGRAMS\Red-R\Red-R Canvas.lnk" "$INSTDIR\canvas\red-RCanvas.pyw" "" $INSTDIR\canvas\icons\orange.ico 0

	WriteRegStr SHELL_CONTEXT "SOFTWARE\Python\PythonCore\2.6\PythonPath\Red-R\${REDRINSTALLDIR}" "" "$INSTDIR\${REDRINSTALLDIR};$INSTDIR\${REDRINSTALLDIR}\libraries;$INSTDIR\${REDRINSTALLDIR}\canvas"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${REDRINSTALLDIR}" "DisplayName" "Red-R (remove only)"
	WriteRegStr SHELL_CONTEXT "Software\Microsoft\Windows\CurrentVersion\Uninstall\Red-R\${REDRINSTALLDIR}" "UninstallString" '"$INSTDIR\uninst ${REDRINSTALLDIR}.exe"'

	WriteRegStr HKEY_CLASSES_ROOT ".rrs" "" "Red R Canvas"
    WriteRegStr HKEY_CLASSES_ROOT ".rrp" "" "Red R Canvas"
    WriteRegStr HKEY_CLASSES_ROOT ".rrts" "" "Red R Canvas"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\DefaultIcon" "" "$INSTDIR\${REDRINSTALLDIR}\canvas\icons\redrOWS.ico"
	WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\Shell\Open\Command\" "" '$PythonDir\pythonw.exe $INSTDIR\${REDRINSTALLDIR}\canvas\red-RCanvas.pyw "%1"';name is appended into the sys.argv variables for opening by Red-R
    WriteRegStr HKEY_CLASSES_ROOT "Red R Canvas\RedRDir" "" "$INSTDIR"
    
    
	WriteUninstaller "$INSTDIR\uninst ${REDRINSTALLDIR}.exe"

SectionEnd

Function .onInit
	StrCpy $AdminInstall 1

	UserInfo::GetAccountType
	Pop $1
	SetShellVarContext all
	${If} $1 != "Admin"
		SetShellVarContext current
		StrCpy $AdminInstall 0
	${Else}
		SetShellVarContext all
		StrCpy $AdminInstall 1
	${EndIf}

	!insertMacro GetPythonDir
		continueinst:
	;!endif
FunctionEnd