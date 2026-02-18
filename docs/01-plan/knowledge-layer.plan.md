# Plan: Knowledge Layer - daily v3.0 학습/인덱싱 아키텍처

> daily v3.0의 "학습+기억+활용 계층" 설계 - 비전 달성율 35% -> 80% 목표

**Version**: 1.1.0
**Created**: 2026-02-13
**Status**: Approved (Ralplan Consensus, Iteration 2, Critic Verdict: OKAY)
**Plan Reference**: `C:\claude\docs\01-plan\daily-redesign.plan.md` (v2.2.1, Approved)
**Relationship**: daily-redesign.plan.md의 **확장 및 부분 Supersede** (아래 Section 17 참조)
**Complexity**: 5/5 (5개 GAP, 크로스시스템 영향)

---

## 1. 배경 및 문제 정의

### 1.1 현재 상태 (AS-IS)

daily v3.0은 9-Phase Pipeline(수집+분석+액션추천)이 설계되었으나, "학습+기억+활용" 계층이 완전히 부재합니다. daily v3.0 자체는 아직 구현되지 않았으며(`.omc/daily-state/` 디렉토리 미존재), Plan 문서만 Approved 상태입니다.

```
현재 daily v3.0 Phase 8 학습 로직 (daily-redesign.plan.md Section 3.3.1 정의):
  state["learned_context"]["entities"].update(new_entities)
  state["learned_context"]["patterns"].extend(new_patterns)

문제:
  .update() -> 이전 entity 상태를 덮어씀 (이력 소실)
  .extend() -> 무한 성장 (퇴거 정책 없음)
  entities -> 빈 {} (스키마 미정의)
  비-daily 세션 -> 이 지식을 전혀 참조하지 않음
```

### 1.2 5개 GAP 상세

| # | GAP | 심각도 | 핵심 문제 |
|:-:|-----|:------:|----------|
| 1 | 비-daily 세션에서 학습 지식 활용 0% | CRITICAL | auto/SKILL.md에 daily-state 참조 없음. /auto, /work 세션은 daily가 축적한 entity/pattern을 전혀 모름 |
| 2 | Entity 스키마/추출 로직 미정의 | CRITICAL | `learned_context.entities`가 빈 `{}`로만 정의. 관계, 상태 이력, 시간 추적 없음 |
| 3 | Event Log/인덱싱 시스템 부재 | HIGH | 수집한 원본 데이터가 분석 후 폐기. 과거 이벤트 검색 불가 |
| 4 | 성장 한계/퇴거 정책 없음 | HIGH | patterns 무한 성장, entities 덮어씀, state 파일 크기 무한 증가 |
| 5 | Notepad Wisdom 시스템 미연동 | MEDIUM | `.omc/notepads/` 지식 저장소, `<remember>` 태그와 단절 |

### 1.3 근본 원인

daily v3.0 Plan(v2.2.1)이 "수집+분석 파이프라인"에 집중하여 Knowledge Layer의 구체적 스키마와 크로스 세션 활용 메커니즘을 정의하지 않았음.

---

## 2. 목표

### 2.1 핵심 목표

| # | 목표 | 측정 기준 | GAP |
|:-:|------|----------|:---:|
| 1 | Entity 스키마 정의 및 이력 추적 | Entity에 상태 이력, 관계, 시간 필드 존재 | GAP-2 |
| 2 | Event Log 시스템 구축 | JSONL 형식으로 이벤트 기록 + 날짜/entity별 검색 가능 | GAP-3 |
| 3 | Cross-Session Bridge | /auto, /work 세션에서 daily 지식 자동 로드 (5500t 예산 내) | GAP-1 |
| 4 | Growth/Eviction 정책 | 파일 크기 제한, 오래된 데이터 자동 퇴거 | GAP-4 |
| 5 | Notepad Wisdom 연동 | daily 학습 결과를 notepads에 기록, 기존 wisdom 참조 | GAP-5 |

### 2.2 비목표 (명시적 제외)

| 항목 | 이유 |
|------|------|
| 9-Phase Pipeline 구조 변경 | 기존 파이프라인 보존 원칙 |
| DB 기반 저장소 | JSON/JSONL 파일 기반 제약 |
| 실시간 인덱싱 | 일일 배치 워크플로우 |
| 벡터 임베딩 검색 | 복잡도 과다, 키워드 기반 검색으로 충분 |

## 구현 범위

### 영향 파일

**신규 생성 (7개 파일)**:
- `knowledge/entities.json` - Entity 레지스트리
- `knowledge/relationships.json` - 관계 그래프
- `knowledge/patterns.json` - 학습 패턴 + 피드백
- `knowledge/events/YYYY-MM.jsonl` - 월별 이벤트 로그
- `knowledge/events/index.json` - 이벤트 인덱스
- `knowledge/snapshots/latest.json` - 크로스 세션 스냅샷
- `knowledge/snapshots/YYYY-MM-DD.json` - 일별 스냅샷

**수정 (3개 파일)**:
- `daily/SKILL.md` - Phase 1/4/8 변경 (~25줄 추가)
- `auto/SKILL.md` - Step 0.0 추가 (~15줄)
- `daily-redesign.plan.md` - v2.3.0 갱신

**활용**:
- `.omc/notepads/{project}/*` - Notepad Wisdom 연동 대상

### 구현 Task (9개)

| Task | 에이전트 | 파일 | 독립/종속 |
|:----:|---------|------|----------|
| 1 | executor | daily-redesign.plan.md v2.3.0 | 독립 |
| 2 | executor-high | daily/SKILL.md Phase 8B | blockedBy: 1 |
| 3 | executor | daily/SKILL.md Phase 8B | blockedBy: 1 |
| 4 | executor | daily/SKILL.md Phase 8C | blockedBy: 2,3 |
| 5 | executor | daily/SKILL.md Phase 8C | blockedBy: 1 |
| 6 | executor-high | daily/SKILL.md Phase 1,4 | blockedBy: 4,5 |
| 7 | executor | auto/SKILL.md Step 0.0 | blockedBy: 4 |
| 8 | executor-low | daily/SKILL.md Phase 8C | blockedBy: 6 |
| 9 | architect | 통합 검증 | blockedBy: 6,7,8 |

자세한 내용은 Section 11 (예상 영향 파일), Section 12 (구현 순서) 참조.

---

## 3. Knowledge Layer 파일 구조

### 3.1 디렉토리 구조

daily v3.0이 아직 구현되지 않았으므로, **처음부터 directory 기반 구조로 설계**합니다. flat file(`<project>.json`) 대신 project 디렉토리를 사용합니다. daily-redesign.plan.md Section 3.3.1의 `<project-name>.json` 경로를 `<project-name>/state.json`으로 변경합니다 (Supersede, Section 17 참조).

```
C:\claude\.omc\daily-state\
  <project-name>\                 # flat file 대신 directory 구조 (처음부터)
    state.json                    # daily-state (커서, 캐시, run 메타)
    knowledge\
      entities.json               # Entity 레지스트리 (스키마 있는 entity 저장소)
      relationships.json          # Entity 간 관계 그래프
      patterns.json               # 학습된 패턴 (크기 제한 있음)
      events\
        YYYY-MM.jsonl             # 월별 Event Log (append-only)
        index.json                # 인덱스 메타 (entity별, topic별 포인터)
      snapshots\
        latest.json               # Cross-Session Bridge용 압축 스냅샷
        YYYY-MM-DD.json           # 일별 스냅샷 (7일 보존)
```

**마이그레이션 불필요**: `.omc/daily-state/` 디렉토리 자체가 아직 존재하지 않으므로 기존 데이터 마이그레이션이 필요 없습니다. daily-redesign.plan.md의 해당 섹션을 직접 수정하여 처음부터 directory 구조로 정의합니다.

### 3.2 파일별 역할과 크기 제한

