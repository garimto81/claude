/**
 * API Routes
 *
 * 챗봇 API 엔드포인트 (Port 3002)
 */

import { Router, Request, Response } from 'express';
import { YouTubeChatService } from '../services/youtube-chat.js';
import { LLMClient } from '../services/llm-client.js';
import { MessageRouter } from '../handlers/message-router.js';
import { getRateLimiter } from '../services/rate-limiter.js';
import { getLiveDetector } from '../services/youtube-live-detector.js';
import ollama from 'ollama';

// 상태 관리 (간단한 인메모리)
interface ChatbotState {
  isRunning: boolean;
  startedAt: Date | null;
  videoId: string | null;
  chatService: YouTubeChatService | null;
  messageRouter: MessageRouter | null;
  stats: {
    messagesReceived: number;
    responseSent: number;
    questionsAnswered: number;
    commandsProcessed: number;
    errors: number;
  };
}

const state: ChatbotState = {
  isRunning: false,
  startedAt: null,
  videoId: null,
  chatService: null,
  messageRouter: null,
  stats: {
    messagesReceived: 0,
    responseSent: 0,
    questionsAnswered: 0,
    commandsProcessed: 0,
    errors: 0,
  },
};

export function createApiRouter(): Router {
  const router = Router();

  /**
   * POST /api/start
   * 챗봇 시작 (videoId 지정)
   */
  router.post('/start', async (req: Request, res: Response) => {
    try {
      const { videoId, liveUrl } = req.body as { videoId?: string; liveUrl?: string };

      if (state.isRunning) {
        res.status(400).json({
          success: false,
          error: 'Chatbot is already running',
          videoId: state.videoId,
        });
        return;
      }

      if (!videoId && !liveUrl) {
        res.status(400).json({
          success: false,
          error: 'videoId or liveUrl is required',
        });
        return;
      }

      // 채팅 서비스 생성
      const chatService = liveUrl
        ? YouTubeChatService.fromLiveUrl(liveUrl)
        : new YouTubeChatService(videoId!);

      // LLM 클라이언트 및 메시지 라우터 초기화
      const llmClient = new LLMClient(process.env.OLLAMA_MODEL);
      const messageRouter = new MessageRouter(llmClient);
      const rateLimiter = getRateLimiter();

      // 채팅 연결
      await chatService.connect(async (message) => {
        state.stats.messagesReceived++;

        // Rate limiting 확인
        if (!rateLimiter.tryRespond(message.author)) {
          return;
        }

        const response = await messageRouter.route(message);
        if (response) {
          try {
            await chatService.sendMessage(response);
            state.stats.responseSent++;
          } catch (sendError) {
            console.error('[API] Failed to send message:', (sendError as Error).message);
            state.stats.errors++;
          }
        }
      });

      // 상태 업데이트
      state.isRunning = true;
      state.startedAt = new Date();
      state.videoId = videoId || extractVideoId(liveUrl!);
      state.chatService = chatService;
      state.messageRouter = messageRouter;

      res.json({
        success: true,
        message: 'Chatbot started',
        videoId: state.videoId,
        startedAt: state.startedAt,
      });
    } catch (error) {
      state.stats.errors++;
      res.status(500).json({
        success: false,
        error: (error as Error).message,
      });
    }
  });

  /**
   * POST /api/stop
   * 챗봇 중지
   */
  router.post('/stop', async (req: Request, res: Response) => {
    try {
      if (!state.isRunning || !state.chatService) {
        res.status(400).json({
          success: false,
          error: 'Chatbot is not running',
        });
        return;
      }

      await state.chatService.disconnect();

      const duration = state.startedAt
        ? Math.floor((Date.now() - state.startedAt.getTime()) / 1000)
        : 0;

      // 상태 초기화
      state.isRunning = false;
      state.startedAt = null;
      state.videoId = null;
      state.chatService = null;
      state.messageRouter = null;

      res.json({
        success: true,
        message: 'Chatbot stopped',
        duration,
        stats: state.stats,
      });
    } catch (error) {
      state.stats.errors++;
      res.status(500).json({
        success: false,
        error: (error as Error).message,
      });
    }
  });

  /**
   * GET /api/status
   * 현재 연결 상태
   */
  router.get('/status', (req: Request, res: Response) => {
    const uptime = state.startedAt
      ? Math.floor((Date.now() - state.startedAt.getTime()) / 1000)
      : 0;

    res.json({
      isRunning: state.isRunning,
      videoId: state.videoId,
      startedAt: state.startedAt,
      uptime,
      connected: state.chatService?.isConnected() ?? false,
    });
  });

  /**
   * GET /api/stats
   * 통계 (응답 수, 질문 수)
   */
  router.get('/stats', (req: Request, res: Response) => {
    const rateLimiter = getRateLimiter();

    res.json({
      ...state.stats,
      rateLimit: rateLimiter.getStats(),
      uptime: state.startedAt
        ? Math.floor((Date.now() - state.startedAt.getTime()) / 1000)
        : 0,
    });
  });

  /**
   * POST /api/test-message
   * 테스트 메시지 전송 (개발용)
   */
  router.post('/test-message', async (req: Request, res: Response) => {
    try {
      const { message, author = 'TestUser' } = req.body as {
        message: string;
        author?: string;
      };

      if (!message) {
        res.status(400).json({
          success: false,
          error: 'message is required',
        });
        return;
      }

      // LLM 클라이언트로 직접 테스트
      const llmClient = new LLMClient(process.env.OLLAMA_MODEL);
      const messageRouter = new MessageRouter(llmClient);

      const response = await messageRouter.route({
        author,
        message,
        timestamp: new Date(),
      });

      res.json({
        success: true,
        input: { author, message },
        response,
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: (error as Error).message,
      });
    }
  });

  /**
   * GET /api/ollama/status
   * Ollama 연결 상태
   */
  router.get('/ollama/status', async (req: Request, res: Response) => {
    try {
      // Ollama 서버에 간단한 요청
      const models = await ollama.list();
      const currentModel = process.env.OLLAMA_MODEL || 'qwen3:8b';
      const hasModel = models.models.some(m => m.name.includes(currentModel.split(':')[0]));

      res.json({
        status: 'ok',
        connected: true,
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        model: currentModel,
        modelAvailable: hasModel,
        availableModels: models.models.map(m => m.name),
      });
    } catch (error) {
      res.json({
        status: 'error',
        connected: false,
        error: (error as Error).message,
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        model: process.env.OLLAMA_MODEL || 'qwen3:8b',
      });
    }
  });

  /**
   * GET /api/live/detect
   * 현재 Live 방송 감지
   */
  router.get('/live/detect', async (req: Request, res: Response) => {
    try {
      const detector = getLiveDetector();

      if (!detector.isConfigured()) {
        res.status(400).json({
          success: false,
          error: 'YouTube API not configured',
          hint: 'Set YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID in .env',
          config: detector.getConfig(),
        });
        return;
      }

      const liveStream = await detector.detectLiveStream();

      if (liveStream) {
        res.json({
          success: true,
          isLive: true,
          ...liveStream,
        });
      } else {
        res.json({
          success: true,
          isLive: false,
          message: 'No live stream found',
        });
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        error: (error as Error).message,
      });
    }
  });

  /**
   * POST /api/live/auto-start
   * Live 방송 자동 감지 후 챗봇 시작
   */
  router.post('/live/auto-start', async (req: Request, res: Response) => {
    try {
      if (state.isRunning) {
        res.status(400).json({
          success: false,
          error: 'Chatbot is already running',
          videoId: state.videoId,
        });
        return;
      }

      const detector = getLiveDetector();

      if (!detector.isConfigured()) {
        res.status(400).json({
          success: false,
          error: 'YouTube API not configured',
          hint: 'Set YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID in .env',
        });
        return;
      }

      const liveStream = await detector.detectLiveStream();

      if (!liveStream) {
        res.status(404).json({
          success: false,
          error: 'No live stream found',
          message: 'Start a live stream first, then try again',
        });
        return;
      }

      // 채팅 서비스 생성
      const chatService = new YouTubeChatService(liveStream.videoId);
      const llmClient = new LLMClient(process.env.OLLAMA_MODEL);
      const messageRouter = new MessageRouter(llmClient);
      const rateLimiter = getRateLimiter();

      // 채팅 연결
      await chatService.connect(async (message) => {
        state.stats.messagesReceived++;

        if (!rateLimiter.tryRespond(message.author)) {
          return;
        }

        const response = await messageRouter.route(message);
        if (response) {
          try {
            await chatService.sendMessage(response);
            state.stats.responseSent++;
          } catch (sendError) {
            console.error('[API] Failed to send message:', (sendError as Error).message);
            state.stats.errors++;
          }
        }
      });

      // 상태 업데이트
      state.isRunning = true;
      state.startedAt = new Date();
      state.videoId = liveStream.videoId;
      state.chatService = chatService;
      state.messageRouter = messageRouter;

      res.json({
        success: true,
        message: 'Chatbot auto-started',
        videoId: liveStream.videoId,
        title: liveStream.title,
        startedAt: state.startedAt,
        viewerCount: liveStream.viewerCount,
      });
    } catch (error) {
      state.stats.errors++;
      res.status(500).json({
        success: false,
        error: (error as Error).message,
      });
    }
  });

  /**
   * GET /api/live/config
   * Live 감지 설정 상태
   */
  router.get('/live/config', (req: Request, res: Response) => {
    const detector = getLiveDetector();
    const config = detector.getConfig();

    res.json({
      configured: detector.isConfigured(),
      ...config,
      channelId: config.channelId ? `${config.channelId.slice(0, 4)}...` : null,
    });
  });

  return router;
}

/**
 * YouTube URL에서 비디오 ID 추출
 */
function extractVideoId(url: string): string | null {
  const match = url.match(/[?&]v=([^&]+)/);
  return match ? match[1] : null;
}

/**
 * 현재 상태 조회 (외부 모듈용)
 */
export function getChatbotState(): Readonly<ChatbotState> {
  return state;
}
