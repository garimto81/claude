import type { HostProfile } from '../types/host.js';

/**
 * 시스템 프롬프트 빌더
 *
 * 호스트 프로필을 기반으로 LLM에 전달할 시스템 프롬프트를 동적으로 생성합니다.
 */
export class PromptBuilder {
  /**
   * 시스템 프롬프트 생성
   */
  static buildSystemPrompt(
    profile: HostProfile,
    options: {
      maxResponseLength?: number;
      includeProjects?: boolean;
    } = {}
  ): string {
    const { maxResponseLength = 200, includeProjects = true } = options;

    const sections = [
      this.buildRoleSection(profile),
      this.buildHostSection(profile),
      this.buildExpertiseSection(profile),
      includeProjects ? this.buildProjectsSection(profile) : null,
      this.buildConstraintsSection(maxResponseLength),
    ].filter(Boolean);

    return sections.join('\n\n');
  }

  /**
   * 역할 섹션 생성
   */
  private static buildRoleSection(profile: HostProfile): string {
    return `당신은 ${profile.persona.role}입니다.

역할:
- 시청자의 프로그래밍/코딩 질문에 간결하고 정확하게 답변
- 방송 진행 상황 안내
- ${profile.persona.tone}`;
  }

  /**
   * 호스트 정보 섹션
   */
  private static buildHostSection(profile: HostProfile): string {
    const displayName = profile.host.displayName || profile.host.name;
    const bio = profile.host.bio ? `\n${profile.host.bio}` : '';

    let social = '';
    if (profile.social.github) {
      social += `\nGitHub: https://github.com/${profile.social.github}`;
    }

    return `호스트 정보:
- 이름: ${displayName}${bio}${social}`;
  }

  /**
   * 전문 분야 섹션
   */
  private static buildExpertiseSection(profile: HostProfile): string {
    const expertise = profile.persona.expertise
      .map(e => `- ${e}`)
      .join('\n');

    const languages = profile.persona.primaryLanguages.join(', ');

    return `전문 분야:
${expertise}

주요 언어: ${languages}`;
  }

  /**
   * 프로젝트 섹션
   */
  private static buildProjectsSection(profile: HostProfile): string {
    if (profile.projects.length === 0) {
      return '';
    }

    const projectList = profile.projects
      .map(p => {
        const active = p.isActive ? ' (현재 작업 중)' : '';
        const stars = p.stars ? ` ⭐${p.stars}` : '';
        return `- **${p.name}** (v${p.version})${active}${stars}: ${p.description}
  기술: ${p.stack}
  GitHub: https://github.com/${p.repository}`;
      })
      .join('\n\n');

    return `활성 프로젝트:
${projectList}`;
  }

  /**
   * 제약사항 섹션
   */
  private static buildConstraintsSection(maxLength: number): string {
    return `제한사항:
- 답변은 ${maxLength}자 이내 (YouTube 채팅 특성)
- 정치, 종교 등 민감한 주제 회피
- 불확실한 정보는 솔직하게 모른다고 답변`;
  }

  /**
   * 간단한 소개 텍스트 생성 (환영 메시지용)
   */
  static buildGreeting(profile: HostProfile): string {
    const displayName = profile.host.displayName || profile.host.name;
    return `안녕하세요! ${displayName}의 AI Coding 방송에 오신 걸 환영합니다!`;
  }

  /**
   * GitHub 링크 생성
   */
  static getGitHubLink(profile: HostProfile): string {
    if (!profile.social.github) {
      return '호스트 GitHub 정보가 없습니다.';
    }
    return `GitHub: https://github.com/${profile.social.github}`;
  }
}
