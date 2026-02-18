# OCR Tesseract 정밀 이미지 분석 시스템 상세 설계 문서

**작성일**: 2026-02-17
**버전**: 1.0.0
**복잡도**: STANDARD (3/5)
**담당**: designer
**참조 계획서**: `docs/01-plan/ocr-tesseract.plan.md`

---

## 1. 모듈 상세 설계

### 1.1 `lib/ocr/extractor.py` - OCRExtractor 클래스

#### 클래스 정의

```python
from typing import List, Optional, Dict, Any
from pathlib import Path
from PIL import Image
import pytesseract
from .models import OCRResult, TextRegion, TableDetection, LayoutInfo, BBox
from .preprocessor import ImagePreprocessor
from .errors import OCRError, TesseractNotFoundError, ImageLoadError


class OCRExtractor:
    """
    Tesseract OCR wrapper 클래스

    이미지에서 텍스트를 추출하는 핵심 클래스. pytesseract를 래핑하여
    전처리, 영역 기반 추출, 표 감지, 레이아웃 분석 기능 제공.

    Attributes:
        image_path (Path): 처리할 이미지 파일 경로
        lang (str): Tesseract 언어 코드 (예: "kor+eng")
        _image (Image.Image): 로드된 PIL 이미지 객체
        _preprocessor (ImagePreprocessor): 이미지 전처리 파이프라인

    Example:
        >>> extractor = OCRExtractor("invoice.jpg", lang="kor+eng")
        >>> result = extractor.extract_text(preprocess=True)
        >>> print(result.text)
        >>> print(f"Confidence: {result.confidence}")
    """

    def __init__(
        self,
        image_path: str | Path,
        lang: str = "kor+eng",
        tesseract_cmd: Optional[str] = None
    ):
        """
        OCRExtractor 초기화

        Args:
            image_path: 처리할 이미지 파일 경로
            lang: Tesseract 언어 코드 (기본값: "kor+eng")
            tesseract_cmd: Tesseract 실행 파일 경로 (None이면 자동 탐색)

        Raises:
            ImageLoadError: 이미지 로드 실패
            TesseractNotFoundError: Tesseract 바이너리 미발견
        """
        self.image_path = Path(image_path)
        self.lang = lang
        self._preprocessor = ImagePreprocessor()

        # Tesseract 경로 설정
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            self._auto_detect_tesseract()

        # Tesseract 설치 검증
        self._verify_tesseract()

        # 이미지 로드
        try:
            self._image = Image.open(self.image_path)
        except Exception as e:
            raise ImageLoadError(f"Failed to load image: {e}")

    def extract_text(
        self,
        preprocess: bool = True,
        config: Optional[str] = None
    ) -> OCRResult:
        """
        전체 이미지에서 텍스트 추출

        Args:
            preprocess: 전처리 활성화 여부 (기본값: True)
            config: Tesseract 설정 문자열 (예: "--psm 6")

        Returns:
            OCRResult: 추출된 텍스트, 신뢰도, 레이아웃 정보

        Example:
            >>> result = extractor.extract_text(preprocess=True)
            >>> if result.confidence > 0.8:
            ...     print(result.text)
        """
        import time
        start_time = time.time()

        # 전처리
        image = self._image.copy()
        if preprocess:
            image = self._preprocessor.pipeline(
                image,
                steps=["grayscale", "threshold", "denoise"]
            )

        # Tesseract 설정
        tesseract_config = config or self._get_default_config()

        # 텍스트 추출
        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=tesseract_config
            )

            # 신뢰도 정보 추출 (pytesseract.image_to_data 사용)
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )
            confidence = self._calculate_confidence(data)

            # 레이아웃 정보 추출
            layout_info = self._extract_layout_info(data)

        except Exception as e:
            raise OCRError(f"OCR extraction failed: {e}")

        processing_time = time.time() - start_time

        return OCRResult(
            text=text.strip(),
            confidence=confidence,
            layout_info=layout_info,
            language=self.lang,
            processing_time=processing_time
        )

    def extract_regions(
        self,
        boxes: List[BBox],
        preprocess: bool = True
    ) -> List[TextRegion]:
        """
        특정 영역(bbox)에서만 텍스트 추출

        Args:
            boxes: 추출할 영역 리스트 [(x, y, width, height), ...]
            preprocess: 전처리 활성화 여부

        Returns:
            List[TextRegion]: 각 영역의 텍스트, bbox, 신뢰도

        Example:
            >>> boxes = [BBox(x=100, y=50, width=200, height=30)]
            >>> regions = extractor.extract_regions(boxes)
            >>> for region in regions:
            ...     print(f"{region.text} (conf: {region.confidence})")
        """
        image = self._image.copy()
        if preprocess:
            image = self._preprocessor.pipeline(
                image,
                steps=["grayscale", "threshold"]
            )

        regions = []
        for bbox in boxes:
            # 영역 크롭
            cropped = image.crop((
                bbox.x,
                bbox.y,
                bbox.x + bbox.width,
                bbox.y + bbox.height
            ))

            # OCR 수행
            text = pytesseract.image_to_string(cropped, lang=self.lang)
            data = pytesseract.image_to_data(
                cropped,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )
            confidence = self._calculate_confidence(data)

            regions.append(TextRegion(
                text=text.strip(),
                bbox=bbox,
                confidence=confidence
            ))

        return regions

    def detect_tables(
        self,
        preprocess: bool = True
    ) -> List[TableDetection]:
        """
        표 영역 자동 감지 및 텍스트 추출

        OpenCV Hough Line Transform으로 가로/세로선 감지 →
        교차점 기반 셀 영역 추출 → 각 셀 OCR 수행

        Args:
            preprocess: 전처리 활성화 여부

        Returns:
            List[TableDetection]: 감지된 표 리스트 (행/열/셀 데이터/bbox)

        Example:
            >>> tables = extractor.detect_tables()
            >>> for table in tables:
            ...     print(f"Table: {table.rows}x{table.cols}")
            ...     for row in table.cells:
            ...         print(" | ".join(row))
        """
        import cv2
        import numpy as np

        # 이미지 전처리
        image = self._image.copy()
        if preprocess:
            image = self._preprocessor.pipeline(
                image,
                steps=["grayscale", "threshold"]
            )

        # PIL → OpenCV
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

        # 선 감지 (Hough Line Transform)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )

        if lines is None:
            return []

        # 가로선/세로선 분리
        h_lines, v_lines = self._separate_lines(lines)

        # 표 영역 감지
        tables = self._detect_table_regions(h_lines, v_lines)

        # 각 표의 셀 OCR 수행
        table_results = []
        for table_bbox, cell_boxes in tables:
            cells = self._extract_table_cells(image, cell_boxes)
            rows, cols = self._infer_table_dimensions(cell_boxes)

            table_results.append(TableDetection(
                rows=rows,
                cols=cols,
                cells=cells,
                bbox=table_bbox
            ))

        return table_results

    def get_layout_info(self) -> LayoutInfo:
        """
        레이아웃 분석 (텍스트 블록, 열, 문단 구조)

        Tesseract의 PSM(Page Segmentation Mode) 3 사용하여
        블록, 문단, 줄, 단어 레벨 위계 추출

        Returns:
            LayoutInfo: 텍스트 블록, 문단, 줄, 단어 위치 정보

        Example:
            >>> layout = extractor.get_layout_info()
            >>> for block in layout.blocks:
            ...     print(f"Block {block.id}: {len(block.paragraphs)} paragraphs")
        """
        data = pytesseract.image_to_data(
            self._image,
            lang=self.lang,
            config="--psm 3",  # Fully automatic page segmentation
            output_type=pytesseract.Output.DICT
        )

        return self._parse_layout_data(data)

    # Private 메서드

    def _auto_detect_tesseract(self) -> None:
        """Tesseract 실행 파일 자동 탐색 (PATH → 기본 경로 → 환경변수)"""
        import shutil
        import os

        # 1. PATH에서 탐색
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            return

        # 2. Windows 기본 경로
        default_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            Path.home() / "scoop/shims/tesseract.exe"
        ]
        for path in default_paths:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = str(path)
                return

        # 3. 환경변수 TESSERACT_CMD
        env_path = os.getenv("TESSERACT_CMD")
        if env_path and Path(env_path).exists():
            pytesseract.pytesseract.tesseract_cmd = env_path
            return

    def _verify_tesseract(self) -> None:
        """Tesseract 설치 및 언어팩 검증"""
        try:
            version = pytesseract.get_tesseract_version()
        except Exception as e:
            raise TesseractNotFoundError(
                "Tesseract not installed. "
                "Install via: scoop install tesseract"
            )

        # 언어팩 검증
        available_langs = pytesseract.get_languages()
        required_langs = self.lang.split("+")
        missing_langs = [l for l in required_langs if l not in available_langs]

        if missing_langs:
            raise OCRError(
                f"Missing language packs: {missing_langs}. "
                f"Available: {available_langs}"
            )

    def _get_default_config(self) -> str:
        """기본 Tesseract 설정 문자열 반환"""
        # PSM 3: Fully automatic page segmentation (default)
        # OEM 3: Default, based on what is available
        return "--psm 3 --oem 3"

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """
        pytesseract.image_to_data의 confidence 필드로부터
        평균 신뢰도 계산 (0.0 ~ 1.0)
        """
        confidences = [
            float(conf) for conf in data["conf"]
            if conf != -1  # -1은 빈 영역
        ]
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences) / 100.0

    def _extract_layout_info(self, data: Dict[str, Any]) -> LayoutInfo:
        """pytesseract.image_to_data로부터 레이아웃 정보 추출"""
        # 상세 구현은 models.py의 LayoutInfo 구조 참조
        # block_num, par_num, line_num, word_num 계층 파싱
        from .models import TextBlock, Paragraph, Line, Word

        blocks = {}
        for i in range(len(data["text"])):
            block_num = data["block_num"][i]
            par_num = data["par_num"][i]
            line_num = data["line_num"][i]
            word_num = data["word_num"][i]

            # 계층 구조 빌드 (상세 로직 생략)
            # ...

        return LayoutInfo(blocks=list(blocks.values()))

    def _parse_layout_data(self, data: Dict[str, Any]) -> LayoutInfo:
        """레이아웃 데이터 파싱 (get_layout_info 헬퍼)"""
        return self._extract_layout_info(data)

    def _separate_lines(
        self,
        lines: np.ndarray
    ) -> tuple[List[np.ndarray], List[np.ndarray]]:
        """Hough Line Transform 결과에서 가로선/세로선 분리"""
        h_lines = []
        v_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

            # 가로선: -10° ~ +10°
            if -10 < angle < 10:
                h_lines.append(line)
            # 세로선: 80° ~ 100°
            elif 80 < abs(angle) < 100:
                v_lines.append(line)

        return h_lines, v_lines

    def _detect_table_regions(
        self,
        h_lines: List[np.ndarray],
        v_lines: List[np.ndarray]
    ) -> List[tuple[BBox, List[BBox]]]:
        """가로선/세로선 교차점으로 표 영역 및 셀 영역 감지"""
        # 간략화된 로직: 실제 구현은 line clustering + intersection 필요
        # 여기서는 단일 표 가정
        if not h_lines or not v_lines:
            return []

        # 표 전체 bbox 계산
        all_x = [line[0][0] for line in v_lines] + [line[0][2] for line in v_lines]
        all_y = [line[0][1] for line in h_lines] + [line[0][3] for line in h_lines]

        table_bbox = BBox(
            x=min(all_x),
            y=min(all_y),
            width=max(all_x) - min(all_x),
            height=max(all_y) - min(all_y)
        )

        # 셀 bbox 계산 (h_lines x v_lines 교차점 기반)
        cell_boxes = self._compute_cell_boxes(h_lines, v_lines)

        return [(table_bbox, cell_boxes)]

    def _compute_cell_boxes(
        self,
        h_lines: List[np.ndarray],
        v_lines: List[np.ndarray]
    ) -> List[BBox]:
        """가로선/세로선 교차점으로 각 셀의 BBox 계산"""
        # 간략화: 실제 구현은 line sorting + grid 생성 필요
        # 여기서는 placeholder
        return []

    def _extract_table_cells(
        self,
        image: Image.Image,
        cell_boxes: List[BBox]
    ) -> List[List[str]]:
        """각 셀 영역 OCR 수행 → 2D 배열 반환"""
        # 셀 bbox를 행/열로 그룹화 (y 좌표로 행, x 좌표로 열)
        # 간략화: 실제 구현 필요
        return []

    def _infer_table_dimensions(
        self,
        cell_boxes: List[BBox]
    ) -> tuple[int, int]:
        """셀 bbox로부터 표 차원 추론 (rows, cols)"""
        # y 좌표 기준 행 수, x 좌표 기준 열 수
        # 간략화: 실제 구현 필요
        return (0, 0)
```

