@echo off
:: Check for Administrator privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting Administrator privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
echo ----------------------------------------------------
echo STOPPING WINDOWS UPDATE SERVICES...
echo ----------------------------------------------------

:: 1. Stop Windows Update Service
echo [Step 1] Stopping wuauserv service...
net stop wuauserv
sc config wuauserv start= disabled

:: 2. Stop Background Intelligent Transfer Service
echo [Step 2] Stopping bits service...
net stop bits
sc config bits start= disabled

:: 3. Stop Delivery Optimization Service
echo [Step 3] Stopping dosvc service...
net stop dosvc
sc config dosvc start= disabled

echo ----------------------------------------------------
echo CONFIGURING REGISTRY POLICIES...
echo ----------------------------------------------------

:: 4. Disable Automatic Updates via Registry (Group Policy equivalent)
echo [Step 4] Setting NoAutoUpdate registry key...
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v "NoAutoUpdate" /t REG_DWORD /d 1 /f

:: 5. Remove Windows Update Cache (Fixes the lingering update list in Settings)
echo [Step 5] Clearing SoftwareDistribution folder...
if exist "%WINDIR%\SoftwareDistribution" (
    rd /s /q "%WINDIR%\SoftwareDistribution"
    echo Cache cleared.
)

echo ----------------------------------------------------
echo DONE! Please restart your computer to reflect changes.
echo ----------------------------------------------------
pause