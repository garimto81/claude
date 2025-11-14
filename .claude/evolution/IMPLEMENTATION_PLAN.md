# Agent Quality Scoring - Implementation Plan

**버전**: 2.0.0
**업데이트**: 2025-01-14

---

## 🎯 목표

서브 레포에서 agent/스킬 사용 시 품질을 **5점 만점 게임화 점수 시스템**으로 추적

---

## 📊 점수 시스템

```
시작 점수: 5.0/5.0 (만점)
✅ 1회차 통과 → 5.0 (만점 유지)
❌ 실패 → -1.0 페널티
🔧 수정 후 통과 → +0.5 복구
❌ 5번 실패 → 0.0 (최악)
```

---

## 🏗️ 구현 단계

### Phase 1: 서브 레포 설정 (각 프로젝트마다)

#### 1.1. 추적 스크립트 설치

```bash
# 전역 레포에서 서브 레포로 복사
cd ~/AI/sso-nextjs  # 또는 다른 서브 레포

# Bash 버전
cp ~/AI/claude01/.claude/evolution/templates/track.sh .claude/track.sh
chmod +x .claude/track.sh

# Python 버전 (권장)
cp ~/AI/claude01/.claude/evolution/templates/track.py .claude/track.py
chmod +x .claude/track.py
```

#### 1.2. 사용법

```bash
# Agent 실행 후 결과 기록

# 통과 시
.claude/track.sh "context7-engineer" "Phase 0" "Verify React docs" "pass"

# 실패 시
.claude/track.sh "debugger" "Phase 1" "Fix TypeError" "fail" "Type mismatch"

# 수정 후 통과
.claude/track.sh "debugger" "Phase 1" "Fix TypeError" "pass"
```

#### 1.3. 로그 파일 생성

자동으로 `.agent-quality.jsonl` 파일 생성:

```jsonl
{"timestamp":"2025-01-14T10:30:00Z","agent":"context7-engineer","phase":"Phase 0","task":"Verify React docs","attempt":1,"status":"pass","score":5.0,"duration":0}
{"timestamp":"2025-01-14T11:00:00Z","agent":"debugger","phase":"Phase 1","task":"Fix TypeError","attempt":1,"status":"fail","score":4.0,"error":"Type mismatch"}
{"timestamp":"2025-01-14T11:30:00Z","agent":"debugger","phase":"Phase 1","task":"Fix TypeError","attempt":2,"status":"pass","score":4.5,"fixed":true}
```

---

### Phase 2: 전역 레포 설정 (claude01)

#### 2.1. 레포 설정 업데이트

```bash
# 전역 레포
cd ~/AI/claude01

# 레포 설정 편집
vim .claude/evolution/config/repo-config.json
```

**추가 예시**:
```json
{
  "repos": [
    {
      "name": "sso-nextjs",
      "path": "~/AI/sso-nextjs",
      "description": "SSO system",
      "enabled": true
    },
    {
      "name": "my-new-project",
      "path": "~/AI/my-new-project",
      "description": "My project",
      "enabled": true
    }
  ]
}
```

#### 2.2. 로그 동기화

```bash
# 전역 레포에서 실행

# 모든 서브 레포 로그 수집
python .claude/evolution/scripts/sync_quality_logs.py --all

# 출력:
# 🔄 Syncing quality logs from 2 repos...
# ✅ sso-nextjs: Synced 15 logs
# ✅ ojt-platform: Synced 8 logs
#
# 📊 Quality Summary
# 🔹 sso-nextjs
#   ✅ context7-engineer: 5.0/5.0 (avg: 5.0, 3✓ 0✗)
#   ⚠️ debugger: 4.5/5.0 (avg: 4.5, 2✓ 1✗)
```

#### 2.3. 품질 분석

```bash
# 전체 요약
python .claude/evolution/scripts/analyze_quality.py --summary

# 특정 Agent 분석
python .claude/evolution/scripts/analyze_quality.py --agent debugger

# 품질 알림 확인
python .claude/evolution/scripts/analyze_quality.py --alerts
```

---

