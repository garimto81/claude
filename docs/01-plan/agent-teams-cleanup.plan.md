# Agent Teams Cleanup Work Plan

## 배경 (Background)

Agent Teams 사용 중 3가지 근본 원인으로 팀 정리 실패 및 무한 대기 발생:

1. **Context Compaction 시 팀 상태 소실** — 긴 HEAVY 세션에서 compaction 발생 시 Lead가 팀 정보 잊음 → `TeamDelete()` 불가
2. **VS Code 환경 메시지 전달 실패** — `isTTY=false` → Task tool 제한 → inbox 파일에 쓰이지만 UI 미전달 → 무한 대기
3. **shutdown_request 타임아웃 없음** — teammate가 응답 안 하면 Lead 영구 차단

추가 문제: 세션 비정상 종료 시 고아 리소스 잔존
- `~/.claude/tasks/` 고아 디렉토리 12개 (UUID 기반)
- `~/.claude/todos/` stale todo 파일 53개

## 구현 범위 (Scope)

### 포함
- `settings.json`에 `teammateMode: "in-process"` 추가 (VS Code 메시지 전달 실패 완화)
- `SKILL.md` Phase 5 섹션 safe cleanup 절차로 교체 (타임아웃 + 수동 fallback)
- `REFERENCE.md`에 Phase 5 Safe Cleanup 상세 절차 추가 (~30줄)
- 현재 세션 고아 리소스 즉시 정리 (`~/.claude/tasks/` 12개, `~/.claude/todos/` 53개)

### 제외
- Agent Teams SDK 수정 (외부 바이너리, 통제 불가)
- `/auto resume` 명령어 구현 (별도 피처 범위)
- teammate 내부 타임아웃 로직 (SDK 레벨 변경 필요)

## 영향 파일 (Affected Files)

### 수정 예정
- `C:/Users/AidenKim/.claude/settings.json` — `teammateMode` 1줄 추가
- `C:/claude/.claude/skills/auto/SKILL.md` — L272-275 Phase 5 팀 정리 블록 교체 (~10줄)
- `C:/claude/.claude/skills/auto/REFERENCE.md` — "팀 라이프사이클" 섹션 확장 (~30줄)

### 신규 생성
- 없음

### 즉시 정리 대상 (Bash 실행)
- `~/.claude/tasks/{12개 UUID 디렉토리}` 삭제
- `~/.claude/todos/{53개 stale 파일}` 삭제

## 위험 요소 (Risks)

1. **`teammateMode: "in-process"` 부작용** — in-process 모드는 teammate가 Lead와 동일 프로세스에서 실행됨. 메모리 사용량 증가 가능. 또한 현재 Claude Code 버전에서 해당 옵션이 인식되지 않는 경우 무시됨 (silent fail). 검증: 변경 후 Agent Teams 정상 동작 확인 필요.

2. **고아 tasks 디렉토리 삭제 시 활성 세션 충돌** — `pdca-agent-teams-cleanup` 팀이 현재 활성 상태(`~/.claude/tasks/pdca-agent-teams-cleanup`). 이 디렉토리는 삭제하면 현재 세션이 끊어짐. UUID 기반 12개만 삭제, `pdca-*` 명칭 디렉토리는 보존.

3. **SKILL.md Phase 5 교체 후 기존 동작 회귀** — 현재 단순 `TeamDelete()` 호출이 fallback 절차로 확장됨. 정상 종료 경로(teammate 정상 응답)에서는 오버헤드 없어야 함.

4. **REFERENCE.md 섹션 위치** — "팀 라이프사이클" 섹션 확장 시 하위 섹션("Teammate 운영 규칙", "Context 분리 장점")과 마크다운 구조 충돌 가능.

## 태스크 목록 (Tasks)

### T1. 즉시 정리 — 고아 리소스 삭제
**설명**: 현재 세션의 UUID 기반 고아 task 디렉토리 12개 및 stale todo 파일 53개 삭제.

**수행 방법**:
```bash
# UUID 형식 디렉토리만 삭제 (pdca-* 보존)
rm -rf ~/.claude/tasks/3688622f-76ed-4e05-a386-750e4ae86c2d
rm -rf ~/.claude/tasks/4b6bb899-c0af-496e-8ce7-4d23b6e3057e
rm -rf ~/.claude/tasks/6046e795-a495-45f1-ac1e-6570d6dcce8e
rm -rf ~/.claude/tasks/732bb3a2-65a4-4999-a49c-32e3e624373c
rm -rf ~/.claude/tasks/84904ac7-68b7-48d5-98e7-7f3142e24d5a
rm -rf ~/.claude/tasks/923d2422-e82e-466b-b80a-534f0083e5c7
rm -rf ~/.claude/tasks/976c4e54-2f73-46e5-ad0d-26fe0773fa42
rm -rf ~/.claude/tasks/981b6139-4436-433d-8d74-97b9f6df4172
rm -rf ~/.claude/tasks/a007ad7c-9cf5-4006-b3e8-15715c9d8377
rm -rf ~/.claude/tasks/a6d96a35-542e-4b0c-b03e-7e69f7e5792f
rm -rf ~/.claude/tasks/e97a7474-cc08-49a2-9b61-a3295bb3f1ba
rm -rf ~/.claude/tasks/e9e7fa86-2555-4403-845b-42885d022f68

# todos 정리 (2026-02-18 이전 생성 파일)
find ~/.claude/todos/ -name "*.json" -mtime +1 -delete
```

**Acceptance Criteria**: `~/.claude/tasks/` 에 UUID 형식 디렉토리 0개. `~/.claude/todos/` 파일 수 감소 확인.

---

### T2. settings.json — `teammateMode` 추가
**설명**: VS Code 환경에서 메시지 전달 실패를 완화하기 위해 `teammateMode: "in-process"` 추가.

