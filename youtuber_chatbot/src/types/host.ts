/**
 * 호스트 프로필 타입 정의
 *
 * 이 파일은 챗봇이 참조하는 호스트(스트리머) 정보의 타입을 정의합니다.
 */

export interface HostProject {
  /** 프로젝트 내부 식별자 (명령어에 사용) */
  id: string;
  /** 프로젝트 표시 이름 */
  name: string;
  /** 프로젝트 설명 (1-2줄) */
  description: string;
  /** GitHub 레포지토리 (owner/repo 형식) */
  repository: string;
  /** 프로젝트 버전 */
  version: string;
  /** 기술 스택 (쉼표 구분 문자열) */
  stack: string;
  /** 프로젝트 URL (선택) */
  url?: string;
  /** 현재 활성 프로젝트 여부 */
  isActive?: boolean;

  // GitHub 동기화 관련 필드
  /** 프로젝트 출처 (manual: 수동 추가, github: GitHub API) */
  source?: 'manual' | 'github';
  /** 마지막 동기화 시간 (ISO 8601) */
  lastSyncedAt?: string;
  /** GitHub Stars */
  stars?: number;
  /** GitHub Topics */
  topics?: string[];
  /** 프로젝트 홈페이지 */
  homepage?: string;
}

export interface HostSocialLinks {
  /** GitHub 사용자명 */
  github?: string;
  /** Twitter 핸들 */
  twitter?: string;
  /** LinkedIn URL */
  linkedin?: string;
  /** 개인 웹사이트 */
  website?: string;
  /** Discord 서버 초대 링크 */
  discord?: string;
  /** YouTube 채널 URL */
  youtube?: string;
}

export interface HostPersona {
  /** 챗봇 페르소나 설명 */
  role: string;
  /** 말투/톤 설명 */
  tone: string;
  /** 주요 언어 */
  primaryLanguages: string[];
  /** 전문 분야 */
  expertise: string[];
}

/** FAQ 항목 */
export interface FAQItem {
  /** 질문 (여러 변형 가능) */
  questions: string[];
  /** 답변 */
  answer: string;
  /** 카테고리 (선택) */
  category?: string;
}

/** 방송 일정 */
export interface StreamSchedule {
  /** 요일 (월, 화, 수, 목, 금, 토, 일) */
  days: string[];
  /** 시작 시간 (HH:MM 형식) */
  startTime: string;
  /** 종료 시간 (HH:MM 형식) */
  endTime?: string;
  /** 타임존 */
  timezone?: string;
  /** 설명 */
  description?: string;
}

/** 호스트 상세 정보 */
export interface HostDetails {
  /** 상세 자기소개 */
  aboutMe?: string;
  /** 경력/배경 */
  background?: string;
  /** 현재 하고 있는 일 */
  currentWork?: string;
  /** 관심사/취미 */
  interests?: string[];
  /** 사용하는 장비/도구 */
  equipment?: string[];
  /** 목표/비전 */
  goals?: string;
}

export interface HostProfile {
  /** 호스트 기본 정보 */
  host: {
    /** 호스트 이름/닉네임 */
    name: string;
    /** 호스트 표시 이름 (실제 이름 또는 브랜드명) */
    displayName?: string;
    /** 자기소개 (1-2줄) */
    bio?: string;
  };

  /** 챗봇 페르소나 */
  persona: HostPersona;

  /** 소셜 링크 */
  social: HostSocialLinks;

  /** 활성 프로젝트 목록 */
  projects: HostProject[];

  /** 호스트 상세 정보 (선택) */
  details?: HostDetails;

  /** 자주 묻는 질문 (선택) */
  faq?: FAQItem[];

  /** 방송 일정 (선택) */
  schedule?: StreamSchedule;

  /** 메타데이터 */
  meta?: {
    /** 프로필 버전 */
    version: string;
    /** 마지막 업데이트 */
    lastUpdated: string;
  };
}

/**
 * 호스트 프로필 검증 옵션
 */
export interface HostProfileValidationOptions {
  /** 필수 필드 검증 */
  requireName?: boolean;
  /** 프로젝트 최소 개수 */
  minProjects?: number;
  /** 프로젝트 최대 개수 */
  maxProjects?: number;
}
