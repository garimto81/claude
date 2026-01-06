import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { YouTubeChatService, ChatMessage } from '../../src/services/youtube-chat.js';
import { OAuthService } from '../../src/services/oauth.js';

// googleapis 모킹
const mockVideosList = vi.fn();
const mockLiveChatMessagesList = vi.fn();
const mockLiveChatMessagesInsert = vi.fn();

vi.mock('googleapis', () => ({
  google: {
    youtube: vi.fn(() => ({
      videos: {
        list: mockVideosList,
      },
      liveChatMessages: {
        list: mockLiveChatMessagesList,
        insert: mockLiveChatMessagesInsert,
      },
    })),
    auth: {
      OAuth2: vi.fn(() => ({
        setCredentials: vi.fn(),
        credentials: {
          access_token: 'mock-token',
          refresh_token: 'mock-refresh',
          expiry_date: Date.now() + 3600000,
        },
      })),
    },
  },
}));

// OAuthService 모킹
vi.mock('../../src/services/oauth.js', () => ({
  getOAuthService: vi.fn(() => ({
    hasValidToken: vi.fn(() => true),
    getClient: vi.fn(() => ({
      credentials: {
        access_token: 'mock-token',
        expiry_date: Date.now() + 3600000,
      },
    })),
    getTokenInfo: vi.fn(() => ({
      hasToken: true,
      expiresAt: new Date(Date.now() + 3600000),
    })),
  })),
  OAuthService: vi.fn(),
}));

