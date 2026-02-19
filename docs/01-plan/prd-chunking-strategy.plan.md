# PRD/기획서 전용 Chunking 전략 구현 계획

**버전**: 1.0.1 | **작성일**: 2026-02-19 | **기반 PRD**: `C:\claude\docs\00-prd\prd-chunking-strategy.prd.md`

---

## 배경 (Background)

### 요청 내용
PRD/기획서 문서(MD/PDF)에서 발생하는 토큰 초과 오류를 해결하기 위해, 문서 구조를 인식하는 지능형 청킹 시스템을 구현한다.

### 해결하려는 문제
- Claude API 토큰 한계(90,000~150,000 토큰 구간)로 인한 MD/PDF 읽기 실패
- 현행 `/chunk` 커맨드는 PDF만 지원, MD 파일 미지원
- 단순 Fixed-size 방식(4,000T/200 오버랩)으로 PRD 섹션 경계 무시 → 청크 내 컨텍스트 손실
- 표(|---|)와 코드블록(```) 분리 → 내용 손실 발생

### 현행 아키텍처 현황
```
  현행 구조:
  ┌──────────────────────────────────────────────────┐
  │  /chunk 커맨드                                    │
  │  └── lib/pdf_utils/_compat.py (subprocess 래퍼)  │
  │       ├── ebs/tools/pdf_chunker.py (토큰 기반)   │
  │       └── ebs/tools/pdf_page_chunker.py (페이지) │
  └──────────────────────────────────────────────────┘

  lib/pdf_utils/ 내 소스 .py는 없음 (pyc만 존재):
  - __init__.py, cli.py, extractor.py, models.py
  - errors.py, _compat.py
  - tests/ (conftest, test_cli, test_extractor, test_models)

  ebs/tools/ 실제 소스:
  - pdf_chunker.py     : TokenCounter + PDFChunker (Fixed-size, fitz)
  - pdf_page_chunker.py: PDFPageChunker (페이지 기반, fitz)
```

---

## 구현 범위 (Scope)

### 포함 항목 (P0~P1 전량 + P2 일부)
- R1: 60,000 토큰 자동 감지 → 청킹 전환 (tiktoken 활용)
- R3: Hierarchical Parent-Child Chunking (H1/H2/H3 계층 추출)
- R7: MD 파일(.md, .markdown) 직접 파싱 및 청킹
- NR2: 표(|---|) 및 코드블록(```) 분리 방지
- NR3: 기존 `/chunk` 하위 호환성 유지 (4,000T/200 오버랩 유지)
- R2: Fixed-size 기본값 개선 (--prd 모드: 8,000T/400 오버랩)
- R6: `/chunk --prd` 옵션 추가
- R8: 청크 간 컨텍스트 메타데이터 (섹션 경로, prev_id, next_id)
- R9: 자동 전략 선택 로직 (60K/100K 분기)
- R4: Semantic Chunking (표/목록 단위 보존)

### 제외 항목
- R5: Late Chunking (sentence-transformers, P3 — 별도 PRD)
- Word/Excel 지원
- 벡터 DB 연동
- 실시간 스트리밍 청킹

---

## 영향 파일 (Affected Files)

### 신규 생성 파일

| 파일 경로 | 역할 |
|-----------|------|
| `C:\claude\lib\pdf_utils\__init__.py` | pdf_utils 패키지 초기화 (lib 임포트 가능하도록) |
| `C:\claude\lib\pdf_utils\md_chunker.py` | MD 파일 파싱 + 4가지 전략 구현 (핵심 신규 모듈) |
| `C:\claude\lib\pdf_utils\prd_models.py` | PRD 전용 데이터 모델 (PRDChunk, PRDChunkResult) |
| `C:\claude\lib\pdf_utils\strategy.py` | 자동 전략 선택 로직 (R9) |
| `C:\claude\lib\pdf_utils\tests\test_md_chunker.py` | MD 청킹 단위 테스트 |
| `C:\claude\lib\pdf_utils\tests\test_prd_models.py` | PRDChunk, PRDChunkResult 데이터모델 단위 테스트 |
| `C:\claude\lib\pdf_utils\tests\test_prd_strategy.py` | 전략 선택 로직 테스트 |