| 파일 | 역할 | 최대 크기 | 퇴거 정책 |
|------|------|:---------:|----------|
| `state.json` | 커서, 캐시, run 메타데이터 | 100KB | 캐시 항목 90일 초과 시 삭제 |
| `entities.json` | Entity 레지스트리 (이력 포함) | 200KB | 최대 200 entities, LRU 퇴거 |
| `relationships.json` | Entity 간 관계 | 50KB | Entity 퇴거 시 연쇄 삭제 |
| `patterns.json` | 반복 패턴 + 피드백 | 50KB | 최대 100 patterns, 오래된 것 병합 |
| `YYYY-MM.jsonl` | 월별 이벤트 로그 | 500KB/월 | 6개월 보존, 이후 요약 후 삭제 |
| `index.json` | 이벤트 인덱스 | 100KB | 이벤트 퇴거 시 자동 정리 |
| `latest.json` | 크로스 세션 스냅샷 | 5KB (~1300t) | 매 daily 실행 시 덮어씀 |
| `YYYY-MM-DD.json` | 일별 스냅샷 | 5KB | 7일 보존 후 삭제 |

**전체 프로젝트당 Knowledge Layer 최대 크기: ~1.5MB**

**한글 토큰 환산 (H5 해결)**:
| 문자 유형 | 토큰 환산율 | 예시 |
|-----------|:----------:|------|
| 영어 단어 | ~0.75t/word | "Brightcove negotiating" = ~2t |
| 한글 단어 | ~1.5t/word | "견적 비교 요청" = ~4.5t |
| JSON 구조 | ~0.3t/char | `{"key":"value"}` = ~5t |

**Snapshot 토큰 예산 (변경: 8KB -> 5KB)**: 한글 비중이 높은 프로젝트에서 8KB JSON은 약 3000t에 달할 수 있으므로, 파일 크기를 5KB로 하향 조정합니다. Entity별 최대 80t, 전체 key_entities 최대 10개 = 800t, 나머지 구조 포함 총 ~1300t로 2000t 예산 이내를 보장합니다.

---

## 4. Entity Schema 설계

### 4.1 Entity 레지스트리 (`entities.json`)

```json
{
  "version": "1.0",
  "project": "wsoptv_ott",
  "updated_at": "2026-02-13T09:00:00Z",
  "entities": {
    "ent_brightcove": {
      "id": "ent_brightcove",
      "name": "Brightcove",
      "type": "vendor",
      "aliases": ["BC", "브라이트코브"],
      "created_at": "2026-01-15T10:00:00Z",
      "last_seen": "2026-02-13T09:00:00Z",
      "mention_count": 47,
      "current_state": {
        "status": "negotiating",
        "confidence": 0.85,
        "updated_at": "2026-02-12T09:00:00Z"
      },
      "state_history": [
        {
          "status": "evaluating",
          "from": "2026-01-15T10:00:00Z",
          "to": "2026-02-01T09:00:00Z",
          "trigger": "RFP 발송 (Gmail, 2026-01-15)"
        },
        {
          "status": "negotiating",
          "from": "2026-02-01T09:00:00Z",
          "to": null,
          "trigger": "견적 수신 (Gmail, 2026-02-01)"
        }
      ],
      "attributes": {
        "domain": "brightcove.com",
        "contact": "john@brightcove.com",
        "product": "Video Cloud Enterprise",
        "latest_quote": "$120K/yr"
      },
      "tags": ["ott", "video-platform", "enterprise"]
    }
  },
  "meta": {
    "total_entities": 1,
    "max_entities": 200,
    "types": {
      "vendor": 1,
      "person": 0,
      "product": 0,
      "project": 0,
      "organization": 0,
      "topic": 0
    }
  }
}
```

### 4.2 Entity 타입 정의

| 타입 | 설명 | 상태 필드 | 예시 |
|------|------|----------|------|
| `vendor` | 외부 업체 | status: evaluating/negotiating/contracted/rejected | Brightcove, Vimeo |
| `person` | 사람 (내부/외부) | role: decision-maker/contributor/contact | 김대표, John |
| `product` | 제품/서비스 | phase: evaluating/selected/deploying/active | VHX, Video Cloud |
| `project` | 프로젝트/이니셔티브 | phase: planning/active/completed/on-hold | WSOPTV MVP |
| `organization` | 회사/팀 | relationship: client/partner/vendor | EBS, JRMAX |
| `topic` | 반복 토픽 | status: active/resolved/recurring | CDN 성능, 라이선스 비용 |

### 4.3 관계 그래프 (`relationships.json`)

```json
{
  "version": "1.0",
  "updated_at": "2026-02-13T09:00:00Z",
  "relationships": [
    {
      "source": "ent_brightcove",
      "target": "ent_kim_daepyo",
      "type": "reports_to",
      "label": "견적 제출 대상",
      "created_at": "2026-02-01T09:00:00Z",
      "last_confirmed": "2026-02-12T09:00:00Z"
    }
  ],
  "meta": {
    "total_relationships": 1,
    "max_relationships": 500,
    "types": ["reports_to", "provides", "belongs_to", "related_to", "competes_with", "depends_on"]
  }
}
```

### 4.4 Entity 추출 프롬프트 및 품질 보장 (C4 해결)

#### 4.4.1 Entity 추출 프롬프트 구조

Phase 4 분석 완료 후, Phase 8B에서 아래 프롬프트로 entity 후보를 추출합니다.

**입력 (Phase 4 분석 결과 + 기존 entities.json):**
```
## Entity 추출 지시

아래 분석 결과에서 entity를 추출하세요.

### 분석 결과
{phase_4_analysis_output}

### 기존 Entity 목록 (ID, 이름, alias)
{existing_entities_summary}

### 출력 형식 (JSON)
다음 JSON 형식으로 정확히 출력하세요:
```

**출력 JSON 형식:**
```json
{
  "extracted_entities": [
    {
      "name": "Brightcove",
      "type": "vendor",
      "aliases": ["BC"],
      "matched_existing_id": "ent_brightcove",
      "status_update": {
        "new_status": "negotiating",
        "confidence": 0.85,
        "evidence": "수정 견적 $115K/yr 수신 메일 (2/13)"
      },
      "new_attributes": {
        "latest_quote": "$115K/yr"
      }
    },
    {
      "name": "Megazone",
      "type": "vendor",
      "aliases": ["메가존"],
      "matched_existing_id": null,
      "status_update": {
        "new_status": "evaluating",
        "confidence": 0.70,
        "evidence": "SI 제안서 수신 (Gmail, 2/11)"
      },
      "new_attributes": {
        "domain": "megazone.com",
        "product": "SI 서비스"
      }
    }
  ],
  "extracted_relationships": [
    {
      "source_name": "Megazone",
      "target_name": "김대표",
      "type": "reports_to",
      "label": "SI 제안서 검토 대상"
    }
  ]
}
```

**추출 규칙:**
- `matched_existing_id`: 기존 entity와 이름 또는 alias 매칭 시 ID 기입. 없으면 `null` (신규)
- `confidence`: 상태 판단 확신도 (아래 산출 공식 참조)
- 6개 entity 타입(`vendor`, `person`, `product`, `project`, `organization`, `topic`) 중 하나 지정
- entity당 최대 80t (snapshot 포함 시)

**예상 토큰 비용**: 입력 프롬프트 ~300t + 기존 entity 목록 ~200t = ~500t 추가. Phase 8 전체 토큰 예산에 포함.

#### 4.4.2 Confidence 산출 공식

```
confidence = base_score * evidence_multiplier * recency_factor

base_score (소스별):
  - 직접 명시 (메일 본문에 "계약 체결"): 0.95
  - 간접 추론 (견적 수신 -> negotiating 추론): 0.75
  - 맥락 추론 (회의 언급 -> 관계 추론): 0.55

evidence_multiplier:
  - 다중 소스 확인 (Gmail + Slack 모두 언급): 1.0
  - 단일 소스: 0.85
  - 메타데이터만 (제목만, 본문 없음): 0.65

recency_factor:
  - 오늘 데이터: 1.0
  - 7일 이내: 0.9
  - 30일 이내: 0.7
  - 30일 초과: 0.5

최종 confidence = round(base * multiplier * recency, 2)
예시: 직접 명시(0.95) * 다중 소스(1.0) * 오늘(1.0) = 0.95
예시: 간접 추론(0.75) * 단일 소스(0.85) * 오늘(1.0) = 0.64
```

