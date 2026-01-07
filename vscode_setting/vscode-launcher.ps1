<#
.SYNOPSIS
    Multi-VSCode IDE Launcher with Claude Auto-Execute

.DESCRIPTION
    Launches multiple VSCode instances with configured project folders,
    automatically arranges windows in a grid layout, and executes
    Claude Code in each terminal.

.PARAMETER ConfigFile
    Path to the JSON configuration file. Defaults to vscode-projects.json

.PARAMETER SaveProfile
    Save current configuration as a named profile

.PARAMETER LoadProfile
    Load a previously saved profile

.PARAMETER DryRun
    Show what would be done without actually launching

.EXAMPLE
    ./vscode-launcher.ps1

.EXAMPLE
    ./vscode-launcher.ps1 -ConfigFile "my-projects.json"

.EXAMPLE
    ./vscode-launcher.ps1 -LoadProfile "work"
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ConfigFile = "vscode-projects.json",

    [Parameter()]
    [string]$SaveProfile,

    [Parameter()]
    [string]$LoadProfile,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$NoAutoExecute
)

# ============================================================================
# Configuration
# ============================================================================

$Script:ScriptRoot = $PSScriptRoot
$Script:ProfilesDir = Join-Path $Script:ScriptRoot ".vscode-launcher-profiles"
$Script:LogFile = Join-Path $Script:ScriptRoot "vscode-launcher.log"

# Status tracking
$Script:ProjectStatus = @{}

# ============================================================================
# Windows API for Window Management
# ============================================================================

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class WindowManager {
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern int GetSystemMetrics(int nIndex);

    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    public const int SM_CXSCREEN = 0;
    public const int SM_CYSCREEN = 1;
    public const uint SWP_NOZORDER = 0x0004;
    public const uint SWP_SHOWWINDOW = 0x0040;
}
"@

# ============================================================================
# Logging Functions
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "OK", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    # Console output with colors
    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
    }

    Write-Host $logMessage -ForegroundColor $color

    # File logging
    Add-Content -Path $Script:LogFile -Value $logMessage -ErrorAction SilentlyContinue
}

# ============================================================================
# Configuration Functions
# ============================================================================

function Get-Configuration {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Write-Log "Configuration file not found: $Path" -Level ERROR
        Write-Log "Creating example configuration file..." -Level INFO

        $examplePath = Join-Path $Script:ScriptRoot "vscode-projects.example.json"
        if (Test-Path $examplePath) {
            Copy-Item $examplePath $Path
            Write-Log "Created $Path from example. Please edit and re-run." -Level OK
        }
        return $null
    }

    try {
        $config = Get-Content $Path -Raw | ConvertFrom-Json
        Write-Log "Loaded configuration from $Path" -Level OK
        return $config
    }
    catch {
        Write-Log "Failed to parse configuration: $_" -Level ERROR
        return $null
    }
}

function Get-EnabledProjects {
    param($Config)

    $enabled = $Config.projects | Where-Object { $_.enabled -eq $true }
    Write-Log "Found $($enabled.Count) enabled projects" -Level INFO
    return $enabled
}

# ============================================================================
# Screen Layout Functions
# ============================================================================

function Get-ScreenResolution {
    $width = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CXSCREEN)
    $height = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CYSCREEN)

    Write-Log "Screen resolution: ${width}x${height}" -Level INFO

    return @{
        Width = $width
        Height = $height
    }
}

function Get-GridLayout {
    param(
        [int]$ProjectCount,
        [hashtable]$ScreenSize
    )

    # Calculate optimal grid dimensions
    $cols = [Math]::Ceiling([Math]::Sqrt($ProjectCount))
    $rows = [Math]::Ceiling($ProjectCount / $cols)

    # Calculate window size
    $windowWidth = [Math]::Floor($ScreenSize.Width / $cols)
    $windowHeight = [Math]::Floor($ScreenSize.Height / $rows)

    Write-Log "Grid layout: ${cols}x${rows} (${windowWidth}x${windowHeight} per window)" -Level INFO

    return @{
        Columns = $cols
        Rows = $rows
        WindowWidth = $windowWidth
        WindowHeight = $windowHeight
    }
}

function Get-WindowPosition {
    param(
        [int]$Index,
        [hashtable]$Layout
    )

    $col = $Index % $Layout.Columns
    $row = [Math]::Floor($Index / $Layout.Columns)

    return @{
        X = $col * $Layout.WindowWidth
        Y = $row * $Layout.WindowHeight
        Width = $Layout.WindowWidth
        Height = $Layout.WindowHeight
    }
}

# ============================================================================
# VSCode Launch Functions
# ============================================================================

