import { describe, it, expect } from 'vitest';
import {
  parseMessage,
  isCommand,
  extractCommand,
  isSpamMessage,
  sanitizeMessage,
} from '../../src/utils/message-parser.js';

describe('Message Parser', () => {
  describe('parseMessage', () => {
    it('일반 메시지를 파싱해야 함', () => {
      const result = parseMessage('안녕하세요!');

      expect(result.raw).toBe('안녕하세요!');
      expect(result.normalized).toBe('안녕하세요!');
      expect(result.command).toBeUndefined();
      expect(result.isGreeting).toBe(true);
      expect(result.isQuestion).toBe(false);
    });

    it('명령어를 파싱해야 함', () => {
      const result = parseMessage('!help');

      expect(result.command).toBe('!help');
      expect(result.args).toEqual([]);
    });

    it('명령어와 인자를 파싱해야 함', () => {
      const result = parseMessage('!search TypeScript tutorial');

      expect(result.command).toBe('!search');
      expect(result.args).toEqual(['typescript', 'tutorial']);
    });

    it('멘션을 감지해야 함', () => {
      const result = parseMessage('@CodingBot 안녕하세요!');

      expect(result.mentions).toContain('CodingBot');
      expect(result.isBotMention).toBe(true);
    });

    it('봇 이름을 감지해야 함', () => {
      const result = parseMessage('bot 질문있어요', 'MyBot');

      expect(result.isBotMention).toBe(true);
    });

    it('질문을 감지해야 함', () => {
      expect(parseMessage('TypeScript는 뭔가요?').isQuestion).toBe(true);
      expect(parseMessage('어떻게 하나요').isQuestion).toBe(true);
      expect(parseMessage('왜 안될까요?').isQuestion).toBe(true);
    });

    it('인사말을 감지해야 함', () => {
      expect(parseMessage('안녕하세요').isGreeting).toBe(true);
      expect(parseMessage('하이~').isGreeting).toBe(true);
      expect(parseMessage('Hello!').isGreeting).toBe(true);
      expect(parseMessage('반갑습니다').isGreeting).toBe(true);
    });

    it('URL을 추출해야 함', () => {
      const result = parseMessage('https://github.com 보세요');

      expect(result.urls).toContain('https://github.com');
    });

    it('이모지를 추출해야 함', () => {
      const result = parseMessage('좋아요! 😀👍');

      expect(result.emojis.length).toBeGreaterThan(0);
    });
  });

  describe('isCommand', () => {
    it('명령어를 인식해야 함', () => {
      expect(isCommand('!help')).toBe(true);
      expect(isCommand('!project')).toBe(true);
    });

    it('일반 메시지는 명령어가 아님', () => {
      expect(isCommand('안녕하세요')).toBe(false);
      expect(isCommand('help')).toBe(false);
    });
  });

  describe('extractCommand', () => {
    it('명령어와 인자를 추출해야 함', () => {
      const result = extractCommand('!help me please');

      expect(result).toEqual({
        command: '!help',
        args: ['me', 'please'],
      });
    });

    it('명령어가 없으면 null 반환', () => {
      expect(extractCommand('안녕')).toBeNull();
    });
  });

  describe('isSpamMessage', () => {
    it('반복 문자를 스팸으로 인식해야 함', () => {
      expect(isSpamMessage('aaaaaaaaaa')).toBe(true);
      expect(isSpamMessage('ㅋㅋㅋㅋㅋㅋㅋ')).toBe(true);
    });

    it('과도한 대문자를 스팸으로 인식해야 함', () => {
      expect(isSpamMessage('THIS IS SPAM MESSAGE')).toBe(true);
    });

    it('스팸 키워드를 감지해야 함', () => {
      expect(isSpamMessage('구독하세요!')).toBe(true);
      expect(isSpamMessage('Subscribe now!')).toBe(true);
    });

    it('과도한 URL을 스팸으로 인식해야 함', () => {
      expect(isSpamMessage('https://a.com https://b.com https://c.com')).toBe(true);
    });

    it('일반 메시지는 스팸이 아님', () => {
      expect(isSpamMessage('안녕하세요!')).toBe(false);
      expect(isSpamMessage('TypeScript 질문있어요')).toBe(false);
    });
  });

  describe('sanitizeMessage', () => {
    it('연속 공백을 정리해야 함', () => {
      expect(sanitizeMessage('안녕   하세요')).toBe('안녕 하세요');
    });

    it('앞뒤 공백을 제거해야 함', () => {
      expect(sanitizeMessage('  안녕하세요  ')).toBe('안녕하세요');
    });
  });
});
