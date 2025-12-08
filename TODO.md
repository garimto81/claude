# TODO - 점진적 개선 계획

**생성일**: 2025-12-08
**기반**: Backend/Frontend 코드베이스 분석

---

## P0: 즉시 수정 (보안)

### [x] `eval()` 보안 취약점 제거 ✅
- **파일**: `backend/src/services/gcs_streaming.py:367-369`
- **수정 완료**: `fractions.Fraction` 사용으로 안전하게 변경
- **완료일**: 2025-12-08

---

## P1: 단기 개선 (1-2일)

### [ ] Clips 페이지 완성
- **파일**: `frontend/src/App.tsx:65`
- **현재 상태**: `<div>Clips Page (Coming Soon)</div>`
- **구현 항목**:
  - [ ] ClipsPage.tsx 컴포넌트 생성
  - [ ] 클립 목록 조회 (apiClient.listClips)
  - [ ] 클립 다운로드 기능
  - [ ] 클립 삭제 기능
- **예상 소요**: 4시간

### [ ] GCSVideosPage 컴포넌트 분리
- **파일**: `frontend/src/pages/GCSVideosPage.tsx` (440줄)
- **분리 대상**:
  - [ ] `GCSVideoCard.tsx` - 비디오 카드 컴포넌트
  - [ ] `ClipCreationModal.tsx` - 클립 생성 모달
  - [ ] `useGCSVideos.ts` - 커스텀 훅 (상태 관리)
- **예상 소요**: 2시간

---

## P2: 중기 개선 (3-5일)

### [ ] FastAPI lifespan 마이그레이션
- **파일**: `backend/src/main.py:18`
- **현재 코드**:
  ```python
  @app.on_event("startup")  # deprecated
  async def startup_event():
  ```
- **수정 방안**:
  ```python
  from contextlib import asynccontextmanager

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # startup
      yield
      # shutdown

  app = FastAPI(lifespan=lifespan)
  ```
- **예상 소요**: 1시간

### [ ] OpenAPI → TypeScript 자동 생성
- **목적**: Backend Pydantic ↔ Frontend TypeScript 타입 동기화
- **도구**: `openapi-typescript` 또는 `orval`
- **설정**:
  ```bash
  npx openapi-typescript http://localhost:8001/openapi.json -o src/types/api.ts
  ```
- **예상 소요**: 2시간

### [ ] 에러 바운더리 추가
- **파일**: `frontend/src/components/ErrorBoundary.tsx` (신규)
- **적용 위치**: `App.tsx` 최상위
- **예상 소요**: 1시간

---

## P3: 장기 개선 (선택)

### [ ] 상태 관리 라이브러리 도입
- **후보**: Zustand (경량) / Jotai (atomic)
- **적용 범위**:
  - GCS 비디오 목록 캐싱
  - 클립 생성 상태
  - 전역 로딩/에러 상태
- **예상 소요**: 1일

### [ ] API 버저닝
- **현재**: `/api/videos`
- **변경**: `/api/v1/videos`
- **예상 소요**: 2시간

### [ ] 테스트 커버리지 확대
- **Backend**: `services/` 테스트 추가
- **Frontend**: 컴포넌트 테스트 추가
- **목표**: 80% 커버리지
- **예상 소요**: 2일

---

## 완료 항목

### [x] CLAUDE.md 업데이트 (v6.0.0)
- 경로 수정: `D:\AI\claude01` → `D:\AI\archive-analyzer`
- 프로젝트 구조 섹션 추가
- 빌드/테스트 명령어 컴포넌트별 분리

---

## 관련 이슈

| 이슈 | 상태 | 설명 |
|------|------|------|
| #43 | Open | Docker 서버 배포 + GUI 모니터링 |
| #41 | Open | NAS 경로 변경 실시간 감지 |
| #23 | Open | Archive MAM 병렬 개발 구조 |

---

## 진행 순서 권장

```
1. P0: eval() 수정 (30분) → 보안 최우선
2. P1: Clips 페이지 (4시간) → 기능 완성
3. P1: 컴포넌트 분리 (2시간) → 유지보수성
4. P2: lifespan 마이그레이션 (1시간) → 기술 부채
5. P2: OpenAPI 자동 생성 (2시간) → 개발 효율
```
