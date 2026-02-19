# 설계: PRD/기획서 전용 Chunking 전략

**버전**: 1.0.0 | **작성일**: 2026-02-19 | **기반 계획**: `C:\claude\docs\01-plan\prd-chunking-strategy.plan.md`

---

## 1. 아키텍처 개요

### 1.1 전체 모듈 관계도

```
  입력 파일
  (.md / .markdown / .pdf)
         |
         v
  +------+------+
  |  pdf_chunker.py  |  (C:\claude\ebs\tools\)
  |  [CLI 진입점]    |  argparse: --prd, --strategy, --threshold, --info
  +------+------+
         |
         |  .md / .markdown 분기
         |                            기존 PDF 경로
         v                            (변경 없음, NR3 하위 호환)
  +------+---------+          +------------------+
  |  md_chunker.py  |          |  PDFChunker       |
  |  (MDParser +    |          |  (기존 4000T/200) |
  |   MDChunker)    |          +------------------+
  +---+--+--+--+---+
      |  |  |  |
      |  |  |  +---- strategy.py (자동 전략 선택)
      |  |  |
      |  |  +-------- prd_models.py (PRDChunk, PRDChunkResult)
      |  |
      |  +------------ __init__.py (패키지 공개 API)
      |
      v
  PRDChunkResult
  (JSON 출력)
  +---------------------------------+
  | source_file, total_pages, ...   |
  | prd_mode, strategy, section_tree|  <- PRD 전용 추가 필드
  | chunks: [PRDChunk, ...]         |
  +---------------------------------+
```

### 1.2 데이터 흐름

```
  1. 입력 파일 경로 수신
         |
         v
  2. 토큰 사전 추정 (strategy.estimate_tokens)
         |
         v
  3. 전략 선택
     +---+---+---+---+
     |       |       |
  none   fixed  hier  semantic  hier+semantic
     |       |       |           |
     v       v       v           v
  4. MDParser.parse() 호출
     → Block 목록 생성 (HEADING/TABLE/CODE_BLOCK/LIST/PARAGRAPH)
         |
         v
  5. MDChunker 전략별 분할
     → PRDChunk 목록 생성
         |
         v
  6. prev/next_chunk_id 체인 연결 (후처리)
         |
         v
  7. PRDChunkResult 조립 → JSON 직렬화
         |
         v
  8. 출력 파일 (.chunks.json) 저장
```

---

## 2. 모듈 설계

### 2.1 prd_models.py

**파일 경로**: `C:\claude\lib\pdf_utils\prd_models.py`

#### PRDChunk 클래스

```python
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class PRDChunk:
    """PRD 전용 청크 데이터 구조 (기존 Chunk 필드 완전 포함)"""

    # --- 기존 Chunk 호환 필드 (chunk_id, text, token_count 필수) ---
    chunk_id: int                      # 0-based 순번
    text: str                          # 청크 본문 텍스트
    token_count: int                   # 실제 토큰 수
    start_page: int = 0                # MD면 0 (PDF 호환용)
    end_page: int = 0                  # MD면 0 (PDF 호환용)
    char_start: int = 0                # 원본 텍스트 내 시작 위치
    char_end: int = 0                  # 원본 텍스트 내 종료 위치

    # --- PRD 전용 필드 ---
    section_path: list[str] = field(default_factory=list)
    # 예: ["PRD: PRD/기획서 전용 Chunking 전략", "2. 요구사항 목록", "기능 요구사항"]

    level: int = 0
    # 1=H1, 2=H2, 3=H3, 4=H4+. 0=미분류

    parent_summary: str = ""
    # 상위 섹션 요약 텍스트 (LLM 컨텍스트 유지용)

    prev_chunk_id: Optional[int] = None  # 이전 청크 ID (R8)
    next_chunk_id: Optional[int] = None  # 다음 청크 ID (R8)

    has_table: bool = False   # 표(|---|) 포함 여부
    has_code: bool = False    # 코드블록(```) 포함 여부
    is_atomic: bool = False   # 원자 블록 여부 (표/코드블록 단독 청크)

    def to_dict(self) -> dict:
        """기존 Chunk.to_dict() 필드 포함 전체 직렬화"""
        return asdict(self)
