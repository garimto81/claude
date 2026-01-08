/**
 * WebSocket 메시지 타입 정의
 */
export type MessageType =
  | 'vtuber:expression'    // 아바타 표정 변경 트리거
  | 'vtuber:status'        // VSeeFace 연결 상태
  | 'vtuber:tracking'      // 웹캠 추적 데이터 (선택사항)
  | 'github:commit'        // GitHub Commit 이벤트
  | 'github:pr'            // GitHub Pull Request 이벤트
  | 'github:check'         // GitHub Check Run (CI) 이벤트
  | 'subscribe'            // 채널 구독 요청
  | 'unsubscribe';         // 채널 구독 해제

/**
 * WebSocket 구독 채널
 */
export type SubscriptionChannel =
  | 'vtuber'
  | 'github'
  | 'chat';

/**
 * VTuber 표정 타입
 */
export type VTuberExpression = 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';

/**
 * VTuber 반응 트리거
 */
export type VTuberTrigger = 'commit' | 'pr_merged' | 'test_passed' | 'test_failed' | 'chat';

/**
 * VTuber 표정 변경 페이로드
 */
export interface VTuberExpressionPayload {
  expression: VTuberExpression;
  duration: number;  // ms (지속 시간)
  trigger: VTuberTrigger;
  metadata?: {
    repo?: string;
    message?: string;
  };
}

/**
 * VTuber 상태 페이로드
 */
export interface VTuberStatusPayload {
  connected: boolean;
  vmcHost: string;
  vmcPort: number;
  avatarName?: string;
  lastUpdate: string;
}

/**
 * WebSocket 메시지 기본 구조
 */
export interface WebSocketMessage<T = unknown> {
  type: MessageType;
  payload: T;
  timestamp: string;
}

/**
 * GitHub Commit 페이로드
 */
export interface GitHubCommitPayload {
  repo: string;
  message: string;
  author: string;
  sha: string;
  url?: string;
}

/**
 * GitHub Pull Request 페이로드
 */
export interface GitHubPRPayload {
  repo: string;
  title: string;
  action: 'opened' | 'closed' | 'merged' | 'reopened';
  number: number;
  author: string;
  url?: string;
}

/**
 * GitHub Check Run (CI) 페이로드
 */
export interface GitHubCheckPayload {
  repo: string;
  name: string;
  status: 'queued' | 'in_progress' | 'completed';
  conclusion?: 'success' | 'failure' | 'cancelled' | 'skipped';
  url?: string;
}

/**
 * 채널 구독 요청 페이로드
 */
export interface SubscribePayload {
  channels: SubscriptionChannel[];
}
