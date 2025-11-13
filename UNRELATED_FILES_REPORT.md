# 전역 워크플로우와 무관한 파일/폴더 분석 보고서

**분석일**: 2025-01-13
**레포 목적**: Claude Code 작업을 위한 전역 워크플로우 및 가이드 관리
**원칙**: 프로젝트별 폴더는 포함하지 않음 (README.md 명시)

---

## 📊 요약

| 카테고리 | 개수 | 비고 |
|---------|------|------|
| 프로젝트 폴더 | 17개 | 별도 레포로 분리 권장 |
| 백업 파일 | 5개 | 삭제 가능 |
| 임시 파일 | 1개 | 삭제 가능 |
| 중복 Symlink | 2개 | 삭제 가능 |
| 가상환경 | 1개 | .gitignore 등록됨 |
| **총계** | **26개** | |

---

## 🚫 인과적 관련 없는 항목

### 1. 프로젝트 폴더 (17개)

이 폴더들은 별도 프로젝트로, 전역 워크플로우와 무관합니다.

#### A. 포커/게임 관련 (6개)
1. **actiontracker/** - 액션 추적 시스템
2. **broadcast-qc/** - 방송 품질 관리
3. **handlogger/** - 핸드 로거
4. **keyplayer_manager/** - 키플레이어 관리
5. **table_tracker/** - 테이블 추적
6. **wsop_plus_story_hub/** - WSOP+ 스토리 허브

#### B. 데이터/분석 관련 (2개)
7. **table_analysis/** - 포커 테이블 분석 (Causal AI Vision System)
   - PRD 확인: 포커 게임 영상 분석 AI 시스템
   - 전역 워크플로우와 전혀 무관
8. **pd-note/** - PD 노트

#### C. SSO/인증 관련 (2개)
9. **sso-system/** - SSO 시스템
10. **VTC_Logger/** - VTC 로거

#### D. 콘텐츠/제작 관련 (3개)
11. **contents-factory/** - 콘텐츠 팩토리
12. **commercial/** - 광고/커머셜
13. **softsender/** - 소프트 센더

#### E. AI/프로덕션 (2개)
14. **ai-production/** - AI 프로덕션
15. **classic-isekai/** - 클래식 이세카이

#### F. 설정/기타 (2개)
16. **config/** - 설정 폴더
17. **claude-code-config/** - Claude Code 설정 (중복?)

---

### 2. 백업 파일 (5개)

삭제 또는 별도 백업 위치로 이동 권장.

1. **CLAUDE.md.backup** - CLAUDE.md 백업
2. **CLAUDE.md.v4.2.0.backup** - CLAUDE.md v4.2.0 백업
3. **docs.backup/** - docs 폴더 백업
4. **scripts.backup/** - scripts 폴더 백업
5. **.gitmodules** (.gitignore 등록됨)

---

### 3. 임시 파일 (1개)

1. **nul** - Windows 임시 파일 (0 바이트)

---

### 4. 중복 Symlink (2개)

.gitignore에 등록되어 있으나 실제로 존재.

1. **docs-global/** - docs/ 폴더와 중복
2. **scripts-global/** - scripts/ 폴더와 중복

---

### 5. 가상환경 (1개)

1. **.venv/** - Python 가상환경 (.gitignore 등록됨)

---

## ✅ 전역 워크플로우 관련 항목 (유지)

### 핵심 문서
- ✅ CLAUDE.md - 핵심 워크플로우
- ✅ README.md - 전체 개요
- ✅ 깃허브_워크플로우_개요.md
- ✅ 깃허브_빠른시작.md
- ✅ README_GITHUB_WORKFLOW.md
- ✅ CLAUDE_CLI_QUICKSTART.md

### 설정 파일
- ✅ .gitignore
- ✅ pytest.ini
- ✅ requirements.txt
- ✅ requirements-test.txt
- ✅ claude-config.json
- ✅ start-claude-auto.bat
- ✅ start-claude-bypass.bat

### 폴더
- ✅ .claude/ - Claude Code 확장
- ✅ .github/ - GitHub Actions
- ✅ .speckit/ - Spec Kit 템플릿
- ✅ .vscode/ - VSCode 설정
- ✅ docs/ - 상세 가이드
- ✅ scripts/ - 자동화 스크립트
- ✅ tasks/ - PRD 및 Task List
- ✅ tests/ - 테스트

---

## 🎯 권장 조치사항

### 즉시 실행 가능

```bash
# 1. 임시 파일 삭제
rm nul

# 2. 백업 파일 삭제 (선택)
rm CLAUDE.md.backup CLAUDE.md.v4.2.0.backup
rm -rf docs.backup scripts.backup

# 3. Symlink 삭제
rm -rf docs-global scripts-global
```

### .gitignore 업데이트 권장

다음 항목들을 .gitignore에 추가하여 향후 커밋 방지:

```gitignore
# 누락된 프로젝트 폴더
classic-isekai/
claude-code-config/
table_analysis/
wsop_plus_story_hub/

# Symlinks
docs-global/
scripts-global/
```

### 프로젝트 폴더 분리 (장기)

17개 프로젝트 폴더를 각각 별도 레포로 분리:
- 각 프로젝트마다 독립 Git 레포 생성
- claude01 레포는 전역 워크플로우만 유지
- 필요 시 Git submodule로 연결

---

## 📈 예상 효과

### Before
- 총 파일/폴더: ~50개
- 전역 워크플로우 관련: ~24개
- **무관한 항목: ~26개 (52%)**

### After (정리 완료 시)
- 총 파일/폴더: ~24개
- 전역 워크플로우 관련: ~24개
- **무관한 항목: 0개 (0%)**

### 이점
1. ✅ **명확한 레포 목적**: 전역 워크플로우만 집중
2. ✅ **관리 용이**: 관련 파일만 추적
3. ✅ **Git 성능 향상**: 불필요한 파일 제외
4. ✅ **협업 효율**: 다른 개발자가 이해하기 쉬움
5. ✅ **백업 효율**: 필요한 것만 백업

---

## 🔍 상세 분석

### table_analysis/ (예시)

**파일**: `table_analysis/docs/prd.md`
**내용**: "Causal AI Vision System (CAVS) - 포커 게임 인과관계 분석 AI"
**결론**: 전역 워크플로우와 **전혀 무관**. 별도 레포로 분리 필요.

### claude-code-config/ (예시)

**의심**: claude01 레포 자체가 Claude Code 설정인데 하위에 또 있음
**확인 필요**: 중복인지, 별도 프로젝트인지 확인
**권장**: 중복이면 삭제, 별도 프로젝트면 분리

---

## ✍️ 결론

**핵심 발견**:
- 현재 레포의 **52%가 전역 워크플로우와 무관**
- 대부분이 별도 프로젝트 폴더 (17개)
- README.md에 명시된 원칙("프로젝트별 폴더 포함 안함")을 위반

**권장 액션**:
1. **즉시**: 임시/백업 파일 삭제 (6개)
2. **단기**: .gitignore 업데이트
3. **장기**: 프로젝트 폴더 별도 레포로 분리 (17개)

**예상 효과**:
- 레포 목적 명확화
- 관리 효율성 대폭 향상
- Git 성능 개선

---

**작성자**: Claude Code
**분석 기준**: README.md 원칙 + CLAUDE.md 워크플로우
**검증**: 전체 파일 시스템 스캔 + .gitignore 확인