---

### 1.2 `lib/ocr/preprocessor.py` - ImagePreprocessor 전처리 파이프라인

```python
from PIL import Image, ImageFilter
import cv2
import numpy as np
from typing import List, Literal


PreprocessStep = Literal["grayscale", "threshold", "deskew", "denoise", "sharpen"]


class ImagePreprocessor:
    """
    이미지 전처리 파이프라인

    OCR 정확도를 높이기 위한 이미지 전처리 단계 제공.
    OpenCV와 Pillow 조합 사용.

    Example:
        >>> preprocessor = ImagePreprocessor()
        >>> image = Image.open("noisy.jpg")
        >>> clean = preprocessor.pipeline(image, ["grayscale", "denoise", "threshold"])
    """

    @staticmethod
    def grayscale(image: Image.Image) -> Image.Image:
        """
        흑백 변환 (RGB → Grayscale)

        Args:
            image: PIL 이미지 객체

        Returns:
            Image.Image: 흑백 변환된 이미지
        """
        return image.convert("L")

    @staticmethod
    def threshold(
        image: Image.Image,
        method: Literal["otsu", "adaptive_gaussian", "adaptive_mean"] = "adaptive_gaussian"
    ) -> Image.Image:
        """
        이진화 (흑백 → 0 또는 255)

        Args:
            image: PIL 이미지 (흑백 권장)
            method: 이진화 방법
                - "otsu": Otsu's method (전역 임계값)
                - "adaptive_gaussian": Adaptive Gaussian Threshold (지역 임계값)
                - "adaptive_mean": Adaptive Mean Threshold

        Returns:
            Image.Image: 이진화된 이미지

        Example:
            >>> gray = ImagePreprocessor.grayscale(image)
            >>> binary = ImagePreprocessor.threshold(gray, method="adaptive_gaussian")
        """
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        if method == "otsu":
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "adaptive_gaussian":
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                blockSize=11,
                C=2
            )
        elif method == "adaptive_mean":
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                blockSize=11,
                C=2
            )
        else:
            raise ValueError(f"Unknown threshold method: {method}")

        return Image.fromarray(binary)

    @staticmethod
    def deskew(image: Image.Image, angle_threshold: float = 0.5) -> Image.Image:
        """
        기울기 보정 (Skew correction)

        Hough Line Transform으로 텍스트 줄 기울기 감지 → 회전 보정

        Args:
            image: PIL 이미지
            angle_threshold: 보정 최소 각도 (도). 이 값 미만이면 보정 스킵

        Returns:
            Image.Image: 기울기 보정된 이미지
        """
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Hough Line Transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

        if lines is None:
            return image

        # 각도 계산 (중앙값)
        angles = []
        for rho, theta in lines[:, 0]:
            angle = (theta - np.pi / 2) * 180 / np.pi
            angles.append(angle)

        median_angle = np.median(angles)

        if abs(median_angle) < angle_threshold:
            return image

        # 회전
        (h, w) = img_cv.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            img_cv,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))

    @staticmethod
    def denoise(
        image: Image.Image,
        method: Literal["gaussian", "median", "bilateral"] = "gaussian"
    ) -> Image.Image:
        """
        노이즈 제거

        Args:
            image: PIL 이미지
            method: 노이즈 제거 방법
                - "gaussian": Gaussian Blur (빠름, 경계 흐림)
                - "median": Median Filter (Salt-and-pepper 노이즈 효과적)
                - "bilateral": Bilateral Filter (경계 보존, 느림)

        Returns:
            Image.Image: 노이즈 제거된 이미지
        """
        if method == "gaussian":
            return image.filter(ImageFilter.GaussianBlur(radius=1))

        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        if method == "median":
            denoised = cv2.medianBlur(img_cv, ksize=3)
        elif method == "bilateral":
            denoised = cv2.bilateralFilter(img_cv, d=9, sigmaColor=75, sigmaSpace=75)
        else:
            raise ValueError(f"Unknown denoise method: {method}")

        return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))

    @staticmethod
    def sharpen(image: Image.Image, strength: float = 1.0) -> Image.Image:
        """
        샤프닝 (선명도 향상)

        Args:
            image: PIL 이미지
            strength: 샤프닝 강도 (0.0 ~ 2.0)

        Returns:
            Image.Image: 샤프닝된 이미지
        """
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1.0 + strength)

    def pipeline(
        self,
        image: Image.Image,
        steps: List[PreprocessStep],
        **kwargs
    ) -> Image.Image:
        """
        전처리 파이프라인 실행

        Args:
            image: PIL 이미지
            steps: 전처리 단계 리스트 (순서대로 실행)
            **kwargs: 각 단계별 파라미터 (예: threshold_method="otsu")

        Returns:
            Image.Image: 전처리된 이미지

        Example:
            >>> preprocessor = ImagePreprocessor()
            >>> result = preprocessor.pipeline(
            ...     image,
            ...     steps=["grayscale", "denoise", "threshold"],
            ...     threshold_method="adaptive_gaussian"
            ... )
        """
        current = image

        for step in steps:
            if step == "grayscale":
                current = self.grayscale(current)
            elif step == "threshold":
                method = kwargs.get("threshold_method", "adaptive_gaussian")
                current = self.threshold(current, method=method)
            elif step == "deskew":
                angle_threshold = kwargs.get("deskew_angle_threshold", 0.5)
                current = self.deskew(current, angle_threshold=angle_threshold)
            elif step == "denoise":
                method = kwargs.get("denoise_method", "gaussian")
                current = self.denoise(current, method=method)
            elif step == "sharpen":
                strength = kwargs.get("sharpen_strength", 1.0)
                current = self.sharpen(current, strength=strength)
            else:
                raise ValueError(f"Unknown preprocessing step: {step}")

        return current

    @classmethod
    def get_preset(cls, preset_name: str) -> List[PreprocessStep]:
        """
        이미지 유형별 최적 전처리 프리셋

        Args:
            preset_name: 프리셋 이름
                - "document": 문서 스캔 (흑백, 이진화)
                - "photo": 사진 텍스트 (노이즈 제거, 샤프닝)
                - "screenshot": 스크린샷 (기본 전처리)
                - "handwriting": 손글씨 (샤프닝, 기울기 보정)

        Returns:
            List[PreprocessStep]: 전처리 단계 리스트

        Example:
            >>> steps = ImagePreprocessor.get_preset("document")
            >>> image = preprocessor.pipeline(image, steps)
        """
        presets = {
            "document": ["grayscale", "deskew", "threshold"],
            "photo": ["denoise", "sharpen", "grayscale", "threshold"],
            "screenshot": ["grayscale", "threshold"],
            "handwriting": ["grayscale", "denoise", "deskew", "sharpen"],
            "table": ["grayscale", "threshold", "denoise"],
        }

        if preset_name not in presets:
            raise ValueError(
                f"Unknown preset: {preset_name}. "
                f"Available: {list(presets.keys())}"
            )

        return presets[preset_name]
```

