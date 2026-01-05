/**
 * Main Server Client
 *
 * 메인 서버(Port 3001)와 HTTP 통신하여
 * 세션 정보, 프로젝트 상태 등을 조회합니다.
 */

export interface SessionStats {
  /** 세션 실행 중 여부 */
  running: boolean;
  /** 세션 경과 시간 (초) */
  duration?: number;
  /** 커밋 수 */
  commits?: number;
  /** 현재 프로젝트 */
  currentProject?: string;
  /** TDD 상태 */
  tdd?: {
    phase: 'red' | 'green' | 'refactor';
    testsPassed: number;
    testsTotal: number;
  };
}

export interface HealthStatus {
  status: 'ok' | 'error';
  version?: string;
  uptime?: number;
}

export interface MainServerConfig {
  /** 메인 서버 URL */
  baseUrl: string;
  /** 요청 타임아웃 (ms) */
  timeout: number;
}

const DEFAULT_CONFIG: MainServerConfig = {
  baseUrl: process.env.MAIN_SERVER_URL || 'http://localhost:3001',
  timeout: 5000,
};

export class MainServerClient {
  private config: MainServerConfig;

  constructor(config: Partial<MainServerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * 메인 서버 헬스 체크
   */
  async health(): Promise<HealthStatus> {
    try {
      const response = await this.fetch('/health');
      return response as HealthStatus;
    } catch (error) {
      console.error('[MainServer] Health check failed:', error);
      return { status: 'error' };
    }
  }

  /**
   * 세션 통계 조회
   */
  async getSessionStats(): Promise<SessionStats | null> {
    try {
      const response = await this.fetch('/api/session/stats');
      return response as SessionStats;
    } catch (error) {
      console.error('[MainServer] Failed to get session stats:', error);
      return null;
    }
  }

  /**
   * 현재 프로젝트 정보 조회
   */
  async getCurrentProject(): Promise<{ name: string; description: string } | null> {
    try {
      const response = await this.fetch('/api/project/current');
      return response as { name: string; description: string };
    } catch (error) {
      console.error('[MainServer] Failed to get current project:', error);
      return null;
    }
  }

  /**
   * TDD 상태 조회
   */
  async getTddStatus(): Promise<SessionStats['tdd'] | null> {
    try {
      const stats = await this.getSessionStats();
      return stats?.tdd || null;
    } catch (error) {
      console.error('[MainServer] Failed to get TDD status:', error);
      return null;
    }
  }

  /**
   * 방송 경과 시간 조회
   */
  async getStreamDuration(): Promise<number | null> {
    try {
      const stats = await this.getSessionStats();
      return stats?.duration || null;
    } catch (error) {
      console.error('[MainServer] Failed to get stream duration:', error);
      return null;
    }
  }

  /**
   * 메인 서버 연결 가능 여부 확인
   */
  async isAvailable(): Promise<boolean> {
    try {
      const health = await this.health();
      return health.status === 'ok';
    } catch {
      return false;
    }
  }

  /**
   * 설정 업데이트
   */
  updateConfig(config: Partial<MainServerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * HTTP fetch wrapper
   */
  private async fetch(path: string): Promise<unknown> {
    const url = `${this.config.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  }
}

// 싱글톤 인스턴스
let mainServerClientInstance: MainServerClient | null = null;

export function getMainServerClient(config?: Partial<MainServerConfig>): MainServerClient {
  if (!mainServerClientInstance) {
    mainServerClientInstance = new MainServerClient(config);
  }
  return mainServerClientInstance;
}

/**
 * 세션 시간을 포맷팅
 * @param seconds 초
 * @returns "1시간 30분" 형식
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (hours > 0) {
    return `${hours}시간 ${minutes}분`;
  }
  return `${minutes}분`;
}

/**
 * TDD 상태를 이모지로 표시
 */
export function formatTddPhase(phase: 'red' | 'green' | 'refactor'): string {
  const phases = {
    red: '🔴 Red (테스트 실패)',
    green: '🟢 Green (테스트 통과)',
    refactor: '🔵 Refactor (리팩토링)',
  };
  return phases[phase] || phase;
}
