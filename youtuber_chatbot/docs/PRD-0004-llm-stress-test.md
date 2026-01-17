# PRD-0004: 로컬 LLM 모델 극한 테스트 환경

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P1 |
| **Created** | 2026-01-07 |
| **Author** | Claude Code |

---

## 1. 개요

### 1.1 목적

Qwen3 시리즈 (4b/8b/14b) 모델의 성능 한계를 측정하고, YouTube 챗봇 운영 시 예상되는 극한 상황에서의 동작을 검증하는 테스트 환경을 설계한다.

### 1.2 배경

- 현재 프로젝트는 Ollama + Qwen3:8b를 기본 모델로 사용
- 라이브 방송 중 동시 채팅 폭주 시 LLM 응답 지연 가능성
- 모델별 성능 차이 및 최적 설정값 파악 필요

### 1.3 범위

| 포함 | 제외 |
|------|------|
| Qwen3 4b/8b/14b 성능 측정 | 클라우드 LLM API 테스트 |
| 응답 속도/지연시간 테스트 | 모델 학습/파인튜닝 |
| 동시 요청 처리 테스트 | 다른 LLM 프레임워크 (vLLM 등) |
| 메모리/GPU 자원 한계 테스트 | 프로덕션 배포 |

---

## 2. 테스트 시나리오

### 2.1 응답 속도/지연시간 한계 (Latency Test)

**목표**: 각 모델의 응답 시간 분포 및 최대 허용 지연시간 측정

| 테스트 항목 | 측정 지표 | 목표 |
|------------|----------|------|
| 첫 토큰 응답 시간 (TTFT) | ms | < 500ms |
| 총 응답 완료 시간 (TTL) | ms | < 3000ms |
| 토큰/초 생성 속도 | tokens/sec | > 30 |
| P50/P95/P99 지연시간 | ms | 분포 파악 |

**테스트 케이스**:

```
1. 짧은 질문 (10 tokens 이하)
   예: "안녕하세요"

2. 중간 질문 (50 tokens)
   예: "이 방송에서 다루는 주제가 뭐예요?"

3. 긴 질문 (200+ tokens)
   예: 복잡한 기술 질문

4. 컨텍스트 포함 질문
   예: 이전 대화 맥락 참조
```

### 2.2 동시 요청 처리 한계 (Concurrency Test)

**목표**: 동시 요청 시 성능 저하 패턴 및 최대 처리량 파악

| 테스트 항목 | 측정 지표 | 임계점 |
|------------|----------|--------|
| 동시 요청 수 | count | 1, 5, 10, 20, 50 |
| 요청 큐 대기 시간 | ms | 측정 |
| 처리량 (Throughput) | req/sec | 최대값 파악 |
| 실패율 | % | < 1% |

**테스트 시나리오**:

```
Level 1: 순차 요청 (baseline)
Level 2: 5 동시 요청
Level 3: 10 동시 요청
Level 4: 20 동시 요청 (스트레스)
Level 5: 50 동시 요청 (극한)
```

### 2.3 메모리/GPU 자원 한계 (Resource Test)

**목표**: 모델별 자원 사용량 및 OOM 임계점 파악

| 테스트 항목 | 측정 지표 | 모니터링 |
|------------|----------|----------|
| VRAM 사용량 | GB | nvidia-smi |
| RAM 사용량 | GB | 시스템 모니터 |
| GPU 사용률 | % | 부하 패턴 |
| 컨텍스트 길이 한계 | tokens | 최대 입력 |

**테스트 케이스**:

```
1. 단일 요청 기본 부하
2. 긴 컨텍스트 (4K, 8K, 16K tokens)
3. 연속 요청 (메모리 누수 검사)
4. OOM 유발 시나리오
```

---

## 3. 테스트 환경

### 3.1 하드웨어 요구사항

```yaml
최소 사양:
  GPU: NVIDIA GPU (8GB+ VRAM)
  RAM: 16GB
  Storage: 50GB SSD

권장 사양:
  GPU: NVIDIA RTX 3080+ (12GB+ VRAM)
  RAM: 32GB
  Storage: 100GB NVMe SSD
```

### 3.2 소프트웨어 환경

```yaml
OS: Windows 10/11
Runtime:
  - Node.js 20+
  - Ollama latest
Models:
  - qwen3:4b
  - qwen3:8b
  - qwen3:14b
Dependencies:
  - vitest (테스트 러너)
  - piscina (워커 풀)
```

### 3.3 디렉토리 구조

```
tests/
├── stress/
│   ├── latency.stress.ts      # 응답 속도 테스트
│   ├── concurrency.stress.ts  # 동시 요청 테스트
│   ├── resource.stress.ts     # 자원 한계 테스트
│   ├── fixtures/
│   │   ├── questions.json     # 테스트 질문 세트
│   │   └── contexts.json      # 컨텍스트 데이터
│   └── utils/
│       ├── metrics.ts         # 메트릭 수집
│       └── reporter.ts        # 결과 리포터
├── benchmarks/
│   └── results/
│       ├── YYYY-MM-DD-qwen3-4b.md
│       ├── YYYY-MM-DD-qwen3-8b.md
│       └── YYYY-MM-DD-qwen3-14b.md
```

