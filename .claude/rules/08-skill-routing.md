# OMC 스킬 라우팅 규칙

## 핵심 원칙

로컬 스킬(`.claude/skills/`)은 OMC 플러그인(`oh-my-claudecode`)으로 **자동 위임**됩니다.

## omc_delegate 필드

SKILL.md의 YAML frontmatter에 `omc_delegate` 필드가 있으면 해당 OMC 스킬로 자동 라우팅됩니다.

```yaml
---
name: auto
omc_delegate: oh-my-claudecode:autopilot
---
```

**동작 방식:**
1. 사용자가 `/auto "작업"` 실행
2. Claude가 `.claude/skills/auto/SKILL.md` 읽음
3. `omc_delegate` 필드 확인
4. `Skill(skill="oh-my-claudecode:autopilot", args="작업")` 자동 호출

## 스킬 매핑 테이블

| 로컬 스킬 | OMC 스킬 | 용도 |
|-----------|----------|------|
| `/auto` | `oh-my-claudecode:autopilot` | 자율 워크플로우 |
| `/check` | `oh-my-claudecode:ultraqa` | QA 사이클 |
| `/debug` | `oh-my-claudecode:analyze` | 디버깅 분석 |
| `/commit` | (직접 실행) | Git 커밋 |
| `/tdd` | `oh-my-claudecode:tdd` | TDD 워크플로우 |

## 에이전트 티어 라우팅

| 복잡도 | 티어 | 에이전트 예시 |
|--------|------|--------------|
| 간단 | LOW (haiku) | `explore`, `executor-low`, `writer` |
| 보통 | MEDIUM (sonnet) | `executor`, `designer`, `qa-tester` |
| 복잡 | HIGH (opus) | `architect`, `planner`, `executor-high` |

## SKILL.md vs command.md 역할

| 파일 | 역할 | 크기 | 용도 |
|------|------|------|------|
| `SKILL.md` | 트리거 정의 + 실행 지시 | ~100줄 | Claude가 읽고 실행 |
| `command.md` | 상세 문서 | ~1000줄 | 참조용 문서 |

## 서브프로젝트 설정

서브프로젝트에서 스킬을 사용하려면 심볼릭 링크 필요:

```powershell
# 관리자 권한 필요
New-Item -ItemType SymbolicLink `
  -Path "서브프로젝트/.claude/skills" `
  -Target "C:\claude\.claude\skills"
```

## 금지 사항

- ❌ SKILL.md에 "참조하세요"만 작성 (실행 지시 필수)
- ❌ omc_delegate 없이 OMC 기능 기대
- ❌ 서브프로젝트에 스킬 복제 (심볼릭 링크 사용)
