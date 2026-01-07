import type { HostProfile, FAQItem } from '../types/host.js';

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
      includeFaq?: boolean;
      includeDetails?: boolean;
    } = {},
  ): string {
    const {
      maxResponseLength = 200,
      includeProjects = true,
      includeFaq = true,
      includeDetails = true,
    } = options;

    const sections = [
      this.buildRoleSection(profile),
      this.buildHostSection(profile),
      includeDetails ? this.buildDetailsSection(profile) : null,
      this.buildExpertiseSection(profile),
      includeProjects ? this.buildProjectsSection(profile) : null,
      this.buildScheduleSection(profile),
      includeFaq ? this.buildFaqSection(profile) : null,
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
- 시청자의 질문에 호스트 프로필 정보를 기반으로 정확하게 답변
- 프로그래밍/코딩 질문에 간결하고 정확하게 답변
- 방송 진행 상황 안내
- ${profile.persona.tone}`;
  }

  /**
   * 호스트 정보 섹션
   */
  private static buildHostSection(profile: HostProfile): string {
    const displayName = profile.host.displayName || profile.host.name;
    const bio = profile.host.bio ? `\n- 소개: ${profile.host.bio}` : '';

    let social = '';
    if (profile.social.github) {
      social += `\n- GitHub: https://github.com/${profile.social.github}`;
    }
    if (profile.social.youtube) {
      social += `\n- YouTube: ${profile.social.youtube}`;
    }
    if (profile.social.discord) {
      social += `\n- Discord: ${profile.social.discord}`;
    }

    return `## 호스트 정보
- 이름: ${displayName}${bio}${social}`;
  }

  /**
   * 상세 정보 섹션
   */
  private static buildDetailsSection(profile: HostProfile): string | null {
    if (!profile.details) {
      return null;
    }

    const details = profile.details;
    const parts: string[] = ['## 호스트 상세 정보'];

    if (details.aboutMe) {
      parts.push(`자기소개: ${details.aboutMe}`);
    }
    if (details.background) {
      parts.push(`배경: ${details.background}`);
    }
    if (details.currentWork) {
      parts.push(`현재 작업: ${details.currentWork}`);
    }
    if (details.interests && details.interests.length > 0) {
      parts.push(`관심사: ${details.interests.join(', ')}`);
    }
    if (details.equipment && details.equipment.length > 0) {
      parts.push(`사용 도구: ${details.equipment.join(', ')}`);
    }
    if (details.goals) {
      parts.push(`목표: ${details.goals}`);
    }

    return parts.length > 1 ? parts.join('\n') : null;
  }

  /**
   * 전문 분야 섹션
   */
  private static buildExpertiseSection(profile: HostProfile): string {
    const expertise = profile.persona.expertise
      .map(e => `- ${e}`)
      .join('\n');

    const languages = profile.persona.primaryLanguages.join(', ');

    return `## 전문 분야
${expertise}

주요 언어: ${languages}`;
  }

  /**
   * 프로젝트 섹션
   */
  private static buildProjectsSection(profile: HostProfile): string | null {
    if (profile.projects.length === 0) {
      return null;
    }

    const projectList = profile.projects
      .map(p => {
        const active = p.isActive ? ' (현재 작업 중)' : '';
        const stars = p.stars ? ` ⭐${p.stars}` : '';
        const version = p.version ? ` v${p.version}` : '';
        return `- **${p.name}**${version}${active}${stars}: ${p.description}
  기술: ${p.stack || 'N/A'}
  GitHub: https://github.com/${p.repository}`;
      })
      .join('\n\n');

    return `## 활성 프로젝트
${projectList}`;
  }

  /**
   * 방송 일정 섹션
   */
  private static buildScheduleSection(profile: HostProfile): string | null {
    if (!profile.schedule) {
      return null;
    }

    const schedule = profile.schedule;
    const days = schedule.days.join(', ');
    const time = schedule.endTime
      ? `${schedule.startTime} ~ ${schedule.endTime}`
      : `${schedule.startTime}부터`;

    return `## 방송 일정
- 요일: ${days}
- 시간: ${time} (${schedule.timezone || 'KST'})
- ${schedule.description || ''}`;
  }

  /**
   * FAQ 섹션
   */
  private static buildFaqSection(profile: HostProfile): string | null {
    if (!profile.faq || profile.faq.length === 0) {
      return null;
    }

    const faqList = profile.faq
      .map((item, index) => {
        const questions = item.questions.slice(0, 2).join(' / ');
        return `${index + 1}. Q: "${questions}"
   A: ${item.answer}`;
      })
      .join('\n\n');

    return `## 자주 묻는 질문 (FAQ)
아래 질문과 유사한 내용이 들어오면 해당 답변을 참고하세요:

${faqList}`;
  }

  /**
   * 제약사항 섹션
   */
  private static buildConstraintsSection(maxLength: number): string {
    return `## 제한사항
- 답변은 ${maxLength}자 이내 (YouTube 채팅 특성)
- 호스트 프로필에 있는 정보를 우선적으로 활용
- 정치, 종교 등 민감한 주제 회피
- 불확실한 정보는 솔직하게 모른다고 답변
- 이모지를 적절히 사용해서 친근하게 답변`;
  }

  /**
   * FAQ 매칭 - 질문과 가장 유사한 FAQ 찾기
   */
  static matchFaq(message: string, faq: FAQItem[]): FAQItem | null {
    const normalizedMessage = message.toLowerCase().trim();

    for (const item of faq) {
      for (const question of item.questions) {
        const normalizedQuestion = question.toLowerCase().trim();

        // 정확히 일치하거나 포함 관계 확인
        if (
          normalizedMessage === normalizedQuestion ||
          normalizedMessage.includes(normalizedQuestion) ||
          normalizedQuestion.includes(normalizedMessage)
        ) {
          return item;
        }

        // 키워드 기반 매칭 (50% 이상 일치)
        const messageWords = normalizedMessage.split(/\s+/);
        const questionWords = normalizedQuestion.split(/\s+/);
        const matchCount = messageWords.filter(word =>
          questionWords.some(qWord => qWord.includes(word) || word.includes(qWord)),
        ).length;

        if (matchCount >= Math.ceil(questionWords.length * 0.5)) {
          return item;
        }
      }
    }

    return null;
  }

  /**
   * 간단한 소개 텍스트 생성 (환영 메시지용)
   */
  static buildGreeting(profile: HostProfile): string {
    const displayName = profile.host.displayName || profile.host.name;
    return `안녕하세요! ${displayName}의 AI Coding 방송에 오신 걸 환영합니다! 🎉`;
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
