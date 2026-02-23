"""TDD Red Phase: GraphicDetector 테스트 (구현 전 작성)"""
from PIL import Image
import numpy as np


class TestGraphicDetector:
    def test_import(self):
        from lib.ocr import GraphicDetector
        assert GraphicDetector is not None

    def test_detect_returns_bbox_list(self):
        from lib.ocr import GraphicDetector
        from lib.ocr.models import BBox
        detector = GraphicDetector()
        image = Image.new("RGB", (100, 100), color=(255, 255, 255))
        result = detector.detect(image)
        assert isinstance(result, list)
        assert all(isinstance(b, BBox) for b in result)

    def test_detect_with_type_returns_ui_elements(self):
        from lib.ocr import GraphicDetector
        from lib.ocr.models import UIElement
        detector = GraphicDetector()
        image = Image.new("RGB", (100, 100), color=(255, 255, 255))
        result = detector.detect_with_type(image)
        assert isinstance(result, list)
        assert all(isinstance(e, UIElement) for e in result)

    def test_detect_finds_contour_on_black_rect(self):
        from lib.ocr import GraphicDetector
        import cv2
        detector = GraphicDetector(min_area=100)
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        img_cv = np.array(image)
        cv2.rectangle(img_cv, (50, 50), (150, 150), (0, 0, 0), -1)
        image = Image.fromarray(img_cv)
        result = detector.detect(image)
        assert len(result) >= 1

    def test_min_area_filter(self):
        from lib.ocr import GraphicDetector
        detector = GraphicDetector(min_area=10000)
        image = Image.new("RGB", (50, 50), color=(255, 255, 255))
        result = detector.detect(image)
        assert len(result) == 0

    def test_element_type_graphic(self):
        from lib.ocr import GraphicDetector
        import cv2
        detector = GraphicDetector(min_area=100)
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        img_cv = np.array(image)
        cv2.rectangle(img_cv, (50, 50), (150, 150), (0, 0, 0), -1)
        image = Image.fromarray(img_cv)
        result = detector.detect_with_type(image)
        assert len(result) >= 1
        assert all(e.element_type == "graphic" for e in result)

    def test_layer_value(self):
        from lib.ocr import GraphicDetector
        import cv2
        detector = GraphicDetector(min_area=100)
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        img_cv = np.array(image)
        cv2.rectangle(img_cv, (50, 50), (150, 150), (0, 0, 0), -1)
        image = Image.fromarray(img_cv)
        result = detector.detect_with_type(image)
        assert len(result) >= 1
        assert all(e.layer == 1 for e in result)
