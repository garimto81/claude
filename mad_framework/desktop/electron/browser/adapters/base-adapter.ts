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
    const isReady = await this.waitForCondition(
      async () => {
        return this.executeScript<boolean>(
          `!!document.querySelector('${this.selectors.inputTextarea}')`,
          false
        );
      },
      { timeout, interval: 500, description: 'input to be ready' }
    );

    if (!isReady) {
      throw new Error(`Input not ready for ${this.provider}`);
    }
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
    const success = await this.executeScript<boolean>(script, false);
    if (!success) {
      throw new Error(`Failed to send message for ${this.provider}: send button not found or click failed`);
    }
  }

  async waitForResponse(timeout: number = 120000): Promise<void> {
    console.log(`[${this.provider}] waitForResponse started, timeout: ${timeout}ms`);

    // Step 1: Wait for typing to start (max 10 seconds)
    const typingStarted = await this.waitForCondition(
      () => this.isWriting(),
      { timeout: 10000, interval: 300, description: 'typing to start' }
    );

    if (!typingStarted) {
      console.warn(`[${this.provider}] Typing never started, checking for response anyway`);
    }

    // Step 2: Wait for typing to finish (remaining timeout)
    const remainingTimeout = Math.max(timeout - 10000, 5000);
    const typingFinished = await this.waitForCondition(
      async () => !(await this.isWriting()),
      { timeout: remainingTimeout, interval: 500, description: 'typing to finish' }
    );

    if (!typingFinished) {
      throw new Error(`Response timeout for ${this.provider}`);
    }

    // Step 3: DOM stabilization delay
    await this.sleep(1000);
    console.log(`[${this.provider}] Response complete`);
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

  /**
   * Wait for a condition to be true with configurable timeout and interval
   * @param checkFn - Function that returns true when condition is met
   * @param options - Configuration options
   * @returns true if condition met, false if timeout
   */
  protected async waitForCondition(
    checkFn: () => Promise<boolean>,
    options: {
      timeout: number;
      interval: number;
      description: string;
    }
  ): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < options.timeout) {
      try {
        if (await checkFn()) {
          console.log(`[${this.provider}] Condition met: ${options.description}`);
          return true;
        }
      } catch (error) {
        console.warn(`[${this.provider}] Check failed for ${options.description}:`, error);
      }
      await this.sleep(options.interval);
    }

    console.warn(`[${this.provider}] Timeout waiting for: ${options.description}`);
    return false;
  }
}
