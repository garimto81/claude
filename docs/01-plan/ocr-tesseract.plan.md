# OCR Tesseract 정밀 이미지 분석 시스템 설계 계획서

**작성일**: 2026-02-17
**버전**: 1.0.0
**복잡도**: STANDARD (3/5)
**담당**: planner

---

## 1. 배경

### 1.1 현재 상황

C:\claude 프로젝트의 이미지 분석은 현재 **Claude Vision API (Read 도구)**만 사용합니다.

**주요 사용처:**
- `/ai-subtitle` 스킬: PocketBase 사진 → Claude Vision → Phase 분류 → 마케팅 자막 생성
- `/shorts-generator` 스킬: ai-subtitle + FFmpeg 통합 영상 생성
- `lib/mockup_hybrid/`: HTML 와이어프레임 → Playwright 스크린샷 (OCR 불필요)
- `lib/google_docs/`: 이미지 삽입/렌더링 (OCR 불필요)

**Vision API의 한계:**
- 시각적 분석과 맥락 이해는 뛰어나지만 **정밀한 텍스트 추출**에는 제한적
- 작은 글씨, 복잡한 레이아웃, 표/차트의 텍스트 추출 정확도 낮음
- 다국어(한글/영어 혼용) 텍스트 인식 정확도 불안정

### 1.2 요구사항

**Tesseract OCR 통합 목표:**
- 정밀한 텍스트 추출 기능 추가 (작은 글씨, 표, 차트 등)
- Claude Vision과의 **하이브리드 분석** 전략
  - Vision: 시각적 맥락 분석, Phase 분류, 마케팅 자막 생성
  - Tesseract: 정밀 텍스트 추출, 표/차트 데이터 추출
- Windows 11 환경 호환 (C:\claude)
- 한글 OCR 지원 (kor 언어팩)

---

## 2. 구현 범위

### 2.1 새 모듈 생성: `lib/ocr/`

#### 디렉토리 구조

```
lib/ocr/
├── __init__.py                # PDFExtractor 스타일 public API
├── extractor.py               # OCRExtractor 핵심 클래스
├── preprocessor.py            # 이미지 전처리 (grayscale, threshold, deskew)
├── models.py                  # OCRResult, TextRegion, TableDetection
├── errors.py                  # OCRError, TesseractNotFoundError, ImageLoadError
├── cli.py                     # python -m lib.ocr extract <image_path>
├── __main__.py                # CLI 진입점
├── tests/
│   ├── conftest.py
│   ├── test_extractor.py
│   ├── test_preprocessor.py
│   └── test_cli.py
└── README.md
```

#### 핵심 클래스 설계

**OCRExtractor** (lib/pdf_utils/PDFExtractor 패턴 차용)

```python
class OCRExtractor:
    """Tesseract OCR wrapper - pytesseract 기반"""

    def __init__(self, image_path: str, lang: str = "kor+eng"):
        """이미지 로드 및 Tesseract 초기화"""

    def extract_text(self, preprocess: bool = True) -> OCRResult:
        """전체 텍스트 추출 (전처리 옵션)"""

    def extract_regions(self, boxes: List[BBox]) -> List[TextRegion]:
        """특정 영역만 텍스트 추출 (bbox 기반)"""

    def detect_tables(self) -> List[TableDetection]:
        """표 영역 자동 감지 + 텍스트 추출"""

    def get_layout_info(self) -> LayoutInfo:
        """레이아웃 분석 (텍스트 블록, 열, 문단 구조)"""
```

**ImagePreprocessor** (전처리 파이프라인)

```python
class ImagePreprocessor:
    """이미지 전처리 파이프라인 (OpenCV/Pillow)"""

    @staticmethod
    def grayscale(image: Image) -> Image:
        """흑백 변환"""

    @staticmethod
    def threshold(image: Image, method: str = "adaptive") -> Image:
        """이진화 (Otsu, Adaptive Gaussian)"""

    @staticmethod
    def deskew(image: Image) -> Image:
        """기울기 보정"""

    @staticmethod
    def denoise(image: Image) -> Image:
        """노이즈 제거 (Gaussian blur, median filter)"""

    def pipeline(self, image: Image, steps: List[str]) -> Image:
        """전처리 파이프라인 실행"""
```

