import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

// googleapis 모킹
const mockGenerateAuthUrl = vi.fn(() => 'https://accounts.google.com/o/oauth2/auth?...');
const mockGetToken = vi.fn();
const mockSetCredentials = vi.fn();
const mockRefreshAccessToken = vi.fn();
const mockRevokeCredentials = vi.fn();

let mockCredentials = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  expiry_date: Date.now() + 3600000,
};

vi.mock('googleapis', () => ({
  google: {
    auth: {
      OAuth2: vi.fn(() => ({
        generateAuthUrl: mockGenerateAuthUrl,
        getToken: mockGetToken,
        setCredentials: mockSetCredentials,
        refreshAccessToken: mockRefreshAccessToken,
        revokeCredentials: mockRevokeCredentials,
        get credentials() {
          return mockCredentials;
        },
      })),
    },
  },
}));

// fs 모킹
vi.mock('fs', async () => {
  const actual = await vi.importActual<typeof import('fs')>('fs');
  return {
    ...actual,
    existsSync: vi.fn(() => false),
    readFileSync: vi.fn(),
    writeFileSync: vi.fn(),
    unlinkSync: vi.fn(),
  };
});

describe('OAuthService', () => {
  let OAuthService: typeof import('../../src/services/oauth.js').OAuthService;

  const mockClientId = 'test-client-id';
  const mockClientSecret = 'test-client-secret';
  const mockRedirectUri = 'http://localhost:3002/oauth/callback';

  beforeEach(async () => {
    vi.clearAllMocks();
    mockCredentials = {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      expiry_date: Date.now() + 3600000,
    };

    // 동적 import로 모듈 재로드
    const module = await import('../../src/services/oauth.js');
    OAuthService = module.OAuthService;
  });

  describe('constructor', () => {
    it('OAuth2Client를 생성', () => {
      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );
      expect(service).toBeDefined();
    });

    it('저장된 토큰이 있으면 로드', () => {
      vi.mocked(fs.existsSync).mockReturnValue(true);
      vi.mocked(fs.readFileSync).mockReturnValue(
        JSON.stringify({
          access_token: 'saved-token',
          refresh_token: 'saved-refresh',
          expiry_date: Date.now() + 3600000,
        })
      );

      new OAuthService(mockClientId, mockClientSecret, mockRedirectUri);

      expect(fs.existsSync).toHaveBeenCalled();
      expect(fs.readFileSync).toHaveBeenCalled();
      expect(mockSetCredentials).toHaveBeenCalled();
    });
  });

  describe('fromEnv', () => {
    it('환경 변수에서 서비스 생성', () => {
      process.env.GOOGLE_CLIENT_ID = mockClientId;
      process.env.GOOGLE_CLIENT_SECRET = mockClientSecret;
      process.env.GOOGLE_REDIRECT_URI = mockRedirectUri;

      const service = OAuthService.fromEnv();
      expect(service).toBeDefined();

      // 정리
      delete process.env.GOOGLE_CLIENT_ID;
      delete process.env.GOOGLE_CLIENT_SECRET;
      delete process.env.GOOGLE_REDIRECT_URI;
    });

    it('환경 변수 누락 시 에러', () => {
      delete process.env.GOOGLE_CLIENT_ID;
      delete process.env.GOOGLE_CLIENT_SECRET;

      expect(() => OAuthService.fromEnv()).toThrow('Missing OAuth credentials');
    });
  });

  describe('getAuthUrl', () => {
    it('인증 URL 생성', () => {
      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      const url = service.getAuthUrl();

      expect(mockGenerateAuthUrl).toHaveBeenCalledWith({
        access_type: 'offline',
        scope: expect.arrayContaining([
          'https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube.force-ssl',
        ]),
        prompt: 'consent',
      });
      expect(url).toContain('accounts.google.com');
    });
  });

  describe('exchangeCode', () => {
    it('인증 코드를 토큰으로 교환', async () => {
      mockGetToken.mockResolvedValue({
        tokens: {
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
          expiry_date: Date.now() + 3600000,
        },
      });

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      await service.exchangeCode('auth-code-123');

      expect(mockGetToken).toHaveBeenCalledWith('auth-code-123');
      expect(mockSetCredentials).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });
  });

  describe('hasValidToken', () => {
    it('유효한 토큰이 있으면 true', () => {
      mockCredentials = {
        access_token: 'valid-token',
        refresh_token: 'refresh',
        expiry_date: Date.now() + 3600000, // 1시간 후 만료
      };

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      expect(service.hasValidToken()).toBe(true);
    });

    it('토큰이 없으면 false', () => {
      mockCredentials = {
        access_token: '',
        refresh_token: '',
        expiry_date: 0,
      };

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      expect(service.hasValidToken()).toBe(false);
    });

    it('만료된 토큰이지만 refresh_token 있으면 true (자동 갱신 가능)', () => {
      mockCredentials = {
        access_token: 'expired-token',
        refresh_token: 'valid-refresh',
        expiry_date: Date.now() - 1000, // 이미 만료
      };

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      expect(service.hasValidToken()).toBe(true);
    });
  });

  describe('refreshToken', () => {
    it('토큰 갱신 성공', async () => {
      mockRefreshAccessToken.mockResolvedValue({
        credentials: {
          access_token: 'new-access-token',
          expiry_date: Date.now() + 3600000,
        },
      });

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      await service.refreshToken();

      expect(mockRefreshAccessToken).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('refresh_token 없으면 에러', async () => {
      mockCredentials = {
        access_token: 'token',
        refresh_token: '',
        expiry_date: Date.now(),
      };

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      await expect(service.refreshToken()).rejects.toThrow(
        'No refresh token available'
      );
    });
  });

  describe('revokeToken', () => {
    it('토큰 삭제 및 파일 제거', () => {
      vi.mocked(fs.existsSync).mockReturnValue(true);

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      service.revokeToken();

      expect(mockRevokeCredentials).toHaveBeenCalled();
      expect(fs.unlinkSync).toHaveBeenCalled();
    });
  });

  describe('getTokenInfo', () => {
    it('토큰 정보 반환', () => {
      mockCredentials = {
        access_token: 'token',
        refresh_token: 'refresh',
        expiry_date: Date.now() + 3600000,
      };

      const service = new OAuthService(
        mockClientId,
        mockClientSecret,
        mockRedirectUri
      );

      const info = service.getTokenInfo();

      expect(info.hasToken).toBe(true);
      expect(info.expiresAt).toBeInstanceOf(Date);
    });
  });
});