```

#### to_dict() 반환값 예시

```json
{
  "chunk_id": 2,
  "text": "### 기능 요구사항\n\n**R1. 토큰 초과 방지 자동 청킹**\n...",
  "token_count": 412,
  "start_page": 0,
  "end_page": 0,
  "char_start": 1024,
  "char_end": 2840,
  "section_path": ["PRD 문서 제목", "2. 요구사항 목록", "기능 요구사항"],
  "level": 3,
  "parent_summary": "요구사항 목록 섹션의 기능 요구사항 항목",
  "prev_chunk_id": 1,
  "next_chunk_id": 3,
  "has_table": false,
  "has_code": false,
  "is_atomic": false
}
```

#### PRDChunkResult 클래스

```python
@dataclass
class PRDChunkResult:
    """PRD 청킹 결과 메타데이터 (기존 ChunkResult 필드 완전 포함)"""

    # --- 기존 ChunkResult 호환 필드 ---
    source_file: str
    total_pages: int          # MD면 0, PDF면 실제 페이지 수
    total_chars: int
    total_tokens: int
    chunk_count: int
    max_tokens_per_chunk: int
    overlap_tokens: int
    encoding: str
    chunks: list[PRDChunk]

    # --- PRD 전용 추가 필드 (C4: 기존 필드 유지 + 확장) ---
    prd_mode: bool = True
    strategy: str = "fixed"
    # "none" | "fixed" | "hierarchical" | "semantic" | "hierarchical+semantic"

    section_tree: list[dict] = field(default_factory=list)
    # 문서 섹션 트리 (선택적 출력)
    # [{"level": 1, "title": "문서 제목", "children": [...]}, ...]

    def to_dict(self) -> dict:
        result = asdict(self)
        result['chunks'] = [c.to_dict() for c in self.chunks]
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
```

---

### 2.2 md_chunker.py

**파일 경로**: `C:\claude\lib\pdf_utils\md_chunker.py`

#### Block 타입 정의

```python
from enum import Enum, auto

class BlockType(Enum):
    HEADING    = auto()    # # ## ### ####
    TABLE      = auto()    # |---| 패턴 (원자)
    CODE_BLOCK = auto()    # ``` ~ ``` (원자)
    LIST       = auto()    # - * 1. 으로 시작
    PARAGRAPH  = auto()    # 그 외 텍스트
    SEPARATOR  = auto()    # --- (수평선)

@dataclass
class Block:
    type: BlockType
    text: str
    level: int = 0           # HEADING일 때 1~4
    is_atomic: bool = False  # TABLE, CODE_BLOCK은 True
    line_start: int = 0      # 원본 파일 내 시작 줄번호
```

#### MDParser 메서드 스펙

```
MDParser.parse(file_path: str) -> list[Block]

  입력: MD 파일 경로 (pathlib.Path 내부 사용, C3 Windows/Unix 호환)
  출력: Block 목록 (원본 순서 유지)

  처리 순서:
    1. pathlib.Path(file_path).read_text(encoding="utf-8") 로 파일 읽기
    2. 줄 단위 순회
    3. 코드블록 감지: line.strip().startswith("```")
       → 닫는 ``` 까지 전체를 단일 CODE_BLOCK으로 래핑
       → is_atomic=True, type=CODE_BLOCK
    4. 표 감지: line.strip().startswith("|")
       and 다음 1~3줄 이내에 구분선(|---|, |:---|, |---:|) 존재
       → 표 끝까지 전체를 단일 TABLE 블록으로 래핑
       → is_atomic=True, type=TABLE
    5. 헤딩 감지: line.startswith("#")
       → level = line.lstrip('#').count('#') + 1 방식 대신
          level = len(line) - len(line.lstrip('#'))
       → type=HEADING, level=1~4
    6. 목록 감지: line.strip().startswith(("-", "*", "+"))
       or re.match(r'^\d+\.', line.strip())
       → type=LIST
    7. 구분선: line.strip() in ("---", "===", "***")
       → type=SEPARATOR
    8. 나머지: type=PARAGRAPH
```

#### MDChunker 메서드별 입출력 스펙

