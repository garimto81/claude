<#
.SYNOPSIS
    Detect running VSCode instances and extract workspace folders
#>

# Get all VSCode windows with titles
$vscodeWindows = Get-Process -Name 'Code' -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -ne '' -and $_.MainWindowTitle -match 'Visual Studio Code' }

$projects = @()

foreach ($window in $vscodeWindows) {
    $title = $window.MainWindowTitle

    # Extract folder name from title (format: "filename - folder - Visual Studio Code")
    if ($title -match '^(.+?) - (.+?) - Visual Studio Code$') {
        $folderName = $Matches[2]
    }
    elseif ($title -match '^(.+?) - Visual Studio Code$') {
        $folderName = $Matches[1]
    }
    else {
        $folderName = $title -replace ' - Visual Studio Code$', ''
    }

    Write-Host "Found: $folderName (PID: $($window.Id))"

    $projects += @{
        Name = $folderName
        PID = $window.Id
        Title = $title
    }
}

# Also check VSCode's recent workspaces storage
$storagePath = "$env:APPDATA\Code\User\globalStorage\storage.json"
if (Test-Path $storagePath) {
    try {
        $storage = Get-Content $storagePath -Raw | ConvertFrom-Json

        if ($storage.windowsState.lastActiveWindow.folder) {
            Write-Host "`nLast Active Window Folder:"
            Write-Host "  $($storage.windowsState.lastActiveWindow.folder)"
        }

        if ($storage.windowsState.openedWindows) {
            Write-Host "`nOpened Windows from storage.json:"
            foreach ($win in $storage.windowsState.openedWindows) {
                if ($win.folder) {
                    Write-Host "  $($win.folder)"
                }
                if ($win.folderUri) {
                    Write-Host "  $($win.folderUri)"
                }
            }
        }
    }
    catch {
        Write-Host "Could not parse storage.json: $_"
    }
}

# Check workspaceStorage for more accurate paths
$workspaceStoragePath = "$env:APPDATA\Code\User\workspaceStorage"
if (Test-Path $workspaceStoragePath) {
    Write-Host "`nWorkspace Storage Folders:"
    Get-ChildItem $workspaceStoragePath -Directory | ForEach-Object {
        $wsFile = Join-Path $_.FullName "workspace.json"
        if (Test-Path $wsFile) {
            try {
                $ws = Get-Content $wsFile -Raw | ConvertFrom-Json
                if ($ws.folder) {
                    # Decode URI format
                    $folderPath = $ws.folder -replace 'file:///', '' -replace '%3A', ':' -replace '%20', ' '
                    Write-Host "  $folderPath"
                }
            }
            catch {}
        }
    }
}

Write-Host "`n=== Summary ==="
Write-Host "Found $($projects.Count) active VSCode window(s)"
