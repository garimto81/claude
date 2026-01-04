import ollama from 'ollama';
import { getHostProfile } from '../config/index.js';
import { PromptBuilder } from './prompt-builder.js';

/**
 * LLM 클라이언트 (Ollama + Qwen 3)
 */
export class LLMClient {
  private model: string;
  private systemPrompt: string;

  constructor(model = 'qwen3:8b') {
    this.model = model;

    // 호스트 프로필 기반 시스템 프롬프트 생성
    const profile = getHostProfile();
    this.systemPrompt = PromptBuilder.buildSystemPrompt(profile, {
      maxResponseLength: parseInt(process.env.MAX_RESPONSE_LENGTH || '200', 10),
      includeProjects: true,
    });

    console.log('[LLMClient] System prompt initialized');
    console.log('[LLMClient] Host:', profile.host.name);
  }

  async generateResponse(userMessage: string): Promise<string> {
    try {
      const response = await ollama.chat({
        model: this.model,
        messages: [
          { role: 'system', content: this.systemPrompt },
          { role: 'user', content: userMessage },
        ],
        options: {
          temperature: 0.7,
          num_predict: 256,
        },
      });

      return response.message.content;
    } catch (error) {
      console.error('[LLM] Error:', error);
      return '죄송합니다, 잠시 후 다시 시도해주세요.';
    }
  }

  /**
   * 메시지 분류
   */
  async classifyMessage(message: string): Promise<MessageType> {
    try {
      const response = await ollama.chat({
        model: this.model,
        messages: [
          {
            role: 'system',
            content: '메시지를 분류하세요. question/greeting/command/chitchat/spam 중 하나만 답변.',
          },
          { role: 'user', content: message },
        ],
        options: { temperature: 0 },
      });

      const result = response.message.content.toLowerCase().trim();
      const validTypes = ['question', 'greeting', 'command', 'chitchat', 'spam'];
      return validTypes.includes(result) ? result as MessageType : 'chitchat';
    } catch (error) {
      console.error('[LLM] Classification error:', error);
      return 'chitchat';
    }
  }

  /**
   * 시스템 프롬프트 재생성 (Hot-reload 지원)
   */
  refreshSystemPrompt(): void {
    const profile = getHostProfile();
    this.systemPrompt = PromptBuilder.buildSystemPrompt(profile);
    console.log('[LLMClient] System prompt refreshed');
  }
}

export type MessageType = 'question' | 'greeting' | 'command' | 'chitchat' | 'spam';
