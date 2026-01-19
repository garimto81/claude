# WSOPTV OTT Project - CLAUDE.md

**Version**: 1.0.0
**Project**: WSOPTV OTT Platform

---

## 프로젝트 개요

WSOP(World Series of Poker) 공식 OTT 스트리밍 플랫폼 구축 프로젝트.

### 핵심 기능

- 5개 플랫폼 (Web, iOS, Android, Samsung TV, LG TV)
- 라이브 스트리밍, VOD, Timeshift
- Advanced Mode (3계층 Multi-view, StatsView)
- 20개국 다국어 자막
- GGPass SSO 연동

---

## 문서 규칙

### 문서 위치

| 유형 | 경로 | 명명 규칙 |
|------|------|-----------|
| PRD | `docs/prds/` | `PRD-NNNN-*.md` |
| ADR | `docs/adrs/` | `ADR-NNNN-*.md` |
| Strategy | `docs/strategies/` | `STRAT-NNNN-*.md` |
| Report | `docs/reports/` | `REPORT-YYYY-MM-DD-*.md` |
| Images | `docs/images/[문서ID]/` | `*.png` |
| Mockups | `docs/mockups/[문서ID]/` | `*.html` |

### 문서 참조

문서 내 상대 경로 사용:

```markdown
# prds/ 폴더에서 다른 문서 참조
[PRD-0006](PRD-0006-advanced-mode.md)                    # 같은 폴더
[ADR-0001](../adrs/ADR-0001-multiview-3layer-rationale.md)  # 다른 폴더
[이미지](../images/PRD-0002/architecture.png)             # 이미지
```

### 문서 인덱스

**메인 인덱스**: [docs/README.md](docs/README.md)

---

## 핵심 문서

| 문서 | 설명 |
|------|------|
| [PRD-0002](docs/prds/PRD-0002-wsoptv-ott-platform-mvp.md) | MVP 플랫폼 스펙 (중심 문서) |
| [PRD-0006](docs/prds/PRD-0006-advanced-mode.md) | Advanced Mode 상세 |
| [ADR-0001](docs/adrs/ADR-0001-multiview-3layer-rationale.md) | 3계층 Multi-view 설계 근거 |
| [STRAT-0003](docs/strategies/STRAT-0003-cross-promotion.md) | 프로모션 전략 |
| [STRAT-0007](docs/strategies/STRAT-0007-content-sourcing.md) | 콘텐츠 소싱 전략 |

---

## 시각 자료 규칙

### 목업 생성

```powershell
# HTML 목업 생성
Write docs/mockups/PRD-0002/feature-name.html

# 스크린샷 캡처 (Playwright)
npx playwright screenshot docs/mockups/PRD-0002/feature-name.html docs/images/PRD-0002/feature-name.png
```

### 문서에 삽입

```markdown
![Feature Name](../images/PRD-0002/feature-name.png)

[HTML 원본](../mockups/PRD-0002/feature-name.html)
```

---

## 상위 규칙 상속

이 프로젝트는 `C:\claude\CLAUDE.md`의 규칙을 상속합니다.

### 주요 상속 규칙

- 언어: 한글 출력, 기술 용어 영어 유지
- 경로: 절대 경로 (`C:\claude\wsoptv_ott\...`)
- TDD: 테스트 먼저 작성
- Git: Conventional Commit 준수

---

*Last Updated: 2026-01-19*
