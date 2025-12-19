# CORE-002 완료 보고서

## 작업: VIP 초대 토큰 인증 시스템

**작업 일시**: 2025-12-19
**프로젝트**: GGP Heritage Mall
**브랜치**: feat/issue-28-token-optimization

---

## 작업 개요

VIP 전용 초대 쇼핑몰을 위한 토큰 기반 인증 시스템을 구축했습니다. URL의 초대 토큰으로 VIP를 인증하고, 세션을 관리하며, 보호된 페이지에 대한 접근 제어를 구현했습니다.

---

## 구현된 파일

### 1. 미들웨어 (D:\AI\claude01\ggp_heritage_mall\web\middleware.ts)

**기능:**
- URL 쿼리 파라미터에서 초대 토큰 추출 (`?token=xxx`)
- Supabase에서 토큰 유효성 검증
- 유효한 토큰: VIP ID를 httpOnly 쿠키에 저장 (7일 유효)
- 무효한 토큰: `/invalid-token` 페이지로 리다이렉트
- 보호된 경로 (`/shop`, `/orders`, `/profile`) 접근 제어
- 세션 없이 보호된 페이지 접근: `/` 홈으로 리다이렉트

**보호된 경로:**
```typescript
const PROTECTED_PATHS = ["/shop", "/orders", "/profile"];
```

**쿠키 설정:**
```typescript
{
  httpOnly: true,              // JavaScript 접근 방지
  secure: NODE_ENV === "production", // HTTPS only
  sameSite: "lax",            // CSRF 방지
  maxAge: 60 * 60 * 24 * 7,   // 7일
  path: "/",
}
```

---

### 2. 서버 컴포넌트 세션 관리 (D:\AI\claude01\ggp_heritage_mall\web\src\lib\auth\vip-session.ts)

**주요 함수:**

| 함수 | 설명 | 반환 타입 |
|------|------|----------|
| `getVipSession()` | 현재 VIP 세션 가져오기 | `Promise<VipSession \| null>` |
| `hasVipTier(tier)` | VIP가 특정 등급 이상인지 확인 | `Promise<boolean>` |
| `getVipOrderLimit()` | 주문 가능 최대 수량 (Silver: 3, Gold: 5) | `Promise<number>` |
| `getVipCurrentOrderCount()` | 현재까지 주문한 수량 | `Promise<number>` |
| `canVipOrder(quantity)` | 추가 주문 가능 여부 | `Promise<boolean>` |

**사용 예시:**
```typescript
import { getVipSession, canVipOrder } from "@/lib/auth";

export default async function ShopPage() {
  const vip = await getVipSession();

  if (!vip) {
    redirect("/");
  }

  const canAdd = await canVipOrder(2); // 2개 추가 가능?

  return (
    <div>
      <h1>Welcome, {vip.name || vip.email}</h1>
      <p>Tier: {vip.tier}</p>
      {!canAdd && <p>주문 수량 제한에 도달했습니다</p>}
    </div>
  );
}
```

---

### 3. 클라이언트 컴포넌트 훅 (D:\AI\claude01\ggp_heritage_mall\web\src\hooks\use-vip-session.ts)

**주요 훅:**

| 훅 | 반환값 | 설명 |
|------|--------|------|
| `useVipSession()` | `{ vip, loading }` | VIP 세션 정보 |
| `useVipOrderLimit()` | `{ limit, currentCount, remaining, canOrder, loading }` | 주문 제한 정보 |

**사용 예시:**
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
      <p>Tier: {vip.tier.toUpperCase()}</p>
      <p>주문: {currentCount} / {limit}</p>
      <p>남은 수량: {remaining}</p>
      {!canOrder(1) && <p className="text-red-500">더 이상 주문할 수 없습니다</p>}
    </div>
  );
}
```

---

### 4. 에러 페이지 (D:\AI\claude01\ggp_heritage_mall\web\src\app\invalid-token\page.tsx)

**기능:**
- 유효하지 않은 토큰으로 접근 시 표시
- 사용자 친화적인 안내 메시지
- 초대 토큰을 받는 방법 안내
- 홈으로 돌아가기 버튼

**UI 요소:**
- 경고 아이콘 (빨간색)
- 설명 메시지
- 초대 토큰 받는 방법 (체크리스트)
- CTA 버튼 (홈으로 돌아가기)

---

### 5. 내보내기 모듈 (D:\AI\claude01\ggp_heritage_mall\web\src\lib\auth\index.ts)

서버 컴포넌트에서 간편하게 import할 수 있도록 통합:

```typescript
export {
  getVipSession,
  hasVipTier,
  getVipOrderLimit,
  getVipCurrentOrderCount,
  canVipOrder,
  type VipSession,
} from "./vip-session";
```

---

### 6. 문서 (D:\AI\claude01\ggp_heritage_mall\web\src\lib\auth\README.md)

**포함 내용:**
- 시스템 개요
- 아키텍처 설명
- 사용 예시 (서버/클라이언트)
- 보안 설정
- 테스트 가이드
- 트러블슈팅

---

## 인증 플로우

### 1. 초대 토큰 인증 플로우

```
사용자가 이메일에서 초대 링크 클릭
https://heritage-mall.ggpoker.com/shop?token=abc123

   ↓

