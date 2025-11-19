# GitHub Issue로 작업 시작
# Windows PowerShell 전용 버전
# Issue → 브랜치 생성 → Draft PR 자동 생성

param(
    [Parameter(Mandatory=$true)]
    [int]$ISSUE_NUMBER
)

$ErrorActionPreference = "Stop"

Write-Host "GitHub Issue #$ISSUE_NUMBER 작업 시작..." -ForegroundColor Cyan
Write-Host ""

# gh CLI 확인
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 오류: GitHub CLI (gh) 설치 필요" -ForegroundColor Red
    Write-Host "   winget install GitHub.cli"
    exit 1
}

# Issue 정보 가져오기
Write-Host "Issue 정보 가져오는 중..." -ForegroundColor Cyan
$issueData = & gh issue view $ISSUE_NUMBER --json title,labels,number 2>&1 | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 오류: Issue #$ISSUE_NUMBER 없음" -ForegroundColor Red
    exit 1
}

$title = $issueData.title
$branchName = "feature/issue-$ISSUE_NUMBER"

Write-Host "   제목: $title" -ForegroundColor Green
Write-Host "   브랜치: $branchName" -ForegroundColor Green

# 브랜치 생성
Write-Host ""
Write-Host "브랜치 생성 중..." -ForegroundColor Cyan

$currentBranch = & git branch --show-current 2>&1
if ($currentBranch -eq $branchName) {
    Write-Host "   브랜치 이미 존재: $branchName" -ForegroundColor Yellow
} else {
    & git checkout -b $branchName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   브랜치 생성 완료: $branchName ✓" -ForegroundColor Green
    } else {
        Write-Host "❌ 오류: 브랜치 생성 실패" -ForegroundColor Red
        exit 1
    }
}

# Draft PR 생성
Write-Host ""
Write-Host "Draft PR 생성 중..." -ForegroundColor Cyan

$prTitle = "WIP: $title"
$prBody = @"
Closes #$ISSUE_NUMBER

## Changes
- [ ] TODO: 변경 사항 작성

## Checklist
- [ ] Tests pass
- [ ] CHANGELOG updated
- [ ] Documentation updated
"@

# 빈 커밋 생성 (PR 생성용)
& git commit --allow-empty -m "chore: Start work on #$ISSUE_NUMBER" 2>&1 | Out-Null
& git push -u origin $branchName 2>&1 | Out-Null

# Draft PR 생성
$prUrl = & gh pr create --title $prTitle --body $prBody --draft --assignee "@me" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Draft PR 생성 완료 ✓" -ForegroundColor Green
    Write-Host "   URL: $prUrl"
} else {
    if ($prUrl -match "already exists") {
        Write-Host "   PR 이미 존재 (스킵)" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  경고: PR 생성 실패 (수동 생성 필요)" -ForegroundColor Yellow
    }
}

# 성공
Write-Host ""
Write-Host "✅ 작업 환경 준비 완료" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "   1. 코드 작성"
Write-Host "   2. 커밋: git commit -m 'feat: ...'"
Write-Host "   3. 푸시: git push"
Write-Host "   4. Draft 해제: gh pr ready"
