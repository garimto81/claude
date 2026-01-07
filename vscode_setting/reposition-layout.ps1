<#
.SYNOPSIS
    Reposition existing VSCode windows to saved layout (without launching new instances)
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "vscode-layout.json",
    [switch]$DryRun
)

$Script:ScriptRoot = $PSScriptRoot

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
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left, Top, Right, Bottom;
    }

    public const uint SWP_NOZORDER = 0x0004;
    public const uint SWP_SHOWWINDOW = 0x0040;
    public const int SW_RESTORE = 9;
}
"@

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
    }
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [$Level] $Message" -ForegroundColor $color
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

        if ($title.ToString() -match "Visual Studio Code" -and $title.ToString() -match $script:searchName) {
            $script:foundHandle = $hwnd
            return $false
        }
        return $true
    }

    [WinAPI]::EnumWindows([WinAPI+EnumWindowsProc]$callback, [IntPtr]::Zero) | Out-Null
    return $script:foundHandle
}

Write-Host ""
Write-Host "=== Reposition VSCode Windows ===" -ForegroundColor Cyan
Write-Host ""

$configPath = Join-Path $Script:ScriptRoot $ConfigFile
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$projects = @($config.projects | Where-Object { $_.enabled })

Write-Log "Found $($projects.Count) projects in config"
Write-Host ""

$repositioned = 0
$notFound = 0

foreach ($project in $projects) {
    $name = $project.name
    $layout = $project.layout

    if (-not $layout) { continue }

    $hwnd = Find-VSCodeWindow -ProjectName $name

    if ($hwnd -eq [IntPtr]::Zero) {
        Write-Log "Window not found: $name" -Level WARN
        $notFound++
        continue
    }

    $x = $layout.position.x
    $y = $layout.position.y
    $w = $layout.size.width
    $h = $layout.size.height
    $loc = $layout.location

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would move $name to ($x, $y) ${w}x${h} [$loc]" -Level INFO
    } else {
        [WinAPI]::ShowWindow($hwnd, [WinAPI]::SW_RESTORE) | Out-Null
        Start-Sleep -Milliseconds 100

        $result = [WinAPI]::SetWindowPos($hwnd, [IntPtr]::Zero, $x, $y, $w, $h,
            [WinAPI]::SWP_NOZORDER -bor [WinAPI]::SWP_SHOWWINDOW)

        if ($result) {
            Write-Log "$name -> ($x, $y) ${w}x${h} [$loc]" -Level OK
            $repositioned++
        } else {
            Write-Log "Failed: $name" -Level ERROR
        }
    }

    Start-Sleep -Milliseconds 150
}

Write-Host ""
Write-Log "=== Complete ===" -Level OK
Write-Log "Repositioned: $repositioned | Not found: $notFound"
