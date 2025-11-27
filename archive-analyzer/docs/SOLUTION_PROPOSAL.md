# Archive Analyzer 솔루션 제안서

## 1. SMB 네트워크 접속 문제 해결

### 1.1 오류 67 원인 및 해결책

| 원인 | 해결 방법 | 참조 |
|------|-----------|------|
| SMB 프로토콜 비활성화 | Windows 기능에서 SMB 1.0/CIFS 활성화 | [Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/system-error-67-network-name-cannot-be-found) |
| IP NAT 드라이버 충돌 | 장치 관리자에서 IP NAT 드라이버 비활성화 후 재부팅 | [MiniTool](https://www.minitool.com/news/system-error-67.html) |
| NetBIOS over TCP/IP 비활성 | 네트워크 어댑터 설정에서 활성화 | [Windows Club](https://www.thewindowsclub.com/system-error-67-has-occurred-the-network-name-cannot-be-found) |
| 공유 이름 오류 | `net view \\서버명`으로 정확한 공유명 확인 | [Stack Overflow](https://stackoverflow.com/questions/61697532/how-do-i-fix-net-use-system-error-67-has-occurred) |

### 1.2 Windows 명령어 진단 절차

```powershell
# 1. SMB 클라이언트 기능 확인
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol

# 2. NetBIOS over TCP/IP 활성화 확인
Get-NetAdapterBinding -ComponentID ms_netbios

# 3. SMB 프로토콜 버전 확인
Get-SmbConnection

# 4. 공유 목록 확인 (성공 시)
net view \\10.10.100.122
```

---

## 2. Python SMB 라이브러리 (네트워크 직접 접근)

### 2.1 추천 라이브러리 비교

| 라이브러리 | SMB 버전 | Async | 대용량 처리 | 추천도 |
|-----------|---------|-------|------------|--------|
| **[smbprotocol](https://github.com/jborean93/smbprotocol)** | SMB 2/3 | 부분 지원 | ✅ | ⭐⭐⭐⭐⭐ |
| **[aiosmb](https://github.com/skelsec/aiosmb)** | SMB 2/3 | ✅ 완전 비동기 | ✅ | ⭐⭐⭐⭐⭐ |
| [pysmb](https://github.com/miketeo/pysmb) | SMB 1/2 | ❌ | ⚠️ 제한적 | ⭐⭐⭐ |

### 2.2 smbprotocol 사용 예시

```python
from smbclient import register_session, scandir, stat
import smbclient

# 세션 등록
register_session("10.10.100.122", username="GGP", password="!@QW12qw")

# 디렉토리 스캔 (메타데이터 포함)
for entry in scandir(r"\\10.10.100.122\ARCHIVE"):
    info = entry.smb_info  # stat() 호출 없이 메타데이터 접근
    print(f"{entry.name}: {info.file_size} bytes")
```

### 2.3 aiosmb (비동기 대용량 처리)

```python
import asyncio
from aiosmb.commons.connection.factory import SMBConnectionFactory

async def scan_archive():
    url = 'smb2+ntlm-password://GGP:password@10.10.100.122/ARCHIVE'
    conn = SMBConnectionFactory.from_url(url)

    async with conn.get_connection() as connection:
        async with connection.create_directory('') as directory:
            async for entry in directory.list():
                print(entry.name, entry.size)

asyncio.run(scan_archive())
```

---

## 3. 미디어 메타데이터 추출 도구

### 3.1 추천 GitHub 프로젝트

| 프로젝트 | 설명 | GitHub |
|---------|------|--------|
| **ffprobe-python** | FFprobe 래퍼, 간단한 API | [gbstack/ffprobe-python](https://github.com/gbstack/ffprobe-python) |
| **ffprobe3-python3** | Python 3 전용, JSON 출력 | [jboy/ffprobe3-python3](https://github.com/jboy/ffprobe3-python3) |
| **Video-Metadata-Extractor** | Excel 리포트 생성 | [CTinMich/Video-Metadata-Extractor](https://github.com/CTinMich/Video-Metadata-Extractor) |
| **pymediainfo** | MediaInfo 래퍼 | [sbraz/pymediainfo](https://github.com/sbraz/pymediainfo) |

### 3.2 FFprobe 원격 파일 분석

```python
import subprocess
import json

def extract_metadata(smb_path: str) -> dict:
    """SMB 경로에서 직접 메타데이터 추출 (FFprobe)"""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', '-show_streams',
        smb_path  # FFprobe는 SMB 경로 직접 지원
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# 사용 예시
metadata = extract_metadata(r"\\10.10.100.122\ARCHIVE\movie.mp4")
print(f"Duration: {metadata['format']['duration']}s")
print(f"Codec: {metadata['streams'][0]['codec_name']}")
```

---

## 4. OTT 미디어 관리 오픈소스 솔루션

### 4.1 메타데이터 스캐너

| 솔루션 | 특징 | 용도 | 링크 |
|--------|------|------|------|
| **Jellyfin** | 완전 무료, 오픈소스, TMDb/TVDB 연동 | 미디어 서버 + 카탈로그 | [jellyfin.org](https://jellyfin.org) |
| **tinyMediaManager** | NFO 생성, 미디어 정리 | 오프라인 카탈로그 | [tinyMediaManager](https://www.tinymediamanager.org/) |
| **Telemeta** | 멀티미디어 아카이브 관리 (MAM) | 전문 아카이브 | [telemeta.org](https://telemeta.org/) |

### 4.2 Jellyfin 메타데이터 플러그인 활용

Jellyfin의 메타데이터 스캐너를 참고하여 자체 구현 가능:

- **TheTVDB / TMDb 연동** - 자동 메타데이터 수집
- **NFO 파일 파싱** - 기존 메타데이터 활용
- **커스텀 스크래퍼** - 플러그인 아키텍처

참조: [awesome-jellyfin](https://github.com/awesome-jellyfin/awesome-jellyfin)

---

## 5. 최종 아키텍처 제안

### 5.1 권장 기술 스택

```
┌─────────────────────────────────────────────────────────────────┐
│                    Archive Analyzer v1.0                         │
├─────────────────────────────────────────────────────────────────┤
│  네트워크 계층                                                    │
│  ├── aiosmb (비동기 SMB 클라이언트)                               │
│  └── smbprotocol (폴백용)                                        │
├─────────────────────────────────────────────────────────────────┤
│  분석 계층                                                        │
│  ├── FFprobe (비디오 기술 메타데이터)                             │
│  ├── pymediainfo (추가 미디어 정보)                               │
│  └── NFO/XML Parser (콘텐츠 메타데이터)                           │
├─────────────────────────────────────────────────────────────────┤
│  저장 계층                                                        │
│  ├── SQLite (로컬 DB)                                            │
│  └── JSON Export (OTT 백엔드용)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 구현 우선순위

| Phase | 작업 | 도구 |
|-------|------|------|
| **1** | SMB 연결 테스트 | smbprotocol |
| **2** | 파일 스캔 (1869개) | aiosmb (async) |
| **3** | 메타데이터 추출 | FFprobe + pymediainfo |
| **4** | 카탈로그 생성 | SQLite + JSON |
| **5** | 리포트 생성 | Pandas + Matplotlib |

### 5.3 의존성 설치

```bash
pip install smbprotocol aiosmb pymediainfo ffmpeg-python
```

---

## 6. 참고 자료

### SMB 오류 해결
- [Microsoft Learn - System error 67](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/system-error-67-network-name-cannot-be-found)
- [Windows 10 Forums - Error 67 해결](https://www.tenforums.com/network-sharing/164814-windows-pe-system-error-67-network-name-cannot-found.html)

### Python SMB 라이브러리
- [smbprotocol (PyPI)](https://pypi.org/project/smbprotocol/)
- [aiosmb (GitHub)](https://github.com/skelsec/aiosmb)
- [pysmb 문서](https://pysmb.readthedocs.io/)

### 미디어 메타데이터
- [ffprobe-python (GitHub)](https://github.com/gbstack/ffprobe-python)
- [Video-Metadata-Extractor (GitHub)](https://github.com/CTinMich/Video-Metadata-Extractor)

### OTT / 미디어 서버
- [Jellyfin vs Plex 비교](https://www.howtogeek.com/876195/why-jellyfin-is-the-plex-alternative-youve-been-waiting-for/)
- [awesome-jellyfin (GitHub)](https://github.com/awesome-jellyfin/awesome-jellyfin)

---

**작성일**: 2025-11-27
**버전**: 1.0.0
