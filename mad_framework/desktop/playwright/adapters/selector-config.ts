/**
 * Playwright Selector Config
 *
 * 기존 Electron 셀렉터 설정 재export
 * 중복 방지 및 단일 소스 유지
 */

export {
  getBaseUrl,
  getDefaultSelectors,
  getSelectorSets,
  PROVIDER_URLS,
  CHATGPT_SELECTORS,
  CLAUDE_SELECTORS,
  GEMINI_SELECTORS,
} from '../../electron/browser/adapters/selector-config';