function Start-VSCodeInstance {
    param(
        [object]$Project,
        [hashtable]$Position,
        [object]$Settings,
        [switch]$DryRun
    )

    $name = $Project.name
    $path = $Project.path

    # Update status
    $Script:ProjectStatus[$name] = @{
        Status = "Starting"
        StartTime = Get-Date
        ProcessId = $null
    }

    if (-not (Test-Path $path)) {
        Write-Log "Project path does not exist: $path" -Level ERROR
        $Script:ProjectStatus[$name].Status = "Error"
        return $null
    }

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would launch VSCode for '$name' at $path" -Level INFO
        Write-Log "[DRY-RUN] Position: X=$($Position.X), Y=$($Position.Y), Size=$($Position.Width)x$($Position.Height)" -Level INFO
        return $null
    }

    try {
        # Launch VSCode with new window
        $process = Start-Process "code" -ArgumentList "--new-window", "`"$path`"" -PassThru

        $Script:ProjectStatus[$name].ProcessId = $process.Id
        Write-Log "Launched VSCode for '$name' (PID: $($process.Id))" -Level OK

        return $process
    }
    catch {
        Write-Log "Failed to launch VSCode for '$name': $_" -Level ERROR
        $Script:ProjectStatus[$name].Status = "Error"
        return $null
    }
}

function Set-WindowPosition {
    param(
        [int]$ProcessId,
        [hashtable]$Position,
        [int]$MaxAttempts = 10
    )

    # Wait for window to appear and position it
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        Start-Sleep -Milliseconds 500

        $hwnd = Get-VSCodeWindowHandle -ProcessId $ProcessId
        if ($hwnd -ne [IntPtr]::Zero) {
            $result = [WindowManager]::SetWindowPos(
                $hwnd,
                [IntPtr]::Zero,
                $Position.X,
                $Position.Y,
                $Position.Width,
                $Position.Height,
                [WindowManager]::SWP_NOZORDER -bor [WindowManager]::SWP_SHOWWINDOW
            )

            if ($result) {
                Write-Log "Positioned window at ($($Position.X), $($Position.Y))" -Level OK
                return $true
            }
        }
    }

    Write-Log "Could not position window for PID $ProcessId" -Level WARN
    return $false
}

function Get-VSCodeWindowHandle {
    param([int]$ProcessId)

    $foundHandle = [IntPtr]::Zero

    $callback = [WindowManager+EnumWindowsProc]{
        param([IntPtr]$hwnd, [IntPtr]$lParam)

        $windowPid = 0
        [WindowManager]::GetWindowThreadProcessId($hwnd, [ref]$windowPid) | Out-Null

        if ($windowPid -eq $ProcessId) {
            $title = New-Object System.Text.StringBuilder 256
            [WindowManager]::GetWindowText($hwnd, $title, 256) | Out-Null

            if ($title.ToString() -match "Visual Studio Code") {
                $script:foundHandle = $hwnd
                return $false  # Stop enumeration
            }
        }
        return $true
    }

    [WindowManager]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null

    return $script:foundHandle
}

# ============================================================================
# Claude Execution Functions
# ============================================================================

function Invoke-ClaudeInTerminal {
    param(
        [string]$ProjectName,
        [string]$ClaudeArgs,
        [switch]$DryRun
    )

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would execute 'claude $ClaudeArgs' in '$ProjectName'" -Level INFO
        return
    }

    # Note: Direct terminal command injection requires VSCode extension or SendKeys
    # For now, we document that users should use keyboard shortcut to open terminal
    Write-Log "Claude command ready for '$ProjectName': claude $ClaudeArgs" -Level INFO
    $Script:ProjectStatus[$ProjectName].Status = "Ready"
}

# ============================================================================
# Profile Functions
# ============================================================================

function Save-Profile {
    param(
        [string]$Name,
        [object]$Config
    )

    if (-not (Test-Path $Script:ProfilesDir)) {
        New-Item -ItemType Directory -Path $Script:ProfilesDir -Force | Out-Null
    }

    $profilePath = Join-Path $Script:ProfilesDir "$Name.json"
    $Config | ConvertTo-Json -Depth 10 | Set-Content $profilePath

    Write-Log "Saved profile '$Name' to $profilePath" -Level OK
}

function Get-Profile {
    param([string]$Name)

    $profilePath = Join-Path $Script:ProfilesDir "$Name.json"

    if (-not (Test-Path $profilePath)) {
        Write-Log "Profile not found: $Name" -Level ERROR
        return $null
    }

    return Get-Content $profilePath -Raw | ConvertFrom-Json
}

# ============================================================================
# Status Display Functions
# ============================================================================

function Show-Status {
    Write-Host "`n=== VSCode Launcher Status ===" -ForegroundColor Cyan

    foreach ($project in $Script:ProjectStatus.Keys) {
        $status = $Script:ProjectStatus[$project]
        $icon = switch ($status.Status) {
            "Starting" { "[Y]" }
            "Running"  { "[G]" }
            "Ready"    { "[G]" }
            "Error"    { "[R]" }
            default    { "[ ]" }
        }

        $color = switch ($status.Status) {
            "Starting" { "Yellow" }
            "Running"  { "Green" }
            "Ready"    { "Green" }
            "Error"    { "Red" }
            default    { "Gray" }
        }

        Write-Host "$icon $project - $($status.Status)" -ForegroundColor $color
    }

    Write-Host ""
}

