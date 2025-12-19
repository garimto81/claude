# VIP 초대 토큰 인증 시스템

GGP Heritage Mall의 VIP 초대 토큰 인증 및 세션 관리 시스템입니다.

## 개요

이 시스템은 다음 기능을 제공합니다:

1. **초대 토큰 검증**: URL의 `?token=xxx` 파라미터로 VIP 인증
2. **세션 관리**: 인증된 VIP 정보를 쿠키에 저장 (7일 유효)
3. **경로 보호**: 인증되지 않은 사용자는 보호된 페이지 접근 불가
4. **VIP 등급 확인**: Silver/Gold 등급별 권한 관리
5. **주문 수량 제한**: VIP 등급별 주문 가능 수량 관리

## 아키텍처

### 미들웨어 (middleware.ts)

Next.js 미들웨어가 모든 요청을 가로채서 다음을 수행합니다:

1. **토큰 검증 플로우**
   ```
   URL에 ?token=xxx 있음
   → VIP 테이블에서 조회
   → 유효하면 쿠키 설정 후 리다이렉트
   → 무효하면 /invalid-token으로 리다이렉트
   ```

2. **보호된 경로 플로우**
   ```
   /shop, /orders, /profile 접근
   → 쿠키에서 vip_session 확인
   → 없으면 / 로 리다이렉트
   → 있으면 VIP 유효성 재확인
   ```

### 서버 컴포넌트 (vip-session.ts)

서버 컴포넌트에서 사용하는 세션 관리 함수:

```typescript
import { getVipSession, canVipOrder } from "@/lib/auth";

export default async function ShopPage() {
  const vip = await getVipSession();

  if (!vip) {
    redirect("/");
  }

  const canOrder = await canVipOrder(2);
  // ...
}
```

**주요 함수:**

| 함수 | 설명 | 반환 타입 |
|------|------|----------|
| `getVipSession()` | 현재 VIP 세션 가져오기 | `VipSession \| null` |
| `hasVipTier(tier)` | VIP가 특정 등급 이상인지 확인 | `boolean` |
| `getVipOrderLimit()` | VIP의 주문 가능 최대 수량 | `number` |
| `getVipCurrentOrderCount()` | VIP의 현재 주문 수량 | `number` |
| `canVipOrder(quantity)` | 추가 주문 가능 여부 | `boolean` |

### 클라이언트 컴포넌트 (use-vip-session.ts)

클라이언트 컴포넌트에서 사용하는 React 훅:

```typescript
"use client";
import { useVipSession, useVipOrderLimit } from "@/hooks/use-vip-session";

export default function VipProfile() {
  const { vip, loading } = useVipSession();
  const { limit, currentCount, remaining, canOrder } = useVipOrderLimit();

  if (loading) return <div>Loading...</div>;
  if (!vip) return <div>Not authenticated</div>;

  return (
    <div>
      <h1>Welcome, {vip.name || vip.email}</h1>
      <p>Tier: {vip.tier}</p>
      <p>Orders: {currentCount} / {limit}</p>
      <p>Remaining: {remaining}</p>
    </div>
  );
}
```

**주요 훅:**

| 훅 | 설명 | 반환값 |
|------|------|--------|
| `useVipSession()` | VIP 세션 정보 | `{ vip, loading }` |
| `useVipOrderLimit()` | 주문 제한 정보 | `{ limit, currentCount, remaining, canOrder, loading }` |

## 사용 예시

### 1. 초대 토큰으로 접근

```
사용자가 이메일에서 링크 클릭
https://heritage-mall.ggpoker.com/shop?token=abc123xyz

→ middleware.ts에서 토큰 검증
→ 유효하면 vip_session 쿠키 설정
→ https://heritage-mall.ggpoker.com/shop 로 리다이렉트
→ VIP로 쇼핑 시작
```

### 2. 보호된 페이지 접근

```typescript
// app/orders/page.tsx
import { getVipSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export default async function OrdersPage() {
  const vip = await getVipSession();

  if (!vip) {
    redirect("/"); // 미들웨어에서 이미 처리되지만 안전장치
  }

  return <div>Orders for {vip.email}</div>;
}
```

### 3. VIP 등급별 컨텐츠 표시

