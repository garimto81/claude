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

## 스킬 매핑 테이블 (최종)

| 로컬 스킬 | OMC 위임 | 서브커맨드 | 비고 |
|-----------|----------|-----------|------|
| `/auto` | `autopilot` | --gdocs, --mockup, --debate, --research | Orchestrator |
| `/check` | `ultraqa` | --fix, --e2e, --perf, --security, --all | QA 사이클 |
| `/debug` | `analyze` | D0-D4 Phase | 디버깅 |
| `/tdd` | `tdd` | - | TDD 워크플로우 |
| `/parallel` | `ultrawork` | dev, test, review, research, check | 병렬 실행 |
| `/research` | `research` | code, web, plan, review | 리서치 |
| `/commit` | - | --no-push | 직접 실행 |
| `/issue` | - | list, create, fix, failed | 직접 실행 |
| `/pr` | - | review, merge, auto, list | 직접 실행 |
| `/verify` | - | --provider openai/gemini | Cross-AI 고유 |
| `/mockup-hybrid` | - | --bnw, --hifi | Stitch API 고유 |

## 인과관계 그래프 (CRITICAL - 절대 보존)

```
                    ┌─────────────────────────────────────────────┐
                    │              /auto (v15.1.0)                │
                    │         5-Tier Discovery + OMC              │
                    └─────────────────────────────────────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┬────────────────┐
        ▼               ▼               ▼               ▼                ▼
   Tier 2 URGENT   Tier 3 WORK    Tier 4 SUPPORT   Tier 5 AUTO      Options
        │               │               │               │                │
   ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────────┴────────┐
   │ /debug  │    │ /issue  │    │ /commit │    │  /tdd   │    │ --gdocs --mockup│
   │ /check  │    │  fix    │    │ /pr auto│    │ /audit  │    │ --debate        │
   └────┬────┘    └────┬────┘    └─────────┘    └────┬────┘    └─────────────────┘
        │               │                            │
        ▼               ▼                            ▼
   OMC analyze     OMC executor                 OMC tdd-guide


                    ┌─────────────────────────────────────────────┐
                    │           /work --loop (자율 루프)           │
                    └─────────────────────────────────────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┐
        ▼               ▼               ▼               ▼
      Tier 1          Tier 2          Tier 3        완료 후
        │               │               │               │
   ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
   │ /debug  │    │ /commit │    │  /tdd   │    │/create  │
   │ /check  │    │ /issue  │    │/research│    │   pr    │
   │ --fix   │    │ /pr auto│    └────┬────┘    └────┬────┘
   └─────────┘    └─────────┘         │              │
                                      ▼              ▼
                              OMC tdd/research  /session journey
```

**⚠️ 이 인과관계가 무너지면 `/auto`, `/work --loop`의 5계층 Discovery 시스템 전체가 작동하지 않음**

## Deprecated 스킬 (Alias 처리)

| Deprecated 스킬 | 리다이렉트 대상 | 처리 방식 |
|----------------|----------------|----------|
| `/auto-workflow` | `/auto` | redirect 필드 |
| `/auto-executor` | `/auto` | redirect 필드 |
| `/tdd-workflow` | `/tdd` | redirect 필드 |
| `/cross-ai-verifier` | `/verify` | redirect 필드 |
| `/issue-resolution` | `/issue fix` | redirect 필드 |

**Deprecated 스킬 YAML 예시:**
```yaml
---
name: auto-workflow
deprecated: true
redirect: auto
deprecation_message: "/auto-workflow는 /auto로 통합되었습니다."
triggers:
  keywords: []  # 비활성화
---
```

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

서브프로젝트에서 스킬을 사용하려면 Junction 필요:

```powershell
# Junction 생성 (관리자 권한 필요)
cmd /c mklink /J 서브프로젝트\.claude\skills C:\claude\.claude\skills
cmd /c mklink /J 서브프로젝트\.claude\commands C:\claude\.claude\commands
cmd /c mklink /J 서브프로젝트\.claude\agents C:\claude\.claude\agents

# 대안: 심볼릭 링크
New-Item -ItemType SymbolicLink `
  -Path "서브프로젝트\.claude\skills" `
  -Target "C:\claude\.claude\skills"
```

**상세 가이드**: `.claude/rules/09-global-only.md`

## 금지 사항

- ❌ SKILL.md에 "참조하세요"만 작성 (실행 지시 필수)
- ❌ omc_delegate 없이 OMC 기능 기대
- ❌ 서브프로젝트에 스킬/커맨드/에이전트 로컬 생성 (Junction 사용)
- ❌ 서브프로젝트에 리소스 복제 (Global-Only Policy 위반)
- ❌ 인과관계 파괴 (커맨드 삭제/변경 시 연쇄 확인 필수)
