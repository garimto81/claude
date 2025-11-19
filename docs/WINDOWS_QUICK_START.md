# Windows Quick Start Guide

**버전**: 5.4.0-Windows
**플랫폼**: Windows 10/11
**소요 시간**: 15분

---

## 🎯 목표

이 가이드를 완료하면:
- ✅ Windows 전용 Phase 0-6 워크플로우 이해
- ✅ PowerShell scripts 실행 가능
- ✅ 첫 PRD 작성 및 검증 완료
- ✅ GitHub integration 설정 완료

---

## 📋 사전 요구사항

### 필수

| 항목 | 설치 명령어 | 확인 |
|------|------------|------|
| **Python 3.8+** | `winget install Python.Python.3.12` | `python --version` |
| **Git** | `winget install Git.Git` | `git --version` |
| **PowerShell 5.1+** | Windows 내장 (또는 `winget install Microsoft.PowerShell`) | `$PSVersionTable.PSVersion` |

### 선택 (GitHub 사용 시)

| 항목 | 설치 명령어 | 확인 |
|------|------------|------|
| **GitHub CLI** | `winget install GitHub.cli` | `gh --version` |

---

## 🚀 Step 1: 레포지토리 설정 (2분)

### 1.1 클론 (이미 완료된 경우 스킵)

```powershell
# 적절한 경로로 이동
cd C:\Projects

# 클론 (예시)
git clone https://github.com/your-username/claude-code-config.git
cd claude-code-config
```

### 1.2 Python 의존성 설치

```powershell
# requirements.txt 확인
if (Test-Path requirements.txt) {
    pip install -r requirements.txt
}
```

### 1.3 PowerShell 실행 정책 설정

```powershell
# 현재 정책 확인
Get-ExecutionPolicy

# RemoteSigned로 변경 (권장)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**출력 예시**:
```
ExecutionPolicy: RemoteSigned
```

---

## 📝 Step 2: 첫 PRD 작성 (5분)

### 2.1 PRD 디렉토리 생성

```powershell
# tasks/prds 디렉토리 생성
if (-not (Test-Path "tasks\prds")) {
    New-Item -ItemType Directory -Path "tasks\prds"
}
```

### 2.2 PRD 파일 작성

```powershell
# 텍스트 에디터로 PRD 작성
notepad tasks\prds\0001-prd-hello-world.md
```

**최소 PRD 템플릿** (복사하여 사용):
```markdown
# PRD-0001: Hello World Feature

## 목적
첫 번째 기능 개발 연습

## 핵심 기능
- [ ] "Hello World" 출력 함수
- [ ] 단위 테스트 작성

## 수락 기준
- ✅ 함수가 "Hello, World!" 반환
- ✅ 테스트 커버리지 100%

## 우선순위
P0 (최우선)

## 추정 시간
1시간
```

---

## ✅ Step 3: Phase 0 검증 (1분)

```powershell
# Phase 0 검증 실행
.\scripts\validate-phase-0.ps1 0001
```

**성공 출력**:
```
✅ Phase 0 검증 통과
   PRD 파일: C:\...\tasks\prds\0001-prd-hello-world.md
   라인 수: 20

다음 단계: Phase 0.5 (Task List)
   python scripts\validate_phase_universal.py 0.5 0001
```

**실패 시**:
- PRD 파일이 `tasks\prds\0001-prd-*.md` 형식인지 확인
- 파일이 50줄 이상인지 확인 (권장)
- `## 목적` 과 `## 핵심 기능` 섹션이 있는지 확인

---

## 📋 Step 4: Task List 생성 (2분)

### 4.1 Claude Code와 대화로 생성 (권장)

```
사용자: "tasks/prds/0001-prd-hello-world.md 읽고 Task List 작성해줘"

Claude Code: [Task List 생성 및 저장]
```

### 4.2 Python 스크립트 사용 (선택)

```powershell
# ANTHROPIC_API_KEY 필요
python scripts\generate_tasks_ai.py tasks\prds\0001-prd-hello-world.md
```

### 4.3 Phase 0.5 검증

```powershell
.\scripts\validate-phase-0.5.ps1 0001
```

**성공 출력**:
```
✅ Phase 0.5 검증 통과
   Task List 파일: C:\...\tasks\0001-tasks-hello-world.md
   Task 0.0: 완료 ✓
   진행률: 1/5 (20%)

다음 단계: Phase 1 (Implementation)
   python scripts\validate_phase_universal.py 1
```

---

## 🔧 Step 5: GitHub Integration (선택, 3분)

### 5.1 GitHub CLI 인증

```powershell
# 인증 확인
gh auth status

# 인증 필요 시
gh auth login
```

### 5.2 GitHub Labels 설정

```powershell
# Phase 0-6 라벨 자동 생성
.\scripts\setup-github-labels.ps1
```

**출력**:
```
✅ GitHub Labels 설정 완료
   생성: 11개
   기존: 0개

다음 단계:
   1. GitHub Issue 생성 (gh issue create)
   2. Phase 라벨 적용
   3. 작업 시작 (.\scripts\github-issue-dev.ps1 <ISSUE_NUMBER>)
```

---

## 🧪 Step 6: 진행 상황 확인 (1분)

```powershell
# 전체 Phase 상태 확인
.\scripts\phase-status.ps1
```

**출력 예시**:
```
Phase 진행 상태 확인
============================================================

PRD-0001: hello-world
------------------------------------------------------------
   Phase 0 (PRD): ✅ 완료 (20 lines)
   Phase 0.5 (Tasks): ✅ 완료 (1/5, 20%)

============================================================

상세 검증:
   python scripts\validate_phase_universal.py <PHASE> [ARGS]
```

