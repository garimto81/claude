/**
 * AvatarController 단위 테스트
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AvatarController } from '../src/avatar-controller';
import type { Expression, ExpressionTask, Priority } from '../src/avatar-controller';

describe('AvatarController', () => {
  let controller: AvatarController;

  beforeEach(() => {
    controller = new AvatarController();
    vi.useFakeTimers();
  });

  afterEach(() => {
    controller.clearQueue();
    vi.useRealTimers();
  });

  describe('초기 상태', () => {
    it('기본 표정은 neutral', () => {
      expect(controller.getCurrentExpression()).toBe('neutral');
    });

    it('재생 중이 아님', () => {
      expect(controller.isPlayingExpression()).toBe(false);
    });

    it('큐가 비어있음', () => {
      expect(controller.getQueueLength()).toBe(0);
    });
  });

  describe('setExpression', () => {
    it('즉시 표정 변경', () => {
      controller.setExpression('happy', 2000);

      expect(controller.getCurrentExpression()).toBe('happy');
      expect(controller.isPlayingExpression()).toBe(true);
    });

    it('duration 후 neutral로 복귀', () => {
      controller.setExpression('happy', 2000);

      expect(controller.getCurrentExpression()).toBe('happy');

      vi.advanceTimersByTime(2000);

      expect(controller.getCurrentExpression()).toBe('neutral');
      expect(controller.isPlayingExpression()).toBe(false);
    });

    it('기존 큐 초기화', () => {
      // 큐에 표정 추가
      controller.queueExpression({
        expression: 'surprised',
        duration: 1000,
        priority: 'low',
        timestamp: 0,
      });

      expect(controller.getQueueLength()).toBe(0); // 재생 시작으로 큐에서 제거됨

      // setExpression으로 즉시 변경
      controller.setExpression('happy', 2000);

      expect(controller.getCurrentExpression()).toBe('happy');
    });
  });

  describe('queueExpression', () => {
    it('큐에 표정 추가 (재생 중 아니면 즉시 재생)', () => {
      const task: ExpressionTask = {
        expression: 'happy',
        duration: 2000,
        priority: 'medium',
        timestamp: 0,
        trigger: 'commit',
      };

      controller.queueExpression(task);

      // 즉시 재생 시작
      expect(controller.getCurrentExpression()).toBe('happy');
      expect(controller.isPlayingExpression()).toBe(true);
    });

    it('우선순위 정렬 (high > medium > low)', () => {
      // 첫 번째 표정 시작 (즉시 재생됨)
      controller.queueExpression({
        expression: 'focused',
        duration: 5000,
        priority: 'low',
        timestamp: 0,
      });

      expect(controller.getCurrentExpression()).toBe('focused');

      // 이제 재생 중이므로 추가 표정들은 큐에 들어감
      controller.queueExpression({
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        timestamp: 0,
      });

      controller.queueExpression({
        expression: 'happy',
        duration: 1000,
        priority: 'high',
        timestamp: 0,
      });

      controller.queueExpression({
        expression: 'surprised',
        duration: 1000,
        priority: 'medium',
        timestamp: 0,
      });

      expect(controller.getQueueLength()).toBe(3);

      // 현재 표정(focused) 종료 후
      vi.advanceTimersByTime(5000);

      // high 우선순위가 먼저 재생됨
      expect(controller.getCurrentExpression()).toBe('happy');
    });

    it('duration 후 다음 표정 재생', () => {
      controller.queueExpression({
        expression: 'happy',
        duration: 1000,
        priority: 'medium',
        timestamp: 0,
      });

      controller.queueExpression({
        expression: 'surprised',
        duration: 1000,
        priority: 'medium',
        timestamp: 0,
      });

      expect(controller.getCurrentExpression()).toBe('happy');

      vi.advanceTimersByTime(1000);

      expect(controller.getCurrentExpression()).toBe('surprised');

      vi.advanceTimersByTime(1000);

      expect(controller.getCurrentExpression()).toBe('neutral');
    });
  });

  describe('clearQueue', () => {
    it('큐 초기화', () => {
      controller.setExpression('happy', 5000);

      controller.queueExpression({
        expression: 'surprised',
        duration: 1000,
        priority: 'medium',
        timestamp: 0,
      });

      controller.clearQueue();

      expect(controller.getQueueLength()).toBe(0);
    });
  });

  describe('expressionChangeHandler', () => {
    it('표정 변경 시 핸들러 호출', () => {
      const handler = vi.fn();
      controller.setExpressionChangeHandler(handler);

      controller.setExpression('happy', 2000);

      expect(handler).toHaveBeenCalledWith('happy', 2000, undefined);
    });

    it('neutral 복귀 시에도 핸들러 호출', () => {
      const handler = vi.fn();
      controller.setExpressionChangeHandler(handler);

      controller.setExpression('happy', 2000);

      vi.advanceTimersByTime(2000);

      expect(handler).toHaveBeenCalledWith('neutral', 0, undefined);
    });

    it('trigger 정보 전달', () => {
      const handler = vi.fn();
      controller.setExpressionChangeHandler(handler);

      controller.queueExpression({
        expression: 'happy',
        duration: 2000,
        priority: 'medium',
        timestamp: 0,
        trigger: 'commit',
      });

      expect(handler).toHaveBeenCalledWith('happy', 2000, 'commit');
    });
  });

  describe('Expression 타입', () => {
    const expressions: Expression[] = ['happy', 'surprised', 'neutral', 'focused', 'sorrow'];

    expressions.forEach((expr) => {
      it(`${expr} 표정 설정 가능`, () => {
        controller.setExpression(expr, 1000);
        expect(controller.getCurrentExpression()).toBe(expr);
      });
    });
  });

  describe('Priority 타입', () => {
    const priorities: Priority[] = ['high', 'medium', 'low'];

    priorities.forEach((priority) => {
      it(`${priority} 우선순위 큐 가능`, () => {
        controller.queueExpression({
          expression: 'happy',
          duration: 1000,
          priority,
          timestamp: 0,
        });

        expect(controller.getCurrentExpression()).toBe('happy');
      });
    });
  });
});
