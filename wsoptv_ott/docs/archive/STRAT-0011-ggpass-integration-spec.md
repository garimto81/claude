# STRAT-0011: GGPass Integration Specification

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | Critical |
| **Created** | 2026-01-19 |
| **Author** | Claude Code |
| **References** | PRD-0002, PRD-0005, STRAT-0003 |

---

## Executive Summary

WSOPTV OTT 플랫폼과 **GGPass/GGPoker 시스템 연동**을 위한 상세 API 스펙을 정의합니다. OAuth 2.0 기반 SSO, 빌링 웹훅, 칩 생성 API, HUD 통계 API를 포함합니다.

### 연동 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WSOPTV OTT Platform                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │  Auth Module │    │Billing Module│    │ Stats Module │           │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘           │
│         │                   │                   │                    │
└─────────┼───────────────────┼───────────────────┼────────────────────┘
          │                   │                   │
          │  OAuth 2.0       │  Webhooks        │  REST API
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GGPass / GGPoker                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   SSO API    │    │ Billing API  │    │  HUD Stats   │           │
│  │  (OAuth 2.0) │    │  (Webhooks)  │    │     API      │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐                               │
│  │   Chip API   │    │  Player API  │                               │
│  └──────────────┘    └──────────────┘                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. GGPass SSO (OAuth 2.0)

### 1.1 Authentication Flow

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│   User     │     │  WSOPTV    │     │  GGPass    │     │  GGPoker   │
│            │     │   Client   │     │   SSO      │     │   API      │
└─────┬──────┘     └─────┬──────┘     └─────┬──────┘     └─────┬──────┘
      │                  │                  │                  │
      │  1. Login Click  │                  │                  │
      │─────────────────>│                  │                  │
      │                  │                  │                  │
      │                  │ 2. Redirect to   │                  │
      │                  │    /oauth/auth   │                  │
      │<─────────────────┼─────────────────>│                  │
      │                  │                  │                  │
      │  3. User Login   │                  │                  │
      │─────────────────────────────────────>│                  │
      │                  │                  │                  │
      │  4. Consent      │                  │                  │
      │<─────────────────────────────────────│                  │
      │                  │                  │                  │
      │  5. Auth Code    │                  │                  │
      │──────────────────>│<────────────────│                  │
      │                  │                  │                  │
      │                  │ 6. Exchange Code │                  │
      │                  │    for Token     │                  │
      │                  │─────────────────>│                  │
      │                  │                  │                  │
      │                  │ 7. Access Token  │                  │
      │                  │<─────────────────│                  │
      │                  │                  │                  │
      │                  │ 8. Get User Info │                  │
      │                  │─────────────────>│                  │
      │                  │                  │                  │
      │                  │ 9. User Data     │                  │
      │                  │<─────────────────│                  │
      │                  │                  │                  │
      │ 10. Login Success│                  │                  │
      │<─────────────────│                  │                  │
      │                  │                  │                  │
```

### 1.2 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/authorize` | GET | Authorization 시작 |
| `/oauth/token` | POST | Access Token 발급 |
| `/oauth/token/refresh` | POST | Token 갱신 |
| `/oauth/revoke` | POST | Token 폐기 |
| `/api/v1/userinfo` | GET | 사용자 정보 조회 |

### 1.3 Authorization Request

**Endpoint**: `GET https://sso.ggpass.com/oauth/authorize`

**Parameters**:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `client_id` | ✓ | WSOPTV 클라이언트 ID |
| `redirect_uri` | ✓ | 콜백 URL |
| `response_type` | ✓ | `code` (Authorization Code Flow) |
| `scope` | ✓ | `openid profile email ggpoker` |
| `state` | ✓ | CSRF 방지용 랜덤 문자열 |
| `code_challenge` | - | PKCE (Optional but recommended) |
| `code_challenge_method` | - | `S256` |

**Example**:
```
GET https://sso.ggpass.com/oauth/authorize?
  client_id=wsoptv_prod&
  redirect_uri=https://wsoptv.com/callback&
  response_type=code&
  scope=openid%20profile%20email%20ggpoker&
  state=abc123xyz&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
  code_challenge_method=S256
```

