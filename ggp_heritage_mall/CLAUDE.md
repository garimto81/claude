# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GGP Heritage Mall - Next.js 기반 VIP 쇼핑몰 웹앱. Supabase 백엔드, Zustand 상태관리.

**Tech Stack**: Next.js 16 (App Router) | React 19 | TypeScript | Supabase | Zustand 5 | Tailwind CSS

---

## Build & Development

```powershell
cd D:\AI\claude01\ggp_heritage_mall\web

# 개발 서버
npm run dev

# 빌드
npm run build

# 린트
npm run lint
```

---

## Testing

```powershell
cd D:\AI\claude01\ggp_heritage_mall\web

# 단위 테스트 (권장)
npm run test                    # 전체 테스트
npm run test:watch              # watch 모드
npm run test -- src/stores/__tests__/cartStore.test.ts  # 개별 파일

# 커버리지
npm run test:coverage
```

**Vitest + Testing Library** 사용. AAA 패턴 적용.

---

## Architecture

### Routes (App Router)

| Route | Description |
|-------|-------------|
| `/` | 홈 |
| `/products` | 상품 목록 |
| `/products/[id]` | 상품 상세 |
| `/checkout` | 결제 |
| `/checkout/complete` | 결제 완료 |
| `/orders` | 주문 내역 |
| `/invalid-token` | 토큰 오류 |

### State Management

- `cartStore` (Zustand): 장바구니 상태 관리
  - VIP 등급별 최대 아이템 수 제한
  - `persist` middleware로 localStorage 동기화

### Backend

- **Supabase**: 인증, 데이터베이스, 스토리지
- 이미지: `*.supabase.co/storage/v1/object/public/**`

---

## Agent Workflow

이 프로젝트는 `.agent/` 디렉토리에서 Supervisor 기반 워크플로우 사용.

```
.agent/
├── state.yaml      # 워크플로우 상태
├── tasks/          # 작업 정의
└── results/        # 작업 결과
```

---

## Inherited Rules

부모 `D:\AI\claude01\CLAUDE.md` 규칙 적용:

- 한글 출력, 기술 용어는 영어
- 절대 경로 사용
- TDD: Red → Green → Refactor
- main 브랜치 직접 수정 금지