### 2.2 의존성

**Python 패키지:**

```toml
# pyproject.toml
[tool.poetry.dependencies]
pytesseract = "^0.3.13"         # Tesseract wrapper
Pillow = "^11.0.0"              # 이미지 처리 (이미 존재)
opencv-python = "^4.10.0"       # 이미지 전처리 (이진화, deskew)
numpy = "^2.2.1"                # OpenCV 의존성 (이미 존재)
```

**Tesseract-OCR 바이너리:**

Windows 설치 전략:
1. **Scoop 설치 (권장)**:
   ```powershell
   scoop install tesseract
   ```
2. **수동 설치**:
   - [UB-Mannheim Release](https://github.com/UB-Mannheim/tesseract/wiki) 다운로드
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - PATH 환경변수 추가 또는 pytesseract 설정:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```

**한글 언어팩:**
- `kor.traineddata` 파일 필요 (Tesseract 설치 시 포함)
- 추가 언어: `eng.traineddata` (영어)
- 언어 조합: `lang="kor+eng"` (한글+영어 혼용)

### 2.3 하이브리드 전략

| 시나리오 | Claude Vision | Tesseract OCR |
|---------|--------------|--------------|
| **휠 복원 사진 (ai-subtitle)** | ✅ Phase 분류, 시각적 맥락, 마케팅 자막 | ❌ 불필요 (텍스트 없음) |
| **차량 계기판/에러 메시지** | ✅ 맥락 분석 | ✅ 정밀 텍스트 추출 |
| **문서 스캔 (표/차트 포함)** | ✅ 레이아웃 이해 | ✅ 표 데이터 추출 |
| **작은 글씨 (명함, 영수증)** | ❌ 정확도 낮음 | ✅ 정밀 추출 |
| **손글씨** | ✅ 맥락 이해 | ❌ 인식률 낮음 |

**통합 전략 3단계:**

```python
# Phase 1: Vision으로 맥락 분석
vision_result = claude.read_image("image.jpg", prompt="이미지 설명")

# Phase 2: Tesseract로 정밀 텍스트 추출
ocr_result = OCRExtractor("image.jpg").extract_text(preprocess=True)

# Phase 3: 결과 통합
final_result = {
    "context": vision_result.description,
    "text": ocr_result.text,
    "confidence": ocr_result.confidence,
    "layout": ocr_result.layout_info
}
```

### 2.4 기존 스킬 통합 포인트

#### `/ai-subtitle` 스킬 (확장 가능, 선택적)

**현재 워크플로우:**
```
PocketBase 사진 → Claude Vision → Phase 분류 + 자막 생성
```

**OCR 확장 (선택적):**
- 차량 계기판/에러 메시지 이미지 → Tesseract로 텍스트 추출 → Vision으로 해석
- 예: "엔진 오일 부족" 경고등 → OCR 추출 → 자막 "엔진 오일 점검 필요"

**변경 필요 없음** - 현재 휠 복원 사진은 Vision만으로 충분.

#### `/shorts-generator` 스킬 (확장 가능, 선택적)

**현재 워크플로우:**
```
ai-subtitle 결과 → FFmpeg 영상 합성
```

**OCR 확장 (선택적):**
- 차량 정보 패널 이미지 → Tesseract로 차종/연식 추출 → 자막 생성

**변경 필요 없음** - 기존 워크플로우 유지.

#### 새 스킬: `/ocr-extract` (신규)

**목적:** 문서/차트/표 정밀 텍스트 추출

**사용법:**
```bash
/ocr-extract <image_path>                 # 전체 텍스트 추출
/ocr-extract <image_path> --table         # 표 감지 + 추출
/ocr-extract <image_path> --lang kor+eng  # 언어 지정
/ocr-extract <image_path> --preprocess    # 전처리 활성화
```

**워크플로우:**
1. 이미지 로드 및 전처리
2. Tesseract OCR 실행
3. 결과 포맷팅 (JSON/텍스트)
4. 선택적: Claude Vision으로 맥락 분석

---

## 3. 영향 파일

### 3.1 신규 파일

```
lib/ocr/                              # 새 모듈
├── __init__.py
├── extractor.py
├── preprocessor.py
├── models.py
├── errors.py
├── cli.py
├── __main__.py
├── tests/
│   ├── conftest.py
│   ├── test_extractor.py
│   ├── test_preprocessor.py
│   └── test_cli.py
└── README.md

.claude/skills/ocr-extract/           # 새 스킬
├── SKILL.md
└── scripts/
    └── extract.py                    # OCRExtractor wrapper

docs/02-design/ocr-tesseract.design.md  # 설계 문서
```

### 3.2 수정 파일 (선택적)

**기존 스킬 확장 (선택적):**
- `.claude/skills/ai-subtitle/SKILL.md` - OCR 옵션 추가 (선택적)
- `.claude/skills/shorts-generator/SKILL.md` - OCR 옵션 추가 (선택적)

**문서:**
- `docs/COMMAND_REFERENCE.md` - /ocr-extract 스킬 추가
- `README.md` - OCR 기능 설명 추가

### 3.3 설정 파일

```toml
# pyproject.toml
[tool.poetry.dependencies]
pytesseract = "^0.3.13"
opencv-python = "^4.10.0"

# lib/ocr/.env (Tesseract 경로 오버라이드)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## 4. 위험 요소

### 4.1 Tesseract 설치 복잡성

**위험:**
- Windows 환경에서 Tesseract 바이너리 설치 실패
- 언어팩 누락 (kor.traineddata)
- PATH 설정 오류

**완화 전략:**
1. **설치 검증 스크립트** 제공:
   ```bash
   python -m lib.ocr --check-install  # Tesseract 설치 확인
   ```
2. **Fallback to Vision API**:
   - Tesseract 미설치 시 Claude Vision으로 자동 fallback
   ```python
   if not is_tesseract_installed():
       logger.warning("Tesseract not found, falling back to Vision API")
       return claude.read_image(image_path)
   ```
3. **명확한 설치 가이드** (README.md):
   - Scoop 설치 방법 (1-liner)
   - 수동 설치 + PATH 설정
   - 언어팩 다운로드 링크

### 4.2 한글 OCR 정확도

**위험:**
- Tesseract의 한글 인식률이 Claude Vision보다 낮을 수 있음
- 손글씨/휴대폰 사진 등 저품질 이미지에서 오인식

**완화 전략:**
1. **전처리 파이프라인 최적화**:
   - 이진화 (Adaptive Gaussian Threshold)
   - 기울기 보정 (deskew)
   - 노이즈 제거 (Gaussian blur)
2. **하이브리드 검증**:
   ```python
   ocr_text = tesseract.extract_text(image)
   vision_text = claude.read_image(image, "Extract text")

   # 신뢰도 비교
   if ocr_result.confidence < 0.7:
       return vision_text  # Fallback to Vision
   ```
3. **사용자 피드백 루프**:
   - 오인식 케이스 수집 → 전처리 파라미터 튜닝

### 4.3 PDF vs 이미지 중복

**위험:**
- `lib/pdf_utils/`는 이미 PyMuPDF로 PDF 텍스트 추출 가능
- OCR은 이미지 기반 PDF에서만 필요 (스캔된 PDF)
- 기능 중복 우려

**완화 전략:**
1. **명확한 역할 분리**:
   - `lib/pdf_utils/`: 텍스트 레이어가 있는 PDF (PyMuPDF 직접 추출)
   - `lib/ocr/`: 이미지 파일 + 스캔된 PDF (Tesseract OCR)
2. **PDF OCR 통합**:
   ```python
   # lib/pdf_utils/extractor.py 확장
   def extract_text_with_ocr(self, page_num: int) -> PageText:
       """텍스트 레이어 없으면 OCR 사용"""
       if self._has_text_layer(page_num):
           return self._extract_text_native(page_num)
       else:
           image = self._render_page(page_num)
           return OCRExtractor(image).extract_text()
   ```

### 4.4 성능 (OCR 속도)

**위험:**
- Tesseract OCR은 Claude Vision API보다 느림 (CPU 기반)
- 대량 이미지 처리 시 병목 가능

**완화 전략:**
1. **병렬 처리**:
   ```python
   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor(max_workers=4) as executor:
       results = executor.map(lambda img: OCRExtractor(img).extract_text(), images)
   ```
2. **배치 최적화**:
   - `ai-subtitle`은 이미지당 0.5초 예상 → 20개 이미지 = 10초 (허용 가능)
3. **선택적 사용**:
   - 기본은 Vision API, 정밀 추출 필요시만 Tesseract 사용

---

## 5. 아키텍처 설계 방향

### 5.1 모듈 아키텍처

```
┌─────────────────────────────────────────┐
│         사용자 인터페이스               │
├─────────────────────────────────────────┤
│  /ai-subtitle  │  /ocr-extract  │  CLI  │
├─────────────────────────────────────────┤
│         하이브리드 레이어               │
│  ┌────────────────────────────────────┐ │
│  │  HybridAnalyzer                   │ │
│  │  - vision_analyze()               │ │
│  │  - ocr_extract()                  │ │
│  │  - combine_results()              │ │
│  └────────────────────────────────────┘ │
├──────────────┬──────────────────────────┤
│ Claude Vision│      lib/ocr/            │
│  (Read 도구) │  ┌────────────────────┐  │
│              │  │  OCRExtractor      │  │
│              │  │  - pytesseract     │  │
│              │  └────────────────────┘  │
│              │  ┌────────────────────┐  │
│              │  │  Preprocessor      │  │
│              │  │  - OpenCV/Pillow   │  │
│              │  └────────────────────┘  │
└──────────────┴──────────────────────────┘
```

**HybridAnalyzer** (신규 클래스, 선택적):

```python
class HybridAnalyzer:
    """Claude Vision + Tesseract OCR 하이브리드 분석"""

    def analyze(self, image_path: str, mode: str = "auto") -> AnalysisResult:
        """
        mode:
          - "auto": 이미지 유형 자동 감지 → 최적 도구 선택
          - "vision": Claude Vision만 사용
          - "ocr": Tesseract OCR만 사용
          - "hybrid": 둘 다 실행 + 결과 통합
        """
        if mode == "auto":
            mode = self._detect_best_mode(image_path)

        if mode == "vision":
            return self._vision_analyze(image_path)
        elif mode == "ocr":
            return self._ocr_extract(image_path)
        else:  # hybrid
            vision_result = self._vision_analyze(image_path)
            ocr_result = self._ocr_extract(image_path)
            return self._combine_results(vision_result, ocr_result)
```

### 5.2 데이터 모델

**OCRResult** (models.py):

```python
@dataclass
class OCRResult:
    """Tesseract OCR 결과"""
    text: str                      # 추출된 텍스트
    confidence: float              # 신뢰도 (0.0 ~ 1.0)
    layout_info: LayoutInfo        # 레이아웃 정보
    language: str                  # 감지된 언어
    processing_time: float         # 처리 시간 (초)

@dataclass
class TextRegion:
    """텍스트 영역 (bbox 기반)"""
    text: str
    bbox: BBox                     # (x, y, width, height)
    confidence: float

@dataclass
class TableDetection:
    """표 감지 결과"""
    rows: int
    cols: int
    cells: List[List[str]]         # 2D 배열
    bbox: BBox
```

### 5.3 테스트 전략

#### 단위 테스트

```python
# tests/test_extractor.py
def test_extract_korean_text(sample_korean_image):
    """한글 텍스트 추출 정확도 테스트"""
    extractor = OCRExtractor(sample_korean_image, lang="kor")
    result = extractor.extract_text()

    assert result.confidence > 0.8
    assert "테스트" in result.text

def test_extract_table(sample_table_image):
    """표 감지 및 추출 테스트"""
    extractor = OCRExtractor(sample_table_image)
    tables = extractor.detect_tables()

    assert len(tables) == 1
    assert tables[0].rows == 3
    assert tables[0].cols == 2
```

#### 통합 테스트

```python
# tests/test_hybrid.py
def test_hybrid_analysis(sample_invoice_image):
    """하이브리드 분석 (Vision + OCR) 테스트"""
    analyzer = HybridAnalyzer()
    result = analyzer.analyze(sample_invoice_image, mode="hybrid")

    assert result.vision_context  # Vision으로 분석한 맥락
    assert result.ocr_text        # OCR로 추출한 텍스트
    assert result.confidence > 0.7
```

#### E2E 테스트

```bash
# 실제 사용 시나리오
pytest tests/e2e/test_ai_subtitle_ocr.py -v
```

#### 벤치마크

```python
# tests/benchmark/test_performance.py
def test_ocr_performance():
    """20개 이미지 OCR 처리 시간 측정"""
    images = load_test_images(count=20)

    start = time.time()
    for img in images:
        OCRExtractor(img).extract_text()
    elapsed = time.time() - start

    assert elapsed < 20.0  # 20초 이내 (이미지당 1초)
```

---

## 6. 구현 단계

### Phase 1: 기본 OCR 모듈 구현 (1일)

- [ ] `lib/ocr/extractor.py` - OCRExtractor 클래스
- [ ] `lib/ocr/models.py` - OCRResult, TextRegion 데이터 모델
- [ ] `lib/ocr/errors.py` - 에러 클래스
- [ ] `lib/ocr/__init__.py` - Public API
- [ ] 단위 테스트 (test_extractor.py)

### Phase 2: 이미지 전처리 파이프라인 (0.5일)

- [ ] `lib/ocr/preprocessor.py` - grayscale, threshold, deskew
- [ ] OpenCV 통합
- [ ] 단위 테스트 (test_preprocessor.py)

### Phase 3: CLI 도구 (0.5일)

- [ ] `lib/ocr/cli.py` - argparse 기반 CLI
- [ ] `lib/ocr/__main__.py` - 진입점
- [ ] 통합 테스트 (test_cli.py)

### Phase 4: /ocr-extract 스킬 (0.5일)

- [ ] `.claude/skills/ocr-extract/SKILL.md`
- [ ] `.claude/skills/ocr-extract/scripts/extract.py`
- [ ] E2E 테스트

### Phase 5: 기존 스킬 통합 (선택적, 1일)

- [ ] HybridAnalyzer 클래스 구현
- [ ] `/ai-subtitle` OCR 옵션 추가 (선택적)
- [ ] 통합 테스트

### Phase 6: 문서화 및 설치 가이드 (0.5일)

- [ ] `lib/ocr/README.md`
- [ ] Tesseract 설치 가이드
- [ ] `docs/COMMAND_REFERENCE.md` 업데이트
- [ ] 벤치마크 결과 문서화

**총 예상 시간:** 3~4일 (선택적 통합 포함 시)

---

## 7. 성공 기준

### 7.1 기능 요구사항

- [ ] 한글/영어 혼용 텍스트 추출 (신뢰도 ≥0.8)
- [ ] 표 감지 및 데이터 추출
- [ ] 이미지 전처리 파이프라인 (grayscale, threshold, deskew)
- [ ] CLI 도구 (`python -m lib.ocr extract <image>`)
- [ ] `/ocr-extract` 스킬 작동

### 7.2 성능 요구사항

- [ ] 이미지당 OCR 처리 시간 < 1초 (일반 이미지)
- [ ] 20개 이미지 배치 처리 < 20초
- [ ] 메모리 사용량 < 500MB (대량 처리 시)

### 7.3 품질 요구사항

- [ ] 단위 테스트 커버리지 ≥ 80%
- [ ] 통합 테스트 5개 이상
- [ ] E2E 테스트 2개 이상 (ai-subtitle, ocr-extract)
- [ ] 벤치마크 결과 문서화

### 7.4 문서 요구사항

- [ ] `lib/ocr/README.md` 작성
- [ ] Tesseract 설치 가이드 (Windows)
- [ ] API 문서 (docstring)
- [ ] 사용 예제 3개 이상

---

## 8. 참조

### 8.1 기존 코드

- `lib/pdf_utils/extractor.py` - PDFExtractor 클래스 패턴 참고
- `.claude/skills/ai-subtitle/SKILL.md` - Claude Vision 워크플로우
- `.claude/skills/shorts-generator/SKILL.md` - 이미지 분석 통합

### 8.2 외부 문서

- [Tesseract OCR 공식 문서](https://github.com/tesseract-ocr/tesseract)
- [pytesseract Documentation](https://pypi.org/project/pytesseract/)
- [UB-Mannheim Tesseract Windows](https://github.com/UB-Mannheim/tesseract/wiki)
- [OpenCV Image Preprocessing](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)

### 8.3 관련 이슈

- TBD (구현 중 발견된 이슈 링크)

---

**END OF PLAN**
