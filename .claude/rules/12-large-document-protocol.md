# 대형 문서 생성 프로토콜 — 출력 토큰 초과 방지

**트리거**: 에이전트가 PRD, Plan, Design, Report 등 대형 문서를 생성하는 모든 상황

## 핵심 원칙

단일 응답으로 전체 문서를 생성하지 않는다. 출력 토큰 한계(64,000)를 초과하면 작업이 중단된다.

## 3-Phase 복구 전략

### Phase 1: 감지 (stop_reason 기반)

| stop_reason | 의미 | 처리 |
|-------------|------|------|
| `max_tokens` | 요청 한계 초과 | Continuation Loop |
| `model_context_window_exceeded` | 컨텍스트 윈도우 초과 | 컨텍스트 압축 후 재시도 |
| `pause_turn` | 서버 툴 반복 한계 | 대화 재개 루프 |

### Phase 2: 복구 (Continuation Loop)

`stop_reason == max_tokens` 감지 시:

```
max_attempts = 3
full_response = ""

Loop (attempt=1..max_attempts):
  response = 생성 요청
  full_response += response.content
  if stop_reason != "max_tokens":
    break
  # 중단점부터 재개: "Please continue from where you left off."
```

**중단점 재개 규칙**:
- 완료된 섹션은 절대 재생성하지 않는다
- 중단된 섹션만 이어서 작성한다
- 3회 초과 시 → 미완료 상태 보고 + 사용자 판단 요청

### Phase 3: 설계 전환 (Map-Reduce 청킹)

3회 Continuation Loop 실패 시 → 섹션별 분산 생성으로 전환:

```
[Map 단계] 섹션별 독립 생성
  섹션 1 (배경/목적) → Write skeleton
  섹션 2 (요구사항) → Edit append
  섹션 3 (기능 범위) → Edit append
  섹션 N (...) → Edit append

[Reduce 단계] 통합 검토
  전체 문서 일관성 확인
  섹션 간 중복/충돌 제거
```

## 에이전트 타임아웃 처리 규칙

### 절대 금지
- 타임아웃 발생 시 전체 문서 재생성 Fallback **절대 금지**
- 이유: 비용 폭증 + 동일 오류 반복 가능성 높음

### 올바른 타임아웃 처리
```
에이전트 타임아웃 감지 (5분+)
  └─ 완료된 섹션 확인 (파일 부분 존재 여부)
  └─ 미완료 섹션만 재시도
  └─ Circuit Breaker: 동일 실패 3회 → 섹션 분할 모드 강제 전환
  └─ 3회 모두 실패 → 에러 보고 + 사용자 판단 요청 (강제 진행 금지)
```

## 대형 문서 작성 표준 프로토콜

문서 예상 크기 기준:
- **소형** (< 100줄): 단일 Write 허용
- **중형** (100~300줄): Write(스켈레톤) + Edit(섹션별) 권장
- **대형** (300줄+): Map-Reduce 청킹 필수

### 스켈레톤-퍼스트 패턴 (중형 이상)

```
Step 1: Write(스켈레톤)
  # 문서제목
  ## 섹션 1
  (내용 placeholder)
  ## 섹션 2
  (내용 placeholder)
  ...

Step 2: Edit(섹션 1 내용 채우기)
Step 3: Edit(섹션 2 내용 채우기)
...
```

## 금지 사항
- 500줄+ 문서를 단일 Write로 생성 금지
- 토큰 초과 후 전체 재생성 Fallback 금지
- 타임아웃된 에이전트의 작업을 Lead가 직접 인계받아 전체 생성 금지
- Circuit Breaker 없이 무한 재시도 금지
