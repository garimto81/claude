---
name: gmail
description: >
  Gmail 메일 관리 스킬. OAuth 2.0 인증, 메일 읽기/전송, 라벨 관리.
  "gmail", "메일 확인", "이메일 보내줘" 요청 시 사용.
version: 1.0.0
triggers:
  keywords:
    - "gmail"
    - "지메일"
    - "email"
    - "이메일"
    - "메일"
    - "mail"
    - "inbox"
    - "받은편지함"
    - "unread"
    - "안읽은 메일"
    - "메일 확인"
    - "메일 보내"
    - "이메일 전송"
  patterns:
    - "gmail (login|inbox|unread|send|read|search|labels)"
    - "(메일|이메일).*(확인|읽|보내|전송|검색)"
    - "(unread|inbox|sent) (mail|email)"
  file_patterns:
    - "**/gmail*.py"
    - "**/gmail_*.json"
  context:
    - "Gmail 연동"
    - "이메일 자동화"
    - "메일 관리"
capabilities:
  - gmail_oauth
  - send_email
  - read_inbox
  - search_emails
  - manage_labels
model_preference: sonnet
auto_trigger: true
---

# Gmail Skill

Gmail API 연동 스킬. OAuth 2.0 인증, 이메일 읽기/전송, 라벨 관리 기능 제공.

## Commands

| Command | Description |
|---------|-------------|
| `python -m lib.gmail login` | OAuth 인증 (최초 1회) |
| `python -m lib.gmail status` | 인증 상태 확인 |
| `python -m lib.gmail inbox` | 받은편지함 보기 |
| `python -m lib.gmail unread` | 안 읽은 메일 보기 |
| `python -m lib.gmail read <id>` | 메일 상세 읽기 |
| `python -m lib.gmail send <to> <subject> <body>` | 메일 전송 |
| `python -m lib.gmail search <query>` | 메일 검색 |
| `python -m lib.gmail labels` | 라벨 목록 |

## Claude 강제 실행 규칙 (MANDATORY)

Gmail 키워드 감지 시 반드시 자동 수행:

**Step 1**: 인증 확인 → `cd C:\claude && python -m lib.gmail status --json`
- `"valid": true` → Step 2 진행
- `"authenticated": false` → 사용자에게 `python -m lib.gmail login` 안내

**Step 2**: 요청별 명령 실행 (`--json` 플래그 필수)

| 사용자 요청 | 실행 명령 |
|-------------|----------|
| "메일 확인해줘" | `python -m lib.gmail inbox --json` |
| "안읽은 메일" | `python -m lib.gmail unread --json` |
| "메일 보내줘" | `python -m lib.gmail send "주소" "제목" "본문"` |
| "메일 검색" | `python -m lib.gmail search "검색어" --json` |

**Step 3**: JSON 결과 파싱 → 사용자에게 읽기 쉬운 형태로 응답

### 필수/금지 행동

| 필수 | 금지 |
|------|------|
| `cd C:\claude &&` 접두사 | gmail_token.json 직접 읽기 |
| `--json` 플래그 사용 | WebFetch로 Gmail API 호출 |
| Bash tool 직접 사용 | "인프라가 없습니다" 응답 |
| 에러 시 상세 안내 | 사용자에게 수동 실행 요청 |

## 상세 참조

> Prerequisites (Google Cloud Console 설정, OAuth), Usage Examples, Python API,
> Search Query 문법, Error Handling, File Locations, Rate Limits 등:
> **Read `references/gmail-workflows.md`**