---

### 1.3 `lib/ocr/models.py` - 데이터 모델

```python
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BBox:
    """바운딩 박스 (좌표 + 크기)"""
    x: int
    y: int
    width: int
    height: int

    def area(self) -> int:
        """면적 계산"""
        return self.width * self.height

    def contains(self, other: "BBox") -> bool:
        """다른 BBox를 포함하는지 검사"""
        return (
            self.x <= other.x and
            self.y <= other.y and
            self.x + self.width >= other.x + other.width and
            self.y + self.height >= other.y + other.height
        )


@dataclass
class Word:
    """단어 레벨 정보"""
    text: str
    bbox: BBox
    confidence: float


@dataclass
class Line:
    """줄 레벨 정보"""
    words: List[Word]
    bbox: BBox

    @property
    def text(self) -> str:
        """줄의 전체 텍스트"""
        return " ".join(word.text for word in self.words)


@dataclass
class Paragraph:
    """문단 레벨 정보"""
    lines: List[Line]
    bbox: BBox

    @property
    def text(self) -> str:
        """문단의 전체 텍스트"""
        return "\n".join(line.text for line in self.lines)


@dataclass
class TextBlock:
    """텍스트 블록 레벨 정보"""
    id: int
    paragraphs: List[Paragraph]
    bbox: BBox

    @property
    def text(self) -> str:
        """블록의 전체 텍스트"""
        return "\n\n".join(para.text for para in self.paragraphs)


@dataclass
class LayoutInfo:
    """전체 레이아웃 정보 (Tesseract PSM 3 결과)"""
    blocks: List[TextBlock]

    @property
    def num_blocks(self) -> int:
        return len(self.blocks)

    @property
    def num_paragraphs(self) -> int:
        return sum(len(block.paragraphs) for block in self.blocks)

    @property
    def num_lines(self) -> int:
        return sum(
            len(para.lines)
            for block in self.blocks
            for para in block.paragraphs
        )


@dataclass
class TextRegion:
    """특정 영역의 텍스트 추출 결과"""
    text: str
    bbox: BBox
    confidence: float


@dataclass
class TableDetection:
    """표 감지 및 추출 결과"""
    rows: int
    cols: int
    cells: List[List[str]]  # 2D 배열 (cells[row][col])
    bbox: BBox

    def to_markdown(self) -> str:
        """Markdown 표 형식으로 변환"""
        if not self.cells:
            return ""

        lines = []

        # 헤더
        header = "| " + " | ".join(self.cells[0]) + " |"
        lines.append(header)

        # 구분선
        separator = "| " + " | ".join(["---"] * self.cols) + " |"
        lines.append(separator)

        # 데이터 행
        for row in self.cells[1:]:
            row_str = "| " + " | ".join(row) + " |"
            lines.append(row_str)

        return "\n".join(lines)

    def to_csv(self) -> str:
        """CSV 형식으로 변환"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.cells)
        return output.getvalue()


@dataclass
class OCRResult:
    """Tesseract OCR 추출 결과"""
    text: str
    confidence: float  # 0.0 ~ 1.0
    layout_info: LayoutInfo
    language: str
    processing_time: float  # 초

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "processing_time": self.processing_time,
            "num_blocks": self.layout_info.num_blocks,
            "num_paragraphs": self.layout_info.num_paragraphs,
            "num_lines": self.layout_info.num_lines,
        }


@dataclass
class AnalysisResult:
    """하이브리드 분석 결과 (Vision + OCR)"""
    vision_context: str  # Claude Vision이 분석한 시각적 맥락
    ocr_text: str  # Tesseract가 추출한 정밀 텍스트
    confidence: float
    mode: str  # "vision", "ocr", "hybrid"
    metadata: dict = field(default_factory=dict)
```

