-- 계정 잠금 테이블
-- Purpose: Track account lockouts after multiple failed login attempts
-- Created: 2025-01-14
-- PRD: Phase 5 - Rate Limiting & Security

CREATE TABLE IF NOT EXISTS account_lockouts (
  email TEXT PRIMARY KEY,
  locked_until TIMESTAMPTZ NOT NULL,
  attempt_count INTEGER DEFAULT 0,
  last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE account_lockouts ENABLE ROW LEVEL SECURITY;

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
CREATE INDEX account_lockouts_locked_until_idx ON account_lockouts(locked_until);
CREATE INDEX account_lockouts_email_idx ON account_lockouts(email);

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