### 1.4 Token Request

**Endpoint**: `POST https://sso.ggpass.com/oauth/token`

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)
```

**Body**:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `grant_type` | ✓ | `authorization_code` |
| `code` | ✓ | Authorization code |
| `redirect_uri` | ✓ | 동일한 redirect_uri |
| `code_verifier` | - | PKCE verifier |

**Response** (Success - 200):
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "openid profile email ggpoker"
}
```

### 1.5 User Info Response

**Endpoint**: `GET https://sso.ggpass.com/api/v1/userinfo`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response Schema**:
```json
{
  "sub": "ggpass_12345678",
  "ggpass_id": "ggpass_12345678",
  "ggpoker_id": "ggpkr_87654321",
  "email": "user@example.com",
  "email_verified": true,
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "preferred_username": "johndoe",
  "picture": "https://cdn.ggpass.com/avatars/12345678.jpg",
  "locale": "en-US",
  "country": "US",
  "birthdate": "1990-01-15",
  "kyc_status": "verified",
  "kyc_level": 2,
  "created_at": "2023-05-20T10:30:00Z",
  "updated_at": "2026-01-15T08:45:00Z"
}
```

### 1.6 Token Lifetime

| Token Type | Lifetime | Refresh |
|-----------|:--------:|:-------:|
| Access Token | 1 hour | Yes |
| Refresh Token | 30 days | Rolling |
| ID Token | 1 hour | No |

**Refresh Token 정책**:
- Sliding window: 사용 시마다 30일 연장
- 최대 수명: 1년
- 비활성 시 만료: 90일

---

## 2. GGPass Billing

### 2.1 Subscription Flow

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   User     │     │  WSOPTV    │     │  GGPass    │
│            │     │            │     │  Billing   │
└─────┬──────┘     └─────┬──────┘     └─────┬──────┘
      │                  │                  │
      │ 1. Subscribe     │                  │
      │     Button       │                  │
      │─────────────────>│                  │
      │                  │                  │
      │                  │ 2. Create        │
      │                  │    Checkout      │
      │                  │─────────────────>│
      │                  │                  │
      │                  │ 3. Checkout URL  │
      │                  │<─────────────────│
      │                  │                  │
      │ 4. Redirect to   │                  │
      │    GGPass        │                  │
      │<─────────────────│                  │
      │                  │                  │
      │ 5. Payment       │                  │
      │    Process       │                  │
      │─────────────────────────────────────>│
      │                  │                  │
      │ 6. Payment       │                  │
      │    Complete      │                  │
      │<─────────────────────────────────────│
      │                  │                  │
      │                  │ 7. Webhook       │
      │                  │    Event         │
      │                  │<─────────────────│
      │                  │                  │
      │ 8. Subscription  │                  │
      │    Activated     │                  │
      │<─────────────────│                  │
      │                  │                  │
```

### 2.2 Create Checkout Session

**Endpoint**: `POST https://api.ggpass.com/v1/billing/checkout/sessions`

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
X-WSOPTV-Signature: sha256={signature}
```

**Request Body**:
```json
{
  "user_id": "ggpass_12345678",
  "plan_id": "wsoptv_plus",
  "success_url": "https://wsoptv.com/subscription/success",
  "cancel_url": "https://wsoptv.com/subscription/cancel",
  "metadata": {
    "wsoptv_user_id": "wsoptv_user_001",
    "promo_code": "WSOP2026"
  }
}
```

**Available Plans**:

| Plan ID | Name | Price | Billing |
|---------|------|:-----:|:-------:|
| `wsoptv_plus` | WSOP Plus | $10/month | Monthly |
| `wsoptv_plus_annual` | WSOP Plus (Annual) | $100/year | Yearly |
| `wsoptv_plus_plus` | WSOP Plus+ | $50/month | Monthly |
| `wsoptv_plus_plus_annual` | WSOP Plus+ (Annual) | $500/year | Yearly |

**Response** (Success - 201):
```json
{
  "id": "cs_live_abc123xyz",
  "url": "https://checkout.ggpass.com/session/cs_live_abc123xyz",
  "expires_at": "2026-01-19T12:00:00Z",
  "status": "pending"
}
```

### 2.3 Webhook Events

**Webhook URL**: `POST https://api.wsoptv.com/webhooks/ggpass/billing`

