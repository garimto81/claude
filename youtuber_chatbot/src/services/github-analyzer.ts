import { Octokit } from 'octokit';
import type { HostProject } from '../types/host.js';

/**
 * GitHub 레포지토리 분석 서비스
 *
 * Octokit을 사용하여 GitHub API와 통신하고,
 * 레포지토리 정보를 HostProject 타입으로 변환합니다.
 */
export class GitHubAnalyzer {
  private octokit: Octokit;
  private username: string;

  constructor(username: string, token?: string) {
    this.username = username;
    this.octokit = new Octokit({ auth: token });
  }

  /**
   * 사용자의 Public 레포지토리 목록 조회
   */
  async listRepositories(options: {
    sort?: 'created' | 'updated' | 'pushed' | 'full_name';
    direction?: 'asc' | 'desc';
    per_page?: number;
  } = {}): Promise<HostProject[]> {
    const { data: repos } = await this.octokit.rest.repos.listForUser({
      username: this.username,
      sort: options.sort || 'updated',
      direction: options.direction || 'desc',
      per_page: options.per_page || 30,
    });

    return repos.map(repo => this.convertToHostProject(repo));
  }

  /**
   * Pinned 레포지토리 조회 (GraphQL)
   */
  async getPinnedRepositories(): Promise<HostProject[]> {
    const query = `
      query {
        user(login: "${this.username}") {
          pinnedItems(first: 6, types: REPOSITORY) {
            nodes {
              ... on Repository {
                name
                description
                owner { login }
                primaryLanguage { name }
                stargazerCount
                repositoryTopics(first: 10) {
                  nodes { topic { name } }
                }
                latestRelease { tagName }
                homepageUrl
                pushedAt
              }
            }
          }
        }
      }
    `;

    const response: any = await this.octokit.graphql(query);
    const repos = response.user.pinnedItems.nodes;

    return repos.map((repo: any) => ({
      id: repo.name.toLowerCase(),
      name: repo.name,
      description: repo.description || 'No description',
      repository: `${repo.owner.login}/${repo.name}`,
      version: repo.latestRelease?.tagName || '1.0.0',
      stack: repo.primaryLanguage?.name || 'Unknown',
      isActive: true,  // Pinned repos are considered active
      source: 'github' as const,
      lastSyncedAt: new Date().toISOString(),
      stars: repo.stargazerCount,
      topics: repo.repositoryTopics.nodes.map((t: any) => t.topic.name),
      homepage: repo.homepageUrl,
    }));
  }

  /**
   * 특정 레포의 최신 릴리스 버전 조회
   */
  async getLatestRelease(repo: string): Promise<string | null> {
    try {
      const [owner, repoName] = repo.split('/');
      const { data } = await this.octokit.rest.repos.getLatestRelease({
        owner,
        repo: repoName,
      });
      return data.tag_name;
    } catch {
      return null;
    }
  }

  /**
   * GitHub Repo 객체를 HostProject로 변환
   */
  private convertToHostProject(repo: any): HostProject {
    return {
      id: repo.name.toLowerCase(),
      name: repo.name,
      description: repo.description || 'No description',
      repository: repo.full_name,
      version: '1.0.0',  // 기본값, 나중에 릴리스로 업데이트
      stack: repo.language || 'Unknown',
      isActive: false,  // 기본값
      source: 'github',
      lastSyncedAt: new Date().toISOString(),
      stars: repo.stargazers_count,
      topics: repo.topics || [],
      homepage: repo.homepage,
    };
  }

  /**
   * 최근 N일 이내 활동이 있는 레포지토리 조회
   *
   * 활동 기준:
   * - 최근 커밋 (pushed_at)
   * - 최근 이슈 생성/업데이트
   *
   * @param days 조회 기간 (기본값: 5일)
   * @returns 최근 활동이 있는 레포지토리 목록
   */
  async getRecentActiveRepositories(days: number = 5): Promise<HostProject[]> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    console.log(
      `[GitHubAnalyzer] Fetching repositories with activity since ${cutoffDate.toISOString()}`
    );

    // 1. 모든 public repos 조회
    const allRepos = await this.listRepositories({ per_page: 100 });
    console.log(`[GitHubAnalyzer] Found ${allRepos.length} total repositories`);

    // 2. 각 레포에 대해 최근 활동 확인
    const activeRepos: HostProject[] = [];
    for (const repo of allRepos) {
      try {
        const hasActivity = await this.hasRecentActivity(
          repo.repository,
          cutoffDate
        );
        if (hasActivity) {
          activeRepos.push(repo);
          console.log(
            `[GitHubAnalyzer] ✅ Active: ${repo.repository}`
          );
        }
      } catch (error) {
        console.error(
          `[GitHubAnalyzer] Error checking ${repo.repository}:`,
          error
        );
      }
    }

    console.log(
      `[GitHubAnalyzer] ${activeRepos.length} repositories with recent activity`
    );
    return activeRepos;
  }

  /**
   * 레포지토리의 최근 활동 여부 확인
   *
   * @param repoFullName owner/repo 형식
   * @param cutoffDate 기준 날짜
   * @returns 최근 활동 여부
   */
  private async hasRecentActivity(
    repoFullName: string,
    cutoffDate: Date
  ): Promise<boolean> {
    const [owner, repo] = repoFullName.split('/');

    // 1. 커밋 확인 (pushed_at)
    try {
      const { data: repoData } = await this.octokit.rest.repos.get({
        owner,
        repo,
      });

      if (new Date(repoData.pushed_at!) >= cutoffDate) {
        return true;
      }
    } catch (error) {
      console.error(
        `[GitHubAnalyzer] Error fetching repo data for ${repoFullName}:`,
        error
      );
      return false;
    }

    // 2. 이슈/PR 확인
    try {
      const { data: issues } = await this.octokit.rest.issues.listForRepo({
        owner,
        repo,
        since: cutoffDate.toISOString(),
        per_page: 1,
      });

      return issues.length > 0;
    } catch (error) {
      // 이슈가 비활성화된 레포일 수 있음
      return false;
    }
  }

  /**
   * Rate Limit 확인
   */
  async checkRateLimit(): Promise<{
    limit: number;
    remaining: number;
    reset: number;
  }> {
    const { data } = await this.octokit.rest.rateLimit.get();
    return data.rate;
  }
}
