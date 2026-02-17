# Design: Daily Integration

> `/secretary` + Slack List 통합 대시보드 상세 기술 설계

**Version**: 1.0.0
**Created**: 2026-02-05
**Status**: Design
**Plan Reference**: `docs/01-plan/daily-integration.plan.md`

---

## 1. 모듈 설계

### 1.1 컴포넌트 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                      /daily 스킬                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  daily_dashboard │  │  checklist_     │  │  prd_linker     │ │
│  │  .py (메인)      │  │  parser.py      │  │  .py (선택)     │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                     │                     │          │
│           ▼                     ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    DashboardFormatter                        ││
│  │  • format_default() - 전체 대시보드                          ││
│  │  • format_standup() - 아침 브리핑                            ││
│  │  • format_retro()   - 저녁 회고                              ││
│  │  • format_projects()- 프로젝트 진행률만                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
           │                     │
           ▼                     ▼
┌─────────────────┐    ┌─────────────────────────────────────────┐
│  /secretary     │    │  docs/checklists/*.md                    │
│  (기존 스크립트) │    │  CHECKLIST_STANDARD.md 형식              │
└─────────────────┘    └─────────────────────────────────────────┘
```

### 1.2 모듈 책임

| 모듈 | 파일 | 책임 |
|------|------|------|
| **DailyDashboard** | `daily_dashboard.py` | 메인 오케스트레이터, CLI 엔트리포인트 |
| **ChecklistParser** | `checklist_parser.py` | Checklist 파일 파싱, 진행률 계산 |
| **SecretaryBridge** | `daily_dashboard.py` 내부 | secretary 스크립트 호출 및 결과 통합 |
| **DashboardFormatter** | `daily_dashboard.py` 내부 | 서브커맨드별 출력 포맷팅 |
| **PRDLinker** | `prd_linker.py` (Phase 3) | 이메일/PR ↔ PRD 연결 |

---

## 2. 데이터 흐름

### 2.1 전체 데이터 파이프라인

```
┌─────────────────────────────────────────────────────────────────┐
│                         /daily 실행                              │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Secretary 호출   │  │ Checklist 읽기  │  │ PRD 연결 (선택) │
│ (병렬 가능)      │  │ (파일 시스템)   │  │ (Phase 3)       │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ SecretaryResult │  │ ChecklistResult │  │ LinkResult      │
│ {               │  │ {               │  │ {               │
│   gmail: {...}  │  │   projects: []  │  │   email_prd: [] │
│   calendar: {}  │  │   total_items   │  │   pr_checklist: │
│   github: {...} │  │   completed     │  │ }               │
│ }               │  │   progress      │  │                 │
│                 │  │ }               │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │ DashboardState  │
                    │ {               │
                    │   personal: {}  │
                    │   projects: []  │
                    │   links: []     │
                    │   generated_at  │
                    │ }               │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Formatter       │
                    │ (서브커맨드별)   │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 출력 (stdout)   │
                    └─────────────────┘
```

### 2.2 Secretary 호출 흐름

```python
# daily_dashboard.py에서 secretary 호출
def call_secretary(sources: list[str] = None) -> SecretaryResult:
    """
    기존 daily_report.py --json 호출
    수정 없이 외부 프로세스로 실행
    """
    cmd = [sys.executable, SECRETARY_SCRIPT, "--json"]
    if sources:
        for src in sources:
            cmd.append(f"--{src}")

    result = subprocess.run(cmd, capture_output=True, ...)
    return SecretaryResult.from_json(result.stdout)
```

### 2.3 Checklist 파싱 흐름

```
docs/checklists/*.md
        │
        ▼
┌─────────────────────────────────────────┐
│ 1. Glob 패턴으로 파일 목록 수집          │
│    Pattern: docs/checklists/PRD-*.md    │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ 2. 각 파일 메타데이터 추출               │
│    - PRD ID (파일명 또는 헤더)           │
│    - Status (In Progress/Completed)     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ 3. Checkbox 항목 파싱                    │
│    - [x] → completed                     │
│    - [ ] → pending                       │
│    - (#NNN) → linked PR                  │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│ 4. 진행률 계산                           │
│    progress = completed / total * 100   │
└─────────────────────────────────────────┘
```

---

## 3. API 정의

### 3.1 ChecklistParser

```python
# checklist_parser.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re


@dataclass
class ChecklistItem:
    """단일 체크리스트 항목"""
    text: str
    completed: bool
    pr_number: Optional[int] = None  # (#123) 형식에서 추출
    phase: Optional[str] = None       # 상위 Phase 헤더


@dataclass
class ChecklistProject:
    """PRD 단위 프로젝트"""
    prd_id: str                       # "PRD-0001"
    title: str                        # Checklist 제목
    status: str                       # "In Progress" | "Completed" | "On Hold"
    items: list[ChecklistItem] = field(default_factory=list)

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def completed_items(self) -> int:
        return len([i for i in self.items if i.completed])

    @property
    def progress(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100

    @property
    def pending_items(self) -> list[ChecklistItem]:
        return [i for i in self.items if not i.completed]


@dataclass
class ChecklistResult:
    """전체 Checklist 파싱 결과"""
    projects: list[ChecklistProject]
    scan_paths: list[str]
    scanned_at: str

    @property
    def total_progress(self) -> float:
        """전체 평균 진행률"""
        if not self.projects:
            return 0.0
        return sum(p.progress for p in self.projects) / len(self.projects)


class ChecklistParser:
    """CHECKLIST_STANDARD.md 형식 파서"""

    # 기본 스캔 경로 (우선순위 순)
    DEFAULT_PATHS = [
        "docs/checklists",
        "tasks/prds",
        "docs",
    ]

    # 파싱 정규식
    CHECKBOX_PATTERN = re.compile(r'^[-*]\s+\[([ xX])\]\s+(.+)$')
    PR_LINK_PATTERN = re.compile(r'\(#(\d+)\)')
    PHASE_HEADER_PATTERN = re.compile(r'^##\s+Phase\s+\d+[:\s]+(.+)$', re.IGNORECASE)
    PRD_ID_PATTERN = re.compile(r'PRD-(\d{4})', re.IGNORECASE)
    STATUS_PATTERN = re.compile(r'\*\*Status\*\*:\s*(.+)', re.IGNORECASE)

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)

    def scan(self, paths: list[str] = None) -> ChecklistResult:
        """
        지정된 경로에서 모든 Checklist 파일 스캔

        Args:
            paths: 스캔할 경로 목록 (None이면 DEFAULT_PATHS 사용)

        Returns:
            ChecklistResult: 파싱된 프로젝트 목록
        """
        pass

    def parse_file(self, file_path: Path) -> Optional[ChecklistProject]:
        """
        단일 Checklist 파일 파싱

        Args:
            file_path: Checklist 파일 경로

        Returns:
            ChecklistProject: 파싱된 프로젝트 또는 None (파싱 실패 시)
        """
        pass

    def _extract_prd_id(self, content: str, filename: str) -> Optional[str]:
        """PRD ID 추출 (헤더 우선, 파일명 fallback)"""
        pass

    def _extract_status(self, content: str) -> str:
        """Status 추출 (기본값: In Progress)"""
        pass

    def _parse_items(self, content: str) -> list[ChecklistItem]:
        """Checkbox 항목 파싱"""
        pass
```

### 3.2 DailyDashboard (메인)

```python
# daily_dashboard.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import argparse
import json
import subprocess
import sys
from pathlib import Path

from checklist_parser import ChecklistParser, ChecklistResult


@dataclass
class SecretaryResult:
    """Secretary 스크립트 결과"""
    gmail: dict
    calendar: dict
    github: dict
    generated_at: str

    @classmethod
    def from_json(cls, data: dict) -> "SecretaryResult":
        """JSON 딕셔너리에서 생성"""
        return cls(
            gmail=data.get("gmail", {}),
            calendar=data.get("calendar", {}),
            github=data.get("github", {}),
            generated_at=data.get("generated_at", datetime.now().isoformat())
        )

    @classmethod
    def empty(cls) -> "SecretaryResult":
        """빈 결과 (에러 시 fallback)"""
        return cls(
            gmail={},
            calendar={},
            github={},
            generated_at=datetime.now().isoformat()
        )


@dataclass
class DashboardState:
    """통합 대시보드 상태"""
    personal: SecretaryResult
    projects: ChecklistResult
    generated_at: str


class DailyDashboard:
    """통합 대시보드 메인 클래스"""

    SECRETARY_SCRIPT = Path(__file__).parent.parent / "secretary" / "scripts" / "daily_report.py"

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path("C:/claude")
        self.parser = ChecklistParser(self.base_path)

    def run(self, subcommand: str = None, **options) -> str:
        """
        대시보드 실행

        Args:
            subcommand: None (기본), "standup", "retro", "projects"
            options: 추가 옵션 (json 출력 등)

        Returns:
            포맷된 출력 문자열
        """
        pass

    def _call_secretary(self, sources: list[str] = None) -> SecretaryResult:
        """Secretary 스크립트 호출"""
        pass

    def _get_state(self, include_personal: bool = True) -> DashboardState:
        """전체 상태 수집"""
        pass

    def _format_default(self, state: DashboardState) -> str:
        """기본 대시보드 포맷"""
        pass

    def _format_standup(self, state: DashboardState) -> str:
        """아침 브리핑 포맷"""
        pass

    def _format_retro(self, state: DashboardState) -> str:
        """저녁 회고 포맷"""
        pass

    def _format_projects(self, state: DashboardState) -> str:
        """프로젝트 진행률만 포맷"""
        pass


def main():
    """CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(
        description="Daily Dashboard - 개인 업무 + 프로젝트 통합 현황"
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["standup", "retro", "projects"],
        help="서브커맨드 (없으면 전체 대시보드)"
    )
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")
    parser.add_argument("--no-personal", action="store_true", help="개인 업무 제외")
    parser.add_argument("--no-projects", action="store_true", help="프로젝트 제외")

    args = parser.parse_args()

    dashboard = DailyDashboard()
    output = dashboard.run(
        subcommand=args.subcommand,
        json_output=args.json,
        include_personal=not args.no_personal,
        include_projects=not args.no_projects
    )
    print(output)


if __name__ == "__main__":
    main()
```

### 3.3 반환 타입 요약

| 함수 | 입력 | 출력 |
|------|------|------|
| `ChecklistParser.scan()` | `paths: list[str]` | `ChecklistResult` |
| `ChecklistParser.parse_file()` | `file_path: Path` | `ChecklistProject | None` |
| `DailyDashboard.run()` | `subcommand: str, **options` | `str` |
| `DailyDashboard._call_secretary()` | `sources: list[str]` | `SecretaryResult` |

---

## 4. 파일 구조

### 4.1 생성할 파일 목록

```
.claude/skills/daily/
├── SKILL.md                    # 스킬 정의 (트리거, 설명)
├── scripts/
│   ├── __init__.py            # 패키지 초기화
│   ├── daily_dashboard.py     # 메인 실행 스크립트 (CLI)
│   └── checklist_parser.py    # Checklist 파서
└── templates/                  # (Phase 2)
    ├── standup.md             # 아침 브리핑 템플릿
    └── retro.md               # 저녁 회고 템플릿
```

### 4.2 각 파일 역할

| 파일 | 역할 | 예상 LOC |
|------|------|:--------:|
| `SKILL.md` | 트리거 키워드, 사용법, 커맨드 설명 | ~80 |
| `daily_dashboard.py` | CLI 엔트리포인트, Secretary 호출, 포맷팅 | ~250 |
| `checklist_parser.py` | Markdown Checklist 파싱 로직 | ~150 |
| `__init__.py` | 모듈 export | ~10 |

### 4.3 기존 파일 변경

**변경 없음** - 기존 secretary 스크립트는 수정하지 않고 외부 호출만 함

| 파일 | 변경 여부 | 사유 |
|------|:--------:|------|
| `secretary/scripts/daily_report.py` | 변경 없음 | subprocess로 호출 |
| `secretary/scripts/gmail_analyzer.py` | 변경 없음 | daily_report.py 경유 |
| `secretary/scripts/github_analyzer.py` | 변경 없음 | daily_report.py 경유 |
| `secretary/scripts/calendar_analyzer.py` | 변경 없음 | daily_report.py 경유 |

---

## 5. Checklist 파서 설계

### 5.1 지원 형식 (CHECKLIST_STANDARD.md 기준)

```markdown
# [PRD-0001] Checklist

**PRD**: PRD-0001
**Version**: 1.0.0
**Last Updated**: 2025-12-22
**Status**: In Progress

## Phase 1: 설계

- [x] 요구사항 분석 (#101)
- [x] 아키텍처 설계 (#102)
- [ ] API 설계

## Phase 2: 구현

- [ ] 핵심 기능 구현
- [ ] 테스트 작성 (#103)
```

### 5.2 파싱 규칙

| 요소 | 패턴 | 예시 |
|------|------|------|
| **PRD ID** | `PRD-\d{4}` (헤더 또는 파일명) | `PRD-0001` |
| **Status** | `**Status**: (.+)` | `In Progress` |
| **Checkbox 완료** | `- [x]` 또는 `- [X]` | `- [x] 완료됨` |
| **Checkbox 미완료** | `- [ ]` | `- [ ] 진행중` |
| **PR 연결** | `(#\d+)` | `(#123)` |
| **Phase 헤더** | `## Phase N: ...` | `## Phase 1: 설계` |

### 5.3 파싱 알고리즘

```python
def parse_file(self, file_path: Path) -> Optional[ChecklistProject]:
    content = file_path.read_text(encoding="utf-8")

    # 1. PRD ID 추출 (헤더 > 파일명)
    prd_id = self._extract_prd_id(content, file_path.stem)
    if not prd_id:
        return None  # PRD ID 없으면 스킵

    # 2. 제목 추출 (첫 번째 # 헤더)
    title = self._extract_title(content)

    # 3. Status 추출
    status = self._extract_status(content)

    # 4. 항목 파싱
    items = []
    current_phase = None

    for line in content.split("\n"):
        # Phase 헤더 감지
        phase_match = self.PHASE_HEADER_PATTERN.match(line)
        if phase_match:
            current_phase = phase_match.group(1)
            continue

        # Checkbox 항목 감지
        checkbox_match = self.CHECKBOX_PATTERN.match(line.strip())
        if checkbox_match:
            completed = checkbox_match.group(1).lower() == "x"
            text = checkbox_match.group(2)

            # PR 번호 추출
            pr_match = self.PR_LINK_PATTERN.search(text)
            pr_number = int(pr_match.group(1)) if pr_match else None

            items.append(ChecklistItem(
                text=text,
                completed=completed,
                pr_number=pr_number,
                phase=current_phase
            ))

    return ChecklistProject(
        prd_id=prd_id,
        title=title,
        status=status,
        items=items
    )
```

### 5.4 엣지 케이스 처리

| 케이스 | 처리 방법 |
|--------|----------|
| PRD ID 없음 | 파일 스킵 (로그 경고) |
| Checkbox 없음 | 빈 프로젝트 반환 (progress=0%) |
| 중첩 리스트 | 최상위만 파싱 (하위 무시) |
| 테이블 형식 Checklist | 지원 (Phase 2) |
| 마크다운 링크 `[text](url)` | PR 번호만 추출, 링크 무시 |

---

## 6. 출력 포맷

### 6.1 기본 대시보드 (`/daily`)

```
================================================================================
                        Daily Dashboard (2026-02-05 Wed)
================================================================================

[Personal] --------------------------------------------------------
  Email (3 action items)
    * [URGENT] 계약서 검토 요청 - Due 2/6 (from: 김대표)
    * [MEDIUM] 회의록 확인 요청 (from: 이팀장)
    * [LOW] 뉴스레터 구독 확인

  Calendar (2 events)
    * 10:00 팀 스탠드업 (Google Meet)
    * 14:00 클라이언트 미팅 (회의실 A)

  GitHub (2 attention needed)
    * PR #42 (secretary): Review pending 3 days
    * Issue #15 (youtuber): No response 4 days

[Projects] --------------------------------------------------------
  PRD-0001  [=========>    ] 80%  인증 시스템
  PRD-0002  [==>           ] 20%  PR 수집
  PRD-0135  [======>       ] 60%  워크플로우 활성화

  Overall: 53% (8/15 items)

================================================================================
```

### 6.2 아침 브리핑 (`/daily standup`)

```
================================================================================
                     Good Morning! (2026-02-05 Wed)
================================================================================

[Today's Focus] ---------------------------------------------------
  1. [URGENT] 계약서 검토 요청 - Due 2/6
  2. 14:00 클라이언트 미팅 준비

[Schedule] --------------------------------------------------------
  10:00  팀 스탠드업 (Google Meet)
  14:00  클라이언트 미팅 (회의실 A)

[Project Blockers] ------------------------------------------------
  PRD-0001: 2 items remaining
    - [ ] 문서 업데이트
    - [ ] 최종 검증

================================================================================
Have a productive day!
```

### 6.3 저녁 회고 (`/daily retro`)

```
================================================================================
                     Day Review (2026-02-05 Wed)
================================================================================

[Completed Today] -------------------------------------------------
  * Answered 5 emails
  * Attended 2 meetings
  * Closed 3 GitHub issues

[Still Pending] ---------------------------------------------------
  * [URGENT] 계약서 검토 요청 - Due 2/6
  * PR #42 still needs review

[Project Progress] ------------------------------------------------
  PRD-0001: +10% (70% -> 80%)
  PRD-0002: No change (20%)

[Tomorrow's Priority] ---------------------------------------------
  1. 계약서 검토 완료
  2. PR #42 리뷰 요청

================================================================================
```

### 6.4 프로젝트 진행률만 (`/daily projects`)

```
================================================================================
                     Project Progress (2026-02-05)
================================================================================

  PRD-0001  [=========>    ] 80%  인증 시스템
    - [ ] 문서 업데이트
    - [ ] 최종 검증

  PRD-0002  [==>           ] 20%  PR 수집
    - [ ] API 연동 (#45)
    - [ ] 에러 처리
    - [ ] 테스트 작성

  PRD-0135  [======>       ] 60%  워크플로우 활성화
    - [ ] CI 파이프라인 (#50)
    - [ ] 문서화

--------------------------------------------------------------------------------
  Total: 3 projects | 53% average | 7 pending items
================================================================================
```

### 6.5 JSON 출력 (`--json`)

```json
{
  "generated_at": "2026-02-05T09:30:00",
  "personal": {
    "gmail": {
      "tasks": [...],
      "unanswered": [...]
    },
    "calendar": {
      "events": [...],
      "needs_prep": [...]
    },
    "github": {
      "attention_needed": [...],
      "active_repos": [...]
    }
  },
  "projects": {
    "projects": [
      {
        "prd_id": "PRD-0001",
        "title": "인증 시스템",
        "status": "In Progress",
        "total_items": 5,
        "completed_items": 4,
        "progress": 80.0,
        "pending_items": [...]
      }
    ],
    "total_progress": 53.3
  }
}
```

---

## 7. 에러 처리

### 7.1 에러 시나리오 및 처리

| 시나리오 | 영향 | 처리 |
|----------|------|------|
| **Gmail OAuth 만료** | 개인 업무 일부 누락 | 경고 메시지 + 나머지 섹션 출력 |
| **GitHub 토큰 없음** | GitHub 섹션 누락 | 경고 메시지 + 나머지 섹션 출력 |
| **Checklist 파일 없음** | 프로젝트 섹션 빈 값 | "No checklist files found" 표시 |
| **Checklist 파싱 실패** | 해당 파일만 스킵 | 로그 경고 + 나머지 파일 처리 |
| **Secretary 스크립트 없음** | 개인 업무 전체 누락 | 에러 메시지 + 프로젝트만 출력 |
| **타임아웃 (>10초)** | 응답 지연 | 120초 타임아웃 설정 |

### 7.2 에러 출력 형식

```
================================================================================
                        Daily Dashboard (2026-02-05 Wed)
================================================================================

[!] Warning: Gmail authentication failed - run secretary setup
[!] Warning: 2 checklist files could not be parsed

[Personal] --------------------------------------------------------
  Email: Unavailable (auth error)
  Calendar (2 events)
    ...
```

### 7.3 Graceful Degradation 전략

```python
def _get_state(self, include_personal: bool = True) -> DashboardState:
    personal = SecretaryResult.empty()
    projects = ChecklistResult(projects=[], scan_paths=[], scanned_at="")
    warnings = []

    # 1. Secretary 호출 (실패해도 계속)
    if include_personal:
        try:
            personal = self._call_secretary()
        except SecretaryError as e:
            warnings.append(f"Personal data unavailable: {e}")

    # 2. Checklist 스캔 (실패해도 계속)
    try:
        projects = self.parser.scan()
    except ChecklistError as e:
        warnings.append(f"Checklist scan failed: {e}")

    return DashboardState(
        personal=personal,
        projects=projects,
        warnings=warnings,
        generated_at=datetime.now().isoformat()
    )
```

---

## 8. 테스트 전략

### 8.1 테스트 범위

| 레벨 | 대상 | 테스트 유형 |
|------|------|------------|
| **Unit** | `ChecklistParser` | 파싱 로직, 엣지 케이스 |
| **Unit** | `DashboardFormatter` | 출력 포맷 검증 |
| **Integration** | `DailyDashboard` | Secretary 연동, 전체 흐름 |
| **E2E** | `/daily` 커맨드 | CLI 실행, 실제 파일 |

### 8.2 Unit Test: ChecklistParser

```python
# tests/test_checklist_parser.py

import pytest
from pathlib import Path
from checklist_parser import ChecklistParser, ChecklistProject, ChecklistItem


class TestChecklistParser:

    @pytest.fixture
    def parser(self, tmp_path):
        return ChecklistParser(tmp_path)

    def test_parse_standard_checklist(self, parser, tmp_path):
        """CHECKLIST_STANDARD.md 형식 파싱"""
        content = """# [PRD-0001] Checklist

**Status**: In Progress

## Phase 1: 설계

- [x] 요구사항 분석 (#101)
- [ ] API 설계
"""
        checklist_file = tmp_path / "docs" / "checklists" / "PRD-0001.md"
        checklist_file.parent.mkdir(parents=True)
        checklist_file.write_text(content, encoding="utf-8")

        project = parser.parse_file(checklist_file)

        assert project.prd_id == "PRD-0001"
        assert project.status == "In Progress"
        assert len(project.items) == 2
        assert project.completed_items == 1
        assert project.progress == 50.0

    def test_extract_pr_number(self, parser):
        """PR 번호 추출"""
        item = parser._parse_item("- [x] 완료됨 (#123)")
        assert item.pr_number == 123

    def test_no_prd_id_returns_none(self, parser, tmp_path):
        """PRD ID 없는 파일은 None 반환"""
        content = "# Random Checklist\n- [ ] Item 1"
        file = tmp_path / "random.md"
        file.write_text(content)

        assert parser.parse_file(file) is None

    def test_empty_checklist(self, parser, tmp_path):
        """Checkbox 없는 파일"""
        content = "# [PRD-0002] Checklist\n**Status**: In Progress\nNo items yet."
        file = tmp_path / "PRD-0002.md"
        file.write_text(content)

        project = parser.parse_file(file)
        assert project.total_items == 0
        assert project.progress == 0.0

    def test_scan_multiple_paths(self, parser, tmp_path):
        """여러 경로 스캔"""
        # 두 개의 checklist 생성
        (tmp_path / "docs" / "checklists").mkdir(parents=True)
        (tmp_path / "docs" / "checklists" / "PRD-0001.md").write_text(
            "# [PRD-0001] Test\n**Status**: In Progress\n- [x] Done"
        )
        (tmp_path / "docs" / "checklists" / "PRD-0002.md").write_text(
            "# [PRD-0002] Test\n**Status**: In Progress\n- [ ] Pending"
        )

        result = parser.scan(["docs/checklists"])

        assert len(result.projects) == 2
```

### 8.3 Integration Test: DailyDashboard

```python
# tests/test_daily_dashboard.py

import pytest
from unittest.mock import patch, MagicMock
from daily_dashboard import DailyDashboard, SecretaryResult


class TestDailyDashboard:

    @pytest.fixture
    def dashboard(self, tmp_path):
        return DailyDashboard(base_path=tmp_path)

    @patch.object(DailyDashboard, '_call_secretary')
    def test_run_default(self, mock_secretary, dashboard, tmp_path):
        """기본 대시보드 실행"""
        # Mock secretary 결과
        mock_secretary.return_value = SecretaryResult(
            gmail={"tasks": [{"subject": "Test", "priority": "high"}]},
            calendar={"events": []},
            github={"attention_needed": []},
            generated_at="2026-02-05T09:00:00"
        )

        # Checklist 파일 생성
        (tmp_path / "docs" / "checklists").mkdir(parents=True)
        (tmp_path / "docs" / "checklists" / "PRD-0001.md").write_text(
            "# [PRD-0001] Test\n**Status**: In Progress\n- [x] Done\n- [ ] Pending"
        )

        output = dashboard.run()

        assert "Daily Dashboard" in output
        assert "PRD-0001" in output
        assert "50%" in output  # 1/2 완료

    def test_run_projects_only(self, dashboard, tmp_path):
        """프로젝트만 출력"""
        (tmp_path / "docs" / "checklists").mkdir(parents=True)
        (tmp_path / "docs" / "checklists" / "PRD-0001.md").write_text(
            "# [PRD-0001] Test\n**Status**: In Progress\n- [x] Done"
        )

        output = dashboard.run(subcommand="projects")

        assert "Project Progress" in output
        assert "PRD-0001" in output
        assert "Email" not in output  # 개인 업무 없음

    def test_graceful_degradation_on_secretary_error(self, dashboard, tmp_path):
        """Secretary 실패 시 프로젝트만 출력"""
        # Secretary 스크립트 없음 시뮬레이션
        dashboard.SECRETARY_SCRIPT = tmp_path / "nonexistent.py"

        (tmp_path / "docs" / "checklists").mkdir(parents=True)
        (tmp_path / "docs" / "checklists" / "PRD-0001.md").write_text(
            "# [PRD-0001] Test\n- [x] Done"
        )

        output = dashboard.run()

        assert "Warning" in output
        assert "PRD-0001" in output  # 프로젝트는 출력됨
```

### 8.4 테스트 실행 명령

```powershell
# Unit 테스트만
pytest tests/test_checklist_parser.py -v

# Integration 테스트
pytest tests/test_daily_dashboard.py -v

# 전체 테스트 + 커버리지
pytest tests/ -v --cov=.claude/skills/daily/scripts
```

---

## 9. SKILL.md 정의

```yaml
---
name: daily
description: >
  Daily Dashboard - 개인 업무와 프로젝트 진행률을 통합하여 한눈에 파악.
  /secretary와 Slack List Checklist를 결합한 통합 현황 대시보드.
version: 1.0.0

triggers:
  keywords:
    - "daily"
    - "오늘 현황"
    - "일일 대시보드"
    - "프로젝트 진행률"
    - "전체 현황"
  file_patterns:
    - "**/daily/**"
    - "**/checklists/**"
  context:
    - "업무 현황"
    - "프로젝트 관리"

capabilities:
  - daily_dashboard
  - project_progress
  - standup_briefing
  - retro_review

model_preference: sonnet
auto_trigger: true
---

# Daily Skill - 통합 대시보드

개인 업무(/secretary)와 프로젝트 진행률(Slack List)을 단일 대시보드로 통합합니다.

## 사용법

### 전체 대시보드

```bash
python .claude/skills/daily/scripts/daily_dashboard.py
```

### 서브커맨드

| 커맨드 | 설명 | 용도 |
|--------|------|------|
| `/daily` | 전체 대시보드 | 기본 |
| `/daily standup` | 아침 브리핑 | 하루 시작 |
| `/daily retro` | 저녁 회고 | 하루 마무리 |
| `/daily projects` | 프로젝트만 | 진행률 확인 |

### 옵션

| 옵션 | 설명 |
|------|------|
| `--json` | JSON 형식 출력 |
| `--no-personal` | 개인 업무 제외 |
| `--no-projects` | 프로젝트 제외 |

## 연동 시스템

| 시스템 | 데이터 |
|--------|--------|
| `/secretary` | Gmail, Calendar, GitHub |
| Slack List | `docs/checklists/*.md` |

## 변경 로그

| 버전 | 변경 |
|------|------|
| 1.0.0 | 초기 릴리스 |
```

---

## 10. 구현 우선순위

### Phase 1: MVP (P0 + 핵심 P1)

| 순서 | 작업 | 파일 | 예상 시간 |
|:----:|------|------|:--------:|
| 1 | SKILL.md 생성 | `.claude/skills/daily/SKILL.md` | 15m |
| 2 | ChecklistParser 구현 | `scripts/checklist_parser.py` | 1h |
| 3 | ChecklistParser 테스트 | `tests/test_checklist_parser.py` | 30m |
| 4 | DailyDashboard 메인 | `scripts/daily_dashboard.py` | 1.5h |
| 5 | 기본 대시보드 포맷터 | (4에 포함) | - |
| 6 | Integration 테스트 | `tests/test_daily_dashboard.py` | 30m |

**MVP 완료 조건**: `/daily` 실행 시 개인 업무 + 프로젝트 진행률 통합 출력

### Phase 2: 서브커맨드 (P1)

| 순서 | 작업 | 예상 시간 |
|:----:|------|:--------:|
| 1 | `standup` 포맷터 | 30m |
| 2 | `retro` 포맷터 | 30m |
| 3 | `projects` 포맷터 | 15m |
| 4 | 템플릿 파일 | 15m |

### Phase 3: 연결 정보 (P2 - 선택)

| 작업 | 예상 시간 |
|------|:--------:|
| PRDLinker 모듈 | 2h |
| 이메일 → PRD 매칭 | 1h |
| PR → Checklist 매칭 | 1h |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-05 | 1.0.0 | 초기 Design 문서 작성 |
