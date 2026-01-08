# Issue #1 해결 계획: SMB 네트워크 접속 테스트

## 문제 요약
- **오류**: 시스템 오류 67 (네트워크 이름을 찾을 수 없음)
- **서버**: 10.10.100.122 (GGPWSOP)
- **상태**: 포트 445 열림, Ping 정상, 그러나 SMB 연결 실패

---

## Phase 1: 클라이언트 측 진단 (로컬 PC)

### 1.1 SMB 클라이언트 서비스 확인

```powershell
# Workstation 서비스 상태 확인
Get-Service -Name LanmanWorkstation

# SMB 클라이언트 설정 확인
Get-SmbClientConfiguration | Select-Object *
```

### 1.2 SMB 프로토콜 버전 확인

```powershell
# 활성화된 SMB 버전 확인
Get-SmbServerConfiguration | Select-Object EnableSMB1Protocol, EnableSMB2Protocol

# SMB1 활성화 여부 (Windows 기능)
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
```

### 1.3 NetBIOS over TCP/IP 설정 확인

```powershell
# 네트워크 어댑터별 NetBIOS 설정
Get-NetAdapterBinding -ComponentID ms_netbios

# NetBIOS 상태 확인 (Wi-Fi 어댑터)
Get-WmiObject Win32_NetworkAdapterConfiguration |
    Where-Object { $_.IPEnabled -eq $true } |
    Select-Object Description, TcpipNetbiosOptions
```
- `0` = Default (DHCP)
- `1` = Enable NetBIOS
- `2` = Disable NetBIOS

### 1.4 방화벽 규칙 확인

```powershell
# SMB 관련 방화벽 규칙
Get-NetFirewallRule -DisplayName "*SMB*" | Select-Object DisplayName, Enabled, Direction
```

---

## Phase 2: 서버 측 진단 (NAS 서버)

