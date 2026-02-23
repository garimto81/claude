"""TDD Red Phase: SoMAnnotator 테스트"""
import os
from PIL import Image

from lib.ocr.models import UIElement, BBox


class TestSoMAnnotator:
    def test_import(self):
        from lib.ocr import SoMAnnotator
        assert SoMAnnotator is not None

    def test_annotate_returns_tuple(self):
        from lib.ocr import SoMAnnotator
        annotator = SoMAnnotator()
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        elements = [UIElement(element_type="text", bbox=BBox(10, 10, 50, 20))]
        result_image, mapping = annotator.annotate(image, elements)
        assert isinstance(result_image, Image.Image)
        assert isinstance(mapping, dict)

    def test_annotate_assigns_marker_ids(self):
        from lib.ocr import SoMAnnotator
        annotator = SoMAnnotator()
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        elements = [
            UIElement(element_type="text", bbox=BBox(10, 10, 50, 20)),
            UIElement(element_type="graphic", bbox=BBox(80, 80, 40, 40)),
        ]
        result_image, mapping = annotator.annotate(image, elements)
        assert len(mapping) == 2
        assert 1 in mapping
        assert 2 in mapping

    def test_save_annotated_creates_file(self, tmp_path):
        from lib.ocr import SoMAnnotator
        annotator = SoMAnnotator()
        image = Image.new("RGB", (100, 100), color=(200, 200, 200))
        output_path = str(tmp_path / "annotated.png")
        saved = annotator.save_annotated(image, output_path)
        assert os.path.exists(saved)

    def test_annotate_empty_elements(self):
        from lib.ocr import SoMAnnotator
        annotator = SoMAnnotator()
        image = Image.new("RGB", (100, 100), color=(255, 255, 255))
        result_image, mapping = annotator.annotate(image, [])
        assert isinstance(result_image, Image.Image)
        assert mapping == {}
