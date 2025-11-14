# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Project**: NextAuth.js + Supabase SSO Integration
**Status**: Phase 1 Complete - Basic NextAuth.js implementation with placeholder auth (v0.1.0)
**PRD**: See `docs/prd.md` for complete requirements (v2.0 - 2025-01-13 업데이트)
**Current Version**: 0.0.0 (Phase 1 완료, Supabase 통합 대기 중)

---

## Project Overview

This is a Next.js 14 authentication system integrating NextAuth.js v5 with Supabase. The project follows the Phase 0-6 development cycle defined in the parent repository's global workflow system.

**Key Technologies**:
- Next.js 14.2+ (App Router)
- NextAuth.js v5 beta.29+ (Auth.js)
- Supabase (PostgreSQL + Auth)
- TypeScript 5.0+
- TailwindCSS
- Sentry (에러 추적)
- Pino (구조화된 로깅)

**Authentication Flow**:
1. User submits credentials → NextAuth Credentials Provider
2. Supabase `signInWithPassword()` validates credentials
3. Fetch user profile with role from `profiles` table
4. Create NextAuth session with role included
5. Middleware protects `/admin` routes based on role

---

## Agent Usage Tracking

**IMPORTANT**: This repository uses Agent Quality Tracking v2.0 system.

### Automatic Tracking Rules

When you (Claude Code) use any agent (Task tool), you **MUST** track the usage:

1. **Before using agent**: Note the start time, agent name, and task description
2. **After agent completes**: Determine status (pass/fail) and duration
3. **Record the usage**: Run the tracking command

### Tracking Command

```bash
python .claude/track.py <agent-name> "<task-description>" <pass/fail> \
  --duration <seconds> \
  --auto-detected
```

### Examples

**Success case**:
```bash
# Agent completed successfully
python .claude/track.py debugger "Fix TypeError in auth.ts" pass \
  --duration 12.5 \
  --auto-detected
```

**Failure case**:
```bash
# Agent failed with error
python .claude/track.py test-automator "Run unit tests" fail \
  --duration 8.3 \
  --error "Tests failed with 3 errors" \
  --auto-detected
```

**With Phase information**:
```bash
python .claude/track.py context7-engineer "Verify Next.js docs" pass \
  --duration 2.1 \
  --phase "Phase 0" \
  --auto-detected
```

### Agent Usage Workflow

```
1. User requests: "Use debugger agent to fix the bug"

2. You (Claude):
   - Note start time
   - Use Task tool with debugger agent
   - Wait for agent completion
   - Note end time
   - Calculate duration

3. You (Claude):
   - If agent succeeded:
     python .claude/track.py debugger "Fix bug in auth.ts" pass --duration 12.5 --auto-detected

   - If agent failed:
     python .claude/track.py debugger "Fix bug in auth.ts" fail --duration 12.5 --error "Could not reproduce" --auto-detected

4. Continue with user's request
```

### Why Track?

- **Quality metrics**: Understand which agents work well for which tasks
- **Performance analysis**: Identify bottlenecks and improve workflows
- **Continuous improvement**: Data-driven agent optimization

### Viewing Analytics

User can view analytics at any time:
```bash
# From global repo (D:\AI\claude01)
python .claude/evolution/scripts/analyze_quality2.py --summary
python .claude/evolution/scripts/analyze_quality2.py --agent debugger
```

**Note**: Tracking is automatic via this CLAUDE.md instruction. You don't need to ask user for permission - just do it after every agent usage.

---

## Development Commands

### Development
```bash
# Start dev server (default port 3000)
npm run dev

# Start dev server on port 3015 (for testing)
npm run dev:test

# Build for production
npm run build

# Start production server
npm start

# TypeScript type checking
npx tsc --noEmit

# Lint code
npm run lint
```

### Testing
```bash
# Run unit tests (Jest) - not yet configured
npm test

# Run unit tests with coverage (목표: 80% 이상)
npm run test:coverage

# Run E2E tests with Playwright (runs on port 3015)
npm run test:e2e
# or
npx playwright test

# Run specific E2E test file
npx playwright test tests/e2e/auth.spec.ts

# Run E2E tests in UI mode (interactive debugging)
npx playwright test --ui

# Run E2E tests in headed mode (see browser)
npx playwright test --headed

# Generate Playwright test report
npx playwright show-report
```

