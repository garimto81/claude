-- GGP Heritage Mall Storage Buckets
-- Version: 1.0.0

-- Create product images bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'product-images',
    'product-images',
    true,
    5242880, -- 5MB
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']
);

-- Storage policies for product images
CREATE POLICY "product_images_select" ON storage.objects
    FOR SELECT USING (bucket_id = 'product-images');

CREATE POLICY "product_images_insert_admin" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'product-images'
        AND (SELECT is_admin())
    );

CREATE POLICY "product_images_update_admin" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'product-images'
        AND (SELECT is_admin())
    );

CREATE POLICY "product_images_delete_admin" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'product-images'
        AND (SELECT is_admin())
    );
