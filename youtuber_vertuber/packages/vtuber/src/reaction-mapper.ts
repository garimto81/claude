/**
 * ReactionMapper - GitHub 이벤트 및 채팅 감정을 아바타 표정으로 매핑
 */

import type { Expression, ExpressionTask, Priority } from './avatar-controller.js';

/**
 * 표정 매핑 결과 (단일 또는 시퀀스)
 */
export type ExpressionMapping = Omit<ExpressionTask, 'timestamp'> | Array<Omit<ExpressionTask, 'timestamp'>>;

/**
 * 이벤트-표정 매핑 테이블
 */
export class ReactionMapper {
  /**
   * GitHub 이벤트 → 표정 매핑 테이블
   */
  private static readonly githubEventMap: Record<string, ExpressionMapping> = {
    // Commit 이벤트
    commit: {
      expression: 'happy',
      duration: 2000,
      priority: 'medium',
      trigger: 'commit',
    },

    // Pull Request 관련
    pr_opened: {
      expression: 'neutral',
      duration: 2000,
      priority: 'low',
      trigger: 'pr_opened',
    },

    pr_merged: {
      expression: 'surprised',  // 기쁜 놀람
      duration: 3000,
      priority: 'high',
      trigger: 'pr_merged',
    },

    pr_closed: {
      expression: 'neutral',
      duration: 2000,
      priority: 'low',
      trigger: 'pr_closed',
    },

    // CI/CD (Test 통과/실패)
    test_passed: [
      {
        expression: 'focused',  // 집중 → 기쁨 시퀀스
        duration: 1000,
        priority: 'high',
        trigger: 'test_passed',
      },
      {
        expression: 'happy',
        duration: 2000,
        priority: 'high',
        trigger: 'test_passed',
      },
    ],

    test_failed: {
      expression: 'sorrow',
      duration: 3000,
      priority: 'medium',
      trigger: 'test_failed',
    },

    // Issue 관련
    issue_opened: {
      expression: 'neutral',
      duration: 2000,
      priority: 'low',
      trigger: 'issue_opened',
    },

    issue_closed: {
      expression: 'neutral',
      duration: 2000,
      priority: 'low',
      trigger: 'issue_closed',
    },
  };

  /**
   * 채팅 감정 → 표정 매핑 테이블
   */
  private static readonly chatEmotionMap: Record<string, ExpressionMapping> = {
    positive: {
      expression: 'happy',
      duration: 2000,
      priority: 'medium',
      trigger: 'chat_positive',
    },

    excited: {
      expression: 'happy',
      duration: 2000,
      priority: 'medium',
      trigger: 'chat_excited',
    },

    curious: {
      expression: 'surprised',
      duration: 2000,
      priority: 'medium',
      trigger: 'chat_curious',
    },

    neutral: {
      expression: 'neutral',
      duration: 1000,
      priority: 'low',
      trigger: 'chat_neutral',
    },

    negative: {
      expression: 'sorrow',
      duration: 2000,
      priority: 'medium',
      trigger: 'chat_negative',
    },
  };

  /**
   * GitHub 이벤트를 표정으로 매핑
   *
   * @param eventType - GitHub 이벤트 타입 (commit, pr_merged, test_passed 등)
   * @returns 표정 매핑 (단일 또는 시퀀스)
   */
  static mapGitHubEvent(eventType: string): ExpressionMapping {
    const mapping = this.githubEventMap[eventType];

    if (!mapping) {
      console.warn(`[ReactionMapper] Unknown GitHub event: ${eventType}, using neutral`);
      return {
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        trigger: eventType,
      };
    }

    return mapping;
  }

  /**
   * 채팅 감정을 표정으로 매핑
   *
   * @param emotion - 감정 타입 (positive, curious, neutral 등)
   * @returns 표정 매핑
   */
  static mapChatEmotion(emotion: string): ExpressionMapping {
    const mapping = this.chatEmotionMap[emotion];

    if (!mapping) {
      console.warn(`[ReactionMapper] Unknown chat emotion: ${emotion}, using neutral`);
      return {
        expression: 'neutral',
        duration: 1000,
        priority: 'low',
        trigger: `chat_${emotion}`,
      };
    }

    return mapping;
  }

  /**
   * 매핑 결과를 ExpressionTask 배열로 변환
   * - 단일 매핑 → [ExpressionTask]
   * - 시퀀스 매핑 → [ExpressionTask, ExpressionTask, ...]
   *
   * @param mapping - 표정 매핑 결과
   * @returns ExpressionTask 배열
   */
  static toExpressionTasks(mapping: ExpressionMapping): Array<Omit<ExpressionTask, 'timestamp'>> {
    if (Array.isArray(mapping)) {
      return mapping;
    }
    return [mapping];
  }

  /**
   * 사용 가능한 GitHub 이벤트 목록
   */
  static getSupportedGitHubEvents(): string[] {
    return Object.keys(this.githubEventMap);
  }

  /**
   * 사용 가능한 채팅 감정 목록
   */
  static getSupportedChatEmotions(): string[] {
    return Object.keys(this.chatEmotionMap);
  }
}