### 수정 예정 파일

| 파일 경로 | 변경 내용 |
|-----------|-----------|
| `C:\claude\ebs\tools\pdf_chunker.py` | --prd 플래그 추가, MD 파일 분기, 섹션 경계 우선 분할 |
| `C:\claude\.claude\commands\chunk.md` | --prd 옵션 문서 추가, MD 파일 지원 안내 |

> `lib/pdf_utils/` 내 소스 .py가 없으므로(pyc만 존재) 신규 모듈은 별도 파일로 생성한다.
> `ebs/tools/pdf_chunker.py`는 실제 소스가 있어 직접 수정 가능하다.

---

## 핵심 알고리즘 설계

### 1. MD 파서 (md_chunker.py)

```
  MD 파일 파싱 흐름:
  ┌──────────────────────────────────────────────┐
  │  입력: .md / .markdown 파일                   │
  │                                              │
  │  Step 1: 토큰 사전 추정 (TokenCounter)        │
  │    tiktoken cl100k_base or 간이 추정           │
  │                                              │
  │  Step 2: 임계값 판단                          │
  │    < 60,000T → 청킹 불필요 (전체 반환)         │
  │    60,000T ~ 100,000T → Fixed-size 또는 Hier  │
  │    PRD 구조 감지됨 → Hierarchical 우선         │
  │    > 100,000T → Hierarchical + Semantic 조합  │
  │                                              │
  │  Step 3: 블록 분류 파싱                       │
  │    - Heading 블록 (# ## ### ####)             │
  │    - Table 블록 (|---|로 시작하는 행 집합)     │
  │    - CodeBlock 블록 (``` ~ ```)               │
  │    - ListBlock (- * 1. 으로 시작)             │
  │    - Paragraph (나머지)                       │
  │                                              │
  │  Step 4: 전략별 분할                          │
  │    → 청크 목록 반환                            │
  └──────────────────────────────────────────────┘
```

### 2. Hierarchical Parent-Child 알고리즘 (핵심)

```
  Pseudo-code: build_hierarchy(blocks)

  section_stack = []  # [(level, title, content_blocks)]
  chunks = []

  for block in blocks:
      if block.type == HEADING:
          level = count_hashes(block)  # H1=1, H2=2, H3=3

          # 스택 정리: 현재 레벨 이상의 섹션 닫기
          while section_stack and section_stack[-1].level >= level:
              closed = section_stack.pop()
              if closed.has_content():
                  chunk = make_child_chunk(closed, parent_path)
                  chunks.append(chunk)

          # 현재 헤딩을 새 섹션으로 push
          parent_path = [s.title for s in section_stack]
          section_stack.append(Section(level, block.text, parent_path))

      elif block.type in (TABLE, CODE_BLOCK):
          # 원자 블록: 반드시 단일 청크로 보존
          current = section_stack[-1] if section_stack else None
          if current:
              current.add_atomic(block)  # 절대 분리 금지 플래그

      else:
          if section_stack:
              section_stack[-1].add(block)

  # 스택 잔여 섹션 닫기
  flush_remaining(section_stack, chunks)
  # flush_remaining 구현 지시:
  # for section in reversed(section_stack):
  #     if section.has_content():
  #         parent_path = [s.title for s in section_stack[:section_stack.index(section)]]
  #         chunk = make_child_chunk(section, parent_path)
  #         chunks.append(chunk)
  # section_stack.clear()

  # 토큰 제한 초과 청크 재분할 (원자 블록은 제외)
  return split_oversized(chunks, max_tokens=8000)
```

### 3. 표/코드블록 분리 방지 (NR2)

```
  ATOMIC BLOCK 규칙:

  표 감지:
    line.strip().startswith('|') and any('|---|' in l or '|:---|' in l or '|---:|' in l
        for l in lines[i+1:i+4])  # 현재 행 기준 다음 3행 이내에서 구분선 확인

  코드블록 감지:
    line.strip().startswith('```')
    → 다음 '```' 닫힘까지 전체를 단일 atomic_block으로 래핑

  분할 시:
    if atomic_block.token_count > max_tokens:
        # 분할 불가 → 단독 청크로 강제 배출 (경고 로그)
        warn("원자 블록이 max_tokens 초과, 단독 청크로 배출")
    else:
        # 현재 청크에 들어가지 않으면 다음 청크로 이동
        start_new_chunk()
        add_to_chunk(atomic_block)
