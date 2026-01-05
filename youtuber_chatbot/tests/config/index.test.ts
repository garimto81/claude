import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { HostProfile } from '../../src/types/host.js';

// 모듈 모킹
vi.mock('node:fs', () => ({
  existsSync: vi.fn(),
}));

vi.mock('../../src/config/host-profile.js', () => ({
  HostProfileLoader: {
    getInstance: vi.fn(() => ({
      load: vi.fn(),
    })),
  },
}));

const mockValidProfile: HostProfile = {
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
  projects: [],
};

describe('Config Module', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    // 환경 변수 정리
    delete process.env.HOST_PROFILE_JSON;
    delete process.env.HOST_PROFILE_PATH;
    delete process.env.HOST_NAME;
    delete process.env.HOST_DISPLAY_NAME;
    delete process.env.HOST_BIO;
    delete process.env.GITHUB_USERNAME;
    delete process.env.TWITTER_HANDLE;
    delete process.env.HOST_WEBSITE;
  });

  describe('loadHostProfile', () => {
    it('HOST_PROFILE_JSON 환경 변수에서 프로필을 로드해야 함', async () => {
      process.env.HOST_PROFILE_JSON = JSON.stringify(mockValidProfile);

      const { loadHostProfile } = await import('../../src/config/index.js');
      const profile = await loadHostProfile();

      expect(profile.host.name).toBe('TestHost');
      expect(profile.host.displayName).toBe('Test Display Name');
    });

    it('잘못된 HOST_PROFILE_JSON은 무시하고 다음 단계로 진행해야 함', async () => {
      process.env.HOST_PROFILE_JSON = 'invalid json';
      process.env.HOST_NAME = 'EnvHost';

      const { existsSync } = await import('node:fs');
      vi.mocked(existsSync).mockReturnValue(false);

      const { loadHostProfile } = await import('../../src/config/index.js');
      const profile = await loadHostProfile();

      // fallback으로 환경 변수에서 빌드된 프로필
      expect(profile.host.name).toBe('EnvHost');
    });

    it('환경 변수에서 개별 필드를 조합하여 프로필을 생성해야 함', async () => {
      process.env.HOST_NAME = 'EnvHost';
      process.env.HOST_DISPLAY_NAME = 'Env Display';
      process.env.HOST_BIO = 'Test bio';
      process.env.GITHUB_USERNAME = 'envuser';
      process.env.TWITTER_HANDLE = 'envtwitter';
      process.env.HOST_WEBSITE = 'https://example.com';

      const { existsSync } = await import('node:fs');
      vi.mocked(existsSync).mockReturnValue(false);

      const { loadHostProfile } = await import('../../src/config/index.js');
      const profile = await loadHostProfile();

      expect(profile.host.name).toBe('EnvHost');
      expect(profile.host.displayName).toBe('Env Display');
      expect(profile.host.bio).toBe('Test bio');
      expect(profile.social.github).toBe('envuser');
      expect(profile.social.twitter).toBe('envtwitter');
      expect(profile.social.website).toBe('https://example.com');
    });

    it('환경 변수가 없으면 기본값을 사용해야 함', async () => {
      const { existsSync } = await import('node:fs');
      vi.mocked(existsSync).mockReturnValue(false);

      const { loadHostProfile } = await import('../../src/config/index.js');
      const profile = await loadHostProfile();

      expect(profile.host.name).toBe('Developer');
      expect(profile.host.displayName).toBe('AI Coding Streamer');
      expect(profile.persona.role).toBe('AI 코딩 방송 어시스턴트');
      expect(profile.persona.primaryLanguages).toContain('TypeScript');
      expect(profile.persona.primaryLanguages).toContain('Python');
    });

    it('캐시된 프로필을 반환해야 함', async () => {
      process.env.HOST_PROFILE_JSON = JSON.stringify(mockValidProfile);

      const { loadHostProfile } = await import('../../src/config/index.js');

      const profile1 = await loadHostProfile();
      const profile2 = await loadHostProfile();

      expect(profile1).toBe(profile2); // 동일한 객체 참조
    });
  });

  describe('getHostProfile', () => {
    it('로드된 프로필을 반환해야 함', async () => {
      process.env.HOST_PROFILE_JSON = JSON.stringify(mockValidProfile);

      const { loadHostProfile, getHostProfile } = await import('../../src/config/index.js');
      await loadHostProfile();

      const profile = getHostProfile();
      expect(profile.host.name).toBe('TestHost');
    });

    it('프로필이 로드되지 않은 상태에서 호출하면 에러를 발생시켜야 함', async () => {
      // 새 모듈 인스턴스 가져오기 (캐시 초기화)
      vi.resetModules();
      const { getHostProfile } = await import('../../src/config/index.js');

      expect(() => getHostProfile()).toThrow(
        'Host profile not loaded. Call loadHostProfile() first.',
      );
    });
  });

  describe('refreshHostProfile', () => {
    it('캐시를 무효화하고 새 프로필을 로드해야 함', async () => {
      process.env.HOST_PROFILE_JSON = JSON.stringify(mockValidProfile);

      const { loadHostProfile, refreshHostProfile, getHostProfile } = await import('../../src/config/index.js');

      // 첫 번째 로드
      await loadHostProfile();
      const firstProfile = getHostProfile();

      // 환경 변수 변경
      const updatedProfile = {
        ...mockValidProfile,
        host: { name: 'UpdatedHost' },
      };
      process.env.HOST_PROFILE_JSON = JSON.stringify(updatedProfile);

      // 리프레시
      await refreshHostProfile();
      const refreshedProfile = getHostProfile();

      expect(refreshedProfile.host.name).toBe('UpdatedHost');
      expect(firstProfile).not.toBe(refreshedProfile);
    });
  });
});