**수행 방법**:
- 파일: `C:/Users/AidenKim/.claude/settings.json`
- 현재 `"outputStyle": "sst"` 라인 앞에 `"teammateMode": "in-process"` 추가

**Acceptance Criteria**: `settings.json` 파싱 오류 없음 (JSON 유효성). Agent Teams 생성 시 in-process 모드로 동작.

---

### T3. SKILL.md Phase 5 — Safe Cleanup 절차 추가
**설명**: L272-275 팀 정리 블록을 타임아웃 + 수동 fallback을 포함한 safe cleanup 절차로 교체.

**수행 방법**:
- 파일: `C:/claude/.claude/skills/auto/SKILL.md`
- 대상 라인: L272-275 (현재 `# 완료 대기 → shutdown_request → TeamDelete()` 및 `**팀 정리 (MANDATORY):** \`TeamDelete()\``)
- 교체 내용:

```
# 완료 대기 → Safe Cleanup (MANDATORY)
# Step 1: shutdown_request 전송 (10초 타임아웃)
SendMessage(type="shutdown_request", recipient="reporter")
# Step 2: 10초 대기 후 응답 없으면 수동 정리
# Step 3: TeamDelete() — 실패 시 수동 fallback:
#   rm -rf ~/.claude/teams/{팀명} ~/.claude/tasks/{팀명}
```

**팀 정리 (MANDATORY — Safe Cleanup):**
1. `SendMessage(type="shutdown_request", recipient="{모든 활성 teammate}")` — 각 teammate에 순차 전송
2. 응답 대기 (최대 10초/teammate). 무응답 시 다음 단계로 진행 (차단 금지)
3. `TeamDelete()` 실행
4. TeamDelete 실패 시: `rm -rf ~/.claude/teams/{팀명} ~/.claude/tasks/{팀명}` (수동 정리 fallback)

**Acceptance Criteria**: SKILL.md L272-L280 구간이 4단계 safe cleanup 절차를 포함. 기존 `# 완료 대기 → shutdown_request → TeamDelete()` 단순 주석 제거됨.

---

### T4. REFERENCE.md — Phase 5 Safe Cleanup 상세 절차 추가
**설명**: "팀 라이프사이클" 섹션에 Safe Cleanup 5단계 절차, crash recovery 프로토콜, 고아 리소스 감지 스크립트 추가.

**수행 방법**:
- 파일: `C:/claude/.claude/skills/auto/REFERENCE.md`
- 위치: L15-19 "팀 라이프사이클" 섹션 뒤
- 추가 내용 (~30줄):

```markdown
### Phase 5 Safe Cleanup 절차 (v22.2)

**정상 종료 (5단계)**:
1. writer teammate 완료 확인 (Mailbox 수신)
2. `SendMessage(type="shutdown_request", recipient="reporter")` 전송
3. 응답 대기 (10초). 무응답 → Step 4로 진행
4. `TeamDelete()` 실행
5. 실패 시 수동 fallback: `rm -rf ~/.claude/teams/{팀명} ~/.claude/tasks/{팀명}`

**세션 비정상 종료 후 복구**:
- 고아 팀 감지: `ls ~/.claude/teams/` — `pdca-*` 디렉토리가 남아있으면 고아 팀
- 복구 순서: TeamDelete 시도 → 실패 시 수동 정리
- 고아 task 정리: UUID 형식 디렉토리만 삭제 (`pdca-*` 보존)
  ```bash
  ls ~/.claude/tasks/ | grep -E '^[0-9a-f-]{36}$' | xargs -I{} rm -rf ~/.claude/tasks/{}
  ```
- stale todo 정리: `find ~/.claude/todos/ -name "*.json" -mtime +1 -delete`

**Context Compaction 후 팀 소실 시**:
- 증상: TeamDelete 호출 시 "team not found" 에러
- 처리: 에러 무시하고 수동 정리 실행
  ```bash
  rm -rf ~/.claude/teams/pdca-{feature} ~/.claude/tasks/pdca-{feature}
  ```

**VS Code 환경 (isTTY=false) 무한 대기 방지**:
- `settings.json`의 `teammateMode: "in-process"` 확인
- 여전히 대기 시 10초 후 강제 진행 (shutdown_request 응답 불필요)
```

**Acceptance Criteria**: REFERENCE.md에 "Phase 5 Safe Cleanup 절차" 섹션 존재. 5단계 정상 종료, crash recovery, compaction 후 복구, VS Code 환경 처리 모두 문서화됨.

---

## 커밋 전략 (Commit Strategy)

```
fix(agent-teams): Phase 5 safe cleanup + 고아 리소스 정리

- settings.json: teammateMode in-process 추가 (VS Code 메시지 전달 완화)
- SKILL.md: Phase 5 TeamDelete 4단계 safe cleanup으로 교체
- REFERENCE.md: Safe Cleanup 상세 절차, crash recovery, 고아 리소스 정리 스크립트 추가
- ~/.claude/tasks/: UUID 기반 고아 디렉토리 12개 삭제
- ~/.claude/todos/: stale todo 파일 53개 정리
```

Conventional Commit 형식: `fix(agent-teams): <요약>` (버그 수정 + 절차 개선)

---

## 검증 체크리스트

- [ ] `settings.json` JSON 파싱 오류 없음
- [ ] SKILL.md Phase 5 섹션이 4단계 절차 포함
- [ ] REFERENCE.md "Phase 5 Safe Cleanup 절차" 섹션 존재
- [ ] `~/.claude/tasks/` UUID 형식 디렉토리 0개
- [ ] `~/.claude/todos/` stale 파일 수 감소
- [ ] 기존 SKILL.md 단순 `TeamDelete()` 주석 제거됨
