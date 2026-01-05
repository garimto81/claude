import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RateLimiter, getRateLimiter, resetRateLimiter } from '../../src/services/rate-limiter.js';

describe('RateLimiter', () => {
  let limiter: RateLimiter;

  beforeEach(() => {
    vi.useFakeTimers();
    limiter = new RateLimiter({
      maxPerMinute: 5,
      maxPerHour: 20,
      userCooldownMs: 1000,
    });
  });

  afterEach(() => {
    limiter.destroy();
    vi.useRealTimers();
  });

  describe('canRespond', () => {
    it('제한이 없으면 응답을 허용해야 함', () => {
      const result = limiter.canRespond('user1');
      expect(result.allowed).toBe(true);
    });

    it('분당 제한에 도달하면 응답을 거부해야 함', () => {
      // 5회 응답 기록
      for (let i = 0; i < 5; i++) {
        limiter.recordResponse(`user${i}`);
      }

      const result = limiter.canRespond('user6');
      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('minute_limit');
    });

    it('시간당 제한에 도달하면 응답을 거부해야 함', () => {
      // 분당 제한을 높게 설정
      const highLimiter = new RateLimiter({
        maxPerMinute: 100,
        maxPerHour: 5,
        userCooldownMs: 0,
      });

      for (let i = 0; i < 5; i++) {
        highLimiter.recordResponse(`user${i}`);
      }

      const result = highLimiter.canRespond('user6');
      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('hour_limit');

      highLimiter.destroy();
    });

    it('사용자 쿨다운 내에는 응답을 거부해야 함', () => {
      limiter.recordResponse('user1');

      const result = limiter.canRespond('user1');
      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('user_cooldown');
      expect(result.waitMs).toBeLessThanOrEqual(1000);
    });

    it('쿨다운 후에는 응답을 허용해야 함', () => {
      limiter.recordResponse('user1');

      // 1초 경과
      vi.advanceTimersByTime(1001);

      const result = limiter.canRespond('user1');
      expect(result.allowed).toBe(true);
    });
  });

  describe('tryRespond', () => {
    it('허용되면 true를 반환하고 기록해야 함', () => {
      const result = limiter.tryRespond('user1');

      expect(result).toBe(true);
      expect(limiter.getStats().totalResponses).toBe(1);
    });

    it('거부되면 false를 반환해야 함', () => {
      limiter.recordResponse('user1');

      const result = limiter.tryRespond('user1');
      expect(result).toBe(false);
    });
  });

  describe('getStats', () => {
    it('통계를 정확히 반환해야 함', () => {
      limiter.recordResponse('user1');
      limiter.recordResponse('user2');

      // 제한으로 거부 발생
      for (let i = 0; i < 3; i++) {
        limiter.recordResponse(`user${i + 3}`);
      }
      limiter.canRespond('user6'); // rate limited

      const stats = limiter.getStats();
      expect(stats.totalResponses).toBe(5);
      expect(stats.currentMinute).toBe(5);
      expect(stats.currentHour).toBe(5);
      expect(stats.rateLimited).toBe(1);
    });
  });

  describe('reset', () => {
    it('모든 카운터와 상태를 초기화해야 함', () => {
      limiter.recordResponse('user1');
      limiter.recordResponse('user2');

      limiter.reset();

      const stats = limiter.getStats();
      expect(stats.totalResponses).toBe(0);
      expect(stats.currentMinute).toBe(0);
      expect(stats.currentHour).toBe(0);
      expect(stats.rateLimited).toBe(0);

      // 쿨다운도 초기화되어야 함
      const result = limiter.canRespond('user1');
      expect(result.allowed).toBe(true);
    });
  });

  describe('timer resets', () => {
    it('1분 후에 분 카운터가 리셋되어야 함', () => {
      limiter.recordResponse('user1');
      expect(limiter.getStats().currentMinute).toBe(1);

      vi.advanceTimersByTime(60 * 1000);

      expect(limiter.getStats().currentMinute).toBe(0);
      expect(limiter.getStats().totalResponses).toBe(1); // 총 카운트는 유지
    });

    it('1시간 후에 시간 카운터가 리셋되어야 함', () => {
      limiter.recordResponse('user1');
      expect(limiter.getStats().currentHour).toBe(1);

      vi.advanceTimersByTime(60 * 60 * 1000);

      expect(limiter.getStats().currentHour).toBe(0);
      expect(limiter.getStats().totalResponses).toBe(1);
    });
  });

  describe('config', () => {
    it('설정을 조회할 수 있어야 함', () => {
      const config = limiter.getConfig();
      expect(config.maxPerMinute).toBe(5);
      expect(config.maxPerHour).toBe(20);
      expect(config.userCooldownMs).toBe(1000);
    });

    it('설정을 업데이트할 수 있어야 함', () => {
      limiter.updateConfig({ maxPerMinute: 10 });

      const config = limiter.getConfig();
      expect(config.maxPerMinute).toBe(10);
      expect(config.maxPerHour).toBe(20); // 변경되지 않음
    });
  });
});

describe('Singleton', () => {
  afterEach(() => {
    resetRateLimiter();
  });

  it('싱글톤 인스턴스를 반환해야 함', () => {
    const limiter1 = getRateLimiter();
    const limiter2 = getRateLimiter();

    expect(limiter1).toBe(limiter2);
  });

  it('resetRateLimiter로 인스턴스를 초기화할 수 있어야 함', () => {
    const limiter1 = getRateLimiter();
    limiter1.recordResponse('user1');

    resetRateLimiter();

    const limiter2 = getRateLimiter();
    expect(limiter2.getStats().totalResponses).toBe(0);
  });
});