**Webhook Signature Verification**:
```
X-GGPass-Signature: t={timestamp},v1={signature}
```

**Signature 계산**:
```
signed_payload = "{timestamp}.{request_body}"
expected_signature = HMAC-SHA256(signed_payload, webhook_secret)
```

#### Event: subscription.created

```json
{
  "id": "evt_sub_created_001",
  "type": "subscription.created",
  "created_at": "2026-01-19T10:30:00Z",
  "data": {
    "subscription_id": "sub_live_xyz789",
    "user_id": "ggpass_12345678",
    "plan_id": "wsoptv_plus",
    "status": "active",
    "current_period_start": "2026-01-19T10:30:00Z",
    "current_period_end": "2026-02-19T10:30:00Z",
    "price_cents": 1000,
    "currency": "USD",
    "metadata": {
      "wsoptv_user_id": "wsoptv_user_001"
    }
  }
}
```

#### Event: subscription.updated

```json
{
  "id": "evt_sub_updated_001",
  "type": "subscription.updated",
  "created_at": "2026-01-20T15:00:00Z",
  "data": {
    "subscription_id": "sub_live_xyz789",
    "user_id": "ggpass_12345678",
    "previous_plan_id": "wsoptv_plus",
    "new_plan_id": "wsoptv_plus_plus",
    "status": "active",
    "upgrade": true
  }
}
```

#### Event: subscription.cancelled

```json
{
  "id": "evt_sub_cancelled_001",
  "type": "subscription.cancelled",
  "created_at": "2026-02-15T09:00:00Z",
  "data": {
    "subscription_id": "sub_live_xyz789",
    "user_id": "ggpass_12345678",
    "plan_id": "wsoptv_plus_plus",
    "status": "cancelled",
    "cancel_at_period_end": true,
    "current_period_end": "2026-02-19T10:30:00Z",
    "cancellation_reason": "user_requested"
  }
}
```

#### Event: subscription.expired

```json
{
  "id": "evt_sub_expired_001",
  "type": "subscription.expired",
  "created_at": "2026-02-19T10:30:00Z",
  "data": {
    "subscription_id": "sub_live_xyz789",
    "user_id": "ggpass_12345678",
    "plan_id": "wsoptv_plus_plus",
    "status": "expired",
    "expired_at": "2026-02-19T10:30:00Z"
  }
}
```

#### Event: payment.failed

```json
{
  "id": "evt_payment_failed_001",
  "type": "payment.failed",
  "created_at": "2026-02-19T10:35:00Z",
  "data": {
    "subscription_id": "sub_live_xyz789",
    "user_id": "ggpass_12345678",
    "amount_cents": 5000,
    "currency": "USD",
    "failure_reason": "card_declined",
    "retry_count": 1,
    "next_retry_at": "2026-02-22T10:35:00Z"
  }
}
```

### 2.4 Subscription Status API

**Endpoint**: `GET https://api.ggpass.com/v1/billing/subscriptions/{user_id}`

**Response**:
```json
{
  "subscriptions": [
    {
      "subscription_id": "sub_live_xyz789",
      "plan_id": "wsoptv_plus_plus",
      "status": "active",
      "current_period_start": "2026-01-19T10:30:00Z",
      "current_period_end": "2026-02-19T10:30:00Z",
      "cancel_at_period_end": false,
      "created_at": "2026-01-19T10:30:00Z"
    }
  ]
}
```

---

## 3. GGPoker Chip API (Cross-Promotion)

### 3.1 Chip Grant Flow

