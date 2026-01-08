# Vibe IDE Switcher 사용 설명서 (8-Instance Edition)

이 도구는 동시에 8개의 VS Code를 사용하는 당신의 생산성을 위해 설계되었습니다.

## 1. 초기 설정 (중요)
`config.json` 파일을 열어 각 인스턴스의 실제 경로를 설정해야 합니다.
- **Instance-1~8**: 기본적으로 `$HOME\AppData\Roaming\Code-InstanceN\User` 와 같이 설정되어 있습니다.
- 만약 `--user-data-dir`을 사용하신다면, 해당 경로 안의 `User` 폴더 위치를 적어주세요.

## 2. 사용 명령어

### 현재 환경 저장하기
8개 VS Code의 현재 테마와 설정을 `work`라는 이름으로 저장합니다.
```powershell
.\vswitch.ps1 save work
```

### 환경 전환하기
저장해둔 `broadcast` 설정으로 8개 VS Code를 일괄 전환합니다. (전환 즉시 VS Code에 반영됩니다.)
```powershell
.\vswitch.ps1 switch broadcast
```

### 프로필 목록 확인
```powershell
.\vswitch.ps1 list
```

## 3. 원리
이 스크립트는 각 인스턴스의 `settings.json`과 `keybindings.json`을 `c:\claude\vibe-profiles` 폴더 아래에 프로필별로 백업하고, 전환 시 해당 파일들을 다시 원본 위치로 덮어씌웁니다. VS Code는 설정 파일이 변경되면 실시간으로 감지하여 테마와 폰트를 즉시 변경하므로 재시작이 필요 없습니다.
