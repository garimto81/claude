<#
.SYNOPSIS
    VCode Multi - Unified VSCode Multi-Instance Launcher
    Version: 1.0.0

.DESCRIPTION
    Launch multiple VSCode instances with saved layouts and auto-execute Claude.

.PARAMETER Action
    detect     - Detect current VSCode windows and save layout
    launch     - Launch all projects with saved layout
    reposition - Reposition existing windows to saved layout
    status     - Show current status
    help       - Show help

.PARAMETER ConfigFile
    Path to layout configuration file

.PARAMETER DryRun
    Preview without launching

.PARAMETER NoAutoExecute
    Skip Claude auto-execution

.EXAMPLE
    ./launch-layout.ps1 detect
    ./launch-layout.ps1 launch
    ./launch-layout.ps1 reposition
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "vscode-layout.json",
    [switch]$DryRun,
    [switch]$NoAutoExecute
)

$Script:ScriptRoot = $PSScriptRoot
$Script:LogFile = Join-Path $Script:ScriptRoot "launcher.log"

# Windows API
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class WinAPI {
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public const uint SWP_NOZORDER = 0x0004;
    public const uint SWP_SHOWWINDOW = 0x0040;
    public const int SW_RESTORE = 9;
}
"@

$Script:WShell = New-Object -ComObject WScript.Shell

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Find-VSCodeWindow {
    param([string]$ProjectName)

    $script:foundHandle = [IntPtr]::Zero
    $script:searchName = $ProjectName

    $callback = {
        param([IntPtr]$hwnd, [IntPtr]$lParam)

        if (-not [WinAPI]::IsWindowVisible($hwnd)) { return $true }

        $title = New-Object System.Text.StringBuilder 256
        [WinAPI]::GetWindowText($hwnd, $title, 256) | Out-Null
        $titleStr = $title.ToString()

        if ($titleStr -match "Visual Studio Code" -and $titleStr -match $script:searchName) {
            $script:foundHandle = $hwnd
            return $false
        }
        return $true
    }

    $delegate = [WinAPI+EnumWindowsProc]$callback
    [WinAPI]::EnumWindows($delegate, [IntPtr]::Zero) | Out-Null

    return $script:foundHandle
}

function Set-WindowPosition {
    param(
        [IntPtr]$Handle,
        [int]$X, [int]$Y,
        [int]$Width, [int]$Height
    )

    [WinAPI]::ShowWindow($Handle, [WinAPI]::SW_RESTORE) | Out-Null
    Start-Sleep -Milliseconds 100

    $result = [WinAPI]::SetWindowPos(
        $Handle, [IntPtr]::Zero,
        $X, $Y, $Width, $Height,
        [WinAPI]::SWP_NOZORDER -bor [WinAPI]::SWP_SHOWWINDOW
    )

    return $result
}

function Send-ClaudeCommand {
    param([IntPtr]$Handle, [string]$Args)

    [WinAPI]::SetForegroundWindow($Handle) | Out-Null
    Start-Sleep -Milliseconds 300

    # Open terminal (Ctrl+`)
    $Script:WShell.SendKeys("^``")
    Start-Sleep -Milliseconds 800

    # Type command
    $Script:WShell.SendKeys("claude $Args")
    Start-Sleep -Milliseconds 200

    # Enter
    $Script:WShell.SendKeys("{ENTER}")
}

# Main
Write-Host @"

  _                            _       _                             _
 | |    __ _ _   _ _ __   ___| |__   | |    __ _ _   _  ___  _   _| |_
 | |   / _` | | | | '_ \ / __| '_ \  | |   / _` | | | |/ _ \| | | | __|
 | |__| (_| | |_| | | | | (__| | | | | |__| (_| | |_| | (_) | |_| | |_
 |_____\__,_|\__,_|_| |_|\___|_| |_| |_____\__,_|\__, |\___/ \__,_|\__|
                                                 |___/

"@ -ForegroundColor Cyan

$configPath = Join-Path $Script:ScriptRoot $ConfigFile
if (-not (Test-Path $configPath)) {
    Write-Log "Config not found: $configPath" -Level ERROR
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json
$projects = @($config.projects | Where-Object { $_.enabled })

Write-Log "Loaded $($projects.Count) projects from $ConfigFile"
Write-Log "Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'LIVE' })"
Write-Host ""

# Phase 1: Launch VSCode instances
Write-Log "Phase 1: Launching VSCode instances..." -Level INFO

$launchedCount = 0
foreach ($project in $projects) {
    $name = $project.name
    $path = $project.path

    if (-not (Test-Path $path)) {
        Write-Log "Path not found: $path" -Level ERROR
        continue
    }

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would launch: $name at $path" -Level INFO
    } else {
        Start-Process "code" -ArgumentList "--new-window", "`"$path`""
        Write-Log "Launched: $name" -Level OK
        $launchedCount++
    }

    Start-Sleep -Milliseconds 500
}

if ($DryRun) {
    Write-Log "[DRY-RUN] Would launch $($projects.Count) instances" -Level INFO
    exit 0
}

# Wait for windows to appear
Write-Log "Waiting for windows to initialize..."
Start-Sleep -Seconds 4

# Phase 2: Position windows
Write-Log "Phase 2: Positioning windows..." -Level INFO

foreach ($project in $projects) {
    $name = $project.name
    $layout = $project.layout

    if (-not $layout) {
        Write-Log "No layout for: $name" -Level WARN
        continue
    }

    $hwnd = Find-VSCodeWindow -ProjectName $name

    if ($hwnd -eq [IntPtr]::Zero) {
        Write-Log "Window not found: $name" -Level WARN
        continue
    }

    $x = $layout.position.x
    $y = $layout.position.y
    $w = $layout.size.width
    $h = $layout.size.height

    $result = Set-WindowPosition -Handle $hwnd -X $x -Y $y -Width $w -Height $h

    if ($result) {
        Write-Log "Positioned: $name at ($x, $y) ${w}x${h}" -Level OK
    } else {
        Write-Log "Failed to position: $name" -Level ERROR
    }

    Start-Sleep -Milliseconds 200
}

# Phase 3: Execute Claude
if (-not $NoAutoExecute -and $config.settings.autoExecuteClaude) {
    Write-Log "Phase 3: Executing Claude in terminals..." -Level INFO
    Start-Sleep -Seconds 1

    $claudeArgs = $config.settings.claudeArgs

    foreach ($project in $projects) {
        $name = $project.name
        $hwnd = Find-VSCodeWindow -ProjectName $name

        if ($hwnd -ne [IntPtr]::Zero) {
            Send-ClaudeCommand -Handle $hwnd -Args $claudeArgs
            Write-Log "Claude started in: $name" -Level OK
            Start-Sleep -Milliseconds 1000
        }
    }
}

Write-Host ""
Write-Log "=== Launch Complete ===" -Level OK
Write-Log "Launched: $launchedCount / $($projects.Count) projects"
