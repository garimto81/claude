"""TDD Red Phase: HybridPipeline 테스트"""
from unittest.mock import patch, MagicMock
from PIL import Image


class TestHybridPipeline:
    def test_import(self):
        from lib.ocr import HybridPipeline
        assert HybridPipeline is not None

    def test_analyze_coords_mode(self):
        from lib.ocr import HybridPipeline
        from lib.ocr.models import HybridAnalysisResult
        pipeline = HybridPipeline()
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        result = pipeline.analyze(image, mode="coords")
        assert isinstance(result, HybridAnalysisResult)
        assert result.mode == "coords"
        assert isinstance(result.elements, list)
        assert result.processing_time >= 0

    def test_analyze_returns_layer_stats(self):
        from lib.ocr import HybridPipeline
        pipeline = HybridPipeline()
        image = Image.new("RGB", (200, 200), color=(255, 255, 255))
        result = pipeline.analyze(image, mode="coords")
        assert "layer1" in result.layer_stats
        assert "layer2" in result.layer_stats

    def test_analyze_with_path_string(self, tmp_path):
        from lib.ocr import HybridPipeline
        pipeline = HybridPipeline()
        image_path = str(tmp_path / "test.png")
        Image.new("RGB", (100, 100), color=(255, 255, 255)).save(image_path)
        result = pipeline.analyze(image_path, mode="coords")
        assert result is not None

    def test_tesseract_not_installed_graceful(self):
        from lib.ocr import HybridPipeline
        from lib.ocr.errors import TesseractNotFoundError
        with patch("lib.ocr.hybrid_pipeline.OCRExtractor") as mock_cls:
            mock_inst = MagicMock()
            mock_inst.extract_text.side_effect = TesseractNotFoundError("Not installed")
            mock_cls.return_value = mock_inst
            pipeline = HybridPipeline()
            image = Image.new("RGB", (100, 100), color=(255, 255, 255))
            result = pipeline.analyze(image, mode="coords")
            assert result is not None
            assert result.layer_stats.get("layer2", 0) == 0

    def test_result_annotated_path_none_for_coords(self):
        from lib.ocr import HybridPipeline
        pipeline = HybridPipeline()
        image = Image.new("RGB", (100, 100), color=(255, 255, 255))
        result = pipeline.analyze(image, mode="coords")
        assert result.annotated_image_path is None
