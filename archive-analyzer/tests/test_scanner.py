"""아카이브 스캐너 테스트"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archive_analyzer.file_classifier import (
    FileType,
    classify_file,
    is_video_file,
    is_audio_file,
    is_subtitle_file,
    is_metadata_file,
    is_image_file,
    FileClassifier,
)
from archive_analyzer.database import Database, FileRecord, ScanCheckpoint
from archive_analyzer.scanner import ArchiveScanner, ScanProgress, ScanResult
from archive_analyzer.smb_connector import SMBConnector
from archive_analyzer.config import SMBConfig


# 테스트용 설정
TEST_SERVER = "10.10.100.122"
TEST_SHARE = "docker"
TEST_USERNAME = "GGP"
TEST_PASSWORD = os.getenv("SMB_PASSWORD", "!@QW12qw")
TEST_ARCHIVE_PATH = "GGPNAs/ARCHIVE"


class TestFileClassifier:
    """파일 분류기 테스트"""

    def test_classify_video_files(self):
        """비디오 파일 분류 테스트"""
        video_files = [
            "movie.mp4", "video.mkv", "clip.avi", "film.mov",
            "stream.wmv", "web.webm", "broadcast.ts"
        ]
        for filename in video_files:
            assert classify_file(filename) == FileType.VIDEO, f"{filename} should be VIDEO"

    def test_classify_audio_files(self):
        """오디오 파일 분류 테스트"""
        audio_files = [
            "song.mp3", "audio.aac", "music.flac", "sound.wav", "track.m4a"
        ]
        for filename in audio_files:
            assert classify_file(filename) == FileType.AUDIO, f"{filename} should be AUDIO"

    def test_classify_subtitle_files(self):
        """자막 파일 분류 테스트"""
        subtitle_files = [
            "sub.srt", "sub.ass", "sub.ssa", "sub.vtt", "sub.sub"
        ]
        for filename in subtitle_files:
            assert classify_file(filename) == FileType.SUBTITLE, f"{filename} should be SUBTITLE"

    def test_classify_metadata_files(self):
        """메타데이터 파일 분류 테스트"""
        meta_files = ["info.nfo", "data.xml", "config.json"]
        for filename in meta_files:
            assert classify_file(filename) == FileType.METADATA, f"{filename} should be METADATA"

    def test_classify_image_files(self):
        """이미지 파일 분류 테스트"""
        image_files = ["photo.jpg", "image.png", "poster.webp", "thumb.gif"]
        for filename in image_files:
            assert classify_file(filename) == FileType.IMAGE, f"{filename} should be IMAGE"

    def test_classify_unknown_files(self):
        """알 수 없는 파일 분류 테스트"""
        other_files = ["document.pdf", "archive.zip", "data.bin"]
        for filename in other_files:
            assert classify_file(filename) == FileType.OTHER, f"{filename} should be OTHER"

    def test_is_video_file(self):
        """is_video_file 헬퍼 테스트"""
        assert is_video_file("movie.mp4") is True
        assert is_video_file("song.mp3") is False

    def test_is_audio_file(self):
        """is_audio_file 헬퍼 테스트"""
        assert is_audio_file("song.mp3") is True
        assert is_audio_file("movie.mp4") is False

    def test_case_insensitive(self):
        """대소문자 구분 없음 테스트"""
        assert classify_file("MOVIE.MP4") == FileType.VIDEO
        assert classify_file("Video.MKV") == FileType.VIDEO

    def test_file_classifier_class(self):
        """FileClassifier 클래스 테스트"""
        classifier = FileClassifier()

        # 기본 분류
        assert classifier.classify("movie.mp4") == FileType.VIDEO

        # 커스텀 확장자 추가
        classifier.add_extension(".custom", FileType.VIDEO)
        assert classifier.classify("file.custom") == FileType.VIDEO

    def test_get_statistics(self):
        """통계 기능 테스트"""
        classifier = FileClassifier()
        files = ["a.mp4", "b.mp4", "c.mp3", "d.srt", "e.bin"]
        stats = classifier.get_statistics(files)

        assert stats[FileType.VIDEO] == 2
        assert stats[FileType.AUDIO] == 1
        assert stats[FileType.SUBTITLE] == 1
        assert stats[FileType.OTHER] == 1


class TestDatabase:
    """데이터베이스 테스트"""

    @pytest.fixture
    def db(self):
        """임시 데이터베이스"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        db = Database(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_insert_file(self, db):
        """파일 삽입 테스트"""
        record = FileRecord(
            path="/test/movie.mp4",
            filename="movie.mp4",
            extension=".mp4",
            size_bytes=1024000,
            file_type="video",
            parent_folder="/test",
            scan_status="scanned",
        )

        record_id = db.insert_file(record)
        assert record_id > 0

    def test_get_file_by_path(self, db):
        """경로로 파일 조회 테스트"""
        record = FileRecord(
            path="/test/movie.mp4",
            filename="movie.mp4",
            extension=".mp4",
            size_bytes=1024000,
            file_type="video",
            parent_folder="/test",
        )
        db.insert_file(record)

        found = db.get_file_by_path("/test/movie.mp4")
        assert found is not None
        assert found.filename == "movie.mp4"
        assert found.size_bytes == 1024000

    def test_insert_files_batch(self, db):
        """배치 삽입 테스트"""
        records = [
            FileRecord(path=f"/test/file{i}.mp4", filename=f"file{i}.mp4",
                      extension=".mp4", size_bytes=1000 * i, file_type="video")
            for i in range(10)
        ]

        count = db.insert_files_batch(records)
        assert count == 10
        assert db.get_file_count() == 10

    def test_get_statistics(self, db):
        """통계 조회 테스트"""
        records = [
            FileRecord(path="/test/v1.mp4", filename="v1.mp4", extension=".mp4",
                      size_bytes=1000, file_type="video"),
            FileRecord(path="/test/v2.mp4", filename="v2.mp4", extension=".mp4",
                      size_bytes=2000, file_type="video"),
            FileRecord(path="/test/a1.mp3", filename="a1.mp3", extension=".mp3",
                      size_bytes=500, file_type="audio"),
        ]
        db.insert_files_batch(records)

        stats = db.get_statistics()
        assert stats['total_files'] == 3
        assert stats['total_size'] == 3500
        assert stats['by_type']['video']['count'] == 2
        assert stats['by_type']['audio']['count'] == 1

    def test_file_exists(self, db):
        """파일 존재 확인 테스트"""
        record = FileRecord(path="/test/exists.mp4", filename="exists.mp4",
                           extension=".mp4", file_type="video")
        db.insert_file(record)

        assert db.file_exists("/test/exists.mp4") is True
        assert db.file_exists("/test/not_exists.mp4") is False

    def test_checkpoint(self, db):
        """체크포인트 테스트"""
        checkpoint = ScanCheckpoint(
            scan_id="test-scan",
            total_files=1000,
            processed_files=500,
            last_path="/test/current.mp4",
            status="in_progress",
        )

        db.save_checkpoint(checkpoint)

        loaded = db.get_checkpoint("test-scan")
        assert loaded is not None
        assert loaded.total_files == 1000
        assert loaded.processed_files == 500

    def test_update_checkpoint_progress(self, db):
        """체크포인트 진행 업데이트 테스트"""
        checkpoint = ScanCheckpoint(scan_id="test-scan", total_files=1000)
        db.save_checkpoint(checkpoint)

        db.update_checkpoint_progress("test-scan", "/test/file500.mp4", 500)

        loaded = db.get_checkpoint("test-scan")
        assert loaded.processed_files == 500
        assert loaded.last_path == "/test/file500.mp4"


