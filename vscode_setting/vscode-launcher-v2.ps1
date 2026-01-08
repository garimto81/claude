<#
.SYNOPSIS
    Multi-VSCode IDE Launcher with Claude Auto-Execute (v2.0)

.DESCRIPTION
    Launches multiple VSCode instances with configured project folders,
    automatically arranges windows in a grid layout, and executes
    Claude Code in each terminal using SendKeys automation.

.PARAMETER ConfigFile
    Path to the JSON configuration file. Defaults to vscode-projects.json

.PARAMETER SaveProfile
    Save current configuration as a named profile

.PARAMETER LoadProfile
    Load a previously saved profile

.PARAMETER DryRun
    Show what would be done without actually launching

.EXAMPLE
    ./vscode-launcher-v2.ps1

.EXAMPLE
    ./vscode-launcher-v2.ps1 -ConfigFile "my-projects.json"
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
    [switch]$NoAutoExecute,

    [Parameter()]
    [switch]$SkipPositioning
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

$TypeDef = @"
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

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

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
    public const int SM_CXVIRTUALSCREEN = 78;
    public const int SM_CYVIRTUALSCREEN = 79;
    public const int SM_XVIRTUALSCREEN = 76;
    public const int SM_YVIRTUALSCREEN = 77;
    public const uint SWP_NOZORDER = 0x0004;
    public const uint SWP_SHOWWINDOW = 0x0040;
    public const int SW_RESTORE = 9;
}
"@

try {
    Add-Type -TypeDefinition $TypeDef -ErrorAction SilentlyContinue
} catch {
    # Type already exists, continue
}

# Load WScript.Shell for SendKeys
$Script:WShell = New-Object -ComObject WScript.Shell

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

    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
    }

    Write-Host $logMessage -ForegroundColor $color
    Add-Content -Path $Script:LogFile -Value $logMessage -ErrorAction SilentlyContinue
}

# ============================================================================
# Configuration Functions
# ============================================================================

function Get-Configuration {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Write-Log "Configuration file not found: $Path" -Level ERROR

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

    $enabled = @($Config.projects | Where-Object { $_.enabled -eq $true })
    Write-Log "Found $($enabled.Count) enabled projects" -Level INFO
    return $enabled
}

# ============================================================================
# Screen Layout Functions
# ============================================================================

function Get-ScreenResolution {
    # Get virtual screen size (multi-monitor support)
    $width = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CXVIRTUALSCREEN)
    $height = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CYVIRTUALSCREEN)

    if ($width -eq 0 -or $height -eq 0) {
        # Fallback to primary screen
        $width = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CXSCREEN)
        $height = [WindowManager]::GetSystemMetrics([WindowManager]::SM_CYSCREEN)
    }

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

    $cols = [Math]::Ceiling([Math]::Sqrt($ProjectCount))
    $rows = [Math]::Ceiling($ProjectCount / $cols)

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
        [switch]$DryRun
    )

    $name = $Project.name
    $path = $Project.path

    $Script:ProjectStatus[$name] = @{
        Status = "Starting"
        StartTime = Get-Date
        ProcessId = $null
        WindowHandle = $null
    }

    if (-not (Test-Path $path)) {
        Write-Log "Project path does not exist: $path" -Level ERROR
        $Script:ProjectStatus[$name].Status = "Error"
        return $null
    }

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would launch VSCode for '$name' at $path" -Level INFO
        return $null
    }

    try {
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

function Get-VSCodeWindowHandle {
    param([int]$ProcessId)

    $foundHandle = [IntPtr]::Zero
    $script:targetPid = $ProcessId

    $callback = {
        param([IntPtr]$hwnd, [IntPtr]$lParam)

        $windowPid = 0
        [WindowManager]::GetWindowThreadProcessId($hwnd, [ref]$windowPid) | Out-Null

        if ($windowPid -eq $script:targetPid) {
            $title = New-Object System.Text.StringBuilder 256
            [WindowManager]::GetWindowText($hwnd, $title, 256) | Out-Null

            if ($title.ToString() -match "Visual Studio Code") {
                $script:foundHandle = $hwnd
                return $false
            }
        }
        return $true
    }

    $delegate = [WindowManager+EnumWindowsProc]$callback
    [WindowManager]::EnumWindows($delegate, [IntPtr]::Zero) | Out-Null

    return $script:foundHandle
}

function Set-WindowPosition {
    param(
        [int]$ProcessId,
        [hashtable]$Position,
        [int]$MaxAttempts = 20
    )

    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        Start-Sleep -Milliseconds 300

        $hwnd = Get-VSCodeWindowHandle -ProcessId $ProcessId
        if ($hwnd -ne [IntPtr]::Zero) {
            [WindowManager]::ShowWindow($hwnd, [WindowManager]::SW_RESTORE) | Out-Null

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
                return $hwnd
            }
        }
    }

    Write-Log "Could not position window for PID $ProcessId" -Level WARN
    return [IntPtr]::Zero
}

