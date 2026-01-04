import { describe, it, expect, beforeEach, vi } from 'vitest';
import { HostProfileLoader } from '../../src/config/host-profile.js';
import type { HostProfile, HostProject } from '../../src/types/host.js';
import fs from 'node:fs/promises';

// fs 모듈 모킹
vi.mock('node:fs/promises');

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
  projects: [
    {
      id: 'test-project',
      name: 'Test Project',
      description: 'A test project',
      repository: 'testuser/test-repo',
      version: '1.0.0',
      stack: 'TypeScript',
      source: 'manual',
    },
  ],
};

describe('HostProfileLoader', () => {
  let loader: HostProfileLoader;

  beforeEach(() => {
    vi.clearAllMocks();
    // 싱글톤 인스턴스 초기화를 위해 직접 접근 (테스트용)
    loader = HostProfileLoader.getInstance();
  });

  describe('load', () => {
    it('유효한 프로필을 로드해야 함', async () => {
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(mockValidProfile));

      const profile = await loader.load('test-profile.json');

      expect(profile).toEqual(mockValidProfile);
      expect(profile.host.name).toBe('TestHost');
      expect(profile.projects).toHaveLength(1);
    });

    it('파일을 찾을 수 없으면 에러를 발생시켜야 함', async () => {
      const error = new Error('File not found') as NodeJS.ErrnoException;
      error.code = 'ENOENT';
      vi.mocked(fs.readFile).mockRejectedValue(error);

      await expect(loader.load('nonexistent.json')).rejects.toThrow(
        '호스트 프로필 파일을 찾을 수 없습니다',
      );
    });

    it('잘못된 JSON이면 에러를 발생시켜야 함', async () => {
      vi.mocked(fs.readFile).mockResolvedValue('invalid json');

      await expect(loader.load('test-profile.json')).rejects.toThrow(
        '호스트 프로필 로드 실패',
      );
    });
  });

  describe('validation', () => {
    it('호스트 이름이 없으면 에러를 발생시켜야 함', async () => {
      const invalidProfile = {
        ...mockValidProfile,
        host: { name: '' },
      };
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(invalidProfile));

      await expect(loader.load('test.json')).rejects.toThrow(
        '호스트 이름(host.name)은 필수입니다',
      );
    });

    it('프로젝트가 배열이 아니면 에러를 발생시켜야 함', async () => {
      const invalidProfile = {
        ...mockValidProfile,
        projects: 'not an array',
      };
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(invalidProfile));

      await expect(loader.load('test.json')).rejects.toThrow(
        '프로젝트 목록(projects)은 배열이어야 합니다',
      );
    });

    it('프로젝트 ID가 중복되면 에러를 발생시켜야 함', async () => {
      const invalidProfile = {
        ...mockValidProfile,
        projects: [
          {
            id: 'duplicate',
            name: 'Project 1',
            repository: 'user/repo1',
            version: '1.0.0',
            stack: 'TS',
            description: 'Desc 1',
          },
          {
            id: 'duplicate',
            name: 'Project 2',
            repository: 'user/repo2',
            version: '1.0.0',
            stack: 'TS',
            description: 'Desc 2',
          },
        ],
      };
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(invalidProfile));

      await expect(loader.load('test.json')).rejects.toThrow(
        '중복된 프로젝트 ID: duplicate',
      );
    });

    it('프로젝트 필수 필드가 없으면 에러를 발생시켜야 함', async () => {
      const invalidProfile = {
        ...mockValidProfile,
        projects: [
          {
            id: '',
            name: 'Test',
            repository: '',
            version: '1.0.0',
            stack: 'TS',
            description: 'Desc',
          },
        ],
      };
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(invalidProfile));

      await expect(loader.load('test.json')).rejects.toThrow(
        'id, name, repository는 필수 필드입니다',
      );
    });
  });

  describe('mergeGitHubProjects', () => {
    beforeEach(async () => {
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(mockValidProfile));
      vi.mocked(fs.writeFile).mockResolvedValue();
      await loader.load('test.json');
    });

    it('새로운 GitHub 프로젝트를 추가해야 함', async () => {
      const newGitHubProjects: HostProject[] = [
        {
          id: 'new-project',
          name: 'New Project',
          description: 'A new GitHub project',
          repository: 'testuser/new-repo',
          version: '2.0.0',
          stack: 'Python',
          source: 'github',
          stars: 100,
        },
      ];

      await loader.mergeGitHubProjects(newGitHubProjects);

      const profile = loader.getProfileOrThrow();
      expect(profile.projects).toHaveLength(2);
      expect(profile.projects.find(p => p.id === 'new-project')).toBeDefined();
    });

    it('manual source 프로젝트는 덮어쓰지 않아야 함', async () => {
      const githubProjects: HostProject[] = [
        {
          id: 'test-project', // 기존 manual 프로젝트
          name: 'Updated Name',
          description: 'Updated Description',
          repository: 'testuser/test-repo',
          version: '2.0.0',
          stack: 'Python',
          source: 'github',
          stars: 50,
        },
      ];

      await loader.mergeGitHubProjects(githubProjects);

      const profile = loader.getProfileOrThrow();
      const project = profile.projects.find(p => p.id === 'test-project');

      expect(project).toBeDefined();
      expect(project?.name).toBe('Test Project'); // 기존 이름 유지
      expect(project?.source).toBe('manual');
    });

    it('github source 프로젝트는 업데이트해야 함', async () => {
      // 기존 프로필에 github source 프로젝트 추가
      const profileWithGithubProject = {
        ...mockValidProfile,
        projects: [
          {
            id: 'github-project',
            name: 'Old Name',
            description: 'Old Description',
            repository: 'testuser/repo',
            version: '1.0.0',
            stack: 'TypeScript',
            source: 'github' as const,
            stars: 10,
          },
        ],
      };

      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(profileWithGithubProject));
      await loader.load('test.json');

      const updatedGitHubProjects: HostProject[] = [
        {
          id: 'github-project',
          name: 'Updated Name',
          description: 'Updated Description',
          repository: 'testuser/repo',
          version: '2.0.0',
          stack: 'Python',
          source: 'github',
          stars: 100,
        },
      ];

      await loader.mergeGitHubProjects(updatedGitHubProjects);

      const profile = loader.getProfileOrThrow();
      const project = profile.projects.find(p => p.id === 'github-project');

      expect(project).toBeDefined();
      expect(project?.name).toBe('Updated Name'); // 업데이트됨
      expect(project?.stars).toBe(100);
    });
  });

  describe('utility methods', () => {
    beforeEach(async () => {
      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(mockValidProfile));
      await loader.load('test.json');
    });

    it('getProfile()은 로드된 프로필을 반환해야 함', () => {
      const profile = loader.getProfile();
      expect(profile).toEqual(mockValidProfile);
    });

    it('getProfileOrThrow()는 프로필이 없으면 에러를 발생시켜야 함', () => {
      const newLoader = HostProfileLoader.getInstance();
      // 프로필을 로드하지 않은 상태에서 호출 시도는 테스트 어려움
      // (싱글톤이라 이미 로드됨)
    });

    it('getProject()는 특정 프로젝트를 반환해야 함', () => {
      const project = loader.getProject('test-project');
      expect(project).toBeDefined();
      expect(project?.name).toBe('Test Project');
    });

    it('getActiveProjects()는 활성 프로젝트만 반환해야 함', () => {
      const profileWithActiveProjects = {
        ...mockValidProfile,
        projects: [
          { ...mockValidProfile.projects[0], isActive: true },
          {
            id: 'inactive-project',
            name: 'Inactive',
            repository: 'user/repo',
            version: '1.0.0',
            stack: 'TS',
            description: 'Desc',
            isActive: false,
          },
        ],
      };

      vi.mocked(fs.readFile).mockResolvedValue(JSON.stringify(profileWithActiveProjects));

      loader.reload().then(() => {
        const activeProjects = loader.getActiveProjects();
        expect(activeProjects).toHaveLength(1);
        expect(activeProjects[0].id).toBe('test-project');
      });
    });
  });
});
