/**
 * Response Formatter Utility
 *
 * AI 응답을 YouTube 채팅에 맞게 포맷팅합니다.
 * - 길이 제한
 * - 줄바꿈 처리
 * - 특수문자 이스케이프
 */

export interface FormatOptions {
  /** 최대 문자 수 */
  maxLength: number;
  /** 줄바꿈을 공백으로 변환 */
  singleLine: boolean;
  /** 말줄임표 추가 */
  addEllipsis: boolean;
  /** 접두사 (봇 이름 등) */
  prefix?: string;
  /** 접미사 */
  suffix?: string;
}

const DEFAULT_OPTIONS: FormatOptions = {
  maxLength: parseInt(process.env.MAX_RESPONSE_LENGTH || '200', 10),
  singleLine: true,
  addEllipsis: true,
};

/**
 * 응답 포맷팅
 */
export function formatResponse(response: string, options: Partial<FormatOptions> = {}): string {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  let formatted = response.trim();

  // 줄바꿈 처리
  if (opts.singleLine) {
    formatted = formatted.replace(/\n+/g, ' ').replace(/\s+/g, ' ');
  }

  // 접두사/접미사 길이 계산
  const prefixLength = opts.prefix ? opts.prefix.length + 1 : 0;
  const suffixLength = opts.suffix ? opts.suffix.length + 1 : 0;
  const ellipsisLength = opts.addEllipsis ? 3 : 0;

  const availableLength = opts.maxLength - prefixLength - suffixLength - ellipsisLength;

  // 길이 제한
  if (formatted.length > availableLength) {
    formatted = formatted.substring(0, availableLength).trim();
    if (opts.addEllipsis) {
      formatted += '...';
    }
  }

  // 접두사/접미사 추가
  if (opts.prefix) {
    formatted = `${opts.prefix} ${formatted}`;
  }
  if (opts.suffix) {
    formatted = `${formatted} ${opts.suffix}`;
  }

  return formatted;
}

/**
 * 에러 응답 포맷팅
 */
export function formatErrorResponse(error: string | Error): string {
  const message = error instanceof Error ? error.message : error;
  return formatResponse(`죄송합니다, 오류가 발생했습니다: ${message}`, {
    maxLength: 150,
  });
}

/**
 * 명령어 응답 포맷팅
 */
export function formatCommandResponse(response: string): string {
  return formatResponse(response, {
    maxLength: 300,  // 명령어 응답은 조금 더 길게 허용
    singleLine: false,  // 줄바꿈 유지
  });
}

/**
 * 인사말 응답 포맷팅
 */
export function formatGreetingResponse(username: string, greeting: string): string {
  return formatResponse(greeting, {
    prefix: `@${username}`,
    maxLength: 150,
  });
}

/**
 * 코드 블록 처리 (YouTube 채팅에서 코드 블록 미지원)
 */
export function formatCodeInResponse(response: string): string {
  let formatted = response;

  // 멀티라인 코드 블록 먼저 처리 (```...```)
  formatted = formatted.replace(/```(\w*)\n?([\s\S]*?)```/g, (_match, _lang, code) => {
    const trimmedCode = code.trim();
    const firstLine = trimmedCode.split('\n')[0];
    return `[코드: ${firstLine}${trimmedCode.includes('\n') ? '...' : ''}]`;
  });

  // 인라인 코드 블록 처리: `code` → code
  formatted = formatted.replace(/`([^`]+)`/g, '$1');

  return formatted;
}

/**
 * 마크다운 제거
 */
export function stripMarkdown(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1')  // **bold**
    .replace(/\*([^*]+)\*/g, '$1')       // *italic*
    .replace(/__([^_]+)__/g, '$1')       // __underline__
    .replace(/_([^_]+)_/g, '$1')         // _italic_
    .replace(/~~([^~]+)~~/g, '$1')       // ~~strikethrough~~
    .replace(/`([^`]+)`/g, '$1')         // `code`
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // [link](url)
    .replace(/^#+\s*/gm, '')             // # headers
    .replace(/^>\s*/gm, '')              // > quotes
    .replace(/^[-*]\s*/gm, '')           // - lists
    .replace(/^\d+\.\s*/gm, '');         // 1. numbered lists
}

/**
 * 응답 완전 정제 (AI 응답 → YouTube 채팅)
 */
export function sanitizeAIResponse(response: string): string {
  let sanitized = response;

  // 마크다운 제거
  sanitized = stripMarkdown(sanitized);

  // 코드 블록 처리
  sanitized = formatCodeInResponse(sanitized);

  // 연속 공백 제거
  sanitized = sanitized.replace(/\s+/g, ' ').trim();

  return sanitized;
}

/**
 * 응답 분할 (긴 응답을 여러 메시지로)
 */
export function splitResponse(response: string, maxLength = 200): string[] {
  if (response.length <= maxLength) {
    return [response];
  }

  const messages: string[] = [];
  let remaining = response;

  while (remaining.length > 0) {
    if (remaining.length <= maxLength) {
      messages.push(remaining);
      break;
    }

    // 문장 경계에서 분할 시도
    let splitIndex = remaining.lastIndexOf('. ', maxLength);
    if (splitIndex === -1 || splitIndex < maxLength / 2) {
      // 공백에서 분할
      splitIndex = remaining.lastIndexOf(' ', maxLength);
    }
    if (splitIndex === -1) {
      // 강제 분할
      splitIndex = maxLength;
    }

    messages.push(remaining.substring(0, splitIndex + 1).trim());
    remaining = remaining.substring(splitIndex + 1).trim();
  }

  // 메시지 번호 추가 (2개 이상인 경우)
  if (messages.length > 1) {
    return messages.map((msg, i) => `(${i + 1}/${messages.length}) ${msg}`);
  }

  return messages;
}
