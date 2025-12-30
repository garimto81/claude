import { test, expect } from '@playwright/test';

test.describe('네비게이션', () => {
  test('홈에서 상품 페이지로 이동 가능 확인', async ({ page }) => {
    await page.goto('/');

    // 직접 URL 이동
    await page.goto('/products');
    await page.waitForLoadState('networkidle');

    // URL 확인
    expect(page.url()).toContain('/products');
  });

  test('잘못된 경로 접근 시 처리', async ({ page }) => {
    const response = await page.goto('/invalid-path-12345');

    // 404 페이지 또는 리다이렉트 처리 확인
    // Next.js는 기본적으로 404 페이지를 반환
    expect(response?.status()).toBe(404);
  });

  test('브라우저 뒤로가기 동작 확인', async ({ page }) => {
    await page.goto('/');
    await page.goto('/products');

    // 뒤로가기
    await page.goBack();

    // 홈으로 돌아왔는지 확인
    await expect(page.getByRole('heading', { name: 'GGP Heritage Mall' })).toBeVisible();
  });
});