**Confidence 활용:**
- confidence < 0.5: entity 생성하지 않음 (노이즈 방지)
- confidence 0.5~0.7: entity 생성하되 snapshot에서 제외
- confidence >= 0.7: 정상 추적 + snapshot 포함 대상

#### 4.4.3 Similarity 계산 (중복 패턴 병합용)

Pattern 퇴거 시 `similarity > 0.8` 조건의 계산 방법:

```
similarity(pattern_a, pattern_b) = keyword_overlap_ratio

keyword_overlap_ratio 계산:
  1. 각 pattern의 description에서 키워드 추출 (조사/접속사 제거)
  2. entities 배열의 겹침 확인
  3. 공식:
     keywords_a = set(pattern_a.description 키워드 + pattern_a.entities)
     keywords_b = set(pattern_b.description 키워드 + pattern_b.entities)
     similarity = len(keywords_a & keywords_b) / len(keywords_a | keywords_b)

예시:
  Pattern A: "Brightcove: 매주 수요일 follow-up 메일 발송", entities=["ent_brightcove"]
  Pattern B: "Brightcove: 수요일마다 follow-up 이메일", entities=["ent_brightcove"]
  keywords_a = {"Brightcove", "수요일", "follow-up", "메일", "발송", "ent_brightcove"}
  keywords_b = {"Brightcove", "수요일", "follow-up", "이메일", "ent_brightcove"}
  overlap = {"Brightcove", "수요일", "follow-up", "ent_brightcove"} = 4
  union = {"Brightcove", "수요일", "follow-up", "메일", "발송", "이메일", "ent_brightcove"} = 7
  similarity = 4/7 = 0.57 -> 병합하지 않음

  만약 description이 거의 동일하면 similarity > 0.8 -> 병합
```

### 4.5 Entity 상태 변화 추적 알고리즘

```
Phase 8B Entity Update 로직:

1. Phase 4 분석 결과로 Entity 추출 프롬프트 실행 (Section 4.4.1)
2. 추출된 각 entity에 대해:
   a. matched_existing_id로 entities.json 검색
   b. matched_existing_id가 null이면 alias/이름으로 fuzzy 검색
   c. 존재하면:
      - last_seen 갱신
      - mention_count 증가
      - confidence >= 0.5인 status_update가 있고, current_state와 다르면:
        * current_state -> state_history에 기록 (to = now)
        * current_state = new_status (from = now, confidence = 산출값)
        * trigger = evidence 필드
      - new_attributes 있으면 attributes에 merge
   d. 존재하지 않으면 (confidence >= 0.5인 경우만):
      - max_entities 미달 시 새 entity 생성
      - max_entities 도달 시 LRU(last_seen 가장 오래된) 퇴거 후 생성
3. extracted_relationships로 relationships.json 갱신
```

---

## 5. Event Log 설계

### 5.1 Event Log 형식 (`events/YYYY-MM.jsonl`)

JSONL 형식으로 한 줄에 하나의 이벤트를 기록합니다. Append-only로 수정하지 않습니다.

```jsonl
{"id":"evt_20260213_001","ts":"2026-02-13T09:15:00Z","source":"gmail","type":"email_received","entities":["ent_brightcove"],"topics":["견적","CDN"],"summary":"Brightcove 수정 견적 수신 ($115K/yr, CDN 포함)","data":{"email_id":"msg_abc123","sender":"john@brightcove.com","subject":"RE: WSOPTV 견적 수정안","urgency":"HIGH"},"run_id":6}
{"id":"evt_20260213_002","ts":"2026-02-13T09:15:00Z","source":"slack","type":"message","entities":["ent_kim_daepyo","ent_brightcove"],"topics":["견적","비교"],"summary":"김대표: Brightcove vs Vimeo 견적 비교 요청","data":{"channel":"C09TX3M1J2W","ts":"1707810900.000000"},"run_id":6}
```

### 5.2 Event 스키마

```json
{
  "id": "evt_YYYYMMDD_NNN",
  "ts": "ISO 8601 timestamp",
  "source": "gmail | slack | github",
  "type": "email_received | email_sent | message | decision | pr_created | pr_merged | issue_created | issue_closed | action_taken | status_change",
  "entities": ["entity_id_1", "entity_id_2"],
  "topics": ["topic_keyword_1", "topic_keyword_2"],
  "summary": "한 줄 요약 (최대 200자)",
  "data": {},
  "run_id": 6
}
```

### 5.3 인덱스 설계 (`events/index.json`)

```json
{
  "version": "1.0",
  "updated_at": "2026-02-13T09:15:00Z",
  "by_entity": {
    "ent_brightcove": {
      "event_count": 47,
      "months": ["2026-01", "2026-02"],
      "last_event": "evt_20260213_001",
      "first_event": "evt_20260115_003"
    }
  },
  "by_topic": {
    "견적": {
      "event_count": 23,
      "months": ["2026-01", "2026-02"],
      "last_event": "evt_20260213_001"
    }
  },
  "by_month": {
    "2026-02": {
      "event_count": 89,
      "file": "2026-02.jsonl",
      "size_bytes": 45000
    }
  },
  "meta": {
    "total_events": 245,
    "oldest_month": "2025-09",
    "retention_months": 6
  }
}
```

### 5.4 검색 알고리즘 및 사용 시점 (H6 해결)

**검색 vs Snapshot 사용 시점 분리:**

| 상황 | 데이터 소스 | 토큰 비용 |
|------|-----------|:---------:|
| daily Phase 4 (크로스소스 분석) | `snapshots/latest.json`의 `recent_events_digest` | ~200t (digest만) |
| daily Phase 8B (entity 갱신) | 당일 수집 데이터만 (JSONL 검색 불필요) | 0t (추가 비용 없음) |
| 비-daily 세션 Step 0.0 | `snapshots/latest.json` 전체 | ~1300t |
| ad-hoc 질문 ("Brightcove 히스토리 알려줘") | JSONL 검색 (index.json -> JSONL Grep) | ~500-2000t |

**핵심 원칙**: daily Phase 내에서는 JSONL 검색을 사용하지 않습니다. Snapshot의 `recent_events_digest`만 참조합니다. JSONL 검색은 사용자의 명시적 ad-hoc 질문 시에만 발생합니다.

**검색 유형 (ad-hoc 전용):**

```
검색 유형 1: Entity별 검색
  Input: entity_id
  Process:
    1. index.json의 by_entity[entity_id].months 확인
    2. 해당 월 JSONL 파일에서 entities 배열에 entity_id 포함된 행 필터
    3. 최신순 정렬, 최대 20건 반환
  토큰 비용: index.json 읽기 ~200t + JSONL Grep ~300-1500t

검색 유형 2: Topic별 검색
  Input: topic_keyword
  Process:
    1. index.json의 by_topic[keyword].months 확인
    2. 해당 월 JSONL 파일에서 topics 배열에 keyword 포함된 행 필터
    3. 최신순 정렬, 최대 20건 반환
  토큰 비용: ~200t + ~300-1500t

검색 유형 3: 날짜 범위 검색
  Input: start_date, end_date
  Process:
    1. index.json의 by_month에서 해당 월 목록 추출
    2. JSONL 파일에서 ts 범위 필터
    3. 시간순 정렬
  토큰 비용: ~200t + ~500-2000t (범위에 따라)
```

**검색 구현**: Claude가 Read tool로 index.json을 읽고, 필요한 JSONL 파일의 특정 행을 Grep으로 검색하는 패턴.

---

## 6. Cross-Session Bridge 설계

### 6.1 문제

현재 auto/SKILL.md의 Expert Context Loading은 daily 세션 내에서만 실행됩니다. /auto "기능 구현"처럼 비-daily 세션에서는 daily가 축적한 entity, pattern, event 지식이 전혀 로드되지 않습니다.

### 6.2 해결: Knowledge Snapshot 시스템

**매 daily 실행 완료 시** (Phase 8C), 전체 Knowledge Layer를 1300 토큰으로 압축한 스냅샷을 생성합니다.

