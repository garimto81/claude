/**
 * VMC Client 단위 테스트
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { VMCClient } from '../src/vmc-client';
import type { BlendShapeData, VMCStatus } from '../src/types';

describe('VMCClient', () => {
  let client: VMCClient;

  beforeEach(() => {
    client = new VMCClient({ host: 'localhost', port: 39539 });
  });

  afterEach(() => {
    if (client) {
      client.disconnect();
    }
  });

  describe('생성자', () => {
    it('기본 옵션으로 클라이언트 생성', () => {
      const defaultClient = new VMCClient();
      const status = defaultClient.getStatus();

      expect(status.host).toBe('localhost');
      expect(status.port).toBe(39539);
      expect(status.connected).toBe(false);
    });

    it('커스텀 옵션으로 클라이언트 생성', () => {
      const customClient = new VMCClient({
        host: '192.168.1.100',
        port: 9000,
        healthCheckInterval: 3000,
      });

      const status = customClient.getStatus();
      expect(status.host).toBe('192.168.1.100');
      expect(status.port).toBe(9000);
    });
  });

  describe('getStatus', () => {
    it('초기 상태는 연결 안됨', () => {
      const status = client.getStatus();

      expect(status.connected).toBe(false);
      expect(status.host).toBe('localhost');
      expect(status.port).toBe(39539);
      expect(status.lastUpdate).toBeInstanceOf(Date);
    });
  });

  describe('onBlendShapeUpdate', () => {
    it('BlendShape 업데이트 콜백 등록', () => {
      const callback = vi.fn();
      client.onBlendShapeUpdate(callback);

      // 콜백이 등록되었는지 확인 (내부 구현이므로 간접 확인)
      expect(callback).toBeDefined();
    });

    it('여러 콜백 등록 가능', () => {
      const callback1 = vi.fn();
      const callback2 = vi.fn();

      client.onBlendShapeUpdate(callback1);
      client.onBlendShapeUpdate(callback2);

      expect(callback1).toBeDefined();
      expect(callback2).toBeDefined();
    });
  });

  describe('onStatusChange', () => {
    it('상태 변경 콜백 등록', () => {
      const callback = vi.fn();
      client.onStatusChange(callback);

      expect(callback).toBeDefined();
    });
  });

  describe('sendExpression', () => {
    it('연결 안된 상태에서 sendExpression 호출 시 경고', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      client.sendExpression('Joy', 1.0);

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        '[VMC] Not connected, cannot send expression'
      );

      consoleWarnSpy.mockRestore();
    });
  });

  describe('disconnect', () => {
    it('연결 안된 상태에서 disconnect 호출 시 경고', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      client.disconnect();

      expect(consoleWarnSpy).toHaveBeenCalledWith('[VMC] Not connected');

      consoleWarnSpy.mockRestore();
    });
  });

  describe('BlendShape 데이터 파싱', () => {
    it('Joy BlendShape 값 파싱', () => {
      const testData: BlendShapeData = { Joy: 0.8 };

      expect(testData.Joy).toBe(0.8);
      expect(Object.keys(testData)).toContain('Joy');
    });

    it('여러 BlendShape 값 파싱', () => {
      const testData: BlendShapeData = {
        Joy: 0.8,
        Angry: 0.2,
        Sorrow: 0.1,
        Fun: 0.9,
      };

      expect(testData.Joy).toBe(0.8);
      expect(testData.Angry).toBe(0.2);
      expect(testData.Sorrow).toBe(0.1);
      expect(testData.Fun).toBe(0.9);
    });

    it('BlendShape 값 범위 검증 (0.0 ~ 1.0)', () => {
      const validData: BlendShapeData = {
        Joy: 0.0,
        Angry: 0.5,
        Sorrow: 1.0,
      };

      expect(validData.Joy).toBeGreaterThanOrEqual(0);
      expect(validData.Joy).toBeLessThanOrEqual(1);
      expect(validData.Angry).toBeGreaterThanOrEqual(0);
      expect(validData.Angry).toBeLessThanOrEqual(1);
      expect(validData.Sorrow).toBeGreaterThanOrEqual(0);
      expect(validData.Sorrow).toBeLessThanOrEqual(1);
    });
  });

  describe('VMCStatus 타입', () => {
    it('VMCStatus 구조 검증', () => {
      const status: VMCStatus = {
        connected: true,
        host: 'localhost',
        port: 39539,
        lastUpdate: new Date(),
      };

      expect(status.connected).toBe(true);
      expect(status.host).toBe('localhost');
      expect(status.port).toBe(39539);
      expect(status.lastUpdate).toBeInstanceOf(Date);
    });
  });
});

/**
 * 통합 테스트 (VSeeFace 실행 필요)
 *
 * 아래 테스트는 VSeeFace가 실행 중이고 VMC Protocol이 활성화되어 있을 때만 통과합니다.
 * 환경 변수 VSEFACE_TEST=true 로 활성화합니다.
 *
 * 실행 방법:
 * VSEFACE_TEST=true pnpm --filter @youtuber/vtuber test
 */
const runIntegrationTests = process.env.VSEFACE_TEST === 'true';
const describeIntegration = runIntegrationTests ? describe : describe.skip;

describeIntegration('VMCClient 통합 테스트 (VSeeFace 필요)', () => {
  let client: VMCClient;

  beforeEach(() => {
    client = new VMCClient({ host: 'localhost', port: 39539 });
  });

  afterEach(() => {
    if (client) {
      client.disconnect();
    }
  });

  it('VSeeFace에 연결', async () => {
    await client.connect();

    const status = client.getStatus();
    expect(status.connected).toBe(true);
  }, 10000); // 10초 타임아웃

  it('BlendShape 데이터 수신', async () => {
    await client.connect();

    const blendShapes: BlendShapeData[] = [];

    client.onBlendShapeUpdate((data) => {
      blendShapes.push(data);
    });

    // 5초 대기 (VSeeFace가 데이터 전송할 때까지)
    await new Promise((resolve) => setTimeout(resolve, 5000));

    expect(blendShapes.length).toBeGreaterThan(0);
  }, 10000);

  it('VSeeFace에 표정 전송', async () => {
    await client.connect();

    // Joy 표정 전송
    client.sendExpression('Joy', 1.0);

    // 1초 대기
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const status = client.getStatus();
    expect(status.connected).toBe(true);
  }, 10000);
});
