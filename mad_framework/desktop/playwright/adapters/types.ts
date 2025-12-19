/**
 * Playwright Adapter Type Definitions
 *
 * Electron WebContents → Playwright Page 전환
 * 기존 SelectorSet, ProviderSelectors 타입 유지
 */

import type { Page } from 'playwright';
import type { LLMProvider } from '../../shared/types';

// Playwright Page 인터페이스 (WebContents 대체)
export type { Page };

// Issue #18: SelectorSet for fallback support
export interface SelectorSet {
  primary: string;
  fallbacks: string[];
}

export interface ProviderSelectors {
  inputTextarea: SelectorSet;
  sendButton: SelectorSet;
  responseContainer: SelectorSet;
  typingIndicator: SelectorSet;
  loginCheck: SelectorSet;
}

// Legacy interface for backward compatibility
export interface AdapterSelectors {
  inputTextarea: string;
  sendButton: string;
  responseContainer: string;
  typingIndicator: string;
  loginCheck: string;
}

export type { LLMProvider };