### Phase 3: CLAUDE.md 통합

#### 3.1. 전역 레포 CLAUDE.md

```markdown
## Agent Quality Tracking

모든 agent/스킬 사용 후 품질 기록:

```bash
# 통과 시
.claude/track.sh "<agent>" "<phase>" "<task>" "pass"

# 실패 시
.claude/track.sh "<agent>" "<phase>" "<task>" "fail" "<error>"
```

주간 품질 리뷰:
```bash
python .claude/evolution/scripts/sync_quality_logs.py --all
python .claude/evolution/scripts/analyze_quality.py --alerts
```
```

#### 3.2. 서브 레포 README.md

각 서브 레포에 추가:

```markdown
## Agent Quality Tracking

이 프로젝트는 Agent 품질 추적 시스템을 사용합니다.

### 사용법

Agent 사용 후:
```bash
.claude/track.sh "<agent>" "<phase>" "<task>" "pass|fail" ["error"]
```

### 현재 점수 확인

```bash
# 전역 레포에서
cd ~/AI/claude01
python .claude/evolution/scripts/analyze_quality.py --repo sso-nextjs
```

### 점수 규칙

- 시작: 5.0/5.0
- 실패: -1.0
- 수정 후 통과: +0.5
- 5번 실패: 0.0 (최악)
```

---

### Phase 4: 자동화 (선택사항)

#### 4.1. Git Hook (Post-Commit)

**서브 레포**: `.git/hooks/post-commit`

```bash
#!/bin/bash
# Agent 품질 자동 기록 (마지막 커밋 메시지 분석)

COMMIT_MSG=$(git log -1 --pretty=%B)

# "feat: Add feature [agent-name]" 패턴 감지
if [[ $COMMIT_MSG =~ \[([^\]]+)\] ]]; then
    AGENT="${BASH_REMATCH[1]}"

    # CI 통과 여부 확인 (향후 구현)
    # if ci_passed; then
    #     .claude/track.sh "$AGENT" "Phase 4" "Commit" "pass"
    # else
    #     .claude/track.sh "$AGENT" "Phase 4" "Commit" "fail" "CI failed"
    # fi
fi
```

#### 4.2. Cron Job (주간 동기화)

**전역 레포**: 매주 일요일 자동 동기화

```bash
# crontab -e
0 0 * * 0 cd ~/AI/claude01 && python .claude/evolution/scripts/sync_quality_logs.py --all
```

#### 4.3. 알림 시스템

품질 점수 < 3.0 시 알림:

```python
# .claude/evolution/scripts/check_alerts.py
analyzer = QualityAnalyzer(data_dir)
analyzer.check_alerts()

# Slack/Discord webhook으로 알림 전송 (향후 구현)
```

---

## 📈 사용 예시

### 예시 1: 새 기능 개발 (sso-nextjs)

```bash
cd ~/AI/sso-nextjs

# Phase 0: PRD 작성
.claude/track.py "context7-engineer" "Phase 0" "Verify NextAuth docs" "pass"
# → Score: 5.0/5.0 ✅

# Phase 1: 코드 구현
.claude/track.py "typescript-expert" "Phase 1" "Define auth types" "pass"
# → Score: 5.0/5.0 ✅

# Phase 2: 테스트
.claude/track.py "test-automator" "Phase 2" "Auth unit tests" "fail" "Token validation"
# → Score: 4.0/5.0 ⚠️

# 버그 수정
.claude/track.py "test-automator" "Phase 2" "Auth unit tests" "pass"
# → Score: 4.5/5.0 ✔️

# Phase 5: E2E
.claude/track.py "playwright-engineer" "Phase 5" "Login flow" "pass"
# → Score: 5.0/5.0 ✅
```

### 예시 2: 전역 레포에서 분석

