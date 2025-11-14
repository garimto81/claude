-- ===================================================================
-- Create Initial Admin User
-- Purpose: Create admin@example.com account for testing
-- ===================================================================
-- Created: 2025-01-14
-- PRD: Phase 0 - Database Setup
-- WARNING: Change credentials in production!
-- ===================================================================

-- This script creates a test admin user via Supabase Auth
-- Password: Admin1234!
-- Email: admin@example.com

-- Step 1: Create auth user (you must run this via Supabase Dashboard or API)
-- Because auth.users table can only be modified by Supabase Auth API

-- MANUAL STEP REQUIRED:
-- Go to Supabase Dashboard → Authentication → Users → Add User
-- Email: admin@example.com
-- Password: Admin1234!
-- Auto Confirm User: YES

-- Step 2: Update profile role to 'admin'
-- This assumes the trigger already created a profile with role='user'

-- Wait a moment after creating user in Dashboard, then run this:
DO $$
DECLARE
  admin_user_id UUID;
BEGIN
  -- Find the admin user by email
  SELECT id INTO admin_user_id
  FROM auth.users
  WHERE email = 'admin@example.com';

  -- If user exists, update role to admin
  IF admin_user_id IS NOT NULL THEN
    UPDATE profiles
    SET role = 'admin',
        display_name = 'Admin User'
    WHERE id = admin_user_id;

    RAISE NOTICE 'Admin user % updated to admin role', admin_user_id;
  ELSE
    RAISE WARNING 'Admin user not found. Please create admin@example.com in Supabase Dashboard first.';
  END IF;
END $$;

-- Create test regular user profile update (optional)
DO $$
DECLARE
  user_user_id UUID;
BEGIN
  -- Find the user by email
  SELECT id INTO user_user_id
  FROM auth.users
  WHERE email = 'user@example.com';

  -- If user exists, update display name
  IF user_user_id IS NOT NULL THEN
    UPDATE profiles
    SET display_name = 'Regular User'
    WHERE id = user_user_id;

    RAISE NOTICE 'Regular user % updated', user_user_id;
  ELSE
    RAISE NOTICE 'Regular user not found (this is optional).';
  END IF;
END $$;

-- Comments
COMMENT ON SCRIPT IS 'Creates initial admin@example.com user. MUST create user in Dashboard first, then run this to set admin role.';

-- Confirm
DO $$
BEGIN
  RAISE NOTICE '=================================================================';
  RAISE NOTICE 'IMPORTANT: Create users manually in Supabase Dashboard first!';
  RAISE NOTICE '';
  RAISE NOTICE '1. Go to: Dashboard → Authentication → Users → Add User';
  RAISE NOTICE '2. Email: admin@example.com, Password: Admin1234!';
  RAISE NOTICE '3. Email: user@example.com, Password: User1234! (optional)';
  RAISE NOTICE '4. Then run this migration again to set admin role';
  RAISE NOTICE '=================================================================';
END $$;