**STRAT-0003 Flow 2**: WSOPTV 구독 → GG POKER 칩 자동 생성

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  GGPass    │     │  WSOPTV    │     │  GGPoker   │     │   User     │
│  Billing   │     │            │     │  Chip API  │     │            │
└─────┬──────┘     └─────┬──────┘     └─────┬──────┘     └─────┬──────┘
      │                  │                  │                  │
      │ 1. subscription  │                  │                  │
      │    .created      │                  │                  │
      │─────────────────>│                  │                  │
      │                  │                  │                  │
      │                  │ 2. Check         │                  │
      │                  │    Eligibility   │                  │
      │                  │    (Country)     │                  │
      │                  │                  │                  │
      │                  │ 3. Grant Chips   │                  │
      │                  │    (if eligible) │                  │
      │                  │─────────────────>│                  │
      │                  │                  │                  │
      │                  │ 4. Chips Granted │                  │
      │                  │<─────────────────│                  │
      │                  │                  │                  │
      │                  │ 5. Notification  │                  │
      │                  │─────────────────────────────────────>│
      │                  │                  │                  │
```

### 3.2 Grant Chips

**Endpoint**: `POST https://api.ggpoker.com/v1/chips/grant`

**Headers**:
```
Authorization: Bearer {service_token}
Content-Type: application/json
X-WSOPTV-Request-ID: {uuid}
X-Idempotency-Key: {unique_key}
```

**Request Body**:
```json
{
  "ggpoker_id": "ggpkr_87654321",
  "amount_cents": 1000,
  "currency": "USD",
  "reason": "wsoptv_subscription_bonus",
  "subscription_id": "sub_live_xyz789",
  "plan_id": "wsoptv_plus",
  "country": "US",
  "state": "NJ",
  "idempotency_key": "wsoptv_sub_xyz789_bonus_001"
}
```

**Response** (Success - 201):
```json
{
  "transaction_id": "txn_chip_grant_abc123",
  "ggpoker_id": "ggpkr_87654321",
  "amount_cents": 1000,
  "currency": "USD",
  "balance_after_cents": 2500,
  "granted_at": "2026-01-19T10:31:00Z",
  "status": "completed"
}
```

**Response** (Ineligible Country - 403):
```json
{
  "error": {
    "code": "COUNTRY_NOT_ELIGIBLE",
    "message": "Chip grants are not available in this country",
    "details": {
      "country": "AU",
      "reason": "regulatory_restriction"
    }
  }
}
```

### 3.3 Check Chip Balance

**Endpoint**: `GET https://api.ggpoker.com/v1/chips/balance/{ggpoker_id}`

**Response**:
```json
{
  "ggpoker_id": "ggpkr_87654321",
  "balances": [
    {
      "currency": "USD",
      "amount_cents": 2500,
      "available_cents": 2500,
      "pending_cents": 0
    }
  ],
  "last_updated_at": "2026-01-19T10:31:00Z"
}
```

### 3.4 Chip Grant Rules by Country

| Country | Chip Grant | Amount Cap | Notes |
|---------|:----------:|:----------:|-------|
| US (NJ, PA, MI) | ✓ | $50/month | 합법 주만 |
| UK | ✓ | £50/month | UKGC 라이선스 |
| Canada (Ontario) | ✓ | $50 CAD/month | 온타리오만 |
| Germany | ⚠️ | €50/month | 검토 중 |
| Australia | ❌ | - | 법적 금지 |
| Japan | ❌ | - | 법적 금지 |
| Korea | ❌ | - | 법적 금지 |

---

## 4. GGPoker HUD Stats API (StatsView)

### 4.1 Get Player Stats

**Endpoint**: `GET https://api.ggpoker.com/v1/players/{player_id}/stats`

**Headers**:
```
Authorization: Bearer {service_token}
X-WSOPTV-Request-ID: {uuid}
```

**Query Parameters**:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `game_type` | - | `nlhe`, `plo`, `mixed` |
| `stake_level` | - | `micro`, `low`, `mid`, `high` |
| `period` | - | `all_time`, `last_30d`, `last_90d`, `ytd` |

