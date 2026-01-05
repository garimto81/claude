/**
 * @youtuber/stream-server
 *
 * WebSocket 서버 및 GitHub Webhook 핸들러
 * VTuber 아바타 반응 시스템의 중앙 허브
 */

import { createServer, IncomingMessage, ServerResponse } from 'http';
import { readFile } from 'fs/promises';
import { join, extname } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

import { wsManager } from './ws-manager.js';
import { handleGitHubWebhook } from './github-webhook.js';
import { handleVTuberRoute } from './vtuber-routes.js';
import { avatarController } from '@youtuber/vtuber';
import type { WebSocketMessage, VTuberExpressionPayload } from '@youtuber/shared';

export const VERSION = '0.1.0';

// __dirname 대체 (ESM)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 환경 변수
const PORT = parseInt(process.env.PORT || '3001', 10);
const HOST = process.env.HOST || '0.0.0.0';

// MIME 타입 매핑
const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

/**
 * 정적 파일 서빙
 */
async function serveStaticFile(
  res: ServerResponse,
  filePath: string
): Promise<boolean> {
  try {
    const publicDir = join(__dirname, '..', 'public');
    const fullPath = join(publicDir, filePath);

    // 보안: public 디렉토리 외부 접근 방지
    if (!fullPath.startsWith(publicDir)) {
      return false;
    }

    const content = await readFile(fullPath);
    const ext = extname(fullPath);
    const mimeType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(content);
    return true;
  } catch {
    return false;
  }
}

/**
 * HTTP 요청 핸들러
 */
async function handleRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<void> {
  const url = new URL(req.url || '/', `http://${req.headers.host}`);
  const path = url.pathname;

  console.log(`[HTTP] ${req.method} ${path}`);

  // CORS 헤더
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // API 라우팅
  // /api/vtuber/*
  if (path.startsWith('/api/vtuber/')) {
    const handled = await handleVTuberRoute(req, res, path);
    if (handled) return;
  }

  // /webhook/github
  if (path === '/webhook/github') {
    await handleGitHubWebhook(req, res);
    return;
  }

  // /api/health
  if (path === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      version: VERSION,
      uptime: process.uptime(),
      clients: wsManager.getClientCount(),
    }));
    return;
  }

  // /api/stats
  if (path === '/api/stats') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      version: VERSION,
      clients: wsManager.getClientCount(),
      channels: wsManager.getChannelStats(),
      avatar: {
        expression: avatarController.getCurrentExpression(),
        isPlaying: avatarController.isPlayingExpression(),
        queueLength: avatarController.getQueueLength(),
      },
    }));
    return;
  }

  // 정적 파일 서빙
  // /overlay/ → public/overlay/
  // /vtuber/ → public/vtuber/
  let staticPath = path;

  // 루트 또는 디렉토리 → index.html
  if (staticPath === '/' || staticPath === '/overlay' || staticPath === '/overlay/') {
    staticPath = '/overlay/index.html';
  } else if (staticPath === '/vtuber' || staticPath === '/vtuber/') {
    staticPath = '/vtuber/index.html';
  }

  const served = await serveStaticFile(res, staticPath);
  if (served) return;

  // 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found', path }));
}

/**
 * 서버 시작
 */
function startServer(): void {
  const server = createServer(handleRequest);

  // WebSocket 서버 연결
  wsManager.attach(server);

  // AvatarController 표정 변경 핸들러 설정
  avatarController.setExpressionChangeHandler((expression, duration, trigger) => {
    const message: WebSocketMessage<VTuberExpressionPayload> = {
      type: 'vtuber:expression',
      payload: {
        expression,
        duration,
        trigger: (trigger as VTuberExpressionPayload['trigger']) || 'chat',
      },
      timestamp: new Date().toISOString(),
    };

    wsManager.broadcast('vtuber', message);
  });

  server.listen(PORT, HOST, () => {
    console.log('');
    console.log('='.repeat(50));
    console.log(`  @youtuber/stream-server v${VERSION}`);
    console.log('='.repeat(50));
    console.log(`  HTTP Server: http://${HOST}:${PORT}`);
    console.log(`  WebSocket:   ws://${HOST}:${PORT}`);
    console.log('');
    console.log('  Endpoints:');
    console.log(`    GET  /overlay/          - OBS Overlay (1920x1080)`);
    console.log(`    GET  /vtuber/           - VTuber Frame (320x180)`);
    console.log(`    GET  /api/health        - Health check`);
    console.log(`    GET  /api/stats         - Server stats`);
    console.log(`    GET  /api/vtuber/status - Avatar status`);
    console.log(`    POST /api/vtuber/expression - Set expression`);
    console.log(`    POST /api/vtuber/trigger - Simulate event`);
    console.log(`    POST /webhook/github    - GitHub Webhook`);
    console.log('='.repeat(50));
    console.log('');
  });

  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n[Server] Shutting down...');
    wsManager.close();
    server.close(() => {
      console.log('[Server] Closed');
      process.exit(0);
    });
  });
}

// 서버 시작
startServer();

// Export for testing
export { wsManager, startServer };
