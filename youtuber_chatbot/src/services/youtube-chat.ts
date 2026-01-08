import { google, youtube_v3 } from 'googleapis';
import { OAuthService, getOAuthService } from './oauth.js';

/**
 * 채팅 메시지 타입
 */
export interface ChatMessage {
  author: string;
  message: string;
  timestamp: Date;
  authorChannelId?: string;
  isModerator?: boolean;
  isOwner?: boolean;
}

/**
 * 메시지 핸들러 타입
 */
type MessageHandler = (message: ChatMessage) => void;

/**
 * YouTube Live Chat 서비스 (공식 API 기반)
 * REST Polling 방식으로 메시지 수신
 */
export class YouTubeChatService {
  private youtube: youtube_v3.Youtube;
  private oauthService: OAuthService;
  private liveChatId: string | null = null;
  private pollingTimer: NodeJS.Timeout | null = null;
  private nextPageToken: string | undefined;
  private messageHandler: MessageHandler | null = null;
  private connected = false;
  private videoId: string | null = null;
  private processedMessageIds: Set<string> = new Set();

  // 기본 폴링 간격 (ms) - API 응답의 pollingIntervalMillis 사용 권장
  private static readonly DEFAULT_POLLING_INTERVAL = 5000;
  // 최대 저장할 메시지 ID 수 (메모리 관리)
  private static readonly MAX_PROCESSED_IDS = 1000;

  constructor(oauthService?: OAuthService) {
    this.oauthService = oauthService || getOAuthService();
    this.youtube = google.youtube({
      version: 'v3',
      auth: this.oauthService.getClient(),
    });
  }

  /**
   * YouTube Live URL에서 비디오 ID 추출
   */
  static extractVideoId(url: string): string {
    // 다양한 YouTube URL 형식 지원
    const patterns = [
      /[?&]v=([^&]+)/, // ?v= 또는 &v=
      /youtu\.be\/([^?]+)/, // youtu.be/VIDEO_ID
      /\/live\/([^?]+)/, // /live/VIDEO_ID
      /\/watch\/([^?]+)/, // /watch/VIDEO_ID
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }

    throw new Error('Invalid YouTube URL: Could not extract video ID');
  }

  /**
   * URL에서 서비스 인스턴스 생성 및 연결
   */
  static async fromLiveUrl(
    url: string,
    messageHandler: MessageHandler,
    oauthService?: OAuthService,
  ): Promise<YouTubeChatService> {
    const videoId = YouTubeChatService.extractVideoId(url);
    const service = new YouTubeChatService(oauthService);
    await service.connect(videoId, messageHandler);
    return service;
  }

  /**
   * 비디오 ID로 Live Chat ID 조회
   */
  async getLiveChatId(videoId: string): Promise<string> {
    const response = await this.youtube.videos.list({
      part: ['liveStreamingDetails'],
      id: [videoId],
    });

    const video = response.data.items?.[0];
    if (!video) {
      throw new Error(`Video not found: ${videoId}`);
    }

    const liveChatId = video.liveStreamingDetails?.activeLiveChatId;
    if (!liveChatId) {
      throw new Error(
        `No active live chat for video: ${videoId}. The stream may not be live.`,
      );
    }

    return liveChatId;
  }

  /**
   * 채팅 연결 (폴링 시작)
   */
  async connect(
    videoId: string,
    messageHandler: MessageHandler,
  ): Promise<void> {
    // OAuth 토큰 확인
    if (!this.oauthService.hasValidToken()) {
      throw new Error(
        'No valid OAuth token. Please authenticate first via /oauth/authorize',
      );
    }

    try {
      this.videoId = videoId;
      this.liveChatId = await this.getLiveChatId(videoId);
      this.messageHandler = messageHandler;
      this.connected = true;
      this.processedMessageIds.clear();

      console.log('[YouTubeChat] Connected to video:', videoId);
      console.log('[YouTubeChat] Live Chat ID:', this.liveChatId);

      // 폴링 시작
      await this.startPolling();
    } catch (error) {
      this.connected = false;
      console.error('[YouTubeChat] Connection failed:', error);
      throw error;
    }
  }

  /**
   * 메시지 폴링 시작
   */
  private async startPolling(): Promise<void> {
    // 초기 폴링
    await this.pollMessages();
  }