#### 6.2.1 Snapshot 스키마 (`snapshots/latest.json`)

```json
{
  "version": "1.0",
  "project": "wsoptv_ott",
  "generated_at": "2026-02-13T09:30:00Z",
  "generated_by": "daily-v3.0-run-6",
  "token_budget": 1300,
  "summary": {
    "project_phase": "Phase 1 MVP - Vimeo 기반 구축 중",
    "active_topics": [
      "Brightcove vs Vimeo 견적 비교",
      "VHX 업로드 파이프라인 구축",
      "SI 업체 평가 진행"
    ],
    "pending_actions": [
      "Brightcove 수정 견적 회신 (D-3)",
      "SI 업체 RFP 마감 (D-7)"
    ]
  },
  "key_entities": [
    {
      "name": "Brightcove",
      "type": "vendor",
      "status": "negotiating",
      "latest": "수정 견적 $115K/yr 수신 (2/13)",
      "attention": "high"
    },
    {
      "name": "김대표",
      "type": "person",
      "role": "decision-maker",
      "latest": "견적 비교 요청 (2/13)"
    }
  ],
  "recent_events_digest": [
    "2/13: Brightcove 수정 견적 $115K/yr 수신 (Gmail)",
    "2/13: 김대표 견적 비교 요청 (Slack)",
    "2/12: PR #42 VHX 업로드 merged (GitHub)",
    "2/11: Megazone SI 제안서 수신 (Gmail)"
  ],
  "active_patterns": [
    "Brightcove: 매주 수요일 follow-up 메일 발송",
    "김대표: Slack에서 업체 현황 질문 후 1일 내 이메일 지시"
  ],
  "domain_vocabulary": ["RFP", "CDN", "DRM", "HLS", "VHX", "OTT"]
}
```

**Entity별 토큰 제한**: key_entities의 각 항목은 최대 80t. 최대 10개 entity = 800t. 나머지 구조(summary, events_digest, patterns, vocabulary) = ~500t. 총합 ~1300t로 2000t 예산 내 확보.

#### 6.2.2 Snapshot 생성 알고리즘

```
Phase 8C Snapshot Generation:

1. entities.json에서 attention이 높은 상위 10개 entity 추출
   - 기준: last_seen 최근 7일 + mention_count 상위
   - confidence >= 0.7인 entity만 포함
   - 각 entity 80t 이내로 압축
2. events/에서 최근 7일 이벤트 요약 (최대 10줄, 각 줄 50자 이내)
3. patterns.json에서 active pattern 상위 5개
4. 전체 JSON을 5KB 이내로 생성
5. 토큰 검증: JSON 문자 수 * 0.25 < 1300 확인
   - 초과 시: key_entities를 8개로 축소, events_digest를 7줄로 축소
6. snapshots/latest.json에 저장
7. snapshots/YYYY-MM-DD.json에도 사본 저장 (7일 보존)
```

### 6.3 auto/SKILL.md 변경 사항

auto/SKILL.md에 Step 0.0 Knowledge Context Loading을 추가합니다.

**추가 위치**: Phase 0 PDCA 문서화의 Step 0.1 (Plan 생성) 직전

**실행 조건 (H7 해결)**: `--daily` 옵션이 없는 경우에만 실행합니다. `--daily` 옵션이 있으면 `Skill(skill="daily")`로 위임되어 auto의 Phase 0 자체가 실행되지 않으므로, Step 0.0의 "daily 여부 판단" 로직은 불필요합니다. 단순히 Step 0.0이 항상 실행되고, `--daily` 세션에서는 auto Phase 0에 도달하지 않습니다.

**추가 내용**:

```markdown
### Step 0.0: Knowledge Context Loading

daily가 축적한 프로젝트 지식을 작업 세션에서 활용합니다.

**로드 순서**:
1. CWD에서 프로젝트명 식별:
   - `.project-sync.yaml` 존재 시: `project_name` 필드
   - 없으면: CWD 디렉토리명
2. 스냅샷 파일 Read:
   ```
   Read: .omc/daily-state/<project>/knowledge/snapshots/latest.json
   ```
3. 존재하면 -> 작업 컨텍스트에 주입 (프로젝트 현황, 핵심 entity, 최근 이벤트)
4. 존재하지 않으면 -> 건너뜀 (daily 미실행 프로젝트)

**토큰 예산**: ~1300t (Tier 2 Operational Context 2000t 슬롯 내)

**주입 형식**:
[프로젝트 지식 컨텍스트] ---------------------
프로젝트: {project_phase}
핵심 토픽: {active_topics}
주의 entity: {key_entities 요약}
최근 이벤트: {recent_events_digest}
활성 패턴: {active_patterns}
----------------------------------------------
```

### 6.4 토큰 예산 재배분

| Tier | 기존 (daily Phase 1) | 변경 (Cross-Session) | 비고 |
|------|:-------------------:|:-------------------:|------|
| Tier 1: Identity | 500t | 500t | 변경 없음 (CLAUDE.md + .project-sync.yaml) |
| Tier 2: Operational | 2000t (daily-state.learned_context) | 1300t (latest.json) + 700t 여유 | 소스 변경, 한글 안전 마진 확보 |
| Tier 3: Deep | 3000t (docs/) | 3000t (docs/) | 변경 없음 |
| **합계** | **5500t** | **4800t + 700t 여유** | 예산 이내 |

---

## 7. Growth/Eviction 정책 설계

### 7.1 Entity 퇴거 정책

| 조건 | 임계값 | 동작 |
|------|:------:|------|
| Entity 수 | 200개 | LRU(last_seen 기준) 퇴거 |
| Entity 상태 이력 | 20개/entity | 오래된 이력 병합 (범위 요약으로 교체) |
| 90일 미참조 entity | last_seen > 90일 | 자동 퇴거 (events에는 유지) |

**퇴거 시 처리**:
1. Entity를 entities.json에서 제거
2. relationships.json에서 해당 entity 관련 관계 삭제
3. events JSONL에서는 entity_id를 유지 (이벤트는 불변)
4. index.json의 by_entity에서 해당 항목 제거

### 7.2 Pattern 퇴거 정책

| 조건 | 임계값 | 동작 |
|------|:------:|------|
| Pattern 수 | 100개 | 가장 오래된 것 삭제 |
| 60일 미확인 pattern | last_confirmed > 60일 | 자동 삭제 |
| 중복 패턴 | similarity > 0.8 (Section 4.4.3 공식) | 병합 (최신 유지) |

**patterns.json 스키마 (M10 반영: action_feedback, false_positives 포함)**:

```json
{
  "version": "1.0",
  "updated_at": "2026-02-13T09:00:00Z",
  "patterns": [
    {
      "id": "pat_001",
      "description": "Brightcove: 매주 수요일 follow-up 메일 발송",
      "type": "recurring",
      "entities": ["ent_brightcove"],
      "confidence": 0.85,
      "occurrences": 4,
      "first_seen": "2026-01-22T09:00:00Z",
      "last_confirmed": "2026-02-12T09:00:00Z",
      "source_events": ["evt_20260122_005", "evt_20260129_003", "evt_20260205_002", "evt_20260212_001"]
    }
  ],
  "action_feedback": [
    {
      "type": "email_tone_correction",
      "original": "Dear Kim, Thank you...",
      "correction": "김 담당님, 검토 감사합니다...",
      "pattern": "한국 업체에는 한글 존칭 사용",
      "created_at": "2026-02-10T09:00:00Z"
    }
  ],
  "false_positives": [
    {
      "entity_name": "Amazon",
      "reason": "AWS 서비스 사용 중이지만 vendor 관계 아님",
      "suppressed_since": "2026-02-05T09:00:00Z"
    }
  ],
  "meta": {
    "total_patterns": 1,
    "max_patterns": 100,
    "types": ["recurring", "correlation", "escalation", "seasonal"],
    "total_feedback": 1,
    "total_false_positives": 1
  }
}
```

### 7.3 Event Log 퇴거 정책

