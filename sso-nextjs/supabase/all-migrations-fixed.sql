-- ===================================================================
-- ALL SUPABASE MIGRATIONS (Fixed for PostgreSQL compatibility)
--
-- Purpose: Run all migrations in one go
-- Created: 2025-01-14
-- Fixed: Removed IF NOT EXISTS from CREATE POLICY
-- ===================================================================


-- ===================================================================
-- [1] Profiles 테이블 생성
-- ===================================================================

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  display_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Admin can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON profiles;

-- RLS Policy: Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

-- RLS Policy: Users can update their own profile (except role)
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (
    auth.uid() = id
    AND role = (SELECT role FROM profiles WHERE id = auth.uid())
  );

-- RLS Policy: Admin can view all profiles
CREATE POLICY "Admin can view all profiles"
  ON profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- RLS Policy: Service role can manage all profiles (for triggers)
CREATE POLICY "Service role can manage profiles"
  ON profiles FOR ALL
  USING (true)
  WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS profiles_email_idx ON profiles(email);
CREATE INDEX IF NOT EXISTS profiles_role_idx ON profiles(role);
CREATE INDEX IF NOT EXISTS profiles_created_at_idx ON profiles(created_at DESC);

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE profiles IS 'User profiles with role-based access control';
COMMENT ON COLUMN profiles.id IS 'References auth.users.id';
COMMENT ON COLUMN profiles.role IS 'User role: admin or user';
COMMENT ON COLUMN profiles.display_name IS 'User display name (defaults to email)';


-- ===================================================================
-- [2] Auto-create Profile Trigger
-- ===================================================================

-- Function: Create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Insert profile with default 'user' role
  INSERT INTO public.profiles (id, email, display_name, role)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'role', 'user')
  );
  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    -- Log error but don't block user creation
    RAISE WARNING 'Failed to create profile for user %: %', NEW.id, SQLERRM;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: On auth.users insert
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Comments
COMMENT ON FUNCTION handle_new_user() IS 'Automatically creates profile when new user signs up via Supabase Auth';


-- ===================================================================
-- [3] 로그인 시도 로깅 테이블
-- ===================================================================

CREATE TABLE IF NOT EXISTS login_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  user_agent TEXT,
  success BOOLEAN NOT NULL DEFAULT false,
  failure_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Admin can view all login attempts" ON login_attempts;
DROP POLICY IF EXISTS "Service role can insert login attempts" ON login_attempts;

-- RLS Policy: Admin만 조회 가능
CREATE POLICY "Admin can view all login attempts"
  ON login_attempts FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Service role can insert (used by auth.ts)
CREATE POLICY "Service role can insert login attempts"
  ON login_attempts FOR INSERT
  WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS login_attempts_email_created_idx ON login_attempts(email, created_at DESC);
CREATE INDEX IF NOT EXISTS login_attempts_ip_created_idx ON login_attempts(ip_address, created_at DESC);
CREATE INDEX IF NOT EXISTS login_attempts_created_idx ON login_attempts(created_at DESC);

-- Cleanup old records (90 days retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_login_attempts()
RETURNS void AS $$
BEGIN
  DELETE FROM login_attempts
  WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comment
COMMENT ON TABLE login_attempts IS 'Records all login attempts for security audit and rate limiting';
COMMENT ON FUNCTION cleanup_old_login_attempts() IS 'Delete login attempts older than 90 days (GDPR compliance)';


-- ===================================================================
-- [4] 계정 잠금 테이블
-- ===================================================================

CREATE TABLE IF NOT EXISTS account_lockouts (
  email TEXT PRIMARY KEY,
  locked_until TIMESTAMPTZ NOT NULL,
  attempt_count INTEGER DEFAULT 0,
  last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE account_lockouts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Admin can view all lockouts" ON account_lockouts;
DROP POLICY IF EXISTS "Service role can manage lockouts" ON account_lockouts;

-- RLS Policy: Admin만 조회 가능
CREATE POLICY "Admin can view all lockouts"
  ON account_lockouts FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Service role can manage lockouts (used by auth.ts)
CREATE POLICY "Service role can manage lockouts"
  ON account_lockouts FOR ALL
  USING (true)
  WITH CHECK (true);

-- Create index for performance
CREATE INDEX IF NOT EXISTS account_lockouts_locked_until_idx ON account_lockouts(locked_until);
CREATE INDEX IF NOT EXISTS account_lockouts_email_idx ON account_lockouts(email);

-- Function: 자동 잠금 해제 (cron job용)
CREATE OR REPLACE FUNCTION cleanup_expired_lockouts()
RETURNS void AS $$
BEGIN
  DELETE FROM account_lockouts
  WHERE locked_until < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Admin 수동 잠금 해제
CREATE OR REPLACE FUNCTION unlock_account(user_email TEXT)
RETURNS void AS $$
BEGIN
  -- Admin 권한 체크
  IF NOT EXISTS (
    SELECT 1 FROM profiles
    WHERE profiles.id = auth.uid()
    AND profiles.role = 'admin'
  ) THEN
    RAISE EXCEPTION 'Insufficient permissions';
  END IF;

  DELETE FROM account_lockouts
  WHERE email = user_email;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Comments
COMMENT ON TABLE account_lockouts IS 'Tracks locked accounts after 5 failed login attempts within 5 minutes';
COMMENT ON FUNCTION cleanup_expired_lockouts() IS 'Delete expired lockouts (automatic unlock after 10 minutes)';
COMMENT ON FUNCTION unlock_account(TEXT) IS 'Admin function to manually unlock an account';


-- ===================================================================
-- ✅ ALL MIGRATIONS COMPLETE
-- ===================================================================

DO $$
BEGIN
  RAISE NOTICE '========================================';
  RAISE NOTICE '✅ All migrations executed successfully!';
  RAISE NOTICE '========================================';
  RAISE NOTICE '';
  RAISE NOTICE '📝 Next steps:';
  RAISE NOTICE '   1. Create admin user in Dashboard:';
  RAISE NOTICE '      - Go to: Authentication → Users → Add User';
  RAISE NOTICE '      - Email: admin@example.com';
  RAISE NOTICE '      - Password: Admin1234!';
  RAISE NOTICE '      - ✅ Auto Confirm User';
  RAISE NOTICE '';
  RAISE NOTICE '   2. Update admin role:';
  RAISE NOTICE '      Run this SQL after creating user:';
  RAISE NOTICE '';
  RAISE NOTICE '      UPDATE profiles';
  RAISE NOTICE '      SET role = ''admin'', display_name = ''Admin User''';
  RAISE NOTICE '      WHERE email = ''admin@example.com'';';
  RAISE NOTICE '';
END $$;
