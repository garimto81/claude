# Figma CLI 연동 — PDCA 완료 보고서

## 요약

Figma 디자인 파일에서 React/Tailwind 코드로 변환하는 CLI 워크플로우를 구축했다.
공식 Figma MCP 플러그인 (v1.2.0)이 이미 설치되어 있어, 별도 MCP 서버 설정 없이 로컬 래퍼 스킬과 /auto 통합으로 완료.

## 복잡도 판단

| 팩터 | 점수 |
|------|:----:|
| 파일 수 | 1 |
| 외부 의존성 | 1 |
| 아키텍처 결정 | 1 |
| 기존 코드 영향 | 0 |
| 테스트 복잡도 | 0 |
| **합계** | **3 (STANDARD)** |

## 산출물

### 신규 파일 (6개)

| 파일 | 줄 수 | 역할 |
|------|:-----:|------|
| `.claude/skills/figma/SKILL.md` | 97 | 로컬 래퍼 스킬 (3개 플러그인 스킬 라우팅) |
| `lib/figma/__init__.py` | 2 | 패키지 초기화 |
| `lib/figma/url_parser.py` | 83 | Figma URL 파싱 (file_key, node_id 추출) |
| `tests/test_figma_url_parser.py` | 52 | URL 파서 테스트 (9개) |
| `docs/00-prd/figma-cli-integration.prd.md` | 57 | PRD |
| `docs/01-plan/figma-cli-integration.plan.md` | 79 | 설계 계획 |

### 수정 파일 (4개)

| 파일 | 변경 내용 |
|------|----------|
| `.claude/skills/auto/SKILL.md` | `--figma` 옵션 2곳 추가 (Phase 0 + Step 2.0) |
| `.claude/agents/designer.md` | Figma Design Context 섹션 추가 (+11줄) |
| `.claude/rules/08-skill-routing.md` | `--figma` 라우팅 + figma 플러그인 연동 등록 |
| `CLAUDE.md` | 스킬 수 40→41 업데이트 |

## 아키텍처

```
  /auto "구현" --figma <URL>
         |
         v
  +------+--------+
  | Phase 2.0     |
  | 옵션 처리      |
  +------+--------+
         |
         v
  +------+--------+     +-----------------------+
  | url_parser.py |---->| Figma MCP Plugin      |
  | file_key      |     | (v1.2.0, HTTP remote) |
  | node_id       |     +-----------+-----------+
  +--------------+                  |
                            Figma REST API
                                    |
                    +---------------+---------------+
                    |               |               |
              implement-     code-connect-    design-system-
              design         components        rules
                    |
                    v
              designer agent
              → React + Tailwind
```

## 검증 결과

| 검증 | 결과 |
|------|------|
| 단위 테스트 | 9/9 통과 |
| Architect 검증 | APPROVE (일치율 100%) |
| 문서 동기화 | 완료 (PRD, 08-skill-routing) |

## 커밋

```
3caf7b2 feat(figma): Figma CLI 연동 스킬 추가 — 공식 MCP 플러그인 래퍼
```

## 사용법

```bash
# 디자인 → 코드 변환
/auto "컴포넌트 구현" --figma https://figma.com/design/KEY/Name?node-id=1-2

# 컴포넌트 매핑
/auto "컴포넌트 매핑" --figma connect https://figma.com/design/KEY/Name

# 디자인 시스템 규칙 생성
/auto "디자인 시스템" --figma rules
```
