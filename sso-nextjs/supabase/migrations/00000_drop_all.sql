-- ===================================================================
-- 기존 데이터베이스 구조 완전 삭제
-- WARNING: 이 스크립트는 모든 데이터를 삭제합니다!
-- Production 환경에서는 절대 실행하지 마세요.
-- ===================================================================
-- Created: 2025-01-14
-- Purpose: Clean slate for fresh database setup
-- ===================================================================

-- Drop existing policies (RLS)
DROP POLICY IF EXISTS "Admin can view all login attempts" ON login_attempts;
DROP POLICY IF EXISTS "Service role can insert login attempts" ON login_attempts;
DROP POLICY IF EXISTS "Admin can view all lockouts" ON account_lockouts;
DROP POLICY IF EXISTS "Service role can manage lockouts" ON account_lockouts;
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admin can view all profiles" ON profiles;

-- Drop existing tables
DROP TABLE IF EXISTS login_attempts CASCADE;
DROP TABLE IF EXISTS account_lockouts CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Drop existing functions
DROP FUNCTION IF EXISTS cleanup_old_login_attempts() CASCADE;
DROP FUNCTION IF EXISTS cleanup_expired_lockouts() CASCADE;
DROP FUNCTION IF EXISTS unlock_account(TEXT) CASCADE;
DROP FUNCTION IF EXISTS handle_new_user() CASCADE;

-- Drop existing triggers
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Confirm cleanup
DO $$
BEGIN
  RAISE NOTICE 'Database cleanup complete. All tables, functions, and triggers have been dropped.';
END $$;
