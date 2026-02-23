# PRD: OCR 3-Layer Hybrid Pipeline

**버전**: 1.0.0 | **작성일**: 2026-02-23 | **상태**: Draft

---

## 목차

1. [배경 및 목적](#1-배경-및-목적)
2. [기능 요구사항](#2-기능-요구사항)
3. [기능 범위](#3-기능-범위)
4. [비기능 요구사항](#4-비기능-요구사항)
5. [제약사항](#5-제약사항)
6. [우선순위](#6-우선순위)
7. [구현 대상 파일](#7-구현-대상-파일)
8. [의존성](#8-의존성)

---

## 1. 배경 및 목적

### 1.1 문제 정의

단일 Vision API(Claude Vision 등)는 이미지 내 UI 요소의 픽셀 좌표를 공식적으로 부정확하게 측정한다. Vision LLM은 의미론적 이해에 강점이 있으나, 정밀한 픽셀 좌표 추출에는 구조적 한계가 있다.

기존 `lib/ocr/` 구현은:
- Tesseract `image_to_data()`로 텍스트 BBox + 신뢰도 추출 (구현 완료)
- `ImagePreprocessor`로 OpenCV + Pillow 전처리 파이프라인 (구현 완료)
- `detect_tables()`에서 `cv2.Canny + HoughLinesP` 기반 선 감지 (부분 구현)
- 비텍스트 요소(버튼, 아이콘, 이미지 등) 감지: **미구현**
- Set-of-Mark(SoM) 프롬프팅: **미구현**
- 파이프라인 통합 오케스트레이터: **미구현**

### 1.2 목적

기존 코드베이스를 기반으로 완전한 3-Layer Hybrid Pipeline을 구현하여:

1. **정밀 좌표**: OpenCV `findContours()`로 비텍스트 UI 요소의 픽셀 BBox 추출
2. **텍스트 정밀도**: Tesseract OCR로 텍스트 요소 BBox + 신뢰도 추출 (기존 재사용)
3. **시맨틱 레이블**: Set-of-Mark 프롬프팅으로 Vision LLM이 좌표 추정 대신 번호 기반 의미 분류 수행

### 1.3 기대 효과

- UI 요소의 픽셀 좌표 정확도 향상 (OpenCV 기반, 서브픽셀 정밀도)
- 텍스트/비텍스트 요소를 통합한 완전한 UI 레이아웃 분석
- Vision LLM의 강점(의미 해석)을 좌표 추정이 아닌 시맨틱 분류에 집중
- CLI 옵션 (`--coords`, `--ui`, `--mode hybrid`) 추가로 기존 워크플로우와 통합

---

## 2. 기능 요구사항

### Layer 1: 비텍스트 요소 감지 (graphic_detector.py)

**FR-1** `cv2.findContours()`를 사용하여 이미지 내 비텍스트 요소(버튼, 아이콘, 이미지 블록, 입력 필드, 구분선 등)의 외곽 컨투어를 감지한다.

**FR-2** 감지된 컨투어로부터 픽셀 BBox (`x, y, width, height`) 를 추출하며, 좌표는 원본 이미지의 픽셀 단위로 정확히 제공한다.

**FR-3** 최소 면적 임계값(`min_area`) 필터링을 통해 노이즈성 소형 컨투어를 제거한다. 기본값은 500px².

**FR-4** 컨투어 근사화(`cv2.approxPolyDP`)를 적용하여 다각형 형태의 UI 요소를 직사각형 BBox로 정규화한다.

**FR-5** 감지된 요소를 `UIElement` 데이터 모델로 반환하며, `element_type`은 감지 단계에서 `"graphic"`으로 표시한다 (시맨틱 레이블은 Layer 3에서 부여).

**FR-6** Tesseract로 이미 감지된 텍스트 BBox 영역과 중복되는 컨투어는 필터링 처리하여 Layer 1과 Layer 2 결과 간 중복을 방지한다.

### Layer 2: 텍스트 요소 BBox 추출 (기존 extractor.py 재사용)

**FR-7** 기존 `OCRExtractor.extract_text()`의 `image_to_data()` 결과를 재사용하여 텍스트 요소의 BBox + 신뢰도를 추출한다. 신규 구현 없이 기존 코드 호출.

**FR-8** 신뢰도 임계값(`confidence_threshold`) 미만의 텍스트 결과는 파이프라인에서 제외한다. 기본값 0.5.

**FR-9** 텍스트 요소는 `UIElement` 모델로 변환되며 `element_type="text"`로 표시된다.

### Layer 3: Set-of-Mark(SoM) 시맨틱 레이블링 (som_annotator.py)

**FR-10** Layer 1 + Layer 2 결과의 각 요소에 고유 번호 마커를 이미지에 시각적으로 삽입한다. 마커는 OpenCV로 원본 이미지에 오버레이하며, 번호는 각 BBox 좌상단에 표시한다.

**FR-11** 마커가 삽입된 어노테이션 이미지를 Vision LLM(Claude Vision)에 전달하고, "각 번호의 요소가 무엇인지 시맨틱 레이블을 부여하라"는 SoM 프롬프트를 함께 제공한다. 좌표 추정을 LLM에 요청하지 않는다.

**FR-12** Vision LLM 응답에서 `{번호: 레이블}` 매핑을 파싱하여 각 `UIElement`의 `semantic_label` 필드를 업데이트한다.

**FR-13** Vision LLM API 호출 실패 시 `semantic_label="unknown"`으로 처리하고, 파이프라인은 중단 없이 Layer 1+2 결과만 반환한다.

### 파이프라인 통합 (hybrid_pipeline.py)

**FR-14** `HybridPipeline` 클래스는 Layer 1→2→3을 순서대로 실행하는 통합 오케스트레이터를 제공한다.

**FR-15** `run(image_path, mode)` 메서드를 제공하며, `mode` 파라미터로 실행 범위를 제어한다:
- `"coords"`: Layer 1+2만 (좌표 추출, LLM 호출 없음)
- `"ui"`: Layer 1+2+3 전체 (시맨틱 레이블 포함)
- `"hybrid"`: `"ui"`와 동일 (기본값)

**FR-16** `HybridAnalysisResult` 모델을 반환하며, 모든 `UIElement` 리스트, 어노테이션 이미지 경로, 처리 시간, 각 레이어 실행 통계를 포함한다.

### CLI 통합 (10-image-analysis.md 업데이트)

**FR-17** `--coords` 옵션: `mode="coords"` 실행 (Layer 1+2, LLM 호출 없음, 빠름).

**FR-18** `--ui` 옵션: `mode="ui"` 실행 (Layer 1+2+3, 시맨틱 레이블 포함).

**FR-19** `--mode hybrid` 옵션: `--ui`와 동일한 동작. 기존 `--mode` 패턴 일관성 유지.

**FR-20** 기존 `--table`, `--preset` 옵션과 새 옵션은 독립적으로 동작하며 병렬 조합이 가능하다.

---

## 3. 기능 범위

### In Scope

| 항목 | 설명 |
|------|------|
| `graphic_detector.py` | `cv2.findContours()` 기반 비텍스트 요소 BBox 추출 신규 구현 |
| `som_annotator.py` | SoM 마커 삽입 + Vision LLM 시맨틱 레이블링 신규 구현 |
| `hybrid_pipeline.py` | 3-Layer 통합 오케스트레이터 신규 구현 |
| `models.py` 확장 | `UIElement`, `HybridAnalysisResult` 데이터 모델 추가 |
| `10-image-analysis.md` 업데이트 | `--coords` / `--ui` / `--mode hybrid` 옵션 문서 추가 |
| 기존 코드 재사용 | `OCRExtractor.extract_text()`, `ImagePreprocessor` 변경 없이 호출 |
| 중복 필터링 | Layer 1, 2 결과 간 BBox 중복 제거 로직 |
| Fallback 처리 | Vision LLM 실패 시 Layer 1+2 결과만 반환 |

### Out of Scope

| 항목 | 제외 이유 |
|------|-----------|
| Vision LLM 좌표 추정 | SoM의 핵심 원칙: LLM에 좌표 요청 금지 |
| 실시간 스트리밍 처리 | 정적 이미지 파일 처리에 집중 |
| GPU 가속 (CUDA) | CPU 기반 OpenCV로 충분 (성능 NFR 참조) |
| 웹 API 엔드포인트 | CLI 통합만 대상 |
| 다중 이미지 배치 처리 | 단일 이미지 파이프라인만 구현 (배치는 호출 측 책임) |
| UI 요소 분류 모델 학습 | SoM 방식으로 Vision LLM 활용, 별도 ML 모델 학습 없음 |
| 기존 `extractor.py` 수정 | Layer 2는 기존 코드 재사용으로 충분 |
| `preprocessor.py` 수정 | 기존 전처리 파이프라인 그대로 사용 |

---

## 4. 비기능 요구사항

### 성능 (NFR-P)

**NFR-P1** Layer 1 (`graphic_detector`): 1920×1080 이미지 기준 처리 시간 **3초 이내** (CPU 기준).

**NFR-P2** Layer 2 (`OCRExtractor.extract_text`): 기존 성능 기준 유지. 변경 없음.

**NFR-P3** Layer 3 (`som_annotator`): Vision LLM API 응답 대기 포함 **30초 이내**. API 타임아웃은 20초로 설정.

**NFR-P4** 전체 파이프라인 (`HybridPipeline.run`): `mode="coords"` 기준 **5초 이내**, `mode="ui"` 기준 **35초 이내**.

### 정확도 (NFR-A)

**NFR-A1** Layer 1 BBox 정확도: 1920×1080 이미지에서 크기 30×30px 이상의 UI 요소를 **85% 이상** 감지 (재현율 기준).

**NFR-A2** Layer 1 좌표 오차: 감지된 BBox의 픽셀 좌표 오차 **±5px 이내**.

**NFR-A3** Layer 2 텍스트 신뢰도: 기존 `OCRExtractor` 기준 유지. 신뢰도 0.5 미만 결과는 필터링.

**NFR-A4** Layer 3 SoM 레이블 정확도: 명확한 UI 요소(버튼, 레이블, 입력 필드)에 대해 **80% 이상** 정확한 시맨틱 레이블 부여 목표.

### 의존성 (NFR-D)

**NFR-D1** Python 패키지: `opencv-python>=4.5`, `pytesseract>=0.3`, `Pillow>=9.0`, `numpy>=1.21`

**NFR-D2** Vision LLM: Claude Vision API (`anthropic` 패키지). API 키는 환경변수 또는 `lib/ai_auth/` 인증 흐름 활용.

**NFR-D3** Tesseract: 기존 요구사항 유지 (v5.0+, kor+eng 언어팩).

**NFR-D4** 신규 의존성 추가 금지: 위 패키지 외 신규 pip 패키지를 추가하지 않는다. 모두 기존 환경에서 사용 가능.

### 코드 품질 (NFR-Q)

**NFR-Q1** 기존 `lib/ocr/` 코드 아키텍처 패턴 준수: dataclass 모델, 명시적 타입 힌트, Private 메서드 `_` 접두사.

**NFR-Q2** 각 신규 파일은 TDD 원칙에 따라 `tests/test_ocr_hybrid_*.py` 테스트 파일과 함께 구현한다.

**NFR-Q3** `__init__.py`에 신규 공개 API (`HybridPipeline`, `UIElement`, `HybridAnalysisResult`) 노출.

---

## 5. 제약사항

| # | 제약사항 | 근거 |
|---|---------|------|
| C-1 | 기존 `extractor.py`, `preprocessor.py`, `models.py` (기존 클래스)는 **수정하지 않는다**. 확장만 허용 (`models.py`에 신규 dataclass 추가). | 기존 API 호환성 유지. `OCRResult`, `BBox` 등 기존 모델 참조 코드 보호. |
| C-2 | Vision LLM에 픽셀 좌표 추정을 요청하는 프롬프트를 생성하지 않는다. | SoM의 핵심 원칙. 좌표는 항상 OpenCV/Tesseract가 제공. |
| C-3 | `lib/ai_auth/` 모듈의 인증 흐름을 우선 사용한다. API 키 하드코딩 절대 금지. | CLAUDE.md 전역 규칙: "API 키 방식 절대 사용 금지, Browser OAuth만 허용" |
| C-4 | 어노테이션 임시 이미지는 `C:\claude\lib\ocr\tmp\` 디렉토리에 저장하며, 파이프라인 완료 후 자동 정리한다. | 디스크 공간 관리. |
| C-5 | OpenCV `findContours()`는 `RETR_EXTERNAL` + `CHAIN_APPROX_SIMPLE` 모드로 고정한다. | 외부 컨투어만 대상으로 하여 중첩 요소 오감지 방지. |
| C-6 | `HybridPipeline`은 `lib/ocr/__init__.py`의 공개 API를 통해서만 외부에 노출한다. 직접 모듈 임포트 패턴을 강제하지 않는다. | 기존 `lib/ocr` 패키지 캡슐화 패턴 준수. |

---

## 6. 우선순위

MoSCoW 방식 적용.

### Must Have (필수)

| FR | 설명 |
|----|------|
| FR-1, FR-2 | `graphic_detector.py` — `findContours()` + BBox 추출 |
| FR-3, FR-4 | 노이즈 필터링 + 다각형 BBox 정규화 |
| FR-5 | `UIElement` 모델 (Layer 1 결과) |
| FR-7, FR-8, FR-9 | Layer 2: 기존 OCR 재사용 + `UIElement` 변환 |
| FR-14, FR-15, FR-16 | `HybridPipeline` 오케스트레이터 + `HybridAnalysisResult` |
| FR-17 | `--coords` CLI 옵션 |

### Should Have (중요)

| FR | 설명 |
|----|------|
| FR-6 | Layer 1/2 BBox 중복 필터링 |
| FR-10, FR-11, FR-12 | `som_annotator.py` SoM 마커 삽입 + LLM 레이블링 |
| FR-13 | Vision LLM 실패 시 Fallback |
| FR-18, FR-19 | `--ui`, `--mode hybrid` CLI 옵션 |

### Could Have (선택)

| FR | 설명 |
|----|------|
| FR-20 | 기존 `--table`, `--preset` 옵션과 새 옵션 병렬 조합 |

### Won't Have (이번 구현 제외)

- GPU 가속, 배치 처리, 웹 API 엔드포인트 (Out of Scope 참조)

---

## 7. 구현 대상 파일

```
C:\claude\lib\ocr\
├── graphic_detector.py   [신규] cv2.findContours() 기반 비텍스트 요소 감지
│                               GraphicDetector 클래스
│                               detect_elements(image) → List[UIElement]
│
├── som_annotator.py      [신규] Set-of-Mark 어노테이션
│                               SomAnnotator 클래스
│                               annotate(image, elements) → 어노테이션 이미지
│                               label_with_vision(annotated_image, elements) → List[UIElement]
│
├── hybrid_pipeline.py    [신규] 3-Layer 통합 오케스트레이터
│                               HybridPipeline 클래스
│                               run(image_path, mode) → HybridAnalysisResult
│
├── models.py             [확장] 신규 dataclass 추가 (기존 클래스 수정 없음)
│                               UIElement (element_type, bbox, semantic_label, confidence, layer)
│                               HybridAnalysisResult (elements, annotated_image_path,
│                                                      processing_time, layer_stats)
│
└── __init__.py           [확장] 신규 공개 API 노출
                                HybridPipeline, UIElement, HybridAnalysisResult 추가

C:\claude\.claude\rules\
└── 10-image-analysis.md  [업데이트] --coords / --ui / --mode hybrid 옵션 문서 추가

C:\claude\tests\
├── test_ocr_hybrid_graphic_detector.py  [신규] Layer 1 단위 테스트
├── test_ocr_hybrid_som_annotator.py     [신규] Layer 3 단위 테스트
└── test_ocr_hybrid_pipeline.py          [신규] 통합 파이프라인 테스트
```

### UIElement 모델 설계

```python
@dataclass
class UIElement:
    element_type: str       # "text" | "graphic"
    bbox: BBox              # 픽셀 좌표 (기존 BBox 재사용)
    semantic_label: str     # SoM 레이블 (예: "submit_button", "logo_image")
    confidence: float       # 0.0~1.0 (Layer 2: OCR 신뢰도 / Layer 1: 컨투어 면적 기반)
    layer: int              # 1 또는 2 (감지 레이어 출처)
    marker_id: int          # SoM 마커 번호

@dataclass
class HybridAnalysisResult:
    elements: List[UIElement]
    annotated_image_path: Optional[str]  # SoM 어노테이션 이미지 경로
    processing_time: float               # 전체 파이프라인 처리 시간 (초)
    layer_stats: dict                    # {"layer1": N, "layer2": M, "total": N+M}
    mode: str                            # "coords" | "ui" | "hybrid"
```

---

## 8. 의존성

### 내부 의존성

```
hybrid_pipeline.py
  ├── graphic_detector.py  (Layer 1)
  ├── extractor.py         (Layer 2, 기존)
  ├── som_annotator.py     (Layer 3)
  ├── preprocessor.py      (전처리, 기존)
  └── models.py            (UIElement, HybridAnalysisResult, BBox 등)

som_annotator.py
  ├── models.py            (UIElement)
  └── lib/ai_auth/         (Vision LLM 인증)
```

### 외부 의존성

| 패키지 | 버전 | 용도 | 설치 여부 |
|--------|------|------|-----------|
| `opencv-python` | >=4.5 | `findContours`, 마커 삽입 | 기존 설치됨 |
| `pytesseract` | >=0.3 | Layer 2 텍스트 추출 | 기존 설치됨 |
| `Pillow` | >=9.0 | 이미지 I/O, 전처리 | 기존 설치됨 |
| `numpy` | >=1.21 | 배열 연산 | 기존 설치됨 |
| `anthropic` | >=0.18 | Claude Vision API (Layer 3) | 기존 설치됨 |

신규 pip 패키지 추가 없음 (NFR-D4).

### 실행 환경

- Python 3.10+
- Windows 11 (기본 환경) / Linux 호환
- Tesseract v5.0+ (kor+eng 언어팩 필수)
- Claude Vision API 접근 권한 (Layer 3 활성화 시)
