-- GGP Heritage Mall - Seed Data
-- Initial data for development and testing

-- Categories
INSERT INTO categories (id, name, slug, description, sort_order) VALUES
  ('c1000000-0000-0000-0000-000000000001', 'Apparel', 'apparel', 'Premium clothing and accessories', 1),
  ('c1000000-0000-0000-0000-000000000002', 'Accessories', 'accessories', 'Luxury watches, bags, and more', 2),
  ('c1000000-0000-0000-0000-000000000003', 'Electronics', 'electronics', 'High-end gadgets and devices', 3),
  ('c1000000-0000-0000-0000-000000000004', 'Lifestyle', 'lifestyle', 'Premium lifestyle products', 4);

-- Sample Products
INSERT INTO products (id, name, description, category_id, tier_required, images) VALUES
  (
    'p1000000-0000-0000-0000-000000000001',
    'GGP Premium Hoodie',
    'Exclusive limited edition hoodie with embroidered GGP logo. Made from premium cotton blend.',
    'c1000000-0000-0000-0000-000000000001',
    'silver',
    ARRAY['products/hoodie-black-1.jpg', 'products/hoodie-black-2.jpg']
  ),
  (
    'p1000000-0000-0000-0000-000000000002',
    'Heritage Leather Jacket',
    'Genuine Italian leather jacket with custom gold hardware. VIP Gold exclusive.',
    'c1000000-0000-0000-0000-000000000001',
    'gold',
    ARRAY['products/jacket-leather-1.jpg', 'products/jacket-leather-2.jpg']
  ),
  (
    'p1000000-0000-0000-0000-000000000003',
    'Limited Edition Watch',
    'Swiss-made automatic watch with sapphire crystal. Serial numbered.',
    'c1000000-0000-0000-0000-000000000002',
    'gold',
    ARRAY['products/watch-gold-1.jpg', 'products/watch-gold-2.jpg']
  ),
  (
    'p1000000-0000-0000-0000-000000000004',
    'VIP Card Holder',
    'Premium leather card holder with gold embossing.',
    'c1000000-0000-0000-0000-000000000002',
    'silver',
    ARRAY['products/cardholder-1.jpg']
  ),
  (
    'p1000000-0000-0000-0000-000000000005',
    'Wireless Earbuds Pro',
    'Noise-cancelling wireless earbuds with custom case.',
    'c1000000-0000-0000-0000-000000000003',
    'silver',
    ARRAY['products/earbuds-1.jpg', 'products/earbuds-2.jpg']
  );

-- Inventory for Products
INSERT INTO inventory (product_id, size, quantity) VALUES
  -- Hoodie sizes
  ('p1000000-0000-0000-0000-000000000001', 'S', 10),
  ('p1000000-0000-0000-0000-000000000001', 'M', 15),
  ('p1000000-0000-0000-0000-000000000001', 'L', 12),
  ('p1000000-0000-0000-0000-000000000001', 'XL', 8),
  -- Leather Jacket sizes
  ('p1000000-0000-0000-0000-000000000002', 'S', 3),
  ('p1000000-0000-0000-0000-000000000002', 'M', 5),
  ('p1000000-0000-0000-0000-000000000002', 'L', 4),
  ('p1000000-0000-0000-0000-000000000002', 'XL', 2),
  -- Watch (one size)
  ('p1000000-0000-0000-0000-000000000003', 'ONE SIZE', 10),
  -- Card Holder (one size)
  ('p1000000-0000-0000-0000-000000000004', 'ONE SIZE', 50),
  -- Earbuds (one size)
  ('p1000000-0000-0000-0000-000000000005', 'ONE SIZE', 30);

-- Sample VIP Users (for testing)
INSERT INTO vips (id, email, name, tier, reg_type, invite_token) VALUES
  (
    'v1000000-0000-0000-0000-000000000001',
    'silver.vip@test.com',
    'Silver VIP Test',
    'silver',
    'email_invite',
    'test-token-silver-001'
  ),
  (
    'v1000000-0000-0000-0000-000000000002',
    'gold.vip@test.com',
    'Gold VIP Test',
    'gold',
    'email_invite',
    'test-token-gold-001'
  );

-- Note: Admin users should be created via Supabase Auth
-- and then added to the admins table manually or via migration
