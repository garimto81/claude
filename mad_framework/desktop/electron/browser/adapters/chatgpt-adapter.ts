/**
 * ChatGPT Adapter
 *
 * chat.openai.com 사이트 자동화
 */

import { BaseLLMAdapter } from './base-adapter';

interface WebContents {
  executeJavaScript: (script: string) => Promise<any>;
  loadURL: (url: string) => void;
  getURL: () => string;
  on: (event: string, callback: (...args: any[]) => void) => void;
}

export class ChatGPTAdapter extends BaseLLMAdapter {
  readonly provider = 'chatgpt' as const;
  readonly baseUrl = 'https://chat.openai.com';

  readonly selectors = {
    inputTextarea: '#prompt-textarea',
    sendButton: '[data-testid="send-button"]',
    responseContainer: '[data-message-author-role="assistant"]',
    typingIndicator: '.result-streaming',
    loginCheck: '[data-testid="profile-button"]',
  };

  constructor(webContents: WebContents) {
    super('chatgpt', webContents);
  }

  async isLoggedIn(): Promise<boolean> {
    const script = `
      !!(
        document.querySelector('[data-testid="profile-button"]') ||
        document.querySelector('button[aria-label*="Account"]') ||
        document.querySelector('img[alt*="User"]') ||
        document.querySelector('#prompt-textarea')
      )
    `;
    return this.executeScript<boolean>(script, false);
  }

  // ChatGPT uses ProseMirror editor - needs special input handling
  async inputPrompt(prompt: string): Promise<void> {
    const escapedPrompt = JSON.stringify(prompt);
    console.log(`[chatgpt] inputPrompt called, length: ${prompt.length}`);

    const script = `
      (() => {
        try {
          const textarea = document.querySelector('#prompt-textarea');
          if (!textarea) {
            return { success: false, error: 'textarea not found' };
          }

          // Focus and clear
          textarea.focus();

          // Method 1: For contenteditable (ProseMirror)
          if (textarea.contentEditable === 'true' || textarea.getAttribute('contenteditable')) {
            // Clear existing content
            textarea.innerHTML = '';

            // Create paragraph with text
            const p = document.createElement('p');
            p.textContent = ${escapedPrompt};
            textarea.appendChild(p);

            // Trigger input event
            textarea.dispatchEvent(new InputEvent('input', {
              bubbles: true,
              cancelable: true,
              inputType: 'insertText',
              data: ${escapedPrompt}
            }));

            return { success: true, method: 'contenteditable' };
          }

          // Method 2: For regular textarea
          if (textarea.tagName === 'TEXTAREA') {
            textarea.value = ${escapedPrompt};
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            return { success: true, method: 'textarea' };
          }

          return { success: false, error: 'unknown input type' };
        } catch (e) {
          return { success: false, error: e.message };
        }
      })()
    `;

    const result = await this.executeScript<{success: boolean; error?: string; method?: string}>(script, { success: false, error: 'script failed' });
    console.log(`[chatgpt] inputPrompt result:`, result);

    // Wait a bit for React to process
    await this.sleep(500);
  }

  async sendMessage(): Promise<void> {
    console.log(`[chatgpt] sendMessage called`);

    const script = `
      (() => {
        try {
          // Try multiple send button selectors (ChatGPT UI changes frequently)
          const selectors = [
            '[data-testid="send-button"]',
            'button[data-testid="send-button"]',
            'button[aria-label="Send prompt"]',
            'button[aria-label*="Send"]',
            'form button:not([disabled])',
            'button svg[viewBox*="24"]'  // SVG send icon
          ];

          for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
              const button = el.tagName === 'BUTTON' ? el : el.closest('button');
              if (button && !button.disabled) {
                button.click();
                return { success: true, selector: sel };
              }
            }
          }

          // Fallback: Submit via Enter key
          const textarea = document.querySelector('#prompt-textarea');
          if (textarea) {
            const enterEvent = new KeyboardEvent('keydown', {
              key: 'Enter',
              code: 'Enter',
              keyCode: 13,
              which: 13,
              bubbles: true,
              cancelable: true
            });
            textarea.dispatchEvent(enterEvent);
            return { success: true, method: 'enter-key' };
          }

          return { success: false, error: 'no send method found' };
        } catch (e) {
          return { success: false, error: e.message };
        }
      })()
    `;

    const result = await this.executeScript<{success: boolean; error?: string; selector?: string}>(script, { success: false });
    console.log(`[chatgpt] sendMessage result:`, result);

    // Wait for message to be sent
    await this.sleep(1000);
  }

  async isWriting(): Promise<boolean> {
    const script = `
      !!(
        document.querySelector('.result-streaming') ||
        document.querySelector('[data-message-author-role="assistant"] .markdown.prose.dark:empty') ||
        document.querySelector('.agent-turn')
      )
    `;
    return this.executeScript<boolean>(script, false);
  }

  async extractResponse(): Promise<string> {
    console.log(`[chatgpt] extractResponse called`);

    // Wait for DOM to be fully rendered after response
    await this.sleep(1000);

    const script = `
      (() => {
        try {
          // Try multiple selectors for ChatGPT responses (ordered by specificity)
          const selectors = [
            '[data-message-author-role="assistant"] .markdown',
            '[data-message-author-role="assistant"]',
            'div[data-message-author-role="assistant"] > div > div',
            '.agent-turn .markdown',
            '.prose',
            'article[data-testid*="conversation"] div.markdown'
          ];

          for (const sel of selectors) {
            const messages = document.querySelectorAll(sel);
            if (messages.length > 0) {
              const lastMessage = messages[messages.length - 1];
              const content = lastMessage?.innerText || lastMessage?.textContent || '';
              if (content.trim()) {
                return { success: true, content: content.trim(), selector: sel, count: messages.length };
              }
            }
          }

          return {
            success: false,
            content: '',
            error: 'no messages found'
          };
        } catch (e) {
          return { success: false, content: '', error: e.message };
        }
      })()
    `;

    const result = await this.executeScript<{success: boolean; content: string; error?: string; selector?: string}>(
      script,
      { success: false, content: '', error: 'script failed' }
    );

    console.log(`[chatgpt] extractResponse result:`, JSON.stringify(result).substring(0, 300));
    return result.content;
  }
}