| 조건 | 임계값 | 동작 |
|------|:------:|------|
| 월별 파일 보존 | 6개월 | 6개월 초과 JSONL 삭제 |
| 월별 파일 크기 | 500KB | 초과 시 low-priority 이벤트 삭제 |
| 삭제 전 | 항상 | 요약 생성 후 삭제 (summary JSONL 1줄 보존) |

**퇴거 프로세스 (Phase 8C에서 실행)**:

```
Phase 8C Eviction Check:

1. events/ 디렉토리 스캔
2. 6개월 초과 JSONL 파일 식별
3. 각 파일에 대해:
   a. 이벤트 요약 생성 (월간 요약 1줄)
   b. 요약을 현재 월 JSONL에 summary 이벤트로 추가
   c. 원본 JSONL 삭제
4. index.json 갱신 (삭제된 월 제거)
5. entities.json 90일 미참조 entity 퇴거
6. patterns.json 60일 미확인 pattern 삭제
```

### 7.4 state.json 캐시 퇴거

| 조건 | 임계값 | 동작 |
|------|:------:|------|
| 캐시 항목 수 | 500개 | LRU 퇴거 |
| 캐시 항목 나이 | 90일 | 자동 삭제 |
| state.json 전체 크기 | 100KB | 캐시 50% 삭제 (가장 오래된 것부터) |

---

## 8. 기존 Pipeline 통합점

### 8.1 Phase 1 변경 (Expert Context Loading)

**기존**: Tier 2에서 `state.json`의 `learned_context` 섹션을 직접 읽음
**변경**: Tier 2에서 `knowledge/snapshots/latest.json`을 읽음

```
# 변경 Phase 1 Tier 2
Read: .omc/daily-state/<project>/knowledge/snapshots/latest.json
-> key_entities, active_patterns, recent_events_digest 추출
-> expert_context.key_entities에 주입
-> expert_context.recent_decisions에 주입
```

### 8.2 Phase 4 변경 (AI Cross-Source Analysis)

Phase 4 분석 시 Snapshot의 `recent_events_digest`를 참조합니다 (JSONL 검색은 하지 않음).

**추가**: 분석 프롬프트에 snapshot의 이전 이벤트 다이제스트 주입

```
# Phase 4 프롬프트 추가 섹션
## 이전 이벤트 기록 (Snapshot에서)
{snapshot.recent_events_digest}

이전 이벤트와 오늘 수집된 데이터의 연결점을 찾으세요:
- 이전에 발송한 메일에 대한 응답이 왔는가?
- 이전 Slack 논의가 GitHub PR로 이어졌는가?
- entity 상태가 변경되었는가?
```

**토큰 비용**: snapshot digest만 사용하므로 ~200t 추가.

### 8.3 Phase 8 변경 (State Update)

Phase 8을 3개 서브페이즈로 확장합니다. **기존 Phase A, B를 보존**하고 Phase C를 추가합니다.

**SKILL.md 줄 수 관리 (C2 해결)**: Phase 8B/8C의 상세 로직은 본 Plan 문서(Section 4.4, 6.2.2, 7.3)를 참조하도록 하고, daily/SKILL.md에는 각 서브페이즈의 요약(5줄 이내)과 참조 링크만 기록합니다. 이를 통해 SKILL.md의 Phase 8 추가분을 **30줄 이내**로 제한합니다.

```
Phase 8A: Cursor Update (기존 - 변경 없음)
  state.json 커서 갱신 (gmail, slack, github)

Phase 8B: Knowledge Update (기존 Phase B 확장)
  1. Entity 추출 프롬프트 실행 (본 Plan Section 4.4.1 참조)
     -> entities.json 갱신 (이력 보존, LRU 퇴거, confidence >= 0.5만)
     -> relationships.json 갱신
  2. Pattern 추출 및 갱신
     -> patterns.json 갱신 (중복 병합, 확인 갱신)
  3. Event 기록
     -> events/YYYY-MM.jsonl에 오늘 이벤트 append
     -> events/index.json 갱신
  4. 캐시 갱신
     -> state.json의 cache.attachments 갱신

Phase 8C: Snapshot & Eviction (신규)
  1. Knowledge Snapshot 생성 (본 Plan Section 6.2.2 참조)
     -> snapshots/latest.json 생성 (5KB, ~1300t)
     -> snapshots/YYYY-MM-DD.json 생성
  2. Eviction 실행 (본 Plan Section 7.3 참조)
  3. Notepad Wisdom 연동 (본 Plan Section 9 참조)
```

### 8.4 daily/SKILL.md 줄 수 관리 전략 (C2 상세)

**현황**: daily/SKILL.md 현재 434줄

**전략**: Phase 8 확장 내용을 SKILL.md에 직접 기술하지 않고, 참조 패턴을 사용합니다.

```markdown
## Phase 8: State Update & Knowledge Layer

### 8A: Cursor Update (기존)
[기존 로직 유지 - 변경 없음]

### 8B: Knowledge Update
Entity/Pattern/Event 갱신. 상세 알고리즘은
`.omc/plans/knowledge-layer.md` Section 4.4, 5.1 참조.

요약: Entity 추출 프롬프트 -> entities.json 갱신 -> events JSONL append -> index 갱신

### 8C: Snapshot & Eviction
Knowledge Snapshot 생성 + 퇴거 실행. 상세 알고리즘은
`.omc/plans/knowledge-layer.md` Section 6.2.2, 7.3 참조.

요약: entities/events/patterns -> latest.json 압축 (5KB) -> 퇴거 체크
```

**예상 추가 줄 수**: ~25줄 (기존 Phase 8의 2줄 로직을 교체)
**예상 최종 줄 수**: 434 - 2 + 25 = **~457줄** (500줄 이내 목표 달성)
**500줄 이내 유지**: 추후 Phase 8 외 영역 리팩토링 시 추가 축소 가능

### 8.5 새로운 Phase 필요 여부

**결론: 새 Phase 불필요. 기존 Phase 확장으로 충분합니다.**

| Phase | 변경 유형 | 변경 내용 |
|:-----:|:---------:|----------|
| Phase 1 | Tier 2 소스 변경 | learned_context -> snapshots/latest.json |
| Phase 4 | 프롬프트 보강 | snapshot의 이전 이벤트 다이제스트 주입 |
| Phase 8 | 서브페이즈 추가 | 8A(기존) + 8B(확장) + 8C(신규) |

9-Phase Pipeline 구조는 완전히 보존됩니다.

---

## 9. Notepad Wisdom 연동 (GAP-5)

### 9.1 연동 방향

daily의 학습 결과 중 범용적인 것을 `.omc/notepads/{project}/`에도 기록합니다.

### 9.2 연동 포인트

| daily 산출물 | Notepad 대상 | 연동 방법 |
|-------------|-------------|----------|
| Entity 상태 변경 (vendor status 등) | `decisions.md` | 중요한 상태 전이 시 자동 기록 |
| 반복 패턴 발견 | `learnings.md` | 새 패턴 발견 시 자동 기록 |
| 미해결 이슈 | `issues.md` | URGENT 액션 아이템 중 미처리 항목 |
| 분석 중 발견한 문제 | `problems.md` | 크로스 소스 불일치 등 |

### 9.3 "중요한 상태 전이" 기준 (M8 해결)

Notepad `decisions.md`에 기록하는 "중요한 상태 전이"의 구체적 기준:

| Entity 타입 | 기록 대상 (status 변경) | 기록 제외 (attribute 변경) |
|------------|----------------------|------------------------|
| `vendor` | evaluating->negotiating, negotiating->contracted, *->rejected | contact 변경, quote 금액 갱신 |
| `person` | role 변경 (contributor->decision-maker 등) | email 변경, organization 변경 |
| `product` | phase 변경 (evaluating->selected, deploying->active 등) | version 갱신 |
| `project` | phase 변경 (planning->active, active->completed 등) | deadline 변경 |
| `organization` | relationship 변경 (vendor->partner 등) | contact 변경 |
| `topic` | status 변경 (active->resolved, resolved->recurring) | 세부 내용 갱신 |

**핵심 원칙**: `current_state.status` (또는 `role`/`phase`/`relationship`) 필드의 변경만 Notepad에 기록합니다. `attributes` 딕셔너리의 변경은 entities.json에만 기록하고 Notepad에는 기록하지 않습니다.

