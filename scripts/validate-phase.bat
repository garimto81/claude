@echo off
REM Windows Batch wrapper for PowerShell validation scripts
REM Usage: validate-phase.bat <PHASE> [ARGS]

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: validate-phase.bat ^<PHASE^> [ARGS]
    echo.
    echo Examples:
    echo   validate-phase.bat 0 0001
    echo   validate-phase.bat 0.5 0001
    echo   validate-phase.bat 1
    echo   validate-phase.bat 2
    echo   validate-phase.bat 3 v1.2.0
    echo   validate-phase.bat 5
    echo   validate-phase.bat 6
    exit /b 1
)

set PHASE=%~1
shift

REM Call appropriate PowerShell script
if "%PHASE%"=="0" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-0.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="0.5" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-0.5.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-1.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="2" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-2.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="3" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-3.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="5" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-5.ps1" %1 %2 %3 %4
) else if "%PHASE%"=="6" (
    powershell -ExecutionPolicy Bypass -File "%~dp0validate-phase-6.ps1" %1 %2 %3 %4
) else (
    echo Error: Unknown phase "%PHASE%"
    echo Supported phases: 0, 0.5, 1, 2, 3, 5, 6
    exit /b 1
)

exit /b %ERRORLEVEL%
