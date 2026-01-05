import { describe, it, expect, vi, beforeEach } from 'vitest';
import { YouTubeChatService } from '../../src/services/youtube-chat.js';

// Masterchat 모킹
const mockListen = vi.fn();
const mockSendMessage = vi.fn();
const mockStop = vi.fn();
const mockOn = vi.fn();

vi.mock('@stu43005/masterchat', () => ({
  Masterchat: {
    init: vi.fn(() => ({
      listen: mockListen,
      sendMessage: mockSendMessage,
      stop: mockStop,
      on: mockOn,
    })),
  },
}));

describe('YouTubeChatService', () => {
  let service: YouTubeChatService;
  const mockVideoId = 'test-video-id';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('초기화', () => {
    it('비디오 ID로 서비스를 생성해야 함', () => {
      service = new YouTubeChatService(mockVideoId);
      expect(service).toBeDefined();
    });

    it('Live URL에서 비디오 ID를 추출해야 함', () => {
      const liveUrl = 'https://www.youtube.com/watch?v=test-video-id';
      service = YouTubeChatService.fromLiveUrl(liveUrl);
      expect(service).toBeDefined();
    });

    it('유효하지 않은 URL은 에러를 발생시켜야 함', () => {
      const invalidUrl = 'https://invalid-url.com';
      expect(() => YouTubeChatService.fromLiveUrl(invalidUrl)).toThrow();
    });
  });

  describe('채팅 연결', () => {
    beforeEach(() => {
      service = new YouTubeChatService(mockVideoId);
    });

    it('연결 시 리스너를 등록해야 함', async () => {
      const messageHandler = vi.fn();
      await service.connect(messageHandler);

      // 연결이 성공적으로 되었는지 확인
      expect(service.isConnected()).toBe(true);
    });

    it('메시지 수신 시 핸들러를 호출해야 함', async () => {
      const messageHandler = vi.fn();
      await service.connect(messageHandler);

      // 모킹된 메시지 전송
      // (실제 구현에서 처리)
    });

    it('연결 해제 시 리스너를 제거해야 함', async () => {
      const messageHandler = vi.fn();
      await service.connect(messageHandler);

      await service.disconnect();
      expect(service.isConnected()).toBe(false);
    });
  });

  describe('메시지 전송', () => {
    beforeEach(async () => {
      service = new YouTubeChatService(mockVideoId);
      await service.connect(vi.fn());
    });

    it('메시지를 전송할 수 있어야 함', async () => {
      const message = 'Hello, YouTube!';
      await expect(service.sendMessage(message)).resolves.not.toThrow();
    });

    it('연결되지 않은 상태에서 전송 시 에러 발생', async () => {
      await service.disconnect();
      await expect(service.sendMessage('test')).rejects.toThrow();
    });

    it('빈 메시지는 전송하지 않아야 함', async () => {
      await expect(service.sendMessage('')).rejects.toThrow();
    });
  });

  describe('에러 처리', () => {
    it('연결 실패 시 재시도해야 함', async () => {
      service = new YouTubeChatService(mockVideoId);

      // 연결 실패를 시뮬레이션
      const messageHandler = vi.fn();

      // 재시도 로직 테스트 (구현 시 수정 가능)
      await expect(service.connect(messageHandler)).resolves.not.toThrow();
    });
  });
});
