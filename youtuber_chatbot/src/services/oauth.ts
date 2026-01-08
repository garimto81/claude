import { google, Auth } from 'googleapis';
import * as fs from 'fs';
import * as path from 'path';

/**
 * 토큰 저장소 인터페이스
 */
interface TokenStorage {
  access_token: string;
  refresh_token: string;
  scope: string;
  token_type: string;
  expiry_date: number;
}

/**
 * OAuth 2.0 서비스
 * Google/YouTube API 인증 관리
 */
export class OAuthService {
  private oauth2Client: Auth.OAuth2Client;
  private tokenPath: string;

  // YouTube API 필수 스코프
  private static readonly SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly', // 채팅 읽기
    'https://www.googleapis.com/auth/youtube.force-ssl', // 채팅 전송
  ];

  constructor(
    clientId: string,
    clientSecret: string,
    redirectUri: string,
    tokenPath?: string,
  ) {
    this.oauth2Client = new google.auth.OAuth2(
      clientId,
      clientSecret,
      redirectUri,
    );

    // 토큰 파일 경로 (기본: 프로젝트 루트)
    this.tokenPath = tokenPath || path.join(process.cwd(), '.tokens.json');

    // 저장된 토큰 로드 시도
    this.loadTokenFromFile();
  }

  /**
   * 환경 변수에서 OAuth 서비스 생성
   */
  static fromEnv(tokenPath?: string): OAuthService {
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const redirectUri =
      process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3002/oauth/callback';

    if (!clientId || !clientSecret) {
      throw new Error(
        'Missing OAuth credentials. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env',
      );
    }

    return new OAuthService(clientId, clientSecret, redirectUri, tokenPath);
  }

  /**
   * 인증 URL 생성
   */
  getAuthUrl(): string {
    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline', // refresh_token 획득
      scope: OAuthService.SCOPES,
      prompt: 'consent', // 항상 동의 화면 표시 (refresh_token 보장)
    });
  }

  /**
   * 인증 코드를 토큰으로 교환
   */
  async exchangeCode(code: string): Promise<void> {
    const { tokens } = await this.oauth2Client.getToken(code);
    this.oauth2Client.setCredentials(tokens);
    this.saveTokenToFile(tokens as TokenStorage);
    console.log('[OAuth] Token saved successfully');
  }

  /**
   * 토큰 파일에서 로드
   */
  private loadTokenFromFile(): boolean {
    try {
      if (fs.existsSync(this.tokenPath)) {
        const tokenData = fs.readFileSync(this.tokenPath, 'utf-8');
        const tokens = JSON.parse(tokenData) as TokenStorage;
        this.oauth2Client.setCredentials(tokens);
        console.log('[OAuth] Token loaded from file');
        return true;
      }
    } catch (error) {
      console.warn('[OAuth] Failed to load token from file:', error);
    }
    return false;
  }

  /**
   * 토큰 파일에 저장
   */
  private saveTokenToFile(tokens: TokenStorage): void {
    try {
      fs.writeFileSync(this.tokenPath, JSON.stringify(tokens, null, 2));
      console.log('[OAuth] Token saved to file');
    } catch (error) {
      console.error('[OAuth] Failed to save token to file:', error);
      throw error;
    }
  }

  /**
   * 유효한 토큰 보유 여부 확인
   */
  hasValidToken(): boolean {
    const credentials = this.oauth2Client.credentials;
    if (!credentials.access_token) {
      return false;
    }

    // 만료 시간 확인 (5분 여유)
    const expiryDate = credentials.expiry_date;
    if (expiryDate && Date.now() >= expiryDate - 5 * 60 * 1000) {
      // refresh_token이 있으면 자동 갱신 시도
      if (credentials.refresh_token) {
        return true; // OAuth2Client가 자동 갱신
      }
      return false;
    }

    return true;
  }

  /**
   * 토큰 강제 갱신
   */
  async refreshToken(): Promise<void> {
    const credentials = this.oauth2Client.credentials;
    if (!credentials.refresh_token) {
      throw new Error('No refresh token available. Re-authentication required.');
    }

    try {
      const { credentials: newTokens } =
        await this.oauth2Client.refreshAccessToken();
      this.oauth2Client.setCredentials(newTokens);
      this.saveTokenToFile(newTokens as TokenStorage);
      console.log('[OAuth] Token refreshed successfully');
    } catch (error) {
      console.error('[OAuth] Token refresh failed:', error);
      throw error;
    }
  }

  /**
   * OAuth2 클라이언트 반환
   */
  getClient(): Auth.OAuth2Client {
    return this.oauth2Client;
  }

  /**
   * 토큰 정보 조회
   */
  getTokenInfo(): { hasToken: boolean; expiresAt: Date | null } {
    const credentials = this.oauth2Client.credentials;
    return {
      hasToken: !!credentials.access_token,
      expiresAt: credentials.expiry_date
        ? new Date(credentials.expiry_date)
        : null,
    };
  }

  /**
   * 토큰 삭제 (로그아웃)
   */
  revokeToken(): void {
    this.oauth2Client.revokeCredentials();
    if (fs.existsSync(this.tokenPath)) {
      fs.unlinkSync(this.tokenPath);
      console.log('[OAuth] Token file deleted');
    }
  }
}

/**
 * 싱글톤 인스턴스 (선택적 사용)
 */
let oauthServiceInstance: OAuthService | null = null;

export function getOAuthService(tokenPath?: string): OAuthService {
  if (!oauthServiceInstance) {
    oauthServiceInstance = OAuthService.fromEnv(tokenPath);
  }
  return oauthServiceInstance;
}
