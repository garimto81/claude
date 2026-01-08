import 'dotenv/config';
import express from 'express';
import { loadHostProfile } from './config/index.js';
import { YouTubeChatService } from './services/youtube-chat.js';
import { LLMClient } from './services/llm-client.js';
import { MessageRouter } from './handlers/message-router.js';
import { getRateLimiter } from './services/rate-limiter.js';
import { createApiRouter } from './routes/api.js';
import { getOAuthService } from './services/oauth.js';

async function main() {
  try {
    // 1. 호스트 프로필 로드 (앱 시작 시 최우선)
    console.log('[App] Loading host profile...');
    const profile = await loadHostProfile();
    console.log(`[App] Host profile loaded: ${profile.host.name}`);
    console.log(`[App] Projects: ${profile.projects.length}`);

    // 2. Express 서버 시작
    const app = express();
    const PORT = parseInt(process.env.PORT || '3002', 10);

    app.use(express.json());

    // Health check endpoint
    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        host: profile.host.name,
        projects: profile.projects.length,
        uptime: process.uptime(),
      });
    });

    // API 라우터 등록
    app.use('/api', createApiRouter());

    app.listen(PORT, () => {
      console.log(`[App] Chatbot server running on http://localhost:${PORT}`);
      console.log(`[App] Health check: http://localhost:${PORT}/health`);
      console.log(`[App] API endpoints: http://localhost:${PORT}/api/*`);
    });

    // 3. YouTube Chat 연동 (선택)
    // OAuth 인증이 필요하므로, 서버 시작 후 /oauth/authorize로 인증
    if (process.env.YOUTUBE_VIDEO_ID || process.env.YOUTUBE_LIVE_URL) {
      console.log('[App] YouTube Chat integration enabled');

      try {
        // OAuth 서비스 초기화
        const oauthService = getOAuthService();

        if (!oauthService.hasValidToken()) {
          console.log('[App] OAuth token not found. Please visit /oauth/authorize to authenticate.');
          console.log(`[App] Auth URL: http://localhost:${PORT}/oauth/authorize`);
        } else {
          // LLM 클라이언트 및 메시지 라우터 초기화
          const llmClient = new LLMClient(process.env.OLLAMA_MODEL);
          const messageRouter = new MessageRouter(llmClient);
          const rateLimiter = getRateLimiter();

          // YouTube Chat 서비스 생성
          const videoId = process.env.YOUTUBE_LIVE_URL
            ? YouTubeChatService.extractVideoId(process.env.YOUTUBE_LIVE_URL)
            : process.env.YOUTUBE_VIDEO_ID!;

          const chatService = new YouTubeChatService(oauthService);

          // 채팅 연결 및 메시지 처리
          await chatService.connect(videoId, async (message) => {
            console.log(`[Chat] ${message.author}: ${message.message}`);

            // Rate limiting 확인
            if (!rateLimiter.tryRespond(message.author)) {
              console.log(`[Chat] Rate limited: ${message.author}`);
              return;
            }

            const response = await messageRouter.route(message);
            if (response) {
              await chatService.sendMessage(response);
            }
          });

          console.log('[App] YouTube Chat connected successfully');
        }
      } catch (error) {
        console.error('[App] YouTube Chat connection failed:', error);
        console.log('[App] You can start the chatbot manually via POST /api/start');
      }
    } else {
      console.log('[App] YouTube Chat integration disabled');
      console.log('[App] Use POST /api/start with videoId or liveUrl to start');
      console.log('[App] Or set YOUTUBE_VIDEO_ID or YOUTUBE_LIVE_URL in .env');
    }

    // 4. GitHub 자동 동기화 (선택)
    if (process.env.GITHUB_AUTO_SYNC === 'true' && profile.social.github) {
      console.log('[App] Auto-sync enabled, syncing GitHub repos...');
      const { GitHubAnalyzer } = await import('./services/github-analyzer.js');
      const { getHostProfileLoader } = await import('./config/host-profile.js');

      try {
        const analyzer = new GitHubAnalyzer(profile.social.github, process.env.GITHUB_TOKEN);
        const activityDays = parseInt(process.env.GITHUB_ACTIVITY_DAYS || '5', 10);

        // 최근 N일간 활동이 있는 레포지토리만 동기화
        const activeRepos = await analyzer.getRecentActiveRepositories(activityDays);
        const loader = getHostProfileLoader();
        await loader.mergeGitHubProjects(activeRepos);

        console.log(`[App] Auto-synced ${activeRepos.length} active repos (last ${activityDays} days)`);
      } catch (error) {
        console.error('[App] Auto-sync failed:', error);
      }
    }

  } catch (error) {
    console.error('[App] Startup failed:', error);
    process.exit(1);
  }
}

main();