---

## 4. 테스트 실행

### 4.1 명령어

```powershell
# 전체 스트레스 테스트
npm run test:stress

# 개별 테스트
npx vitest run tests/stress/latency.stress.ts
npx vitest run tests/stress/concurrency.stress.ts
npx vitest run tests/stress/resource.stress.ts

# 특정 모델 지정
OLLAMA_MODEL=qwen3:14b npm run test:stress

# 벤치마크 결과 생성
npm run benchmark:report
```

### 4.2 환경 변수

```env
# 테스트 대상 모델
STRESS_TEST_MODELS=qwen3:4b,qwen3:8b,qwen3:14b

# 테스트 강도
STRESS_TEST_ITERATIONS=100
STRESS_TEST_CONCURRENCY_MAX=50
STRESS_TEST_TIMEOUT=30000

# 결과 저장
STRESS_TEST_OUTPUT_DIR=tests/benchmarks/results
```

---

## 5. 결과 리포트 형식

### 5.1 Markdown 벤치마크 테이블

```markdown
# Qwen3 스트레스 테스트 결과

**테스트 일시**: 2026-01-07
**하드웨어**: RTX 3080 12GB / 32GB RAM
**Ollama 버전**: 0.5.x

## 응답 속도 비교

| 모델 | TTFT (ms) | TTL (ms) | Tokens/sec | P95 (ms) |
|------|-----------|----------|------------|----------|
| qwen3:4b | 120 | 1200 | 45 | 1800 |
| qwen3:8b | 250 | 2100 | 35 | 3200 |
| qwen3:14b | 480 | 3800 | 22 | 5500 |

## 동시 요청 처리

| 모델 | Max Concurrent | Throughput | Fail Rate |
|------|----------------|------------|-----------|
| qwen3:4b | 30 | 8.5 req/s | 0.5% |
| qwen3:8b | 15 | 4.2 req/s | 1.2% |
| qwen3:14b | 8 | 2.1 req/s | 2.5% |

## 자원 사용량

| 모델 | VRAM (GB) | RAM (GB) | Context Max |
|------|-----------|----------|-------------|
| qwen3:4b | 4.2 | 8.5 | 32K |
| qwen3:8b | 8.1 | 12.3 | 32K |
| qwen3:14b | 12.8 | 18.2 | 32K |

## 권장 설정

| 시나리오 | 권장 모델 | 이유 |
|----------|----------|------|
| 일반 방송 | qwen3:8b | 품질/속도 균형 |
| 고트래픽 | qwen3:4b | 동시 처리 우선 |
| 저트래픽+고품질 | qwen3:14b | 응답 품질 최대화 |
```

---

## 6. 성공 기준

### 6.1 필수 (Must Have)

- [ ] 3개 모델 (4b/8b/14b) 모두 테스트 완료
- [ ] 응답 속도 테스트: 100회 반복, P95 측정
- [ ] 동시 요청 테스트: 1~50 범위 단계별 측정
- [ ] 자원 사용량: VRAM/RAM 피크값 기록
- [ ] Markdown 벤치마크 테이블 자동 생성

### 6.2 권장 (Should Have)

- [ ] OOM 발생 시 graceful 복구 테스트
- [ ] 장시간 연속 테스트 (1시간+)
- [ ] 다양한 질문 유형별 성능 차이 분석

### 6.3 선택 (Nice to Have)

- [ ] 히스토그램/차트 시각화
- [ ] 이전 결과 대비 성능 추이 비교
- [ ] 자동 최적 모델 추천 로직

---

## 7. 의존성

### 7.1 새로 추가할 패키지

```json
{
  "devDependencies": {
    "piscina": "^4.0.0",
    "systeminformation": "^5.21.0"
  }
}
```

### 7.2 기존 활용

- `vitest`: 테스트 러너
- `src/services/llm-client.ts`: LLM 클라이언트

---

## 8. 리스크 및 완화

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| 테스트 중 OOM | 시스템 불안정 | 모니터링 + 자동 중단 |
| GPU 과열 | 하드웨어 손상 | 쿨링 확인, 온도 모니터링 |
| 긴 테스트 시간 | 개발 지연 | 병렬 실행, 샘플링 |

---

## 9. 일정

> **주의**: 시간 추정은 제공하지 않습니다. 아래는 작업 순서입니다.

1. 테스트 인프라 구축 (디렉토리, 설정)
2. 응답 속도 테스트 구현
3. 동시 요청 테스트 구현
4. 자원 모니터링 테스트 구현
5. 리포트 생성기 구현
6. 전체 테스트 실행 및 검증

---

## 10. 참조

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Qwen3 Model Card](https://ollama.com/library/qwen3)
- PRD-0002: YouTube 챗봇 기본 설계
