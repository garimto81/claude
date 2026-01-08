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

describe('LRU Cache & Memory Management', () => {
  let limiter: RateLimiter;

  beforeEach(() => {
    vi.useFakeTimers();
    limiter = new RateLimiter({
      maxPerMinute: 1000,
      maxPerHour: 10000,
      userCooldownMs: 1000,
      maxTrackedUsers: 5,
      cleanupIntervalMs: 5000,
    });
  });

  afterEach(() => {
    limiter.destroy();
    vi.useRealTimers();
  });

  describe('getTrackedUserCount', () => {
    it('추적 중인 사용자 수를 반환해야 함', () => {
      expect(limiter.getTrackedUserCount()).toBe(0);

      limiter.recordResponse('user1');
      expect(limiter.getTrackedUserCount()).toBe(1);

      limiter.recordResponse('user2');
      expect(limiter.getTrackedUserCount()).toBe(2);
    });
  });

  describe('maxTrackedUsers', () => {
    it('최대 사용자 수를 초과하면 가장 오래된 사용자를 제거해야 함', () => {
      // 5명의 사용자 기록
      for (let i = 1; i <= 5; i++) {
        limiter.recordResponse(`user${i}`);
      }
      expect(limiter.getTrackedUserCount()).toBe(5);

      // 6번째 사용자 기록 - user1이 제거되어야 함
      limiter.recordResponse('user6');
      expect(limiter.getTrackedUserCount()).toBe(5);

      // user1은 제거되었으므로 쿨다운 없이 응답 가능
      const result = limiter.canRespond('user1');
      expect(result.allowed).toBe(true);
    });

    it('같은 사용자가 다시 응답하면 LRU 순서가 갱신되어야 함', () => {
      // 5명의 사용자 기록
      for (let i = 1; i <= 5; i++) {
        limiter.recordResponse(`user${i}`);
      }

      // user1이 다시 응답 - LRU 순서 갱신 (가장 최근으로)
      vi.advanceTimersByTime(1001); // 쿨다운 지남
      limiter.recordResponse('user1');

      // 새 사용자 추가 - user2가 가장 오래되었으므로 제거됨
      limiter.recordResponse('user6');

      // user1은 여전히 추적 중 (쿨다운 적용됨)
      const result1 = limiter.canRespond('user1');
      expect(result1.allowed).toBe(false);
      expect(result1.reason).toBe('user_cooldown');

      // user2는 제거되어 쿨다운 없음
      const result2 = limiter.canRespond('user2');
      expect(result2.allowed).toBe(true);
    });
  });

  describe('cleanupInactiveUsers', () => {
    it('비활성 사용자가 정리되어야 함', () => {
      limiter.recordResponse('user1');
      limiter.recordResponse('user2');
      expect(limiter.getTrackedUserCount()).toBe(2);

      // 비활성 임계값: 쿨다운 * 10 = 10초
      // cleanupInterval: 5초
      vi.advanceTimersByTime(5000); // 첫 번째 정리 실행 (5초 경과)
      expect(limiter.getTrackedUserCount()).toBe(2); // 아직 비활성 아님

      vi.advanceTimersByTime(5000); // 두 번째 정리 실행 (10초 경과)
      expect(limiter.getTrackedUserCount()).toBe(2); // 정확히 10초라 아직 유지

      vi.advanceTimersByTime(5000); // 세 번째 정리 실행 (15초 경과)
      expect(limiter.getTrackedUserCount()).toBe(0); // 비활성으로 제거됨
    });

    it('활성 사용자는 정리되지 않아야 함', () => {
      limiter.recordResponse('user1');

      // 4초 후 user1이 다시 응답
      vi.advanceTimersByTime(4000);
      limiter.recordResponse('user1');

      // cleanupInterval 대기 (5초 간격이므로 5초씩 진행)
      vi.advanceTimersByTime(5000); // 총 9초, cleanup 실행 (user1: 5초 경과)
      expect(limiter.getTrackedUserCount()).toBe(1);

      vi.advanceTimersByTime(5000); // 총 14초, cleanup 실행 (user1: 10초 경과)
      expect(limiter.getTrackedUserCount()).toBe(1); // 정확히 10초라 아직 유지

      vi.advanceTimersByTime(5000); // 총 19초, cleanup 실행 (user1: 15초 경과)
      expect(limiter.getTrackedUserCount()).toBe(0); // 비활성으로 제거
    });
  });
});
