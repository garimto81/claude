---
name: chunk
description: PDF 청킹 - 백그라운드 실행으로 안전한 토큰 기반 분할
---

# /chunk - PDF 청킹 커맨드

PDF를 LLM 입력용 토큰 기반 청크로 분할합니다.
**백그라운드 실행**으로 Claude Code 멈춤 현상을 방지합니다.

## Usage

```
/chunk <pdf_path>                    # 기본 청킹 (4000토큰, 200 오버랩)
/chunk <pdf_path> --tokens 2000      # 토큰 수 지정
/chunk <pdf_path> --overlap 100      # 오버랩 지정
/chunk <pdf_path> --info             # PDF 정보만 확인 (빠름)
/chunk <pdf_path> --preview 3        # 처음 3개 청크 미리보기
```

## 핵심: 백그라운드 실행

**문제**: 큰 PDF 처리 시 Claude Code가 멈추는 현상
**해결**: 모든 청킹 작업은 **백그라운드로 실행**

### 실행 방식

1. **정보 확인** (`--info`): 빠른 foreground 실행
2. **청킹 작업**: 반드시 `run_in_background: true`로 실행
3. **결과 확인**: 완료 후 JSON 파일 경로 안내

## Workflow

1. PDF 경로 유효성 검사
2. `--info` 옵션 시: 빠른 정보 출력 (foreground)
3. 청킹 실행: **백그라운드**로 실행
   ```powershell
   python C:\claude\ebs\tools\pdf_chunker.py <pdf_path> -t <tokens> --overlap <overlap> -o <output.json>
   ```
4. 작업 상태 안내
5. 완료 시 JSON 파일 경로 및 요약 출력

## 출력 형식

### 성공 시
```
✅ 청킹 완료: input.pdf
- 청크 수: 15개
- 총 토큰: 45,000
- 출력 파일: C:\claude\...\input.chunks.json

다음 단계:
- JSON 파일을 읽어 청크별로 LLM에 전달하세요
```

### 백그라운드 실행 시
```
🔄 청킹 작업 시작 (백그라운드)
- 입력: large.pdf (120 페이지)
- 예상 청크: ~30개

⏳ 작업 ID: chunk_12345
완료 시 알림이 표시됩니다.
```

## 안전 규칙

1. **120초 타임아웃**: 백그라운드에서도 안전하게
2. **대용량 PDF (100+ 페이지)**: 자동 백그라운드 전환
3. **메모리 관리**: PyMuPDF의 점진적 페이지 처리

## 옵션 상세

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-t, --tokens` | 청크당 최대 토큰 수 | 4000 |
| `--overlap` | 청크 간 오버랩 토큰 수 | 200 |
| `--encoding` | tiktoken 인코딩 (tiktoken 설치 시) | cl100k_base |
| `-o, --output` | 출력 JSON 파일 경로 | `<input>.chunks.json` |
| `--info` | PDF 정보만 출력 (빠름) | - |
| `--preview N` | 처음 N개 청크 미리보기 | - |
| `--quiet` | 진행 메시지 숨기기 | - |

## 스크립트 경로

```
C:\claude\ebs\tools\pdf_chunker.py
```

## 의존성

- **필수**: `pymupdf` (PDF 파싱)
- **선택**: `tiktoken` (정확한 토큰 계산, 없으면 간이 추정 사용)

설치:
```powershell
pip install pymupdf tiktoken
```

## 예제

### 기본 사용
```
/chunk C:\claude\docs\manual.pdf
```

### 토큰 크기 조정
```
/chunk C:\claude\docs\large.pdf --tokens 2000 --overlap 100
```

### 정보 확인 후 청킹
```
/chunk C:\claude\docs\report.pdf --info
/chunk C:\claude\docs\report.pdf --tokens 3000
```

### 미리보기로 확인
```
/chunk C:\claude\docs\test.pdf --preview 5
```

## 출력 JSON 구조

```json
{
  "source_file": "C:\\claude\\docs\\input.pdf",
  "total_pages": 50,
  "total_chars": 120000,
  "total_tokens": 30000,
  "chunk_count": 8,
  "max_tokens_per_chunk": 4000,
  "overlap_tokens": 200,
  "encoding": "cl100k_base",
  "chunks": [
    {
      "chunk_id": 0,
      "text": "...",
      "token_count": 3980,
      "start_page": 1,
      "end_page": 6,
      "char_start": 0,
      "char_end": 15000
    }
  ]
}
```

## Related

- `/research` - 청킹 후 분석 작업
- `/work` - 청킹 기반 자동화 워크플로우
- `/auto` - 자율 반복 모드에서 청킹 활용

## Troubleshooting

### tiktoken 미설치 시
- 간이 토큰 추정 사용 (평균 3자 = 1토큰)
- 정확한 계산이 필요하면: `pip install tiktoken`

### 백그라운드 타임아웃
- 기본 120초 제한
- 초대형 PDF (500+ 페이지)는 청크 크기를 늘려서 실행

### 메모리 부족
- `--tokens` 값을 줄여서 실행 (예: 2000)
- PyMuPDF가 페이지 단위로 처리하므로 대용량도 안전
