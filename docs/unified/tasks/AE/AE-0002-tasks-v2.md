# Task List: PRD-0001 v2.0 (Phase 5-8)

**PRD**: [0001-prd-ae-automation.md](prds/0001-prd-ae-automation.md)
**Version**: 2.0.0
**Created**: 2025-12-25
**Updated**: 2025-12-26
**Status**: Phase 5-6 Complete, Phase 7 In Progress (93%), Phase 8 Pending

---

## 개요

After Effects 자동화 시스템 v2.0 기능 구현을 위한 작업 목록입니다.
Phase 1-4는 완료 상태이며, 이 문서는 Phase 5-8의 신규 기능을 다룹니다.

---

## Phase 5: 데이터 관리 시스템

**목표**: DB 최적화 웹 UI로 마스터/이벤트 데이터 관리

### 5.1 Backend - DB 모델

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 5.1.1 | DataType 모델 생성 | ★★☆ | - | `backend/app/models/data_type.py` | [x] |
| 5.1.2 | DataRecord 모델 생성 | ★★☆ | 5.1.1 | `backend/app/models/data_record.py` | [x] |
| 5.1.3 | TemplateDataMapping 모델 생성 | ★★☆ | 5.1.1 | `backend/app/models/template_data_mapping.py` | [x] |
| 5.1.4 | models/__init__.py 업데이트 | ★☆☆ | 5.1.1~3 | `backend/app/models/__init__.py` | [x] |
| 5.1.5 | Alembic 마이그레이션 생성 | ★☆☆ | 5.1.4 | `backend/alembic/versions/` | [x] |

### 5.2 Backend - 데이터 타입 API

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 5.2.1 | DataType Pydantic 스키마 | ★★☆ | 5.1.1 | `backend/app/schemas/data_type.py` | [x] |
| 5.2.2 | 데이터 타입 CRUD API | ★★★ | 5.2.1 | `backend/app/api/v1/data_types.py` | [x] |
| 5.2.3 | API 라우터 등록 | ★☆☆ | 5.2.2 | `backend/app/api/v1/__init__.py` | [x] |
| 5.2.4 | 데이터 타입 API 테스트 | ★★☆ | 5.2.2 | `backend/tests/test_api_data_types.py` | [x] |

### 5.3 Backend - 데이터 레코드 API

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 5.3.1 | DataRecord Pydantic 스키마 | ★★☆ | 5.1.2 | `backend/app/schemas/data_record.py` | [x] |
| 5.3.2 | 레코드 CRUD API | ★★★ | 5.3.1 | `backend/app/api/v1/data_records.py` | [x] |
| 5.3.3 | Bulk 생성/수정 API | ★★★ | 5.3.2 | `backend/app/api/v1/data_records.py` | [x] |
| 5.3.4 | 검색/자동완성 API | ★★★ | 5.3.2 | `backend/app/api/v1/data_records.py` | [x] |
| 5.3.5 | 레코드 API 테스트 | ★★☆ | 5.3.2~4 | `backend/tests/test_api_data_records.py` | [x] |

### 5.4 Frontend - 데이터 그리드 컴포넌트

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 5.4.1 | DataGrid 컴포넌트 | ★★★ | - | `frontend/src/components/DataGrid/DataGrid.tsx` | [x] |
| 5.4.2 | EditableCell 컴포넌트 | ★★★ | 5.4.1 | `frontend/src/components/DataGrid/EditableCell.tsx` | [x] |
| 5.4.3 | AutocompleteCell 컴포넌트 | ★★★ | 5.4.1 | `frontend/src/components/DataGrid/AutocompleteCell.tsx` | [x] |
| 5.4.4 | DataGrid index 내보내기 | ★☆☆ | 5.4.1~3 | `frontend/src/components/DataGrid/index.ts` | [x] |
| 5.4.5 | API 클라이언트 확장 | ★★☆ | 5.2.2, 5.3.2 | `frontend/src/api/dataTypes.ts` | [x] |

### 5.5 Frontend - 데이터 관리 페이지

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 5.5.1 | 데이터 타입 목록 페이지 | ★★☆ | 5.4.5 | `frontend/src/pages/DataTypes.tsx` | [x] |
| 5.5.2 | 타입 생성/편집 모달 | ★★★ | 5.5.1 | `frontend/src/pages/DataTypes.tsx` (통합) | [x] |
| 5.5.3 | 레코드 편집 페이지 | ★★★ | 5.4.1~3 | `frontend/src/pages/DataRecords.tsx` | [x] |
| 5.5.4 | 라우터 업데이트 | ★☆☆ | 5.5.1, 5.5.3 | `frontend/src/App.tsx` | [x] |