```

### 4. 자동 전략 선택 (R9)

```
  auto_select_strategy(file_path, token_count):

  1. PRD 구조 감지:
     prd_score = 0
     if heading_count >= 3:    prd_score += 1
     if has_req_numbers:       prd_score += 2  # R1, NR1, SC1 패턴
     if has_table:             prd_score += 1
     if h2_count >= 2:         prd_score += 1

  2. 전략 결정:
     if token_count < 60_000:
         return "none"  # 청킹 불필요

     if prd_score >= 3 and token_count < 100_000:
         return "hierarchical"

     if has_table_heavy and not prd_score:
         return "semantic"

     if token_count >= 100_000:
         return "hierarchical+semantic"  # 조합

     return "fixed"  # 기본 fallback
```

---

## 구현 순서 (의존성 고려)

```
  구현 순서:
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Task 1 (기반 모델)                                       │
  │  prd_models.py: PRDChunk, PRDChunkResult 데이터클래스     │
  │  ↓                                                       │
  │  Task 2 (핵심 파서)                                       │
  │  md_chunker.py: MDParser + 4가지 전략                     │
  │  ├── Fixed-size (섹션 경계 우선)                          │
  │  ├── Hierarchical (Parent-Child)                          │
  │  ├── Semantic (표/목록 보존)                              │
  │  └── 원자 블록 보호 로직 (NR2)                            │
  │  ↓                                                       │
  │  Task 3 (자동 선택)                                       │
  │  strategy.py: auto_select_strategy + PRD 구조 감지        │
  │  ↓                                                       │
  │  Task 4 (CLI 확장)                                        │
  │  ebs/tools/pdf_chunker.py: --prd 플래그 + MD 분기         │
  │  ↓                                                       │
  │  Task 5 (테스트)                                          │
  │  test_md_chunker.py + test_prd_strategy.py               │
  │  ↓                                                       │
  │  Task 6 (커맨드 문서 업데이트)                             │
  │  .claude/commands/chunk.md: --prd 옵션 추가               │
  └──────────────────────────────────────────────────────────┘
```

---

## 태스크 목록 (Tasks)

### Task 1: PRD 전용 데이터 모델 생성

**파일**: `C:\claude\lib\pdf_utils\prd_models.py` (신규)

**구현 내용**:
```python
@dataclass
class PRDChunk:
    chunk_id: int
    text: str
    token_count: int
    section_path: list[str]   # ["문서제목", "2. 요구사항", "기능 요구사항"]
    level: int                 # 1=H1, 2=H2, 3=H3
    parent_summary: str        # 상위 섹션 요약 (메타데이터)
    prev_chunk_id: int | None  # 이전 청크 ID (R8)
    next_chunk_id: int | None  # 다음 청크 ID (R8)
    has_table: bool            # 표 포함 여부
    has_code: bool             # 코드블록 포함 여부
    is_atomic: bool            # 원자 블록 여부 (분리 불가)

@dataclass
class PRDChunkResult:
    source_file: str
    total_pages: int           # MD면 0, PDF면 실제 페이지 수
    total_chars: int
    total_tokens: int
    chunk_count: int
    max_tokens_per_chunk: int
    overlap_tokens: int
    encoding: str
    # PRD 전용 추가 필드 (C4 요구사항)
    prd_mode: bool
    strategy: str              # "fixed"|"hierarchical"|"semantic"|"hierarchical+semantic"
    section_tree: list[dict]   # 문서 섹션 트리 (선택)
    chunks: list[PRDChunk]