```
MDChunker.__init__(
    strategy: str = "auto",        # "auto"|"fixed"|"hierarchical"|"semantic"|"hierarchical+semantic"
    max_tokens: int = 8000,        # PRD 기본값 (NR3: PDF 기존값 4000은 변경 없음)
    overlap: int = 400,            # PRD 기본값
    encoding: str = "cl100k_base"
)

MDChunker.chunk_fixed(blocks: list[Block]) -> list[PRDChunk]
  - 입력: Block 목록
  - 출력: PRDChunk 목록
  - 분할 우선순위: HEADING 경계 > SEPARATOR 경계 > PARAGRAPH 경계 > 고정 토큰
  - 원자 블록(TABLE, CODE_BLOCK): 현재 청크에 미포함 시 다음 청크로 이동
  - 원자 블록 토큰 > max_tokens: 단독 청크 강제 배출 + WARNING 출력

MDChunker.chunk_hierarchical(blocks: list[Block]) -> list[PRDChunk]
  - 입력: Block 목록
  - 출력: PRDChunk 목록 (section_path, level 필드 채워짐)
  - 알고리즘: section_stack 기반 (2.2절 Hierarchical 알고리즘 상세 참조)
  - 후처리: prev_chunk_id / next_chunk_id 체인 연결

MDChunker.chunk_semantic(blocks: list[Block]) -> list[PRDChunk]
  - 입력: Block 목록
  - 출력: PRDChunk 목록
  - 분할 기준:
    1. TABLE, CODE_BLOCK → 단독 청크 (is_atomic=True)
    2. 요구사항 번호 변경점 (R\d+|NR\d+|SC\d+) 새 PARAGRAPH 시작 시 경계
    3. 빈 줄 2개 이상 연속 (SEPARATOR 또는 연속 빈 PARAGRAPH)
    4. 목록(LIST) 블록: 논리 그룹(동일 들여쓰기 깊이) 단위로 묶음

MDChunker.process(file_path: str) -> PRDChunkResult
  - 입력: MD 파일 경로
  - 출력: PRDChunkResult
  - 내부 흐름:
    1. MDParser.parse(file_path) → blocks
    2. strategy == "auto" → strategy.auto_select_strategy(file_path) 호출
    3. 전략별 chunk_* 메서드 호출
    4. PRDChunkResult 조립 (section_tree 선택적 생성)
    5. 반환
```

#### Hierarchical 알고리즘 세부 설계

```python
def chunk_hierarchical(self, blocks: list[Block]) -> list[PRDChunk]:
    section_stack = []  # list of Section(level, title, content_blocks, parent_path)
    chunks = []

    for block in blocks:
        if block.type == BlockType.HEADING:
            level = block.level

            # 현재 레벨 이상의 섹션 닫기 (스택 정리)
            while section_stack and section_stack[-1].level >= level:
                closed = section_stack.pop()
                if closed.has_content():
                    parent_path = [s.title for s in section_stack]
                    chunk = self._make_chunk(closed, parent_path, len(chunks))
                    chunks.append(chunk)

            # 현재 헤딩을 새 섹션으로 push
            parent_path = [s.title for s in section_stack]
            section_stack.append(
                Section(level=level, title=block.text.lstrip('#').strip(),
                        parent_path=parent_path)
            )

        elif block.is_atomic:
            # 원자 블록: 절대 분리 금지
            if section_stack:
                section_stack[-1].add_atomic(block)
            else:
                # 헤딩 없는 원자 블록 → 직접 청크화
                chunk = self._atomic_to_chunk(block, len(chunks))
                chunks.append(chunk)

        else:
            if section_stack:
                section_stack[-1].add(block)
            # 헤딩 없는 일반 블록: 미분류 섹션에 추가

    # flush_remaining: 스택 잔여 섹션 닫기
    self._flush_remaining(section_stack, chunks)

    # 토큰 초과 청크 재분할 (원자 블록 제외)
    chunks = self._split_oversized(chunks)

    # prev/next 체인 연결
    self._link_chain(chunks)

    return chunks

def _flush_remaining(self, section_stack, chunks):
    """스택 잔여를 역순으로 닫아 청크화"""
    for section in reversed(section_stack):
        if section.has_content():
            idx = section_stack.index(section)
            parent_path = [s.title for s in section_stack[:idx]]
            chunk = self._make_chunk(section, parent_path, len(chunks))
            chunks.append(chunk)
    section_stack.clear()
```

#### 원자 블록 보호 로직 상세

```
원자 블록 처리 규칙:

  [TABLE 감지]
  조건: line.strip().startswith('|')
        AND 다음 3줄 이내에 re.match(r'\|[\s:]*-+[\s:]*\|', line) 존재

  [CODE_BLOCK 감지]
  조건: line.strip().startswith('```')
        → 닫는 ``` 줄까지 전체 수집

  [분할 시 처리]
  원자 블록 토큰 <= max_tokens:
    → 현재 청크에 들어가지 않으면 다음 청크로 이동 (start_new_chunk)
    → 항상 단독으로 또는 관련 헤딩과 함께 배치

  원자 블록 토큰 > max_tokens:
    → 단독 청크로 강제 배출
    → warnings.warn(f"원자 블록(ID={chunk_id}) max_tokens 초과: {token_count}T")
    → is_atomic=True 마킹

  청크 내 검증:
    has_table  = '|' in text and re.search(r'\|[\s:]*-+', text)
    has_code   = '```' in text
    코드블록 오픈/클로즈 쌍 불일치 → 경고 로그
