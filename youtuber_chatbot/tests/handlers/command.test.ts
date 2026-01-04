import { describe, it, expect, beforeEach, vi } from 'vitest';
import { buildCommandMap, handleCommand } from '../../src/handlers/command.js';
import type { HostProfile } from '../../src/types/host.js';

// config/index.js 모킹
vi.mock('../../src/config/index.js', () => ({
  getHostProfile: vi.fn(() => mockProfile),
}));

// host-profile.js 모킹 (sync-repos 테스트용)
vi.mock('../../src/config/host-profile.js', () => ({
  getHostProfileLoader: vi.fn(() => ({
    mergeGitHubProjects: vi.fn().mockResolvedValue(undefined),
  })),
}));

// github-analyzer.js 모킹
vi.mock('../../src/services/github-analyzer.js', () => ({
  GitHubAnalyzer: vi.fn().mockImplementation(() => ({
    getRecentActiveRepositories: vi.fn().mockResolvedValue([
      {
        name: 'active-repo-1',
        stars: 50,
        stack: 'TypeScript, React',
      },
      {
        name: 'active-repo-2',
        stars: 20,
        stack: 'Python, FastAPI',
      },
    ]),
    getPinnedRepositories: vi.fn().mockResolvedValue([
      {
        id: 'pinned-1',
        name: 'Pinned Repo 1',
        description: 'A pinned repository',
        repository: 'testuser/pinned-1',
        version: '1.0.0',
        stack: 'TypeScript',
      },
    ]),
  })),
}));

const mockProfile: HostProfile = {
  host: {
    name: 'TestHost',
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
      description: 'Test description',
      repository: 'testuser/test-repo',
      version: '1.0.0',
      stack: 'TypeScript',
      stars: 100,
    },
  ],
};

describe('Command Handler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // 환경 변수 설정
    process.env.OLLAMA_MODEL = 'qwen3:8b';
  });

  describe('buildCommandMap', () => {
    it('기본 명령어를 포함해야 함', () => {
      const commands = buildCommandMap();

      expect(commands).toHaveProperty('!help');
      expect(commands).toHaveProperty('!github');
      expect(commands).toHaveProperty('!ai');
      expect(commands).toHaveProperty('!projects');
      expect(commands).toHaveProperty('!sync-repos');
    });

    it('프로젝트별 명령어를 동적으로 생성해야 함', () => {
      const commands = buildCommandMap();

      expect(commands).toHaveProperty('!test-project');
    });
  });

  describe('handleCommand - 기본 명령어', () => {
    it('!help 명령어를 처리해야 함', async () => {
      const result = await handleCommand('!help');

      expect(result).toContain('명령어:');
      expect(result).toContain('!help');
      expect(result).toContain('!projects');
      expect(result).toContain('!test-project');
    });

    it('!github 명령어를 처리해야 함', async () => {
      const result = await handleCommand('!github');

      expect(result).toContain('GitHub:');
      expect(result).toContain('https://github.com/testuser');
    });

    it('!ai 명령어를 처리해야 함', async () => {
      const result = await handleCommand('!ai');

      expect(result).toContain('AI:');
      expect(result).toContain('Qwen 3');
      expect(result).toContain('Ollama');
    });
  });

  describe('handleCommand - 프로젝트 명령어', () => {
    it('프로젝트 명령어를 처리해야 함', async () => {
      const result = await handleCommand('!test-project');

      expect(result).toContain('Test Project');
      expect(result).toContain('v1.0.0');
      expect(result).toContain('⭐100');
      expect(result).toContain('github.com/testuser/test-repo');
    });
  });

  describe('handleCommand - !projects (GitHub API)', () => {
    it('최근 활동 프로젝트를 조회해야 함', async () => {
      const result = await handleCommand('!projects');

      expect(result).toContain('최근 5일간 활동 프로젝트');
      expect(result).toContain('active-repo-1');
      expect(result).toContain('⭐50');
      expect(result).toContain('TypeScript, React');
    });

    it('GitHub 사용자명이 없으면 에러 메시지를 반환해야 함', async () => {
      // 임시로 getHostProfile 모킹 변경
      const { getHostProfile } = await import('../../src/config/index.js');
      vi.mocked(getHostProfile).mockReturnValueOnce({
        ...mockProfile,
        social: {},
      });

      const result = await handleCommand('!projects');

      expect(result).toContain('❌ GitHub 사용자명이 설정되지 않았습니다');
    });
  });

  describe('handleCommand - !sync-repos', () => {
    it('GitHub 레포지토리를 동기화해야 함', async () => {
      const result = await handleCommand('!sync-repos');

      expect(result).toContain('✅ GitHub 레포지토리');
      expect(result).toContain('개 동기화 완료');
    });

    it('GitHub 사용자명이 없으면 에러 메시지를 반환해야 함', async () => {
      // 임시로 getHostProfile 모킹 변경
      const { getHostProfile } = await import('../../src/config/index.js');
      vi.mocked(getHostProfile).mockReturnValueOnce({
        ...mockProfile,
        social: {},
      });

      const result = await handleCommand('!sync-repos');

      expect(result).toContain('❌ GitHub 사용자명이 설정되지 않았습니다');
    });
  });

  describe('handleCommand - 에러 처리', () => {
    it('알 수 없는 명령어에 대해 안내 메시지를 반환해야 함', async () => {
      const result = await handleCommand('!unknown');

      expect(result).toContain('알 수 없는 명령어');
      expect(result).toContain('!help');
    });

    it('대소문자 구분 없이 명령어를 처리해야 함', async () => {
      const result = await handleCommand('!HELP');

      expect(result).toContain('명령어:');
    });
  });
});
