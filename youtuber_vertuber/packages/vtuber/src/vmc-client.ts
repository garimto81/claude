/**
 * VMC Protocol 클라이언트
 *
 * VSeeFace와 VMC Protocol (OSC over UDP)을 통해 통신하는 클라이언트
 */

import osc from 'osc';
import type {
  BlendShapeData,
  VMCStatus,
  VMCClientOptions,
  BlendShapeUpdateCallback,
  ConnectionStatusCallback,
} from './types';

/**
 * VMC Protocol 클라이언트 클래스
 *
 * @example
 * ```ts
 * const client = new VMCClient({ host: 'localhost', port: 39539 });
 * await client.connect();
 *
 * client.onBlendShapeUpdate((blendShapes) => {
 *   console.log('BlendShapes:', blendShapes);
 * });
 *
 * client.sendExpression('Joy', 1.0);
 * ```
 */
export class VMCClient {
  private udpPort: osc.UDPPort | null = null;
  private connected: boolean = false;
  private host: string;
  private port: number;
  private localPort: number;
  private healthCheckInterval: number;
  private healthCheckTimer: NodeJS.Timeout | null = null;
  private lastUpdate: Date = new Date();

  private blendShapeCallbacks: BlendShapeUpdateCallback[] = [];
  private statusCallbacks: ConnectionStatusCallback[] = [];

  constructor(options: VMCClientOptions = {}) {
    this.host = options.host || 'localhost';
    this.port = options.port || 39539; // VSeeFace VMC Protocol 기본 포트
    this.localPort = options.localPort || 0; // 0 = 자동 할당
    this.healthCheckInterval = options.healthCheckInterval || 5000; // 5초
  }

  /**
   * VSeeFace VMC Protocol 서버에 연결
   */
  async connect(): Promise<void> {
    if (this.connected) {
      console.warn('[VMC] Already connected');
      return;
    }

    return new Promise((resolve, reject) => {
      this.udpPort = new osc.UDPPort({
        localAddress: '0.0.0.0',
        localPort: this.localPort,
        metadata: true,
      });

      this.udpPort.on('ready', () => {
        console.log(`[VMC] UDP Port ready on port ${this.udpPort?.options.localPort}`);
        this.connected = true;
        this.lastUpdate = new Date();
        this.notifyStatusChange();
        this.startHealthCheck();
        resolve();
      });

      this.udpPort.on('error', (err) => {
        console.error('[VMC] Error:', err);
        this.connected = false;
        this.notifyStatusChange();
        reject(err);
      });

      this.udpPort.on('message', (oscMsg) => {
        this.handleOSCMessage(oscMsg);
      });

      this.udpPort.open();
    });
  }

  /**
   * VMC 연결 해제
   */
  disconnect(): void {
    if (!this.connected) {
      console.warn('[VMC] Not connected');
      return;
    }

    this.stopHealthCheck();

    if (this.udpPort) {
      this.udpPort.close();
      this.udpPort = null;
    }

    this.connected = false;
    this.notifyStatusChange();
    console.log('[VMC] Disconnected');
  }

  /**
   * BlendShape 데이터 업데이트 콜백 등록
   */
  onBlendShapeUpdate(callback: BlendShapeUpdateCallback): void {
    this.blendShapeCallbacks.push(callback);
  }

  /**
   * 연결 상태 변경 콜백 등록
   */
  onStatusChange(callback: ConnectionStatusCallback): void {
    this.statusCallbacks.push(callback);
  }

  /**
   * VSeeFace에 표정 전송 (BlendShape 적용)
   *
   * @param expression - BlendShape 이름 (Joy, Angry, Sorrow, Fun 등)
   * @param value - BlendShape 값 (0.0 ~ 1.0)
   */
  sendExpression(expression: string, value: number = 1.0): void {
    if (!this.connected || !this.udpPort) {
      console.warn('[VMC] Not connected, cannot send expression');
      return;
    }

    // VMC Protocol: /VMC/Ext/Blend/Apply
    const message: osc.OscMessage = {
      address: '/VMC/Ext/Blend/Apply',
      args: [
        { type: 's', value: expression },
        { type: 'f', value: Math.max(0, Math.min(1, value)) }, // 0.0 ~ 1.0 클램프
      ],
    };

    this.udpPort.send(message, this.host, this.port);
    console.log(`[VMC] Sent expression: ${expression} = ${value}`);
  }

  /**
   * 현재 연결 상태 반환
   */
  getStatus(): VMCStatus {
    return {
      connected: this.connected,
      host: this.host,
      port: this.port,
      lastUpdate: this.lastUpdate,
    };
  }

  /**
   * OSC 메시지 핸들러 (내부)
   */
  private handleOSCMessage(oscMsg: osc.OscMessage): void {
    this.lastUpdate = new Date();

    // BlendShape 데이터 수신: /VMC/Ext/Blend/Val
    if (oscMsg.address.startsWith('/VMC/Ext/Blend/Val')) {
      const blendShapeName = oscMsg.address.split('/').pop();
      const value = oscMsg.args[0] as number;

      if (blendShapeName && typeof value === 'number') {
        const blendShapes: BlendShapeData = { [blendShapeName]: value };
        this.notifyBlendShapeUpdate(blendShapes);
      }
    }

    // 추가 VMC Protocol 메시지 처리 (필요 시)
    // /VMC/Ext/Root/Pos, /VMC/Ext/Bone/Pos 등
  }

  /**
   * BlendShape 업데이트 알림 (내부)
   */
  private notifyBlendShapeUpdate(blendShapes: BlendShapeData): void {
    this.blendShapeCallbacks.forEach((callback) => {
      try {
        callback(blendShapes);
      } catch (err) {
        console.error('[VMC] BlendShape callback error:', err);
      }
    });
  }

  /**
   * 연결 상태 변경 알림 (내부)
   */
  private notifyStatusChange(): void {
    const status = this.getStatus();
    this.statusCallbacks.forEach((callback) => {
      try {
        callback(status);
      } catch (err) {
        console.error('[VMC] Status callback error:', err);
      }
    });
  }

  /**
   * Health Check 시작 (내부)
   */
  private startHealthCheck(): void {
    this.healthCheckTimer = setInterval(() => {
      const now = new Date();
      const elapsed = now.getTime() - this.lastUpdate.getTime();

      // 10초 동안 데이터 수신 없으면 연결 끊김으로 간주
      if (elapsed > 10000 && this.connected) {
        console.warn('[VMC] No data received for 10s, marking as disconnected');
        this.connected = false;
        this.notifyStatusChange();
      }
    }, this.healthCheckInterval);

    console.log(`[VMC] Health check started (interval: ${this.healthCheckInterval}ms)`);
  }

  /**
   * Health Check 중지 (내부)
   */
  private stopHealthCheck(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
      console.log('[VMC] Health check stopped');
    }
  }
}
