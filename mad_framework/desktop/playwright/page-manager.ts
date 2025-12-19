/**
 * Playwright Page Manager
 *
 * BrowserView → Page 전환
 * 각 LLM provider별로 독립된 Page 생성/관리
 */

import type { Browser, BrowserContext, Page } from 'playwright';
import type { LLMProvider } from '../shared/types';

// LLM 웹사이트 URL
const LLM_URLS: Record<LLMProvider, string> = {
  chatgpt: 'https://chat.openai.com',
  claude: 'https://claude.ai',
  gemini: 'https://gemini.google.com',
};

export class PlaywrightPageManager {
  private pages: Map<LLMProvider, Page> = new Map();
  private browser: Browser;

  constructor(browser: Browser) {
    this.browser = browser;
  }

  /**
   * Page 생성 (BrowserView.create() 대응)
   * @param provider - LLM provider
   * @param context - BrowserContext (세션 포함)
   * @returns 생성된 Page
   */
  async createPage(provider: LLMProvider, context: BrowserContext): Promise<Page> {
    // 이미 존재하면 재사용
    if (this.pages.has(provider)) {
      const existingPage = this.pages.get(provider)!;
      if (!existingPage.isClosed()) {
        return existingPage;
      }
      // 닫힌 Page는 제거
      this.pages.delete(provider);
    }

    // 새 Page 생성
    const page = await context.newPage();

    // Page 이벤트 핸들러
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.error(`[${provider}:console] ${msg.text()}`);
      }
    });

    page.on('pageerror', (error) => {
      console.error(`[${provider}:pageerror] ${error.message}`);
    });

    // LLM 사이트 로드
    const url = LLM_URLS[provider];
    console.log(`[PageManager] Loading ${url}...`);

    try {
      await page.goto(url, {
        waitUntil: 'domcontentloaded',  // networkidle은 너무 느림
        timeout: 30000,
      });
      console.log(`[PageManager] Page loaded for ${provider}`);
    } catch (error) {
      console.error(`[PageManager] Failed to load ${url}:`, error);
      throw error;
    }

    this.pages.set(provider, page);
    return page;
  }

  /**
   * Page 가져오기 (BrowserViewManager.getView() 대응)
   */
  getPage(provider: LLMProvider): Page | undefined {
    const page = this.pages.get(provider);
    if (page && !page.isClosed()) {
      return page;
    }
    return undefined;
  }

  /**
   * Page 닫기 (BrowserView.destroy() 대응)
   */
  async closePage(provider: LLMProvider): Promise<void> {
    const page = this.pages.get(provider);
    if (page && !page.isClosed()) {
      await page.close();
      console.log(`[PageManager] Closed page for ${provider}`);
    }
    this.pages.delete(provider);
  }

  /**
   * 모든 Page 닫기
   */
  async closeAllPages(): Promise<void> {
    const providers = Array.from(this.pages.keys());
    for (const provider of providers) {
      await this.closePage(provider);
    }
    console.log(`[PageManager] Closed all pages`);
  }

  /**
   * Page 새로고침
   */
  async reloadPage(provider: LLMProvider): Promise<void> {
    const page = this.pages.get(provider);
    if (page && !page.isClosed()) {
      await page.reload({ waitUntil: 'domcontentloaded' });
      console.log(`[PageManager] Reloaded page for ${provider}`);
    }
  }

  /**
   * 스크린샷 캡처 (디버깅용)
   */
  async captureScreenshot(provider: LLMProvider, outputPath: string): Promise<void> {
    const page = this.pages.get(provider);
    if (page && !page.isClosed()) {
      await page.screenshot({
        path: outputPath,
        fullPage: true,
      });
      console.log(`[PageManager] Screenshot saved: ${outputPath}`);
    }
  }

  /**
   * 현재 URL 가져오기
   */
  getUrl(provider: LLMProvider): string | undefined {
    const page = this.pages.get(provider);
    if (page && !page.isClosed()) {
      return page.url();
    }
    return undefined;
  }

  /**
   * 활성 Page 목록
   */
  getActiveProviders(): LLMProvider[] {
    const active: LLMProvider[] = [];
    for (const [provider, page] of this.pages) {
      if (!page.isClosed()) {
        active.push(provider);
      }
    }
    return active;
  }
}
