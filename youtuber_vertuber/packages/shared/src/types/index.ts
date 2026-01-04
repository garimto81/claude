/**
 * WebSocket 메시지 타입 정의
 */
export type MessageType =
  | 'vtuber:expression'    // 아바타 표정 변경 트리거
  | 'vtuber:status'        // VSeeFace 연결 상태
  | 'vtuber:tracking';     // 웹캠 추적 데이터 (선택사항)

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
