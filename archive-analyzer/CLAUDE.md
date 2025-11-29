# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Archive Analyzer는 OTT 솔루션을 위한 미디어 아카이브 분석 도구입니다. SMB 네트워크를 통해 원격 NAS에 저장된 미디어 파일(18TB+)의 메타데이터를 추출하고 카탈로그를 생성합니다.

**주요 대상**: WSOP, HCL, PAD 등 포커 방송 콘텐츠 아카이브 (1,400+ 파일)

## Build & Test Commands

```powershell
# 의존성 설치
pip install -e ".[dev,media]"

# 테스트 실행
pytest tests/ -v

# 테스트 (커버리지 포함)
pytest tests/ -v --cov=src/archive_analyzer --cov-report=term

# 단일 테스트 파일 실행
pytest tests/test_scanner.py -v

# 특정 테스트만 실행
pytest tests/test_media_extractor.py::test_ffprobe_extract -v

# 린터
ruff check src/
black --check src/

# 타입 체크
mypy src/archive_analyzer/
```

## Architecture

```
src/archive_analyzer/
├── config.py           # SMBConfig, AnalyzerConfig (환경변수/JSON 로드)
├── smb_connector.py    # SMB 2/3 네트워크 연결 (smbprotocol 기반)
├── file_classifier.py  # 파일 유형 분류 (video, audio, subtitle, metadata)
├── scanner.py          # 재귀 디렉토리 스캔, 체크포인트 기반 재개
├── database.py         # SQLite 저장 (files, media_info, checkpoints 테이블)
├── media_extractor.py  # FFprobe 기반 메타데이터 추출
└── report_generator.py # Markdown/JSON/Console 리포트 생성
```

### 데이터 흐름

1. `SMBConnector` → SMB 세션 관리, 파일 탐색
2. `ArchiveScanner` → 재귀 스캔, `Database`에 파일 정보 저장
3. `SMBMediaExtractor` → 파일 일부 다운로드 → FFprobe 분석
4. `ReportGenerator` → 통계 집계, 스트리밍 적합성 평가

### 주요 클래스

| 클래스 | 역할 | 위치 |
|--------|------|------|
| `SMBConnector` | SMB 연결/재시도/디렉토리 스캔 | `smb_connector.py:64` |
| `ArchiveScanner` | 체크포인트 기반 스캔 | `scanner.py:68` |
| `FFprobeExtractor` | 로컬 파일 메타데이터 추출 | `media_extractor.py:117` |
| `SMBMediaExtractor` | SMB 파일 → 임시 다운로드 → 분석 | `media_extractor.py:262` |
| `ReportGenerator` | DB 쿼리 → 리포트 생성 | `report_generator.py:235` |

## Key Scripts

```powershell
# 아카이브 스캔 실행
python scripts/run_scan.py

# 메타데이터 추출 (네트워크 드라이브)
python scripts/extract_metadata_netdrive.py

# 리포트 생성
python scripts/generate_report.py

# SMB 연결 테스트
python scripts/test_smb.py

# 실패한 항목 재처리
python scripts/retry_failed.py
```

## Configuration

SMB 연결 설정은 환경변수 또는 JSON 파일로 관리:

```python
# 환경변수
SMB_SERVER=10.10.100.122
SMB_SHARE=docker
SMB_USERNAME=GGP
SMB_PASSWORD=****
ARCHIVE_PATH=GGPNAs/ARCHIVE

# 코드에서 로드
config = AnalyzerConfig.from_env()
config = AnalyzerConfig.from_file("config.json")
```

## Database Schema

- **files**: 파일 경로, 크기, 유형, 스캔 상태
- **media_info**: 비디오/오디오 코덱, 해상도, 재생시간, 비트레이트
- **scan_checkpoints**: 스캔 재개를 위한 체크포인트

## External Dependencies

- **FFprobe**: 시스템에 설치 필요 (`ffprobe` 명령어 PATH에 있어야 함)
- **smbprotocol**: SMB 2/3 네트워크 접근
- **rapidfuzz**: 파일명 퍼지 매칭 (클립 매칭용)

## File Type Classification

| FileType | 확장자 |
|----------|--------|
| video | .mp4, .mkv, .mov, .mxf, .webm, .ts 등 |
| audio | .mp3, .aac, .flac, .wav 등 |
| subtitle | .srt, .ass, .vtt, .smi 등 |
| metadata | .nfo, .xml, .json 등 |
| image | .jpg, .png, .webp 등 |

## Streaming Compatibility

OTT 호환 판정 기준:
- **코덱**: h264, hevc, vp9, av1
- **컨테이너**: mp4, webm, mov, matroska
- MXF 등 방송용 포맷은 트랜스코딩 필요로 분류
