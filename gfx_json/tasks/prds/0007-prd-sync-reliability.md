# PRD-0007: GFX JSON → Supabase 동기화 신뢰성 개선

**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-01-19
**Issue**: [#7](https://github.com/garimto81/gfx_json/issues/7)

---

## 1. 개요

### 1.1 배경

GFX Sync Agent가 NAS의 JSON 파일을 Supabase로 동기화하는 과정에서 **데이터 불일치**가 발생하고 있습니다. 분석 결과, 다음 핵심 문제들이 식별되었습니다:

- 멀티 PC 환경에서 같은 session_id 충돌 시 데이터 덮어쓰기
- 네트워크 장애 시 OfflineQueue 데이터 영구 손실
- 배치 처리 중 메타데이터 손실로 추적 불가

### 1.2 목표

| 목표 | 측정 지표 | 현재 | 목표 |
|------|----------|------|------|
| 데이터 무결성 | 손실률 | 미측정 | 0% |
| 멀티 PC 지원 | 중복 처리 | 덮어쓰기 | 공존 |
| 장애 복구 | 복구율 | ~80% | 99.9% |

### 1.3 범위

**포함**:
- on_conflict 키 변경 (session_id → file_hash)
- gfx_pc_id DB 저장 기능
- 배치 처리 메타데이터 보존
- OfflineQueue 안전장치

**제외**:
- Dashboard UI 변경
- 성능 최적화 (별도 이슈)

---

## 2. 현재 상태 분석

### 2.1 아키텍처

```
NAS Storage → PollingWatcher → SyncService → Supabase
   (JSON)       (watchdog)        (httpx)      (PostgreSQL)
     │              │                │              │
     │              │                │              │
     └── PC01 ─────┼────────────────┼──────────────┤
     └── PC02 ─────┼────────────────┼──────────────┤  ← 충돌 발생 지점
     └── PC03 ─────┘                │              │
                                    │              │
                              BatchQueue      on_conflict=session_id
                                    │              │
                              OfflineQueue    └── 덮어쓰기 발생
                                    │
                              └── 자동 삭제 (10,000 초과)
```

### 2.2 문제점 상세

#### 2.2.1 CRITICAL: session_id 단일 키 충돌

**현재 코드** (`sync_service_v3.py:156`):
```python
await self.supabase.upsert(
    table=self.settings.supabase_table,
    records=[clean_record],
    on_conflict="session_id",  # 문제: 단일 키
)
```

**문제 시나리오**:
```
PC01: session_id=12345, file_hash=abc123 → 저장
PC02: session_id=12345, file_hash=def456 → PC01 데이터 덮어쓰기
```

#### 2.2.2 CRITICAL: OfflineQueue 자동 삭제

**현재 코드** (`offline_queue.py:176-181`):
```python
def _remove_oldest(self):
    # 큐 크기 초과 시 가장 오래된 항목 삭제
    if self._count() > self.max_size:
        logger.warning("Queue full, removing oldest item")
        # 복구 불가능한 삭제
```

**문제**: 로그만 남기고 영구 삭제 → 복구 불가

#### 2.2.3 HIGH: 배치 메타데이터 손실

**현재 코드** (`sync_service_v3.py:194-195`):
```python
for record in batch:
    file_path = record.pop("_file_path", "unknown")  # 원본 변경
    gfx_pc_id = record.pop("_gfx_pc_id", "UNKNOWN")  # 원본 변경
```

**문제**: `pop()` 사용으로 원본 dict 변경 → 재시도 시 메타데이터 없음

#### 2.2.4 HIGH: Dead Letter Queue 조기 이동

**현재 코드** (`offline_queue.py:286`):
```python
if current_retry >= self.max_retries - 1:  # max_retries=5 → 4회만 재시도
    self._move_to_dlq(record)
```

---

## 3. 요구사항

### 3.1 기능 요구사항

| ID | 요구사항 | 우선순위 | 관련 파일 |
|:--:|----------|:--------:|-----------|
| FR-01 | on_conflict를 file_hash로 변경 | P0 | `sync_service_v3.py` |
| FR-02 | gfx_pc_id를 DB 컬럼으로 저장 | P0 | `json_parser.py` |
| FR-03 | 배치 처리 시 pop() → get() 변경 | P1 | `sync_service_v3.py` |
| FR-04 | OfflineQueue 삭제 전 백업 | P1 | `offline_queue.py` |
| FR-05 | Dead Letter Queue 조건 수정 | P1 | `offline_queue.py` |
| FR-06 | 큐 상태 모니터링 API | P2 | 신규 |

### 3.2 비기능 요구사항

| ID | 요구사항 | 기준 |
|:--:|----------|------|
| NFR-01 | 데이터 손실률 | 0% |
| NFR-02 | 장애 복구 시간 | < 1분 |
| NFR-03 | 배치 처리 성능 | 500건/5초 유지 |

---

## 4. 설계

### 4.1 on_conflict 키 변경 (FR-01)

**변경 전**:
```python
on_conflict="session_id"
```

**변경 후**:
```python
on_conflict="file_hash"
```

**근거**:
- `file_hash`는 파일 내용 기반 SHA-256 → 파일마다 고유
- 같은 session_id라도 다른 PC에서 다른 내용이면 공존

**DB 스키마 변경 필요**:
```sql
-- file_hash에 UNIQUE 제약 추가
ALTER TABLE gfx_sessions
ADD CONSTRAINT gfx_sessions_file_hash_unique UNIQUE (file_hash);
```

### 4.2 gfx_pc_id DB 저장 (FR-02)

**변경 전** (`json_parser.py:221`):
```python
record = {
    ...
    "_gfx_pc_id": gfx_pc_id,  # 언더스코어 → DB 저장 안 됨
}
```

**변경 후**:
```python
record = {
    ...
    "gfx_pc_id": gfx_pc_id,  # DB 컬럼으로 저장
}
```

**DB 스키마 변경 필요**:
```sql
-- gfx_pc_id 컬럼 추가
ALTER TABLE gfx_sessions
ADD COLUMN gfx_pc_id VARCHAR(50);
```

### 4.3 배치 메타데이터 보존 (FR-03)

**변경 전**:
```python
file_path = record.pop("_file_path", "unknown")
```

**변경 후**:
```python
file_path = record.get("_file_path", "unknown")
```

### 4.4 OfflineQueue 안전장치 (FR-04)

**새 로직**:
```python
def _remove_oldest(self):
    if self._count() > self.max_size:
        oldest = self._get_oldest()

        # 1. 백업 파일로 저장
        backup_path = self.backup_dir / f"overflow_{datetime.now().isoformat()}.json"
        backup_path.write_text(json.dumps(oldest))

        # 2. 경고 로그 + 메트릭
        logger.warning(f"Queue overflow, backed up to {backup_path}")
        self.metrics.increment("queue_overflow_count")

        # 3. 삭제
        self._delete_oldest()
```

### 4.5 Dead Letter Queue 조건 수정 (FR-05)

**변경 전**:
```python
if current_retry >= self.max_retries - 1:
```

**변경 후**:
```python
if current_retry >= self.max_retries:
```

---

## 5. 데이터 흐름

### 5.1 개선된 동기화 흐름

```
JSON 파일 생성
    │
    ▼
┌─────────────────────────────────────────┐
│ JsonParser.parse()                       │
│   - session_id 추출                      │
│   - file_hash 생성 (SHA-256)             │
│   - gfx_pc_id 저장 (DB 컬럼)  ← NEW      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ SyncService.sync_file()                  │
│   - created → 단건 upsert                │
│   - modified → BatchQueue                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ SupabaseClient.upsert()                  │
│   - on_conflict="file_hash"  ← CHANGED  │
│   - 같은 파일만 업데이트                 │
│   - 다른 파일은 새 레코드                │
└─────────────────────────────────────────┘
    │
    ├── 성공 → 완료
    │
    └── 실패 → OfflineQueue
              │
              ├── 재시도 (max_retries=5)  ← FIXED
              │
              └── 실패 → DLQ
                        │
                        └── 백업 후 삭제  ← NEW
```

---

## 6. 테스트 계획

### 6.1 단위 테스트

| TC ID | 테스트 케이스 | 예상 결과 |
|:-----:|--------------|----------|
| UT-01 | 같은 session_id, 다른 file_hash | 두 레코드 공존 |
| UT-02 | 같은 file_hash 재동기화 | 업데이트 (덮어쓰기 아님) |
| UT-03 | 배치 실패 후 재시도 | 메타데이터 유지 |
| UT-04 | OfflineQueue 10,000 초과 | 백업 파일 생성 후 삭제 |
| UT-05 | 5회 재시도 실패 | DLQ 이동 (4회 아님) |

### 6.2 통합 테스트

| TC ID | 테스트 케이스 | 예상 결과 |
|:-----:|--------------|----------|
| IT-01 | 멀티 PC 동시 동기화 | 모든 데이터 저장 |
| IT-02 | 네트워크 장애 복구 | 100% 복구 |
| IT-03 | 대량 배치 (1000건) | 성능 저하 없음 |

---

## 7. 구현 계획

### 7.1 Phase 1: 핵심 수정 (Week 1)

| 작업 | 파일 | 담당 |
|------|------|------|
| on_conflict 변경 | `sync_service_v3.py` | - |
| gfx_pc_id 저장 | `json_parser.py` | - |
| DB 스키마 변경 | Supabase Migration | - |

### 7.2 Phase 2: 안정화 (Week 2)

| 작업 | 파일 | 담당 |
|------|------|------|
| 배치 메타데이터 수정 | `sync_service_v3.py` | - |
| DLQ 조건 수정 | `offline_queue.py` | - |
| 단위 테스트 작성 | `tests/` | - |

### 7.3 Phase 3: 모니터링 (Week 3)

| 작업 | 파일 | 담당 |
|------|------|------|
| OfflineQueue 백업 | `offline_queue.py` | - |
| 큐 상태 API | 신규 | - |
| Dashboard 연동 | `dashboard/` | - |

---

## 8. 체크리스트

### 8.1 구현 체크리스트

- [ ] Supabase 스키마 확인 (`supabase db dump`)
- [ ] file_hash UNIQUE 제약 추가
- [ ] gfx_pc_id 컬럼 추가
- [ ] on_conflict 변경 (session_id → file_hash)
- [ ] gfx_pc_id DB 저장 (`_gfx_pc_id` → `gfx_pc_id`)
- [ ] 배치 메타데이터 수정 (pop → get)
- [ ] DLQ 조건 수정 (>= max_retries)
- [ ] OfflineQueue 백업 메커니즘

### 8.2 테스트 체크리스트

- [ ] UT-01 ~ UT-05 통과
- [ ] IT-01 ~ IT-03 통과
- [ ] E2E 테스트 통과
- [ ] 성능 테스트 (500건/5초)

### 8.3 배포 체크리스트

- [ ] Supabase Migration 적용
- [ ] Docker 이미지 빌드
- [ ] NAS 배포
- [ ] 모니터링 확인

---

## 9. 리스크

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| DB 마이그레이션 실패 | 서비스 중단 | 백업 후 롤백 계획 |
| file_hash 충돌 | 데이터 손실 | SHA-256 사용 (충돌 확률 극히 낮음) |
| 기존 데이터 불일치 | 중복 레코드 | 마이그레이션 스크립트로 정리 |

---

## 10. 참고 자료

- [Issue #7](https://github.com/garimto81/gfx_json/issues/7)
- [Issue #4](https://github.com/garimto81/gfx_json/issues/4) - PascalCase 지원
- [Issue #6](https://github.com/garimto81/gfx_json/issues/6) - 필드 매핑 (Closed)
