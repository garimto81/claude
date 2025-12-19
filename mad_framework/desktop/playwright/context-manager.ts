/**
 * Playwright Context Manager
 *
 * Electron session.fromPartition() → BrowserContext + storageState 전환
 * 각 LLM별 독립된 세션 관리 (쿠키, localStorage 등)
 */

import type { Browser, BrowserContext } from 'playwright';
import type { LLMProvider } from '../shared/types';
import * as fs from 'fs';
import * as path from 'path';

// 세션 데이터 저장 경로
const STORAGE_DIR = '.playwright-storage';

const STORAGE_PATHS: Record<LLMProvider, string> = {
  chatgpt: path.join(STORAGE_DIR, 'chatgpt-storage.json'),
  claude: path.join(STORAGE_DIR, 'claude-storage.json'),
  gemini: path.join(STORAGE_DIR, 'gemini-storage.json'),
};

// 기본 User-Agent (봇 탐지 회피)
const DEFAULT_USER_AGENT =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

export class PlaywrightContextManager {
  private contexts: Map<LLMProvider, BrowserContext> = new Map();
  private browser: Browser;

  constructor(browser: Browser) {
    this.browser = browser;
    this.ensureStorageDir();
  }

  /**
   * storageState 디렉토리 생성
   */
  private ensureStorageDir(): void {
    if (!fs.existsSync(STORAGE_DIR)) {
      fs.mkdirSync(STORAGE_DIR, { recursive: true });
      console.log(`[ContextManager] Created storage directory: ${STORAGE_DIR}`);
    }
  }

  /**
   * storageState 파일 로드
   * @param storagePath - storageState JSON 파일 경로
   * @returns storageState 또는 undefined
   */
  private loadStorageState(storagePath: string): string | undefined {
    if (fs.existsSync(storagePath)) {
      console.log(`[ContextManager] Loading storage from: ${storagePath}`);
      return storagePath;
    }
    console.log(`[ContextManager] No existing storage at: ${storagePath}`);
    return undefined;
  }

  /**
   * BrowserContext 생성 또는 가져오기
   * Electron의 session.fromPartition('persist:chatgpt') 대응
   */
  async getContext(provider: LLMProvider): Promise<BrowserContext> {
    // 이미 존재하면 재사용
    if (this.contexts.has(provider)) {
      return this.contexts.get(provider)!;
    }

    const storagePath = STORAGE_PATHS[provider];
    const storageState = this.loadStorageState(storagePath);

    // 새 Context 생성
    const context = await this.browser.newContext({
      storageState,  // 쿠키 + localStorage 자동 복원
      viewport: { width: 1280, height: 720 },
      userAgent: DEFAULT_USER_AGENT,
      locale: 'ko-KR',
      timezoneId: 'Asia/Seoul',
      // 봇 탐지 회피
      javaScriptEnabled: true,
      bypassCSP: false,
      ignoreHTTPSErrors: false,
    });

    this.contexts.set(provider, context);
    console.log(`[ContextManager] Created context for ${provider}`);

    return context;
  }

  /**
   * storageState 저장 (로그인 세션 유지)
   * 호출 시점: 로그인 완료 후, 프로그램 종료 전
   */
  async saveContext(provider: LLMProvider): Promise<void> {
    const context = this.contexts.get(provider);
    if (!context) {
      console.warn(`[ContextManager] No context found for ${provider}`);
      return;
    }

    const storagePath = STORAGE_PATHS[provider];
    await context.storageState({ path: storagePath });
    console.log(`[ContextManager] Saved storage for ${provider} → ${storagePath}`);
  }

  /**
   * 모든 Context의 storageState 저장
   */
  async saveAllContexts(): Promise<void> {
    const providers = Array.from(this.contexts.keys());
    for (const provider of providers) {
      await this.saveContext(provider);
    }
    console.log(`[ContextManager] Saved all contexts (${providers.length})`);
  }

  /**
   * Context 닫기 (세션 정리)
   * @param save - 닫기 전에 storageState 저장 여부
   */
  async closeContext(provider: LLMProvider, save: boolean = true): Promise<void> {
    const context = this.contexts.get(provider);
    if (!context) {
      return;
    }

    if (save) {
      await this.saveContext(provider);
    }

    await context.close();
    this.contexts.delete(provider);
    console.log(`[ContextManager] Closed context for ${provider}`);
  }

  /**
   * 모든 Context 닫기
   */
  async closeAllContexts(save: boolean = true): Promise<void> {
    const providers = Array.from(this.contexts.keys());
    for (const provider of providers) {
      await this.closeContext(provider, save);
    }
    console.log(`[ContextManager] Closed all contexts`);
  }

  /**
   * 세션 삭제 (로그아웃 대응)
   * storageState 파일 삭제
   */
  async clearStorage(provider: LLMProvider): Promise<void> {
    const storagePath = STORAGE_PATHS[provider];

    // Context 닫기 (저장 없이)
    await this.closeContext(provider, false);

    // 파일 삭제
    if (fs.existsSync(storagePath)) {
      fs.unlinkSync(storagePath);
      console.log(`[ContextManager] Cleared storage for ${provider}`);
    }
  }

  /**
   * 모든 세션 삭제
   */
  async clearAllStorage(): Promise<void> {
    const providers: LLMProvider[] = ['chatgpt', 'claude', 'gemini'];
    for (const provider of providers) {
      await this.clearStorage(provider);
    }
    console.log(`[ContextManager] Cleared all storage`);
  }

  /**
   * storageState 존재 여부 확인 (로그인 상태 추정)
   */
  hasStorageState(provider: LLMProvider): boolean {
    const storagePath = STORAGE_PATHS[provider];
    return fs.existsSync(storagePath);
  }

  /**
   * 모든 provider의 storageState 상태 조회
   */
  getStorageStatus(): Record<LLMProvider, boolean> {
    return {
      chatgpt: this.hasStorageState('chatgpt'),
      claude: this.hasStorageState('claude'),
      gemini: this.hasStorageState('gemini'),
    };
  }
}