### 9.4 Phase 8C에서의 Notepad 기록

```
Phase 8C 마지막 단계:

Notepad Sync (조건부 - 중요 변경 있을 때만):
  1. 오늘 entity status/role/phase 변경 -> decisions.md에 append
     형식: "- [YYYY-MM-DD] {entity_name}: {old_status} -> {new_status} ({trigger})"
  2. 오늘 발견된 새 패턴 -> learnings.md에 append
     형식: "- [YYYY-MM-DD] {pattern_description} (confidence: {value})"
  3. URGENT 미처리 액션 -> issues.md에 append
     형식: "- [YYYY-MM-DD] [URGENT] {action_description}"

Notepad 위치: .omc/notepads/<project>/
  - 없으면 초기화 (learnings.md, decisions.md, issues.md, problems.md 생성)
```

### 9.5 `<remember>` 태그 연동

**공존**: `<remember>` 태그는 그대로 유지합니다. Knowledge Layer는 daily 실행 기반 자동 축적이고, `<remember>`는 세션 내 수동 기록입니다. 서로 다른 용도이므로 교체하지 않습니다.

---

## 10. state.json 스키마 (daily-redesign.plan.md 직접 수정)

### 10.1 마이그레이션 불필요 선언

daily v3.0이 아직 구현되지 않았으므로 (`.omc/daily-state/` 디렉토리 미존재), v1.0->v2.0 마이그레이션 알고리즘은 불필요합니다.

**대신**: daily-redesign.plan.md Section 3.3.1의 state.json 스키마를 직접 수정하여 처음부터 Knowledge Layer 기반으로 정의합니다.

### 10.2 state.json 스키마 (Knowledge Layer 통합)

```json
{
  "version": "2.0",
  "project": "wsoptv_ott",
  "last_run": "2026-02-12T09:00:00Z",
  "run_count": 5,
  "cursors": {
    "gmail": {
      "history_id": "12345678",
      "last_message_id": "msg_abc123",
      "last_timestamp": "2026-02-11T18:00:00Z"
    },
    "slack": {
      "last_ts": "1707699600.000000",
      "last_timestamp": "2026-02-11T18:00:00Z"
    },
    "github": {
      "last_check": "2026-02-11T18:00:00Z",
      "last_commit_sha": "abc1234"
    }
  },
  "cache": {
    "attachments": {}
  },
  "knowledge_version": "1.0",
  "knowledge_path": "knowledge/"
}
```

**변경점 대비 daily-redesign.plan.md Section 3.3.1:**
- `learned_context` 필드 제거 (Knowledge Layer가 대체)
- `knowledge_version`, `knowledge_path` 필드 추가
- `version`을 `"2.0"`으로 설정
- `action_feedback`, `false_positives`는 `knowledge/patterns.json`에 포함

---

## 11. 예상 영향 파일

### 11.1 신규 생성

| 파일 | 역할 |
|------|------|
| `.omc/daily-state/<project>/knowledge/entities.json` | Entity 레지스트리 |
| `.omc/daily-state/<project>/knowledge/relationships.json` | 관계 그래프 |
| `.omc/daily-state/<project>/knowledge/patterns.json` | 학습 패턴 + 피드백 |
| `.omc/daily-state/<project>/knowledge/events/YYYY-MM.jsonl` | 월별 이벤트 로그 |
| `.omc/daily-state/<project>/knowledge/events/index.json` | 이벤트 인덱스 |
| `.omc/daily-state/<project>/knowledge/snapshots/latest.json` | 크로스 세션 스냅샷 |
| `.omc/daily-state/<project>/knowledge/snapshots/YYYY-MM-DD.json` | 일별 스냅샷 |

### 11.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\skills\daily\SKILL.md` | Phase 1 Tier 2 소스 변경, Phase 4 프롬프트 보강, Phase 8 서브페이즈 추가 (8B 확장, 8C 신규). 상세 로직은 본 Plan 참조 패턴으로 ~25줄 추가. |
| `C:\claude\.claude\skills\auto\SKILL.md` | Step 0.0 Knowledge Context Loading 추가 (~15줄). `--daily` 세션에서는 도달하지 않으므로 조건 분기 불필요. |
| `C:\claude\docs\01-plan\daily-redesign.plan.md` | Section 3.3.1: state.json 스키마를 v2.0으로 갱신 (learned_context -> knowledge_path). Section 5.1: knowledge/ 디렉토리 추가. 파일 경로를 `<project>.json` -> `<project>/state.json`으로 변경. **Version을 v2.3.0으로 갱신.** |

### 11.3 활용 (수정 없음)

| 파일 | 활용 방식 |
|------|----------|
| `C:\claude\docs\02-design\daily-redesign.design.md` | Design 참조 |
| `.omc/notepads/{project}/*` | Notepad Wisdom 시스템 연동 대상 |

---

## 12. 구현 순서 (Task Flow)

### 12.1 Task 종속성 그래프

```
Task 1: daily-redesign.plan.md v2.3.0 갱신 + Knowledge 스키마 정의
  - 에이전트: executor (sonnet)
  - 대상 파일: daily-redesign.plan.md
  - 독립

Task 2: Entity 추출/갱신 로직 (Phase 8B)
  - 에이전트: executor-high (opus)
  - 대상 파일: daily/SKILL.md (Phase 8B 섹션)
  - blockedBy: Task 1

Task 3: Event Log 기록/인덱싱 로직 (Phase 8B)
  - 에이전트: executor (sonnet)
  - 대상 파일: daily/SKILL.md (Phase 8B 섹션)
  - blockedBy: Task 1

Task 4: Snapshot 생성 로직 (Phase 8C)
  - 에이전트: executor (sonnet)
  - 대상 파일: daily/SKILL.md (Phase 8C 섹션)
  - blockedBy: Task 2, Task 3

Task 5: Eviction 로직 (Phase 8C)
  - 에이전트: executor (sonnet)
  - 대상 파일: daily/SKILL.md (Phase 8C 섹션)
  - blockedBy: Task 1

Task 6: daily/SKILL.md Phase 1, 4 수정
  - 에이전트: executor-high (opus)
  - 대상 파일: daily/SKILL.md (Phase 1, Phase 4 섹션)
  - blockedBy: Task 4, Task 5

Task 7: auto/SKILL.md Step 0.0 추가
  - 에이전트: executor (sonnet)
  - 대상 파일: auto/SKILL.md
  - blockedBy: Task 4

Task 8: Notepad Wisdom 연동
  - 에이전트: executor-low (haiku)
  - 대상 파일: daily/SKILL.md (Phase 8C Notepad 섹션)
  - blockedBy: Task 6

Task 9: 통합 검증
  - 에이전트: architect (opus)
  - blockedBy: Task 6, Task 7, Task 8
```

### 12.2 실행 순서 (Wave 분할) (M9 반영: 파일 충돌 해소)

```
Wave 1 (단독):   Task 1 (daily-redesign.plan.md 갱신)
Wave 2 (병렬):   Task 2, Task 3, Task 5
                  - Task 2, 3, 5는 daily/SKILL.md의 서로 다른 섹션을 수정하지만
                    동시 편집 위험이 있으므로 순차 실행 권장
                  - 대안: Task 2, 5만 병렬 (다른 섹션), Task 3은 Wave 3으로 이동
Wave 3 (병렬):   Task 4 (+ Task 3 if moved)
Wave 4 (병렬):   Task 6, Task 7 (다른 파일이므로 안전)
Wave 5 (단독):   Task 8
Wave 6:          Task 9 (검증)
```

**파일 충돌 분석 (M9 상세):**

| Task | 수정 파일 | 수정 섹션 | 충돌 위험 |
|:----:|----------|----------|:--------:|
| 2 | daily/SKILL.md | Phase 8B (entity) | Task 3과 충돌 가능 |
| 3 | daily/SKILL.md | Phase 8B (event) | Task 2와 충돌 가능 |
| 5 | daily/SKILL.md | Phase 8C (eviction) | 독립 섹션, 안전 |
| 6 | daily/SKILL.md | Phase 1, Phase 4 | Task 2,3,5와 다른 섹션 |
| 7 | auto/SKILL.md | Step 0.0 | 다른 파일, 안전 |
| 8 | daily/SKILL.md | Phase 8C (notepad) | Task 5와 같은 섹션 근처 |

