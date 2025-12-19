/**
 * Cycle Detector
 *
 * 텍스트 유사도 기반 순환 패턴 감지
 * - Levenshtein distance를 사용한 유사도 계산
 * - 3회 연속 동일 패턴 감지
 */

import type {
  ElementVersion,
  LLMProvider,
  CycleDetectionOptions,
} from '../../shared/types';
import type { BrowserViewManager } from '../browser/browser-view-manager';

interface CycleDetectionResult {
  isCycle: boolean;
  reason: string;
}

/**
 * Levenshtein distance 계산
 * 두 문자열 간의 편집 거리를 계산
 */
function levenshteinDistance(str1: string, str2: string): number {
  const len1 = str1.length;
  const len2 = str2.length;
  const dp: number[][] = Array(len1 + 1)
    .fill(null)
    .map(() => Array(len2 + 1).fill(0));

  for (let i = 0; i <= len1; i++) {
    dp[i][0] = i;
  }
  for (let j = 0; j <= len2; j++) {
    dp[0][j] = j;
  }

  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1;
      }
    }
  }

  return dp[len1][len2];
}

/**
 * 유사도 계산 (0-1 사이의 값)
 * 1에 가까울수록 유사함
 */
function calculateSimilarity(str1: string, str2: string): number {
  if (str1 === str2) return 1.0;
  if (str1.length === 0 && str2.length === 0) return 1.0;
  if (str1.length === 0 || str2.length === 0) return 0.0;

  const distance = levenshteinDistance(str1, str2);
  const maxLen = Math.max(str1.length, str2.length);

  return 1 - distance / maxLen;
}

/**
 * 텍스트 정규화
 * - 공백 제거
 * - 소문자 변환
 */
function normalizeText(text: string): string {
  return text.replace(/\s+/g, ' ').trim().toLowerCase();
}

export class CycleDetector {
  private readonly DEFAULT_SIMILARITY_THRESHOLD = 0.85;
  private readonly DEFAULT_MIN_VERSIONS = 3;

  constructor(private browserManager: BrowserViewManager) {}

  /**
   * 순환 패턴 감지
   * @param judgeProvider Judge 모델 제공자 (useJudgeModel=true일 때만 사용)
   * @param versions 버전 히스토리
   * @param options 감지 옵션
   */
  async detectCycle(
    judgeProvider: LLMProvider,
    versions: ElementVersion[],
    options: CycleDetectionOptions = {}
  ): Promise<boolean> {
    const {
      similarityThreshold = this.DEFAULT_SIMILARITY_THRESHOLD,
      minVersions = this.DEFAULT_MIN_VERSIONS,
      useJudgeModel = false,
    } = options;

    // 최소 버전 수 체크
    if (versions.length < minVersions) {
      return false;
    }

    // Judge 모델 사용 옵션이 켜져있으면 기존 방식 사용
    if (useJudgeModel) {
      return this.detectCycleWithJudge(judgeProvider, versions);
    }

    // 텍스트 유사도 기반 감지
    return this.detectCycleWithSimilarity(versions, similarityThreshold);
  }

  /**
   * 텍스트 유사도 기반 순환 감지
   * 최근 3개 버전이 유사한 패턴을 보이면 순환으로 판단
   */
  private detectCycleWithSimilarity(
    versions: ElementVersion[],
    threshold: number
  ): boolean {
    const last3 = versions.slice(-3);

    // 3개 미만이면 순환 아님
    if (last3.length < 3) {
      return false;
    }

    const [v1, v2, v3] = last3.map((v) => normalizeText(v.content));

    // 각 버전 간 유사도 계산
    const sim12 = calculateSimilarity(v1, v2);
    const sim23 = calculateSimilarity(v2, v3);
    const sim13 = calculateSimilarity(v1, v3);

    // 케이스 1: A → A → A (모든 버전이 유사)
    if (sim12 >= threshold && sim23 >= threshold && sim13 >= threshold) {
      console.log(`[CycleDetector] Detected A→A→A pattern (sim: ${sim12.toFixed(2)})`);
      return true;
    }

    // 케이스 2: A → B → A (첫 번째와 세 번째가 유사하고, 중간이 다름)
    if (sim13 >= threshold && sim12 < threshold && sim23 < threshold) {
      console.log(`[CycleDetector] Detected A→B→A pattern (sim13: ${sim13.toFixed(2)})`);
      return true;
    }

    // 점수가 개선되지 않고 유사한 경우도 순환으로 간주
    const scores = last3.map((v) => v.score);
    const scoreImprovement = Math.max(...scores) - Math.min(...scores);
    const avgSimilarity = (sim12 + sim23 + sim13) / 3;

    if (avgSimilarity >= threshold && scoreImprovement < 5) {
      console.log(
        `[CycleDetector] Detected stagnation (avgSim: ${avgSimilarity.toFixed(2)}, scoreImprovement: ${scoreImprovement})`
      );
      return true;
    }

    return false;
  }

  /**
   * Judge 모델을 사용한 순환 감지 (레거시)
   */
  private async detectCycleWithJudge(
    judgeProvider: LLMProvider,
    versions: ElementVersion[]
  ): Promise<boolean> {
    // Need at least 3 versions to detect a cycle
    if (versions.length < 3) {
      return false;
    }

    try {
      const adapter = this.browserManager.getAdapter(judgeProvider);

      // Build prompt for judge
      const prompt = this.buildCycleDetectionPrompt(versions);

      // Send to judge model
      await adapter.waitForInputReady();
      await adapter.inputPrompt(prompt);
      await adapter.sendMessage();
      await adapter.waitForResponse(60000);

      // Extract and parse response
      const response = await adapter.extractResponse();
      const result = this.parseCycleResponse(response);

      return result.isCycle;
    } catch (error) {
      // On error, assume no cycle
      console.error('Cycle detection error:', error);
      return false;
    }
  }

  /**
   * 유사도 계산 (외부에서 사용 가능)
   */
  calculateTextSimilarity(text1: string, text2: string): number {
    return calculateSimilarity(normalizeText(text1), normalizeText(text2));
  }

  buildCycleDetectionPrompt(versions: ElementVersion[]): string {
    const last3 = versions.slice(-3);

    const versionTexts = last3
      .map(
        (v, i) => `
## Version ${i + 1} (반복 ${v.iteration}, 점수: ${v.score})
${v.content}
`
      )
      .join('\n---\n');

    return `다음 3개의 버전을 분석하여 순환 패턴이 있는지 판단해주세요.

순환 패턴의 정의:
- 버전들이 서로 유사한 내용으로 반복됨
- 더 이상 개선이 되지 않고 같은 내용이 반복됨
- A → B → A 또는 A → B → C → A 형태의 패턴

${versionTexts}

응답 형식 (JSON으로만 응답):
\`\`\`json
{
  "isCycle": true 또는 false,
  "reason": "판단 이유"
}
\`\`\``;
  }

  parseCycleResponse(response: string): CycleDetectionResult {
    try {
      // Try to extract JSON from response
      const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
      const jsonStr = jsonMatch ? jsonMatch[1] : response;

      const parsed = JSON.parse(jsonStr.trim());

      return {
        isCycle: !!parsed.isCycle,
        reason: parsed.reason || '',
      };
    } catch {
      return {
        isCycle: false,
        reason: 'Parse error',
      };
    }
  }
}
