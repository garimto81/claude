# VSeeFace 설치 및 설정 가이드

**버전**: 1.0.0
**작성일**: 2026-01-04
**대상**: youtuber_vertuber 프로젝트 (PRD-0001)

---

## 개요

이 가이드는 VSeeFace를 설치하고 VMC Protocol을 활성화하여 youtuber_vertuber 프로젝트와 연동하는 방법을 설명합니다.

---

## 시스템 요구사항

### 최소 사양
- **OS**: Windows 10 (64-bit) 이상
- **CPU**: Intel i5 4세대 이상 또는 동급
- **RAM**: 8GB 이상
- **GPU**: DirectX 11 지원 GPU
- **웹캠**: HD 웹캠 (720p 이상) 권장

### 권장 사양
- **OS**: Windows 11 (64-bit)
- **CPU**: Intel i7 8세대 이상 또는 AMD Ryzen 5 3600 이상
- **RAM**: 16GB 이상
- **GPU**: NVIDIA GTX 1060 / AMD RX 580 이상
- **웹캠**: Full HD 웹캠 (1080p)

---

## 1단계: VSeeFace 다운로드

### 1.1 공식 다운로드

VSeeFace 공식 사이트에서 최신 버전을 다운로드합니다.

**다운로드 링크**: https://www.vseeface.icu/

**권장 버전**: v1.13.38+ (2024년 이후 버전)

### 1.2 설치 방법

1. 다운로드한 ZIP 파일을 원하는 폴더에 압축 해제
   ```
   C:\VSeeFace\  (권장 경로)
   ```

2. `VSeeFace.exe` 파일 확인

3. Windows Defender 예외 설정 (선택사항)
   - 설정 → 업데이트 및 보안 → Windows 보안 → 바이러스 및 위협 방지
   - 제외 항목 추가 → `C:\VSeeFace\` 폴더 추가

---

## 2단계: VRM 아바타 준비

### 2.1 VRoid Hub에서 아바타 다운로드

VRoid Hub는 무료 VRM 아바타를 제공하는 플랫폼입니다.

**VRoid Hub**: https://hub.vroid.com/

**추천 검색어**:
- "programmer" (프로그래머 컨셉)
- "coder" (코더 컨셉)
- "tech" (테크 컨셉)
- "casual" (캐주얼 의상)

### 2.2 아바타 다운로드 절차

1. VRoid Hub 계정 생성 (Google/Twitter 로그인 가능)
2. 검색창에서 원하는 컨셉 검색
3. 라이선스 확인 (**CC0, CC BY 4.0 권장**)
4. "Download" 버튼 클릭 → VRM 파일 저장
5. 다운로드한 VRM 파일을 `C:\VSeeFace\Models\` 폴더에 저장

### 2.3 권장 아바타 (2026년 기준)

| 아바타 이름 | 라이선스 | 특징 |
|-----------|---------|------|
| "Simple Coder" | CC0 | 안경, 후드티, 중성적 외모 |
| "Tech Girl" | CC BY 4.0 | 헤드셋, 캐주얼 의상 |
| "Developer Boy" | CC BY 4.0 | 체크 셔츠, 노트북 소지 |

---

## 3단계: VSeeFace 초기 설정

### 3.1 첫 실행

1. `VSeeFace.exe` 실행
2. "Select VRM Model" 클릭 → 다운로드한 VRM 파일 선택
3. 아바타가 화면에 표시되는지 확인

### 3.2 웹캠 설정

1. VSeeFace 상단 메뉴 → "Settings"
2. "Camera" 탭 선택
3. "Camera Device" 드롭다운에서 웹캠 선택
4. "Resolution"을 **1280x720** 또는 **1920x1080**으로 설정
5. "FPS"를 **30fps**로 설정 (권장)

### 3.3 얼굴 추적 테스트

1. 웹캠 앞에서 고개를 끄덕이거나 좌우로 움직이기
2. 아바타가 실시간으로 따라하는지 확인
3. 눈 깜빡임, 입 움직임 동기화 확인

**문제 해결**:
- 추적이 불안정한 경우: 조명을 밝게 하거나 웹캠 위치 조정
- 아바타가 움직이지 않는 경우: "Settings" → "Camera" → "Restart Tracking" 클릭

---

## 4단계: VMC Protocol 활성화

### 4.1 VMC Protocol이란?

VMC (Virtual Motion Capture) Protocol은 VSeeFace의 모션 데이터(BlendShape, 위치, 회전)를 외부 애플리케이션으로 전송하는 프로토콜입니다.

**프로토콜**: OSC (Open Sound Control)
**기본 포트**: 39539
**전송 형식**: UDP

### 4.2 VMC Protocol 설정

1. VSeeFace 실행
2. 상단 메뉴 → "Settings" → "VMC Protocol" 탭
3. **"Enable VMC Protocol"** 체크박스 활성화
4. 포트 설정:
   ```
   Port: 39539
   IP Address: 127.0.0.1 (localhost)
   ```
5. "Send BlendShapes" 옵션 활성화
6. "Send Rate"를 **30 FPS**로 설정
7. "Apply" 버튼 클릭

### 4.3 VMC Protocol 테스트

VSeeFace가 VMC 데이터를 전송하는지 확인하려면 OSC 디버그 도구를 사용할 수 있습니다.

**권장 도구**: [oscmon](https://github.com/kineticaudio/oscmon) (무료)

1. oscmon 설치 및 실행
2. Port를 **39539**로 설정
3. "Listen" 버튼 클릭
4. VSeeFace에서 표정을 바꾸거나 고개를 움직이기
5. oscmon에서 `/VMC/Ext/Blend/Val` 메시지 확인

**예상 출력**:
```
/VMC/Ext/Blend/Val "Joy" 0.85
/VMC/Ext/Blend/Val "Angry" 0.0
/VMC/Ext/Blend/Val "Sorrow" 0.0
```

---

## 5단계: 배경 투명화 설정 (OBS 연동용)

### 5.1 투명 배경 활성화

1. VSeeFace → "Settings" → "General" 탭
2. **"Transparent Background"** 체크박스 활성화
3. "Apply" 버튼 클릭
4. VSeeFace 배경이 투명해지는지 확인 (체크무늬 패턴 표시)

### 5.2 카메라 뷰 설정

1. VSeeFace 화면에서 마우스 휠로 줌 조정
2. 마우스 드래그로 아바타 위치 조정
3. **권장 프레임**: 상반신(어깨 위) 중심 구도
4. 아바타가 320x180 영역에 맞게 크기 조정

---

## 6단계: 자동 시작 설정 (선택사항)

### 6.1 Windows 시작 프로그램 등록

1. `Win + R` → `shell:startup` 입력 → Enter
2. VSeeFace 바로가기를 시작 프로그램 폴더에 복사

### 6.2 VSeeFace 자동 설정 복원

VSeeFace는 마지막 설정을 자동으로 저장합니다.

**설정 파일 경로**:
```
%APPDATA%\VSeeFace\config.json
```

**백업 권장**: 설정 완료 후 `config.json` 파일을 별도 저장

---

## 7단계: youtuber_vertuber 연동 확인

### 7.1 VMC Client 테스트

youtuber_vertuber 프로젝트의 VMC Client가 VSeeFace와 연결되는지 확인합니다.

```bash
# 프로젝트 디렉토리로 이동
cd D:\AI\claude01\youtuber_vertuber

