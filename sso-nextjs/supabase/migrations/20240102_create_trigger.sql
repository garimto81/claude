-- ===================================================================
-- Auto-create Profile Trigger
-- Purpose: Automatically create profile when user signs up
-- ===================================================================
-- Created: 2025-01-14
-- PRD: Phase 0 - Database Setup
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
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Comments
COMMENT ON FUNCTION handle_new_user() IS 'Automatically creates profile when new user signs up via Supabase Auth';
COMMENT ON TRIGGER on_auth_user_created ON auth.users IS 'Triggers handle_new_user() after INSERT on auth.users';

-- Confirm creation
DO $$
BEGIN
  RAISE NOTICE 'Auto-create profile trigger installed successfully.';
END $$;