**Phase 5 소계**: 23개 항목

---

## Phase 6: 폴더 감시 시스템

**목표**: 템플릿 자동 등록 기능

### 6.1 Backend - Watchdog 서비스

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 6.1.1 | Watchdog 설정 확장 | ★☆☆ | - | `backend/app/core/config.py` | [x] |
| 6.1.2 | 폴더 감시 서비스 | ★★★ | 6.1.1 | `backend/app/services/folder_watcher.py` | [x] |
| 6.1.3 | 감시 워커 | ★★☆ | 6.1.2 | `backend/app/workers/watcher_worker.py` | [x] |
| 6.1.4 | 감시 실행 스크립트 | ★☆☆ | 6.1.3 | `backend/run_watcher.py` | [x] |
| 6.1.5 | requirements.txt 업데이트 | ★☆☆ | 6.1.2 | `backend/requirements.txt` | [x] |

### 6.2 Backend - 감시 API

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 6.2.1 | 감시 상태 API | ★★☆ | 6.1.2 | `backend/app/api/v1/watcher.py` | [x] |
| 6.2.2 | WebSocket 알림 연동 | ★★★ | 6.1.2 | `backend/app/api/v1/websocket.py` | [x] |
| 6.2.3 | API 라우터 등록 | ★☆☆ | 6.2.1 | `backend/app/api/v1/__init__.py` | [x] |

### 6.3 테스트

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 6.3.1 | 폴더 감시 서비스 테스트 | ★★☆ | 6.1.2 | `backend/tests/test_folder_watcher.py` | [x] |
| 6.3.2 | 감시 API 테스트 | ★★☆ | 6.2.1 | `backend/tests/test_api_watcher.py` | [x] |

**Phase 6 소계**: 10개 항목

---

## Phase 7: 새 렌더링 워크플로우

**목표**: 데이터 선택 기반 렌더링

### 7.1 Backend - 템플릿-데이터 매핑

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 7.1.1 | TemplateDataMapping 스키마 | ★★☆ | 5.1.3 | `backend/app/schemas/template_mapping.py` | [x] |
| 7.1.2 | 매핑 API | ★★☆ | 7.1.1 | `backend/app/api/v1/template_mapping.py` | [x] |
| 7.1.3 | API 라우터 등록 | ★☆☆ | 7.1.2 | `backend/app/api/v1/__init__.py` | [x] |
| 7.1.4 | 매핑 API 테스트 | ★★☆ | 7.1.2 | `backend/tests/test_template_mapping.py` | [x] |

### 7.2 Backend - Job API 수정

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 7.2.1 | Job 스키마 수정 (data_selections) | ★★☆ | 5.3.1 | `backend/app/schemas/job.py` | [x] |
| 7.2.2 | Job 모델 수정 | ★★☆ | 7.2.1 | `backend/app/models/job.py` | [x] |
| 7.2.3 | Job 생성 로직 수정 | ★★★ | 7.2.2 | `backend/app/api/v1/jobs.py` | [x] |
| 7.2.4 | Nexrender 클라이언트 수정 | ★★★ | 7.2.3 | `backend/app/services/nexrender_client.py` | [ ] |
| 7.2.5 | Job API 테스트 업데이트 | ★★☆ | 7.2.3 | `backend/tests/test_api_jobs.py` | [x] |

### 7.3 Frontend - 매핑 UI

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 7.3.1 | 템플릿 매핑 페이지 | ★★★ | 7.1.2 | `frontend/src/pages/TemplateMapping.tsx` | [x] |
| 7.3.2 | 매핑 컴포넌트 | ★★★ | 7.3.1 | `frontend/src/components/LayerMappingForm.tsx` | [x] (통합) |

### 7.4 Frontend - 렌더링 선택 페이지

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 7.4.1 | 렌더링 선택 페이지 | ★★★ | 7.2.3, 5.5.3 | `frontend/src/pages/RenderSelect.tsx` | [x] |
| 7.4.2 | 데이터 선택 컴포넌트 | ★★★ | 7.4.1 | `frontend/src/components/DataSelector.tsx` | [x] (통합) |
| 7.4.3 | 라우터 업데이트 | ★☆☆ | 7.3.1, 7.4.1 | `frontend/src/App.tsx` | [x] |

**Phase 7 소계**: 14개 항목

---

## Phase 8: 고급 기능 및 안정화

**목표**: 완성도 향상

