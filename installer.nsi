; MODIFIED FROM: basic script template for NSIS installers
;
; Originally Written by Philip Chu
; Modified by Ian Sanders
; Original code Copyright (c) 2004-2005 Technicat, LLC
;
; This software is provided 'as-is', without any express or implied warranty.
; In no event will the authors be held liable for any damages arising from the
; use of this software.

; Permission is granted to anyone to use this software for any purpose,
; including commercial applications, and to alter it ; and redistribute
; it freely, subject to the following restrictions:

;    1. The origin of this software must not be misrepresented; you must not claim that
;       you wrote the original software. If you use this software in a product, an
;       acknowledgment in the product documentation would be appreciated but is not required.

;    2. Altered source versions must be plainly marked as such, and must not be
;       misrepresented as being the original software.

;    3. This notice may not be removed or altered from any source distribution.

!include "MUI2.nsh"

!define setup "bubble_sheet_reader_install.exe"
!define srcdir ".\dist\bubble_sheet_reader"
!define company "Ian Sanders"
!define prodname "Bubble Sheet Reader"
!define exec "bubble_sheet_reader\bubble_sheet_reader.exe"

!define icon "assets\icon.ico"

!define regkey "Software\${prodname}"
!define uninstkey "Software\Microsoft\Windows\CurrentVersion\Uninstall\${prodname}"

!define startmenu "$SMPROGRAMS\${prodname}"
!define uninstaller "uninstall.exe"

; Settings ---------------------------------------------------------------------

XPStyle off
ShowInstDetails hide
ShowUninstDetails hide

Name "${prodname}"
Caption "${prodname}"

!ifdef icon
  Icon "${srcdir}\${icon}"
!endif

OutFile "${setup}"

SetDateSave on
SetDatablockOptimize on
CRCCheck on
SilentInstall normal

InstallDir "$PROGRAMFILES\${prodname}"
InstallDirRegKey HKLM "${regkey}" ""

; Pages ------------------------------------------------------------------------

Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

AutoCloseWindow false
ShowInstDetails show

; Beginning (invisible) section
Section
  WriteRegStr HKLM "${regkey}" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "${uninstkey}" "DisplayName" "${prodname} (remove only)"
  WriteRegStr HKLM "${uninstkey}" "UninstallString" '"$INSTDIR\${uninstaller}"'

  WriteRegStr HKCR "${prodname}\Shell\open\command\" "" '"$INSTDIR\${exec} "%1"'

  !ifdef icon
    WriteRegStr HKCR "${prodname}\DefaultIcon" "" "$INSTDIR\${icon}"
  !endif

  SetOutPath $INSTDIR

  File /a /r "${srcdir}"

  !ifdef icon
    File /a "${srcdir}\${icon}"
  !endif

  WriteUninstaller "${uninstaller}"
SectionEnd

; Create shortcuts
Section
  CreateDirectory "${startmenu}"
  SetOutPath $INSTDIR ; for working directory

  !ifdef icon
    CreateShortCut "${startmenu}\${prodname}.lnk" "$INSTDIR\${exec}" "" "$INSTDIR\${icon}"
  !else
    CreateShortCut "${startmenu}\${prodname}.lnk" "$INSTDIR\${exec}"
  !endif
SectionEnd

; Uninstaller
; All section names prefixed by "Un" will be in the uninstaller
UninstallText "This will uninstall ${prodname}."

!ifdef icon
  UninstallIcon "${srcdir}\${icon}"
!endif

Section "Uninstall"
  DeleteRegKey HKLM "${uninstkey}"
  DeleteRegKey HKLM "${regkey}"

  Delete "${startmenu}\*.*"
  Delete "${startmenu}"

  !ifdef licensefile
    Delete "$INSTDIR\${licensefile}"
  !endif

  !ifdef notefile
    Delete "$INSTDIR\${notefile}"
  !endif

  !ifdef icon
    Delete "$INSTDIR\${icon}"
  !endif

  Delete "$INSTDIR"

  !ifdef unfiles
    !include "${unfiles}"
  !endif
SectionEnd