**권장 실행 순서**: Task 2 -> Task 3 -> Task 5 순차 (같은 SKILL.md Phase 8 영역)

### 12.3 Detailed TODOs

#### Task 1: daily-redesign.plan.md 갱신 + 스키마 정의

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 1.1 | daily-redesign.plan.md Section 3.3.1 state.json 스키마를 v2.0으로 갱신 | `learned_context` -> `knowledge_path` 교체, version "2.0" |
| 1.2 | Section 5.1에 knowledge/ 디렉토리 추가 | 7개 파일 목록 추가 |
| 1.3 | 파일 경로를 `<project>.json` -> `<project>/state.json`으로 변경 | Section 3.3.1, 3.3.2의 경로 일관성 |
| 1.4 | daily-redesign.plan.md Version을 2.3.0으로 갱신 | 변경 이력에 Knowledge Layer 통합 기록 |
| 1.5 | Knowledge Layer 스키마를 Plan 문서에 참조로 명시 | "상세 스키마는 `.omc/plans/knowledge-layer.md` 참조" 추가 |

#### Task 2: Entity 추출/갱신 로직

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 2.1 | Entity 추출 프롬프트를 daily/SKILL.md Phase 8B에 참조 링크로 추가 | Section 4.4.1 참조, 입력/출력 JSON 형식 명시 |
| 2.2 | Entity lookup (ID/alias 검색) 로직 문서화 | alias 매칭으로 중복 entity 방지 |
| 2.3 | Entity 상태 변경 감지 + state_history 기록 로직 | confidence >= 0.5인 변경만 기록 |
| 2.4 | Relationship 갱신 로직 | 새 관계 추가, 기존 관계 last_confirmed 갱신 |
| 2.5 | LRU 퇴거 로직 (200 entity 초과 시) | last_seen 기준 가장 오래된 entity 제거, 관계 연쇄 삭제 |

#### Task 3: Event Log 기록/인덱싱

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 3.1 | 이벤트 생성 로직 (Phase 4 분석 결과 -> JSONL 행) | Section 5.2 스키마 준수, entity/topic 태깅 |
| 3.2 | JSONL append 로직 | 월별 파일 자동 생성, append-only |
| 3.3 | index.json 갱신 로직 | by_entity, by_topic, by_month 모두 갱신 |
| 3.4 | Event 검색 프롬프트 (Claude Read + Grep 패턴) | ad-hoc 검색 유형 3가지 지원 |

#### Task 4: Snapshot 생성

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 4.1 | Snapshot 생성 알고리즘 (Section 6.2.2) | entities + events + patterns -> 5KB, ~1300t |
| 4.2 | Entity별 80t 제한 + 한글 토큰 검증 | 10 entities * 80t = 800t 이내 |
| 4.3 | latest.json 생성 로직 | 매 daily 실행 시 최신 snapshot 교체 |
| 4.4 | 일별 snapshot 생성 및 7일 보존 로직 | YYYY-MM-DD.json 생성, 7일 초과 삭제 |
| 4.5 | 토큰 초과 시 축소 로직 | key_entities 8개, events_digest 7줄로 자동 축소 |

#### Task 5: Eviction 로직

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 5.1 | 6개월 초과 이벤트 요약+삭제 로직 | 요약 이벤트 1줄 보존 후 원본 삭제 |
| 5.2 | 90일 미참조 entity 퇴거 로직 | entity + relationship 연쇄 삭제 |
| 5.3 | 60일 미확인 pattern 삭제 로직 | last_confirmed 기준 |
| 5.4 | 중복 pattern 병합 (similarity > 0.8) | Section 4.4.3 키워드 겹침 공식 사용 |
| 5.5 | 캐시 90일/500개 퇴거 로직 | state.json cache.attachments 정리 |

#### Task 6: daily/SKILL.md Phase 1, 4 수정

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 6.1 | Phase 1 Tier 2 소스를 snapshots/latest.json으로 변경 | Tier 2 Operational Context가 snapshot에서 로드 |
| 6.2 | Phase 4 프롬프트에 snapshot의 이전 이벤트 다이제스트 주입 | JSONL 검색 없이 snapshot.recent_events_digest만 사용 |
| 6.3 | SKILL.md 전체 줄 수가 500줄 이내인지 검증 | `wc -l` 결과 <= 500 |

#### Task 7: auto/SKILL.md 수정

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 7.1 | Step 0.0 Knowledge Context Loading 섹션 추가 (~15줄) | Section 6.3 내용 반영 |
| 7.2 | 프로젝트명 식별 로직 (.project-sync.yaml 또는 CWD) | 프로젝트명으로 올바른 knowledge 경로 해석 |
| 7.3 | `--daily` 분기 설명 (Step 0.0은 항상 실행, `--daily`는 auto Phase 0 도달 안 함) | 조건문 불필요함을 명시 |

#### Task 8: Notepad Wisdom 연동

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 8.1 | Phase 8C에서 Notepad 초기화 로직 | `.omc/notepads/<project>/` 4개 파일 자동 생성 |
| 8.2 | Entity status/role/phase 변경 -> decisions.md 자동 기록 | Section 9.3 기준표에 따라 status 변경만 필터링 |
| 8.3 | 새 패턴 -> learnings.md 자동 기록 | 새 패턴 발견 시 append |
| 8.4 | URGENT 미처리 -> issues.md 기록 | 미처리 URGENT 액션만 |
| 8.5 | 중복 방지 (마지막 5줄 비교) | 동일 entity+status 조합 이미 기록되어 있으면 skip |

#### Task 9: 통합 검증

| # | TODO | 수용 기준 |
|:-:|------|----------|
| 9.1 | daily/SKILL.md 변경이 9-Phase Pipeline 구조를 파괴하지 않음 | Phase 0~8 순차 흐름 유지 |
| 9.2 | auto/SKILL.md 변경이 인과관계 그래프를 파괴하지 않음 | 08-skill-routing.md 인과관계 보존 |
| 9.3 | Cross-Session Bridge가 토큰 예산 5500t 이내 | latest.json이 ~1300t, Tier 2 2000t 이내 |
| 9.4 | Eviction이 데이터 무결성 유지 | Entity 삭제 시 관계도 연쇄 정리 |
| 9.5 | daily/SKILL.md가 500줄 이내 | `wc -l` <= 500 |
| 9.6 | daily-redesign.plan.md v2.3.0이 일관성 있음 | Knowledge Layer 경로와 state.json 스키마 일치 |

---

## 13. 커밋 전략

| 순서 | 커밋 메시지 | 포함 Task |
|:----:|-----------|:---------:|
| 1 | `feat(daily): daily-redesign.plan.md v2.3.0 - Knowledge Layer 디렉토리 구조 통합` | Task 1 |
| 2 | `feat(daily): Entity 추출/갱신 로직 - Phase 8B 확장 (confidence 기반)` | Task 2 |
| 3 | `feat(daily): Event Log JSONL 기록 및 인덱싱 시스템` | Task 3 |
| 4 | `feat(daily): Eviction 정책 - entity/pattern/event 퇴거 로직` | Task 5 |
| 5 | `feat(daily): Knowledge Snapshot 생성 - Cross-Session Bridge (5KB/1300t)` | Task 4 |
| 6 | `feat(daily): daily/SKILL.md Phase 1/4 Knowledge Layer 통합` | Task 6 |
| 7 | `feat(auto): Step 0.0 Knowledge Context Loading 추가` | Task 7 |
| 8 | `feat(daily): Notepad Wisdom 연동 - status 변경 자동 기록` | Task 8 |

---

## 위험 요소

