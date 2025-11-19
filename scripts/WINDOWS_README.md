# Windows 전용 스크립트 가이드

**버전**: 5.4.0 (Windows Edition)
**플랫폼**: Windows 10/11 + PowerShell 5.1+

---

## 🎯 개요

이 디렉토리는 **Windows 전용** Phase 검증 스크립트를 제공합니다.

### Legacy Bash Scripts (Deprecated)

```
⚠️  다음 Bash scripts는 deprecated되었습니다:
   - validate-phase-*.sh (8개)
   - setup-github-labels.sh
   - github-issue-dev.sh
   - phase-status.sh

   → PowerShell 버전 (.ps1) 사용하세요!
```

---

## 📋 사용 가능한 스크립트

### Phase Validation Scripts

| 스크립트 | 목적 | 사용법 |
|---------|------|--------|
| `validate-phase-0.ps1` | PRD 파일 확인 | `.\validate-phase-0.ps1 0001` |
| `validate-phase-0.5.ps1` | Task List 확인 | `.\validate-phase-0.5.ps1 0001` |
| `validate-phase-1.ps1` | 1:1 test pairing | `.\validate-phase-1.ps1` |
| `validate-phase-2.ps1` | 테스트 실행 | `.\validate-phase-2.ps1` |
| `validate-phase-3.ps1` | 버전 & CHANGELOG | `.\validate-phase-3.ps1 v1.2.0` |
| `validate-phase-5.ps1` | E2E & Security | `.\validate-phase-5.ps1` |
| `validate-phase-6.ps1` | Deployment 준비 | `.\validate-phase-6.ps1` |

### GitHub Integration Scripts

| 스크립트 | 목적 | 사용법 |
|---------|------|--------|
| `setup-github-labels.ps1` | GitHub 라벨 생성 | `.\setup-github-labels.ps1` |
| `github-issue-dev.ps1` | Issue → 브랜치 → PR | `.\github-issue-dev.ps1 123` |
| `phase-status.ps1` | 전체 Phase 상태 | `.\phase-status.ps1` |

### Batch Wrapper (편의성)

| 파일 | 목적 | 사용법 |
|------|------|--------|
| `validate-phase.bat` | PowerShell wrapper | `validate-phase.bat 0 0001` |

---

## 🚀 Quick Start

### 1. PowerShell 실행 정책 확인

```powershell
# 현재 정책 확인
Get-ExecutionPolicy

# RemoteSigned로 변경 (권장)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Phase 0 검증 예시

```powershell
# PRD 작성 후
cd C:\claude\claude-code-config
.\scripts\validate-phase-0.ps1 0001

# 출력:
# ✅ Phase 0 검증 통과
#    PRD 파일: C:\...\tasks\prds\0001-prd-auth.md
#    라인 수: 75
```

### 3. GitHub Labels 설정

```powershell
# gh CLI 설치 (winget 사용)
winget install GitHub.cli

# 인증
gh auth login

# 라벨 생성
cd C:\claude\claude-code-config
.\scripts\setup-github-labels.ps1

# 출력:
# ✅ GitHub Labels 설정 완료
#    생성: 11개
```

### 4. Issue 작업 시작

```powershell
# Issue #123 작업 시작
.\scripts\github-issue-dev.ps1 123

# 자동으로:
# - feature/issue-123 브랜치 생성
# - Draft PR 생성
# - 작업 준비 완료
```

---

## 📝 실행 예시

### Phase 0-6 전체 검증 흐름

```powershell
# Phase 0: PRD
.\scripts\validate-phase-0.ps1 0001

# Phase 0.5: Task List
.\scripts\validate-phase-0.5.ps1 0001

# Phase 1: Implementation
.\scripts\validate-phase-1.ps1

# Phase 2: Testing
.\scripts\validate-phase-2.ps1

# Phase 3: Versioning
.\scripts\validate-phase-3.ps1 v1.2.0

# Phase 5: E2E & Security
.\scripts\validate-phase-5.ps1

# Phase 6: Deployment
.\scripts\validate-phase-6.ps1
```

### Batch Wrapper 사용

```cmd
# CMD 또는 PowerShell에서
cd C:\claude\claude-code-config\scripts

validate-phase.bat 0 0001
validate-phase.bat 1
validate-phase.bat 2
validate-phase.bat 3 v1.2.0
```

---

## 🔧 Troubleshooting

### 문제 1: "스크립트 실행이 차단되었습니다"

**해결**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 문제 2: "gh 명령을 찾을 수 없습니다"

**해결**:
```powershell
# winget 사용
winget install GitHub.cli

# 또는 Scoop 사용
scoop install gh
```

### 문제 3: PowerShell 5.1 이하 버전

**확인**:
```powershell
$PSVersionTable.PSVersion
```

**해결**: PowerShell 7+ 설치 (권장)
```powershell
winget install Microsoft.PowerShell
```

### 문제 4: "파일을 찾을 수 없습니다"

**원인**: 상대 경로 문제

**해결**:
```powershell
# 올바른 방법 (프로젝트 루트에서)
.\scripts\validate-phase-0.ps1 0001

# 잘못된 방법
validate-phase-0.ps1 0001  # ❌
```

---

## 🆚 Bash vs PowerShell 차이

| 기능 | Bash (Legacy) | PowerShell (New) |
|------|---------------|------------------|
| Platform | Git Bash 필요 | Windows 네이티브 |
| 색상 출력 | ❌ 제한적 | ✅ 완전 지원 |
| 에러 처리 | `set -e` | `$ErrorActionPreference` |
| 경로 표기 | `/` (Unix) | `\` (Windows) |
| 파이프 | `\|` | `\|` (동일) |
| 변수 | `$VAR` | `$VAR` (동일) |

---

## 📚 추가 리소스

**Universal Validator** (크로스 플랫폼):
```powershell
# Python 기반 (Windows/Mac/Linux)
python scripts\validate_phase_universal.py 0 0001
python scripts\validate_phase_universal.py 1
python scripts\validate_phase_universal.py 2 --coverage 80
```

**문서**:
- [CLAUDE.md](../CLAUDE.md) - Phase 0-6 전체 가이드
- [Phase Validation Guide](../docs/PHASE_VALIDATION_GUIDE.md) - 검증 상세
- [Quick Start](../docs/QUICK_START_GUIDE.md) - 5분 시작 가이드

---

## 🔄 Migration from Bash

기존 Bash scripts 사용자를 위한 마이그레이션 가이드:

| Bash (Old) | PowerShell (New) |
|------------|------------------|
| `bash scripts/validate-phase-0.sh 0001` | `.\scripts\validate-phase-0.ps1 0001` |
| `bash scripts/validate-phase-1.sh` | `.\scripts\validate-phase-1.ps1` |
| `bash scripts/setup-github-labels.sh` | `.\scripts\setup-github-labels.ps1` |
| `bash scripts/github-issue-dev.sh 123` | `.\scripts\github-issue-dev.ps1 123` |

**차이점**:
- ✅ Git Bash 불필요
- ✅ 더 나은 Windows 통합
- ✅ 컬러 출력 개선
- ✅ 에러 메시지 명확화

---

## ⚡ 성능

PowerShell 스크립트는 Windows 환경에서 Bash 대비:
- **실행 속도**: 20-30% 빠름 (Git Bash 오버헤드 없음)
- **에러 감지**: 즉시 감지 (`$ErrorActionPreference = "Stop"`)
- **사용자 경험**: 컬러 출력, 이모지 지원

---

**버전**: 5.4.0 (Windows Edition)
**마지막 업데이트**: 2025-01-19
**작성자**: garimto81
**라이센스**: MIT