---

### 1.4 `lib/ocr/errors.py` - 에러 계층 구조

```python
class OCRError(Exception):
    """OCR 모듈 기본 에러 클래스"""
    pass


class TesseractNotFoundError(OCRError):
    """Tesseract 바이너리 미발견"""
    pass


class ImageLoadError(OCRError):
    """이미지 로드 실패"""
    pass


class LanguagePackError(OCRError):
    """언어팩 누락"""
    pass


class PreprocessingError(OCRError):
    """이미지 전처리 실패"""
    pass


class TableDetectionError(OCRError):
    """표 감지 실패"""
    pass
```

---

## 2. 인터페이스 설계

### 2.1 Public API (`lib/ocr/__init__.py`)

```python
"""
lib.ocr - Tesseract OCR 정밀 텍스트 추출 모듈

Example:
    >>> from lib.ocr import OCRExtractor, ImagePreprocessor
    >>> extractor = OCRExtractor("invoice.jpg", lang="kor+eng")
    >>> result = extractor.extract_text(preprocess=True)
    >>> print(result.text)
"""

from .extractor import OCRExtractor
from .preprocessor import ImagePreprocessor
from .models import (
    OCRResult,
    TextRegion,
    TableDetection,
    LayoutInfo,
    BBox,
    AnalysisResult,
)
from .errors import (
    OCRError,
    TesseractNotFoundError,
    ImageLoadError,
    LanguagePackError,
    PreprocessingError,
    TableDetectionError,
)

__version__ = "1.0.0"

__all__ = [
    # 핵심 클래스
    "OCRExtractor",
    "ImagePreprocessor",
    # 데이터 모델
    "OCRResult",
    "TextRegion",
    "TableDetection",
    "LayoutInfo",
    "BBox",
    "AnalysisResult",
    # 에러
    "OCRError",
    "TesseractNotFoundError",
    "ImageLoadError",
    "LanguagePackError",
    "PreprocessingError",
    "TableDetectionError",
]


def extract_text(image_path: str, lang: str = "kor+eng", preprocess: bool = True) -> str:
    """
    편의 함수: 이미지에서 텍스트 추출 (one-liner)

    Args:
        image_path: 이미지 파일 경로
        lang: 언어 코드 (기본값: "kor+eng")
        preprocess: 전처리 활성화 여부

    Returns:
        str: 추출된 텍스트

    Example:
        >>> from lib.ocr import extract_text
        >>> text = extract_text("receipt.jpg")
        >>> print(text)
    """
    extractor = OCRExtractor(image_path, lang=lang)
    result = extractor.extract_text(preprocess=preprocess)
    return result.text


def check_installation() -> dict:
    """
    Tesseract 설치 상태 검증

    Returns:
        dict: 설치 상태 정보
            - installed (bool): Tesseract 설치 여부
            - version (str): Tesseract 버전
            - languages (list): 사용 가능 언어팩
            - path (str): tesseract 실행 파일 경로

    Example:
        >>> from lib.ocr import check_installation
        >>> info = check_installation()
        >>> if not info["installed"]:
        ...     print("Install Tesseract: scoop install tesseract")
    """
    import pytesseract

    try:
        version = pytesseract.get_tesseract_version()
        languages = pytesseract.get_languages()
        cmd = pytesseract.pytesseract.tesseract_cmd

        return {
            "installed": True,
            "version": str(version),
            "languages": languages,
            "path": str(cmd),
        }
    except Exception as e:
        return {
            "installed": False,
            "version": None,
            "languages": [],
            "path": None,
            "error": str(e),
        }
```

---

### 2.2 CLI 인터페이스 (`lib/ocr/cli.py`)

```python
import argparse
import json
from pathlib import Path
from . import OCRExtractor, check_installation, ImagePreprocessor


def main():
    parser = argparse.ArgumentParser(
        prog="python -m lib.ocr",
        description="Tesseract OCR CLI - 이미지 텍스트 추출 도구"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract 서브커맨드
    extract_parser = subparsers.add_parser(
        "extract",
        help="이미지에서 텍스트 추출"
    )
    extract_parser.add_argument(
        "image_path",
        type=str,
        help="이미지 파일 경로"
    )
    extract_parser.add_argument(
        "--lang",
        type=str,
        default="kor+eng",
        help="언어 코드 (기본값: kor+eng)"
    )
    extract_parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="전처리 비활성화"
    )
    extract_parser.add_argument(
        "--preset",
        type=str,
        choices=["document", "photo", "screenshot", "handwriting", "table"],
        help="전처리 프리셋"
    )
    extract_parser.add_argument(
        "--output",
        type=str,
        help="출력 파일 경로 (JSON)"
    )
    extract_parser.add_argument(
        "--table",
        action="store_true",
        help="표 감지 및 추출 모드"
    )

    # check 서브커맨드
    check_parser = subparsers.add_parser(
        "check",
        help="Tesseract 설치 확인"
    )

    args = parser.parse_args()

    if args.command == "check":
        info = check_installation()
        print(json.dumps(info, indent=2, ensure_ascii=False))

        if not info["installed"]:
            print("\n설치 방법:")
            print("  scoop install tesseract")
            print("  또는: https://github.com/UB-Mannheim/tesseract/wiki")
            return 1

        return 0

    elif args.command == "extract":
        image_path = Path(args.image_path)

        if not image_path.exists():
            print(f"Error: 파일을 찾을 수 없음: {image_path}")
            return 1

        try:
            extractor = OCRExtractor(image_path, lang=args.lang)

            if args.table:
                # 표 감지 모드
                tables = extractor.detect_tables(preprocess=not args.no_preprocess)

                result_data = {
                    "num_tables": len(tables),
                    "tables": [
                        {
                            "rows": table.rows,
                            "cols": table.cols,
                            "markdown": table.to_markdown(),
                            "csv": table.to_csv(),
                        }
                        for table in tables
                    ]
                }

                if args.output:
                    Path(args.output).write_text(
                        json.dumps(result_data, indent=2, ensure_ascii=False)
                    )
                else:
                    for i, table in enumerate(tables):
                        print(f"\n=== Table {i+1} ({table.rows}x{table.cols}) ===")
                        print(table.to_markdown())

            else:
                # 일반 텍스트 추출 모드
                result = extractor.extract_text(preprocess=not args.no_preprocess)

                if args.output:
                    Path(args.output).write_text(
                        json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
                    )
                else:
                    print(result.text)
                    print(f"\n[Confidence: {result.confidence:.2f}]")
                    print(f"[Processing time: {result.processing_time:.2f}s]")

        except Exception as e:
            print(f"Error: {e}")
            return 1

        return 0


if __name__ == "__main__":
    exit(main())
```

---

### 2.3 `/ocr-extract` 스킬 SKILL.md 구조

