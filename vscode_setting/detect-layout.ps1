<#
.SYNOPSIS
    Detect monitor configuration and VSCode window layouts
#>

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class LayoutDetector {
    [DllImport("user32.dll")]
    public static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip, MonitorEnumProc lpfnEnum, IntPtr dwData);

    [DllImport("user32.dll")]
    public static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFOEX lpmi);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    public delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdcMonitor, ref RECT lprcMonitor, IntPtr dwData);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    public struct MONITORINFOEX {
        public int cbSize;
        public RECT rcMonitor;
        public RECT rcWork;
        public uint dwFlags;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string szDevice;
    }

    public const uint MONITORINFOF_PRIMARY = 1;
}
"@

# Get monitor information
Write-Host "=== Monitor Configuration ===" -ForegroundColor Cyan
Write-Host ""

$monitors = @()
$monitorIndex = 0

$monitorCallback = {
    param([IntPtr]$hMonitor, [IntPtr]$hdcMonitor, [ref]$lprcMonitor, [IntPtr]$dwData)

    $mi = New-Object LayoutDetector+MONITORINFOEX
    $mi.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($mi)

    if ([LayoutDetector]::GetMonitorInfo($hMonitor, [ref]$mi)) {
        $script:monitorIndex++
        $isPrimary = ($mi.dwFlags -band [LayoutDetector]::MONITORINFOF_PRIMARY) -ne 0

        $monitorInfo = @{
            Index = $script:monitorIndex
            Device = $mi.szDevice
            IsPrimary = $isPrimary
            Monitor = @{
                Left = $mi.rcMonitor.Left
                Top = $mi.rcMonitor.Top
                Right = $mi.rcMonitor.Right
                Bottom = $mi.rcMonitor.Bottom
                Width = $mi.rcMonitor.Right - $mi.rcMonitor.Left
                Height = $mi.rcMonitor.Bottom - $mi.rcMonitor.Top
            }
            WorkArea = @{
                Left = $mi.rcWork.Left
                Top = $mi.rcWork.Top
                Right = $mi.rcWork.Right
                Bottom = $mi.rcWork.Bottom
                Width = $mi.rcWork.Right - $mi.rcWork.Left
                Height = $mi.rcWork.Bottom - $mi.rcWork.Top
            }
        }

        $script:monitors += $monitorInfo

        $primaryTag = if ($isPrimary) { " [PRIMARY]" } else { "" }
        Write-Host "Monitor $($script:monitorIndex)$primaryTag" -ForegroundColor Yellow
        Write-Host "  Device: $($mi.szDevice)"
        Write-Host "  Position: ($($mi.rcMonitor.Left), $($mi.rcMonitor.Top))"
        Write-Host "  Resolution: $($monitorInfo.Monitor.Width) x $($monitorInfo.Monitor.Height)"
        Write-Host "  Work Area: $($monitorInfo.WorkArea.Width) x $($monitorInfo.WorkArea.Height)"
        Write-Host ""
    }

    return $true
}

$delegate = [LayoutDetector+MonitorEnumProc]$monitorCallback
[LayoutDetector]::EnumDisplayMonitors([IntPtr]::Zero, [IntPtr]::Zero, $delegate, [IntPtr]::Zero) | Out-Null

# Get VSCode windows
Write-Host "=== VSCode Window Layouts ===" -ForegroundColor Cyan
Write-Host ""

$vscodeProcesses = Get-Process -Name 'Code' -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 }

$vscodeWindows = @()

$windowCallback = {
    param([IntPtr]$hwnd, [IntPtr]$lParam)

    if (-not [LayoutDetector]::IsWindowVisible($hwnd)) {
        return $true
    }

    $title = New-Object System.Text.StringBuilder 256
    [LayoutDetector]::GetWindowText($hwnd, $title, 256) | Out-Null
    $titleStr = $title.ToString()

    if ($titleStr -match 'Visual Studio Code') {
        $rect = New-Object LayoutDetector+RECT
        [LayoutDetector]::GetWindowRect($hwnd, [ref]$rect) | Out-Null

        $pid = 0
        [LayoutDetector]::GetWindowThreadProcessId($hwnd, [ref]$pid) | Out-Null

        # Extract project name from title
        $projectName = "Unknown"
        if ($titleStr -match '^(.+?) - (.+?) - Visual Studio Code$') {
            $projectName = $Matches[2]
        }
        elseif ($titleStr -match '^(.+?) - Visual Studio Code$') {
            $projectName = $Matches[1]
        }

        $windowInfo = @{
            Handle = $hwnd
            PID = $pid
            Title = $titleStr
            ProjectName = $projectName
            Position = @{
                X = $rect.Left
                Y = $rect.Top
            }
            Size = @{
                Width = $rect.Right - $rect.Left
                Height = $rect.Bottom - $rect.Top
            }
            Rect = @{
                Left = $rect.Left
                Top = $rect.Top
                Right = $rect.Right
                Bottom = $rect.Bottom
            }
        }

        $script:vscodeWindows += $windowInfo

        # Determine which monitor this window is on
        $centerX = $rect.Left + ($rect.Right - $rect.Left) / 2
        $centerY = $rect.Top + ($rect.Bottom - $rect.Top) / 2

        $onMonitor = "Unknown"
        foreach ($mon in $script:monitors) {
            if ($centerX -ge $mon.Monitor.Left -and $centerX -lt $mon.Monitor.Right -and
                $centerY -ge $mon.Monitor.Top -and $centerY -lt $mon.Monitor.Bottom) {
                $onMonitor = "Monitor $($mon.Index)"
                break
            }
        }

        Write-Host "[$projectName]" -ForegroundColor Green
        Write-Host "  PID: $pid"
        Write-Host "  Position: ($($rect.Left), $($rect.Top))"
        Write-Host "  Size: $($windowInfo.Size.Width) x $($windowInfo.Size.Height)"
        Write-Host "  Monitor: $onMonitor"
        Write-Host ""
    }

    return $true
}

$windowDelegate = [LayoutDetector+EnumWindowsProc]$windowCallback
[LayoutDetector]::EnumWindows($windowDelegate, [IntPtr]::Zero) | Out-Null

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Monitors: $($monitors.Count)"
Write-Host "VSCode Windows: $($vscodeWindows.Count)"

# Create visual layout
if ($monitors.Count -gt 0 -and $vscodeWindows.Count -gt 0) {
    Write-Host ""
    Write-Host "=== Visual Layout ===" -ForegroundColor Cyan

    # Find bounds
    $minX = ($monitors | ForEach-Object { $_.Monitor.Left } | Measure-Object -Minimum).Minimum
    $maxX = ($monitors | ForEach-Object { $_.Monitor.Right } | Measure-Object -Maximum).Maximum
    $minY = ($monitors | ForEach-Object { $_.Monitor.Top } | Measure-Object -Minimum).Minimum
    $maxY = ($monitors | ForEach-Object { $_.Monitor.Bottom } | Measure-Object -Maximum).Maximum

    Write-Host ""
    Write-Host "Total virtual screen: ($minX, $minY) to ($maxX, $maxY)"
    Write-Host "Total size: $($maxX - $minX) x $($maxY - $minY)"
}

# Export to JSON
$layoutData = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Monitors = $monitors
    VSCodeWindows = $vscodeWindows
}

$layoutData | ConvertTo-Json -Depth 10 | Set-Content "C:/claude/vscode_setting/current-layout.json"
Write-Host ""
Write-Host "Layout saved to: current-layout.json" -ForegroundColor Green