```

---

### 2.3 strategy.py

**파일 경로**: `C:\claude\lib\pdf_utils\strategy.py`

#### estimate_tokens() 구현 스펙

```python
# tiktoken/간이 추정 분기 (pdf_chunker.py의 TIKTOKEN_AVAILABLE 패턴 동일하게 적용)
try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False

THRESHOLD_CHUNK = 60_000    # 청킹 필요 임계값
THRESHOLD_HIER  = 100_000   # 조합 전략 임계값
THRESHOLD_CHUNK_FALLBACK = 40_000  # tiktoken 미설치 시 보수적 임계값 (Risk 4)

def estimate_tokens(text: str, encoding: str = "cl100k_base") -> int:
    """
    입력: text (str), encoding (str)
    출력: int (추정 토큰 수)

    분기:
      tiktoken 설치됨 → tiktoken.get_encoding(encoding).encode(text) 토큰 수
      미설치        → len(text) // 3  (한글 보수적 추정)

    반환값 활용:
      tiktoken 모드: THRESHOLD_CHUNK(60000) 기준 사용
      간이 추정 모드: THRESHOLD_CHUNK_FALLBACK(40000) 기준 사용
    """
```

#### detect_prd_structure() 점수 계산 로직

```python
def detect_prd_structure(text: str) -> dict:
    """
    입력: text (str) — MD 파일 전체 내용
    출력: dict {
        "prd_score": int,           # 0~5
        "heading_count": int,
        "h2_count": int,
        "has_req_numbers": bool,    # R\d+|NR\d+|SC\d+ 패턴 존재
        "has_table": bool,
        "is_heavy_table": bool      # 표 5개 이상
    }

    점수 계산:
      lines = text.splitlines()

      heading_count = sum(1 for l in lines if l.startswith('#'))
      h2_count      = sum(1 for l in lines if l.startswith('## '))
      has_req       = bool(re.search(r'\b(R\d+|NR\d+|SC\d+)\b', text))
      table_count   = sum(1 for l in lines if re.match(r'\|\s*[-:]+\s*\|', l))

      prd_score = 0
      if heading_count >= 3:    prd_score += 1
      if has_req:               prd_score += 2   # 가중치 2 (가장 강력한 신호)
      if table_count >= 1:      prd_score += 1
      if h2_count >= 2:         prd_score += 1
      # 최대 5점
    """
```

#### auto_select_strategy() 결정 트리

```
  auto_select_strategy(file_path, text=None)
           |
           v
  text 없으면 file_path에서 읽기
           |
           v
  estimate_tokens(text) → token_count
           |
           v
  +--------+--------+
  |                 |
  token_count       token_count
  < THRESHOLD       >= THRESHOLD
  _CHUNK             _CHUNK
  (40K or 60K)          |
  |                     v
  v               detect_prd_structure(text)
  return "none"         → prd_score, has_table, is_heavy_table
                        |
               +--------+--------+--------+
               |                 |        |
          prd_score >= 3   is_heavy_table  token_count
          AND token_count  AND prd_score<3  >= THRESHOLD_HIER
          < THRESHOLD_HIER      |          (100K)
               |                |           |
               v                v           v
          return            return     return
       "hierarchical"     "semantic"  "hierarchical
                                       +semantic"
                               |
                   (위 어느 것도 아니면)
                               v
                          return "fixed"
```

---

### 2.4 pdf_chunker.py 확장

**파일 경로**: `C:\claude\ebs\tools\pdf_chunker.py` (수정)

#### 추가 argparse 인수 목록

```
현재 인수 (변경 없음):
  input, -o/--output, -t/--tokens (기본 4000), --overlap (기본 200),
  --encoding, --info, --preview, --quiet

신규 추가 인수:
  --prd             action="store_true"
                    설명: "PRD 전용 계층형 청킹 활성화 (MD/PDF 모두 지원)"

  --strategy        choices=["auto","fixed","hierarchical","semantic","hierarchical+semantic"]
                    default="auto"
                    설명: "청킹 전략 수동 지정 (기본: auto)"

  --threshold       type=int, default=60000
                    설명: "청킹 자동 전환 임계값 토큰 수 (기본: 60000)"