```typescript
// app/products/[id]/page.tsx
import { getVipSession, hasVipTier } from "@/lib/auth";

export default async function ProductPage({ params }: { params: { id: string } }) {
  const vip = await getVipSession();
  const isGold = await hasVipTier("gold");

  return (
    <div>
      {isGold && <div className="gold-badge">Gold Member Exclusive</div>}
      {/* ... */}
    </div>
  );
}
```

### 4. 주문 수량 제한 확인

```typescript
// app/checkout/page.tsx
import { canVipOrder, getVipOrderLimit } from "@/lib/auth";

export default async function CheckoutPage() {
  const limit = await getVipOrderLimit(); // 3 or 5
  const canAdd = await canVipOrder(2); // 2개 추가 가능?

  return (
    <div>
      <p>Your limit: {limit} items</p>
      {!canAdd && <p>You cannot order more items</p>}
    </div>
  );
}
```

## 보안

### 쿠키 설정

```typescript
response.cookies.set("vip_session", vip.id, {
  httpOnly: true,              // JavaScript 접근 방지
  secure: NODE_ENV === "production", // HTTPS only
  sameSite: "lax",            // CSRF 방지
  maxAge: 60 * 60 * 24 * 7,   // 7일
  path: "/",
});
```

### RLS (Row Level Security)

Supabase의 RLS 정책이 데이터베이스 레벨에서 보안을 강화합니다:

```sql
-- VIPs 테이블: 자신의 정보만 조회 가능
CREATE POLICY "VIPs can view own data"
ON vips FOR SELECT
USING (id = auth.uid());

-- Orders 테이블: 자신의 주문만 조회 가능
CREATE POLICY "VIPs can view own orders"
ON orders FOR SELECT
USING (vip_id = auth.uid());
```

## 테스트

### 1. 수동 테스트

```bash
# 1. 테스트 VIP 생성 (Supabase SQL Editor에서)
INSERT INTO vips (email, tier, invite_token, is_active)
VALUES ('test@example.com', 'gold', 'test-token-123', true);

# 2. 브라우저에서 접근
http://localhost:3000/shop?token=test-token-123

# 3. 쿠키 확인 (DevTools > Application > Cookies)
vip_session = <vip-id>

# 4. 보호된 페이지 접근
http://localhost:3000/orders (쿠키 있으면 접근 가능)

# 5. 쿠키 삭제 후 다시 접근
http://localhost:3000/orders (/ 로 리다이렉트)
```

### 2. 자동 테스트 (Playwright)

```typescript
// tests/e2e/vip-auth.spec.ts
import { test, expect } from "@playwright/test";

test("valid token creates VIP session", async ({ page }) => {
  await page.goto("/shop?token=test-token-123");

  // 쿠키 확인
  const cookies = await page.context().cookies();
  const vipSession = cookies.find(c => c.name === "vip_session");
  expect(vipSession).toBeDefined();

  // 리다이렉트 확인
  expect(page.url()).not.toContain("token=");
});

test("invalid token redirects to /invalid-token", async ({ page }) => {
  await page.goto("/shop?token=invalid-token");

  expect(page.url()).toContain("/invalid-token");
});

test("protected page without session redirects to home", async ({ page }) => {
  await page.goto("/orders");

  expect(page.url()).toContain("/");
});
```

## 환경 변수

`.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=eyJxxx...
```

## 트러블슈팅

### 쿠키가 설정되지 않음

- HTTPS 확인 (로컬은 localhost 허용)
- 도메인이 일치하는지 확인
- SameSite 설정 확인

### 미들웨어가 실행되지 않음

- `middleware.ts`가 프로젝트 루트에 있는지 확인
- `config.matcher`에 경로가 포함되는지 확인
- Next.js 개발 서버 재시작

### VIP 조회 실패

- Supabase 환경 변수 확인
- `vips` 테이블에 데이터가 있는지 확인
- `is_active = true` 확인
- RLS 정책 확인

## 다음 단계

이 인증 시스템을 기반으로 다음 기능을 구현할 수 있습니다:

1. **이메일 초대 발송**: VIP에게 자동으로 초대 링크 발송
2. **QR 코드 가입**: QR 스캔 후 관리자 승인 플로우
3. **세션 갱신**: 만료 전 자동 갱신
4. **로그아웃**: VIP 세션 종료 기능
5. **어드민 대시보드**: VIP 관리 및 초대 토큰 생성

## 참고 자료

- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