### 2.1 NAS 관리 페이지 확인
- [ ] NAS 웹 관리자 로그인 (http://10.10.100.122)
- [ ] SMB/CIFS 서비스 활성화 여부 확인
- [ ] 공유 폴더 목록 및 경로 확인
- [ ] 사용자 권한 설정 확인

### 2.2 공유 폴더 경로 검증
현재 추정 경로:
```
\\GGPWSOP\docker\GGPNAs\ARCHIVE
```

가능한 대안 경로:
```
\\10.10.100.122\ARCHIVE
\\10.10.100.122\GGPNAs
\\10.10.100.122\docker
\\10.10.100.122\share
\\10.10.100.122\public
```

### 2.3 SMB 버전 호환성
| NAS SMB 버전 | Windows 지원 |
|-------------|-------------|
| SMB1 | Win7+ (비활성화 기본) |
| SMB2 | Win7+ |
| SMB3 | Win8+ |

---

## Phase 3: 연결 테스트

### 3.1 다양한 방법으로 연결 시도

```powershell
# 방법 1: IP + 공유명
net use Z: \\10.10.100.122\ARCHIVE /user:GGP "!@QW12qw"

# 방법 2: 호스트명 + 공유명
net use Z: \\GGPWSOP\ARCHIVE /user:GGP "!@QW12qw"

# 방법 3: 도메인 포함
net use Z: \\10.10.100.122\ARCHIVE /user:GGPWSOP\GGP "!@QW12qw"

# 방법 4: 익명 접근 시도
net use Z: \\10.10.100.122\ARCHIVE

# 방법 5: 자격 증명 명시적 전달
$cred = Get-Credential
New-PSDrive -Name Z -PSProvider FileSystem -Root "\\10.10.100.122\ARCHIVE" -Credential $cred
```

### 3.2 Windows 탐색기로 직접 접근

```
실행 (Win+R) → \\10.10.100.122
```

### 3.3 smbclient 테스트 (WSL 사용 가능 시)

```bash
# WSL에서 smbclient 사용
smbclient -L //10.10.100.122 -U GGP

# 특정 공유 접속
smbclient //10.10.100.122/ARCHIVE -U GGP
```

---

## Phase 4: 대안 솔루션

### 4.1 SMB1 프로토콜 활성화 (임시)

```powershell
# SMB1 클라이언트 활성화 (관리자 권한)
Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol-Client -NoRestart

# 재부팅 후 확인
```

> ⚠️ **보안 경고**: SMB1은 보안 취약점이 있어 권장되지 않음

### 4.2 IP NAT 드라이버 비활성화

```powershell
# 장치 관리자에서 숨김 장치 표시 후
# Network → IP Network Address Translator 비활성화
# 재부팅
```

### 4.3 TCP/IP 스택 재설정

```powershell
# 관리자 권한으로 실행
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
# 재부팅
```

### 4.4 Python SMB 라이브러리로 직접 접근

```python
# smbprotocol 사용 (Windows net use 우회)
from smbclient import register_session, listdir

register_session("10.10.100.122", username="GGP", password="!@QW12qw")
files = listdir(r"\\10.10.100.122\ARCHIVE")
print(files)
```

### 4.5 WebDAV 대안 (NAS 지원 시)

```powershell
# WebDAV 클라이언트 설치
Install-WindowsFeature WebDAV-Redirector

# WebDAV 마운트
net use W: http://10.10.100.122/webdav /user:GGP "!@QW12qw"
```

---

## Phase 5: 문제별 해결책 매핑

| 문제 | 해결책 |
|------|--------|
| SMB1만 지원하는 구형 NAS | Phase 4.1 - SMB1 활성화 |
| NetBIOS 비활성화 | Phase 1.3 - NetBIOS 활성화 |
| 잘못된 공유 경로 | Phase 2.2 - NAS에서 정확한 경로 확인 |
| IP NAT 충돌 | Phase 4.2 - NAT 드라이버 비활성화 |
| Windows SMB 스택 오류 | Phase 4.3 - TCP/IP 재설정 |
| Windows 문제 우회 필요 | Phase 4.4 - Python SMB 라이브러리 |

---

## 실행 체크리스트

### 클라이언트 측 (즉시 실행 가능)
- [ ] `Get-SmbClientConfiguration` 실행
- [ ] `Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` 확인
- [ ] NetBIOS 설정 확인
- [ ] Windows 탐색기에서 `\\10.10.100.122` 직접 접근 시도
- [ ] Python smbprotocol 설치 및 테스트

### 서버 측 (NAS 관리자 접근 필요)
- [ ] NAS 웹 관리 페이지 접속
- [ ] SMB 서비스 상태 확인
- [ ] 정확한 공유 폴더명 확인
- [ ] 사용자 권한 확인

---

## 예상 소요 시간

| Phase | 작업 | 예상 시간 |
|-------|------|----------|
| 1 | 클라이언트 진단 | 15분 |
| 2 | 서버 진단 | 30분 |
| 3 | 연결 테스트 | 15분 |
| 4 | 대안 적용 | 30분 |
| **Total** | | **~1.5시간** |

---

## 다음 단계

1. **Phase 1 실행** → 클라이언트 설정 확인
2. 결과에 따라 Phase 2 또는 Phase 4 진행
3. 연결 성공 시 Issue #1 Close → Issue #2 진행

---

**작성일**: 2025-11-27
**관련 이슈**: https://github.com/garimto81/archive-analyzer/issues/1

---

## 해결 결과 (2025-11-27)

### 문제 원인
- Windows `net use` 명령어의 SMB 스택 문제
- 공유 경로가 `\\10.10.100.122\docker\GGPNAs\ARCHIVE`가 아닌 `\\10.10.100.122\docker` 루트 공유

### 해결 방법
**Python smbprotocol 라이브러리 사용** (Windows 네이티브 SMB 우회)

```bash
pip install smbprotocol
```

```python
from smbclient import register_session, listdir

register_session("10.10.100.122", username="GGP", password="!@QW12qw")
files = listdir(r"\\10.10.100.122\docker\GGPNAs\ARCHIVE")
```

### 스캔 결과

| 항목 | 값 |
|------|-----|
| **총 파일 수** | 1,418개 |
| **총 디렉토리** | 162개 |
| **총 용량** | 18.03 TB |
| **비디오 파일** | 1,271개 (15.34 TB) |
| **기타 파일** | 147개 (2.68 TB) |

### 아카이브 구조
```
\\10.10.100.122\docker\GGPNAs\ARCHIVE
├── MPP (3 items)
├── WSOP (4 items)
├── GGMillions (15 items)
├── PAD (3 items)
└── HCL (3 items)
```

### 상태
**✅ RESOLVED** - smbprotocol로 네트워크 접근 성공