### 8.1 다중 선택 배치 렌더링

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 8.1.1 | 다중 데이터 선택 UI | ★★★ | 7.4.1 | `frontend/src/pages/RenderSelect.tsx` | [ ] |
| 8.1.2 | 배치 Job API 수정 | ★★☆ | 7.2.3 | `backend/app/api/v1/jobs.py` | [ ] |
| 8.1.3 | 배치 진행률 컴포넌트 | ★★☆ | 8.1.2 | `frontend/src/components/BatchProgress.tsx` | [ ] |

### 8.2 데이터 가져오기/내보내기

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 8.2.1 | CSV 내보내기 API | ★★☆ | 5.3.2 | `backend/app/api/v1/data_records.py` | [ ] |
| 8.2.2 | CSV 가져오기 API | ★★★ | 5.3.3 | `backend/app/api/v1/data_records.py` | [ ] |
| 8.2.3 | Excel 지원 (openpyxl) | ★★☆ | 8.2.1~2 | `backend/app/services/data_export.py` | [ ] |
| 8.2.4 | 가져오기/내보내기 UI | ★★☆ | 8.2.1~3 | `frontend/src/pages/DataRecords.tsx` | [ ] |
| 8.2.5 | requirements.txt 업데이트 | ★☆☆ | 8.2.3 | `backend/requirements.txt` | [ ] |

### 8.3 성능 최적화

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 8.3.1 | 가상 스크롤 적용 | ★★★ | 5.4.1 | `frontend/src/components/DataGrid/` | [ ] |
| 8.3.2 | 검색 인덱싱 최적화 | ★★☆ | 5.3.4 | `backend/app/models/data_record.py` | [ ] |
| 8.3.3 | Redis 캐싱 적용 | ★★☆ | 5.2.2 | `backend/app/api/v1/data_types.py` | [ ] |

### 8.4 테스트 및 문서화

| # | Task | 난이도 | 의존성 | 파일 | 상태 |
|---|------|--------|--------|------|------|
| 8.4.1 | 통합 테스트 작성 | ★★★ | Phase 5~7 | `backend/tests/test_integration.py` | [ ] |
| 8.4.2 | API 문서 업데이트 | ★★☆ | Phase 5~7 | OpenAPI (자동) | [ ] |
| 8.4.3 | 사용자 가이드 작성 | ★★☆ | 8.4.2 | `docs/USER_GUIDE.md` | [ ] |

**Phase 8 소계**: 14개 항목

---

## 통계 요약

| Phase | 설명 | 항목 수 | 완료 | 진행률 |
|-------|------|---------|------|--------|
| Phase 5 | 데이터 관리 시스템 | 23 | 23 | 100% |
| Phase 6 | 폴더 감시 시스템 | 10 | 10 | 100% |
| Phase 7 | 새 렌더링 워크플로우 | 14 | 13 | 93% |
| Phase 8 | 고급 기능 및 안정화 | 14 | 0 | 0% |
| **합계** | | **61** | **46** | **75%** |

### 우선순위별 분포

| 우선순위 | 항목 수 | 설명 |
|----------|---------|------|
| P0 (Critical) | 47 | Phase 5-7 핵심 기능 |
| P1 (High) | 10 | Phase 6.2, 8.1, 8.3, 8.4 |
| P2 (Medium) | 4 | Phase 8.2 (Import/Export) |

### 난이도별 분포

| 난이도 | 항목 수 | 설명 |
|--------|---------|------|
| ★☆☆ | 12 | 설정, 라우터, 업데이트 |
| ★★☆ | 28 | 스키마, 표준 API, 테스트 |
| ★★★ | 21 | 핵심 로직, 복잡한 UI |

---

## 의존성 그래프

```
Phase 5.1 (Models)
    │
    ├──▶ Phase 5.2 (Data Type API)
    │        │
    │        └──▶ Phase 5.4.5 (API Client)
    │                  │
    │                  └──▶ Phase 5.5 (Pages)
    │
    ├──▶ Phase 5.3 (Data Record API)
    │        │
    │        └──▶ Phase 5.4.5 (API Client)
    │
    └──▶ Phase 7.1 (Template Mapping)
             │
             └──▶ Phase 7.2 (Job API)
                      │
                      └──▶ Phase 7.4 (Render Select)

Phase 5.4.1~3 (DataGrid) ──▶ Phase 5.5.3 (Records Page)
                                   │
                                   └──▶ Phase 7.4.1 (Render Select)

Phase 6 (Folder Watcher) ──▶ 독립적 (병렬 진행 가능)

Phase 8 (Advanced) ──▶ Phase 5-7 완료 후 진행
```

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-25 | 1.0.0 | 초기 작성 |
| 2025-12-26 | 1.1.0 | Phase 5 완료, Phase 6 부분 완료 상태 반영 |
