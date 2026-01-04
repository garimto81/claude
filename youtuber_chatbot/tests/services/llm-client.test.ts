import { describe, it, expect, beforeEach, vi } from 'vitest';
import { LLMClient } from '../../src/services/llm-client.js';
import ollama from 'ollama';

// ollama 모듈 모킹
vi.mock('ollama', () => ({
  default: {
    chat: vi.fn(),
  },
}));

// config 모듈 모킹
vi.mock('../../src/config/index.js', () => ({
  getHostProfile: vi.fn(() => ({
    host: {
      name: 'TestHost',
      displayName: 'Test Display Name',
    },
    persona: {
      role: 'AI Assistant',
      tone: '친절한 톤',
      primaryLanguages: ['TypeScript'],
      expertise: ['백엔드'],
    },
    social: {
      github: 'testuser',
    },
    projects: [
      {
        id: 'test-project',
        name: 'Test Project',
        description: 'A test project',
        repository: 'testuser/test-repo',
        version: '1.0.0',
        stack: 'TypeScript',
      },
    ],
  })),
}));

describe('LLMClient', () => {
  let client: LLMClient;

  beforeEach(() => {
    vi.clearAllMocks();
    client = new LLMClient('qwen3:8b');
  });

  describe('generateResponse', () => {
    it('사용자 메시지에 대한 응답을 생성해야 함', async () => {
      const mockResponse = {
        message: {
          content: '안녕하세요! 무엇을 도와드릴까요?',
        },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const response = await client.generateResponse('안녕하세요');

      expect(response).toBe('안녕하세요! 무엇을 도와드릴까요?');
      expect(ollama.chat).toHaveBeenCalledWith({
        model: 'qwen3:8b',
        messages: expect.arrayContaining([
          { role: 'system', content: expect.any(String) },
          { role: 'user', content: '안녕하세요' },
        ]),
        options: {
          temperature: 0.7,
          num_predict: 256,
        },
      });
    });

    it('시스템 프롬프트를 포함해야 함', async () => {
      const mockResponse = {
        message: { content: '응답' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      await client.generateResponse('테스트');

      const callArgs = vi.mocked(ollama.chat).mock.calls[0][0];
      const systemMessage = callArgs.messages.find(m => m.role === 'system');

      expect(systemMessage).toBeDefined();
      expect(systemMessage?.content).toContain('AI Assistant');
      expect(systemMessage?.content).toContain('Test Display Name');
    });

    it('에러 발생 시 기본 메시지를 반환해야 함', async () => {
      vi.mocked(ollama.chat).mockRejectedValue(new Error('Ollama connection failed'));

      const response = await client.generateResponse('안녕');

      expect(response).toBe('죄송합니다, 잠시 후 다시 시도해주세요.');
    });
  });

  describe('classifyMessage', () => {
    it('메시지를 question으로 분류해야 함', async () => {
      const mockResponse = {
        message: { content: 'question' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('TypeScript는 어떻게 배우나요?');

      expect(type).toBe('question');
      expect(ollama.chat).toHaveBeenCalledWith({
        model: 'qwen3:8b',
        messages: expect.arrayContaining([
          {
            role: 'system',
            content: '메시지를 분류하세요. question/greeting/command/chitchat/spam 중 하나만 답변.',
          },
          { role: 'user', content: 'TypeScript는 어떻게 배우나요?' },
        ]),
        options: { temperature: 0 },
      });
    });

    it('메시지를 greeting으로 분류해야 함', async () => {
      const mockResponse = {
        message: { content: 'GREETING' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('안녕하세요!');

      expect(type).toBe('greeting');
    });

    it('메시지를 command로 분류해야 함', async () => {
      const mockResponse = {
        message: { content: 'command' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('!help');

      expect(type).toBe('command');
    });

    it('유효하지 않은 분류는 chitchat으로 처리해야 함', async () => {
      const mockResponse = {
        message: { content: 'invalid_type' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('blah blah');

      expect(type).toBe('chitchat');
    });

    it('에러 발생 시 chitchat으로 처리해야 함', async () => {
      vi.mocked(ollama.chat).mockRejectedValue(new Error('Classification failed'));

      const type = await client.classifyMessage('test');

      expect(type).toBe('chitchat');
    });

    it('대소문자 구분 없이 분류해야 함', async () => {
      const mockResponse = {
        message: { content: 'QUESTION' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('질문입니다');

      expect(type).toBe('question');
    });

    it('공백을 제거하고 분류해야 함', async () => {
      const mockResponse = {
        message: { content: '  spam  ' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      const type = await client.classifyMessage('광고 메시지');

      expect(type).toBe('spam');
    });
  });

  describe('refreshSystemPrompt', () => {
    it('시스템 프롬프트를 재생성해야 함', () => {
      // 프롬프트 갱신 테스트는 내부 상태 변경이므로
      // 실제로는 generateResponse를 호출하여 변경된 프롬프트가 사용되는지 확인
      expect(() => client.refreshSystemPrompt()).not.toThrow();
    });
  });

  describe('Model Configuration', () => {
    it('커스텀 모델을 사용할 수 있어야 함', async () => {
      const customClient = new LLMClient('qwen3:14b');

      const mockResponse = {
        message: { content: '응답' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      await customClient.generateResponse('테스트');

      expect(ollama.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'qwen3:14b',
        }),
      );
    });

    it('기본 모델은 qwen3:8b여야 함', async () => {
      const defaultClient = new LLMClient();

      const mockResponse = {
        message: { content: '응답' },
      };

      vi.mocked(ollama.chat).mockResolvedValue(mockResponse);

      await defaultClient.generateResponse('테스트');

      expect(ollama.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'qwen3:8b',
        }),
      );
    });
  });
});
