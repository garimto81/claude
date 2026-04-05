# Audit Backlog

> 자동 생성: /audit 커맨드 | 최초 생성: 2026-04-02

---

## PENDING

### [B-001] verify 커맨드/스킬 구현
- **날짜**: 2026-04-02
- **설명**: 08-skill-routing.md에 /verify 참조되나 구현 없음
- **수락 기준**: verify 커맨드 실행 가능 또는 규칙에서 제거

### [B-002] overlay-fallback, calendar, daily, mockup-hybrid 커맨드 파일 생성
- **날짜**: 2026-04-02
- **설명**: 라우팅 규칙 참조되나 commands/ 파일 없음
- **수락 기준**: 파일 생성 또는 규칙 업데이트

### [B-003] 에이전트 수 불일치 명확화 (선언 43 vs 실제 11)
- **날짜**: 2026-04-02
- **설명**: CLAUDE.md 에이전트 43 선언. 실제 agents/*.md는 11개.
- **수락 기준**: 카운터 명확화 또는 실제 수 반영

### [B-004] Deprecated 스킬 6개 디렉토리 정리
- **날짜**: 2026-04-02
- **설명**: code-quality-checker 등 Deprecated 스킬 디렉토리 잔존
- **수락 기준**: 아카이브 또는 삭제 완료

### [B-005] figma/frontend-design 플러그인 SKILL.md 생성 또는 참조 수정
- **날짜**: 2026-04-02
- **설명**: 라우팅 규칙에 figma 참조되나 skills/figma/SKILL.md 없음
- **수락 기준**: 스킬 파일 생성 또는 참조 제거

### [B-006] MCP Tool Search 지연 로딩 설정 추가
- **날짜**: 2026-04-05
- **설명**: Claude Code v2.1.89+ MCP Tool Search 기능으로 컨텍스트 95% 절감 가능. settings.json 또는 mcp 설정 추가 필요.
- **수락 기준**: 지연 로딩 활성화 설정 적용 및 컨텍스트 사용량 감소 확인

### [B-007] PermissionDenied hook 구현
- **날짜**: 2026-04-05
- **설명**: Claude Code v2.1.89+에서 PermissionDenied hook 지원. 권한 거부 이벤트 감사/로깅에 활용 가능.
- **수락 기준**: permission_denied_logger.py 훅 구현 및 settings.json 등록

### [B-008] Agent Teams 공식 기능 통합 검토
- **날짜**: 2026-04-05
- **설명**: Claude Code 공식 Agent Teams 기능(실험적) — 팀원 간 직접 메시지, 공유 태스크 큐. 현재 OMC 의존 구조 대체 또는 보완 검토 필요.
- **수락 기준**: 기능 평가 보고서 작성 또는 통합 구현

---

## IN_PROGRESS

(없음)

---

## DONE

| 날짜 | ID | 제목 | 커밋 |
|------|----|------|-----|
| 2026-04-02 | T1-001 | CLAUDE.md 카운터 수정 | chore(audit): daily audit 2026-04-02 |
| 2026-04-02 | T1-002 | backlog.md 파일 생성 | chore(audit): daily audit 2026-04-02 |
