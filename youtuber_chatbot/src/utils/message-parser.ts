/**
 * Message Parser Utility
 *
 * YouTube 채팅 메시지를 파싱하고 분석합니다.
 * - 명령어 추출
 * - 멘션 감지
 * - 이모지/특수문자 처리
 */

export interface ParsedMessage {
  /** 원본 메시지 */
  raw: string;
  /** 정규화된 메시지 (소문자, 공백 정리) */
  normalized: string;
  /** 명령어 (있는 경우) */
  command?: string;
  /** 명령어 인자 */
  args?: string[];
  /** 멘션된 사용자 목록 */
  mentions: string[];
  /** 봇 멘션 여부 */
  isBotMention: boolean;
  /** 질문 형태 여부 */
  isQuestion: boolean;
  /** 인사말 여부 */
  isGreeting: boolean;
  /** 이모지 목록 */
  emojis: string[];
  /** URL 목록 */
  urls: string[];
}

const COMMAND_PREFIX = '!';
const BOT_NAMES = ['codingbot', 'bot', '봇', 'ai'];
const GREETING_PATTERNS = [
  /^안녕/,
  /^하이/,
  /^헬로/,
  /^hi\b/i,
  /^hello\b/i,
  /^hey\b/i,
  /반갑/,
  /처음/,
];
const QUESTION_PATTERNS = [
  /\?$/,
  /인가요/,
  /인가요\?/,
  /할까요/,
  /뭐예요/,
  /뭔가요/,
  /어떻게/,
  /왜\s/,
  /뭐가/,
  /무엇/,
  /어디/,
  /언제/,
  /누가/,
];

// 이모지 정규식 (기본적인 유니코드 이모지)
const EMOJI_REGEX = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FA6F}]|[\u{1FA70}-\u{1FAFF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;

// URL 정규식
const URL_REGEX = /https?:\/\/[^\s]+/gi;

// 멘션 정규식 (@username)
const MENTION_REGEX = /@(\w+)/g;

/**
 * 메시지 파싱
 */
export function parseMessage(message: string, botName?: string): ParsedMessage {
  const raw = message;
  const normalized = message.toLowerCase().trim();

  // 명령어 추출
  let command: string | undefined;
  let args: string[] | undefined;
  if (normalized.startsWith(COMMAND_PREFIX)) {
    const parts = normalized.slice(1).split(/\s+/);
    command = COMMAND_PREFIX + parts[0];
    args = parts.slice(1);
  }

  // 멘션 추출
  const mentions: string[] = [];
  let match;
  while ((match = MENTION_REGEX.exec(message)) !== null) {
    mentions.push(match[1]);
  }

  // 봇 멘션 확인
  const botNamesToCheck = botName
    ? [...BOT_NAMES, botName.toLowerCase()]
    : BOT_NAMES;
  const isBotMention = mentions.some(m =>
    botNamesToCheck.includes(m.toLowerCase()),
  ) || botNamesToCheck.some(name => normalized.includes(name));

  // 질문 여부 확인
  const isQuestion = QUESTION_PATTERNS.some(pattern => pattern.test(normalized));

  // 인사말 여부 확인
  const isGreeting = GREETING_PATTERNS.some(pattern => pattern.test(normalized));

  // 이모지 추출
  const emojis = message.match(EMOJI_REGEX) || [];

  // URL 추출
  const urls = message.match(URL_REGEX) || [];

  return {
    raw,
    normalized,
    command,
    args,
    mentions,
    isBotMention,
    isQuestion,
    isGreeting,
    emojis,
    urls,
  };
}

/**
 * 명령어인지 확인
 */
export function isCommand(message: string): boolean {
  return message.trim().startsWith(COMMAND_PREFIX);
}

/**
 * 명령어 추출
 */
export function extractCommand(message: string): { command: string; args: string[] } | null {
  if (!isCommand(message)) {
    return null;
  }

  const parts = message.trim().slice(1).split(/\s+/);
  return {
    command: COMMAND_PREFIX + parts[0].toLowerCase(),
    args: parts.slice(1),
  };
}

/**
 * 스팸 메시지 감지 (기본적인 휴리스틱)
 */
export function isSpamMessage(message: string): boolean {
  const normalized = message.toLowerCase();

  // 과도한 반복 문자
  if (/(.)\1{5,}/.test(message)) {
    return true;
  }

  // 과도한 대문자
  const upperCount = (message.match(/[A-Z]/g) || []).length;
  if (message.length > 10 && upperCount / message.length > 0.7) {
    return true;
  }

  // 스팸 키워드
  const spamKeywords = ['구독', '좋아요', 'subscribe', 'follow', '광고', 'ad'];
  if (spamKeywords.some(keyword => normalized.includes(keyword))) {
    return true;
  }

  // 과도한 URL
  const urls = message.match(URL_REGEX) || [];
  if (urls.length > 2) {
    return true;
  }

  return false;
}

/**
 * 메시지 정제 (특수문자, 과도한 공백 제거)
 */
export function sanitizeMessage(message: string): string {
  return message
    .replace(/\s+/g, ' ')  // 연속 공백을 단일 공백으로
    .trim();
}
