#!/usr/bin/env python
"""아카이브 파일 수 및 용량 카운트 스크립트"""

from smbclient import listdir, stat
import os
from collections import defaultdict

BASE_PATH = r"\\10.10.100.122\docker\GGPNAs\ARCHIVE"

# 파일 확장자별 분류
VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts'}
AUDIO_EXTS = {'.mp3', '.aac', '.flac', '.wav', '.m4a', '.ogg'}
SUBTITLE_EXTS = {'.srt', '.ass', '.ssa', '.vtt', '.sub'}
META_EXTS = {'.nfo', '.xml', '.json'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}

def classify_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in VIDEO_EXTS:
        return 'video'
    elif ext in AUDIO_EXTS:
        return 'audio'
    elif ext in SUBTITLE_EXTS:
        return 'subtitle'
    elif ext in META_EXTS:
        return 'metadata'
    elif ext in IMAGE_EXTS:
        return 'image'
    else:
        return 'other'

def scan_recursive(path, stats, depth=0):
    """재귀적으로 디렉토리 스캔"""
    try:
        items = listdir(path)
        for item in items:
            if item.startswith('.'):
                continue
            full_path = os.path.join(path, item)
            try:
                s = stat(full_path)
                if s.st_file_attributes & 0x10:  # Directory
                    stats['dirs'] += 1
                    scan_recursive(full_path, stats, depth + 1)
                else:
                    stats['files'] += 1
                    stats['size'] += s.st_size
                    file_type = classify_file(item)
                    stats['types'][file_type] += 1
                    stats['type_size'][file_type] += s.st_size

                    # 진행 상황 출력
                    if stats['files'] % 100 == 0:
                        print(f"  Scanned {stats['files']} files...")
            except Exception as e:
                stats['errors'] += 1
    except Exception as e:
        stats['errors'] += 1

def format_size(bytes_size):
    """바이트를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def main():
    print("=== Archive File Count ===")
    print(f"Target: {BASE_PATH}")
    print()
    print("Scanning... (this may take a while)")
    print()

    stats = {
        'files': 0,
        'dirs': 0,
        'size': 0,
        'errors': 0,
        'types': defaultdict(int),
        'type_size': defaultdict(int)
    }

    scan_recursive(BASE_PATH, stats)

    print()
    print("=" * 50)
    print("=== Summary ===")
    print(f"Total Files: {stats['files']:,}")
    print(f"Total Directories: {stats['dirs']:,}")
    print(f"Total Size: {format_size(stats['size'])}")
    print(f"Errors: {stats['errors']}")
    print()
    print("=== File Types ===")
    for file_type in ['video', 'audio', 'subtitle', 'metadata', 'image', 'other']:
        count = stats['types'][file_type]
        size = stats['type_size'][file_type]
        if count > 0:
            print(f"  {file_type}: {count:,} files ({format_size(size)})")

if __name__ == "__main__":
    main()
