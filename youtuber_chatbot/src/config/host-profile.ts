/**
 * Host Profile Loader
 *
 * 호스트 프로필을 파일에서 로드하고 관리합니다.
 */

import { readFile, writeFile } from 'node:fs/promises';
import type { HostProfile, HostProject } from '../types/host.js';

/**
 * 호스트 프로필 로더 클래스 (싱글톤)
 */
export class HostProfileLoader {
  private static instance: HostProfileLoader | null = null;
  private profile: HostProfile | null = null;
  private profilePath: string | null = null;

  /**
   * 싱글톤 인스턴스 반환
   */
  static getInstance(): HostProfileLoader {
    if (!HostProfileLoader.instance) {
      HostProfileLoader.instance = new HostProfileLoader();
    }
    return HostProfileLoader.instance;
  }

  /**
   * 프로필 로드
   * @param path 프로필 JSON 파일 경로
   */
  async load(path: string): Promise<HostProfile> {
    this.profilePath = path;

    try {
      const content = await readFile(path, 'utf-8');
      const profile = JSON.parse(content) as HostProfile;

      this.validate(profile);
      this.profile = profile;

      return profile;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new Error(`호스트 프로필 파일을 찾을 수 없습니다: ${path}`);
      }
      if (error instanceof SyntaxError) {
        throw new Error('호스트 프로필 로드 실패: 잘못된 JSON 형식');
      }
      throw error;
    }
  }

  /**
   * 프로필 리로드
   */
  async reload(): Promise<HostProfile> {
    if (!this.profilePath) {
      throw new Error('프로필이 로드되지 않았습니다');
    }
    return this.load(this.profilePath);
  }

  /**
   * 프로필 검증
   */
  private validate(profile: HostProfile): void {
    // 호스트 이름 필수
    if (!profile.host?.name) {
      throw new Error('호스트 이름(host.name)은 필수입니다');
    }

    // 프로젝트 배열 검증
    if (profile.projects && !Array.isArray(profile.projects)) {
      throw new Error('프로젝트 목록(projects)은 배열이어야 합니다');
    }

    if (profile.projects) {
      // 프로젝트 ID 중복 검사
      const ids = new Set<string>();
      for (const project of profile.projects) {
        // 필수 필드 검증
        if (!project.id || !project.name || !project.repository) {
          throw new Error('id, name, repository는 필수 필드입니다');
        }

        if (ids.has(project.id)) {
          throw new Error(`중복된 프로젝트 ID: ${project.id}`);
        }
        ids.add(project.id);
      }
    }
  }

  /**
   * GitHub 프로젝트 병합
   *
   * - manual source 프로젝트는 덮어쓰지 않음
   * - github source 프로젝트는 업데이트
   * - 새 프로젝트는 추가
   */
  async mergeGitHubProjects(projects: HostProject[]): Promise<void> {
    if (!this.profile) {
      throw new Error('프로필이 로드되지 않았습니다');
    }

    const existingProjects = this.profile.projects || [];
    const mergedProjects: HostProject[] = [];

    // 기존 manual 프로젝트 유지
    for (const existing of existingProjects) {
      if (existing.source === 'manual') {
        mergedProjects.push(existing);
      }
    }

    // GitHub 프로젝트 병합/추가
    for (const newProject of projects) {
      const existingManual = mergedProjects.find(
        (p) => p.id === newProject.id && p.source === 'manual',
      );

      // manual source가 있으면 스킵 (덮어쓰지 않음)
      if (existingManual) {
        continue;
      }

      // github source 프로젝트 추가/업데이트
      mergedProjects.push({
        ...newProject,
        source: 'github',
        lastSyncedAt: new Date().toISOString(),
      });
    }

    this.profile.projects = mergedProjects;
    this.profile.meta = {
      ...this.profile.meta,
      version: this.profile.meta?.version || '1.0.0',
      lastUpdated: new Date().toISOString(),
    };

    // 파일에 저장
    if (this.profilePath) {
      await writeFile(
        this.profilePath,
        JSON.stringify(this.profile, null, 2),
        'utf-8',
      );
    }
  }

  /**
   * 현재 프로필 반환 (nullable)
   */
  getProfile(): HostProfile | null {
    return this.profile;
  }

  /**
   * 현재 프로필 반환 (에러 throw)
   */
  getProfileOrThrow(): HostProfile {
    if (!this.profile) {
      throw new Error('프로필이 로드되지 않았습니다');
    }
    return this.profile;
  }

  /**
   * 특정 프로젝트 조회
   */
  getProject(id: string): HostProject | undefined {
    return this.profile?.projects?.find((p) => p.id === id);
  }

  /**
   * 활성 프로젝트 목록
   */
  getActiveProjects(): HostProject[] {
    return (
      this.profile?.projects?.filter((p) => p.isActive !== false) || []
    );
  }
}

/**
 * 호스트 프로필 로더 인스턴스 반환 (편의 함수)
 */
export function getHostProfileLoader(): HostProfileLoader {
  return HostProfileLoader.getInstance();
}
