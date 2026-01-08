# Product Requirements Document (PRD): Vibe IDE Switcher (Multi-Instance Edition)

## 1. 프로젝트 개요
여러 개의 IDE(VS Code, Cursor, Windsurf 등)를 동시에 사용하는 환경, 특히 **8개 이상의 VS Code 인스턴스를 병렬로 운용하는 하드한 개발 환경**에서 '업무 모드', '방송 모드', '프로젝트별 모드'를 원클릭으로 통합 관리하고 전환할 수 있는 환경 최적화 도구입니다.

## 2. 해결하고자 하는 문제 (Problem Statement)
- **다중 인스턴스 관리의 한계:** 8개의 VS Code 창을 하나하나 설정(테마, 폰트, 확장 프로그램)하는 것은 불가능에 가깝습니다.
- **설정 동기화 및 차별화의 충돌:** 모든 인스턴스에 공통 설정을 적용해야 할 때와, 특정 역할(Front-end, Back-end, Infra 등)에 따라 개별 설정을 유지해야 할 때의 관리가 매우 복잡합니다.
- **리소스 부하 및 가독성:** 다수의 창이 열려 있을 때, 모드 전환(예: 방송용 고대비 테마) 시 한꺼번에 모든 창의 시각적 요소를 변경하기 어렵습니다.

## 3. 핵심 사용자 (Target Audience)
- **8개 이상의 VS Code 인스턴스**를 띄워놓고 마이크로서비스나 대형 프로젝트를 수행하는 유저.
- **바이브 코딩(Vibe Coding)** 시 여러 창의 테마를 동시에 스위칭하여 분위기를 전환하고 싶은 개발자.
- 다중 모니터 환경에서 각 화면의 VS Code를 일괄 제어하고자 하는 크리에이터.

## 4. 주요 기능 (Key Features)

### 4.1. 다중 인스턴스 프로필 그룹 (Instance Grouping)
- **일괄 저장(Bulk Save):** 현재 실행 중인 8개(또는 그 이상)의 모든 VS Code 인스턴스 설정을 하나의 '그룹 프로필'로 스냅샷 저장.
- **개별/공통 설정 상속:** 모든 인스턴스에 적용될 `Global Settings`와 각 창(Instance 1~8)에만 적용될 `Specific Settings`를 계층적으로 관리.

### 4.2. 원클릭 벌크 전환 (Bulk Environment Switching)
- 단 한 번의 명령으로 8개 VS Code의 설정 파일(`settings.json`)을 즉시 교체.
- **실시간 리로드:** 인스턴스가 켜져 있는 상태에서 재시작 없이 설정이 반영되도록 바이너리/링크 기반 교체 최적화.

### 4.3. 인스턴스 식별 및 경로 자동 탐색
- `--user-data-dir` 별로 분리된 8개의 VS Code 경로를 자동으로 감지하거나 `config.json`에서 매핑.
- 각 인스턴스별 역할을 지정(예: Instance 1 = Main Logic, Instance 2 = DB UI 등)하여 관리.

## 5. 기술 사양 (Technical Specifications)
- **Language:** PowerShell Core (Windows 10/11 최적화 및 빠른 파일 시스템 접근)
- **Data Format:** JSON (인스턴스별 경로 및 설정 매핑 파일)
- **Storage:** Local Storage (`c:\claude\vibe-profiles`)
- **Execution:** 병렬 처리를 통해 8개 이상의 설정 파일을 거의 동시에 교체 (Race Condition 방지 처리).

## 6. 사용자 시나리오 (User Scenario)
1. **상황:** 유저는 현재 8개의 VS Code를 띄워 각각 다른 마이크로서비스를 코딩 중.
2. **명령:** 터미널에 `./vswitch focus-mode` 입력.
3. **시스템 동작:** 
   - 8개 인스턴스 전체의 테마가 `Zen Mode` 스타일의 다크 테마로 변경됨.
   - 각 인스턴스별로 미리 지정된 폰트 크기(예: 메인 창은 16pt, 보조 창은 12pt)로 자동 조정.
4. **결과:** 8개의 화면이 1초 이내에 일괄적으로 최적의 몰입 환경으로 전환됨.

## 7. 향후 확장 계획 (Future Roadmap)
- **Window Management:** 프로필 전환 시 8개 창의 윈도우 위치(좌표)와 크기까지 복원하는 기능.
- **Workspace Sync:** 각 인스턴스가 열고 있어야 할 프로젝트 폴더(Workspace)까지 세트로 관리.
- **Dashboard UI:** 8개 인스턴스의 상태를 한눈에 보고 제어하는 GUI 대시보드.
