import { getHostProfile } from '../config/index.js';
import { getHostProfileLoader } from '../config/host-profile.js';
import { GitHubAnalyzer } from '../services/github-analyzer.js';
import { PromptBuilder } from '../services/prompt-builder.js';

/**
 * 동적 명령어 맵 생성
 *
 * 호스트 프로필을 기반으로 프로젝트별 명령어를 자동 생성합니다.
 */
export function buildCommandMap(): Record<string, () => string | Promise<string>> {
  const profile = getHostProfile();

  // 기본 명령어
  const baseCommands: Record<string, () => string | Promise<string>> = {
    '!help': () => {
      const projectCommands = profile.projects
        .map(p => `!${p.id}`)
        .join(', ');
      return `명령어: !help, !projects, !github, !ai, !sync-repos${projectCommands ? ', ' + projectCommands : ''}`;
    },

    '!github': () => PromptBuilder.getGitHubLink(profile),

    '!ai': () => `AI: Qwen 3 (${process.env.OLLAMA_MODEL || '8B'}) - Ollama 로컬 실행`,

    '!projects': async () => {
      try {
        if (!profile.social.github) {
          return '❌ GitHub 사용자명이 설정되지 않았습니다.';
        }

        const analyzer = new GitHubAnalyzer(
          profile.social.github,
          process.env.GITHUB_TOKEN,
        );

        // 최근 5일간 활동이 있는 레포 조회
        const activeRepos = await analyzer.getRecentActiveRepositories(5);

        if (activeRepos.length === 0) {
          return '📭 최근 5일간 활동이 있는 프로젝트가 없습니다.';
        }

        const projectList = activeRepos
          .slice(0, 10) // 최대 10개만 표시
          .map(p => {
            const stars = p.stars ? ` ⭐${p.stars}` : '';
            return `- ${p.name}${stars} (${p.stack})`;
          })
          .join('\n');

        return `📊 최근 5일간 활동 프로젝트 (${activeRepos.length}개):\n${projectList}`;
      } catch (error) {
        console.error('[Command] projects error:', error);
        return `❌ GitHub 조회 실패: ${(error as Error).message}`;
      }
    },

    // GitHub 동기화 명령어
    '!sync-repos': async () => {
      try {
        if (!profile.social.github) {
          return '❌ GitHub 사용자명이 설정되지 않았습니다.';
        }

        const loader = getHostProfileLoader();
        const analyzer = new GitHubAnalyzer(
          profile.social.github,
          process.env.GITHUB_TOKEN,
        );

        // Pinned repos 조회
        const pinnedRepos = await analyzer.getPinnedRepositories();

        // 프로필에 병합
        await loader.mergeGitHubProjects(pinnedRepos);

        return `✅ GitHub 레포지토리 ${pinnedRepos.length}개 동기화 완료!`;
      } catch (error) {
        console.error('[Command] sync-repos error:', error);
        return `❌ 동기화 실패: ${(error as Error).message}`;
      }
    },
  };

  // 프로젝트별 명령어 동적 생성
  const projectCommands: Record<string, () => string> = {};
  profile.projects.forEach(p => {
    const stars = p.stars ? ` ⭐${p.stars}` : '';
    projectCommands[`!${p.id}`] = () =>
      `${p.name} v${p.version}${stars} - ${p.description} | github.com/${p.repository}`;
  });

  return { ...baseCommands, ...projectCommands };
}

/**
 * 명령어 처리 핸들러
 */
export async function handleCommand(command: string): Promise<string> {
  const commands = buildCommandMap();
  const handler = commands[command.toLowerCase()];

  if (!handler) {
    return '알 수 없는 명령어입니다. !help를 입력해보세요.';
  }

  return await handler();
}