  /**
   * 메시지 폴링 (한 번 실행)
   */
  private async pollMessages(): Promise<void> {
    if (!this.connected || !this.liveChatId) {
      return;
    }

    try {
      const response = await this.youtube.liveChatMessages.list({
        liveChatId: this.liveChatId,
        part: ['snippet', 'authorDetails'],
        pageToken: this.nextPageToken,
      });

      const data = response.data;

      // 다음 페이지 토큰 저장
      this.nextPageToken = data.nextPageToken || undefined;

      // 폴링 간격 (API 권장값 사용)
      const pollingIntervalMillis =
        data.pollingIntervalMillis ||
        YouTubeChatService.DEFAULT_POLLING_INTERVAL;

      // 메시지 처리
      for (const item of data.items || []) {
        const messageId = item.id;

        // 중복 방지
        if (messageId && this.processedMessageIds.has(messageId)) {
          continue;
        }

        if (messageId) {
          this.processedMessageIds.add(messageId);

          // 메모리 관리: 오래된 ID 제거
          if (
            this.processedMessageIds.size >
            YouTubeChatService.MAX_PROCESSED_IDS
          ) {
            const idsArray = Array.from(this.processedMessageIds);
            this.processedMessageIds = new Set(
              idsArray.slice(-YouTubeChatService.MAX_PROCESSED_IDS / 2),
            );
          }
        }

        // textMessageEvent만 처리 (일반 채팅)
        if (item.snippet?.type === 'textMessageEvent') {
          const chatMessage: ChatMessage = {
            author: item.authorDetails?.displayName || 'Anonymous',
            message: item.snippet.textMessageDetails?.messageText || '',
            timestamp: new Date(item.snippet.publishedAt || Date.now()),
            authorChannelId: item.authorDetails?.channelId || undefined,
            isModerator: item.authorDetails?.isChatModerator || false,
            isOwner: item.authorDetails?.isChatOwner || false,
          };

          if (this.messageHandler && chatMessage.message) {
            this.messageHandler(chatMessage);
          }
        }
      }

      // 다음 폴링 스케줄
      if (this.connected) {
        this.pollingTimer = setTimeout(
          () => this.pollMessages(),
          pollingIntervalMillis,
        );
      }
    } catch (error: unknown) {
      console.error('[YouTubeChat] Polling error:', error);

      // 재시도 (지수 백오프)
      if (this.connected) {
        const retryDelay = 10000; // 10초 후 재시도
        console.log(`[YouTubeChat] Retrying in ${retryDelay / 1000}s...`);
        this.pollingTimer = setTimeout(() => this.pollMessages(), retryDelay);
      }
    }
  }

  /**
   * 메시지 전송
   */
  async sendMessage(message: string): Promise<void> {
    if (!this.connected || !this.liveChatId) {
      throw new Error('Not connected to YouTube Chat');
    }

    if (!message.trim()) {
      throw new Error('Message cannot be empty');
    }

    // 메시지 길이 제한 (YouTube 최대 200자)
    const maxLength = 200;
    const truncatedMessage =
      message.length > maxLength
        ? message.substring(0, maxLength - 3) + '...'
        : message;

    try {
      await this.youtube.liveChatMessages.insert({
        part: ['snippet'],
        requestBody: {
          snippet: {
            liveChatId: this.liveChatId,
            type: 'textMessageEvent',
            textMessageDetails: {
              messageText: truncatedMessage,
            },
          },
        },
      });

      console.log('[YouTubeChat] Message sent:', truncatedMessage);
    } catch (error) {
      console.error('[YouTubeChat] Failed to send message:', error);
      throw error;
    }
  }

  /**
   * 연결 해제
   */
  async disconnect(): Promise<void> {
    this.connected = false;

    if (this.pollingTimer) {
      clearTimeout(this.pollingTimer);
      this.pollingTimer = null;
    }

    this.liveChatId = null;
    this.videoId = null;
    this.messageHandler = null;
    this.nextPageToken = undefined;
    this.processedMessageIds.clear();

    console.log('[YouTubeChat] Disconnected');
  }

  /**
   * 연결 상태 확인
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * 현재 비디오 ID 반환
   */
  getVideoId(): string | null {
    return this.videoId;
  }

  /**
   * 현재 Live Chat ID 반환
   */
  getLiveChatIdSync(): string | null {
    return this.liveChatId;
  }
}