**Response Schema**:
```json
{
  "player_id": "ggpkr_87654321",
  "display_name": "Phil Ivey",
  "avatar_url": "https://cdn.ggpoker.com/avatars/87654321.jpg",
  "last_updated_at": "2026-01-19T08:00:00Z",
  "stats": {
    "sample_size": {
      "hands_played": 125000,
      "tournaments_played": 450
    },
    "preflop": {
      "vpip": 28.5,
      "pfr": 22.1,
      "three_bet": 12.3,
      "four_bet": 4.2,
      "fold_to_3bet": 52.1,
      "steal_attempt": 34.5,
      "fold_to_steal": 78.2
    },
    "postflop": {
      "aggression_factor": 3.2,
      "aggression_frequency": 48.5,
      "cbet_flop": 72.3,
      "cbet_turn": 58.1,
      "cbet_river": 45.2,
      "fold_to_cbet_flop": 42.1,
      "fold_to_cbet_turn": 38.5,
      "check_raise": 8.2
    },
    "showdown": {
      "wtsd": 28.5,
      "w$sd": 52.3,
      "wwsf": 45.2
    },
    "overall": {
      "bb_per_100": 4.5,
      "roi_percent": 18.2,
      "itm_percent": 22.1
    }
  },
  "position_stats": {
    "UTG": { "vpip": 15.2, "pfr": 12.1, "win_rate": 2.1 },
    "MP": { "vpip": 18.5, "pfr": 14.2, "win_rate": 3.2 },
    "CO": { "vpip": 28.1, "pfr": 22.5, "win_rate": 5.1 },
    "BTN": { "vpip": 42.3, "pfr": 35.2, "win_rate": 8.5 },
    "SB": { "vpip": 32.1, "pfr": 18.5, "win_rate": -12.3 },
    "BB": { "vpip": 38.5, "pfr": 12.1, "win_rate": -8.5 }
  }
}
```

### 4.2 Get Player Stats (Batch)

**Endpoint**: `POST https://api.ggpoker.com/v1/players/stats/batch`

**Request Body**:
```json
{
  "player_ids": [
    "ggpkr_11111111",
    "ggpkr_22222222",
    "ggpkr_33333333"
  ],
  "game_type": "nlhe",
  "fields": ["preflop", "postflop", "showdown"]
}
```

**Response**:
```json
{
  "players": [
    {
      "player_id": "ggpkr_11111111",
      "display_name": "Player 1",
      "stats": { ... }
    },
    {
      "player_id": "ggpkr_22222222",
      "display_name": "Player 2",
      "stats": { ... }
    }
  ],
  "not_found": ["ggpkr_33333333"]
}
```

### 4.3 Stats Definitions

| Stat | Full Name | Description |
|------|-----------|-------------|
| VPIP | Voluntarily Put $ In Pot | 자발적 팟 참여 비율 |
| PFR | Pre-Flop Raise | 프리플롭 레이즈 비율 |
| 3-Bet | Three-Bet Percentage | 3-Bet 빈도 |
| AF | Aggression Factor | (Bet+Raise) / Call |
| C-Bet | Continuation Bet | 프리플롭 어그레서의 플롭 베팅 |
| WTSD | Went to Showdown | 쇼다운까지 간 비율 |
| W$SD | Won $ at Showdown | 쇼다운에서 이긴 비율 |
| WWSF | Won When Saw Flop | 플롭을 보고 이긴 비율 |

---

## 5. Error Handling

