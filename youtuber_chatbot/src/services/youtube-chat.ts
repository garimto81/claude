import { Masterchat, AddChatItemAction } from '@stu43005/masterchat';

/**
 * YouTube Live Chat 서비스
 * masterchat을 래핑하여 간편한 인터페이스 제공
 */
export class YouTubeChatService {
  private videoId: string;
  private mc: Masterchat | null = null;
  private connected = false;

  constructor(videoId: string) {
    this.videoId = videoId;
  }

  /**
   * YouTube Live URL에서 비디오 ID 추출
   */
  static fromLiveUrl(url: string): YouTubeChatService {
    const videoIdMatch = url.match(/[?&]v=([^&]+)/);
    if (!videoIdMatch) {
      throw new Error('Invalid YouTube URL: Could not extract video ID');
    }
    return new YouTubeChatService(videoIdMatch[1]);
  }

  /**
   * 채팅 연결
   */
  async connect(messageHandler: (message: ChatMessage) => void): Promise<void> {
    try {
      this.mc = await Masterchat.init(this.videoId);

      this.mc.listen();
      this.mc.on('actions', (actions) => {
        for (const action of actions) {
          if (action.type === 'addChatItemAction') {
            const chatAction = action as AddChatItemAction;
            messageHandler({
              author: chatAction.authorName || 'Anonymous',
              message: chatAction.rawMessage || '',
              timestamp: chatAction.timestamp || new Date(),
            });
          }
        }
      });

      this.mc.on('error', (error) => {
        console.error('[YouTubeChat] Error:', error);
      });

      this.connected = true;
      console.log('[YouTubeChat] Connected to video:', this.videoId);
    } catch (error) {
      console.error('[YouTubeChat] Connection failed:', error);
      throw error;
    }
  }

  /**
   * 메시지 전송
   */
  async sendMessage(message: string): Promise<void> {
    if (!this.mc || !this.connected) {
      throw new Error('Not connected to YouTube Chat');
    }

    if (!message.trim()) {
      throw new Error('Message cannot be empty');
    }

    try {
      await this.mc.sendMessage(message);
      console.log('[YouTubeChat] Message sent:', message);
    } catch (error) {
      console.error('[YouTubeChat] Failed to send message:', error);
      throw error;
    }
  }

  /**
   * 연결 해제
   */
  async disconnect(): Promise<void> {
    if (this.mc) {
      this.mc.stop();
      this.mc = null;
      this.connected = false;
      console.log('[YouTubeChat] Disconnected');
    }
  }

  /**
   * 연결 상태 확인
   */
  isConnected(): boolean {
    return this.connected;
  }
}

/**
 * 채팅 메시지 타입
 */
export interface ChatMessage {
  author: string;
  message: string;
  timestamp: Date;
}
