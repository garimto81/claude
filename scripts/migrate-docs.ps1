# migrate-docs.ps1 - PRD document migration script
# Usage: .\migrate-docs.ps1 -Namespace HUB -DryRun
#        .\migrate-docs.ps1 -Namespace ALL

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("MAIN", "HUB", "FT", "SUB", "AE", "ALL")]
    [string]$Namespace,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RootPath = "C:\claude"
$UnifiedPath = "$RootPath\docs\unified"

$Namespaces = @{
    "MAIN" = @{
        Source = "$RootPath\tasks\prds"
        Pattern = "PRD-*.md"
        Transform = { param($file)
            $num = [regex]::Match($file.Name, 'PRD-(\d{4})').Groups[1].Value
            $slug = $file.Name -replace 'PRD-\d{4}-?', '' -replace '\.md$', ''
            if ($slug) { "MAIN-$num-$slug.md" } else { "MAIN-$num.md" }
        }
    }
    "HUB" = @{
        Source = "$RootPath\automation_hub\tasks\prds"
        Pattern = "PRD-*.md"
        Transform = { param($file)
            $num = [regex]::Match($file.Name, 'PRD-(\d{4})').Groups[1].Value
            $slug = $file.Name -replace 'PRD-\d{4}-?', '' -replace '\.md$', ''
            if ($slug) { "HUB-$num-$slug.md" } else { "HUB-$num.md" }
        }
    }
    "FT" = @{
        Source = "$RootPath\automation_feature_table\tasks\prds"
        Pattern = "PRD-*.md"
        Transform = { param($file)
            $num = [regex]::Match($file.Name, 'PRD-(\d{4})').Groups[1].Value
            $slug = $file.Name -replace 'PRD-\d{4}-?', '' -replace '\.md$', ''
            if ($slug) { "FT-$num-$slug.md" } else { "FT-$num.md" }
        }
    }
    "SUB" = @{
        Source = "$RootPath\automation_sub\tasks\prds"
        Pattern = "*.md"
        Filter = { param($file) $file.Name -match '^\d{4}-prd-' }
        Transform = { param($file)
            $num = [regex]::Match($file.Name, '^(\d{4})').Groups[1].Value
            $slug = $file.Name -replace '^\d{4}-prd-', '' -replace '\.md$', ''
            "SUB-$num-$slug.md"
        }
    }
    "AE" = @{
        Source = "$RootPath\automation_ae\tasks\prds"
        Pattern = "*.md"
        Filter = { param($file) $file.Name -match '(^\d{4}-prd-|^PRD-)' }
        Transform = { param($file)
            if ($file.Name -match '^PRD-(\d{4})-(.+)\.md$') {
                $num = $Matches[1]
                $slug = $Matches[2]
                "AE-$num-$slug.md"
            } elseif ($file.Name -match '^(\d{4})-prd-(.+)\.md$') {
                $num = $Matches[1]
                $slug = $Matches[2]
                "AE-$num-$slug.md"
            } else {
                $file.Name
            }
        }
    }
}

function Update-InternalLinks {
    param([string]$Content, [string]$Ns)
    $Content = $Content -replace '\./PRD-(\d{4})-', "./$Ns-`$1-"
    $Content = $Content -replace '\./PRD-(\d{4})\.md', "./$Ns-`$1.md"
    $Content = $Content -replace '\.\./\.\./docs/images/prd-(\d{4})', "/docs/unified/images/$($Ns.ToLower())-`$1"
    $Content = $Content -replace '\.\./docs/images/prd-(\d{4})', "/docs/unified/images/$($Ns.ToLower())-`$1"
    $Content = $Content -replace 'docs/checklists/PRD-(\d{4})', "docs/unified/checklists/$Ns/$Ns-`$1"
    return $Content
}

function Migrate-Namespace {
    param([string]$Ns)

    $config = $Namespaces[$Ns]
    $targetDir = "$UnifiedPath\prds\$Ns"

    Write-Host ""
    Write-Host "=== Migrating $Ns ===" -ForegroundColor Cyan

    if (-not (Test-Path $config.Source)) {
        Write-Host "Source directory not found: $($config.Source)" -ForegroundColor Yellow
        return
    }

    $files = Get-ChildItem -Path $config.Source -Filter $config.Pattern -File
    if ($config.Filter) {
        $files = $files | Where-Object { & $config.Filter $_ }
    }

    Write-Host "Found files: $($files.Count)"

    foreach ($file in $files) {
        $newName = & $config.Transform $file
        $targetPath = "$targetDir\$newName"

        Write-Host "  $($file.Name) -> $newName" -ForegroundColor Green

        if (-not $DryRun) {
            $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
            $updatedContent = Update-InternalLinks -Content $content -Ns $Ns

            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }

            Set-Content -Path $targetPath -Value $updatedContent -Encoding UTF8
        }
    }
}

Write-Host "PRD Document Migration" -ForegroundColor Yellow
Write-Host "Root: $RootPath"
Write-Host "Target: $UnifiedPath"
if ($DryRun) {
    Write-Host "[DRY RUN MODE]" -ForegroundColor Magenta
}

if ($Namespace -eq "ALL") {
    @("HUB", "FT", "AE", "SUB", "MAIN") | ForEach-Object { Migrate-Namespace -Ns $_ }
} else {
    Migrate-Namespace -Ns $Namespace
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