```markdown
# /ocr-extract - Tesseract 정밀 텍스트 추출 스킬

**Version**: 1.0.0
**Complexity**: STANDARD (3/5)
**Model**: sonnet

---

## 개요

Tesseract OCR로 이미지에서 정밀한 텍스트 추출. 문서, 표, 차트, 작은 글씨 등에 특화.

**사용 사례:**
- 스캔된 문서 텍스트 추출
- 표/차트 데이터 추출
- 명함/영수증 텍스트 추출
- 차량 계기판/에러 메시지 텍스트 추출

---

## 사용법

```bash
/ocr-extract <image_path>                       # 기본 텍스트 추출
/ocr-extract <image_path> --table               # 표 감지 + 추출
/ocr-extract <image_path> --lang kor+eng        # 언어 지정
/ocr-extract <image_path> --preset document     # 전처리 프리셋
/ocr-extract <image_path> --hybrid              # Vision + OCR 하이브리드
```

---

## 워크플로우

### 1. 기본 텍스트 추출

```python
from lib.ocr import OCRExtractor

extractor = OCRExtractor(image_path, lang="kor+eng")
result = extractor.extract_text(preprocess=True)

print(result.text)
print(f"신뢰도: {result.confidence}")
```

### 2. 표 추출

```python
tables = extractor.detect_tables()

for table in tables:
    print(table.to_markdown())
```

### 3. 하이브리드 분석 (Vision + OCR)

```python
# Vision으로 맥락 분석
vision_result = claude.read_image(image_path, "이미지 설명")

# OCR로 정밀 텍스트 추출
ocr_result = extractor.extract_text()

# 결과 통합
final = {
    "context": vision_result,
    "text": ocr_result.text,
    "confidence": ocr_result.confidence
}
```

---

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--lang` | 언어 코드 (예: kor+eng) | kor+eng |
| `--table` | 표 감지 모드 | False |
| `--preset` | 전처리 프리셋 (document/photo/screenshot/handwriting) | None |
| `--no-preprocess` | 전처리 비활성화 | False |
| `--hybrid` | Vision + OCR 하이브리드 분석 | False |
| `--output` | JSON 출력 파일 경로 | None |

---

## 설치 확인

```bash
python -m lib.ocr check
```

출력 예시:
```json
{
  "installed": true,
  "version": "5.3.0",
  "languages": ["kor", "eng", "..."],
  "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

---

## 구현 파일

- `lib/ocr/extractor.py` - OCRExtractor 핵심 클래스
- `lib/ocr/preprocessor.py` - 이미지 전처리 파이프라인
- `lib/ocr/cli.py` - CLI 인터페이스
- `.claude/skills/ocr-extract/scripts/extract.py` - 스킬 래퍼
```

---

## 3. 전처리 파이프라인 상세

### 3.1 OpenCV 함수 매핑

| 전처리 단계 | OpenCV 함수 | 파라미터 |
|------------|------------|---------|
| **흑백 변환** | `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` | - |
| **이진화 (Otsu)** | `cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` | - |
| **이진화 (Adaptive Gaussian)** | `cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)` | blockSize=11, C=2 |
| **기울기 보정** | `cv2.HoughLines` → `cv2.getRotationMatrix2D` → `cv2.warpAffine` | rho=1, theta=π/180 |
| **노이즈 제거 (Gaussian)** | `PIL.ImageFilter.GaussianBlur(radius=1)` | radius=1 |
| **노이즈 제거 (Median)** | `cv2.medianBlur(img, ksize=3)` | ksize=3 |
| **샤프닝** | `PIL.ImageEnhance.Sharpness` | strength=1.0 |

---

### 3.2 파이프라인 순서 및 기본값

**기본 파이프라인 (일반 이미지):**
```python
steps = ["grayscale", "threshold", "denoise"]
```

**권장 순서:**
1. **grayscale** - 먼저 흑백 변환 (다른 전처리가 grayscale 가정)
2. **deskew** (선택적) - 기울기 보정은 이진화 전
3. **denoise** - 노이즈 제거
4. **threshold** - 이진화 (OCR 직전)
5. **sharpen** (선택적) - 최종 선명도 향상

---

### 3.3 이미지 유형별 최적 전처리 프리셋

| 프리셋 | 단계 | 설명 |
|--------|------|------|
| **document** | `["grayscale", "deskew", "threshold"]` | 문서 스캔 (스캐너, PDF) |
| **photo** | `["denoise", "sharpen", "grayscale", "threshold"]` | 사진 속 텍스트 (휴대폰 촬영) |
| **screenshot** | `["grayscale", "threshold"]` | 스크린샷 (이미 깨끗함) |
| **handwriting** | `["grayscale", "denoise", "deskew", "sharpen"]` | 손글씨 (샤프닝 강화) |
| **table** | `["grayscale", "threshold", "denoise"]` | 표 (선 감지 최적화) |

**사용 예시:**
```python
preprocessor = ImagePreprocessor()
steps = preprocessor.get_preset("document")
processed = preprocessor.pipeline(image, steps)
```

---

## 4. 하이브리드 분석 전략 상세

### 4.1 HybridAnalyzer 클래스 설계

```python
# lib/ocr/hybrid.py (신규 파일)

from typing import Literal
from pathlib import Path
from .extractor import OCRExtractor
from .models import AnalysisResult


class HybridAnalyzer:
    """
    Claude Vision + Tesseract OCR 하이브리드 분석

    이미지 유형을 자동 감지하여 최적 도구 선택:
    - Vision: 시각적 맥락, Phase 분류, 복잡한 장면 이해
    - OCR: 정밀 텍스트 추출, 표/차트 데이터
    - Hybrid: 둘 다 실행 후 결과 통합

    Example:
        >>> analyzer = HybridAnalyzer()
        >>> result = analyzer.analyze("invoice.jpg", mode="auto")
        >>> print(result.vision_context)
        >>> print(result.ocr_text)
    """

    def __init__(self, claude_api_key: Optional[str] = None):
        """
        Args:
            claude_api_key: Claude API 키 (None이면 환경변수 사용)
        """
        self.claude_api_key = claude_api_key

    def analyze(
        self,
        image_path: str | Path,
        mode: Literal["auto", "vision", "ocr", "hybrid"] = "auto",
        lang: str = "kor+eng"
    ) -> AnalysisResult:
        """
        하이브리드 이미지 분석

        Args:
            image_path: 이미지 파일 경로
            mode: 분석 모드
                - "auto": 이미지 유형 자동 감지 → 최적 도구 선택
                - "vision": Claude Vision만 사용
                - "ocr": Tesseract OCR만 사용
                - "hybrid": 둘 다 실행 + 결과 통합
            lang: OCR 언어 코드

        Returns:
            AnalysisResult: Vision 맥락 + OCR 텍스트 + 신뢰도 + 메타데이터
        """
        image_path = Path(image_path)

        if mode == "auto":
            mode = self._detect_best_mode(image_path)

        if mode == "vision":
            return self._vision_analyze(image_path)
        elif mode == "ocr":
            return self._ocr_extract(image_path, lang)
        else:  # hybrid
            vision_result = self._vision_analyze(image_path)
            ocr_result = self._ocr_extract(image_path, lang)
            return self._combine_results(vision_result, ocr_result)

    def _detect_best_mode(self, image_path: Path) -> str:
        """
        이미지 유형 자동 감지 → 최적 모드 선택

        판단 기준:
        - 파일 이름 패턴 (invoice, receipt, table, chart → ocr)
        - 이미지 크기 (작은 이미지 → ocr)
        - 텍스트 밀도 (OCR 사전 실행으로 추정)

        Returns:
            str: "vision", "ocr", "hybrid" 중 하나
        """
        filename = image_path.stem.lower()

        # 파일 이름 패턴
        ocr_keywords = ["invoice", "receipt", "table", "chart", "document", "scan"]
        vision_keywords = ["photo", "wheel", "vehicle", "scene"]

        if any(kw in filename for kw in ocr_keywords):
            return "ocr"
        if any(kw in filename for kw in vision_keywords):
            return "vision"

        # 이미지 크기 검사
        from PIL import Image
        image = Image.open(image_path)
        width, height = image.size

        # 작은 이미지 (명함, 영수증 크기) → OCR
        if width < 800 and height < 1200:
            return "ocr"

        # 대형 이미지 → 하이브리드 (맥락 + 텍스트)
        if width > 2000 or height > 2000:
            return "hybrid"

        # 기본값: hybrid
        return "hybrid"

    def _vision_analyze(self, image_path: Path) -> AnalysisResult:
        """Claude Vision으로 시각적 맥락 분석"""
        # CLAUDE_API_KEY 환경변수 또는 생성자 파라미터 사용
        # Read 도구는 Claude Code 내부에서만 가능하므로
        # 실제 구현은 스킬에서 래핑 필요

        # Placeholder 구현 (실제는 Claude API 호출)
        vision_context = f"[Vision Analysis of {image_path.name}]"

        return AnalysisResult(
            vision_context=vision_context,
            ocr_text="",
            confidence=0.9,
            mode="vision",
            metadata={"source": "claude-vision"}
        )

    def _ocr_extract(self, image_path: Path, lang: str) -> AnalysisResult:
        """Tesseract OCR로 정밀 텍스트 추출"""
        extractor = OCRExtractor(image_path, lang=lang)
        result = extractor.extract_text(preprocess=True)

        return AnalysisResult(
            vision_context="",
            ocr_text=result.text,
            confidence=result.confidence,
            mode="ocr",
            metadata={
                "source": "tesseract",
                "language": result.language,
                "processing_time": result.processing_time,
                "num_blocks": result.layout_info.num_blocks,
            }
        )

    def _combine_results(
        self,
        vision_result: AnalysisResult,
        ocr_result: AnalysisResult
    ) -> AnalysisResult:
        """Vision과 OCR 결과 통합"""
        # 신뢰도 기반 가중 평균
        combined_confidence = (
            vision_result.confidence * 0.4 +
            ocr_result.confidence * 0.6
        )

        return AnalysisResult(
            vision_context=vision_result.vision_context,
            ocr_text=ocr_result.ocr_text,
            confidence=combined_confidence,
            mode="hybrid",
            metadata={
                "vision": vision_result.metadata,
                "ocr": ocr_result.metadata,
            }
        )
```

