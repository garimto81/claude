import { describe, it, expect } from 'vitest';
import {
  formatResponse,
  formatErrorResponse,
  formatCommandResponse,
  formatGreetingResponse,
  formatCodeInResponse,
  stripMarkdown,
  sanitizeAIResponse,
  splitResponse,
} from '../../src/utils/response-formatter.js';

describe('Response Formatter', () => {
  describe('formatResponse', () => {
    it('기본 포맷팅을 적용해야 함', () => {
      const result = formatResponse('안녕하세요!');
      expect(result).toBe('안녕하세요!');
    });

    it('길이 제한을 적용해야 함', () => {
      const longText = 'a'.repeat(300);
      const result = formatResponse(longText, { maxLength: 100 });

      expect(result.length).toBeLessThanOrEqual(100);
      expect(result.endsWith('...')).toBe(true);
    });

    it('줄바꿈을 공백으로 변환해야 함', () => {
      const result = formatResponse('첫째줄\n둘째줄\n셋째줄', { singleLine: true });
      expect(result).toBe('첫째줄 둘째줄 셋째줄');
    });

    it('접두사를 추가해야 함', () => {
      const result = formatResponse('안녕!', { prefix: '@user' });
      expect(result).toBe('@user 안녕!');
    });

    it('접미사를 추가해야 함', () => {
      const result = formatResponse('안녕!', { suffix: '(by bot)' });
      expect(result).toBe('안녕! (by bot)');
    });

    it('말줄임표 없이 포맷팅할 수 있어야 함', () => {
      const longText = 'a'.repeat(50);
      const result = formatResponse(longText, { maxLength: 20, addEllipsis: false });

      expect(result.endsWith('...')).toBe(false);
      expect(result.length).toBe(20);
    });
  });

  describe('formatErrorResponse', () => {
    it('에러 메시지를 포맷팅해야 함', () => {
      const result = formatErrorResponse('연결 실패');
      expect(result).toContain('오류');
      expect(result).toContain('연결 실패');
    });

    it('Error 객체를 처리해야 함', () => {
      const result = formatErrorResponse(new Error('테스트 에러'));
      expect(result).toContain('테스트 에러');
    });
  });

  describe('formatCommandResponse', () => {
    it('명령어 응답을 포맷팅해야 함', () => {
      const result = formatCommandResponse('프로젝트 목록:\n- A\n- B');
      expect(result).toContain('프로젝트 목록');
      expect(result).toContain('\n'); // 줄바꿈 유지
    });
  });

  describe('formatGreetingResponse', () => {
    it('멘션과 함께 인사말을 포맷팅해야 함', () => {
      const result = formatGreetingResponse('TestUser', '환영합니다!');
      expect(result).toBe('@TestUser 환영합니다!');
    });
  });

  describe('formatCodeInResponse', () => {
    it('인라인 코드를 처리해야 함', () => {
      const result = formatCodeInResponse('`console.log()` 함수를 사용하세요');
      expect(result).toBe('console.log() 함수를 사용하세요');
    });

    it('코드 블록을 처리해야 함', () => {
      const result = formatCodeInResponse('코드:\n```javascript\nconsole.log("hi")\nreturn true\n```');
      expect(result).toContain('[코드:');
      expect(result).not.toContain('```');
    });
  });

  describe('stripMarkdown', () => {
    it('볼드 마크다운을 제거해야 함', () => {
      expect(stripMarkdown('**굵은글씨**')).toBe('굵은글씨');
    });

    it('이탤릭 마크다운을 제거해야 함', () => {
      expect(stripMarkdown('*기울임*')).toBe('기울임');
      expect(stripMarkdown('_기울임_')).toBe('기울임');
    });

    it('링크 마크다운을 제거해야 함', () => {
      expect(stripMarkdown('[링크](https://example.com)')).toBe('링크');
    });

    it('헤더 마크다운을 제거해야 함', () => {
      expect(stripMarkdown('# 제목')).toBe('제목');
      expect(stripMarkdown('## 부제목')).toBe('부제목');
    });

    it('인용 마크다운을 제거해야 함', () => {
      expect(stripMarkdown('> 인용문')).toBe('인용문');
    });
  });

  describe('sanitizeAIResponse', () => {
    it('AI 응답을 완전히 정제해야 함', () => {
      const aiResponse = '**굵은글씨**와 `코드`가 있는 응답\n\n다음 줄';
      const result = sanitizeAIResponse(aiResponse);

      expect(result).not.toContain('**');
      expect(result).not.toContain('`');
      expect(result).not.toContain('\n\n');
    });
  });

  describe('splitResponse', () => {
    it('짧은 응답은 분할하지 않아야 함', () => {
      const result = splitResponse('짧은 응답');
      expect(result).toEqual(['짧은 응답']);
    });

    it('긴 응답을 분할해야 함', () => {
      const longText = '이것은 매우 긴 응답입니다. '.repeat(20);
      const result = splitResponse(longText, 50);

      expect(result.length).toBeGreaterThan(1);
      result.forEach(msg => {
        expect(msg.length).toBeLessThanOrEqual(60); // 번호 포함
      });
    });

    it('분할된 메시지에 번호를 추가해야 함', () => {
      const longText = '긴 문장입니다. '.repeat(30);
      const result = splitResponse(longText, 50);

      expect(result[0]).toMatch(/^\(1\/\d+\)/);
      expect(result[1]).toMatch(/^\(2\/\d+\)/);
    });

    it('문장 경계에서 분할을 시도해야 함', () => {
      const text = '첫 번째 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다.';
      const result = splitResponse(text, 30);

      // 문장이 중간에 잘리지 않도록
      expect(result[0]).toContain('.');
    });
  });
});
