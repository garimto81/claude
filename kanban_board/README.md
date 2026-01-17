# Vibe Kanban Integration

Claude Code 프로젝트들을 칸반 보드로 관리하는 통합 환경.

## 빠른 시작

```bash
# Vibe Kanban 실행
npx vibe-kanban

# 웹 UI 접속
# http://localhost:5173
```

## 기능

- **멀티 프로젝트 보드**: 여러 프로젝트를 하나의 칸반 뷰로 관리
- **병렬 에이전트 실행**: 여러 작업을 동시에 Claude Code로 처리
- **GitHub 연동**: PR 자동 생성, 머지, 리베이스
- **실시간 모니터링**: 작업 상태 및 로그 확인

## 기술 스택

| 구분 | 기술 |
|------|------|
| 런타임 | Node.js 18+ |
| 칸반 도구 | Vibe Kanban |
| 에이전트 | Claude Code |
| 연동 | GitHub API |

## 문서

- [PRD-0001: Vibe Kanban 통합](tasks/prds/0001-prd-vibe-kanban-integration.md)

## 라이선스

Private
