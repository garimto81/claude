import { describe, it, expect } from 'vitest';
import { PromptBuilder } from '../../src/services/prompt-builder.js';
import type { HostProfile } from '../../src/types/host.js';

describe('PromptBuilder', () => {
  const mockProfile: HostProfile = {
    host: {
      name: 'TestHost',
      displayName: 'Test Display Name',
      bio: 'Test bio description',
    },
    persona: {
      role: 'AI Coding Assistant',
      tone: '친절하고 전문적인 톤',
      primaryLanguages: ['TypeScript', 'Python'],
      expertise: ['백엔드 개발', 'AI/ML'],
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
        stack: 'TypeScript, Node.js',
        isActive: true,
        stars: 10,
      },
    ],
    meta: {
      version: '1.0.0',
      lastUpdated: '2024-01-01',
    },
  };

  describe('buildSystemPrompt', () => {
    it('기본 시스템 프롬프트를 생성해야 함', () => {
      const prompt = PromptBuilder.buildSystemPrompt(mockProfile);

      expect(prompt).toContain('AI Coding Assistant');
      expect(prompt).toContain('Test Display Name');
      expect(prompt).toContain('백엔드 개발');
      expect(prompt).toContain('TypeScript, Python');
      expect(prompt).toContain('200자 이내');
    });

    it('프로젝트 정보를 포함해야 함', () => {
      const prompt = PromptBuilder.buildSystemPrompt(mockProfile, {
        includeProjects: true,
      });

      expect(prompt).toContain('Test Project');
      expect(prompt).toContain('testuser/test-repo');
      expect(prompt).toContain('⭐10');
      expect(prompt).toContain('현재 작업 중');
    });

    it('프로젝트 정보를 제외할 수 있어야 함', () => {
      const prompt = PromptBuilder.buildSystemPrompt(mockProfile, {
        includeProjects: false,
      });

      expect(prompt).not.toContain('Test Project');
      expect(prompt).not.toContain('testuser/test-repo');
    });

    it('maxResponseLength 옵션을 적용해야 함', () => {
      const prompt = PromptBuilder.buildSystemPrompt(mockProfile, {
        maxResponseLength: 100,
      });

      expect(prompt).toContain('100자 이내');
    });

    it('GitHub 링크를 포함해야 함', () => {
      const prompt = PromptBuilder.buildSystemPrompt(mockProfile);

      expect(prompt).toContain('GitHub: https://github.com/testuser');
    });
  });

  describe('buildGreeting', () => {
    it('환영 메시지를 생성해야 함', () => {
      const greeting = PromptBuilder.buildGreeting(mockProfile);

      expect(greeting).toContain('Test Display Name');
      expect(greeting).toContain('AI Coding 방송');
      expect(greeting).toContain('환영합니다');
    });

    it('displayName이 없으면 name을 사용해야 함', () => {
      const profileWithoutDisplayName = {
        ...mockProfile,
        host: {
          name: 'TestHost',
        },
      };

      const greeting = PromptBuilder.buildGreeting(profileWithoutDisplayName);

      expect(greeting).toContain('TestHost');
    });
  });

  describe('getGitHubLink', () => {
    it('GitHub 링크를 반환해야 함', () => {
      const link = PromptBuilder.getGitHubLink(mockProfile);

      expect(link).toBe('GitHub: https://github.com/testuser');
    });

    it('GitHub 정보가 없으면 안내 메시지를 반환해야 함', () => {
      const profileWithoutGitHub = {
        ...mockProfile,
        social: {},
      };

      const link = PromptBuilder.getGitHubLink(profileWithoutGitHub);

      expect(link).toBe('호스트 GitHub 정보가 없습니다.');
    });
  });

  describe('Edge Cases', () => {
    it('빈 프로젝트 배열을 처리해야 함', () => {
      const profileWithoutProjects = {
        ...mockProfile,
        projects: [],
      };

      const prompt = PromptBuilder.buildSystemPrompt(profileWithoutProjects);

      expect(prompt).not.toContain('활성 프로젝트');
    });

    it('stars가 없는 프로젝트를 처리해야 함', () => {
      const profileWithoutStars = {
        ...mockProfile,
        projects: [
          {
            ...mockProfile.projects[0],
            stars: undefined,
          },
        ],
      };

      const prompt = PromptBuilder.buildSystemPrompt(profileWithoutStars);

      expect(prompt).not.toContain('⭐');
    });

    it('isActive가 false인 프로젝트를 처리해야 함', () => {
      const profileWithInactiveProject = {
        ...mockProfile,
        projects: [
          {
            ...mockProfile.projects[0],
            isActive: false,
          },
        ],
      };

      const prompt = PromptBuilder.buildSystemPrompt(profileWithInactiveProject);

      expect(prompt).not.toContain('현재 작업 중');
    });
  });
});
