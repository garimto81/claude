/**
 * Claude Adapter
 *
 * claude.ai 사이트 자동화
 */

import { BaseLLMAdapter } from './base-adapter';

interface WebContents {
  executeJavaScript: (script: string) => Promise<any>;
  loadURL: (url: string) => void;
  getURL: () => string;
  on: (event: string, callback: (...args: any[]) => void) => void;
}

export class ClaudeAdapter extends BaseLLMAdapter {
  readonly provider = 'claude' as const;
  readonly baseUrl = 'https://claude.ai';

  readonly selectors = {
    inputTextarea: '[contenteditable="true"]',
    sendButton: '[aria-label="Send message"]',
    responseContainer: '[data-is-streaming="false"]',
    typingIndicator: '[data-is-streaming="true"]',
    loginCheck: '[data-testid="user-menu"]',
  };

  constructor(webContents: WebContents) {
    super('claude', webContents);
  }

  async isLoggedIn(): Promise<boolean> {
    // Check multiple possible login indicators
    const script = `
      !!(
        document.querySelector('[data-testid="user-menu"]') ||
        document.querySelector('button[aria-label*="account"]') ||
        document.querySelector('button[aria-label*="Account"]') ||
        document.querySelector('[data-testid="menu-trigger"]') ||
        document.querySelector('[contenteditable="true"]') ||
        document.querySelector('fieldset[dir="auto"]')
      )
    `;
    return this.executeScript<boolean>(script, false);
  }

  async inputPrompt(prompt: string): Promise<void> {
    const escapedPrompt = JSON.stringify(prompt);
    // Claude uses contenteditable div
    const script = `
      (() => {
        const editor = document.querySelector('${this.selectors.inputTextarea}');
        if (!editor) return false;
        editor.innerHTML = '';
        editor.innerText = ${escapedPrompt};
        editor.dispatchEvent(new InputEvent('input', { bubbles: true }));
        return true;
      })()
    `;
    await this.executeScript<boolean>(script, false);
  }

  async isWriting(): Promise<boolean> {
    const script = `!!document.querySelector('${this.selectors.typingIndicator}')`;
    return this.executeScript<boolean>(script, false);
  }

  // extractResponse, getTokenCount use base class methods with proper error handling
}
