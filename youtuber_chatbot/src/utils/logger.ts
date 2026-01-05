/**
 * Logger Utility
 *
 * 구조화된 로깅을 제공합니다.
 * - 레벨별 로깅 (debug, info, warn, error)
 * - 타임스탬프
 * - 컨텍스트 태그
 */

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerConfig {
  /** 최소 로그 레벨 */
  minLevel: LogLevel;
  /** 타임스탬프 표시 여부 */
  showTimestamp: boolean;
  /** 컨텍스트 태그 */
  context?: string;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const DEFAULT_CONFIG: LoggerConfig = {
  minLevel: (process.env.LOG_LEVEL as LogLevel) || 'info',
  showTimestamp: true,
};

export class Logger {
  private config: LoggerConfig;

  constructor(context?: string, config: Partial<LoggerConfig> = {}) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
      context,
    };
  }

  debug(message: string, ...args: unknown[]): void {
    this.log('debug', message, ...args);
  }

  info(message: string, ...args: unknown[]): void {
    this.log('info', message, ...args);
  }

  warn(message: string, ...args: unknown[]): void {
    this.log('warn', message, ...args);
  }

  error(message: string, ...args: unknown[]): void {
    this.log('error', message, ...args);
  }

  /**
   * 자식 로거 생성 (컨텍스트 상속)
   */
  child(context: string): Logger {
    const childContext = this.config.context
      ? `${this.config.context}:${context}`
      : context;
    return new Logger(childContext, this.config);
  }

  private log(level: LogLevel, message: string, ...args: unknown[]): void {
    if (LOG_LEVELS[level] < LOG_LEVELS[this.config.minLevel]) {
      return;
    }

    const parts: string[] = [];

    // 타임스탬프
    if (this.config.showTimestamp) {
      parts.push(this.formatTimestamp());
    }

    // 레벨
    parts.push(this.formatLevel(level));

    // 컨텍스트
    if (this.config.context) {
      parts.push(`[${this.config.context}]`);
    }

    // 메시지
    parts.push(message);

    const logMessage = parts.join(' ');

    // 콘솔 출력
    switch (level) {
    case 'debug':
      console.debug(logMessage, ...args);
      break;
    case 'info':
      console.log(logMessage, ...args);
      break;
    case 'warn':
      console.warn(logMessage, ...args);
      break;
    case 'error':
      console.error(logMessage, ...args);
      break;
    }
  }

  private formatTimestamp(): string {
    const now = new Date();
    return `[${now.toISOString()}]`;
  }

  private formatLevel(level: LogLevel): string {
    const levelColors: Record<LogLevel, string> = {
      debug: '🔍',
      info: 'ℹ️',
      warn: '⚠️',
      error: '❌',
    };
    return levelColors[level];
  }
}

// 기본 로거 인스턴스
const defaultLogger = new Logger();

export const logger = {
  debug: (message: string, ...args: unknown[]) => defaultLogger.debug(message, ...args),
  info: (message: string, ...args: unknown[]) => defaultLogger.info(message, ...args),
  warn: (message: string, ...args: unknown[]) => defaultLogger.warn(message, ...args),
  error: (message: string, ...args: unknown[]) => defaultLogger.error(message, ...args),
  child: (context: string) => defaultLogger.child(context),
};

export function createLogger(context: string): Logger {
  return new Logger(context);
}
