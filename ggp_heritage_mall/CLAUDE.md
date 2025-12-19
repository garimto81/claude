# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GGP Heritage Mall - VIP 전용 초대 쇼핑몰. 초대 토큰 URL로만 접근, 무료 증정, 등급별 수량 제한 (Silver: 3개, Gold: 5개).

## Tech Stack

Next.js 16 + React 19 + TypeScript | Tailwind CSS 4 + shadcn/ui | Zustand | Supabase

## Commands

```bash
cd D:\AI\claude01\ggp_heritage_mall\web
npm run dev           # http://localhost:5000
npm run build         # 프로덕션 빌드
npm run lint          # ESLint
npm test              # Vitest 1회 실행
npm run test:watch    # Vitest watch 모드
npm run test:coverage # 커버리지 리포트
```

## Architecture

### VIP 인증 흐름 (middleware.ts)

```
/products?token=abc → 토큰 검증 → vip_session 쿠키 (7일) → 보호 경로 접근
```

**보호 경로:** `/shop`, `/orders`, `/profile`
**공개 경로:** `/`, `/invalid-token`

### Supabase 클라이언트 선택

| 컨텍스트 | import | 비고 |
|---------|--------|------|
| Client Component | `@/lib/supabase/client` | `createClient()` |
| Server Component | `@/lib/supabase/server` | `await createClient()` |
| RLS 우회 | `@/lib/supabase/admin` | Server only |

### Server Actions

주문 생성: `src/app/checkout/actions.ts` → `createOrderAction()`

### 주요 훅/스토어

| 훅/스토어 | 용도 | 반환값 |
|----------|------|--------|
| `useVipSession()` | VIP 정보 | `{ vip, loading }` |
| `useVipOrderLimit()` | 주문 제한 | `{ limit, remaining, canOrder }` |
| `useCartStore` | 장바구니 (Zustand) | persist: `ggp-cart-storage` |

### DB 테이블

```
vips (tier, invite_token)
  └─ orders (status, shipping_address)
       └─ order_items (product_id, size, quantity)

products (tier_required, images[])
  ├─ categories (name, slug)
  └─ inventory (size, quantity)
```

**타입:** `src/types/database.ts` - Row/Insert/Update 타입 정의

## Design System

다크 모드: `--color-gold: #D4AF37`, `--color-background: #0A0A0A`, `--color-surface: #1A1A1A`

## Env

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=  # 또는 NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SECRET_KEY=
```
