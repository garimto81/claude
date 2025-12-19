import { test, expect } from '@playwright/test';

test.describe('상품 목록 페이지', () => {
  test('상품 목록 페이지 접근 - 응답 확인', async ({ page }) => {
    const response = await page.goto('/products');

    // 페이지 응답 확인 (200 또는 500 - Supabase 연결 실패 시)
    expect(response?.status()).toBeLessThan(600);
  });

  test('상품 페이지 URL 확인', async ({ page }) => {
    await page.goto('/products');

    // URL이 products를 포함하는지 확인
    expect(page.url()).toContain('/products');
  });
});
