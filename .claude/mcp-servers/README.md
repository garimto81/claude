# MCP Servers

Claude Code용 커스텀 MCP 서버 모음입니다.

## 목적

기본 내장 도구를 MCP 서버로 분리하여 **토큰 사용량을 최적화**합니다.

- 필요한 도구만 동적으로 로드
- 기본 세션에서 ~1,000 토큰 절감

## 설치된 서버

### notebook-tools

Jupyter 노트북 관련 도구 (`.ipynb` 파일 작업 시 활성화)

```bash
# 설치
claude mcp add notebook-tools -- python .claude/mcp-servers/notebook-tools/server.py

# 제공 도구
- notebook_edit: 셀 편집
- notebook_run: 셀 실행
- notebook_export: 내보내기 (html, pdf, py, md)
```

### system-tools

시스템 관리 도구 (백그라운드 작업, 프로세스 관리)

```bash
# 설치
claude mcp add system-tools -- python .claude/mcp-servers/system-tools/server.py

# 제공 도구
- kill_process: 프로세스 종료
- list_background_tasks: 백그라운드 작업 목록
- system_info: 시스템 정보
```

## 조건부 활성화 설정

`.claude.json`에 추가:

```json
{
  "mcpServers": {
    "notebook-tools": {
      "command": "python",
      "args": [".claude/mcp-servers/notebook-tools/server.py"],
      "autoStart": false
    },
    "system-tools": {
      "command": "python",
      "args": [".claude/mcp-servers/system-tools/server.py"],
      "autoStart": false
    }
  }
}
```

## 토큰 절감 효과

| 시나리오 | 기존 | MCP 분리 후 | 절감 |
|----------|------|-------------|------|
| 일반 세션 | 10k | 9k | 10% |
| 노트북 작업 | 10k | 9.4k | 6% |
| 시스템 작업 | 10k | 9.7k | 3% |

## 관련 이슈

- [#28](https://github.com/garimto81/claude/issues/28) - System Tools 토큰 최적화
