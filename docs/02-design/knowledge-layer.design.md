# Design: Knowledge Layer - daily v3.0 학습/인덱싱 아키텍처

**Version**: 1.0.0
**Created**: 2026-02-13
**Plan Reference**: `docs/01-plan/knowledge-layer.plan.md` (v1.1.0, Approved)
**Parent Design**: `docs/02-design/daily-redesign.design.md` (v1.0.0)
**Relationship**: daily-redesign.design.md의 **확장 및 부분 Supersede**

---

## 1. 컴포넌트 설계

### 1.1 Knowledge Storage Layer

| 컴포넌트 | 파일 | 크기 제한 | 역할 |
|----------|------|:---------:|------|
| Entity Registry | `knowledge/entities.json` | 200KB, 200개 | 업체/사람/제품/프로젝트/조직/토픽 추적 |
| Relationship Graph | `knowledge/relationships.json` | 50KB, 500개 | Entity 간 관계 (reports_to, provides 등) |
| Pattern Store | `knowledge/patterns.json` | 50KB, 100개 | 반복 패턴 + action_feedback + false_positives |

### 1.2 Event Logging System

| 컴포넌트 | 파일 | 크기 제한 | 역할 |
|----------|------|:---------:|------|
| Event Log | `knowledge/events/YYYY-MM.jsonl` | 500KB/월 | Append-only 월별 이벤트 기록 |
| Event Index | `knowledge/events/index.json` | 100KB | by_entity, by_topic, by_month 인덱스 |

### 1.3 Cross-Session Bridge

| 컴포넌트 | 파일 | 크기 제한 | 역할 |
|----------|------|:---------:|------|
| Knowledge Snapshot | `knowledge/snapshots/latest.json` | 5KB (~1300t) | 비-daily 세션용 압축 지식 |
| Daily Snapshot | `knowledge/snapshots/YYYY-MM-DD.json` | 5KB | 일별 스냅샷 (7일 보존) |

### 1.4 Eviction Engine (Phase 8C)

| 대상 | 임계값 | 정책 |
|------|:------:|------|
| Entity | 200개, 90일 미참조 | LRU 퇴거 + 관계 연쇄 삭제 |
| Pattern | 100개, 60일 미확인 | 삭제 또는 유사도 > 0.8 병합 |
| Event | 6개월 | 요약 1줄 보존 후 원본 삭제 |
| Snapshot | 7일 | 초과 일별 스냅샷 삭제 |

---

## 2. 인터페이스 정의

### 2.1 Phase 8B: Entity Update Interface

```
Input:  Phase 4 분석 결과 (JSON) + 기존 entities.json
Output: 갱신된 entities.json, relationships.json, patterns.json
Logic:  Entity 추출 프롬프트 → confidence 산출 → 매칭/생성/퇴거
Detail: Plan Section 4.4 참조
```

### 2.2 Phase 8B: Event Record Interface

```
Input:  이벤트 데이터 (source, type, entities, topics, summary)
Output: events/YYYY-MM.jsonl append + index.json 갱신
Format: {"id":"evt_YYYYMMDD_NNN", "ts":"ISO", "source":"gmail|slack|github", ...}
Detail: Plan Section 5.1-5.3 참조
```

### 2.3 Phase 8C: Snapshot Generation Interface

```
Input:  entities.json + events/ + patterns.json
Output: snapshots/latest.json (5KB, ~1300t)
Logic:  상위 10 entities + 7일 이벤트 요약 + 활성 패턴 5개
Budget: Entity별 80t, 전체 1300t, 초과 시 자동 축소
Detail: Plan Section 6.2.2 참조
```

### 2.4 Step 0.0: Knowledge Loading Interface

```
Input:  프로젝트명 (.project-sync.yaml 또는 CWD)
Output: 컨텍스트 문자열 (~1300t)
Source: .omc/daily-state/<project>/knowledge/snapshots/latest.json
Inject: project_phase, active_topics, key_entities, recent_events, active_patterns
Detail: Plan Section 6.3 참조
```

