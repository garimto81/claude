/**
 * ReactionMapper 단위 테스트
 */

import { describe, it, expect } from 'vitest';
import { ReactionMapper } from '../src/reaction-mapper';

describe('ReactionMapper', () => {
  describe('mapGitHubEvent', () => {
    it('commit → happy (medium)', () => {
      const mapping = ReactionMapper.mapGitHubEvent('commit');

      expect(mapping).toEqual({
        expression: 'happy',
        duration: 2000,
        priority: 'medium',
        trigger: 'commit',
      });
    });

    it('pr_merged → surprised (high)', () => {
      const mapping = ReactionMapper.mapGitHubEvent('pr_merged');

      expect(mapping).toEqual({
        expression: 'surprised',
        duration: 3000,
        priority: 'high',
        trigger: 'pr_merged',
      });
    });

    it('test_passed → focused → happy 시퀀스 (high)', () => {
      const mapping = ReactionMapper.mapGitHubEvent('test_passed');

      expect(Array.isArray(mapping)).toBe(true);
      expect(mapping).toHaveLength(2);

      const sequence = mapping as Array<{ expression: string; duration: number; priority: string }>;
      expect(sequence[0].expression).toBe('focused');
      expect(sequence[1].expression).toBe('happy');
    });

    it('test_failed → sorrow (medium)', () => {
      const mapping = ReactionMapper.mapGitHubEvent('test_failed');

      expect(mapping).toEqual({
        expression: 'sorrow',
        duration: 3000,
        priority: 'medium',
        trigger: 'test_failed',
      });
    });

    it('pr_opened → neutral (low)', () => {
      const mapping = ReactionMapper.mapGitHubEvent('pr_opened');

      expect(mapping).toEqual({
        expression: 'neutral',
        duration: 2000,
        priority: 'low',
        trigger: 'pr_opened',
      });
    });

    it('unknown event → neutral fallback', () => {
      const mapping = ReactionMapper.mapGitHubEvent('unknown_event');

      expect(mapping).toEqual({
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        trigger: 'unknown_event',
      });
    });
  });

  describe('mapChatEmotion', () => {
    it('positive → happy (medium)', () => {
      const mapping = ReactionMapper.mapChatEmotion('positive');

      expect(mapping).toEqual({
        expression: 'happy',
        duration: 2000,
        priority: 'medium',
        trigger: 'chat_positive',
      });
    });

    it('excited → happy (medium)', () => {
      const mapping = ReactionMapper.mapChatEmotion('excited');

      expect(mapping).toEqual({
        expression: 'happy',
        duration: 2000,
        priority: 'medium',
        trigger: 'chat_excited',
      });
    });

    it('curious → surprised (medium)', () => {
      const mapping = ReactionMapper.mapChatEmotion('curious');

      expect(mapping).toEqual({
        expression: 'surprised',
        duration: 2000,
        priority: 'medium',
        trigger: 'chat_curious',
      });
    });

    it('neutral → neutral (low)', () => {
      const mapping = ReactionMapper.mapChatEmotion('neutral');

      expect(mapping).toEqual({
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        trigger: 'chat_neutral',
      });
    });

    it('negative → sorrow (medium)', () => {
      const mapping = ReactionMapper.mapChatEmotion('negative');

      expect(mapping).toEqual({
        expression: 'sorrow',
        duration: 2000,
        priority: 'medium',
        trigger: 'chat_negative',
      });
    });

    it('unknown emotion → neutral fallback', () => {
      const mapping = ReactionMapper.mapChatEmotion('angry');

      expect(mapping).toEqual({
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        trigger: 'chat_angry',
      });
    });
  });

  describe('toExpressionTasks', () => {
    it('단일 매핑 → 배열로 변환', () => {
      const mapping = ReactionMapper.mapGitHubEvent('commit');
      const tasks = ReactionMapper.toExpressionTasks(mapping);

      expect(Array.isArray(tasks)).toBe(true);
      expect(tasks).toHaveLength(1);
      expect(tasks[0].expression).toBe('happy');
    });

    it('시퀀스 매핑 → 그대로 반환', () => {
      const mapping = ReactionMapper.mapGitHubEvent('test_passed');
      const tasks = ReactionMapper.toExpressionTasks(mapping);

      expect(Array.isArray(tasks)).toBe(true);
      expect(tasks).toHaveLength(2);
    });
  });

  describe('getSupportedGitHubEvents', () => {
    it('지원되는 GitHub 이벤트 목록 반환', () => {
      const events = ReactionMapper.getSupportedGitHubEvents();

      expect(events).toContain('commit');
      expect(events).toContain('pr_merged');
      expect(events).toContain('test_passed');
      expect(events).toContain('test_failed');
      expect(events).toContain('pr_opened');
      expect(events).toContain('pr_closed');
      expect(events).toContain('issue_opened');
      expect(events).toContain('issue_closed');
    });
  });

  describe('getSupportedChatEmotions', () => {
    it('지원되는 채팅 감정 목록 반환', () => {
      const emotions = ReactionMapper.getSupportedChatEmotions();

      expect(emotions).toContain('positive');
      expect(emotions).toContain('excited');
      expect(emotions).toContain('curious');
      expect(emotions).toContain('neutral');
      expect(emotions).toContain('negative');
    });
  });
});
