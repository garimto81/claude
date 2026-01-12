# PRD-0031: 문서 통합 관리 시스템

> **Version**: 1.0.0 | **Status**: Completed | **Priority**: P0
>
> **Created**: 2026-01-12 | **Namespace**: MAIN

---

## 1. 개요

### 1.1 배경

5개 프로젝트(MAIN, HUB, FT, SUB, AE)가 각각 독립적인 문서 체계를 가지고 있어 다음과 같은 문제가 발생:

| 문제 | 영향 |
|------|------|
| PRD 번호 중복 | 모든 프로젝트가 0001부터 시작하여 혼란 |
| 분산된 문서 | 검색/탐색 어려움, 유지보수 부담 |
| 일관성 부재 | 파일명 패턴, 경로 구조 불일치 |
| 크로스 참조 복잡 | 프로젝트 간 문서 링크 관리 어려움 |

### 1.2 목표

- 모든 문서를 `C:\claude\docs\unified/`에 물리적 통합
- 프로젝트별 네임스페이스 접두어로 고유 식별자 부여
- 각 프로젝트는 CLAUDE.md만 유지하고 문서는 중앙 관리
- 통합 인덱스와 레지스트리로 검색/탐색 용이성 확보

---

## 2. 설계

### 2.1 네임스페이스 정의

| 접두어 | 프로젝트 | 경로 | 설명 |
|--------|----------|------|------|
| **MAIN** | C:\claude | 루트 | Claude Code 환경, 워크플로우, 에이전트 |
| **HUB** | automation_hub | 공유 인프라 | PostgreSQL, Pydantic 모델, Repository |
| **FT** | automation_feature_table | RFID 처리 | PokerGFX, 핸드 캡처, Fusion Engine |
| **SUB** | automation_sub | 방송 그래픽 | WSOP 자막, Caption DB |
| **AE** | automation_ae | AE 렌더링 | After Effects, Nexrender, 템플릿 |

### 2.2 통합 폴더 구조

```
C:\claude\docs\unified\
├── prds/                    # PRD 문서
│   ├── MAIN/               # MAIN-0001 ~ MAIN-0031
│   ├── HUB/                # HUB-0001 ~ HUB-0006
│   ├── FT/                 # FT-0001 ~ FT-0011
│   ├── SUB/                # SUB-0001 ~ SUB-0007
│   └── AE/                 # AE-0001 ~ AE-0005
│
├── specs/                   # 기술 명세서
│   └── SUB/                # SUB-0001-spec ~ SUB-0007-spec
│
├── tasks/                   # 작업 문서
│   ├── MAIN/               # MAIN-XXXX-tasks
│   └── AE/                 # AE-XXXX-tasks
│
├── archive/                 # 아카이브
│   ├── HUB/                # HUB-0000 등
│   └── SUB/                # SUB-0004 등
│
├── checklists/             # 체크리스트
│   ├── MAIN/
│   ├── HUB/
│   ├── FT/
│   ├── SUB/
│   └── AE/
│
├── images/                  # 이미지 (접두어로 구분)
│   └── {namespace}-{number}-{desc}.png
│
├── mockups/                 # HTML 목업
│   └── {namespace}-{slug}.html
│
├── index.md                 # 통합 인덱스
└── registry.json            # 메타데이터 레지스트리
```

### 2.3 파일명 규칙

| 유형 | 패턴 | 예시 |
|------|------|------|
| PRD | `{NS}-{NNNN}-{slug}.md` | `HUB-0001-automation-hub-v2.md` |
| Spec | `{NS}-{NNNN}-spec-{slug}.md` | `SUB-0003-spec-caption-database.md` |
| Task | `{NS}-{NNNN}-tasks.md` | `MAIN-0026-tasks.md` |
| Archive | `{NS}-{NNNN}-{slug}.md` | `HUB-0000-automation-hub-integration.md` |
| Image | `{ns}-{nnnn}-{desc}.png` | `hub-0005-architecture.png` |

### 2.4 레지스트리 스키마 (registry.json)

```json
{
  "version": "2.0.0",
  "last_updated": "2026-01-12T00:00:00Z",
  "namespaces": {
    "MAIN": { "name": "Claude Root", "path": "C:\\claude", "color": "#4A90D9" },
    "HUB": { "name": "Automation Hub", "path": "...", "color": "#7B68EE" },
    ...
  },
  "prds": {
    "HUB-0001": {
      "title": "WSOP Automation Hub v2.0",
      "slug": "automation-hub-v2",
      "status": "Draft",
      "priority": "P0",
      "namespace": "HUB",
      "original_id": "PRD-0001",
      "path": "prds/HUB/HUB-0001-automation-hub-v2.md",
      "created_at": "2025-12-26",
      "tags": ["infrastructure", "database"]
    }
  },
  "statistics": {
    "total_prds": 37,
    "by_namespace": { "MAIN": 9, "HUB": 6, ... }
  }
}
```

---

## 3. 구현

### 3.1 마이그레이션 프로세스