```

**Acceptance Criteria**:
- [x] `PRDChunk.to_dict()` 호출 시 기존 `Chunk.to_dict()` 필드(chunk_id, text, token_count)를 포함
- [x] `PRDChunkResult.to_dict()` 기존 JSON 출력 필드 4종 유지 (source_file, total_pages, chunk_count, chunks)
- [x] `pytest C:\claude\lib\pdf_utils\tests\test_prd_models.py -v` PASS

---

### Task 2: MD 파서 + 청킹 전략 구현

**파일**: `C:\claude\lib\pdf_utils\md_chunker.py` (신규)

**구현 내용**:

```
  MDParser 클래스:
  - parse(file_path) → list[Block]
    - Block 타입: HEADING, TABLE, CODE_BLOCK, LIST, PARAGRAPH
    - 원자 블록(TABLE, CODE_BLOCK) 자동 래핑
    - HEADING 레벨(1~4) 자동 감지

  MDChunker 클래스:
  - __init__(strategy, max_tokens=8000, overlap=400, encoding="cl100k_base")
  - chunk_fixed(blocks) → list[PRDChunk]
    - 섹션 경계(HEADING) 우선 분할점
    - 원자 블록 보호
  - chunk_hierarchical(blocks) → list[PRDChunk]
    - section_stack 기반 Parent-Child
    - prev_chunk_id/next_chunk_id 연결 (후처리)
  - chunk_semantic(blocks) → list[PRDChunk]
    - 표/목록 단위 단일 청크
    - 빈 줄 2개 이상 = 의미 경계
    - 요구사항 번호(R\d+|NR\d+|SC\d+) 변경점 = 경계
  - process(file_path) → PRDChunkResult
    - 토큰 사전 추정 → 자동 전략 선택 or 명시 전략
```

**Acceptance Criteria**:
- [x] 100줄 이상 MD 파일 청킹 시 단일 청크 내 `|---|` 패턴이 분리된 케이스 0건
- [x] 단일 청크 내 ` ``` ` 오픈/클로즈 쌍이 불일치하는 케이스 0건
- [x] Hierarchical 청킹 시 section_path가 올바른 계층 경로를 반환 (H1→H2→H3)
- [x] `pytest tests/test_md_chunker.py -v` PASS (7개 이상 케이스)

---

### Task 3: 자동 전략 선택 로직 구현

**파일**: `C:\claude\lib\pdf_utils\strategy.py` (신규)

**구현 내용**:

```python
def estimate_tokens(text: str, encoding: str = "cl100k_base") -> int:
    """tiktoken 또는 간이 추정으로 토큰 수 반환"""

def detect_prd_structure(text: str) -> dict:
    """PRD 구조 감지
    Returns: {
        "prd_score": int,       # 0~5
        "heading_count": int,
        "has_req_numbers": bool,  # R1, NR1, SC1 패턴
        "has_table": bool,
        "is_heavy_table": bool,
        "h2_count": int
    }
    """

THRESHOLD_CHUNK = 60_000     # 이 이상 → 청킹 필요
THRESHOLD_HIER  = 100_000    # 이 이상 → 조합 전략

def auto_select_strategy(file_path: str, text: str = None) -> str:
    """문서 분석 → 전략 자동 선택
    Returns: "none" | "fixed" | "hierarchical" | "semantic" | "hierarchical+semantic"
    """
```

**Acceptance Criteria**:
- [x] 60,000 토큰 이하 문서에 대해 "none" 반환
- [x] PRD 구조(섹션 헤딩 3개 이상 + 요구사항 번호) 문서 10개 중 9개 이상에서 "hierarchical" 선택 (SC6)
- [x] `pytest tests/test_prd_strategy.py -v` PASS

---

### Task 4: pdf_chunker.py 확장 (--prd 플래그 + MD 지원)

**파일**: `C:\claude\ebs\tools\pdf_chunker.py` (수정)

**추가 로직**:

