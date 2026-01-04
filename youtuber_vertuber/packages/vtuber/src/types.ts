/**
 * VTuber 전용 타입 정의
 */

/**
 * VMC Protocol BlendShape 데이터
 */
export interface BlendShapeData {
  [key: string]: number; // e.g., { "Joy": 0.8, "Angry": 0.0 }
}

/**
 * VMC 연결 상태
 */
export interface VMCStatus {
  connected: boolean;
  host: string;
  port: number;
  lastUpdate: Date;
}

/**
 * VMC Client 설정
 */
export interface VMCClientOptions {
  host?: string;
  port?: number;
  localPort?: number;
  healthCheckInterval?: number; // ms (기본값: 5000)
}

/**
 * BlendShape 업데이트 콜백
 */
export type BlendShapeUpdateCallback = (blendShapes: BlendShapeData) => void;

/**
 * 연결 상태 변경 콜백
 */
export type ConnectionStatusCallback = (status: VMCStatus) => void;

/**
 * 아바타 표정 타입
 */
export type ExpressionType = 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';

/**
 * VMC BlendShape 매핑 (VSeeFace 표준)
 */
export const VMC_BLENDSHAPE_NAMES = {
  JOY: 'Joy',
  ANGRY: 'Angry',
  SORROW: 'Sorrow',
  FUN: 'Fun',
  BLINK_LEFT: 'Blink_L',
  BLINK_RIGHT: 'Blink_R',
} as const;