# packages/vtuber 패키지로 이동 (Phase 1 완료 후)
cd packages/vtuber

# VMC Client 테스트 실행
pnpm test vmc-client.test.ts
```

**예상 결과**:
```
✓ VMC Client 연결 성공
✓ BlendShape 데이터 수신 (Joy, Angry, Sorrow, Fun)
✓ 연결 상태 모니터링 (health check)
```

---

## 문제 해결 (Troubleshooting)

### 문제 1: VSeeFace가 실행되지 않음

**증상**: VSeeFace.exe 실행 시 오류 또는 즉시 종료

**해결**:
1. DirectX 11 설치 확인
   - [DirectX End-User Runtime](https://www.microsoft.com/en-us/download/details.aspx?id=35) 다운로드 및 설치
2. Visual C++ Redistributable 설치
   - [VC++ 2015-2022 Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) 다운로드 및 설치
3. 안티바이러스 예외 설정

### 문제 2: 웹캠이 인식되지 않음

**증상**: VSeeFace "Camera Device"에서 웹캠이 보이지 않음

**해결**:
1. 다른 프로그램(Zoom, Skype)이 웹캠을 사용 중인지 확인 → 종료
2. Windows 설정 → 개인 정보 → 카메라 → VSeeFace 권한 허용
3. 웹캠 드라이버 업데이트

### 문제 3: VMC Protocol 데이터가 수신되지 않음

**증상**: oscmon에서 `/VMC/Ext/Blend/Val` 메시지가 보이지 않음

**해결**:
1. VSeeFace "Settings" → "VMC Protocol" → "Enable VMC Protocol" 재확인
2. Windows 방화벽에서 UDP Port 39539 허용
   - 제어판 → Windows Defender 방화벽 → 고급 설정
   - 인바운드 규칙 → 새 규칙 → 포트 → UDP, 39539 → 허용
3. VSeeFace 재시작

### 문제 4: 아바타 추적이 불안정함

**증상**: 아바타가 떨리거나 부자연스럽게 움직임

**해결**:
1. 조명 개선 (정면 조명 추가)
2. 웹캠 위치 조정 (눈높이 맞춤)
3. VSeeFace "Settings" → "Tracking" → "Smoothing" 값 증가 (0.5 → 0.8)
4. 배경을 단순하게 변경 (단색 벽)

---

## 성능 최적화

### CPU/GPU 사용량 줄이기

1. VSeeFace "Settings" → "Quality" 탭
2. "Render Quality"를 **Medium** 또는 **Low**로 설정
3. "Shadow Quality"를 **Off**로 설정
4. "Anti-Aliasing"을 **Off**로 설정

### 웹캠 해상도 조정

- 고성능: 1920x1080 @ 30fps
- 권장: 1280x720 @ 30fps
- 저성능: 640x480 @ 30fps

---

## 참고 자료

- **VSeeFace 공식 사이트**: https://www.vseeface.icu/
- **VMC Protocol 문서**: https://protocol.vmc.info/
- **VRoid Hub**: https://hub.vroid.com/
- **VSeeFace Discord**: https://discord.gg/vseefaceCommunity
- **OSC Protocol**: https://opensoundcontrol.stanford.edu/

---

## 다음 단계

VSeeFace 설치 및 VMC Protocol 활성화를 완료했다면:

1. **Phase 1 Task 1.1**: VRoid Hub에서 아바타 선택 및 다운로드
2. **Phase 1 Task 1.2**: packages/vtuber 패키지 생성
3. **Phase 1 Task 1.3**: VMC Protocol 클라이언트 구현

**관련 문서**:
- [PRD-0001: VSeeFace 통합](../tasks/prds/0001-prd-vseface-integration.md)
- [Checklist: PRD-0001](./checklists/PRD-0001.md)
- [Task List: PRD-0001](../tasks/0001-tasks-vseface-integration.md)

---

**Last Updated**: 2026-01-04
**Version**: 1.0.0
**작성자**: Claude (AI Assistant)
