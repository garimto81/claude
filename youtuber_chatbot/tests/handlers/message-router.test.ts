import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MessageRouter } from '../../src/handlers/message-router.js';
import type { ChatMessage } from '../../src/services/youtube-chat.js';
import type { LLMClient } from '../../src/services/llm-client.js';

// Command 핸들러 모킹
vi.mock('../../src/handlers/command.js', () => ({
  handleCommand: vi.fn((message: string) => {
    if (message.startsWith('!help')) {
      return '사용 가능한 명령어: !help, !project, !status';
    }
    return '알 수 없는 명령어입니다.';
  }),
}));

describe('MessageRouter', () => {
  let router: MessageRouter;
  let mockLLMClient: LLMClient;

  beforeEach(() => {
    mockLLMClient = {
      classifyMessage: vi.fn(),
      generateResponse: vi.fn(),
    } as unknown as LLMClient;

    router = new MessageRouter(mockLLMClient);
  });

  describe('메시지 라우팅', () => {
    it('question 타입 메시지는 LLM 응답을 생성해야 함', async () => {
      const message: ChatMessage = {
        author: 'TestUser',
        message: 'TypeScript는 무엇인가요?',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('question');
      vi.mocked(mockLLMClient.generateResponse).mockResolvedValue('TypeScript는 JavaScript의 타입이 있는 슈퍼셋입니다.');

      const response = await router.route(message);

      expect(response).toBe('TypeScript는 JavaScript의 타입이 있는 슈퍼셋입니다.');
      expect(mockLLMClient.classifyMessage).toHaveBeenCalledWith(message.message);
      expect(mockLLMClient.generateResponse).toHaveBeenCalledWith(message.message);
    });

    it('greeting 타입 메시지는 환영 메시지를 반환해야 함', async () => {
      const message: ChatMessage = {
        author: 'NewViewer',
        message: '안녕하세요!',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('greeting');

      const response = await router.route(message);

      expect(response).toContain('NewViewer');
      expect(mockLLMClient.generateResponse).not.toHaveBeenCalled();
    });

    it('command 타입 메시지는 명령어 핸들러로 전달해야 함', async () => {
      const message: ChatMessage = {
        author: 'TestUser',
        message: '!help',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('command');

      const response = await router.route(message);

      expect(response).toBeDefined();
      expect(response).toContain('명령어');
    });

    it('chitchat 타입 메시지는 간단한 응답을 반환해야 함', async () => {
      const message: ChatMessage = {
        author: 'TestUser',
        message: '오늘 날씨 좋네요',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('chitchat');

      const response = await router.route(message);

      expect(response).toBeTruthy();
    });

    it('spam 타입 메시지는 무시해야 함', async () => {
      const message: ChatMessage = {
        author: 'Spammer',
        message: 'BUY NOW!!! CLICK HERE!!!',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('spam');

      const response = await router.route(message);

      expect(response).toBeNull();
    });
  });

  describe('에러 처리', () => {
    it('분류 실패 시 기본 응답을 반환해야 함', async () => {
      const message: ChatMessage = {
        author: 'TestUser',
        message: 'Test message',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockRejectedValue(new Error('Classification failed'));

      const response = await router.route(message);

      expect(response).toBeTruthy();
    });

    it('응답 생성 실패 시 에러 메시지를 반환해야 함', async () => {
      const message: ChatMessage = {
        author: 'TestUser',
        message: 'Test question',
        timestamp: new Date(),
      };

      vi.mocked(mockLLMClient.classifyMessage).mockResolvedValue('question');
      vi.mocked(mockLLMClient.generateResponse).mockRejectedValue(new Error('Generation failed'));

      const response = await router.route(message);

      expect(response).toContain('죄송');
    });
  });
});