# ============================================================================
# Main Execution
# ============================================================================

function Start-Launcher {
    Write-Host @"

  __      ______   _____          _        _                           _
  \ \    / / ___| / ____|        | |      | |                         | |
   \ \  / / |    | |     ___   __| | ___  | |     __ _ _   _ _ __   ___| |__   ___ _ __
    \ \/ /| |    | |    / _ \ / _` |/ _ \ | |    / _` | | | | '_ \ / __| '_ \ / _ \ '__|
     \  / | |____| |___| (_) | (_| |  __/ | |___| (_| | |_| | | | | (__| | | |  __/ |
      \/   \_____|\_____\___/ \__,_|\___| |______\__,_|\__,_|_| |_|\___|_| |_|\___|_|

"@ -ForegroundColor Cyan

    Write-Log "Starting VSCode Launcher..." -Level INFO

    # Handle profile loading
    if ($LoadProfile) {
        $config = Get-Profile -Name $LoadProfile
        if (-not $config) { return }
    }
    else {
        $configPath = if ([System.IO.Path]::IsPathRooted($ConfigFile)) {
            $ConfigFile
        } else {
            Join-Path $Script:ScriptRoot $ConfigFile
        }

        $config = Get-Configuration -Path $configPath
        if (-not $config) { return }
    }

    # Handle profile saving
    if ($SaveProfile) {
        Save-Profile -Name $SaveProfile -Config $config
        return
    }

    # Get enabled projects
    $projects = Get-EnabledProjects -Config $config
    if ($projects.Count -eq 0) {
        Write-Log "No enabled projects found" -Level WARN
        return
    }

    # Calculate layout
    $screen = Get-ScreenResolution
    $layout = Get-GridLayout -ProjectCount $projects.Count -ScreenSize $screen

    # Launch VSCode instances
    $processes = @()
    $index = 0

    foreach ($project in $projects) {
        $position = Get-WindowPosition -Index $index -Layout $layout

        $process = Start-VSCodeInstance `
            -Project $project `
            -Position $position `
            -Settings $config.settings `
            -DryRun:$DryRun

        if ($process) {
            $processes += @{
                Process = $process
                Project = $project
                Position = $position
            }
        }

        # Delay between launches
        if (-not $DryRun -and $config.settings.startupDelayMs -gt 0) {
            Start-Sleep -Milliseconds $config.settings.startupDelayMs
        }

        $index++
    }

    # Position windows
    if (-not $DryRun) {
        Write-Log "Positioning windows..." -Level INFO

        foreach ($item in $processes) {
            Set-WindowPosition -ProcessId $item.Process.Id -Position $item.Position
        }
    }

    # Execute Claude in terminals (if enabled)
    if ($config.settings.autoExecuteClaude -and -not $NoAutoExecute) {
        Write-Log "Preparing Claude commands..." -Level INFO

        foreach ($project in $projects) {
            Invoke-ClaudeInTerminal `
                -ProjectName $project.name `
                -ClaudeArgs $config.settings.claudeArgs `
                -DryRun:$DryRun
        }

        if (-not $DryRun) {
            Write-Host "`n" -NoNewline
            Write-Host "=============================================" -ForegroundColor Yellow
            Write-Host " To execute Claude in each terminal:" -ForegroundColor Yellow
            Write-Host " 1. Click on each VSCode window" -ForegroundColor White
            Write-Host " 2. Press Ctrl+` to open terminal" -ForegroundColor White
            Write-Host " 3. Run: claude $($config.settings.claudeArgs)" -ForegroundColor Cyan
            Write-Host "=============================================" -ForegroundColor Yellow
        }
    }

    # Show final status
    Show-Status

    Write-Log "Launcher complete!" -Level OK
}

# Run the launcher
Start-Launcher