---

### 4.2 신뢰도 기반 Fallback 전략

**시나리오 1: OCR 신뢰도 낮음 (< 0.7)**
```python
ocr_result = extractor.extract_text()

if ocr_result.confidence < 0.7:
    # Vision으로 fallback
    vision_result = claude.read_image(image_path, "Extract text")
    return vision_result
else:
    return ocr_result.text
```

**시나리오 2: Tesseract 미설치**
```python
from lib.ocr import check_installation

info = check_installation()

if not info["installed"]:
    logger.warning("Tesseract not found, falling back to Vision API")
    return claude.read_image(image_path)
else:
    return OCRExtractor(image_path).extract_text()
```

**시나리오 3: 하이브리드 검증**
```python
# OCR 실행
ocr_text = extractor.extract_text().text

# Vision으로 검증 요청
verification_prompt = f"""
아래 OCR 추출 텍스트가 이미지와 일치하는지 검증하세요:

{ocr_text}

일치하면 "OK", 오류가 있으면 수정된 텍스트 반환.
"""
vision_verification = claude.read_image(image_path, verification_prompt)

# 최종 결과 반환
if "OK" in vision_verification:
    return ocr_text
else:
    return vision_verification
```

---

## 5. Tesseract 설정 관리

### 5.1 tesseract_cmd 경로 탐색 전략

**우선순위 (높음 → 낮음):**

1. **생성자 파라미터** (명시적 지정)
   ```python
   extractor = OCRExtractor("image.jpg", tesseract_cmd=r"C:\custom\tesseract.exe")
   ```

2. **PATH 환경변수** (시스템 전역)
   ```python
   import shutil
   tesseract_path = shutil.which("tesseract")
   ```

3. **Windows 기본 경로** (UB-Mannheim 설치)
   ```python
   default_paths = [
       r"C:\Program Files\Tesseract-OCR\tesseract.exe",
       r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
   ]
   ```

4. **Scoop 설치 경로**
   ```python
   scoop_path = Path.home() / "scoop/shims/tesseract.exe"
   ```

5. **환경변수 TESSERACT_CMD** (프로젝트 .env)
   ```python
   import os
   env_path = os.getenv("TESSERACT_CMD")
   ```

**구현 (extractor.py의 _auto_detect_tesseract):**
```python
def _auto_detect_tesseract(self) -> None:
    import shutil
    import os

    # 1. PATH 탐색
    if cmd := shutil.which("tesseract"):
        pytesseract.pytesseract.tesseract_cmd = cmd
        return

    # 2. Windows 기본 경로
    for path in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        Path.home() / "scoop/shims/tesseract.exe",
    ]:
        if Path(path).exists():
            pytesseract.pytesseract.tesseract_cmd = str(path)
            return

    # 3. 환경변수
    if (env_path := os.getenv("TESSERACT_CMD")) and Path(env_path).exists():
        pytesseract.pytesseract.tesseract_cmd = env_path
        return
```

---

### 5.2 언어팩 검증 로직

```python
def _verify_tesseract(self) -> None:
    """Tesseract 설치 및 언어팩 검증"""
    try:
        version = pytesseract.get_tesseract_version()
    except Exception as e:
        raise TesseractNotFoundError(
            f"Tesseract not installed. Install via: scoop install tesseract\n{e}"
        )

    # 언어팩 검증
    available_langs = pytesseract.get_languages()
    required_langs = self.lang.split("+")
    missing_langs = [l for l in required_langs if l not in available_langs]

    if missing_langs:
        raise LanguagePackError(
            f"Missing language packs: {missing_langs}. "
            f"Available: {available_langs}\n"
            f"Install guide: https://github.com/tesseract-ocr/tessdata"
        )
```

**언어팩 다운로드 가이드 (에러 메시지):**
```
Error: Missing language packs: ['kor']

설치 방법:
1. https://github.com/tesseract-ocr/tessdata 방문
2. kor.traineddata 다운로드
3. C:\Program Files\Tesseract-OCR\tessdata\ 에 복사
4. 또는: scoop install tesseract-languages
```

---

### 5.3 PSM(Page Segmentation Mode) 선택 전략

**Tesseract PSM 모드:**

| PSM | 설명 | 사용 사례 |
|-----|------|----------|
| 0 | Orientation and script detection (OSD) only | 회전 감지만 |
| 1 | Automatic page segmentation with OSD | 자동 + OSD |
| 3 | Fully automatic page segmentation, but no OSD | **기본값** (문서) |
| 4 | Assume a single column of text of variable sizes | 단일 열 (신문) |
| 6 | Assume a single uniform block of text | 단일 블록 (명함) |
| 7 | Treat the image as a single text line | 단일 줄 (영수증 항목) |
| 8 | Treat the image as a single word | 단일 단어 |
| 11 | Sparse text. Find as much text as possible | 흩어진 텍스트 (광고) |
| 13 | Raw line. Treat as single text line, bypass hacks | 원시 줄 |

**선택 전략:**

