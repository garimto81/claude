/**
 * Playwright Module Index
 *
 * Playwright 기반 브라우저 자동화 모듈
 */

// Manager
export { PlaywrightBrowserManager } from './playwright-browser-manager';
export {
  getPlaywrightManager,
  initializePlaywright,
  closePlaywright,
} from './playwright-browser-manager';

// Context & Page
export { PlaywrightContextManager } from './context-manager';
export { PlaywrightPageManager } from './page-manager';

// Adapters
export { PlaywrightBaseLLMAdapter } from './adapters/base-adapter';
export { PlaywrightChatGPTAdapter } from './adapters/chatgpt-adapter';

// Types
export type { Page, SelectorSet, ProviderSelectors, AdapterSelectors } from './adapters/types';