```bash
cd ~/AI/claude01

# 로그 동기화
python .claude/evolution/scripts/sync_quality_logs.py --all

# sso-nextjs 분석
python .claude/evolution/scripts/analyze_quality.py --repo sso-nextjs

# 출력:
# 📊 sso-nextjs - Repository Analysis
# Total Logs: 5
# Agents: 4
#
# Agent                      Score      Pass    Fail    Total
# ----------------------------------------------------------
# context7-engineer          ✅ 5.0/5.0  1       0       1
# typescript-expert          ✅ 5.0/5.0  1       0       1
# playwright-engineer        ✅ 5.0/5.0  1       0       1
# test-automator             ⚠️ 4.5/5.0  1       1       2
```

### 예시 3: 품질 저하 감지

```bash
# ojt-platform에서 반복 실패
cd ~/AI/ojt-platform

.claude/track.py "debugger" "Phase 1" "Fix bug" "fail" "Error A"
# → Score: 4.0

.claude/track.py "debugger" "Phase 1" "Fix bug" "fail" "Error B"
# → Score: 3.0 ⚠️ WARNING

.claude/track.py "debugger" "Phase 1" "Fix bug" "fail" "Error C"
# → Score: 2.0 ❌

# 전역 레포에서 알림
cd ~/AI/claude01
python .claude/evolution/scripts/analyze_quality.py --alerts

# 출력:
# 🚨 Quality Alerts (1)
# ❌ [URGENT] ojt-platform/debugger
#    Score: 2.0/5.0 - Quality critically low
```

---

## 🎯 체크리스트

### 서브 레포별 (각 프로젝트)

- [ ] `.claude/track.sh` 또는 `.claude/track.py` 설치
- [ ] 실행 권한 설정 (`chmod +x`)
- [ ] Agent 사용 후 `track` 실행 습관화
- [ ] `.agent-quality.jsonl` 파일이 `.gitignore`에 포함되는지 확인
- [ ] README.md에 사용법 추가

### 전역 레포 (claude01)

- [ ] `.claude/evolution/config/repo-config.json` 업데이트
- [ ] 서브 레포 경로 확인
- [ ] 주기적 동기화 스케줄 설정 (주간/월간)
- [ ] CLAUDE.md에 사용법 추가
- [ ] 알림 시스템 설정 (선택)

---

## 💡 Best Practices

### 1. 일관된 기록

모든 agent 사용 후 즉시 기록:

```bash
# ❌ Bad
run_agent()
# (기록 안 함)

# ✅ Good
run_agent()
.claude/track.sh "agent-name" "phase" "task" "pass|fail"
```

### 2. 명확한 Task 이름

```bash
# ❌ Bad
.claude/track.sh "debugger" "Phase 1" "fix" "fail"

# ✅ Good
.claude/track.sh "debugger" "Phase 1" "Fix TypeError in auth.ts" "fail" "Cannot read property 'id' of undefined"
```

### 3. 정기 리뷰

```bash
# 주간 리뷰 (매주 일요일)
cd ~/AI/claude01
python .claude/evolution/scripts/sync_quality_logs.py --all
python .claude/evolution/scripts/analyze_quality.py --alerts

# 품질 저하 발견 시 즉시 대응
```

### 4. Baseline 설정

```bash
# 새 프로젝트 시작 시 baseline 설정
.claude/track.py "all-agents" "Phase 0" "Initial setup" "pass"
```

---

## 🔗 관련 파일

| 파일 | 설명 |
|------|------|
| `QUALITY_SCORING_SYSTEM.md` | 점수 시스템 상세 설명 |
| `templates/track.sh` | Bash 추적 스크립트 |
| `templates/track.py` | Python 추적 스크립트 |
| `scripts/sync_quality_logs.py` | 로그 동기화 |
| `scripts/analyze_quality.py` | 품질 분석 |
| `config/repo-config.json` | 레포 설정 |

---

## 🚀 다음 단계

1. **Phase 1**: 서브 레포에 추적 스크립트 설치 (5분/레포)
2. **Phase 2**: 전역 레포 설정 (10분)
3. **Phase 3**: CLAUDE.md 업데이트 (5분)
4. **Phase 4**: 1주일 사용 후 첫 분석
5. **Phase 5**: 자동화 설정 (선택)

---

**작성자**: Claude Code
**업데이트**: 2025-01-14
**버전**: 2.0.0