```python
def _get_default_config(self) -> str:
    """이미지 유형별 최적 PSM 선택"""
    # 파일 이름 또는 이미지 크기로 유형 추정
    image_type = self._detect_image_type()

    psm_map = {
        "document": 3,      # Fully automatic
        "receipt": 6,       # Single block
        "line": 7,          # Single line
        "sparse": 11,       # Sparse text
        "table": 4,         # Single column
    }

    psm = psm_map.get(image_type, 3)
    return f"--psm {psm} --oem 3"
```

**사용자 지정 PSM:**
```python
result = extractor.extract_text(config="--psm 6 --oem 3")
```

---

## 6. 테스트 설계

### 6.1 테스트 픽스처 (샘플 이미지) 전략

**디렉토리 구조:**
```
lib/ocr/tests/
├── conftest.py                      # pytest fixtures
├── fixtures/
│   ├── korean_text.png              # 한글 텍스트
│   ├── english_text.png             # 영어 텍스트
│   ├── mixed_text.png               # 한글+영어 혼용
│   ├── table_3x2.png                # 3행 2열 표
│   ├── receipt.png                  # 영수증 (작은 글씨)
│   ├── handwriting.png              # 손글씨
│   ├── noisy.png                    # 노이즈 많은 이미지
│   ├── skewed.png                   # 기울어진 이미지
│   └── expected/
│       ├── korean_text.txt          # Ground truth
│       ├── table_3x2.json           # 표 ground truth
│       └── ...
├── test_extractor.py
├── test_preprocessor.py
├── test_hybrid.py
└── test_cli.py
```

**conftest.py:**
```python
import pytest
from pathlib import Path
from PIL import Image


@pytest.fixture
def fixtures_dir():
    """Fixtures 디렉토리 경로"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def korean_text_image(fixtures_dir):
    """한글 텍스트 샘플 이미지"""
    return fixtures_dir / "korean_text.png"


@pytest.fixture
def korean_text_expected(fixtures_dir):
    """한글 텍스트 기대값"""
    return (fixtures_dir / "expected" / "korean_text.txt").read_text(encoding="utf-8")


@pytest.fixture
def table_image(fixtures_dir):
    """표 샘플 이미지"""
    return fixtures_dir / "table_3x2.png"


@pytest.fixture
def table_expected(fixtures_dir):
    """표 기대값 (JSON)"""
    import json
    return json.loads((fixtures_dir / "expected" / "table_3x2.json").read_text())


@pytest.fixture
def mock_tesseract_not_installed(monkeypatch):
    """Tesseract 미설치 상황 mock"""
    import pytesseract

    def mock_get_version():
        raise FileNotFoundError("tesseract not found")

    monkeypatch.setattr(pytesseract, "get_tesseract_version", mock_get_version)
```

---

### 6.2 Mock 전략 (Tesseract 미설치 환경 테스트)

**시나리오 1: Tesseract 미설치**
```python
def test_tesseract_not_installed(mock_tesseract_not_installed):
    """Tesseract 미설치 시 TesseractNotFoundError 발생"""
    from lib.ocr.errors import TesseractNotFoundError

    with pytest.raises(TesseractNotFoundError, match="not installed"):
        OCRExtractor("dummy.png")
```

**시나리오 2: 언어팩 누락**
```python
def test_missing_language_pack(monkeypatch):
    """언어팩 누락 시 LanguagePackError 발생"""
    import pytesseract

    monkeypatch.setattr(
        pytesseract,
        "get_languages",
        lambda: ["eng"]  # kor 누락
    )

    from lib.ocr.errors import LanguagePackError

    with pytest.raises(LanguagePackError, match="Missing language packs: \\['kor'\\]"):
        OCRExtractor("dummy.png", lang="kor+eng")
```

**시나리오 3: 이미지 로드 실패**
```python
def test_image_load_error():
    """존재하지 않는 파일 → ImageLoadError"""
    from lib.ocr.errors import ImageLoadError

    with pytest.raises(ImageLoadError):
        OCRExtractor("nonexistent.png")
```

---

### 6.3 커버리지 목표별 테스트 케이스 목록

**목표: 단위 테스트 커버리지 ≥ 80%**

#### **test_extractor.py** (OCRExtractor 클래스)

| 테스트 케이스 | 검증 내용 | 우선순위 |
|--------------|----------|---------|
| `test_extract_korean_text` | 한글 텍스트 추출 정확도 | HIGH |
| `test_extract_english_text` | 영어 텍스트 추출 정확도 | HIGH |
| `test_extract_mixed_text` | 한글+영어 혼용 추출 | HIGH |
| `test_extract_text_with_preprocess` | 전처리 활성화 시 정확도 향상 | MEDIUM |
| `test_extract_text_no_preprocess` | 전처리 비활성화 동작 | LOW |
| `test_extract_regions` | 특정 영역 추출 (bbox 기반) | MEDIUM |
| `test_detect_tables` | 표 감지 및 추출 | HIGH |
| `test_get_layout_info` | 레이아웃 분석 (블록/문단/줄) | MEDIUM |
| `test_confidence_calculation` | 신뢰도 계산 정확성 | MEDIUM |
| `test_auto_detect_tesseract` | Tesseract 경로 자동 탐색 | HIGH |
| `test_verify_tesseract_installed` | Tesseract 설치 검증 | HIGH |
| `test_verify_tesseract_not_installed` | Tesseract 미설치 시 에러 | HIGH |
| `test_missing_language_pack` | 언어팩 누락 시 에러 | HIGH |
| `test_image_load_error` | 이미지 로드 실패 에러 | MEDIUM |

**예시 구현:**
```python
# tests/test_extractor.py

def test_extract_korean_text(korean_text_image, korean_text_expected):
    """한글 텍스트 추출 정확도 테스트"""
    extractor = OCRExtractor(korean_text_image, lang="kor")
    result = extractor.extract_text()

    assert result.confidence > 0.8, f"낮은 신뢰도: {result.confidence}"
    assert korean_text_expected in result.text, "기대 텍스트 미포함"


def test_detect_tables(table_image, table_expected):
    """표 감지 및 추출 테스트"""
    extractor = OCRExtractor(table_image)
    tables = extractor.detect_tables()

    assert len(tables) == 1
    assert tables[0].rows == table_expected["rows"]
    assert tables[0].cols == table_expected["cols"]

    # 셀 데이터 검증 (일부만)
    assert tables[0].cells[0][0] == table_expected["cells"][0][0]
```

#### **test_preprocessor.py** (ImagePreprocessor 클래스)

| 테스트 케이스 | 검증 내용 | 우선순위 |
|--------------|----------|---------|
| `test_grayscale` | 흑백 변환 동작 | HIGH |
| `test_threshold_otsu` | Otsu 이진화 동작 | HIGH |
| `test_threshold_adaptive_gaussian` | Adaptive Gaussian 이진화 | HIGH |
| `test_deskew` | 기울기 보정 동작 | MEDIUM |
| `test_deskew_no_correction_needed` | 기울기 작을 때 스킵 | LOW |
| `test_denoise_gaussian` | Gaussian 노이즈 제거 | MEDIUM |
| `test_denoise_median` | Median 노이즈 제거 | MEDIUM |
| `test_sharpen` | 샤프닝 동작 | MEDIUM |
| `test_pipeline_multiple_steps` | 다단계 파이프라인 실행 | HIGH |
| `test_get_preset_document` | document 프리셋 | HIGH |
| `test_get_preset_photo` | photo 프리셋 | MEDIUM |
| `test_get_preset_invalid` | 잘못된 프리셋 → ValueError | MEDIUM |