class TestArchiveScanner:
    """아카이브 스캐너 통합 테스트"""

    @pytest.fixture
    def smb_config(self):
        """SMB 설정"""
        return SMBConfig(
            server=TEST_SERVER,
            share=TEST_SHARE,
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
        )

    @pytest.fixture
    def connector(self, smb_config):
        """SMB 커넥터"""
        conn = SMBConnector(smb_config)
        yield conn
        if conn.is_connected:
            conn.disconnect()

    @pytest.fixture
    def db(self):
        """임시 데이터베이스"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        db = Database(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_quick_scan(self, connector, db):
        """빠른 스캔 테스트"""
        scanner = ArchiveScanner(
            connector=connector,
            database=db,
            archive_path=TEST_ARCHIVE_PATH,
        )

        stats = scanner.quick_scan()

        assert stats['total_files'] > 0
        assert stats['total_size'] > 0
        assert 'video' in stats['by_type']

        print(f"\nQuick scan results:")
        print(f"  Total files: {stats['total_files']:,}")
        print(f"  Total size: {stats['total_size'] / (1024**4):.2f} TB")
        for ft, data in stats['by_type'].items():
            print(f"  {ft}: {data['count']:,} files ({data['size'] / (1024**3):.2f} GB)")

    def test_full_scan(self, connector, db):
        """전체 스캔 테스트 (DB 저장)"""
        scanner = ArchiveScanner(
            connector=connector,
            database=db,
            archive_path=TEST_ARCHIVE_PATH,
            batch_size=50,
        )

        # 진행률 출력
        def progress_callback(progress: ScanProgress):
            print(f"\r{progress}", end="", flush=True)

        scanner.set_progress_callback(progress_callback)

        result = scanner.scan(count_first=True)

        print(f"\n\nScan complete!")
        print(f"  Scan ID: {result.scan_id}")
        print(f"  Total files: {result.total_files:,}")
        print(f"  Total size: {result.total_size / (1024**4):.2f} TB")
        print(f"  Duration: {result.duration_seconds:.1f}s")
        print(f"  Errors: {len(result.errors)}")

        # DB 확인
        db_stats = db.get_statistics()
        assert db_stats['total_files'] == result.total_files

    def test_scan_progress(self):
        """ScanProgress 출력 테스트"""
        progress = ScanProgress(
            scan_id="test",
            total_files=1000,
            processed_files=500,
            current_path="/test/file.mp4",
            files_per_second=100.5,
            estimated_remaining=5.0,
        )

        assert progress.percentage == 50.0
        assert "50.0%" in str(progress)
        assert "100.5 files/s" in str(progress)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
