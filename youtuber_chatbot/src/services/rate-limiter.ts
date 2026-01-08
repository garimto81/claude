/**
 * Rate Limiter
 *
 * YouTube 채팅 응답 제한을 관리합니다.
 * - 분당 최대 응답 수
 * - 사용자별 쿨다운
 * - 시간당 총 응답 제한
 */

interface RateLimitConfig {
  /** 분당 최대 응답 수 */
  maxPerMinute: number;
  /** 시간당 최대 응답 수 */
  maxPerHour: number;
  /** 사용자별 쿨다운 (ms) */
  userCooldownMs: number;
  /** 최대 추적 사용자 수 (메모리 제한) */
  maxTrackedUsers: number;
  /** 비활성 사용자 정리 주기 (ms) */
  cleanupIntervalMs: number;
}

interface RateLimitStats {
  /** 현재 분 응답 수 */
  currentMinute: number;
  /** 현재 시간 응답 수 */
  currentHour: number;
  /** 총 응답 수 */
  totalResponses: number;
  /** 제한으로 거부된 수 */
  rateLimited: number;
}

const DEFAULT_CONFIG: RateLimitConfig = {
  maxPerMinute: 30,
  maxPerHour: 500,
  userCooldownMs: 5000, // 5초
  maxTrackedUsers: 10000, // 최대 10,000명
  cleanupIntervalMs: 5 * 60 * 1000, // 5분마다 정리
};

export class RateLimiter {
  private config: RateLimitConfig;
  private minuteCount = 0;
  private hourCount = 0;
  private totalCount = 0;
  private rateLimitedCount = 0;
  private userLastResponse: Map<string, number> = new Map();
  private minuteResetTimer: NodeJS.Timeout | null = null;
  private hourResetTimer: NodeJS.Timeout | null = null;
  private cleanupTimer: NodeJS.Timeout | null = null;

  constructor(config: Partial<RateLimitConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.startTimers();
  }

  /**
   * 추적 중인 사용자 수
   */
  getTrackedUserCount(): number {
    return this.userLastResponse.size;
  }

  /**
   * 응답 가능 여부 확인
   * @param userId 사용자 ID (채널 ID 또는 이름)
   * @returns 응답 가능 여부와 대기 시간
   */
  canRespond(userId: string): { allowed: boolean; waitMs?: number; reason?: string } {
    // 1. 분당 제한 확인
    if (this.minuteCount >= this.config.maxPerMinute) {
      this.rateLimitedCount++;
      return {
        allowed: false,
        reason: 'minute_limit',
        waitMs: this.getTimeUntilMinuteReset(),
      };
    }

    // 2. 시간당 제한 확인
    if (this.hourCount >= this.config.maxPerHour) {
      this.rateLimitedCount++;
      return {
        allowed: false,
        reason: 'hour_limit',
        waitMs: this.getTimeUntilHourReset(),
      };
    }

    // 3. 사용자별 쿨다운 확인
    const lastResponse = this.userLastResponse.get(userId);
    if (lastResponse) {
      const elapsed = Date.now() - lastResponse;
      if (elapsed < this.config.userCooldownMs) {
        return {
          allowed: false,
          reason: 'user_cooldown',
          waitMs: this.config.userCooldownMs - elapsed,
        };
      }
    }

    return { allowed: true };
  }

  /**
   * 응답 기록
   * @param userId 사용자 ID
   */
  recordResponse(userId: string): void {
    this.minuteCount++;
    this.hourCount++;
    this.totalCount++;

    // LRU: 기존 항목 삭제 후 재삽입 (최신으로 이동)
    this.userLastResponse.delete(userId);
    this.userLastResponse.set(userId, Date.now());

    // 최대 사용자 수 초과 시 가장 오래된 항목 제거
    if (this.userLastResponse.size > this.config.maxTrackedUsers) {
      const oldestKey = this.userLastResponse.keys().next().value;
      if (oldestKey) {
        this.userLastResponse.delete(oldestKey);
      }
    }
  }

  /**
   * 응답 시도 (확인 + 기록)
   * @param userId 사용자 ID
   * @returns 응답 가능 여부
   */
  tryRespond(userId: string): boolean {
    const result = this.canRespond(userId);
    if (result.allowed) {
      this.recordResponse(userId);
      return true;
    }
    return false;
  }

  /**
   * 통계 조회
   */
  getStats(): RateLimitStats {
    return {
      currentMinute: this.minuteCount,
      currentHour: this.hourCount,
      totalResponses: this.totalCount,
      rateLimited: this.rateLimitedCount,
    };
  }

  /**
   * 설정 조회
   */
  getConfig(): RateLimitConfig {
    return { ...this.config };
  }

  /**
   * 설정 업데이트
   */
  updateConfig(config: Partial<RateLimitConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * 리셋
   */
  reset(): void {
    this.minuteCount = 0;
    this.hourCount = 0;
    this.totalCount = 0;
    this.rateLimitedCount = 0;
    this.userLastResponse.clear();
  }

  /**
   * 정리 (타이머 해제)
   */
  destroy(): void {
    if (this.minuteResetTimer) {
      clearInterval(this.minuteResetTimer);
    }
    if (this.hourResetTimer) {
      clearInterval(this.hourResetTimer);
    }
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }
  }

  private startTimers(): void {
    // 매 분마다 분 카운트 리셋
    this.minuteResetTimer = setInterval(() => {
      this.minuteCount = 0;
    }, 60 * 1000);

    // 매 시간마다 시간 카운트 리셋
    this.hourResetTimer = setInterval(() => {
      this.hourCount = 0;
    }, 60 * 60 * 1000);

    // 주기적으로 비활성 사용자 정리
    this.cleanupTimer = setInterval(() => {
      this.cleanupInactiveUsers();
    }, this.config.cleanupIntervalMs);
  }

  /**
   * 비활성 사용자 정리 (쿨다운 시간의 10배 이상 비활성)
   */
  private cleanupInactiveUsers(): void {
    const now = Date.now();
    const inactiveThreshold = this.config.userCooldownMs * 10; // 쿨다운의 10배

    for (const [userId, lastResponse] of this.userLastResponse.entries()) {
      if (now - lastResponse > inactiveThreshold) {
        this.userLastResponse.delete(userId);
      }
    }
  }

  private getTimeUntilMinuteReset(): number {
    // 다음 분까지 남은 시간 (대략적)
    return 60 * 1000 - (Date.now() % (60 * 1000));
  }

  private getTimeUntilHourReset(): number {
    // 다음 시간까지 남은 시간 (대략적)
    return 60 * 60 * 1000 - (Date.now() % (60 * 60 * 1000));
  }
}

// 싱글톤 인스턴스
let rateLimiterInstance: RateLimiter | null = null;

export function getRateLimiter(config?: Partial<RateLimitConfig>): RateLimiter {
  if (!rateLimiterInstance) {
    rateLimiterInstance = new RateLimiter(config);
  }
  return rateLimiterInstance;
}

export function resetRateLimiter(): void {
  if (rateLimiterInstance) {
    rateLimiterInstance.destroy();
    rateLimiterInstance = null;
  }
}
