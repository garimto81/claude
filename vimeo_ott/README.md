# Vimeo OTT Automation

WSOPTV를 위한 Vimeo Enterprise 연동 자동화 도구

## 개요

WSOP 아카이브 콘텐츠를 Vimeo Enterprise에 자동 업로드하고 관리하는 시스템

## 빠른 시작

### 1. 인증 설정

```bash
# 최초 인증 (브라우저 OAuth)
python scripts/vimeo/auth.py
```

### 2. 비디오 업로드

```bash
# 단일 업로드
python scripts/vimeo/upload_poc.py "video.mp4" --title "제목"

# 비디오 목록
python scripts/vimeo/upload_poc.py --list

# 업로드 쿼터 확인
python scripts/vimeo/upload_poc.py --quota
```

## 프로젝트 구조

```
vimeo_ott/
├── CLAUDE.md           # Claude Code 가이드
├── README.md           # 이 파일
├── docs/
│   └── prds/           # PRD 문서
└── scripts/
    └── vimeo/          # Vimeo 연동 스크립트
```

## 문서

- [PRD-0001: Vimeo Automation](docs/prds/PRD-0001-vimeo-automation.md)

## 연관 프로젝트

| 프로젝트 | 설명 |
|----------|------|
| [wsoptv_ott](../wsoptv_ott) | WSOPTV OTT 플랫폼 기획 |
| [automation_hub](../automation_hub) | 방송 자동화 인프라 |

## 요구사항

- Python 3.12+
- PyVimeo (`pip install PyVimeo`)
- Vimeo Enterprise 계정

## 라이선스

Private - GGP Internal Use Only