```

#### MD 파일 분기 로직

```python
def main():
    # ... (기존 argparse 코드) ...

    input_path = Path(args.input)

    # MD 파일 분기 (기존 PDF 경로 완전 분리)
    if input_path.suffix.lower() in ('.md', '.markdown'):
        # MD 처리 경로 (신규)
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # C:\claude
        from lib.pdf_utils.md_chunker import MDChunker

        effective_max_tokens = args.tokens if args.tokens != 4000 else (
            8000 if args.prd else args.tokens
        )
        # 사용자가 -t를 명시하면 그 값 우선 (Edge Case 3, Risk 3)
        # --prd 없이도 MD 파일은 처리 가능

        chunker = MDChunker(
            strategy=args.strategy,
            max_tokens=effective_max_tokens,
            overlap=args.overlap if not args.prd else max(args.overlap, 400),
            encoding=args.encoding
        )

        if args.info:
            # MD 파일 정보 출력 (토큰 추정 + 추천 전략)
            from lib.pdf_utils.strategy import estimate_tokens, auto_select_strategy
            text = input_path.read_text(encoding="utf-8")
            token_count = estimate_tokens(text)
            recommended = auto_select_strategy(str(input_path), text)
            print(f"파일: {args.input}")
            print(f"크기: {input_path.stat().st_size / 1024:.1f} KB")
            print(f"추정 토큰: {token_count:,}")
            print(f"추천 전략: {recommended}")
            return

        result = chunker.process(str(input_path))
        # result는 PRDChunkResult

    else:
        # PDF 처리 경로 (기존 코드 그대로, NR3 하위 호환)
        chunker = PDFChunker(
            max_tokens=args.tokens,
            overlap_tokens=args.overlap,
            encoding=args.encoding
        )
        # ... (기존 info/process 로직 그대로) ...
```

#### PRD 모드 JSON 출력 확장 스펙

```
기존 JSON 출력 필드 (변경 없음, C4):
  source_file, total_pages, total_chars, total_tokens,
  chunk_count, max_tokens_per_chunk, overlap_tokens, encoding, chunks

PRD 전용 추가 필드 (--prd 또는 MD 파일일 때):
  prd_mode: true
  strategy: "hierarchical"  (실제 사용된 전략)
  section_tree: [           (문서 섹션 트리)
    {
      "level": 1,
      "title": "PRD 문서 제목",
      "children": [
        {"level": 2, "title": "1. 배경", "children": []},
        {"level": 2, "title": "2. 요구사항", "children": [
          {"level": 3, "title": "기능 요구사항", "children": []}
        ]}
      ]
    }
  ]

chunks 배열 내 각 청크:
  기존 필드: chunk_id, text, token_count, start_page, end_page, char_start, char_end
  PRD 추가:  section_path, level, parent_summary, prev_chunk_id, next_chunk_id,
             has_table, has_code, is_atomic
```

---

## 3. 인터페이스 정의 (I/O 스펙)

### 3.1 CLI 입출력 예시

```bash
# [1] 기존 PDF (변경 없음 — NR3)
python pdf_chunker.py input.pdf
python pdf_chunker.py input.pdf -t 4000 --overlap 200

# [2] MD 파일 기본 (자동 전략)
python pdf_chunker.py doc.md

# [3] MD 파일 + PRD 모드 (Hierarchical 전략 기본)
python pdf_chunker.py doc.md --prd

# [4] 전략 수동 지정
python pdf_chunker.py doc.md --prd --strategy hierarchical
python pdf_chunker.py doc.md --prd --strategy semantic
python pdf_chunker.py doc.md --prd --strategy fixed

# [5] 정보 출력 (토큰 추정 + 추천 전략)
python pdf_chunker.py doc.md --info

# [6] 미리보기
python pdf_chunker.py doc.md --prd --preview 3

