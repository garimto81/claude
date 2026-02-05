# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

**Vimeo OTT Automation** - WSOP 아카이브를 **AWS S3에 영구 보관**하고 **Vimeo Enterprise로 스트리밍** 제공하는 3계층 시스템

### 아키텍처 개요

```
NAS (작업용) ──▶ AWS S3 (영구 보관) ──▶ Vimeo (스트리밍) ──▶ WSOPTV Apps
```

### 연관 프로젝트

| 프로젝트 | 경로 | 관계 |
|----------|------|------|
| **wsoptv_ott** | `C:\claude\wsoptv_ott` | 상위 기획 (PRD-0012) |
| **automation_hub** | `C:\claude\automation_hub` | 공유 인프라 |

---

## 빌드 및 명령어

### 인증

```bash
# 최초 인증 (브라우저 OAuth 플로우)
python C:\claude\vimeo_ott\scripts\vimeo\auth.py

# 강제 재인증
python C:\claude\vimeo_ott\scripts\vimeo\auth.py --force
```

### 비디오 관리

```bash
# 업로드
python C:\claude\vimeo_ott\scripts\vimeo\upload_poc.py "video.mp4" --title "제목" --description "설명" --privacy unlisted

# 목록 조회
python C:\claude\vimeo_ott\scripts\vimeo\upload_poc.py --list

# 비디오 정보
python C:\claude\vimeo_ott\scripts\vimeo\upload_poc.py --info /videos/123456

# 업로드 쿼터 확인
python C:\claude\vimeo_ott\scripts\vimeo\upload_poc.py --quota
```

### AWS S3 연동

```bash
# S3 상태 확인
python C:\claude\vimeo_ott\scripts\aws\s3_client.py status

# S3 업로드
python C:\claude\vimeo_ott\scripts\aws\s3_client.py upload local.mp4 raw/wsop-classic/1973/file.mp4

# S3 객체 목록
python C:\claude\vimeo_ott\scripts\aws\s3_client.py list --prefix raw/

# NAS → S3 동기화 (dry-run)
python C:\claude\vimeo_ott\scripts\aws\s3_sync.py "Z:\GGPNAs\ARCHIVE\WSOP" --dry-run

# NAS → S3 동기화 (실행)
python C:\claude\vimeo_ott\scripts\aws\s3_sync.py "Z:\GGPNAs\ARCHIVE\WSOP" --limit 10
```

### POC 테스트

```bash
# 전체 파이프라인 테스트 (dry-run)
python C:\claude\vimeo_ott\scripts\poc\test_pipeline.py --dry-run

# S3만 테스트
python C:\claude\vimeo_ott\scripts\poc\test_pipeline.py --test-s3

# Vimeo만 테스트
python C:\claude\vimeo_ott\scripts\poc\test_pipeline.py --test-vimeo

# 전체 테스트 (실제 실행)
python C:\claude\vimeo_ott\scripts\poc\test_pipeline.py --test-full
```

### 린트

```bash
ruff check C:\claude\vimeo_ott\scripts\ --fix
```

---

## 아키텍처

### 인증 흐름

```
auth.py
├── load_credentials()     # C:\claude\json\vimeo_credentials.json에서 Client ID/Secret 로드
├── authenticate()         # Browser OAuth 플로우 실행
│   ├── OAuthCallbackHandler  # localhost:8585/callback에서 인증 코드 수신
│   └── Token Exchange        # 코드를 Access Token으로 교환
└── get_client()           # PyVimeo VimeoClient 인스턴스 반환
```

- Token 저장 위치: `C:\claude\json\vimeo_token.json`
- Callback URL: `http://localhost:8585/callback`
- Scopes: public, private, create, edit, delete, upload, video_files

### 업로드 흐름

```
upload_poc.py
├── get_client()           # 인증된 Vimeo 클라이언트 획득
├── client.upload()        # TUS 프로토콜로 청크 업로드
└── Vimeo Transcoding      # 서버측 자동 트랜스코딩
```

### 모듈 현황

| 모듈 | 상태 | 설명 |
|------|:----:|------|
| `scripts/vimeo/auth.py` | ✅ | Vimeo OAuth 인증 |
| `scripts/vimeo/upload_poc.py` | ✅ | Vimeo 단일 업로드 CLI |
| `scripts/aws/s3_client.py` | ✅ | S3 업로드/다운로드 클라이언트 |
| `scripts/aws/s3_sync.py` | ✅ | NAS → S3 동기화 |
| `scripts/poc/test_pipeline.py` | ✅ | 파이프라인 POC 테스트 |

---

## 인증 파일

| 파일 | 경로 | 내용 |
|------|------|------|
| Vimeo Credentials | `C:\claude\json\vimeo_credentials.json` | `client_id`, `client_secret`, `redirect_uri` |
| Vimeo Token | `C:\claude\json\vimeo_token.json` | `access_token`, `user` 정보 |
| AWS Credentials | `~/.aws/credentials` | `aws_access_key_id`, `aws_secret_access_key` |

---

## 개발 규칙

- `C:\claude\CLAUDE.md` 상위 규칙 상속 (절대 경로, Conventional Commit, API 키 금지)
- **Browser OAuth만 사용** - API 키 환경변수 설정 금지
- **AWS credentials**: `~/.aws/credentials` 파일 사용 (환경변수 금지)
- 요구사항: Python 3.12+, PyVimeo, boto3

---

## 참고

| 문서 | 경로 |
|------|------|
| PRD-0001 (Vimeo 기초) | `docs/prds/PRD-0001-vimeo-automation.md` |
| PRD-0002 (S3 통합) | `docs/prds/PRD-0002-vimeo-ott-s3-strategy.md` |
| Plan 문서 | `docs/01-plan/vimeo-ott-s3-strategy.plan.md` |
| Design 문서 | `docs/02-design/vimeo-ott-s3-architecture.design.md` |
| Vimeo API | https://developer.vimeo.com/api (v3.4) |
| AWS S3 | https://docs.aws.amazon.com/s3/ |
