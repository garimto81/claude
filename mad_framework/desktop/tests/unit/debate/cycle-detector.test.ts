/**
 * CycleDetector Tests
 *
 * TDD: 텍스트 유사도 기반 순환 감지 테스트
 * - Levenshtein distance 기반 유사도 계산
 * - 3회 연속 유사 패턴 감지
 * - 설정 가능한 임계값
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CycleDetector } from '../../../electron/debate/cycle-detector';
import type { ElementVersion, LLMProvider } from '../../../shared/types';

const createMockBrowserManager = () => ({
  getAdapter: vi.fn().mockReturnValue({
    isLoggedIn: vi.fn().mockResolvedValue(true),
    waitForInputReady: vi.fn().mockResolvedValue(undefined),
    inputPrompt: vi.fn().mockResolvedValue(undefined),
    sendMessage: vi.fn().mockResolvedValue(undefined),
    waitForResponse: vi.fn().mockResolvedValue(undefined),
    extractResponse: vi.fn().mockResolvedValue(''),
  }),
  getWebContents: vi.fn().mockReturnValue({}),
});

describe('CycleDetector', () => {
  let detector: CycleDetector;
  let mockBrowserManager: ReturnType<typeof createMockBrowserManager>;

  beforeEach(() => {
    mockBrowserManager = createMockBrowserManager();
    detector = new CycleDetector(mockBrowserManager as any);
    vi.clearAllMocks();
  });

  describe('detectCycle - Similarity-based (default)', () => {
    it('should return false when less than 3 versions', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 82, timestamp: '', provider: 'claude' },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(false);
    });

    it('should detect A→A→A pattern (identical versions)', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'This is version A',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'This is version A',
          score: 81,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'This is version A',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(true);
    });

    it('should detect A→B→A pattern (alternating versions)', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'Version A with some content',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Version B completely different content here',
          score: 85,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Version A with some content',
          score: 81,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(true);
    });

    it('should detect stagnation (high similarity + low score improvement)', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'Code has minor issue in function A',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Code has minor issue in function B',
          score: 81,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Code has minor issue in function C',
          score: 82,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(true);
    });

    it('should NOT detect cycle for progressive improvement', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'Initial code with basic structure',
          score: 70,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Improved code with better error handling',
          score: 80,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Refactored code with clean architecture',
          score: 90,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(false);
    });

    it('should respect custom similarity threshold', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'Code version 1',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Code version 2',
          score: 81,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Code version 3',
          score: 82,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      // With low threshold (0.5), should detect cycle
      const resultLow = await detector.detectCycle('gemini', versions, {
        similarityThreshold: 0.5,
      });

      // With high threshold (0.95), should NOT detect cycle
      const resultHigh = await detector.detectCycle('gemini', versions, {
        similarityThreshold: 0.95,
      });

      expect(resultLow).toBe(true);
      expect(resultHigh).toBe(false);
    });

    it('should handle empty content gracefully', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: '', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: '', score: 81, timestamp: '', provider: 'claude' },
        { iteration: 3, content: '', score: 82, timestamp: '', provider: 'chatgpt' },
      ];

      const result = await detector.detectCycle('gemini', versions);

      // Empty content → 유사도 1.0 → 순환 감지
      expect(result).toBe(true);
    });

    it('should normalize text before comparison', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'CODE   WITH   SPACES',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'code with spaces',
          score: 81,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'CODE WITH SPACES',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      // Should detect cycle (case-insensitive, whitespace-normalized)
      expect(result).toBe(true);
    });

    it('should respect custom minVersions option', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V1', score: 81, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
      ];

      // With minVersions = 4, should return false (not enough versions)
      const result = await detector.detectCycle('gemini', versions, { minVersions: 4 });

      expect(result).toBe(false);
    });
  });

  describe('detectCycle - Judge model mode', () => {
    it('should use judge provider when useJudgeModel=true', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'Version A', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'Version B', score: 82, timestamp: '', provider: 'claude' },
        {
          iteration: 3,
          content: 'Version A similar',
          score: 81,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      expect(mockBrowserManager.getAdapter).toHaveBeenCalledWith('gemini');
    });

    it('should send prompt with 3 versions to judge', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'Code v1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'Code v2', score: 85, timestamp: '', provider: 'claude' },
        {
          iteration: 3,
          content: 'Code v1 again',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      const adapter = mockBrowserManager.getAdapter('gemini');
      expect(adapter.inputPrompt).toHaveBeenCalled();

      const prompt = adapter.inputPrompt.mock.calls[0][0];
      expect(prompt).toContain('Version 1');
      expect(prompt).toContain('Version 2');
      expect(prompt).toContain('Version 3');
      expect(prompt).toContain('Code v1');
      expect(prompt).toContain('Code v2');
    });

    it('should return true when judge detects cycle', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 82, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
      ];

      mockBrowserManager.getAdapter().extractResponse.mockResolvedValue(
        JSON.stringify({ isCycle: true, reason: 'V1 and V3 are identical' })
      );

      const result = await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      expect(result).toBe(true);
    });

    it('should return false when judge detects no cycle', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 85, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V3', score: 88, timestamp: '', provider: 'chatgpt' },
      ];

      mockBrowserManager.getAdapter().extractResponse.mockResolvedValue(
        JSON.stringify({ isCycle: false, reason: 'Progressive improvement detected' })
      );

      const result = await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      expect(result).toBe(false);
    });

    it('should handle judge response timeout gracefully', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 82, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V3', score: 84, timestamp: '', provider: 'chatgpt' },
      ];

      mockBrowserManager.getAdapter().waitForResponse.mockRejectedValue(
        new Error('Response timeout')
      );

      // Should not throw, should return false (assume no cycle on error)
      const result = await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      expect(result).toBe(false);
    });

    it('should handle malformed judge response', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 82, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V3', score: 84, timestamp: '', provider: 'chatgpt' },
      ];

      mockBrowserManager.getAdapter().extractResponse.mockResolvedValue('Invalid JSON response');

      const result = await detector.detectCycle('gemini', versions, { useJudgeModel: true });

      expect(result).toBe(false);
    });
  });

  describe('calculateTextSimilarity', () => {
    it('should return 1.0 for identical text', () => {
      const text = 'This is a test';
      const similarity = detector.calculateTextSimilarity(text, text);

      expect(similarity).toBe(1.0);
    });

    it('should return 0.0 for completely different text', () => {
      const text1 = 'AAAA';
      const text2 = 'BBBB';
      const similarity = detector.calculateTextSimilarity(text1, text2);

      expect(similarity).toBe(0.0);
    });

    it('should return value between 0-1 for similar text', () => {
      const text1 = 'Hello world';
      const text2 = 'Hello word';
      const similarity = detector.calculateTextSimilarity(text1, text2);

      expect(similarity).toBeGreaterThan(0.5);
      expect(similarity).toBeLessThan(1.0);
    });

    it('should be case-insensitive', () => {
      const text1 = 'HELLO';
      const text2 = 'hello';
      const similarity = detector.calculateTextSimilarity(text1, text2);

      expect(similarity).toBe(1.0);
    });

    it('should normalize whitespace', () => {
      const text1 = 'hello   world';
      const text2 = 'hello world';
      const similarity = detector.calculateTextSimilarity(text1, text2);

      expect(similarity).toBe(1.0);
    });

    it('should handle empty strings', () => {
      const similarity1 = detector.calculateTextSimilarity('', '');
      const similarity2 = detector.calculateTextSimilarity('', 'text');
      const similarity3 = detector.calculateTextSimilarity('text', '');

      expect(similarity1).toBe(1.0);
      expect(similarity2).toBe(0.0);
      expect(similarity3).toBe(0.0);
    });
  });

  describe('buildCycleDetectionPrompt', () => {
    it('should build clear prompt for judge', () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'First version',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Second version',
          score: 85,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Third version',
          score: 82,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const prompt = detector.buildCycleDetectionPrompt(versions);

      expect(prompt).toContain('순환');
      expect(prompt).toContain('Version 1');
      expect(prompt).toContain('First version');
      expect(prompt).toContain('JSON');
      expect(prompt).toContain('isCycle');
    });
  });

  describe('parseCycleResponse', () => {
    it('should parse valid JSON response', () => {
      const response = '{"isCycle": true, "reason": "Versions are repeating"}';

      const result = detector.parseCycleResponse(response);

      expect(result).toEqual({
        isCycle: true,
        reason: 'Versions are repeating',
      });
    });

    it('should extract JSON from markdown code block', () => {
      const response = `Here's my analysis:
\`\`\`json
{"isCycle": false, "reason": "No cycle detected"}
\`\`\`
`;

      const result = detector.parseCycleResponse(response);

      expect(result).toEqual({
        isCycle: false,
        reason: 'No cycle detected',
      });
    });

    it('should return default on invalid JSON', () => {
      const response = 'Not a JSON response';

      const result = detector.parseCycleResponse(response);

      expect(result).toEqual({
        isCycle: false,
        reason: 'Parse error',
      });
    });
  });

  describe('Edge cases', () => {
    it('should handle versions with special characters', async () => {
      const versions: ElementVersion[] = [
        {
          iteration: 1,
          content: 'Code with special chars: !@#$%^&*()',
          score: 80,
          timestamp: '',
          provider: 'chatgpt',
        },
        {
          iteration: 2,
          content: 'Code with special chars: !@#$%^&*()',
          score: 81,
          timestamp: '',
          provider: 'claude',
        },
        {
          iteration: 3,
          content: 'Code with special chars: !@#$%^&*()',
          score: 82,
          timestamp: '',
          provider: 'chatgpt',
        },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(true);
    });

    it('should handle very long content', async () => {
      const longContent = 'A'.repeat(10000);

      const versions: ElementVersion[] = [
        { iteration: 1, content: longContent, score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: longContent, score: 81, timestamp: '', provider: 'claude' },
        { iteration: 3, content: longContent, score: 82, timestamp: '', provider: 'chatgpt' },
      ];

      const result = await detector.detectCycle('gemini', versions);

      expect(result).toBe(true);
    });

    it('should handle more than 3 versions (use last 3)', async () => {
      const versions: ElementVersion[] = [
        { iteration: 1, content: 'V1', score: 80, timestamp: '', provider: 'chatgpt' },
        { iteration: 2, content: 'V2', score: 82, timestamp: '', provider: 'claude' },
        { iteration: 3, content: 'V3', score: 84, timestamp: '', provider: 'chatgpt' },
        { iteration: 4, content: 'V4', score: 80, timestamp: '', provider: 'claude' },
        { iteration: 5, content: 'V4', score: 81, timestamp: '', provider: 'chatgpt' },
        { iteration: 6, content: 'V4', score: 80, timestamp: '', provider: 'claude' },
      ];

      const result = await detector.detectCycle('gemini', versions);

      // Should only check last 3 (V4, V4, V4) → cycle
      expect(result).toBe(true);
    });
  });
});