# [7] 출력 파일 지정
python pdf_chunker.py doc.md --prd -o output.chunks.json
```

### 3.2 JSON 출력 형식 전체 스키마

```json
{
  "source_file": "C:\\claude\\docs\\00-prd\\prd-chunking-strategy.prd.md",
  "total_pages": 0,
  "total_chars": 12480,
  "total_tokens": 3210,
  "chunk_count": 8,
  "max_tokens_per_chunk": 8000,
  "overlap_tokens": 400,
  "encoding": "cl100k_base",
  "prd_mode": true,
  "strategy": "hierarchical",
  "section_tree": [
    {
      "level": 1,
      "title": "PRD: PRD/기획서 전용 Chunking 전략",
      "children": [
        {
          "level": 2,
          "title": "1. 배경 및 목적",
          "children": [
            {"level": 3, "title": "1.1 배경", "children": []},
            {"level": 3, "title": "1.2 목적", "children": []}
          ]
        },
        {
          "level": 2,
          "title": "2. 요구사항 목록",
          "children": [
            {"level": 3, "title": "기능 요구사항", "children": []},
            {"level": 3, "title": "비기능 요구사항", "children": []}
          ]
        }
      ]
    }
  ],
  "chunks": [
    {
      "chunk_id": 0,
      "text": "# PRD: PRD/기획서 전용 Chunking 전략\n\n**버전**: 1.0.0 ...",
      "token_count": 156,
      "start_page": 0,
      "end_page": 0,
      "char_start": 0,
      "char_end": 612,
      "section_path": ["PRD: PRD/기획서 전용 Chunking 전략"],
      "level": 1,
      "parent_summary": "",
      "prev_chunk_id": null,
      "next_chunk_id": 1,
      "has_table": false,
      "has_code": false,
      "is_atomic": false
    },
    {
      "chunk_id": 3,
      "text": "| 요구사항 | 우선순위 | 이유 |\n|---------|---------|------|\n...",
      "token_count": 284,
      "start_page": 0,
      "end_page": 0,
      "char_start": 4200,
      "char_end": 5380,
      "section_path": ["PRD 문서 제목", "5. 우선순위"],
      "level": 2,
      "parent_summary": "우선순위 섹션",
      "prev_chunk_id": 2,
      "next_chunk_id": 4,
      "has_table": true,
      "has_code": false,
      "is_atomic": true
    }
  ]
}
```

---

## 4. 테스트 설계

### 4.1 test_md_chunker.py (TC01~TC09)

**파일 경로**: `C:\claude\lib\pdf_utils\tests\test_md_chunker.py`

```
TC01: 단순 MD (헤딩 3개, 표 없음) → Fixed 청킹 정상 동작
  입력: 헤딩 3개, 단락 5개, 총 2000 토큰 MD
  기대: 청크 수 >= 1, 각 청크 token_count <= 8000
  검증: result.strategy == "fixed" (또는 "none")

TC02: 표 포함 MD → 단일 청크 내 표 분리 없음 (NR2)
  입력: 표(|---|) 3개 포함, 총 3000 토큰 MD
  기대: 각 청크에서 코드 ```"| ... |---| ..."``` 패턴이 청크 경계에 분리되지 않음
  검증:
    for chunk in result.chunks:
        if chunk.has_table:
            # |---| 가 chunk.text 안에 완전히 포함
            assert '|---' in chunk.text or '|:---' in chunk.text

TC03: 코드블록 포함 MD → 코드블록 분리 없음 (NR2)
  입력: ``` 코드블록 2개 포함 MD
  기대: 각 청크에서 ``` 오픈/클로즈 쌍이 짝수 개 (0, 2, 4...)
  검증:
    for chunk in result.chunks:
        assert chunk.text.count('```') % 2 == 0

TC04: PRD 구조 MD → Hierarchical 청크의 section_path 검증
  입력: H1 1개 + H2 3개 + H3 각 2개 포함 PRD 구조 MD
  기대: H3 레벨 청크의 section_path 길이 >= 3
  검증:
    h3_chunks = [c for c in result.chunks if c.level == 3]
    for c in h3_chunks:
        assert len(c.section_path) >= 3

TC05: 60,000 토큰 미만 MD → "none" 전략 반환 (전체 텍스트 단일 반환)
  입력: 총 토큰 < 60000인 MD 파일 (모킹 또는 실제 작은 파일)
  기대: result.strategy == "none", result.chunk_count == 1
  검증: len(result.chunks) == 1

TC06: prev_chunk_id / next_chunk_id 연결 체인 검증 (R8)
  입력: 청크 4개 이상 생성되는 MD (Hierarchical)
  기대: chunk[0].prev_chunk_id is None
        chunk[0].next_chunk_id == 1
        chunk[-1].next_chunk_id is None
        모든 중간 청크의 prev/next 연결 일관성
  검증:
    for i, chunk in enumerate(result.chunks):
        if i > 0:
            assert chunk.prev_chunk_id == i - 1
        if i < len(result.chunks) - 1:
            assert chunk.next_chunk_id == i + 1

