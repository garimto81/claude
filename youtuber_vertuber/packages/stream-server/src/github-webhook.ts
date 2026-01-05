/**
 * GitHub Webhook Handler
 *
 * GitHub Webhook 이벤트를 처리하고 아바타 반응을 트리거합니다.
 */

import type { IncomingMessage, ServerResponse } from 'http';
import { createHmac } from 'crypto';
import { wsManager } from './ws-manager.js';
import { avatarController, ReactionMapper } from '@youtuber/vtuber';
import type {
  WebSocketMessage,
  GitHubCommitPayload,
  GitHubPRPayload,
  GitHubCheckPayload,
  VTuberExpressionPayload,
  VTuberTrigger,
} from '@youtuber/shared';

// GitHub Webhook Secret (환경 변수에서 로드)
const WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET || '';

/**
 * GitHub Webhook 요청 본문 파싱
 */
async function parseBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk: Buffer) => {
      body += chunk.toString();
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

/**
 * GitHub Webhook 서명 검증
 */
function verifySignature(payload: string, signature: string | undefined): boolean {
  if (!WEBHOOK_SECRET) {
    console.warn('[GitHub] No webhook secret configured, skipping verification');
    return true;
  }

  if (!signature) {
    console.error('[GitHub] Missing signature header');
    return false;
  }

  const hmac = createHmac('sha256', WEBHOOK_SECRET);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');

  return signature === digest;
}

/**
 * Push 이벤트 처리 (Commit)
 */
function handlePush(payload: GitHubPushEvent): void {
  const commits = payload.commits || [];
  const repo = payload.repository?.name || 'unknown';

  commits.forEach((commit) => {
    // WebSocket 브로드캐스트: github 채널
    const commitPayload: GitHubCommitPayload = {
      repo,
      message: commit.message.split('\n')[0], // 첫 줄만
      author: commit.author?.name || 'unknown',
      sha: commit.id.substring(0, 7),
      url: commit.url,
    };

    const message: WebSocketMessage<GitHubCommitPayload> = {
      type: 'github:commit',
      payload: commitPayload,
      timestamp: new Date().toISOString(),
    };

    wsManager.broadcast('github', message);

    // 아바타 반응 트리거
    triggerAvatarReaction('commit', { repo, message: commitPayload.message });

    console.log(`[GitHub] Commit: ${repo} - ${commitPayload.sha} by ${commitPayload.author}`);
  });
}

/**
 * Pull Request 이벤트 처리
 */
function handlePullRequest(payload: GitHubPREvent): void {
  const repo = payload.repository?.name || 'unknown';
  const pr = payload.pull_request;
  const action = payload.action;

  // merged 상태 확인
  const prAction = pr.merged ? 'merged' : action as GitHubPRPayload['action'];

  const prPayload: GitHubPRPayload = {
    repo,
    title: pr.title,
    action: prAction,
    number: pr.number,
    author: pr.user?.login || 'unknown',
    url: pr.html_url,
  };

  const message: WebSocketMessage<GitHubPRPayload> = {
    type: 'github:pr',
    payload: prPayload,
    timestamp: new Date().toISOString(),
  };

  wsManager.broadcast('github', message);

  // 아바타 반응 트리거 (merged 또는 opened만)
  if (prAction === 'merged') {
    triggerAvatarReaction('pr_merged', { repo, message: prPayload.title });
  } else if (prAction === 'opened') {
    // pr_opened는 낮은 우선순위로 큐에 추가
    const mapping = ReactionMapper.mapGitHubEvent('pr_opened');
    const tasks = ReactionMapper.toExpressionTasks(mapping);
    tasks.forEach((task) => {
      avatarController.queueExpression({
        ...task,
        timestamp: Date.now(),
      });
    });
  }

  console.log(`[GitHub] PR #${prPayload.number}: ${prAction} - ${prPayload.title}`);
}

/**
 * Check Run 이벤트 처리 (CI/CD)
 */
function handleCheckRun(payload: GitHubCheckRunEvent): void {
  const repo = payload.repository?.name || 'unknown';
  const checkRun = payload.check_run;

  const checkPayload: GitHubCheckPayload = {
    repo,
    name: checkRun.name,
    status: checkRun.status as GitHubCheckPayload['status'],
    conclusion: checkRun.conclusion as GitHubCheckPayload['conclusion'],
    url: checkRun.html_url,
  };

  const message: WebSocketMessage<GitHubCheckPayload> = {
    type: 'github:check',
    payload: checkPayload,
    timestamp: new Date().toISOString(),
  };

  wsManager.broadcast('github', message);

  // CI 완료 시 아바타 반응
  if (checkPayload.status === 'completed') {
    if (checkPayload.conclusion === 'success') {
      triggerAvatarReaction('test_passed', { repo, message: checkPayload.name });
    } else if (checkPayload.conclusion === 'failure') {
      triggerAvatarReaction('test_failed', { repo, message: checkPayload.name });
    }
  }

  console.log(`[GitHub] Check: ${checkPayload.name} - ${checkPayload.status} (${checkPayload.conclusion || 'pending'})`);
}

/**
 * 아바타 반응 트리거
 */
function triggerAvatarReaction(
  trigger: VTuberTrigger,
  metadata: { repo: string; message: string }
): void {
  // ReactionMapper로 표정 매핑
  const mapping = ReactionMapper.mapGitHubEvent(trigger);
  const tasks = ReactionMapper.toExpressionTasks(mapping);

  // AvatarController 큐에 추가
  tasks.forEach((task) => {
    avatarController.queueExpression({
      ...task,
      timestamp: Date.now(),
    });
  });

  // WebSocket 브로드캐스트: vtuber 채널
  const expressionPayload: VTuberExpressionPayload = {
    expression: tasks[0].expression,
    duration: tasks[0].duration,
    trigger,
    metadata,
  };

  const message: WebSocketMessage<VTuberExpressionPayload> = {
    type: 'vtuber:expression',
    payload: expressionPayload,
    timestamp: new Date().toISOString(),
  };

  wsManager.broadcast('vtuber', message);

  console.log(`[VTuber] Triggered: ${expressionPayload.expression} (${trigger})`);
}

/**
 * GitHub Webhook HTTP 핸들러
 */
export async function handleGitHubWebhook(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  // POST 요청만 허용
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }

  try {
    const body = await parseBody(req);
    const signature = req.headers['x-hub-signature-256'] as string | undefined;

    // 서명 검증
    if (!verifySignature(body, signature)) {
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid signature' }));
      return;
    }

    const event = req.headers['x-github-event'] as string;
    const payload = JSON.parse(body);

    console.log(`[GitHub] Webhook received: ${event}`);

    // 이벤트별 처리
    switch (event) {
      case 'push':
        handlePush(payload);
        break;
      case 'pull_request':
        handlePullRequest(payload);
        break;
      case 'check_run':
        handleCheckRun(payload);
        break;
      case 'ping':
        console.log('[GitHub] Ping received');
        break;
      default:
        console.log(`[GitHub] Unhandled event: ${event}`);
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, event }));
  } catch (error) {
    console.error('[GitHub] Webhook error:', error);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Internal server error' }));
  }
}

// GitHub Webhook 페이로드 타입 (간소화)
interface GitHubPushEvent {
  commits?: Array<{
    id: string;
    message: string;
    url: string;
    author?: { name: string };
  }>;
  repository?: { name: string };
}

interface GitHubPREvent {
  action: string;
  pull_request: {
    number: number;
    title: string;
    html_url: string;
    merged: boolean;
    user?: { login: string };
  };
  repository?: { name: string };
}

interface GitHubCheckRunEvent {
  check_run: {
    name: string;
    status: string;
    conclusion: string | null;
    html_url: string;
  };
  repository?: { name: string };
}

// 수동 테스트용 함수 export
export { triggerAvatarReaction };