**예시 구현:**
```python
# tests/test_preprocessor.py

def test_grayscale(korean_text_image):
    """흑백 변환 테스트"""
    from PIL import Image

    image = Image.open(korean_text_image)
    gray = ImagePreprocessor.grayscale(image)

    assert gray.mode == "L", "흑백 모드가 아님"


def test_pipeline_multiple_steps(korean_text_image):
    """다단계 파이프라인 실행 테스트"""
    from PIL import Image

    image = Image.open(korean_text_image)
    preprocessor = ImagePreprocessor()

    result = preprocessor.pipeline(
        image,
        steps=["grayscale", "denoise", "threshold"]
    )

    assert result.mode == "L", "최종 이미지가 흑백이 아님"
```

#### **test_hybrid.py** (HybridAnalyzer 클래스)

| 테스트 케이스 | 검증 내용 | 우선순위 |
|--------------|----------|---------|
| `test_analyze_auto_mode` | auto 모드 동작 | HIGH |
| `test_analyze_vision_only` | Vision만 사용 | MEDIUM |
| `test_analyze_ocr_only` | OCR만 사용 | MEDIUM |
| `test_analyze_hybrid` | Vision + OCR 통합 | HIGH |
| `test_detect_best_mode_ocr` | 파일 이름 기반 OCR 선택 | MEDIUM |
| `test_detect_best_mode_vision` | 파일 이름 기반 Vision 선택 | MEDIUM |
| `test_combine_results` | Vision과 OCR 결과 통합 | HIGH |

#### **test_cli.py** (CLI 인터페이스)

| 테스트 케이스 | 검증 내용 | 우선순위 |
|--------------|----------|---------|
| `test_cli_extract` | `extract` 서브커맨드 | HIGH |
| `test_cli_extract_with_table` | `--table` 옵션 | HIGH |
| `test_cli_extract_with_output` | `--output` JSON 출력 | MEDIUM |
| `test_cli_check_installed` | `check` 서브커맨드 (설치됨) | HIGH |
| `test_cli_check_not_installed` | `check` 서브커맨드 (미설치) | HIGH |

---

## 7. 에러 처리 설계

### 7.1 에러 발생 시나리오별 처리 전략

| 에러 | 발생 시나리오 | 처리 전략 | 사용자 메시지 |
|------|--------------|----------|--------------|
| **TesseractNotFoundError** | Tesseract 바이너리 미설치 | Vision API로 fallback 또는 에러 반환 | "Tesseract not installed. Install via: scoop install tesseract" |
| **LanguagePackError** | 언어팩 누락 (kor.traineddata 없음) | 에러 반환 + 다운로드 가이드 | "Missing language packs: ['kor']. Download from: https://..." |
| **ImageLoadError** | 이미지 파일 손상/미존재 | 에러 반환 | "Failed to load image: {path}" |
| **PreprocessingError** | OpenCV 전처리 실패 | 전처리 스킵 + 원본 이미지로 OCR 재시도 | "Preprocessing failed, using original image" |
| **TableDetectionError** | 표 감지 실패 (선 없음) | 빈 리스트 반환 | "No tables detected" |
| **OCRError** (일반) | Tesseract 실행 실패 | Vision API로 fallback | "OCR extraction failed, falling back to Vision API" |

---

### 7.2 로깅 전략

**로깅 레벨:**

| 레벨 | 사용 사례 | 예시 |
|------|----------|------|
| **DEBUG** | 전처리 단계별 진행 상황 | "Applied grayscale preprocessing" |
| **INFO** | OCR 실행 시작/완료 | "OCR completed in 0.45s, confidence: 0.92" |
| **WARNING** | Fallback 발생 | "Tesseract not found, falling back to Vision API" |
| **ERROR** | 에러 발생 | "Failed to load image: file not found" |

**로거 설정 (lib/ocr/__init__.py):**
```python
import logging

logger = logging.getLogger("lib.ocr")
logger.setLevel(logging.INFO)

# 핸들러 설정 (선택적)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

**사용 예시 (extractor.py):**
```python
import logging
logger = logging.getLogger("lib.ocr.extractor")

def extract_text(self, preprocess: bool = True) -> OCRResult:
    logger.info(f"Starting OCR extraction: {self.image_path}")

    if preprocess:
        logger.debug("Applying preprocessing pipeline")

    try:
        # OCR 실행
        ...
        logger.info(f"OCR completed in {processing_time:.2f}s, confidence: {confidence:.2f}")
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise OCRError(f"OCR extraction failed: {e}")
```

---

### 7.3 Graceful Degradation (Tesseract 미설치 → Vision Fallback)

**전략:**

1. **설치 검증 시점**: OCRExtractor 초기화 시 Tesseract 설치 확인
2. **Fallback 트리거**: TesseractNotFoundError 발생 시
3. **Fallback 동작**: Claude Vision API로 자동 전환
4. **사용자 알림**: WARNING 로그 + 설치 가이드 출력

**구현 (lib/ocr/__init__.py 편의 함수):**

```python
def extract_text_safe(
    image_path: str,
    lang: str = "kor+eng",
    fallback_to_vision: bool = True
) -> str:
    """
    Graceful degradation이 적용된 텍스트 추출

    Tesseract 미설치 시 Claude Vision으로 자동 fallback

    Args:
        image_path: 이미지 파일 경로
        lang: 언어 코드
        fallback_to_vision: Vision API fallback 활성화 여부

    Returns:
        str: 추출된 텍스트
    """
    try:
        extractor = OCRExtractor(image_path, lang=lang)
        result = extractor.extract_text(preprocess=True)
        return result.text

    except TesseractNotFoundError as e:
        if not fallback_to_vision:
            raise

        logger.warning(f"Tesseract not found, falling back to Vision API: {e}")
        logger.info("Install Tesseract: scoop install tesseract")

        # Vision API fallback (실제 구현은 스킬에서)
        # 여기서는 placeholder
        return _fallback_to_vision(image_path)


def _fallback_to_vision(image_path: str) -> str:
    """Claude Vision API로 텍스트 추출 (fallback)"""
    # 실제 구현: Claude Read 도구 호출
    # Claude Code 스킬 내부에서만 가능
    logger.info(f"Using Vision API for {image_path}")
    return "[Vision API result placeholder]"
```

**스킬에서의 사용 (.claude/skills/ocr-extract/scripts/extract.py):**

```python
from lib.ocr import extract_text_safe

# Tesseract 미설치 시 자동 Vision fallback
text = extract_text_safe(image_path, fallback_to_vision=True)
print(text)
```

---

## 8. 요약

본 설계 문서는 `docs/01-plan/ocr-tesseract.plan.md` 계획서를 기반으로 다음 항목을 상세화했습니다:

1. **모듈 상세 설계** - OCRExtractor, ImagePreprocessor, 데이터 모델, 에러 계층 구조 (메서드 시그니처, 반환 타입, docstring 포함)
2. **인터페이스 설계** - Public API, CLI, /ocr-extract 스킬 SKILL.md
3. **전처리 파이프라인 상세** - OpenCV 함수 매핑, 파이프라인 순서, 프리셋 전략
4. **하이브리드 분석 전략** - HybridAnalyzer 클래스, auto mode 판단 로직, 신뢰도 기반 fallback
5. **Tesseract 설정 관리** - tesseract_cmd 경로 탐색 전략, 언어팩 검증, PSM 선택 전략
6. **테스트 설계** - 픽스처 전략, Mock 전략, 커버리지 목표별 테스트 케이스 15개+
7. **에러 처리 설계** - 시나리오별 처리 전략, 로깅 전략, Graceful degradation

**다음 단계:**
- Phase 1-6 구현 (계획서 참조)
- TDD 기반 테스트 먼저 작성 → 구현
- E2E 테스트 및 벤치마크 실행
- 문서화 (README.md, API 문서)

---

**END OF DESIGN**