```
  수정 위치:
  1. argparse에 --prd 플래그 추가
     "--prd: PRD 전용 계층형 청킹 활성화"
     "--strategy: fixed|hierarchical|semantic (기본: auto)"
     "--threshold: 청킹 임계값 (기본: 60000)"

  2. main() 분기 로직:
     if input_path.suffix in ('.md', '.markdown'):
         # MD 파일 처리 경로
         from lib.pdf_utils.md_chunker import MDChunker
         chunker = MDChunker(
             strategy = args.strategy or "auto",
             max_tokens = args.tokens if not args.prd else 8000,
             overlap = args.overlap if not args.prd else 400,
         )
         result = chunker.process(args.input)
     else:
         # 기존 PDF 처리 경로 (변경 없음 — NR3 하위 호환)
         chunker = PDFChunker(...)
         result = chunker.process(args.input)

  3. PRD 모드 JSON 출력 확장:
     if args.prd:
         output["prd_mode"] = True
         output["strategy"] = result.strategy
         output["section_tree"] = result.section_tree
```

**Acceptance Criteria**:
- [x] `python pdf_chunker.py doc.pdf` (기존) → 출력 JSON 형식 변경 없음
- [x] `python pdf_chunker.py doc.md --prd` → PRDChunkResult JSON 출력
- [x] `python pdf_chunker.py doc.md --prd --strategy hierarchical` → Hierarchical 전략 강제 사용
- [x] `python pdf_chunker.py doc.md --info` → 토큰 추정치 + 추천 전략 출력

---

### Task 5: 테스트 작성

**파일**:
- `C:\claude\lib\pdf_utils\tests\test_md_chunker.py` (신규)
- `C:\claude\lib\pdf_utils\tests\test_prd_strategy.py` (신규)

**test_md_chunker.py 케이스**:

```
  TC01: 단순 MD (헤딩 3개, 표 없음) → Fixed 청킹 정상 동작
  TC02: 표 포함 MD → 단일 청크 내 표 분리 없음 (NR2)
  TC03: 코드블록 포함 MD → 코드블록 분리 없음 (NR2)
  TC04: PRD 구조 MD → Hierarchical 청크의 section_path 검증
  TC05: 60,000 토큰 미만 MD → "none" 전략 반환 (전체 텍스트 단일 반환)
  TC06: prev_chunk_id / next_chunk_id 연결 체인 검증 (R8)
  TC07: 하위 호환성 — 기존 Chunk 필드(chunk_id, text, token_count) 누락 없음
  TC08: Windows 경로 (C:\) 및 Unix 경로(/) 모두 처리 (C3)
  TC09: 성능 검증 — 30,000 단어(약 40K 토큰) MD 파일 Hierarchical 청킹이 30초 이내 완료
        (time.perf_counter 기반 assertion, SC4 대응)
```

**test_prd_strategy.py 케이스**:

```
  TC01: 빈 문서 → "none" 반환
  TC02: 50K 토큰 문서 → "none" 반환
  TC03: 70K 토큰 PRD 문서 → "hierarchical" 반환
  TC04: 70K 토큰 비PRD 문서 (표 없음) → "fixed" 반환
  TC05: 120K 토큰 PRD 문서 → "hierarchical+semantic" 반환
  TC06: 표 집중 문서(prd_score < 3) → "semantic" 반환
```

**Acceptance Criteria**:
- [x] `pytest C:\claude\lib\pdf_utils\tests\test_md_chunker.py -v` → 9개 케이스 PASS (TC09 성능 포함)
- [x] `pytest C:\claude\lib\pdf_utils\tests\test_prd_strategy.py -v` → 6개 케이스 PASS
- [x] 기존 테스트 pyc 파일(`test_cli.pyc`, `test_extractor.pyc`, `test_models.pyc`) 소스 부재로 직접 실행 불가. 대신 `ebs/tools/pdf_chunker.py`를 기존 인수(--tokens 4000, --overlap 200)로 실행하여 출력 JSON 형식이 변경 없음을 수동 검증한다.

---

### Task 6: /chunk 커맨드 문서 업데이트

**파일**: `C:\claude\.claude\commands\chunk.md` (수정)

**추가 섹션**:
```
### PRD 모드 (--prd)
/chunk <md_or_pdf_path> --prd                      # 계층형 청킹 (Hierarchical)
/chunk <md_or_pdf_path> --prd --strategy semantic  # PRD + 의미 단위 분할
/chunk <md_or_pdf_path> --prd --strategy fixed     # PRD 메타데이터 + 고정 크기
/chunk <md_or_pdf_path> --prd --preview 3          # 처음 3개 청크 미리보기

### MD 파일 지원
/chunk <path>.md                   # MD 파일 자동 인식
/chunk <path>.md --prd             # MD + PRD 모드
/chunk <path>.md --info            # 토큰 추정 + 추천 전략 출력
```

