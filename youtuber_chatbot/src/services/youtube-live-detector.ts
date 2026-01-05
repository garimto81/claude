/**
 * YouTube Live Detector
 *
 * YouTube Data API v3를 사용하여 현재 진행 중인 Live 방송을 자동 감지합니다.
 */

interface LiveStreamInfo {
  videoId: string;
  title: string;
  startTime: string;
  viewerCount?: number;
}

interface YouTubeSearchResponse {
  items: Array<{
    id: { videoId: string };
    snippet: {
      title: string;
      liveBroadcastContent: string;
      publishedAt: string;
    };
  }>;
}

interface YouTubeVideoResponse {
  items: Array<{
    liveStreamingDetails?: {
      actualStartTime: string;
      concurrentViewers?: string;
    };
  }>;
}

export class YouTubeLiveDetector {
  private apiKey: string;
  private channelId: string;
  private baseUrl = 'https://www.googleapis.com/youtube/v3';

  constructor(apiKey?: string, channelId?: string) {
    this.apiKey = apiKey || process.env.YOUTUBE_API_KEY || '';
    this.channelId = channelId || process.env.YOUTUBE_CHANNEL_ID || '';

    if (!this.apiKey) {
      console.warn('[LiveDetector] YOUTUBE_API_KEY not set');
    }
    if (!this.channelId) {
      console.warn('[LiveDetector] YOUTUBE_CHANNEL_ID not set');
    }
  }

  /**
   * 현재 진행 중인 Live 방송 감지
   */
  async detectLiveStream(): Promise<LiveStreamInfo | null> {
    if (!this.apiKey || !this.channelId) {
      console.error('[LiveDetector] API Key or Channel ID missing');
      return null;
    }

    try {
      // Step 1: 채널의 Live 방송 검색
      const searchUrl = new URL(`${this.baseUrl}/search`);
      searchUrl.searchParams.set('part', 'snippet');
      searchUrl.searchParams.set('channelId', this.channelId);
      searchUrl.searchParams.set('eventType', 'live');
      searchUrl.searchParams.set('type', 'video');
      searchUrl.searchParams.set('key', this.apiKey);

      const searchResponse = await fetch(searchUrl.toString());
      if (!searchResponse.ok) {
        const error = await searchResponse.json();
        console.error('[LiveDetector] Search API error:', error);
        return null;
      }

      const searchData: YouTubeSearchResponse = await searchResponse.json();

      if (!searchData.items || searchData.items.length === 0) {
        console.log('[LiveDetector] No live stream found');
        return null;
      }

      const liveVideo = searchData.items[0];
      const videoId = liveVideo.id.videoId;

      console.log(`[LiveDetector] Found live stream: ${videoId} - ${liveVideo.snippet.title}`);

      // Step 2: Live 상세 정보 조회 (optional)
      const videoUrl = new URL(`${this.baseUrl}/videos`);
      videoUrl.searchParams.set('part', 'liveStreamingDetails');
      videoUrl.searchParams.set('id', videoId);
      videoUrl.searchParams.set('key', this.apiKey);

      const videoResponse = await fetch(videoUrl.toString());
      const videoData: YouTubeVideoResponse = await videoResponse.json();

      const liveDetails = videoData.items?.[0]?.liveStreamingDetails;

      return {
        videoId,
        title: liveVideo.snippet.title,
        startTime: liveDetails?.actualStartTime || liveVideo.snippet.publishedAt,
        viewerCount: liveDetails?.concurrentViewers
          ? parseInt(liveDetails.concurrentViewers)
          : undefined,
      };
    } catch (error) {
      console.error('[LiveDetector] Error detecting live stream:', error);
      return null;
    }
  }

  /**
   * Live 방송이 시작될 때까지 폴링
   */
  async waitForLiveStream(intervalMs = 30000, maxAttempts = 60): Promise<LiveStreamInfo | null> {
    console.log(`[LiveDetector] Waiting for live stream (polling every ${intervalMs / 1000}s)...`);

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const liveStream = await this.detectLiveStream();

      if (liveStream) {
        console.log(`[LiveDetector] Live stream detected on attempt ${attempt}`);
        return liveStream;
      }

      if (attempt < maxAttempts) {
        await this.sleep(intervalMs);
      }
    }

    console.log('[LiveDetector] Max attempts reached, no live stream found');
    return null;
  }

  /**
   * 설정 확인
   */
  isConfigured(): boolean {
    return !!(this.apiKey && this.channelId);
  }

  /**
   * 현재 설정 정보
   */
  getConfig(): { hasApiKey: boolean; channelId: string | null } {
    return {
      hasApiKey: !!this.apiKey,
      channelId: this.channelId || null,
    };
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// 싱글톤 인스턴스
let detectorInstance: YouTubeLiveDetector | null = null;

export function getLiveDetector(): YouTubeLiveDetector {
  if (!detectorInstance) {
    detectorInstance = new YouTubeLiveDetector();
  }
  return detectorInstance;
}

export function resetLiveDetector(): void {
  detectorInstance = null;
}