TC07: 하위 호환성 — 기존 Chunk 필드(chunk_id, text, token_count) 누락 없음
  입력: 임의 MD 파일
  기대: 모든 청크에 chunk_id, text, token_count 필드 존재
  검증:
    for chunk in result.chunks:
        d = chunk.to_dict()
        assert "chunk_id" in d
        assert "text" in d
        assert "token_count" in d

TC08: Windows/Unix 경로 모두 처리 (C3)
  입력:
    - Windows 경로: r"C:\claude\docs\test.md"
    - Unix 경로: "/tmp/test.md" (또는 동일 파일을 Path로 접근)
  기대: FileNotFoundError 없이 정상 처리 (파일 실제 존재 시)
  검증: pathlib.Path(path).exists() 확인 후 처리

TC09: 성능 검증 — 30,000단어(약 40K 토큰) MD Hierarchical 청킹이 30초 이내
  입력: 30,000 단어 분량 MD 파일 (픽스처로 생성)
  기대: 처리 시간 <= 30초 (SC4 대응)
  검증:
    import time
    start = time.perf_counter()
    result = chunker.process(large_md_path)
    elapsed = time.perf_counter() - start
    assert elapsed <= 30.0, f"청킹 시간 초과: {elapsed:.2f}초"
```

### 4.2 test_prd_strategy.py (TC01~TC06)

**파일 경로**: `C:\claude\lib\pdf_utils\tests\test_prd_strategy.py`

```
TC01: 빈 문서 → "none" 반환
  입력: text = ""
  기대: auto_select_strategy(path, "") == "none"

TC02: 50K 토큰 문서 → "none" 반환
  입력: 50,000 토큰 분량 텍스트 (모킹: estimate_tokens 반환값 패치)
  기대: "none"

TC03: 70K 토큰 PRD 문서 → "hierarchical" 반환
  입력: 70,000 토큰, prd_score >= 3 (헤딩 3개 + R1/NR1 패턴 포함)
  기대: "hierarchical"

TC04: 70K 토큰 비PRD 문서 (표 없음, 헤딩 1개) → "fixed" 반환
  입력: 70,000 토큰, prd_score <= 2
  기대: "fixed"

TC05: 120K 토큰 PRD 문서 → "hierarchical+semantic" 반환
  입력: 120,000 토큰, prd_score >= 3
  기대: "hierarchical+semantic"

TC06: 표 집중 문서(prd_score < 3, is_heavy_table=True) → "semantic" 반환
  입력: 70,000 토큰, 표 5개 이상, 헤딩 1개, 요구사항 번호 없음
  기대: "semantic"
```

### 4.3 test_prd_models.py

**파일 경로**: `C:\claude\lib\pdf_utils\tests\test_prd_models.py`

```
TM01: PRDChunk.to_dict() 기존 Chunk 필드 포함 검증
  검증: chunk_id, text, token_count, start_page, end_page, char_start, char_end 존재

TM02: PRDChunk.to_dict() PRD 전용 필드 포함 검증
  검증: section_path, level, parent_summary, prev_chunk_id,
        next_chunk_id, has_table, has_code, is_atomic 존재

TM03: PRDChunkResult.to_dict() 기존 ChunkResult 필드 포함 검증
  검증: source_file, total_pages, chunk_count, chunks 배열 존재 (C4)

TM04: PRDChunkResult.to_dict() PRD 전용 필드 포함 검증
  검증: prd_mode, strategy, section_tree 존재

TM05: PRDChunkResult.to_json() 유효한 JSON 반환
  검증: json.loads(result.to_json()) 예외 없음

TM06: section_path 기본값 빈 리스트
  검증: PRDChunk(chunk_id=0, text="t", token_count=1).section_path == []
```

---

## 5. 위험 요소 및 완화 전략

### Risk 1: lib/pdf_utils 소스 파일 부재

**문제**: `lib/pdf_utils/`에 .py 소스 없음, pyc만 존재.

**완화 코드**:
```python
# lib/pdf_utils/__init__.py (신규 생성)
"""
lib.pdf_utils 패키지 초기화.

기존 pyc 모듈(extractor, models 등)과 신규 PRD 모듈을 병행 제공.
신규 모듈: md_chunker, prd_models, strategy
"""
try:
    from .md_chunker import MDChunker, MDParser
    from .prd_models import PRDChunk, PRDChunkResult
    from .strategy import auto_select_strategy, estimate_tokens
except ImportError:
    pass  # 선택적 임포트 (기존 사용자 보호)