**Acceptance Criteria**:
- [x] Usage 섹션에 --prd 옵션 추가됨
- [x] MD 파일 지원 명시
- [x] 출력 JSON 구조에 prd_mode/strategy/section_tree 필드 추가됨

---

## 위험 요소 (Risks)

### Risk 1: lib/pdf_utils 소스 파일 부재
- **현황**: `lib/pdf_utils/` 내 .py 소스가 없고 pyc만 존재. 실제 구현체는 `ebs/tools/`에 있음.
- **대응**: 신규 모듈(`md_chunker.py`, `prd_models.py`, `strategy.py`)을 `lib/pdf_utils/`에 직접 생성.  기존 CLI 진입점은 `ebs/tools/pdf_chunker.py`를 수정하여 새 모듈을 import하는 방식으로 연결.
- **리스크**: `lib/pdf_utils`가 패키지로 import 되는지 확인 필요 (`__init__.py` 존재 여부 → pyc만 있어 확인 어려움). 신규 `__init__.py`를 생성하여 명시적으로 패키지화.

### Risk 2: 원자 블록(표/코드) 토큰 초과
- **현황**: 단일 표가 max_tokens(8,000)를 초과할 수 있음.
- **대응**: 원자 블록이 max_tokens를 초과하면 경고 로그를 출력하고 단독 청크로 강제 배출. LLM은 컨텍스트 윈도우 여유 있을 경우 처리 가능하므로 오류보다 경고로 처리.
- **Edge Case 1**: 10,000 토큰짜리 코드블록 → 단독 청크 배출 후 WARNING 출력
- **Edge Case 2**: 헤딩이 없는 순수 표 전용 MD → Semantic 전략 자동 선택

### Risk 3: 기존 `ebs/tools/pdf_chunker.py` 수정 시 하위 호환성 파괴
- **현황**: 기존 `PDFChunker`의 기본 동작(4,000T/200 오버랩)이 `--prd` 플래그 없이는 유지되어야 함(NR3).
- **대응**: 모든 신규 코드는 `args.prd` 조건 분기 안에만 위치. 기존 argparse defaults 변경 금지. 회귀 테스트(TC07) 필수.
- **Edge Case 3**: `pdf_chunker.py --tokens 4000`(명시 지정) 시 --prd와 무관하게 지정값 우선 사용.

### Risk 4: tiktoken 미설치 환경
- **현황**: `TIKTOKEN_AVAILABLE` 플래그로 이미 간이 추정 지원 중.
- **대응**: `strategy.py`의 `estimate_tokens()`도 동일한 폴백 패턴 적용. 간이 추정(문자수 // 3) 시 실제 토큰 수보다 낮게 추정될 수 있으므로, 간이 추정 모드에서는 임계값을 보수적으로 40,000으로 낮춤.

---

## 커밋 전략 (Commit Strategy)

Conventional Commit 형식, 태스크 단위 커밋:

```
feat(pdf_utils): PRD 전용 데이터 모델 추가 (prd_models.py)
feat(pdf_utils): MD 파일 파서 + 4가지 청킹 전략 구현 (md_chunker.py)
feat(pdf_utils): 자동 전략 선택 로직 추가 (strategy.py)
feat(chunk): --prd 플래그 및 MD 파일 지원 추가
test(pdf_utils): MD 청킹 및 전략 선택 단위 테스트 추가
docs(chunk): --prd 옵션 및 MD 파일 지원 문서 업데이트
```

---

## 참조

- PRD: `C:\claude\docs\00-prd\prd-chunking-strategy.prd.md`
- 기존 청커: `C:\claude\ebs\tools\pdf_chunker.py`
- 기존 커맨드: `C:\claude\.claude\commands\chunk.md`
- 테스트 디렉토리: `C:\claude\lib\pdf_utils\tests\`