---

## 🎉 완료 체크리스트

- [ ] **Step 1**: Python, Git, PowerShell 설치 확인
- [ ] **Step 1**: PowerShell 실행 정책 설정 (RemoteSigned)
- [ ] **Step 2**: 첫 PRD 작성 (`tasks\prds\0001-prd-*.md`)
- [ ] **Step 3**: Phase 0 검증 통과 (`.\scripts\validate-phase-0.ps1`)
- [ ] **Step 4**: Task List 생성 (`tasks\0001-tasks-*.md`)
- [ ] **Step 4**: Phase 0.5 검증 통과 (`.\scripts\validate-phase-0.5.ps1`)
- [ ] **Step 5**: (선택) GitHub Labels 설정
- [ ] **Step 6**: Phase 상태 확인 (`.\scripts\phase-status.ps1`)

---

## 📚 다음 단계

### 추천 학습 순서

1. **Workflow Recipes** (즉시 사용 가능한 패턴)
   - [recipe-debugging-tdd.md](WORKFLOWS/recipe-debugging-tdd.md) - 15분 버그 수정
   - [recipe-new-feature.md](WORKFLOWS/recipe-new-feature.md) - 30-60분 기능 개발

2. **Phase 1-6 실습**
   - Phase 1: 코드 작성 + 1:1 테스트 pairing
   - Phase 2: 테스트 실행 (`pytest`, `npm test`)
   - Phase 3: 버전 태그 (`v1.0.0`)
   - Phase 4: Git commit + Auto PR
   - Phase 5: E2E + Security 테스트
   - Phase 6: Deployment

3. **고급 기능**
   - [Plugin System](PLUGIN_SYSTEM_GUIDE.md) - 122+ agents
   - [Agent Optimizer](AGENT_OPTIMIZER_GUIDE.md) - 자동 최적화

---

## 🔧 Troubleshooting

### 문제 1: "스크립트를 로드할 수 없습니다"

**에러**:
```
.\scripts\validate-phase-0.ps1 : 이 시스템에서 스크립트를 실행할 수 없으므로 파일을 로드할 수 없습니다.
```

**해결**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 문제 2: "python 명령을 찾을 수 없습니다"

**해결**:
```powershell
# Python 설치
winget install Python.Python.3.12

# PATH 확인
$env:PATH -split ';' | Select-String Python

# PowerShell 재시작
```

### 문제 3: "tasks\prds 디렉토리가 없습니다"

**해결**:
```powershell
# 디렉토리 생성
New-Item -ItemType Directory -Path "tasks\prds" -Force
```

### 문제 4: "gh 명령을 찾을 수 없습니다"

**해결** (선택 - GitHub 사용 시에만):
```powershell
winget install GitHub.cli
```

---

## 💡 팁 & 트릭

### Tip 1: Batch Wrapper 사용

```cmd
# 더 짧은 명령어
cd scripts
validate-phase.bat 0 0001
validate-phase.bat 0.5 0001
```

### Tip 2: PowerShell Alias 설정

```powershell
# $PROFILE 편집
notepad $PROFILE

# 추가:
Set-Alias vp0 "C:\claude\claude-code-config\scripts\validate-phase-0.ps1"
Set-Alias vp1 "C:\claude\claude-code-config\scripts\validate-phase-1.ps1"

# 사용:
vp0 0001
vp1
```

### Tip 3: VSCode Tasks 설정

`.vscode\tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate Phase 0",
      "type": "shell",
      "command": "pwsh",
      "args": [
        "-File",
        "${workspaceFolder}\\scripts\\validate-phase-0.ps1",
        "0001"
      ]
    }
  ]
}
```

**사용**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Validate Phase 0"

---

## 📖 참고 문서

**핵심 문서**:
- [CLAUDE.md](../CLAUDE.md) - Phase 0-6 완전 가이드
- [scripts/WINDOWS_README.md](../scripts/WINDOWS_README.md) - PowerShell 스크립트 상세

**PRD 가이드**:
- [PRD_GUIDE_MINIMAL.md](guides/PRD_GUIDE_MINIMAL.md) - 10분, ~1270 tokens
- [PRD_GUIDE_STANDARD.md](guides/PRD_GUIDE_STANDARD.md) - 20-30분
- [PRD_GUIDE_JUNIOR.md](guides/PRD_GUIDE_JUNIOR.md) - 40-60분

**Workflow Recipes**:
- [recipe-debugging-tdd.md](WORKFLOWS/recipe-debugging-tdd.md)
- [recipe-legacy-analysis.md](WORKFLOWS/recipe-legacy-analysis.md)
- [recipe-daily-routine.md](WORKFLOWS/recipe-daily-routine.md)
- [recipe-new-feature.md](WORKFLOWS/recipe-new-feature.md)

---

## 🆘 도움 받기

**문제가 해결되지 않으면**:
1. [GitHub Issues](https://github.com/garimto81/claude-code-config/issues) - 버그 리포트
2. Claude Code에게 직접 질문: "Windows에서 Phase 0 검증이 실패해"
3. CLAUDE.md 재확인: 전체 워크플로우 문서

---

**작성**: 2025-01-19
**버전**: 5.4.0-Windows
**작성자**: garimto81
**라이센스**: MIT

**다음 문서**: [Workflow Recipes](WORKFLOWS/README.md) → 실전 패턴 학습