# ============================================================================
# Claude Execution Functions (SendKeys)
# ============================================================================

function Invoke-ClaudeInTerminal {
    param(
        [IntPtr]$WindowHandle,
        [string]$ProjectName,
        [string]$ClaudeArgs,
        [switch]$DryRun
    )

    if ($DryRun) {
        Write-Log "[DRY-RUN] Would execute 'claude $ClaudeArgs' in '$ProjectName'" -Level INFO
        return $true
    }

    if ($WindowHandle -eq [IntPtr]::Zero) {
        Write-Log "No window handle for '$ProjectName'" -Level WARN
        return $false
    }

    try {
        # Bring window to front
        [WindowManager]::SetForegroundWindow($WindowHandle) | Out-Null
        Start-Sleep -Milliseconds 500

        # Open terminal with Ctrl+`
        $Script:WShell.SendKeys("^``")
        Start-Sleep -Milliseconds 1000

        # Type claude command
        $command = "claude $ClaudeArgs"
        $Script:WShell.SendKeys($command)
        Start-Sleep -Milliseconds 200

        # Press Enter
        $Script:WShell.SendKeys("{ENTER}")

        Write-Log "Sent Claude command to '$ProjectName'" -Level OK
        $Script:ProjectStatus[$ProjectName].Status = "Running"
        return $true
    }
    catch {
        Write-Log "Failed to send command to '$ProjectName': $_" -Level ERROR
        return $false
    }
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
    Write-Log "Saved profile '$Name'" -Level OK
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

                                                                          v2.0

"@ -ForegroundColor Cyan

    Write-Log "Starting VSCode Launcher v2.0..." -Level INFO

    # Handle profile
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

    if ($SaveProfile) {
        Save-Profile -Name $SaveProfile -Config $config
        return
    }

    # Get projects
    $projects = @(Get-EnabledProjects -Config $config)
    if ($projects.Count -eq 0) {
        Write-Log "No enabled projects found" -Level WARN
        return
    }

    # Calculate layout
    $screen = Get-ScreenResolution
    $projectCount = [Math]::Max(1, $projects.Count)
    $layout = Get-GridLayout -ProjectCount $projectCount -ScreenSize $screen

    # Phase 1: Launch all VSCode instances
    Write-Log "Phase 1: Launching VSCode instances..." -Level INFO
    $launchedProjects = @()

    foreach ($project in $projects) {
        $process = Start-VSCodeInstance -Project $project -DryRun:$DryRun

        if ($process) {
            $launchedProjects += @{
                Process = $process
                Project = $project
                Index = $launchedProjects.Count
            }
        }

        if (-not $DryRun -and $config.settings.startupDelayMs -gt 0) {
            Start-Sleep -Milliseconds $config.settings.startupDelayMs
        }
    }

    # Phase 2: Position windows
    if (-not $DryRun -and -not $SkipPositioning) {
        Write-Log "Phase 2: Positioning windows..." -Level INFO
        Start-Sleep -Seconds 2  # Wait for windows to fully load

        foreach ($item in $launchedProjects) {
            $position = Get-WindowPosition -Index $item.Index -Layout $layout
            $hwnd = Set-WindowPosition -ProcessId $item.Process.Id -Position $position

            if ($hwnd -ne [IntPtr]::Zero) {
                $Script:ProjectStatus[$item.Project.name].WindowHandle = $hwnd
            }
        }
    }

    # Phase 3: Execute Claude in terminals
    if ($config.settings.autoExecuteClaude -and -not $NoAutoExecute -and -not $DryRun) {
        Write-Log "Phase 3: Executing Claude in terminals..." -Level INFO
        Start-Sleep -Seconds 1

        foreach ($item in $launchedProjects) {
            $hwnd = $Script:ProjectStatus[$item.Project.name].WindowHandle

            if ($hwnd) {
                Invoke-ClaudeInTerminal `
                    -WindowHandle $hwnd `
                    -ProjectName $item.Project.name `
                    -ClaudeArgs $config.settings.claudeArgs

                Start-Sleep -Milliseconds 800
            }
        }
    }
    elseif ($config.settings.autoExecuteClaude -and -not $NoAutoExecute) {
        foreach ($project in $projects) {
            Write-Log "[DRY-RUN] Would execute 'claude $($config.settings.claudeArgs)' in '$($project.name)'" -Level INFO
        }
    }

    # Show status
    Show-Status

    Write-Log "Launcher complete!" -Level OK
}

# Run
Start-Launcher
