/**
 * Playwright Browser Manager
 *
 * BrowserViewManager 완전 대응
 * debate-controller.ts와 호환되도록 동일 인터페이스 제공
 */

import { chromium, Browser } from 'playwright';
import type { LLMProvider, LLMLoginStatus } from '../shared/types';
import { PlaywrightContextManager } from './context-manager';
import { PlaywrightPageManager } from './page-manager';
import { PlaywrightChatGPTAdapter } from './adapters/chatgpt-adapter';
import { PlaywrightBaseLLMAdapter } from './adapters/base-adapter';

export class PlaywrightBrowserManager {
  private browser: Browser | null = null;
  private contextManager!: PlaywrightContextManager;
  private pageManager!: PlaywrightPageManager;
  private adapters: Map<LLMProvider, PlaywrightBaseLLMAdapter> = new Map();

  /**
   * 초기화 (Electron app.whenReady() 대응)
   * @param headless - headless 모드 (기본: true)
   */
  async initialize(headless: boolean = true): Promise<void> {
    console.log('[Playwright] Launching browser...');

    this.browser = await chromium.launch({
      headless,
      args: [
        '--disable-blink-features=AutomationControlled',  // 봇 탐지 회피
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
      ],
    });

    this.contextManager = new PlaywrightContextManager(this.browser);
    this.pageManager = new PlaywrightPageManager(this.browser);

    console.log(`[Playwright] Browser ready (headless: ${headless})`);
  }

  /**
   * Provider별 Adapter 생성 (BrowserViewManager.createView() 대응)
   */
  async createAdapter(provider: LLMProvider): Promise<PlaywrightBaseLLMAdapter> {
    if (!this.browser) {
      throw new Error('Browser not initialized. Call initialize() first.');
    }

    // 이미 존재하면 재사용
    if (this.adapters.has(provider)) {
      return this.adapters.get(provider)!;
    }

    // Context + Page 생성
    const context = await this.contextManager.getContext(provider);
    const page = await this.pageManager.createPage(provider, context);

    // Adapter 생성
    let adapter: PlaywrightBaseLLMAdapter;
    switch (provider) {
      case 'chatgpt':
        adapter = new PlaywrightChatGPTAdapter(page);
        break;
      // TODO: Claude, Gemini 추가 시
      // case 'claude':
      //   adapter = new PlaywrightClaudeAdapter(page);
      //   break;
      // case 'gemini':
      //   adapter = new PlaywrightGeminiAdapter(page);
      //   break;
      default:
        // 기본 어댑터 사용 (fallback)
        adapter = new PlaywrightBaseLLMAdapter(provider, page);
    }

    this.adapters.set(provider, adapter);
    console.log(`[Playwright] Created adapter for ${provider}`);

    return adapter;
  }

  /**
   * Adapter 가져오기 (BrowserViewManager.getAdapter() 대응)
   * @throws Error if adapter not found
   */
  getAdapter(provider: LLMProvider): PlaywrightBaseLLMAdapter {
    const adapter = this.adapters.get(provider);
    if (!adapter) {
      throw new Error(`Adapter not found for ${provider}. Call createAdapter() first.`);
    }
    return adapter;
  }

  /**
   * 로그인 상태 확인 (BrowserViewManager.checkLoginStatus() 대응)
   */
  async checkLoginStatus(): Promise<Record<LLMProvider, LLMLoginStatus>> {
    const result: Record<LLMProvider, LLMLoginStatus> = {
      chatgpt: {
        provider: 'chatgpt',
        isLoggedIn: false,
        lastChecked: new Date().toISOString(),
      },
      claude: {
        provider: 'claude',
        isLoggedIn: false,
        lastChecked: new Date().toISOString(),
      },
      gemini: {
        provider: 'gemini',
        isLoggedIn: false,
        lastChecked: new Date().toISOString(),
      },
    };

    for (const [provider, adapter] of this.adapters) {
      try {
        const loginResult = await adapter.checkLogin();
        result[provider] = {
          provider,
          isLoggedIn: loginResult.success && loginResult.data === true,
          lastChecked: new Date().toISOString(),
        };
      } catch (error) {
        console.error(`[Playwright] Login check failed for ${provider}:`, error);
        result[provider].isLoggedIn = false;
      }
    }

    return result;
  }

  /**
   * 세션 저장 (로그인 유지)
   */
  async saveSessions(): Promise<void> {
    await this.contextManager.saveAllContexts();
  }

  /**
   * 특정 provider 세션 저장
   */
  async saveSession(provider: LLMProvider): Promise<void> {
    await this.contextManager.saveContext(provider);
  }

  /**
   * 스크린샷 캡처 (디버깅용)
   */
  async captureScreenshot(provider: LLMProvider, outputPath: string): Promise<void> {
    await this.pageManager.captureScreenshot(provider, outputPath);
  }

  /**
   * storageState 존재 여부 확인
   */
  getStorageStatus(): Record<LLMProvider, boolean> {
    return this.contextManager.getStorageStatus();
  }

  /**
   * 브라우저 상태 확인
   */
  isInitialized(): boolean {
    return this.browser !== null;
  }

  /**
   * 활성 adapter 목록
   */
  getActiveProviders(): LLMProvider[] {
    return Array.from(this.adapters.keys());
  }

  /**
   * 종료 (Electron app.quit() 대응)
   */
  async close(): Promise<void> {
    console.log('[Playwright] Closing browser...');

    // 세션 저장
    try {
      await this.saveSessions();
    } catch (error) {
      console.error('[Playwright] Failed to save sessions:', error);
    }

    // 리소스 정리
    await this.pageManager.closeAllPages();
    await this.contextManager.closeAllContexts(false);

    // Adapter 맵 초기화
    this.adapters.clear();

    // 브라우저 종료
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }

    console.log('[Playwright] Browser closed');
  }
}

// 편의를 위한 singleton instance
let defaultManager: PlaywrightBrowserManager | null = null;

/**
 * 기본 PlaywrightBrowserManager 인스턴스 가져오기
 */
export function getPlaywrightManager(): PlaywrightBrowserManager {
  if (!defaultManager) {
    defaultManager = new PlaywrightBrowserManager();
  }
  return defaultManager;
}

/**
 * 기본 인스턴스 초기화
 */
export async function initializePlaywright(headless: boolean = true): Promise<PlaywrightBrowserManager> {
  const manager = getPlaywrightManager();
  if (!manager.isInitialized()) {
    await manager.initialize(headless);
  }
  return manager;
}

/**
 * 기본 인스턴스 종료
 */
export async function closePlaywright(): Promise<void> {
  if (defaultManager) {
    await defaultManager.close();
    defaultManager = null;
  }
}