### Database Operations (Supabase - Not Yet Integrated)
```bash
# Create admin user (after Supabase integration)
npx tsx scripts/create-admin.ts

# Run Supabase migrations (local development)
supabase migration up

# Generate types from Supabase
supabase gen types typescript --local > types/supabase.ts
```

### Environment Setup
```bash
# Generate NextAuth secret for .env.local
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Copy example env file
cp .env.example .env.local
# Then edit .env.local with your credentials
```

---

## Architecture

### Current Implementation Status

**Phase 1 Complete** ✅:
- NextAuth.js v5 configuration with Credentials Provider
- Basic login/logout functionality with Server Actions
- JWT-based session management (24-hour duration)
- Role-based session data (admin/user)
- E2E tests for authentication flow with Playwright
- TypeScript type extensions for session/user

**Pending Implementation** (Phases 2+):
- Supabase integration for real authentication
- Rate limiting and account lockout
- Login attempt logging
- User registration flow
- Middleware for route protection
- Error handling with custom error codes
- Sentry integration for error tracking
- Pino logging for structured logs

### Authentication Components

**Core Files (Implemented)**:
- `auth.ts` - NextAuth v5 configuration with Credentials Provider
  - Currently uses placeholder test accounts (admin@example.com, user@example.com)
  - JWT callbacks to add `id` and `role` to token
  - Session callbacks to expose user data to client
- `app/api/auth/[...nextauth]/route.ts` - NextAuth API route handler (GET/POST)
- `app/actions/auth.ts` - Server Actions for login/logout
  - `authenticate()` - Form action for credential validation
  - `logout()` - Server action for sign out
- `types/next-auth.d.ts` - TypeScript module augmentation
  - Extends `Session.user` with `id` and `role`
  - Extends `JWT` interface with `id` and `role`
- `app/providers.tsx` - Client-side SessionProvider wrapper

**UI Components (Implemented)**:
- `app/login/page.tsx` - Login form with email/password fields
  - Uses `useFormState` for server-side validation errors
  - Displays test credentials for development
- `app/admin/page.tsx` - Protected admin dashboard
  - Shows user email and role
  - Logout button
- `app/page.tsx` - Home page with login/admin links
  - Shows session status

**Key Routes**:
- `/` - Home page (public)
- `/login` - Login page (public, redirects to `/admin` on success)
- `/admin` - Admin dashboard (currently not protected by middleware)
- `/api/auth/*` - NextAuth endpoints (signIn, signOut, session, etc.)

### Test Accounts (Current Placeholder Auth)

The application currently uses hardcoded test accounts in `auth.ts`:

- **Admin Account**:
  - Email: `admin@example.com`
  - Password: `Admin1234!`
  - Role: `admin`

- **User Account**:
  - Email: `user@example.com`
  - Password: `User1234!`
  - Role: `user`

These will be replaced with Supabase authentication in Phase 2.

### Supabase Schema (Not Yet Implemented)