```

**검증**: `python -c "from lib.pdf_utils import MDChunker"` 성공 확인.

### Risk 2: 원자 블록 토큰 초과

**문제**: 단일 표/코드블록이 max_tokens(8000)를 초과할 수 있음.

**완화 코드**:
```python
import warnings

def _split_oversized(self, chunks: list[PRDChunk]) -> list[PRDChunk]:
    result = []
    for chunk in chunks:
        if chunk.token_count > self.max_tokens:
            if chunk.is_atomic:
                # 원자 블록은 분할 불가 → 경고 후 단독 배출
                warnings.warn(
                    f"원자 블록(chunk_id={chunk.chunk_id}) 토큰 초과: "
                    f"{chunk.token_count}T > {self.max_tokens}T. "
                    f"단독 청크로 강제 배출.",
                    UserWarning,
                    stacklevel=2
                )
                result.append(chunk)
            else:
                # 비원자 블록: 재분할 (Fixed-size 폴백)
                sub_chunks = self._fixed_split_text(chunk)
                result.extend(sub_chunks)
        else:
            result.append(chunk)
    return result
```

### Risk 3: 기존 pdf_chunker.py 하위 호환성 파괴

**문제**: 신규 코드가 기존 동작을 변경할 수 있음.

**완화 설계**:
```
수정 원칙:
  1. 모든 신규 코드는 args.prd 또는 MD 파일 분기 내에만 위치
  2. 기존 argparse 기본값 변경 금지:
     -t/--tokens default=4000  (유지)
     --overlap default=200     (유지)
  3. 기존 PDFChunker 클래스 코드 변경 없음
  4. 기존 Chunk, ChunkResult 클래스 변경 없음

검증 (TC07 대응):
  python pdf_chunker.py doc.pdf -t 4000 --overlap 200
  → JSON에 prd_mode 필드 없음, 기존 형식 유지
```

### Risk 4: tiktoken 미설치 환경

**문제**: 간이 추정(// 3)은 실제 토큰보다 낮게 추정 → 청킹 누락 위험.

**완화 코드**:
```python
def estimate_tokens(text: str, encoding: str = "cl100k_base") -> int:
    if _TIKTOKEN_AVAILABLE:
        try:
            enc = tiktoken.get_encoding(encoding)
            return len(enc.encode(text))
        except Exception:
            pass

    # 간이 추정 모드: 보수적 계산 (3자 = 1토큰)
    return len(text) // 3

def _get_threshold() -> int:
    """tiktoken 미설치 시 보수적 임계값 반환"""
    return THRESHOLD_CHUNK if _TIKTOKEN_AVAILABLE else THRESHOLD_CHUNK_FALLBACK
    # THRESHOLD_CHUNK = 60_000, THRESHOLD_CHUNK_FALLBACK = 40_000
```

---

## 6. 구현 체크리스트

```
신규 파일 생성:
  [ ] C:\claude\lib\pdf_utils\__init__.py        (패키지 초기화)
  [ ] C:\claude\lib\pdf_utils\prd_models.py      (PRDChunk, PRDChunkResult)
  [ ] C:\claude\lib\pdf_utils\md_chunker.py      (MDParser, MDChunker)
  [ ] C:\claude\lib\pdf_utils\strategy.py        (auto_select_strategy 등)

기존 파일 수정:
  [ ] C:\claude\ebs\tools\pdf_chunker.py         (--prd 플래그 + MD 분기)

테스트 파일 작성:
  [ ] C:\claude\lib\pdf_utils\tests\test_md_chunker.py   (TC01~TC09)
  [ ] C:\claude\lib\pdf_utils\tests\test_prd_strategy.py (TC01~TC06)
  [ ] C:\claude\lib\pdf_utils\tests\test_prd_models.py   (TM01~TM06)

문서 업데이트:
  [ ] C:\claude\.claude\commands\chunk.md        (--prd 옵션 추가, MD 지원 안내)
```

---

## 참조

- PRD: `C:\claude\docs\00-prd\prd-chunking-strategy.prd.md`
- 계획: `C:\claude\docs\01-plan\prd-chunking-strategy.plan.md`
- 기존 청커: `C:\claude\ebs\tools\pdf_chunker.py`
- 기존 커맨드: `C:\claude\.claude\commands\chunk.md`
- 테스트 디렉토리: `C:\claude\lib\pdf_utils\tests\`

---

## Changelog

- v1.0.0 (2026-02-19): 최초 작성 — PRD/기획서 전용 Chunking 전략 설계 문서 초안
