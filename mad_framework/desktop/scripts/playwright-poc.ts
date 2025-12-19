/**
 * Playwright PoC Script
 *
 * Electron 없이 Playwright로 ChatGPT 자동화 테스트
 *
 * 실행: cd desktop && npx tsx scripts/playwright-poc.ts
 */

import { PlaywrightBrowserManager } from '../playwright/playwright-browser-manager';

// 유틸리티: sleep
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 메인 함수
async function main() {
  console.log('='.repeat(60));
  console.log('Playwright PoC - ChatGPT 자동화 테스트');
  console.log('='.repeat(60));

  const manager = new PlaywrightBrowserManager();

  try {
    // 1. 브라우저 초기화 (headless: false로 GUI 표시)
    console.log('\n[Step 1] 브라우저 초기화...');
    await manager.initialize(false);  // GUI 표시 (수동 로그인 가능)
    console.log('✅ 브라우저 초기화 완료');

    // 2. ChatGPT 어댑터 생성
    console.log('\n[Step 2] ChatGPT 어댑터 생성...');
    await manager.createAdapter('chatgpt');
    const adapter = manager.getAdapter('chatgpt');
    console.log('✅ ChatGPT 어댑터 생성 완료');

    // 3. storageState 확인
    console.log('\n[Step 3] 세션 상태 확인...');
    const storageStatus = manager.getStorageStatus();
    console.log('📁 storageState 존재 여부:', storageStatus);

    // 4. 로그인 확인
    console.log('\n[Step 4] 로그인 상태 확인...');

    // 페이지 로드 대기
    await sleep(3000);

    const loginResult = await adapter.checkLogin();
    console.log('🔐 로그인 상태:', loginResult);

    if (!loginResult.data) {
      console.log('\n⚠️  로그인되어 있지 않습니다.');
      console.log('👉 브라우저에서 수동으로 로그인해주세요.');
      console.log('👉 60초 대기 후 세션을 저장합니다...');

      // 60초 대기 (수동 로그인 시간)
      for (let i = 60; i > 0; i -= 10) {
        console.log(`   남은 시간: ${i}초...`);
        await sleep(10000);
      }

      // 세션 저장
      await manager.saveSessions();
      console.log('✅ 세션 저장 완료');

      // 다시 로그인 확인
      const retryResult = await adapter.checkLogin();
      if (!retryResult.data) {
        console.log('❌ 로그인 실패. 프로그램을 종료합니다.');
        await manager.close();
        process.exit(1);
      }
      console.log('✅ 로그인 확인됨');
    } else {
      console.log('✅ 이미 로그인되어 있습니다.');
    }

    // 5. 메시지 전송 테스트
    console.log('\n[Step 5] 메시지 전송 테스트...');
    const testPrompt = 'Hello! Please respond with just "Hi from Playwright!" in one line.';
    console.log(`📝 프롬프트: "${testPrompt}"`);

    // 입력 준비
    console.log('   → 입력 준비 중...');
    const prepareResult = await adapter.prepareInput(15000);
    if (!prepareResult.success) {
      console.error('❌ 입력 준비 실패:', prepareResult.error);
      await manager.close();
      process.exit(1);
    }
    console.log('   ✅ 입력 준비 완료');

    // 프롬프트 입력
    console.log('   → 프롬프트 입력 중...');
    const enterResult = await adapter.enterPrompt(testPrompt);
    if (!enterResult.success) {
      console.error('❌ 프롬프트 입력 실패:', enterResult.error);
      // 스크린샷 저장
      await manager.captureScreenshot('chatgpt', 'error-enter-prompt.png');
      await manager.close();
      process.exit(1);
    }
    console.log('   ✅ 프롬프트 입력 완료');

    // 메시지 전송
    console.log('   → 메시지 전송 중...');
    const submitResult = await adapter.submitMessage();
    if (!submitResult.success) {
      console.error('❌ 메시지 전송 실패:', submitResult.error);
      await manager.captureScreenshot('chatgpt', 'error-submit.png');
      await manager.close();
      process.exit(1);
    }
    console.log('   ✅ 메시지 전송 완료');

    // 6. 응답 대기
    console.log('\n[Step 6] 응답 대기 중...');
    const awaitResult = await adapter.awaitResponse(60000);
    if (!awaitResult.success) {
      console.error('❌ 응답 대기 실패:', awaitResult.error);
      await manager.captureScreenshot('chatgpt', 'error-await.png');
      await manager.close();
      process.exit(1);
    }
    console.log('   ✅ 응답 수신 완료');

    // 7. 응답 추출
    console.log('\n[Step 7] 응답 추출...');
    const responseResult = await adapter.getResponse();
    if (!responseResult.success) {
      console.error('❌ 응답 추출 실패:', responseResult.error);
      await manager.captureScreenshot('chatgpt', 'error-extract.png');
      await manager.close();
      process.exit(1);
    }

    console.log('='.repeat(60));
    console.log('📨 ChatGPT 응답:');
    console.log('-'.repeat(60));
    console.log(responseResult.data);
    console.log('='.repeat(60));

    // 8. 스크린샷 저장
    console.log('\n[Step 8] 스크린샷 저장...');
    await manager.captureScreenshot('chatgpt', 'success-response.png');
    console.log('✅ 스크린샷 저장: success-response.png');

    // 9. 세션 저장
    console.log('\n[Step 9] 세션 저장...');
    await manager.saveSessions();
    console.log('✅ 세션 저장 완료');

    // 10. 종료
    console.log('\n[Step 10] 브라우저 종료...');
    await manager.close();
    console.log('✅ 브라우저 종료 완료');

    console.log('\n' + '='.repeat(60));
    console.log('🎉 Playwright PoC 테스트 완료!');
    console.log('='.repeat(60));

  } catch (error) {
    console.error('\n❌ 오류 발생:', error);

    // 오류 시 스크린샷 저장 시도
    try {
      await manager.captureScreenshot('chatgpt', 'error-screenshot.png');
    } catch {
      // ignore
    }

    await manager.close();
    process.exit(1);
  }
}

// 실행
main().catch(console.error);