**Tables (To Be Created)**:
```sql
-- profiles table (extends auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- login_attempts table (로그인 시도 기록)
CREATE TABLE login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  user_agent TEXT,
  success BOOLEAN NOT NULL DEFAULT false,
  failure_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- account_lockouts table (계정 잠금)
CREATE TABLE account_lockouts (
  email TEXT PRIMARY KEY,
  locked_until TIMESTAMPTZ NOT NULL,
  attempt_count INTEGER DEFAULT 0,
  last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Triggers**:
- `handle_new_user()` - Auto-creates profile when user signs up

**Migrations**:
- `20240101_create_profiles.sql` - profiles 테이블 및 RLS
- `20240102_create_trigger.sql` - 자동 프로필 생성 트리거
- `20240103_login_attempts.sql` - 로그인 시도 로깅 (신규)
- `20240104_account_lockouts.sql` - 계정 잠금 관리 (신규)

### Session Management

NextAuth.js uses JWT strategy with httpOnly cookies:
- Session includes: `{ user: { id, email, role, name } }`
- Token stored in httpOnly cookie (XSS prevention)
- CSRF protection built-in
- Session duration: 24 hours

### Middleware Protection (To Be Implemented)

**Current Status**: No middleware implemented yet. All routes are publicly accessible.

**Planned Implementation**: Routes matching `/admin/*` and `/dashboard/*` will be protected:
1. Check if session exists → redirect to `/login` if not
2. Check if `session.user.role === 'admin'` → redirect to `/forbidden` if not
3. Allow access if both conditions pass

File to create: `middleware.ts` in project root.

---

## Environment Variables

**Current Requirements** (Phase 1):
```bash
# NextAuth.js v5 - Required
AUTH_SECRET=your-generated-secret-min-32-chars
AUTH_URL=http://localhost:3000

# Node Environment
NODE_ENV=development
```

**Future Requirements** (Phase 2+ with Supabase):
```bash
# Supabase - Not yet required
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Setup Instructions**:
1. Copy `.env.example` to `.env.local`
2. Generate `AUTH_SECRET`: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
3. Set `AUTH_URL=http://localhost:3000` (or your local dev URL)

**Production (Vercel)**:
- Set `AUTH_URL` to production domain (e.g., `https://your-app.vercel.app`)
- Use different `AUTH_SECRET` than development
- Never commit `.env.local` to git (already in `.gitignore`)

---

## Security Considerations

### Built-in Protections
- **httpOnly cookies** - Prevents XSS token theft (NextAuth default)
- **CSRF tokens** - Automatic CSRF protection (NextAuth built-in)
- **Secure headers** - X-Frame-Options, X-Content-Type-Options via `next.config.js`

### Required Implementation (PRD v2.0)
- [ ] **Rate limiting** - 5회 로그인 실패 시 10분간 계정 잠금
- [ ] **Login attempt logging** - IP 주소, User-Agent, 성공/실패 기록
- [ ] **Account lockout system** - `account_lockouts` 테이블 관리
- [ ] **Error handling strategy** - 7개 에러 코드 정의 (AUTH001~AUTH007)
- [ ] Content Security Policy (CSP) headers in middleware
- [ ] Password strength validation with Zod (min 8 chars, uppercase, lowercase, number, special char)
- [ ] RLS policies on Supabase tables (profiles, login_attempts, account_lockouts)
- [ ] Environment variable validation on startup

### Rate Limiting Implementation
로그인 시도 제한:
- 동일 이메일 5회 실패 → 10분 계정 잠금
- IP 주소별 시간당 최대 20회 시도
- 자동 해제: 10분 경과 후 또는 Admin 수동 해제

```typescript
// lib/rate-limiter.ts
export async function checkAccountLockout(email: string): Promise<boolean>
export async function recordLoginAttempt(email, ip, userAgent, success, failureReason)
```

### Supabase RLS Policies
```sql
-- Users can only view their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

-- Users can only update their own profile (except role)
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);
```

---

## Testing Strategy

### Coverage Goals (PRD v2.0)
- **Unit Test Coverage**: 80% 이상
- **E2E Test Coverage**: 모든 critical path
- **Performance**: 로그인 응답시간 < 500ms (p95)

### Unit Tests (lib/__tests__/)
- Test NextAuth configuration callbacks
- Test credential validation logic
- Test session/JWT token generation
- Test rate limiting logic (checkAccountLockout, recordLoginAttempt)
- Test error handling (AuthError, AuthErrorCode)
- Test password validation (Zod schema)

### Integration Tests
- Test 회원가입 API (`/api/auth/register`)
- Test 로그인 시도 로깅
- Test 계정 잠금 로직 (5회 실패)
- Test Supabase RLS policies

### E2E Tests (tests/e2e/) - Playwright

**Implemented** ✅ (`tests/e2e/auth.spec.ts`):
- ✅ Show login page with email/password fields
- ✅ Login with admin credentials → redirects to `/admin`
- ✅ Login with user credentials → redirects to `/admin`
- ✅ Login with invalid credentials → shows error message
- ✅ Access `/admin` without auth → redirects to `/login` (currently NOT working - no middleware)
- ✅ Logout → redirects to home page
- ✅ Show user status on home page when logged in

**To Be Implemented** (Future Phases):
- 회원가입 flow (register with valid/invalid data)
- 계정 잠금/해제 (5 failed attempts → lockout)
- Admin 권한 검증 (non-admin cannot access `/admin`)
- Rate limiting enforcement
- Password validation errors

**Critical Test**: Admin role enforcement
```typescript
test('non-admin cannot access admin dashboard', async ({ page }) => {
  // Login as regular user
  await loginAs(page, 'user@example.com', 'password')

  // Try to access /admin
  await page.goto('/admin')

  // Should redirect to /forbidden
  await expect(page).toHaveURL('/forbidden')
})
```

**New Test**: Rate limiting enforcement
```typescript
test('account locks after 5 failed login attempts', async ({ page }) => {
  const email = 'test@example.com'

  // Attempt 5 failed logins
  for (let i = 0; i < 5; i++) {
    await loginAs(page, email, 'wrong-password')
  }

  // 6th attempt should show lockout message
  await loginAs(page, email, 'correct-password')
  await expect(page.locator('[role="alert"]')).toContainText('계정이 일시적으로 잠겼습니다')
})
```

---

## Development Workflow

This project follows the parent repository's Phase 0-6 workflow (PRD v2.0 확장):

1. **Phase 0**: 환경 설정
2. **Phase 1**: NextAuth.js 기본 설정
3. **Phase 1.5**: 보안 강화 (Rate limiting, 로깅) ← 신규
4. **Phase 2**: Supabase 통합
5. **Phase 2.5**: 사용자 등록 ← 신규
6. **Phase 3**: 인증 구현
7. **Phase 3.5**: UI/UX Polish (접근성) ← 신규
8. **Phase 4**: 보호된 페이지
9. **Phase 5**: 테스트 및 검증 (커버리지 80%)
10. **Phase 6**: Production 배포
11. **Phase 6.5**: 운영/모니터링 (Sentry, 헬스체크) ← 신규

**예상 시간**: 12-16시간 (경험 있는 개발자 기준)

**Commit Format**: `feat: Add rate limiting (v1.0.0) [PRD-0004]`

---

## Integration with Parent Workflow

This project is located in the global workflow repository at `D:\AI\claude01\`. Key integrations:

- **PRD Reference**: All commits should reference `[PRD-0004]`
- **Task Generation**: Use parent's `scripts/generate_tasks.py`
- **Agent Optimization**: Post-commit hooks analyze agent usage
- **GitHub Automation**: Auto PR/merge on feature branch push

**Important**: When committing, reference the parent PRD number to maintain traceability.

---

## Common Issues & Solutions

### Issue: NextAuth session undefined in Server Components
**Solution**: Use `await auth()` from `@/auth`, not `useSession()` hook (which is client-side only)

### Issue: CSRF error during login
**Solution**: Ensure you're using Server Actions (not API routes) for form submission. The current implementation uses `app/actions/auth.ts` with Server Actions to avoid CSRF issues.

### Issue: Role not included in session
**Solution**: Verify both `jwt()` and `session()` callbacks in `auth.ts` pass role through:
- JWT callback: `token.role = (user as ExtendedUser).role || "user"`
- Session callback: `session.user.role = token.role as string`

### Issue: TypeScript errors on `session.user.role`
**Solution**: Ensure `types/next-auth.d.ts` is included in `tsconfig.json`. The type extensions should be automatically picked up.

### Known Limitation: No route protection yet
**Status**: Middleware is not implemented. Anyone can access `/admin` without authentication.
**Fix**: Implement `middleware.ts` in Phase 4 following NextAuth.js v5 middleware pattern.

---

## Quick Reference

### File Structure (Current vs Planned)

**Implemented** ✅:
```
app/
├── actions/
│   └── auth.ts                     # ✅ Server Actions (authenticate, logout)
├── api/
│   └── auth/
│       └── [...nextauth]/route.ts  # ✅ NextAuth handler (GET/POST)
├── admin/
│   └── page.tsx                    # ✅ Admin dashboard (not protected yet)
├── login/
│   └── page.tsx                    # ✅ Login form UI
├── globals.css                     # ✅ TailwindCSS styles
├── layout.tsx                      # ✅ Root layout
├── page.tsx                        # ✅ Home page
└── providers.tsx                   # ✅ SessionProvider wrapper

auth.ts                             # ✅ NextAuth v5 config (root level)
types/next-auth.d.ts                # ✅ Type extensions
tests/e2e/auth.spec.ts              # ✅ E2E tests with Playwright
playwright.config.ts                # ✅ Playwright configuration
next.config.js                      # ✅ Next.js config
tsconfig.json                       # ✅ TypeScript config
tailwind.config.ts                  # ✅ TailwindCSS config
.env.example                        # ✅ Environment variable template
```

**To Be Implemented** ⏳:
```
lib/
├── supabase.ts                     # ⏳ Supabase client factory
├── validators.ts                   # ⏳ Zod schemas (password, email)
├── errors.ts                       # ⏳ Custom error codes (AUTH001-007)
└── rate-limiter.ts                 # ⏳ Rate limiting logic

middleware.ts                       # ⏳ Route protection (Phase 4)

app/
├── api/auth/register/route.ts      # ⏳ User registration API
└── register/page.tsx               # ⏳ Registration form UI

supabase/migrations/                # ⏳ Database migrations
├── 20240101_create_profiles.sql
├── 20240102_create_trigger.sql
├── 20240103_login_attempts.sql
└── 20240104_account_lockouts.sql

scripts/create-admin.ts             # ⏳ Admin user creation utility

tests/
├── unit/                           # ⏳ Jest unit tests
│   ├── rate-limiter.test.ts
│   └── validators.test.ts
└── e2e/
    ├── register.spec.ts            # ⏳ Registration E2E tests
    └── rate-limiting.spec.ts       # ⏳ Rate limit E2E tests
```

### Key Functions

**Currently Implemented** ✅:
- `auth()` - Get session in Server Components (from `@/auth`)
- `signIn(provider, options)` - NextAuth sign in (internal use)
- `signOut(options)` - NextAuth sign out (internal use)
- `authenticate(prevState, formData)` - Server Action for login form (from `@/app/actions/auth`)
- `logout()` - Server Action for logout button (from `@/app/actions/auth`)

**To Be Implemented** ⏳:
- `createClient()` - Supabase client factory
- `checkAccountLockout(email)` - 계정 잠금 여부 확인
- `recordLoginAttempt(email, ip, userAgent, success, failureReason)` - 로그인 시도 기록
- `AuthError(code, message)` - 인증 에러 클래스
- `ERROR_MESSAGES` - 에러 코드별 메시지 매핑

---

## Next Steps

**Completed** ✅:
- ✅ Phase 0: 환경 설정 및 Next.js 프로젝트 생성
- ✅ Phase 1: NextAuth.js 기본 설정 (placeholder auth)
- ✅ Feature branch: `feature/PRD-0004-nextauth-supabase-v2`
- ✅ Basic E2E tests with Playwright

**Current Phase**: Phase 1.5 - 2 (보안 강화 및 Supabase 통합)

**Immediate Next Steps**:
1. **Implement middleware** - Protect `/admin` routes (Phase 4)
2. **Supabase integration** - Replace placeholder auth with real Supabase (Phase 2)
3. **Rate limiting** - Add account lockout logic (Phase 1.5)
4. **User registration** - Implement signup flow (Phase 2.5)
5. **Unit tests** - Configure Jest and add unit tests (Phase 5)

### 추천 Agent 활용 순서
1. **context7-engineer** ⭐ - NextAuth v5 beta.29 최신 문서 확인
2. **security-auditor** - 보안 요구사항 검토 (Phase 1.5)
3. **typescript-expert** - 타입 정의 작성 (errors.ts, rate-limiter.ts)
4. **database-optimizer** - Supabase 마이그레이션 최적화
5. **test-automator** - 테스트 커버리지 80% 달성
6. **playwright-engineer** ⭐ - E2E 테스트 (로그인, 회원가입, Rate limiting)

### Success Criteria
- [ ] 테스트 커버리지 80% 이상
- [ ] E2E 테스트 모든 critical path 통과
- [ ] 로그인 응답시간 < 500ms (p95)
- [ ] npm audit 0 high/critical vulnerabilities
- [ ] Lighthouse Score: Performance > 90, Accessibility > 90

---

---

## Important Notes for Future Development

### NextAuth.js v5 Specifics
- **File Location**: `auth.ts` in **project root** (not `lib/auth.ts`)
- **Server Actions**: Use Server Actions for form submission to avoid CSRF issues
- **Session in Server Components**: Use `await auth()`, not `useSession()`
- **Middleware**: NextAuth v5 middleware pattern is different from v4 - consult latest docs

### Project Path Aliases
- `@/*` maps to project root (configured in `tsconfig.json`)
- Examples:
  - `@/auth` → `auth.ts`
  - `@/app/actions/auth` → `app/actions/auth.ts`
  - `@/types/next-auth` → `types/next-auth.d.ts`

### Testing Configuration
- **E2E Tests**: Run on port 3015 (configured in `playwright.config.ts`)
- **Dev Server**: Use `npm run dev:test` for E2E testing (port 3015)
- **Regular Dev**: Use `npm run dev` (port 3000)

---

**Version**: 0.1.0 (Phase 1 완료 - 기본 NextAuth.js 구현)
**Last Updated**: 2025-01-14
**PRD Version**: 2.0 (보안/모니터링 강화)
**Remaining Effort**: 10-14 hours (Phases 2-6)
**Parent Repository**: D:\AI\claude01 (Global Workflow System)
