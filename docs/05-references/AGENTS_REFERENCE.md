# Agents Reference

> 자동 생성: `/audit` 기준. 에이전트 42개.

## 에이전트 목록

| # | 에이전트 | 모델 | 설명 |
|:-:|----------|:----:|------|
| 1 | ai-engineer | sonnet | LLM 애플리케이션, RAG 시스템, 프롬프트 엔지니어링 전문가 |
| 2 | analyst | sonnet | Pre-planning consultant for requirements analysis |
| 3 | architect | opus | Strategic Architecture & Debugging Advisor (READ-ONLY) |
| 4 | architect-low | haiku | Quick code questions & simple lookups |
| 5 | architect-medium | sonnet | Architecture & Debugging Advisor - Medium complexity |
| 6 | build-fixer | sonnet | Build and TypeScript error resolution specialist |
| 7 | build-fixer-low | haiku | Simple build error fixer |
| 8 | catalog-engineer | sonnet | WSOPTV 카탈로그 및 제목 생성 전문가 (Block F/G) |
| 9 | claude-expert | sonnet | Claude Code, MCP, 에이전트, 프롬프트 엔지니어링 통합 전문가 |
| 10 | cloud-architect | sonnet | 클라우드 인프라, 네트워크, 비용 최적화 통합 전문가 |
| 11 | code-reviewer | sonnet | Expert code review specialist (quality, security, maintainability) |
| 12 | code-reviewer-low | haiku | Quick code quality checker |
| 13 | critic | opus | Adversarial document weakness analyzer |
| 14 | data-specialist | sonnet | 데이터 분석, 엔지니어링, ML 파이프라인 통합 전문가 |
| 15 | database-specialist | sonnet | DB 설계, 최적화, Supabase 통합 전문가 |
| 16 | designer | sonnet | UI/UX Designer-Developer for stunning interfaces |
| 17 | designer-high | sonnet | Complex UI architecture and design systems |
| 18 | designer-low | haiku | Simple styling and minor UI tweaks |
| 19 | devops-engineer | sonnet | DevOps 통합 전문가 (CI/CD, K8s, Terraform, 트러블슈팅) |
| 20 | executor | sonnet | Focused task executor for implementation work |
| 21 | executor-high | opus | Complex multi-file task executor |
| 22 | executor-low | haiku | Simple single-file task executor |
| 23 | explore | haiku | Fast codebase search specialist |
| 24 | explore-high | sonnet | Complex architectural search for deep system understanding |
| 25 | explore-medium | sonnet | Thorough codebase search with reasoning |
| 26 | frontend-dev | sonnet | 프론트엔드 개발 및 UI/UX (React/Next.js 성능 최적화) |
| 27 | gap-detector | sonnet | 설계 문서와 구현 간 Gap 정량 분석 |
| 28 | github-engineer | haiku | GitHub 및 Git 워크플로우 전문가 |
| 29 | planner | opus | Strategic planning consultant (work plans) |
| 30 | qa-tester | sonnet | QA Runner - 6종 QA 실행 및 결과 보고 |
| 31 | qa-tester-high | sonnet | Comprehensive production-ready QA testing |
| 32 | researcher | sonnet | External Documentation & Reference Researcher |
| 33 | researcher-low | haiku | Quick documentation lookups |
| 34 | scientist | sonnet | Data analysis and research execution specialist |
| 35 | scientist-high | sonnet | Complex research, hypothesis testing, and ML specialist |
| 36 | scientist-low | haiku | Quick data inspection and simple statistics |
| 37 | security-reviewer | sonnet | Security vulnerability detection specialist (OWASP Top 10) |
| 38 | security-reviewer-low | haiku | Quick security scan specialist |
| 39 | tdd-guide | sonnet | TDD specialist enforcing write-tests-first methodology |
| 40 | tdd-guide-low | haiku | Quick test suggestion specialist |
| 41 | vision | sonnet | Visual/media file analyzer for images, PDFs, and diagrams |
| 42 | writer | haiku | Technical documentation writer (README, API docs, comments) |

## 모델 티어별 분류

### Opus (4개) — 복잡한 설계/구현/검증

| 에이전트 | 용도 |
|----------|------|
| architect | 전략적 아키텍처 검증 (READ-ONLY) |
| critic | Adversarial 약점 분석 |
| executor-high | 복잡한 다중 파일 구현 |
| planner | 전략적 계획 수립 |

### Sonnet (25개) — 표준 실행/분석/리뷰

| 에이전트 | 용도 |
|----------|------|
| ai-engineer | AI/ML 솔루션 |
| analyst | 요구사항 분석 |
| architect-medium | 중간 복잡도 아키텍처 |
| build-fixer | 빌드 에러 수정 |
| catalog-engineer | WSOPTV 카탈로그 |
| claude-expert | Claude Code 설정 |
| cloud-architect | 클라우드 인프라 |
| code-reviewer | 코드 리뷰 |
| data-specialist | 데이터 분석/ETL |
| database-specialist | DB 설계/최적화 |
| designer | UI/UX 개발 |
| designer-high | 복잡한 UI 아키텍처 |
| devops-engineer | DevOps/CI/CD |
| executor | 표준 구현 |
| explore-high | 심층 코드 탐색 |
| explore-medium | 중간 코드 탐색 |
| frontend-dev | 프론트엔드 개발 |
| gap-detector | 설계-구현 Gap 분석 |
| qa-tester | QA 실행 |
| qa-tester-high | 프로덕션 QA |
| researcher | 외부 문서 리서치 |
| scientist | 데이터 분석/실험 |
| scientist-high | 복잡한 연구/ML |
| security-reviewer | 보안 취약점 탐지 |
| tdd-guide | TDD 가이드 |
| vision | 이미지/PDF 분석 |

### Haiku (13개) — 빠른 조회/단순 작업

| 에이전트 | 용도 |
|----------|------|
| architect-low | 빠른 코드 질문 |
| build-fixer-low | 단순 빌드 에러 |
| code-reviewer-low | 빠른 코드 체크 |
| designer-low | 단순 스타일링 |
| executor-low | 단일 파일 실행 |
| explore | 빠른 파일 탐색 |
| github-engineer | Git 워크플로우 |
| researcher-low | 빠른 문서 조회 |
| scientist-low | 빠른 데이터 검사 |
| security-reviewer-low | 빠른 보안 스캔 |
| tdd-guide-low | 빠른 테스트 제안 |
| writer | 기술 문서 작성 |

## /auto Phase별 에이전트 배치

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 INIT | explore | 사전 탐색 |
| 1 PLAN | planner, critic, analyst | 계획 수립, 약점 분석, 요구사항 분석 |
| 2 BUILD | executor-high, code-reviewer, architect, gap-detector | 구현, 리뷰, 검증, Gap 분석 |
| 3 VERIFY | qa-tester, architect | QA 실행, 최종 검증 |
| 4 CLOSE | writer, executor-high | 보고서 작성, 정리 |
