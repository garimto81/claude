/**
 * WebSocket Manager
 *
 * 클라이언트 연결 관리, 채널 구독, 브로드캐스트 기능 제공
 */

import { WebSocketServer, WebSocket } from 'ws';
import type { Server } from 'http';
import type {
  SubscriptionChannel,
  WebSocketMessage,
  SubscribePayload,
} from '@youtuber/shared';

interface ClientInfo {
  id: string;
  ws: WebSocket;
  channels: Set<SubscriptionChannel>;
  connectedAt: Date;
}

/**
 * WebSocket Manager 클래스
 *
 * @example
 * ```ts
 * const wsManager = new WSManager();
 * wsManager.attach(httpServer);
 *
 * // 특정 채널에 브로드캐스트
 * wsManager.broadcast('vtuber', {
 *   type: 'vtuber:expression',
 *   payload: { expression: 'happy', duration: 2000, trigger: 'commit' },
 *   timestamp: new Date().toISOString(),
 * });
 * ```
 */
export class WSManager {
  private wss: WebSocketServer | null = null;
  private clients: Map<string, ClientInfo> = new Map();
  private clientIdCounter = 0;

  /**
   * HTTP 서버에 WebSocket 서버 연결
   */
  attach(server: Server): void {
    this.wss = new WebSocketServer({ server });

    this.wss.on('connection', (ws: WebSocket) => {
      const clientId = this.generateClientId();
      const clientInfo: ClientInfo = {
        id: clientId,
        ws,
        channels: new Set(),
        connectedAt: new Date(),
      };

      this.clients.set(clientId, clientInfo);
      console.log(`[WS] Client connected: ${clientId} (total: ${this.clients.size})`);

      // 메시지 핸들링
      ws.on('message', (data: Buffer) => {
        this.handleMessage(clientId, data);
      });

      // 연결 종료
      ws.on('close', () => {
        this.clients.delete(clientId);
        console.log(`[WS] Client disconnected: ${clientId} (total: ${this.clients.size})`);
      });

      // 에러 처리
      ws.on('error', (error) => {
        console.error(`[WS] Client error (${clientId}):`, error.message);
      });

      // 연결 환영 메시지
      this.send(clientId, {
        type: 'vtuber:status',
        payload: { connected: true, clientId },
        timestamp: new Date().toISOString(),
      });
    });

    console.log('[WS] WebSocket server attached');
  }

  /**
   * 클라이언트 메시지 처리
   */
  private handleMessage(clientId: string, data: Buffer): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    try {
      const message = JSON.parse(data.toString()) as WebSocketMessage;

      switch (message.type) {
        case 'subscribe':
          this.handleSubscribe(clientId, message.payload as SubscribePayload);
          break;
        case 'unsubscribe':
          this.handleUnsubscribe(clientId, message.payload as SubscribePayload);
          break;
        default:
          console.log(`[WS] Received message from ${clientId}:`, message.type);
      }
    } catch (error) {
      console.error(`[WS] Invalid message from ${clientId}:`, error);
    }
  }

  /**
   * 채널 구독 처리
   */
  private handleSubscribe(clientId: string, payload: SubscribePayload): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    const { channels } = payload;
    channels.forEach((channel) => {
      client.channels.add(channel);
    });

    console.log(`[WS] Client ${clientId} subscribed to: ${channels.join(', ')}`);
  }

  /**
   * 채널 구독 해제 처리
   */
  private handleUnsubscribe(clientId: string, payload: SubscribePayload): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    const { channels } = payload;
    channels.forEach((channel) => {
      client.channels.delete(channel);
    });

    console.log(`[WS] Client ${clientId} unsubscribed from: ${channels.join(', ')}`);
  }

  /**
   * 특정 클라이언트에 메시지 전송
   */
  send(clientId: string, message: WebSocketMessage): boolean {
    const client = this.clients.get(clientId);
    if (!client || client.ws.readyState !== WebSocket.OPEN) {
      return false;
    }

    try {
      client.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error(`[WS] Failed to send to ${clientId}:`, error);
      return false;
    }
  }

  /**
   * 특정 채널 구독자에게 브로드캐스트
   */
  broadcast(channel: SubscriptionChannel, message: WebSocketMessage): number {
    let sentCount = 0;

    this.clients.forEach((client) => {
      // 채널 구독자이거나, 모든 클라이언트에게 전송 (채널이 비어있으면 구독 안해도 전송)
      if (client.channels.has(channel) || client.channels.size === 0) {
        if (client.ws.readyState === WebSocket.OPEN) {
          try {
            client.ws.send(JSON.stringify(message));
            sentCount++;
          } catch (error) {
            console.error(`[WS] Broadcast failed for ${client.id}:`, error);
          }
        }
      }
    });

    console.log(`[WS] Broadcast to ${channel}: ${sentCount} clients`);
    return sentCount;
  }

  /**
   * 모든 클라이언트에게 브로드캐스트
   */
  broadcastAll(message: WebSocketMessage): number {
    let sentCount = 0;

    this.clients.forEach((client) => {
      if (client.ws.readyState === WebSocket.OPEN) {
        try {
          client.ws.send(JSON.stringify(message));
          sentCount++;
        } catch (error) {
          console.error(`[WS] Broadcast failed for ${client.id}:`, error);
        }
      }
    });

    console.log(`[WS] Broadcast all: ${sentCount} clients`);
    return sentCount;
  }

  /**
   * 연결된 클라이언트 수
   */
  getClientCount(): number {
    return this.clients.size;
  }

  /**
   * 채널별 구독자 수
   */
  getChannelStats(): Record<SubscriptionChannel, number> {
    const stats: Record<string, number> = {
      vtuber: 0,
      github: 0,
      chat: 0,
    };

    this.clients.forEach((client) => {
      client.channels.forEach((channel) => {
        stats[channel] = (stats[channel] || 0) + 1;
      });
    });

    return stats as Record<SubscriptionChannel, number>;
  }

  /**
   * WebSocket 서버 종료
   */
  close(): void {
    if (this.wss) {
      this.wss.close();
      this.clients.clear();
      console.log('[WS] WebSocket server closed');
    }
  }

  /**
   * 클라이언트 ID 생성
   */
  private generateClientId(): string {
    this.clientIdCounter++;
    return `client_${this.clientIdCounter}_${Date.now().toString(36)}`;
  }
}

// Singleton 인스턴스
export const wsManager = new WSManager();
