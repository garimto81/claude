/**
 * Config Module
 *
 * 호스트 프로필을 로드하고 관리하는 설정 모듈입니다.
 */

import { existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { HostProfile } from '../types/host.js';
import { HostProfileLoader } from './host-profile.js';

// ESM에서 __dirname 대체
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 기본 프로필 경로
const DEFAULT_PROFILE_PATH = join(__dirname, '..', '..', 'config', 'host-profile.json');

// 싱글톤 캐시
let cachedProfile: HostProfile | null = null;

/**
 * 호스트 프로필 로드 (비동기)
 *
 * 앱 시작 시 최초 1회 호출합니다.
 * 1. 환경 변수 HOST_PROFILE_JSON에서 직접 로드
 * 2. 환경 변수 HOST_PROFILE_PATH에서 경로 지정
 * 3. 기본 경로 config/host-profile.json
 * 4. 환경 변수에서 개별 필드 조합
 */
export async function loadHostProfile(): Promise<HostProfile> {
  if (cachedProfile) {
    return cachedProfile;
  }

  // 1. 환경 변수에서 직접 JSON 로드
  if (process.env.HOST_PROFILE_JSON) {
    try {
      cachedProfile = JSON.parse(process.env.HOST_PROFILE_JSON);
      console.log('[Config] Host profile loaded from HOST_PROFILE_JSON');
      return cachedProfile!;
    } catch (error) {
      console.warn('[Config] Failed to parse HOST_PROFILE_JSON:', error);
    }
  }

  // 2. 환경 변수에서 경로 지정
  const profilePath = process.env.HOST_PROFILE_PATH || DEFAULT_PROFILE_PATH;

  // 3. 파일에서 로드
  if (existsSync(profilePath)) {
    try {
      const loader = HostProfileLoader.getInstance();
      cachedProfile = await loader.load(profilePath);
      console.log(`[Config] Host profile loaded from ${profilePath}`);
      return cachedProfile;
    } catch (error) {
      console.warn('[Config] Failed to load profile file:', error);
    }
  }

  // 4. 환경 변수에서 개별 필드 조합 (기본값)
  cachedProfile = buildFromEnv();
  console.log('[Config] Host profile built from environment variables');

  return cachedProfile;
}

/**
 * 환경 변수에서 프로필 구성
 */
function buildFromEnv(): HostProfile {
  return {
    host: {
      name: process.env.HOST_NAME || 'Developer',
      displayName: process.env.HOST_DISPLAY_NAME || 'AI Coding Streamer',
      bio: process.env.HOST_BIO || '코딩과 AI를 사랑하는 개발자입니다.',
    },
    persona: {
      role: 'AI 코딩 방송 어시스턴트',
      tone: '친절하고 전문적인 말투로 답변합니다.',
      primaryLanguages: ['TypeScript', 'Python'],
      expertise: ['웹 개발', 'AI/ML', '클라우드'],
    },
    social: {
      github: process.env.GITHUB_USERNAME || undefined,
      twitter: process.env.TWITTER_HANDLE || undefined,
      website: process.env.HOST_WEBSITE || undefined,
    },
    projects: [],
    meta: {
      version: '1.0.0',
      lastUpdated: new Date().toISOString(),
    },
  };
}

/**
 * 호스트 프로필 조회 (동기)
 *
 * loadHostProfile()가 먼저 호출되어야 합니다.
 * @throws 프로필이 로드되지 않은 경우 에러
 */
export function getHostProfile(): HostProfile {
  if (!cachedProfile) {
    throw new Error(
      'Host profile not loaded. Call loadHostProfile() first.',
    );
  }
  return cachedProfile;
}

/**
 * 프로필 캐시 갱신
 */
export async function refreshHostProfile(): Promise<HostProfile> {
  cachedProfile = null;
  return loadHostProfile();
}

/**
 * 프로필 로더 인스턴스 반환
 */
export function getProfileLoader(): HostProfileLoader {
  return HostProfileLoader.getInstance();
}
