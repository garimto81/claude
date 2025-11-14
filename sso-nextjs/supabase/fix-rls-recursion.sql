-- ===================================================================
-- FIX: Remove infinite recursion in RLS policies
--
-- Problem: Policies that SELECT from profiles cause circular reference
-- Solution: Simplify policies to avoid recursion
-- ===================================================================

-- 1. Drop the problematic "Admin can view all profiles" policy
DROP POLICY IF EXISTS "Admin can view all profiles" ON profiles;

-- 2. Replace "Users can update own profile" with simpler version (no role check)
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Note: Service role (used in auth.ts) bypasses RLS automatically.
-- The role check is removed to prevent recursion - role changes
-- should be handled at the application level or via service role.