middleware.ts: 토큰 파라미터 감지

   ↓

Supabase에서 VIP 조회
SELECT * FROM vips
WHERE invite_token = 'abc123'
AND is_active = true

   ↓

토큰 유효?
  - YES → VIP ID를 쿠키에 저장 (vip_session)
         → /shop 페이지로 리다이렉트 (토큰 제거)
         → VIP로 쇼핑 시작

  - NO  → /invalid-token 페이지로 리다이렉트
         → 에러 메시지 표시
```

### 2. 보호된 페이지 접근 플로우

```
사용자가 /orders 페이지 접근

   ↓

middleware.ts: 보호된 경로 확인

   ↓

쿠키에서 vip_session 확인

   ↓

세션 존재?
  - YES → Supabase에서 VIP 유효성 재확인
         → VIP 활성화?
            - YES → 페이지 접근 허용
            - NO  → 쿠키 삭제 후 / 홈으로 리다이렉트

  - NO  → / 홈으로 리다이렉트
```

### 3. VIP 주문 수량 제한 플로우

```
VIP가 상품을 장바구니에 추가

   ↓

canVipOrder(quantity) 호출

   ↓

현재 주문 수량 조회
SELECT SUM(order_items.quantity)
FROM orders
JOIN order_items ON orders.id = order_items.order_id
WHERE orders.vip_id = <vip_id>
AND orders.status != 'cancelled'

   ↓

제한 확인
currentCount + quantity <= limit?
  - Silver: limit = 3
  - Gold: limit = 5

   ↓

결과 반환
  - true: 추가 가능
  - false: 수량 제한 초과
```

---

## 보안 기능

### 1. HttpOnly 쿠키

```typescript
httpOnly: true // JavaScript로 쿠키 접근 불가
```

브라우저의 `document.cookie`로 접근할 수 없어 XSS 공격 방지.

### 2. HTTPS Only (프로덕션)

```typescript
secure: process.env.NODE_ENV === "production"
```

프로덕션에서는 HTTPS 연결에서만 쿠키 전송.

### 3. SameSite 설정

```typescript
sameSite: "lax"
```

크로스 사이트 요청 위조(CSRF) 공격 방지.

### 4. 쿠키 만료 (7일)

```typescript
maxAge: 60 * 60 * 24 * 7
```

7일 후 자동 만료되어 오래된 세션 방지.

### 5. 서버 사이드 검증

모든 보호된 페이지에서 서버 사이드에서 VIP 유효성 재확인:

```typescript
const { data: vip, error } = await supabase
  .from("vips")
  .select("id, email, tier, is_active")
  .eq("id", vipSessionId)
  .eq("is_active", true)
  .single();
```

---

## 테스트 방법

### 1. 수동 테스트

#### 1.1 테스트 VIP 생성

Supabase SQL Editor에서 실행:

```sql
INSERT INTO vips (email, tier, invite_token, is_active)
VALUES ('test@example.com', 'gold', 'test-token-123', true);
```

#### 1.2 유효한 토큰 테스트

1. 브라우저에서 접근:
   ```
   http://localhost:3000/shop?token=test-token-123
   ```

2. 예상 결과:
   - `/shop` 페이지로 리다이렉트 (토큰 제거됨)
   - 브라우저 DevTools > Application > Cookies에서 `vip_session` 확인

#### 1.3 무효한 토큰 테스트

1. 브라우저에서 접근:
   ```
   http://localhost:3000/shop?token=invalid-token
   ```

2. 예상 결과:
   - `/invalid-token` 페이지 표시
   - 에러 메시지 표시

#### 1.4 보호된 페이지 접근 테스트

1. 쿠키 있을 때:
   ```
   http://localhost:3000/orders
   ```
   → 페이지 접근 가능

2. 쿠키 삭제 후:
   - DevTools > Application > Cookies에서 `vip_session` 삭제
   - 다시 `/orders` 접근
   → `/` 홈으로 리다이렉트

#### 1.5 VIP 등급 테스트

1. Silver VIP 생성:
   ```sql
   INSERT INTO vips (email, tier, invite_token, is_active)
   VALUES ('silver@example.com', 'silver', 'silver-token', true);
   ```

2. Gold VIP 생성:
   ```sql
   INSERT INTO vips (email, tier, invite_token, is_active)
   VALUES ('gold@example.com', 'gold', 'gold-token', true);
   ```

3. 각 토큰으로 로그인 후 주문 제한 확인:
   - Silver: 3개
   - Gold: 5개

---

### 2. 자동 테스트 (Playwright)

테스트 파일: `tests/e2e/vip-auth.spec.ts` (예정)

```typescript
import { test, expect } from "@playwright/test";

