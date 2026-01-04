/**
 * VTuber 아바타 오버레이 - WebSocket 클라이언트
 */

// DOM 요소
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const expressionIndicator = document.getElementById('expressionIndicator');
const expressionIcon = document.getElementById('expressionIcon');
const connectionStatus = document.querySelector('.connection-status');

// WebSocket 연결
let ws = null;
let reconnectInterval = null;

// 표정 아이콘 매핑
const expressionIcons = {
  happy: '😊',
  surprised: '😮',
  neutral: '😐',
  focused: '🤔',
  sorrow: '😢',
};

/**
 * WebSocket 연결
 */
function connectWebSocket() {
  // WebSocket 서버 URL (stream-server)
  const wsUrl = `ws://${window.location.hostname}:3001`;

  try {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('[VTuber Overlay] WebSocket connected');
      updateConnectionStatus(false, '연결 시도 중...');
      clearInterval(reconnectInterval);

      // 'vtuber' 채널 구독 요청
      ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'vtuber',
      }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleMessage(message);
      } catch (err) {
        console.error('[VTuber Overlay] Message parse error:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('[VTuber Overlay] WebSocket error:', error);
      updateConnectionStatus(false, '연결 오류');
    };

    ws.onclose = () => {
      console.log('[VTuber Overlay] WebSocket closed');
      updateConnectionStatus(false, '연결 끊김');

      // 5초 후 재연결 시도
      reconnectInterval = setInterval(() => {
        console.log('[VTuber Overlay] Reconnecting...');
        connectWebSocket();
      }, 5000);
    };
  } catch (err) {
    console.error('[VTuber Overlay] Connection error:', err);
    updateConnectionStatus(false, '연결 실패');
  }
}

/**
 * WebSocket 메시지 처리
 */
function handleMessage(message) {
  console.log('[VTuber Overlay] Message:', message);

  switch (message.type) {
    case 'vtuber:status':
      handleVTuberStatus(message.payload);
      break;

    case 'vtuber:expression':
      handleVTuberExpression(message.payload);
      break;

    default:
      console.log('[VTuber Overlay] Unknown message type:', message.type);
  }
}

/**
 * VTuber 연결 상태 처리
 */
function handleVTuberStatus(payload) {
  const { connected, vmcHost, vmcPort } = payload;

  if (connected) {
    updateConnectionStatus(true, `연결됨 (${vmcHost}:${vmcPort})`);
  } else {
    updateConnectionStatus(false, 'VSeeFace 연결 대기 중');
  }
}

/**
 * VTuber 표정 변경 처리
 */
function handleVTuberExpression(payload) {
  const { expression, duration = 2000 } = payload;

  // 표정 아이콘 업데이트
  const icon = expressionIcons[expression] || '😐';
  expressionIcon.textContent = icon;

  // 표정 인디케이터 표시
  expressionIndicator.classList.add('active');

  // duration 후 숨김
  setTimeout(() => {
    expressionIndicator.classList.remove('active');
  }, duration);
}

/**
 * 연결 상태 UI 업데이트
 */
function updateConnectionStatus(connected, text) {
  if (connected) {
    statusIndicator.textContent = '🟢';
    connectionStatus.classList.add('connected');
  } else {
    statusIndicator.textContent = '🔴';
    connectionStatus.classList.remove('connected');
  }

  statusText.textContent = text;
}

/**
 * OBS 투명 모드 활성화 (URL 파라미터)
 */
function checkTransparentMode() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('transparent') === 'true') {
    document.body.classList.add('transparent-mode');
    console.log('[VTuber Overlay] Transparent mode enabled');
  }
}

/**
 * 초기화
 */
function init() {
  console.log('[VTuber Overlay] Initializing...');
  checkTransparentMode();
  connectWebSocket();
}

// 페이지 로드 시 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
