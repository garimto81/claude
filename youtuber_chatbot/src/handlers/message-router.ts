import type { ChatMessage } from '../services/youtube-chat.js';
import type { LLMClient } from '../services/llm-client.js';
import { handleCommand } from './command.js';

/**
 * 메시지 라우터
 * - 메시지를 분류하고 적절한 핸들러로 라우팅
 */
export class MessageRouter {
  constructor(private llmClient: LLMClient) {}

  /**
   * 메시지를 라우팅하고 응답 생성
   */
  async route(message: ChatMessage): Promise<string | null> {
    try {
      // 1. 메시지 분류
      const messageType = await this.llmClient.classifyMessage(message.message);

      // 2. 타입별 처리
      switch (messageType) {
      case 'question':
        return await this.handleQuestion(message);

      case 'greeting':
        return this.handleGreeting(message);

      case 'command':
        return this.handleCommand(message);

      case 'chitchat':
        return this.handleChitChat(message);

      case 'spam':
        console.log(`[MessageRouter] Spam message ignored from ${message.author}`);
        return null;

      default:
        return this.handleChitChat(message);
      }
    } catch (error) {
      console.error('[MessageRouter] Error routing message:', error);
      return '죄송합니다, 메시지 처리 중 문제가 발생했습니다.';
    }
  }

  /**
   * 질문 처리
   */
  private async handleQuestion(message: ChatMessage): Promise<string> {
    try {
      const response = await this.llmClient.generateResponse(message.message);
      return response;
    } catch (error) {
      console.error('[MessageRouter] Error generating response:', error);
      return '죄송합니다, 답변을 생성할 수 없습니다.';
    }
  }

  /**
   * 인사 처리
   */
  private handleGreeting(message: ChatMessage): string {
    const greetings = [
      `${message.author}님, 환영합니다! 👋`,
      `안녕하세요 ${message.author}님! 방송에 오신 걸 환영합니다!`,
      `${message.author}님, 반갑습니다! 궁금한 점이 있으시면 언제든 물어보세요!`,
    ];

    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  /**
   * 명령어 처리
   */
  private handleCommand(message: ChatMessage): string {
    try {
      return handleCommand(message.message);
    } catch (error) {
      console.error('[MessageRouter] Error handling command:', error);
      return '명령어 처리 중 오류가 발생했습니다.';
    }
  }

  /**
   * 잡담 처리
   */
  private handleChitChat(_message: ChatMessage): string {
    const responses = [
      '그렇군요! 😊',
      '재미있네요!',
      '좋은 의견이에요!',
      '감사합니다!',
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }
}