test.describe("VIP Authentication", () => {
  test("valid token creates session", async ({ page }) => {
    await page.goto("/shop?token=test-token-123");

    // 쿠키 확인
    const cookies = await page.context().cookies();
    const vipSession = cookies.find((c) => c.name === "vip_session");
    expect(vipSession).toBeDefined();

    // 리다이렉트 확인 (토큰 제거)
    expect(page.url()).not.toContain("token=");
    expect(page.url()).toContain("/shop");
  });

  test("invalid token shows error page", async ({ page }) => {
    await page.goto("/shop?token=invalid-token");

    expect(page.url()).toContain("/invalid-token");
    await expect(page.locator("h1")).toContainText("유효하지 않은");
  });

  test("protected page without session redirects", async ({ page }) => {
    await page.goto("/orders");

    expect(page.url()).not.toContain("/orders");
    expect(page.url()).toMatch(/\/$|\/$/); // 홈페이지
  });

  test("VIP tier limits are enforced", async ({ page, context }) => {
    // Silver VIP 로그인
    await page.goto("/shop?token=silver-token");

    // 3개 주문 후 제한 메시지 확인
    // (실제 테스트는 주문 플로우 구현 후 작성)
  });
});
```

---

## 환경 변수

`.env.local` 파일:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=eyJxxx...
```

---

## 디렉터리 구조

```
web/
├── middleware.ts                # Next.js 미들웨어 (토큰 검증, 경로 보호)
├── src/
│   ├── app/
│   │   └── invalid-token/
│   │       └── page.tsx        # 무효한 토큰 에러 페이지
│   ├── lib/
│   │   └── auth/
│   │       ├── index.ts        # 통합 export
│   │       ├── vip-session.ts  # 서버 컴포넌트 세션 관리
│   │       └── README.md       # 상세 문서
│   └── hooks/
│       └── use-vip-session.ts  # 클라이언트 훅
```

---

## 다음 단계

이 인증 시스템을 기반으로 다음 기능을 구현할 예정:

1. **이메일 초대 발송**
   - VIP 생성 시 자동으로 초대 링크 이메일 발송
   - 이메일 템플릿: GGP 브랜딩 + 초대 링크

2. **QR 코드 가입**
   - QR 코드 스캔 페이지 (`/qr-signup`)
   - 6자리 인증 코드 입력
   - 관리자 승인 대기 플로우

3. **세션 갱신**
   - 만료 전 자동 갱신 (refresh token 개념)
   - 사용자 활동 감지 시 세션 연장

4. **로그아웃 기능**
   - VIP 세션 종료 버튼
   - 쿠키 삭제 + 서버 세션 무효화

5. **어드민 대시보드**
   - VIP 목록 조회/관리
   - 초대 토큰 생성
   - QR 코드 승인/거부
   - 주문 수량 모니터링

---

## 트러블슈팅

### 쿠키가 설정되지 않음

**증상:** 유효한 토큰으로 로그인했지만 쿠키가 보이지 않음

**해결:**
1. HTTPS 확인 (로컬은 localhost 허용)
2. 브라우저 개발자 도구 > Application > Cookies 확인
3. SameSite 설정 확인
4. 도메인이 일치하는지 확인

### 미들웨어가 실행되지 않음

**증상:** 토큰을 포함한 URL로 접근해도 아무 일도 일어나지 않음

**해결:**
1. `middleware.ts`가 프로젝트 루트에 있는지 확인
2. `config.matcher`에 경로가 포함되는지 확인
3. Next.js 개발 서버 재시작

### VIP 조회 실패

**증상:** 유효한 토큰인데도 `/invalid-token`으로 리다이렉트됨

**해결:**
1. Supabase 환경 변수 확인 (`.env.local`)
2. `vips` 테이블에 데이터가 있는지 확인
3. `is_active = true` 확인
4. Supabase RLS 정책 확인

---

## 참고 자료

- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [GGP Heritage Mall PRD](../tasks/prds/CORE-002-vip-auth.md)

---

## 완료 조건 체크리스트

- [x] 초대 토큰 검증 미들웨어 구현
- [x] VIP 세션 관리 (쿠키 기반)
- [x] 인증 실패 시 리다이렉트 (`/invalid-token`)
- [x] 보호된 경로 접근 제어
- [x] VIP 등급별 주문 수량 제한 구현
- [x] 서버 컴포넌트 헬퍼 함수 (`vip-session.ts`)
- [x] 클라이언트 컴포넌트 훅 (`use-vip-session.ts`)
- [x] 에러 페이지 UI (`invalid-token/page.tsx`)
- [x] TypeScript 타입 체크 통과
- [x] 상세 문서 작성 (README.md)

---

## 마무리

CORE-002 작업이 성공적으로 완료되었습니다.

VIP 초대 토큰 인증 시스템이 완전히 구축되어, 사용자는 이메일로 받은 초대 링크로 안전하게 쇼핑몰에 접근할 수 있습니다.

또한, VIP 등급별 주문 수량 제한이 자동으로 관리되어 비즈니스 요구사항을 충족합니다.

**작성자**: Claude Opus 4.5
**작성일**: 2025-12-19