describe('YouTubeChatService', () => {
  let service: YouTubeChatService;
  const mockVideoId = 'test-video-id';
  const mockLiveChatId = 'test-live-chat-id';

  beforeEach(() => {
    vi.clearAllMocks();

    // 기본 모킹 설정
    mockVideosList.mockResolvedValue({
      data: {
        items: [
          {
            liveStreamingDetails: {
              activeLiveChatId: mockLiveChatId,
            },
          },
        ],
      },
    });

    mockLiveChatMessagesList.mockResolvedValue({
      data: {
        items: [],
        nextPageToken: 'next-page',
        pollingIntervalMillis: 5000,
      },
    });

    mockLiveChatMessagesInsert.mockResolvedValue({
      data: { id: 'sent-message-id' },
    });
  });

  afterEach(() => {
    if (service) {
      service.disconnect();
    }
  });

  describe('extractVideoId', () => {
    it('표준 watch URL에서 비디오 ID 추출', () => {
      const url = 'https://www.youtube.com/watch?v=abc123';
      expect(YouTubeChatService.extractVideoId(url)).toBe('abc123');
    });

    it('youtu.be 단축 URL에서 비디오 ID 추출', () => {
      const url = 'https://youtu.be/abc123';
      expect(YouTubeChatService.extractVideoId(url)).toBe('abc123');
    });

    it('/live/ URL에서 비디오 ID 추출', () => {
      const url = 'https://www.youtube.com/live/abc123';
      expect(YouTubeChatService.extractVideoId(url)).toBe('abc123');
    });

    it('추가 파라미터가 있는 URL 처리', () => {
      const url = 'https://www.youtube.com/watch?v=abc123&feature=share';
      expect(YouTubeChatService.extractVideoId(url)).toBe('abc123');
    });

    it('유효하지 않은 URL은 에러 발생', () => {
      expect(() =>
        YouTubeChatService.extractVideoId('https://invalid.com')
      ).toThrow('Invalid YouTube URL');
    });
  });

  describe('getLiveChatId', () => {
    beforeEach(() => {
      service = new YouTubeChatService();
    });

    it('비디오 ID로 Live Chat ID 조회', async () => {
      const liveChatId = await service.getLiveChatId(mockVideoId);
      expect(liveChatId).toBe(mockLiveChatId);
      expect(mockVideosList).toHaveBeenCalledWith({
        part: ['liveStreamingDetails'],
        id: [mockVideoId],
      });
    });

    it('비디오가 없으면 에러 발생', async () => {
      mockVideosList.mockResolvedValue({ data: { items: [] } });

      await expect(service.getLiveChatId('nonexistent')).rejects.toThrow(
        'Video not found'
      );
    });

    it('활성 라이브 채팅이 없으면 에러 발생', async () => {
      mockVideosList.mockResolvedValue({
        data: {
          items: [{ liveStreamingDetails: {} }],
        },
      });

      await expect(service.getLiveChatId(mockVideoId)).rejects.toThrow(
        'No active live chat'
      );
    });
  });

  describe('connect', () => {
    beforeEach(() => {
      service = new YouTubeChatService();
    });

    it('성공적으로 연결', async () => {
      const handler = vi.fn();
      await service.connect(mockVideoId, handler);

      expect(service.isConnected()).toBe(true);
      expect(service.getVideoId()).toBe(mockVideoId);
      expect(service.getLiveChatIdSync()).toBe(mockLiveChatId);
    });

    it('연결 후 폴링 시작', async () => {
      const handler = vi.fn();
      await service.connect(mockVideoId, handler);

      // 폴링이 시작되었는지 확인
      expect(mockLiveChatMessagesList).toHaveBeenCalled();
    });
  });

  describe('메시지 폴링', () => {
    it('폴링된 메시지를 핸들러에 전달', async () => {
      const mockMessage: youtube_v3.Schema$LiveChatMessage = {
        id: 'msg-1',
        snippet: {
          type: 'textMessageEvent',
          publishedAt: new Date().toISOString(),
          textMessageDetails: {
            messageText: 'Hello!',
          },
        },
        authorDetails: {
          displayName: 'TestUser',
          channelId: 'UC123',
          isChatModerator: false,
          isChatOwner: false,
        },
      };

      mockLiveChatMessagesList.mockResolvedValueOnce({
        data: {
          items: [mockMessage],
          nextPageToken: 'next',
          pollingIntervalMillis: 5000,
        },
      });

      const handler = vi.fn();
      service = new YouTubeChatService();
      await service.connect(mockVideoId, handler);

      // 핸들러가 호출되었는지 확인 (첫 폴링)
      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          author: 'TestUser',
          message: 'Hello!',
        })
      );
    });

    it('중복 메시지는 무시', async () => {
      const mockMessage = {
        id: 'duplicate-msg',
        snippet: {
          type: 'textMessageEvent',
          publishedAt: new Date().toISOString(),
          textMessageDetails: { messageText: 'Duplicate' },
        },
        authorDetails: { displayName: 'User' },
      };

      // 같은 메시지를 두 번 반환
      mockLiveChatMessagesList
        .mockResolvedValueOnce({
          data: { items: [mockMessage], pollingIntervalMillis: 100 },
        })
        .mockResolvedValueOnce({
          data: { items: [mockMessage], pollingIntervalMillis: 100 },
        });

      const handler = vi.fn();
      service = new YouTubeChatService();
      await service.connect(mockVideoId, handler);

      // 약간의 지연 후 두 번째 폴링
      await new Promise((resolve) => setTimeout(resolve, 150));

      // 핸들러는 한 번만 호출되어야 함
      expect(handler).toHaveBeenCalledTimes(1);
    });
  });

  describe('sendMessage', () => {
    beforeEach(async () => {
      service = new YouTubeChatService();
      await service.connect(mockVideoId, vi.fn());
    });

    it('메시지 전송 성공', async () => {
      await service.sendMessage('Test message');

      expect(mockLiveChatMessagesInsert).toHaveBeenCalledWith({
        part: ['snippet'],
        requestBody: {
          snippet: {
            liveChatId: mockLiveChatId,
            type: 'textMessageEvent',
            textMessageDetails: {
              messageText: 'Test message',
            },
          },
        },
      });
    });

    it('긴 메시지는 자동으로 잘림', async () => {
      const longMessage = 'A'.repeat(250);
      await service.sendMessage(longMessage);

      expect(mockLiveChatMessagesInsert).toHaveBeenCalledWith(
        expect.objectContaining({
          requestBody: expect.objectContaining({
            snippet: expect.objectContaining({
              textMessageDetails: expect.objectContaining({
                messageText: expect.stringMatching(/^A{197}\.\.\.$/),
              }),
            }),
          }),
        })
      );
    });

    it('빈 메시지는 에러 발생', async () => {
      await expect(service.sendMessage('')).rejects.toThrow(
        'Message cannot be empty'
      );
    });

    it('연결 안 된 상태에서 전송 시 에러', async () => {
      await service.disconnect();
      await expect(service.sendMessage('Test')).rejects.toThrow(
        'Not connected'
      );
    });
  });

  describe('disconnect', () => {
    it('연결 해제 후 상태 초기화', async () => {
      service = new YouTubeChatService();
      await service.connect(mockVideoId, vi.fn());

      await service.disconnect();

      expect(service.isConnected()).toBe(false);
      expect(service.getVideoId()).toBeNull();
      expect(service.getLiveChatIdSync()).toBeNull();
    });
  });
});

// youtube_v3 타입 인라인 정의 (테스트용)
declare namespace youtube_v3 {
  interface Schema$LiveChatMessage {
    id?: string;
    snippet?: {
      type?: string;
      publishedAt?: string;
      textMessageDetails?: {
        messageText?: string;
      };
    };
    authorDetails?: {
      displayName?: string;
      channelId?: string;
      isChatModerator?: boolean;
      isChatOwner?: boolean;
    };
  }
}