### 5.1 Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "field": "specific_field",
      "reason": "additional_context"
    },
    "request_id": "req_abc123xyz",
    "documentation_url": "https://docs.ggpass.com/errors/ERROR_CODE"
  }
}
```

### 5.2 Error Codes

| Code | HTTP Status | Description | 재시도 |
|------|:-----------:|-------------|:------:|
| `INVALID_REQUEST` | 400 | 잘못된 요청 | No |
| `AUTHENTICATION_FAILED` | 401 | 인증 실패 | No |
| `INSUFFICIENT_PERMISSIONS` | 403 | 권한 부족 | No |
| `RESOURCE_NOT_FOUND` | 404 | 리소스 없음 | No |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit 초과 | Yes |
| `INTERNAL_ERROR` | 500 | 서버 오류 | Yes |
| `SERVICE_UNAVAILABLE` | 503 | 서비스 불가 | Yes |

### 5.3 Retry Policy

| Error Type | Max Retries | Backoff |
|-----------|:-----------:|---------|
| 429 Rate Limit | 3 | Exponential (1s, 2s, 4s) |
| 500 Server Error | 3 | Exponential (2s, 4s, 8s) |
| 503 Service Unavailable | 5 | Exponential (5s, 10s, 20s, 40s, 60s) |
| Network Timeout | 3 | Fixed (5s) |

---

## 6. Rate Limits

| API | Limit | Window | Scope |
|-----|:-----:|:------:|-------|
| SSO /oauth/token | 100 | 1 min | Per Client |
| SSO /userinfo | 1000 | 1 min | Per Client |
| Billing API | 500 | 1 min | Per Client |
| Chip API | 100 | 1 min | Per Client |
| HUD Stats (Single) | 1000 | 1 min | Per Client |
| HUD Stats (Batch) | 100 | 1 min | Per Client |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705662000
```

---

## 7. Security Requirements

### 7.1 Transport Security

- **TLS 1.2+** 필수
- **Certificate Pinning** 권장 (Mobile)
- **HSTS** 활성화

### 7.2 Authentication

| 용도 | 인증 방식 |
|------|---------|
| User API | OAuth 2.0 Access Token |
| Service API | API Key + HMAC Signature |
| Webhooks | HMAC-SHA256 Signature |

### 7.3 Service-to-Service Auth

**Headers**:
```
X-WSOPTV-API-Key: {api_key}
X-WSOPTV-Timestamp: {unix_timestamp}
X-WSOPTV-Signature: {hmac_signature}
```

**Signature 계산**:
```
string_to_sign = "{method}\n{path}\n{timestamp}\n{body_hash}"
signature = HMAC-SHA256(string_to_sign, api_secret)
```

---

## 8. GG POKER 팀 협의 필요 항목

### 8.1 확정 필요 항목

| 항목 | 현재 상태 | 협의 필요 |
|------|---------|---------|
| OAuth 2.0 Endpoint URLs | 예상 | ✓ 확인 필요 |
| Client ID/Secret 발급 | 미발급 | ✓ 요청 필요 |
| Webhook Secret 발급 | 미발급 | ✓ 요청 필요 |
| HUD Stats API 범위 | 예상 | ✓ 확인 필요 |
| Rate Limits | 예상 | ✓ 협의 필요 |

### 8.2 기술 협의 필요

| 주제 | 질문 |
|------|------|
| SSO | PKCE 지원 여부? |
| SSO | Refresh Token 정책 확인 |
| Billing | Webhook retry 정책? |
| Billing | Promo code 연동 방식? |
| Chips | 국가별 제한 API? |
| Chips | Idempotency key 유효 기간? |
| HUD | 실시간 갱신 주기? |
| HUD | 대회 중 stats 접근 가능? |

### 8.3 SLA 협의

| 항목 | 요청 SLA |
|------|:--------:|
| SSO API 가용성 | 99.9% |
| Billing Webhook 전달 | < 5초 |
| HUD Stats API 응답 | < 200ms |
| Support 응답 시간 | < 4시간 |

---

## References

- [PRD-0002 WSOPTV OTT Platform MVP](../prds/PRD-0002-wsoptv-ott-platform-mvp.md)
- [PRD-0005 RFP](../prds/PRD-0005-wsoptv-ott-rfp.md)
- [PRD-0006 Advanced Mode](../prds/PRD-0006-advanced-mode.md)
- [STRAT-0003 Cross-Promotion Strategy](STRAT-0003-cross-promotion.md)
- [STRAT-0010 Legal Compliance](STRAT-0010-legal-compliance.md)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

---

*Created: 2026-01-19*
*Last Updated: 2026-01-19*

> **Note**: 이 문서의 API 스펙은 예상 설계입니다. 실제 구현 전 GGPass/GGPoker 팀과의 협의를 통해 확정해야 합니다.
