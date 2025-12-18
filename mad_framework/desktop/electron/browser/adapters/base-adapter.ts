/**
 * Base LLM Adapter
 *
 * 브라우저 자동화를 위한 기본 어댑터 클래스
 */

import type { LLMProvider } from '../../../shared/types';

interface WebContents {
  executeJavaScript: (script: string) => Promise<any>;
  loadURL: (url: string) => void;
  getURL: () => string;
  on: (event: string, callback: (...args: any[]) => void) => void;
}

interface AdapterSelectors {
  inputTextarea: string;
  sendButton: string;
  responseContainer: string;
  typingIndicator: string;
  loginCheck: string;
}

export class BaseLLMAdapter {
  readonly provider: LLMProvider;
  readonly baseUrl: string;
  readonly selectors: AdapterSelectors;
  protected webContents: WebContents;

  constructor(provider: LLMProvider, webContents: WebContents) {
    this.provider = provider;
    this.webContents = webContents;

    // Default selectors - should be overridden by subclasses
    this.baseUrl = this.getBaseUrl(provider);
    this.selectors = this.getDefaultSelectors(provider);
  }

  // Safe wrapper for executeJavaScript with error handling
  protected async executeScript<T>(script: string, defaultValue?: T): Promise<T> {
    try {
      const result = await this.webContents.executeJavaScript(script);
      return result as T;
    } catch (error) {
      console.error(`[${this.provider}] Script execution failed:`, error);
      if (defaultValue !== undefined) {
        return defaultValue;
      }
      throw new Error(`Script execution failed for ${this.provider}: ${error}`);
    }
  }

  private getBaseUrl(provider: LLMProvider): string {
    const urls: Record<LLMProvider, string> = {
      chatgpt: 'https://chat.openai.com',
      claude: 'https://claude.ai',
      gemini: 'https://gemini.google.com',
    };
    return urls[provider];
  }

  private getDefaultSelectors(provider: LLMProvider): AdapterSelectors {
    const selectorMap: Record<LLMProvider, AdapterSelectors> = {
      chatgpt: {
        inputTextarea: '#prompt-textarea',
        sendButton: '[data-testid="send-button"]',
        responseContainer: '[data-message-author-role="assistant"]',
        typingIndicator: '.result-streaming',
        loginCheck: '[data-testid="profile-button"]',
      },
      claude: {
        inputTextarea: '[contenteditable="true"]',
        sendButton: '[aria-label="Send message"]',
        responseContainer: '[data-is-streaming="false"]',
        typingIndicator: '[data-is-streaming="true"]',
        loginCheck: '[data-testid="user-menu"]',
      },
      gemini: {
        inputTextarea: '.ql-editor',
        sendButton: '.send-button',
        responseContainer: '.response-container',
        typingIndicator: '.loading-indicator',
        loginCheck: '[data-user-email]',
      },
    };
    return selectorMap[provider];
  }

  async isLoggedIn(): Promise<boolean> {
    const script = `!!document.querySelector('${this.selectors.loginCheck}')`;
    return this.executeScript<boolean>(script, false);
  }

  async waitForInputReady(timeout: number = 10000): Promise<void> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const isReady = await this.executeScript<boolean>(
        `!!document.querySelector('${this.selectors.inputTextarea}')`,
        false
      );
      if (isReady) return;
      await this.sleep(500);
    }

    throw new Error(`Input not ready for ${this.provider}`);
  }

  async inputPrompt(prompt: string): Promise<void> {
    const escapedPrompt = JSON.stringify(prompt);
    const script = `
      (() => {
        const textarea = document.querySelector('${this.selectors.inputTextarea}');
        if (!textarea) return false;
        if (textarea.tagName === 'TEXTAREA' || textarea.tagName === 'INPUT') {
          textarea.value = ${escapedPrompt};
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
          textarea.innerText = ${escapedPrompt};
          textarea.dispatchEvent(new InputEvent('input', { bubbles: true }));
        }
        return true;
      })()
    `;
    const success = await this.executeScript<boolean>(script, false);
    if (!success) {
      throw new Error(`Failed to input prompt for ${this.provider}`);
    }
  }

  async sendMessage(): Promise<void> {
    const script = `
      (() => {
        const button = document.querySelector('${this.selectors.sendButton}');
        if (button) {
          button.click();
          return true;
        }
        return false;
      })()
    `;
    await this.executeScript<boolean>(script, false);
  }

  async waitForResponse(timeout: number = 120000): Promise<void> {
    console.log(`[${this.provider}] waitForResponse started, timeout: ${timeout}ms`);
    const startTime = Date.now();

    // Initial delay to let typing start
    console.log(`[${this.provider}] Waiting 2s for typing to start...`);
    await this.sleep(2000);

    while (Date.now() - startTime < timeout) {
      try {
        const isWriting = await this.executeScript<boolean>(
          `!!document.querySelector('${this.selectors.typingIndicator}')`,
          false
        );
        console.log(`[${this.provider}] isWriting: ${isWriting}`);
        if (!isWriting) {
          console.log(`[${this.provider}] Response complete`);
          return;
        }
        await this.sleep(500);
      } catch (error) {
        console.error(`[${this.provider}] Error checking writing status:`, error);
        // Continue checking instead of failing
        await this.sleep(500);
      }
    }

    throw new Error(`Response timeout for ${this.provider}`);
  }

  async extractResponse(): Promise<string> {
    const script = `
      (() => {
        const messages = document.querySelectorAll('${this.selectors.responseContainer}');
        const lastMessage = messages[messages.length - 1];
        return lastMessage?.innerText || '';
      })()
    `;
    return this.executeScript<string>(script, '');
  }

  async isWriting(): Promise<boolean> {
    const script = `!!document.querySelector('${this.selectors.typingIndicator}')`;
    return this.executeScript<boolean>(script, false);
  }

  async getTokenCount(): Promise<number> {
    const script = `
      (() => {
        const messages = document.querySelectorAll('${this.selectors.responseContainer}');
        const lastMessage = messages[messages.length - 1];
        return (lastMessage?.innerText || '').length;
      })()
    `;
    return this.executeScript<number>(script, 0);
  }

  async clearInput(): Promise<void> {
    const script = `
      (() => {
        const textarea = document.querySelector('${this.selectors.inputTextarea}');
        if (!textarea) return;
        if (textarea.tagName === 'TEXTAREA' || textarea.tagName === 'INPUT') {
          textarea.value = '';
        } else {
          textarea.innerHTML = '';
        }
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
      })()
    `;
    await this.executeScript<void>(script);
  }

  async scrollToBottom(): Promise<void> {
    const script = `window.scrollTo(0, document.body.scrollHeight)`;
    await this.executeScript<void>(script);
  }

  protected sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
