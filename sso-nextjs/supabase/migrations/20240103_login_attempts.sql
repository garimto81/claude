-- 로그인 시도 기록 테이블
-- Purpose: Track all login attempts (success/failure) for security audit
-- Created: 2025-01-14
-- PRD: Phase 5 - Rate Limiting & Security

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
CREATE INDEX login_attempts_email_created_idx ON login_attempts(email, created_at DESC);
CREATE INDEX login_attempts_ip_created_idx ON login_attempts(ip_address, created_at DESC);
CREATE INDEX login_attempts_created_idx ON login_attempts(created_at DESC);

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