---

## 3. 데이터 흐름

```
Phase 2 (수집)
    │ Gmail/Slack/GitHub 증분 데이터
    ▼
Phase 4 (분석)
    │ AI 크로스소스 분석 결과
    │ ← snapshots/latest.json의 recent_events_digest 주입
    ▼
Phase 8B (Knowledge Update)
    │ Entity 추출 → entities.json
    │ Relationship → relationships.json
    │ Pattern → patterns.json
    │ Event → events/YYYY-MM.jsonl + index.json
    ▼
Phase 8C (Snapshot & Eviction)
    │ → snapshots/latest.json (5KB)
    │ → Eviction (6개월 이벤트, 90일 entity, 60일 pattern)
    │ → Notepad Wisdom (.omc/notepads/<project>/)
    ▼
비-daily 세션 Step 0.0
    │ ← snapshots/latest.json 로드 (~1300t)
    └── 작업 컨텍스트에 프로젝트 지식 주입
```

---

## 4. 파일 디렉토리 구조

```
.omc/daily-state/<project>/
  state.json                    # v2.0 (커서, 캐시, knowledge_path)
  knowledge/
    entities.json               # Entity Registry (200KB)
    relationships.json          # Relationship Graph (50KB)
    patterns.json               # Pattern Store (50KB)
    events/
      YYYY-MM.jsonl             # Monthly Event Log (500KB)
      index.json                # Event Index (100KB)
    snapshots/
      latest.json               # Cross-Session Snapshot (5KB)
      YYYY-MM-DD.json           # Daily Snapshot (5KB, 7일)
```

**프로젝트당 최대 크기**: ~1.5MB

---

## 5. 토큰 예산

| Tier | 소스 | 예산 |
|------|------|:----:|
| Tier 1: Identity | CLAUDE.md + .project-sync.yaml | 500t |
| Tier 2: Operational | snapshots/latest.json | 1300t |
| Tier 3: Deep | docs/ 핵심 문서 | 3000t |
| **합계** | | **4800t** (5500t 예산 내, 700t 여유) |

---

## 6. daily-redesign.design.md와의 관계

| 구분 | 대상 | 처리 |
|------|------|------|
| **Supersede** | Phase 8B 학습 로직 (learned_context.update/extend) | Knowledge Layer로 대체 |
| **Supersede** | Phase 1 Tier 2 소스 (state.json learned_context) | snapshots/latest.json |
| **Supersede** | state.json 스키마 (learned_context 필드) | knowledge_path 필드 |
| **보존** | Phase 0-7 전체 | 변경 없음 |
| **보존** | Phase 8A (Cursor Update) | 변경 없음 |
| **확장** | Phase 4 프롬프트 | 이전 이벤트 다이제스트 주입 추가 |
| **확장** | Phase 8 (8C 추가) | Snapshot + Eviction + Notepad |

---

## 7. 위험 요소 및 완화 방안

| # | 위험 | 영향 | 확률 | 완화 |
|:-:|------|------|:----:|------|
| 1 | Entity 추출 품질 불안정 | 노이즈 entity 누적 | 중 | confidence >= 0.5 필터 + false_positives 목록 |
| 2 | Snapshot 토큰 초과 (한글) | Phase 1/Step 0.0 예산 초과 | 중 | 5KB 제한 + 자동 축소 로직 |
| 3 | JSONL 파일 크기 증가 | 디스크 사용량 | 낮 | 6개월 퇴거 + 500KB/월 제한 |
| 4 | SKILL.md 500줄 초과 | 유지보수성 저하 | 낮 | 참조 패턴 (상세 → Plan 문서) |
| 5 | 초회 실행 시 Knowledge 미존재 | Step 0.0 건너뜀 | - | 의도적 설계 (daily 선실행 권장) |

---

## 변경 이력

- **1.0.0** (2026-02-13): 초기 설계 문서 작성
