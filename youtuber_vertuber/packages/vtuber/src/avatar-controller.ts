/**
 * AvatarController - 아바타 표정 제어 및 우선순위 큐 관리
 */

export type Expression = 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';
export type Priority = 'high' | 'medium' | 'low';

export interface ExpressionTask {
  expression: Expression;
  duration: number;
  priority: Priority;
  timestamp: number;
  trigger?: string;  // 트리거 출처 (commit, pr_merged, chat 등)
}

const PRIORITY_MAP: Record<Priority, number> = {
  high: 3,
  medium: 2,
  low: 1,
};

/**
 * 아바타 표정 컨트롤러
 * - 우선순위 큐 기반 표정 관리
 * - 동시 이벤트 발생 시 우선순위 높은 표정 먼저 재생
 * - 표정 지속 시간 자동 관리
 */
export class AvatarController {
  private queue: ExpressionTask[] = [];
  private currentExpression: Expression = 'neutral';
  private isPlaying: boolean = false;
  private playTimeout: NodeJS.Timeout | null = null;

  /**
   * 현재 표정 조회
   */
  getCurrentExpression(): Expression {
    return this.currentExpression;
  }

  /**
   * 재생 중 여부
   */
  isPlayingExpression(): boolean {
    return this.isPlaying;
  }

  /**
   * 큐에 있는 표정 개수
   */
  getQueueLength(): number {
    return this.queue.length;
  }

  /**
   * 즉시 표정 변경
   * - 현재 재생 중인 표정 중단
   * - 큐 초기화
   * - 즉시 표정 변경
   */
  setExpression(expression: Expression, duration: number = 2000): void {
    this.clearQueue();
    this.currentExpression = expression;
    this.isPlaying = true;

    // 이벤트 발생 (WebSocket broadcast는 외부에서 처리)
    this.onExpressionChange(expression, duration);

    // duration 후 neutral로 복귀
    if (this.playTimeout) {
      clearTimeout(this.playTimeout);
    }

    this.playTimeout = setTimeout(() => {
      this.currentExpression = 'neutral';
      this.isPlaying = false;
      this.onExpressionChange('neutral', 0);
    }, duration);
  }

  /**
   * 표정을 우선순위 큐에 추가
   * - 우선순위에 따라 정렬
   * - 현재 재생 중이 아니면 즉시 재생
   */
  queueExpression(task: ExpressionTask): void {
    // 타임스탬프 추가
    task.timestamp = Date.now();

    // 우선순위 정렬 삽입 (높은 우선순위가 앞으로)
    this.queue.push(task);
    this.queue.sort((a, b) => {
      const priorityDiff = PRIORITY_MAP[b.priority] - PRIORITY_MAP[a.priority];
      if (priorityDiff !== 0) {
        return priorityDiff;
      }
      // 우선순위 같으면 타임스탬프 순 (먼저 들어온 것 먼저)
      return a.timestamp - b.timestamp;
    });

    console.log(`[AvatarController] Queued: ${task.expression} (priority: ${task.priority}, queue: ${this.queue.length})`);

    // 현재 재생 중이 아니면 즉시 재생
    if (!this.isPlaying) {
      this.playNext();
    }
  }

  /**
   * 큐 초기화
   */
  clearQueue(): void {
    this.queue = [];
    if (this.playTimeout) {
      clearTimeout(this.playTimeout);
      this.playTimeout = null;
    }
    console.log('[AvatarController] Queue cleared');
  }

  /**
   * 다음 표정 재생
   */
  private playNext(): void {
    if (this.queue.length === 0) {
      this.isPlaying = false;
      this.currentExpression = 'neutral';
      this.onExpressionChange('neutral', 0);
      console.log('[AvatarController] Queue empty, returning to neutral');
      return;
    }

    this.isPlaying = true;
    const task = this.queue.shift()!;
    this.currentExpression = task.expression;

    console.log(`[AvatarController] Playing: ${task.expression} (${task.duration}ms, trigger: ${task.trigger || 'unknown'})`);

    // 이벤트 발생 (WebSocket broadcast는 외부에서 처리)
    this.onExpressionChange(task.expression, task.duration, task.trigger);

    // duration 후 다음 표정 재생
    if (this.playTimeout) {
      clearTimeout(this.playTimeout);
    }

    this.playTimeout = setTimeout(() => {
      this.playNext();
    }, task.duration);
  }

  /**
   * 표정 변경 이벤트 핸들러 (외부에서 설정)
   * - WebSocket broadcast 등을 이곳에서 처리
   */
  private expressionChangeHandler: ((expression: Expression, duration: number, trigger?: string) => void) | null = null;

  /**
   * 표정 변경 이벤트 핸들러 등록
   */
  onExpressionChange(expression: Expression, duration: number, trigger?: string): void {
    if (this.expressionChangeHandler) {
      this.expressionChangeHandler(expression, duration, trigger);
    }
  }

  /**
   * 표정 변경 이벤트 핸들러 설정
   */
  setExpressionChangeHandler(handler: (expression: Expression, duration: number, trigger?: string) => void): void {
    this.expressionChangeHandler = handler;
  }
}

// Singleton 인스턴스
export const avatarController = new AvatarController();
