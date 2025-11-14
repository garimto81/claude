# Supabase Database Setup Guide

이 가이드는 Supabase 데이터베이스를 처음부터 설정하는 방법을 설명합니다.

## 📋 전체 마이그레이션 목록

```
supabase/migrations/
├── 00000_drop_all.sql              # [1] 기존 DB 완전 삭제 (선택)
├── 20240101_create_profiles.sql    # [2] Profiles 테이블 생성
├── 20240102_create_trigger.sql     # [3] 자동 프로필 생성 트리거
├── 20240103_login_attempts.sql     # [4] 로그인 시도 로깅
├── 20240104_account_lockouts.sql   # [5] 계정 잠금 관리
└── 20240105_create_admin.sql       # [6] 초기 Admin 사용자
```

---

## 🚀 Quick Start (처음 설정)

### Step 1: Supabase 프로젝트 설정

1. **Supabase Dashboard 접속**: https://dqkghhlnnskjfwntdtor.supabase.co
2. **SQL Editor 열기**: 왼쪽 메뉴 → SQL Editor → New Query

### Step 2: 기존 DB 삭제 (선택)

⚠️ **경고**: 이 단계는 모든 데이터를 삭제합니다!

```sql
-- 00000_drop_all.sql 내용 복사 → SQL Editor에 붙여넣기 → Run
```

### Step 3: 마이그레이션 실행 (순서대로)

각 파일을 순서대로 SQL Editor에서 실행:

#### 3-1. Profiles 테이블 생성
```sql
-- 20240101_create_profiles.sql 복사 → Run
-- ✅ profiles 테이블 생성
-- ✅ RLS 정책 설정
-- ✅ 인덱스 생성
```

#### 3-2. 자동 프로필 트리거 설정
```sql
-- 20240102_create_trigger.sql 복사 → Run
-- ✅ handle_new_user() 함수 생성
-- ✅ on_auth_user_created 트리거 생성
```

#### 3-3. 로그인 시도 로깅
```sql
-- 20240103_login_attempts.sql 복사 → Run
-- ✅ login_attempts 테이블 생성
-- ✅ 90일 보존 정책 함수 생성
```

#### 3-4. 계정 잠금 관리
```sql
-- 20240104_account_lockouts.sql 복사 → Run
-- ✅ account_lockouts 테이블 생성
-- ✅ 자동/수동 잠금 해제 함수 생성
```

### Step 4: 테스트 사용자 생성

#### 4-1. Supabase Dashboard에서 사용자 생성

1. **Authentication → Users → Add User** 클릭
2. **Admin 계정 생성**:
   - Email: `admin@example.com`
   - Password: `Admin1234!`
   - ✅ Auto Confirm User 체크
   - "Create User" 클릭

3. **일반 사용자 생성 (선택)**:
   - Email: `user@example.com`
   - Password: `User1234!`
   - ✅ Auto Confirm User 체크
   - "Create User" 클릭

#### 4-2. Admin 역할 부여

```sql
-- 20240105_create_admin.sql 복사 → Run
-- ✅ admin@example.com을 admin 역할로 업데이트
```

### Step 5: 확인

```sql
-- Profiles 테이블 확인
SELECT * FROM profiles;

-- 예상 결과:
-- | id (UUID)           | email                | role  | display_name |
-- |---------------------|----------------------|-------|--------------|
-- | xxxxxxxx-xxxx-...   | admin@example.com    | admin | Admin User   |
-- | yyyyyyyy-yyyy-...   | user@example.com     | user  | Regular User |
```

---

## 🔧 문제 해결

### 문제 1: "permission denied for table auth.users"

**원인**: auth.users 테이블은 Supabase Auth API를 통해서만 수정 가능

**해결**: Dashboard UI를 통해 사용자 생성 (Step 4-1)

### 문제 2: "trigger 'on_auth_user_created' already exists"

**원인**: 트리거가 이미 존재함

**해결**:
```sql
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
-- 그 다음 20240102_create_trigger.sql 다시 실행
```

### 문제 3: "profile not created automatically"

**원인**: 트리거 실행 전에 사용자 생성됨

**해결**: 수동으로 프로필 생성
```sql
INSERT INTO profiles (id, email, role, display_name)
SELECT id, email, 'user', email
FROM auth.users
WHERE id NOT IN (SELECT id FROM profiles);
```

### 문제 4: "table already exists"

**원인**: 테이블이 이미 존재

**해결**: 00000_drop_all.sql 실행 후 다시 시작

---

## 📊 데이터베이스 스키마

### profiles 테이블
```sql
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### login_attempts 테이블
```sql
CREATE TABLE login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  user_agent TEXT,
  success BOOLEAN NOT NULL DEFAULT false,
  failure_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### account_lockouts 테이블
```sql
CREATE TABLE account_lockouts (
  email TEXT PRIMARY KEY,
  locked_until TIMESTAMPTZ NOT NULL,
  attempt_count INTEGER DEFAULT 0,
  last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔐 보안 정책 (RLS)

### Profiles
- ✅ Users can view their own profile
- ✅ Users can update their own profile (except role)
- ✅ Admin can view all profiles
- ✅ Service role can manage all (for triggers)

### Login Attempts
- ✅ Admin can view all attempts
- ✅ Service role can insert (for auth.ts logging)

### Account Lockouts
- ✅ Admin can view all lockouts
- ✅ Service role can manage (for rate limiting)

---

## 🧪 테스트

### 1. 로그인 테스트
```bash
# Next.js 개발 서버 시작
npm run dev

# 브라우저에서 http://localhost:3000/login 접속
# admin@example.com / Admin1234! 로그인
```

### 2. Rate Limiting 테스트
```bash
# 5회 틀린 비밀번호 입력
# → "계정이 일시적으로 잠겼습니다. 10분 후 다시 시도해주세요." 메시지 확인
```

### 3. 로그 확인
```sql
-- 로그인 시도 기록 확인
SELECT * FROM login_attempts ORDER BY created_at DESC LIMIT 10;

-- 계정 잠금 확인
SELECT * FROM account_lockouts;
```

---

## 📝 Production Checklist

- [ ] AUTH_SECRET 변경 (32자 이상 랜덤 문자열)
- [ ] admin@example.com 비밀번호 변경
- [ ] user@example.com 삭제 (테스트 계정)
- [ ] RLS 정책 재확인
- [ ] 환경 변수 (.env.local) Git에 커밋 안 됨 확인
- [ ] Supabase Service Role Key 보안 확인

---

**작성일**: 2025-01-14
**버전**: v1.0.0
**PRD**: Phase 0 - Database Setup