| # | 위험 | 영향 | 완화 |
|:-:|------|------|------|
| 1 | Entity 추출 품질이 낮으면 잘못된 지식 축적 | 잘못된 상태 이력 | confidence 공식(Section 4.4.2)으로 품질 추적, confidence < 0.5 entity 생성 차단, < 0.7 snapshot 제외 |
| 2 | SKILL.md가 500줄 초과 | daily/SKILL.md 읽기 시 토큰 과다 | Phase 8 상세 로직은 Plan 문서 참조, SKILL.md에는 요약+참조만 (~25줄 추가) |
| 3 | Knowledge Layer 파일 I/O가 daily 실행 시간 증가 | 사용자 대기 시간 증가 | Phase 8C는 분석/출력 이후 실행 (사용자는 결과를 먼저 봄) |
| 4 | auto/SKILL.md 변경이 기존 워크플로우 파괴 | /auto 전체 기능 영향 | Step 0.0은 "존재하면 로드, 없으면 건너뜀" 방어적 구현. `--daily`는 Phase 0 도달 안 함 |
| 5 | 한글 JSON이 토큰 예산 초과 | Cross-Session Bridge 실패 | 5KB 제한 + entity별 80t + 초과 시 자동 축소 |
| 6 | 월별 JSONL이 대량이면 Grep 검색 느림 | 이벤트 검색 지연 | daily Phase 내에서는 JSONL 검색 안 함, ad-hoc만. index.json 사전 필터 |
| 7 | Notepad 파일 중복 기록 | 노이즈 증가 | 마지막 5줄 비교하여 중복 방지 |
| 8 | daily-redesign.plan.md v2.3.0 갱신이 기존 Plan 일관성 파괴 | 다른 구현 작업 혼란 | Knowledge Layer 변경 섹션만 수정, 나머지 섹션 무변경 |

---

## 14. 성공 기준

| # | 기준 | 측정 방법 | 목표 |
|:-:|------|----------|:----:|
| 1 | Entity 이력 추적 | entity의 state_history에 최소 1건 이상 이력 | 100% |
| 2 | Event Log 기록 | daily 1회 실행 후 JSONL에 이벤트 기록됨 | 100% |
| 3 | Cross-Session 지식 로드 | /auto 세션에서 latest.json이 로드됨 | 100% |
| 4 | 토큰 예산 준수 | latest.json이 ~1300t, 한글 프로젝트 포함 2000t 미만 | 100% |
| 5 | Eviction 동작 | 200 entity 초과 시 LRU 퇴거 실행 | 100% |
| 6 | 9-Phase Pipeline 보존 | Phase 0~8 순차 실행 변경 없음 | 100% |
| 7 | 인과관계 그래프 보존 | 08-skill-routing.md 무변경 | 100% |
| 8 | daily/SKILL.md 줄 수 | 500줄 이내 | 100% |
| 9 | 비전 달성율 | daily Knowledge Layer 완성도 | 80%+ |

---

## 15. 아키텍처 제약 조건 확인

| 제약 | 준수 | 방법 |
|------|:----:|------|
| 9-Phase Pipeline 보존 | OK | Phase 추가 없음, 기존 Phase 확장만 |
| 인과관계 그래프 보존 | OK | auto/SKILL.md는 Step 0.0 추가만, 기존 Phase 0~4 구조 무변경 |
| Global-Only Policy | OK | 스킬은 `C:\claude\.claude\skills\`에만, Knowledge는 `.omc/` |
| JSON/JSONL 파일 기반 | OK | DB 미사용 |
| 토큰 예산 5500t | OK | Tier 2를 snapshot(~1300t)으로 교체, 한글 안전 마진 700t |
| Windows 환경 | OK | 절대 경로 `C:\claude\` 사용 |
| 절대 경로만 사용 | OK | 모든 경로 절대 경로 |
| SKILL.md 줄 수 | OK | Phase 8 상세는 Plan 참조, SKILL.md ~457줄 (500줄 이내) |

---

## 16. daily-redesign.plan.md와의 관계 매핑

**Relationship 선언**: 본 Plan은 daily-redesign.plan.md (v2.2.1)를 **확장 및 부분 Supersede**합니다.

| daily-redesign.plan.md 섹션 | Knowledge Layer 영향 | 변경 유형 | 상세 |
|----------------------------|---------------------|:--------:|------|
| Section 3.3 Incremental State | 파일 경로를 directory 구조로 변경 | **Supersede** | `<project>.json` -> `<project>/state.json` |
| Section 3.3.1 상태 파일 스키마 | learned_context 제거, knowledge_path 추가 | **Supersede** | state.json v2.0 스키마로 교체 |
| Section 3.4 Expert Context Loading | Tier 2 소스를 snapshot으로 변경 | **Supersede** | learned_context -> snapshots/latest.json |
| Section 3.6 Action Recommendation | action_feedback -> patterns.json 이전 | **이전** | patterns.json에 action_feedback 필드 포함 |
| Section 5.1 신규 생성 | knowledge/ 디렉토리 추가 | **확장** | 7개 파일 추가 |
| 나머지 모든 섹션 | 변경 없음 | **보존** | Phase 0~7, 9-Phase 구조 완전 보존 |

**구체적 조치**: Task 1에서 daily-redesign.plan.md를 v2.3.0으로 갱신하며, Supersede 대상 섹션을 직접 수정합니다. 이는 daily v3.0이 아직 구현되지 않았기 때문에 가능합니다. daily-redesign.plan.md의 변경 이력에 "v2.3.0: Knowledge Layer 통합 (knowledge-layer.md Plan 반영)"을 추가합니다.

---

## 17. Critic 피드백 반영 추적 (v1.0.0 -> v1.1.0)

| # | 이슈 | 심각도 | 해결 | 반영 위치 |
|:-:|------|:------:|:----:|----------|
| C1 | "보완" 관계 자기모순 | CRITICAL | 해결 | Section 9 line `Relationship` 변경, Section 17 Supersede 명시 |
| C2 | SKILL.md 300줄 이내 유지 불가 | CRITICAL | 해결 | Section 8.4 참조 패턴 전략, 500줄 이내 목표로 현실화 |
| C3 | flat file -> directory 마이그레이션 부재 | CRITICAL | 해결 | Section 3.1 "마이그레이션 불필요" 선언, 처음부터 directory |
| C4 | Entity 추출 품질 대비 불충분 | CRITICAL | 해결 | Section 4.4 전체 (프롬프트, confidence 공식, similarity 계산) |
| H5 | Cross-Session Bridge 한글 토큰 | HIGH | 해결 | Section 3.2 한글 환산 테이블, 8KB->5KB 하향, entity별 80t |
| H6 | JSONL 검색 시점/비용 미분석 | HIGH | 해결 | Section 5.4 사용 시점 분리 테이블, daily 내 JSONL 검색 금지 |
| H7 | auto/SKILL.md Step 0.0 실행 조건 | HIGH | 해결 | Section 6.3 `--daily`는 Phase 0 도달 안 함 설명 |
| M8 | Notepad "중요한 상태 전이" 기준 | MINOR | 해결 | Section 9.3 entity type별 기록 대상/제외 테이블 |
| M9 | Wave 2 파일 충돌 | MINOR | 해결 | Section 12.2 파일 충돌 분석 테이블, 순차 실행 권장 |
| M10 | patterns.json 누락 필드 | MINOR | 해결 | Section 7.2 patterns.json에 action_feedback, false_positives 추가 |

---

## 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0.0 | 2026-02-13 | 초기 Plan 작성 - 5개 GAP 해결, 6개 핵심 질문 답변 |
| 1.1.0 | 2026-02-13 | Critic REJECT 피드백 반영 (C1-C4 CRITICAL 4건, H5-H7 HIGH 3건, M8-M10 MINOR 3건). Relationship "보완" -> "확장 및 부분 Supersede". Snapshot 8KB->5KB. Entity 추출 프롬프트/confidence/similarity 공식 추가. SKILL.md 참조 패턴 전략. 마이그레이션 불필요 선언. JSONL 검색 시점 분리. Wave 파일 충돌 해소. patterns.json 필드 추가. Notepad 기록 기준 구체화. Task 8 제거 (마이그레이션 -> Task 1 흡수). daily-redesign.plan.md v2.3.0 갱신 Task 추가. |
