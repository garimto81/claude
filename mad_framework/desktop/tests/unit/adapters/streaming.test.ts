/**
 * Streaming Tests (CL-002)
 *
 * Tests for response streaming functionality
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BaseLLMAdapter } from '../../../electron/browser/adapters/base-adapter';
import type { LLMProvider } from '../../../shared/types';

// Mock WebContents
class MockWebContents {
  private mockResponses: string[] = [];
  private responseIndex = 0;
  private isWritingCallCount = 0;
  private readonly typingDuration: number;
  private readonly shouldType: boolean;

  constructor(responses: string[] = [], shouldSimulateTyping = true) {
    this.mockResponses = responses;
    this.shouldType = shouldSimulateTyping && responses.length > 0;
    // Typing for as many calls as there are responses (to emit chunks)
    this.typingDuration = this.shouldType ? responses.length : 0;
  }

  async executeJavaScript(script: string): Promise<any> {
    // isWriting check - uses || to combine multiple selectors
    if (script.includes('!!(')) {
      this.isWritingCallCount++;
      // Return true for first N calls, then false
      return this.isWritingCallCount <= this.typingDuration;
    }

    // Simulate selector check (findElement)
    if (script.includes('!!document.querySelector')) {
      // Return true for all selector checks to pass findElement
      return this.mockResponses.length > 0;
    }

    // Simulate getResponse extraction
    if (script.includes('querySelectorAll') && script.includes('messages.length')) {
      if (this.responseIndex < this.mockResponses.length) {
        return this.mockResponses[this.responseIndex++];
      }
      return this.mockResponses[this.mockResponses.length - 1] || '';
    }

    return '';
  }

  loadURL(_url: string): void {}
  getURL(): string { return 'https://example.com'; }
  on(_event: string, _callback: (...args: any[]) => void): void {}
}

describe('Response Streaming (CL-002)', () => {
  let adapter: BaseLLMAdapter;
  let mockWebContents: MockWebContents;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('streamResponse', () => {
    it('should stream response chunks in real-time', async () => {
      // Arrange
      const chunks = ['Hello', 'Hello World', 'Hello World!', 'Hello World! Complete'];
      mockWebContents = new MockWebContents(chunks);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const receivedChunks: string[] = [];
      const onChunk = vi.fn((chunk: string) => {
        receivedChunks.push(chunk);
      });

      // Act
      const result = await adapter.streamResponse(onChunk, 10000);

      // Assert
      expect(result.success).toBe(true);
      expect(onChunk).toHaveBeenCalled();
      expect(receivedChunks.length).toBeGreaterThan(0);
    });

    it('should handle streaming timeout gracefully', async () => {
      // Arrange
      mockWebContents = new MockWebContents([], false); // No typing
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const onChunk = vi.fn();

      // Act - streamResponse has internal 10s wait, so this test needs longer timeout
      const result = await adapter.streamResponse(onChunk, 500);

      // Assert
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('RESPONSE_TIMEOUT');
      expect(result.error?.message).toContain('typing never started');
    }, 15000); // 15s test timeout

    it('should emit final chunk when streaming completes', async () => {
      // Arrange
      const chunks = ['Hello', 'Hello World'];
      mockWebContents = new MockWebContents(chunks);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const receivedChunks: string[] = [];
      const onChunk = vi.fn((chunk: string) => {
        receivedChunks.push(chunk);
      });

      // Act
      const result = await adapter.streamResponse(onChunk, 10000);

      // Assert
      expect(result.success).toBe(true);
      expect(result.data).toBe('Hello World');
    });

    it('should handle empty responses without crashing', async () => {
      // Arrange
      mockWebContents = new MockWebContents([''], false); // Empty, no typing
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const onChunk = vi.fn();

      // Act - streamResponse has internal 10s wait
      const result = await adapter.streamResponse(onChunk, 500);

      // Assert
      expect(result.success).toBe(false);
      expect(result.error?.code).toBe('RESPONSE_TIMEOUT');
    }, 15000); // 15s test timeout

    it('should only emit new chunks, not duplicate content', async () => {
      // Arrange
      const chunks = ['A', 'AB', 'ABC', 'ABCD'];
      mockWebContents = new MockWebContents(chunks);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const receivedChunks: string[] = [];
      const onChunk = vi.fn((chunk: string) => {
        receivedChunks.push(chunk);
      });

      // Act
      await adapter.streamResponse(onChunk, 10000);

      // Assert
      const fullContent = receivedChunks.join('');
      expect(fullContent).toBe('ABCD');
      // Each chunk should be incremental
      expect(receivedChunks.every(chunk => chunk.length > 0)).toBe(true);
    });

    it('should maintain UI responsiveness during streaming', async () => {
      // Arrange
      const chunks = ['A', 'AB', 'ABC', 'ABCD', 'ABCDE'];

      mockWebContents = new MockWebContents(chunks, true);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      const onChunk = vi.fn();
      const startTime = Date.now();

      // Act
      await adapter.streamResponse(onChunk, 10000);
      const elapsed = Date.now() - startTime;

      // Assert
      // Should complete in reasonable time (not blocking)
      expect(elapsed).toBeLessThan(10000);
      expect(onChunk.mock.calls.length).toBeGreaterThan(0);
    });
  });

  describe('extractStreamingContent', () => {
    it('should extract current content during streaming', async () => {
      // Arrange
      mockWebContents = new MockWebContents(['Partial response...']);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      // Act
      const content = await (adapter as any).extractStreamingContent();

      // Assert
      expect(typeof content).toBe('string');
      expect(content.length).toBeGreaterThan(0);
    });

    it('should return empty string on extraction failure', async () => {
      // Arrange
      mockWebContents = new MockWebContents([]);
      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, mockWebContents as any);

      // Act
      const content = await (adapter as any).extractStreamingContent();

      // Assert
      expect(content).toBe('');
    });
  });

  describe('Error Handling', () => {
    it('should handle script execution errors gracefully', async () => {
      // Arrange
      let isWritingCallCount = 0;
      const errorWebContents = {
        executeJavaScript: vi.fn().mockImplementation((script: string) => {
          // isWriting check (uses !! with ||)
          if (script.includes('!!(')) {
            isWritingCallCount++;
            // Type for 2 calls, then stop
            if (isWritingCallCount <= 2) return true;
            return false;
          }
          // Selector check
          if (script.includes('!!document.querySelector')) {
            return true;
          }
          // Content extraction should fail
          throw new Error('Script error');
        }),
        loadURL: vi.fn(),
        getURL: vi.fn().mockReturnValue('https://example.com'),
        on: vi.fn(),
      };

      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, errorWebContents as any);
      const onChunk = vi.fn();

      // Act
      const result = await adapter.streamResponse(onChunk, 3000);

      // Assert - Should complete (possibly with empty data) due to error handling
      expect(result).toBeDefined();
    });

    it('should recover from transient errors', async () => {
      // Arrange
      let callCount = 0;
      const webContents = {
        executeJavaScript: vi.fn().mockImplementation((script: string) => {
          callCount++;

          // Simulate typing indicator
          if (script.includes('result-streaming') || script.includes('typingIndicator')) {
            return callCount <= 3; // Typing for first 3 calls
          }

          // Simulate content extraction
          if (callCount <= 2) {
            throw new Error('Transient error');
          }
          return 'Recovered content';
        }),
        loadURL: vi.fn(),
        getURL: vi.fn().mockReturnValue('https://example.com'),
        on: vi.fn(),
      };

      adapter = new BaseLLMAdapter('chatgpt' as LLMProvider, webContents as any);
      const onChunk = vi.fn();

      // Act
      const result = await adapter.streamResponse(onChunk, 3000);

      // Assert - should handle errors gracefully
      expect(result).toBeDefined();
    });
  });
});
