import { test, expect } from '@playwright/test';

test.describe('홈 페이지', () => {
  test('홈 페이지 렌더링 확인', async ({ page }) => {
    await page.goto('/');

    // 메인 타이틀 확인
    await expect(page.getByRole('heading', { name: 'GGP Heritage Mall' })).toBeVisible();

    // 서브 타이틀 확인
    await expect(page.getByText('VIP Exclusive Shopping Experience')).toBeVisible();

    // 초대 링크 안내 메시지 확인
    await expect(page.getByText('Access requires a valid invitation link')).toBeVisible();
  });

  test('페이지 타이틀 확인', async ({ page }) => {
    await page.goto('/');

    // 페이지 타이틀에 GGP 포함 확인
    await expect(page).toHaveTitle(/GGP|Heritage/i);
  });
});
