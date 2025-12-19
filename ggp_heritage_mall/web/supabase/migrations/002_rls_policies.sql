-- GGP Heritage Mall RLS Policies
-- Version: 1.0.0

-- Enable RLS on all tables
ALTER TABLE vips ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE admins ENABLE ROW LEVEL SECURITY;

-- Helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM admins
        WHERE user_id = auth.uid()
        AND is_active = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- VIPs Policies
-- VIPs can view their own data
CREATE POLICY "vips_select_own" ON vips
    FOR SELECT USING (id = auth.uid());

-- VIPs can update their own shipping address
CREATE POLICY "vips_update_own" ON vips
    FOR UPDATE USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Admins can do everything on vips
CREATE POLICY "vips_admin_all" ON vips
    FOR ALL USING (is_admin());

-- Verification Codes Policies
-- VIPs can view their own verification codes
CREATE POLICY "verification_codes_select_own" ON verification_codes
    FOR SELECT USING (vip_id = auth.uid());

-- Only admins can manage verification codes
CREATE POLICY "verification_codes_admin_all" ON verification_codes
    FOR ALL USING (is_admin());

-- Categories Policies
-- Anyone can view active categories
CREATE POLICY "categories_select_active" ON categories
    FOR SELECT USING (is_active = true);

-- Admins can manage categories
CREATE POLICY "categories_admin_all" ON categories
    FOR ALL USING (is_admin());

-- Products Policies
-- Authenticated users can view active products with matching tier
CREATE POLICY "products_select_active" ON products
    FOR SELECT USING (
        is_active = true
        AND (
            tier_required = 'silver'
            OR (
                tier_required = 'gold'
                AND EXISTS (
                    SELECT 1 FROM vips
                    WHERE id = auth.uid()
                    AND tier = 'gold'
                )
            )
        )
    );

-- Admins can manage products
CREATE POLICY "products_admin_all" ON products
    FOR ALL USING (is_admin());

-- Inventory Policies
-- Anyone can view inventory (read-only)
CREATE POLICY "inventory_select" ON inventory
    FOR SELECT USING (true);

-- Admins can manage inventory
CREATE POLICY "inventory_admin_all" ON inventory
    FOR ALL USING (is_admin());

-- Orders Policies
-- VIPs can view their own orders
CREATE POLICY "orders_select_own" ON orders
    FOR SELECT USING (vip_id = auth.uid());

-- VIPs can create orders for themselves
CREATE POLICY "orders_insert_own" ON orders
    FOR INSERT WITH CHECK (vip_id = auth.uid());

-- Admins can manage all orders
CREATE POLICY "orders_admin_all" ON orders
    FOR ALL USING (is_admin());

-- Order Items Policies
-- VIPs can view their own order items
CREATE POLICY "order_items_select_own" ON order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND orders.vip_id = auth.uid()
        )
    );

-- VIPs can insert items to their own orders
CREATE POLICY "order_items_insert_own" ON order_items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND orders.vip_id = auth.uid()
        )
    );

-- Admins can manage all order items
CREATE POLICY "order_items_admin_all" ON order_items
    FOR ALL USING (is_admin());

-- Admins Policies
-- Admins can view themselves
CREATE POLICY "admins_select_self" ON admins
    FOR SELECT USING (user_id = auth.uid());

-- Only admins can view all admins
CREATE POLICY "admins_admin_all" ON admins
    FOR ALL USING (is_admin());
