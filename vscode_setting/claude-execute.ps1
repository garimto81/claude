<#
.SYNOPSIS
    Claude Execute - 현재 실행 중인 모든 VSCode 터미널에 Claude 명령어 자동 실행

.PARAMETER ClaudeArgs
    Claude 명령어 인자 (기본값: --dangerously-skip-permissions)

.PARAMETER DryRun
    실제 실행 없이 동작 확인

.EXAMPLE
    ./claude-execute.ps1
    ./claude-execute.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [string]$ClaudeArgs = "--dangerously-skip-permissions",
    [switch]$DryRun,
    [int]$Delay = 1500
)

# Windows API (unique name to avoid conflicts)
$typeName = "WinAPI_$(Get-Random)"
$typeCode = @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class $typeName {
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

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public const int SW_RESTORE = 9;
}
"@
Add-Type -TypeDefinition $typeCode -ErrorAction SilentlyContinue

$WShell = New-Object -ComObject WScript.Shell

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "HH:mm:ss"
    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        "DRY"   { "Magenta" }
        default { "White" }
    }
    Write-Host "[$ts] [$Level] $Message" -ForegroundColor $color
}

function Get-VSCodeWindows {
    $windows = [System.Collections.ArrayList]::new()

    # EnumWindows를 사용하여 모든 VSCode 창 찾기
    $callback = {
        param([IntPtr]$hwnd, [IntPtr]$lParam)

        $visible = [bool]([System.Runtime.InteropServices.Marshal]::ReadInt32(
            [System.Runtime.InteropServices.Marshal]::GetFunctionPointerForDelegate(
                [Func[IntPtr,bool]]{ param($h)
                    Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);' -Name 'U' -Namespace 'W' -PassThru -ErrorAction SilentlyContinue
                    return [W.U]::IsWindowVisible($h)
                }
            )
        ))

        return $true
    }

    # 대안: Get-Process로 모든 Code 프로세스 찾고 UI Automation 사용
    # 또는 단순히 타이틀로 창 찾기

    # PowerShell에서 직접 창 열거
    $source = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public class VSCodeFinder {
    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static List<WindowInfo> FindVSCodeWindows() {
        var result = new List<WindowInfo>();

        EnumWindows((hwnd, lParam) => {
            if (!IsWindowVisible(hwnd)) return true;

            StringBuilder title = new StringBuilder(512);
            GetWindowText(hwnd, title, 512);
            string titleStr = title.ToString();

            if (titleStr.Contains("Visual Studio Code")) {
                uint pid;
                GetWindowThreadProcessId(hwnd, out pid);
                result.Add(new WindowInfo {
                    Handle = hwnd.ToInt64(),
                    Title = titleStr,
                    PID = pid
                });
            }
            return true;
        }, IntPtr.Zero);

        return result;
    }

    public class WindowInfo {
        public long Handle { get; set; }
        public string Title { get; set; }
        public uint PID { get; set; }
    }
}
'@

    try {
        Add-Type -TypeDefinition $source -ErrorAction SilentlyContinue
    } catch {}

    $foundWindows = [VSCodeFinder]::FindVSCodeWindows()

    foreach ($win in $foundWindows) {
        $title = $win.Title

        # Extract project name from title
        $projectName = ""
        if ($title -match '^(.+?) - (.+?) - Visual Studio Code$') {
            $projectName = $Matches[2]
        }
        elseif ($title -match '^(.+?) - Visual Studio Code$') {
            $projectName = $Matches[1]
        }
        else {
            $projectName = $title -replace ' - Visual Studio Code$', ''
        }

        $windows.Add([PSCustomObject]@{
            Handle = [IntPtr]::new($win.Handle)
            Title = $title
            ProjectName = $projectName
            PID = $win.PID
        }) | Out-Null
    }

    return $windows
}

function Send-ClaudeCommand {
    param([IntPtr]$Handle, [string]$ProjectName, [string]$Args)

    # Restore and activate window
    Add-Type -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
'@ -Name 'Win32' -Namespace 'Native' -ErrorAction SilentlyContinue

    [Native.Win32]::ShowWindow($Handle, 9) | Out-Null  # SW_RESTORE
    Start-Sleep -Milliseconds 300
    [Native.Win32]::SetForegroundWindow($Handle) | Out-Null
    Start-Sleep -Milliseconds 500

    # Focus on existing terminal (via Command Palette)
    # Ctrl+Shift+P -> "Terminal: Focus on Terminal View"
    $WShell.SendKeys("^+p")
    Start-Sleep -Milliseconds 400
    $WShell.SendKeys("Terminal: Focus")
    Start-Sleep -Milliseconds 300
    $WShell.SendKeys("{ENTER}")
    Start-Sleep -Milliseconds 500

    # Type command
    $command = "claude $Args"
    $WShell.SendKeys($command)
    Start-Sleep -Milliseconds 300

    # Press Enter
    $WShell.SendKeys("{ENTER}")

    Write-Log "Claude started: $ProjectName" -Level OK
}

# ===== Main =====
Write-Host ""
Write-Host "  Claude Execute - Dynamic VSCode Claude Executor v1.0.0" -ForegroundColor Cyan
Write-Host ""

Write-Log "Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'LIVE' })"
Write-Log "Claude Args: $ClaudeArgs"
Write-Host ""

# Phase 1: Detect VSCode windows
Write-Log "Phase 1: Detecting VSCode windows..." -Level INFO

$vscodeWindows = @(Get-VSCodeWindows)

if ($vscodeWindows.Count -eq 0) {
    Write-Log "No VSCode windows found." -Level WARN
    exit 0
}

Write-Log "Found $($vscodeWindows.Count) VSCode window(s)" -Level OK
Write-Host ""

# Display detected windows
Write-Host "  # | Project                        | PID" -ForegroundColor Gray
Write-Host "  --|--------------------------------|----------" -ForegroundColor Gray

$idx = 1
foreach ($w in $vscodeWindows) {
    $name = if ($w.ProjectName.Length -gt 30) { $w.ProjectName.Substring(0,30) } else { $w.ProjectName.PadRight(30) }
    Write-Host "  $idx | $name | $($w.PID)" -ForegroundColor White
    $idx++
}

Write-Host ""

# Phase 2: Execute Claude commands
Write-Log "Phase 2: Executing Claude commands..." -Level INFO

$successCount = 0
foreach ($w in $vscodeWindows) {
    if ($DryRun) {
        Write-Log "[DRY-RUN] Would execute: 'claude $ClaudeArgs' in '$($w.ProjectName)'" -Level DRY
    }
    else {
        try {
            Send-ClaudeCommand -Handle $w.Handle -ProjectName $w.ProjectName -Args $ClaudeArgs
            $successCount++
            Start-Sleep -Milliseconds $Delay
        }
        catch {
            Write-Log "Failed: $($w.ProjectName) - $_" -Level ERROR
        }
    }
}

Write-Host ""
Write-Log "=== Complete ===" -Level OK

if ($DryRun) {
    Write-Log "DRY-RUN: Would execute on $($vscodeWindows.Count) window(s)"
}
else {
    Write-Log "Success: $successCount / $($vscodeWindows.Count) projects"
}