```
Phase 1: 인프라 구축
├── docs/unified/ 폴더 구조 생성
├── registry.json 스키마 정의
└── index.md 템플릿 생성

Phase 2: PRD 마이그레이션
├── HUB (6개) → docs/unified/prds/HUB/
├── FT (10개) → docs/unified/prds/FT/
├── AE (6개) → docs/unified/prds/AE/
├── SUB (6개) → docs/unified/prds/SUB/
└── MAIN (9개) → docs/unified/prds/MAIN/

Phase 3: 추가 문서 마이그레이션
├── Specs (4개) → docs/unified/specs/SUB/
├── Tasks (4개) → docs/unified/tasks/
└── Archive (12개) → docs/unified/archive/

Phase 4: 정리
├── 기존 tasks 폴더 제거
├── CLAUDE.md 업데이트
└── index.md 완성
```

### 3.2 마이그레이션 스크립트

**위치**: `C:\claude\scripts\migrate-docs.ps1`

```powershell
# 사용법
.\migrate-docs.ps1 -Namespace HUB -DryRun    # 미리보기
.\migrate-docs.ps1 -Namespace ALL            # 전체 마이그레이션
```

**기능**:
- 파일명 변환 (PRD-0001 → HUB-0001)
- 내부 링크 자동 업데이트
- 네임스페이스별 폴더 자동 생성

### 3.3 CLAUDE.md 업데이트

각 프로젝트의 CLAUDE.md에 통합 문서 참조 섹션 추가:

```markdown
## 문서 (통합 관리)

> 이 프로젝트의 모든 문서는 **루트 프로젝트**에서 통합 관리됩니다.
>
> **절대 경로**: `C:\claude\docs\unified\`

| 유형 | 위치 | 네임스페이스 |
|------|------|-------------|
| PRD | `docs/unified/prds/{NS}/` | {NS}-0001 ~ {NS}-NNNN |

**전체 문서 인덱스**: [C:\claude\docs\unified\index.md](../docs/unified/index.md)
```

---

## 4. 결과

### 4.1 통합 현황

| 유형 | 수량 | 설명 |
|------|:----:|------|
| **PRD** | 37 | MAIN(9), HUB(6), FT(10), SUB(6), AE(6) |
| **Spec** | 4 | SUB 기술 명세서 |
| **Tasks** | 4 | MAIN(3), AE(1) |
| **Archive** | 12 | HUB(2), SUB(10) |
| **총합** | **57** | 전체 마이그레이션 완료 |

### 4.2 제거된 항목

| 프로젝트 | 제거된 폴더 |
|---------|------------|
| C:\claude | tasks/ |
| automation_hub | tasks/ |
| automation_feature_table | tasks/ |
| automation_sub | tasks/ |
| automation_ae | tasks/ |

### 4.3 업데이트된 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\CLAUDE.md` | 통합 문서 구조 섹션 추가 |
| `automation_hub\CLAUDE.md` | 문서 참조 섹션 간소화 |
| `automation_feature_table\CLAUDE.md` | 문서 참조 섹션 간소화 |
| `automation_sub\CLAUDE.md` | 문서 참조 섹션 간소화 |
| `automation_ae\CLAUDE.md` | 문서 참조 섹션 간소화 |

---

## 5. 사용 가이드

### 5.1 새 PRD 생성

```powershell
# 1. PRD 파일 생성
docs/unified/prds/{NS}/{NS}-{NNNN}-{slug}.md

# 2. 체크리스트 생성 (선택)
docs/unified/checklists/{NS}/{NS}-{NNNN}.md

# 3. registry.json 업데이트
# 4. index.md에 항목 추가
```

### 5.2 문서 검색

```powershell
# 전체 PRD 목록
Get-ChildItem -Recurse "C:\claude\docs\unified\prds" -Filter "*.md"

# 특정 네임스페이스
Get-ChildItem "C:\claude\docs\unified\prds\HUB" -Filter "*.md"

# 키워드 검색
Select-String -Path "C:\claude\docs\unified\prds\**\*.md" -Pattern "Supabase"
```

### 5.3 크로스 프로젝트 참조

```markdown
<!-- 같은 네임스페이스 -->
[HUB-0002](./HUB-0002-conflict-monitoring.md)

<!-- 다른 네임스페이스 -->
[FT-0001](../FT/FT-0001-poker-hand-auto-capture.md)

<!-- 절대 경로 (권장) -->
[HUB-0001](/docs/unified/prds/HUB/HUB-0001-automation-hub-v2.md)
```

---

## 6. 유지보수

### 6.1 문서 추가 시 체크리스트

- [ ] 네임스페이스 접두어 사용 (MAIN, HUB, FT, SUB, AE)
- [ ] 올바른 폴더에 배치 (prds/, specs/, tasks/, archive/)
- [ ] registry.json 업데이트
- [ ] index.md에 항목 추가
- [ ] 내부 링크 검증

### 6.2 검증 스크립트

```powershell
# 링크 검증
.\scripts\validate-docs.ps1 -CheckLinks

# registry.json 동기화 확인
.\scripts\validate-docs.ps1 -CheckRegistry
```

---

## Changelog

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-12 | 초기 버전 - 57개 문서 통합 완료 |
