/**
 * VTuber API Routes
 *
 * VTuber 상태 조회 및 수동 표정 제어 API
 */

import type { IncomingMessage, ServerResponse } from 'http';
import { wsManager } from './ws-manager.js';
import { avatarController, ReactionMapper } from '@youtuber/vtuber';
import type {
  WebSocketMessage,
  VTuberExpressionPayload,
  VTuberExpression,
  VTuberTrigger,
} from '@youtuber/shared';

/**
 * 요청 본문 파싱
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
 * JSON 응답 전송
 */
function sendJSON(res: ServerResponse, status: number, data: unknown): void {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(data));
}

/**
 * GET /api/vtuber/status
 * 현재 아바타 상태 조회
 */
function handleGetStatus(res: ServerResponse): void {
  const status = {
    currentExpression: avatarController.getCurrentExpression(),
    isPlaying: avatarController.isPlayingExpression(),
    queueLength: avatarController.getQueueLength(),
    connectedClients: wsManager.getClientCount(),
    channelStats: wsManager.getChannelStats(),
    timestamp: new Date().toISOString(),
  };

  sendJSON(res, 200, status);
}

/**
 * POST /api/vtuber/expression
 * 수동 표정 변경 (테스트용)
 */
async function handleSetExpression(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  try {
    const body = await parseBody(req);
    const { expression, duration = 2000, trigger = 'chat' } = JSON.parse(body) as {
      expression: VTuberExpression;
      duration?: number;
      trigger?: VTuberTrigger;
    };

    // 유효한 표정인지 확인
    const validExpressions: VTuberExpression[] = ['happy', 'surprised', 'neutral', 'focused', 'sorrow'];
    if (!validExpressions.includes(expression)) {
      sendJSON(res, 400, {
        error: 'Invalid expression',
        validExpressions,
      });
      return;
    }

    // 아바타 표정 설정
    avatarController.setExpression(expression, duration);

    // WebSocket 브로드캐스트
    const expressionPayload: VTuberExpressionPayload = {
      expression,
      duration,
      trigger,
      metadata: { message: 'Manual trigger via API' },
    };

    const message: WebSocketMessage<VTuberExpressionPayload> = {
      type: 'vtuber:expression',
      payload: expressionPayload,
      timestamp: new Date().toISOString(),
    };

    const sentCount = wsManager.broadcast('vtuber', message);

    sendJSON(res, 200, {
      success: true,
      expression,
      duration,
      sentTo: sentCount,
    });

    console.log(`[VTuber] Manual expression: ${expression} (${duration}ms)`);
  } catch (error) {
    console.error('[VTuber] Expression error:', error);
    sendJSON(res, 400, { error: 'Invalid request body' });
  }
}

/**
 * GET /api/vtuber/triggers
 * 지원되는 트리거 및 매핑 목록
 */
function handleGetTriggers(res: ServerResponse): void {
  const triggers = {
    github: ReactionMapper.getSupportedGitHubEvents(),
    chat: ReactionMapper.getSupportedChatEmotions(),
    expressions: ['happy', 'surprised', 'neutral', 'focused', 'sorrow'],
    mappings: {
      commit: 'happy (2s)',
      pr_merged: 'surprised (3s)',
      test_passed: 'focused (1s) → happy (2s)',
      test_failed: 'sorrow (3s)',
      positive: 'happy (2s)',
      curious: 'surprised (2s)',
    },
  };

  sendJSON(res, 200, triggers);
}

/**
 * POST /api/vtuber/trigger
 * GitHub 이벤트 시뮬레이션 (테스트용)
 */
async function handleTrigger(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  try {
    const body = await parseBody(req);
    const { event, repo = 'test-repo', message = 'Test trigger' } = JSON.parse(body) as {
      event: string;
      repo?: string;
      message?: string;
    };

    // 유효한 이벤트인지 확인
    const validEvents = ReactionMapper.getSupportedGitHubEvents();
    if (!validEvents.includes(event)) {
      sendJSON(res, 400, {
        error: 'Invalid event',
        validEvents,
      });
      return;
    }

    // ReactionMapper로 표정 매핑
    const mapping = ReactionMapper.mapGitHubEvent(event);
    const tasks = ReactionMapper.toExpressionTasks(mapping);

    // AvatarController 큐에 추가
    tasks.forEach((task) => {
      avatarController.queueExpression({
        ...task,
        timestamp: Date.now(),
      });
    });

    // WebSocket 브로드캐스트
    const expressionPayload: VTuberExpressionPayload = {
      expression: tasks[0].expression,
      duration: tasks[0].duration,
      trigger: event as VTuberTrigger,
      metadata: { repo, message },
    };

    const wsMessage: WebSocketMessage<VTuberExpressionPayload> = {
      type: 'vtuber:expression',
      payload: expressionPayload,
      timestamp: new Date().toISOString(),
    };

    const sentCount = wsManager.broadcast('vtuber', wsMessage);

    sendJSON(res, 200, {
      success: true,
      event,
      expression: tasks[0].expression,
      duration: tasks[0].duration,
      sentTo: sentCount,
    });

    console.log(`[VTuber] Trigger simulation: ${event} → ${tasks[0].expression}`);
  } catch (error) {
    console.error('[VTuber] Trigger error:', error);
    sendJSON(res, 400, { error: 'Invalid request body' });
  }
}

/**
 * VTuber API 라우터
 */
export async function handleVTuberRoute(
  req: IncomingMessage,
  res: ServerResponse,
  path: string
): Promise<boolean> {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    sendJSON(res, 200, {});
    return true;
  }

  // /api/vtuber/status
  if (path === '/api/vtuber/status' && req.method === 'GET') {
    handleGetStatus(res);
    return true;
  }

  // /api/vtuber/expression
  if (path === '/api/vtuber/expression' && req.method === 'POST') {
    await handleSetExpression(req, res);
    return true;
  }

  // /api/vtuber/triggers
  if (path === '/api/vtuber/triggers' && req.method === 'GET') {
    handleGetTriggers(res);
    return true;
  }

  // /api/vtuber/trigger (테스트용 시뮬레이션)
  if (path === '/api/vtuber/trigger' && req.method === 'POST') {
    await handleTrigger(req, res);
    return true;
  }

  return false;
}
