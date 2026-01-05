/**
 * OBS 스트리밍 오버레이 - WebSocket 클라이언트
 */

// DOM 요소
const projectCards = {
  1: document.getElementById('project1'),
  2: document.getElementById('project2'),
  3: document.getElementById('project3'),
};

const reactionOverlays = {
  1: document.getElementById('reaction1'),
  2: document.getElementById('reaction2'),
  3: document.getElementById('reaction3'),
};

const activeProjectList = document.getElementById('activeProjectList');

// WebSocket 연결
let ws = null;
let reconnectInterval = null;

// 프로젝트 매핑 (repo name → card index)
const projectMapping = {
  'youtuber_vertuber': 1,
  'youtuber_chatbot': 2,
  'tft-assist': 3,
  'claude': 1, // 기본값
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
      console.log('[OBS Overlay] WebSocket connected');
      clearInterval(reconnectInterval);

      // 'commit', 'pr', 'vtuber' 채널 구독 요청
      ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'commit',
      }));
      ws.send(JSON.stringify({
        type: 'subscribe',
        channel: 'pr',
      }));
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
        console.error('[OBS Overlay] Message parse error:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('[OBS Overlay] WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('[OBS Overlay] WebSocket closed');

      // 5초 후 재연결 시도
      reconnectInterval = setInterval(() => {
        console.log('[OBS Overlay] Reconnecting...');
        connectWebSocket();
      }, 5000);
    };
  } catch (err) {
    console.error('[OBS Overlay] Connection error:', err);
  }
}

/**
 * WebSocket 메시지 처리
 */
function handleMessage(message) {
  console.log('[OBS Overlay] Message:', message);

  switch (message.type) {
    case 'commit':
      handleCommit(message.payload);
      break;

    case 'pr':
      handlePullRequest(message.payload);
      break;

    case 'vtuber:expression':
      handleVTuberExpression(message.payload);
      break;

    default:
      console.log('[OBS Overlay] Unknown message type:', message.type);
  }
}

/**
 * Commit 이벤트 처리
 */
function handleCommit(payload) {
  const { repo, message: commitMessage, author } = payload;

  // 프로젝트 카드 찾기
  const cardIndex = projectMapping[repo] || 1;
  const card = projectCards[cardIndex];

  if (!card) return;

  // 활동 텍스트 업데이트
  const activityText = card.querySelector('.activity-text');
  activityText.textContent = `✨ Commit: ${commitMessage.split('\n')[0].substring(0, 40)}...`;

  // 반응 오버레이 표시 (2초)
  showReaction(cardIndex, '🎉', 2000);
}

/**
 * Pull Request 이벤트 처리
 */
function handlePullRequest(payload) {
  const { repo, title, action } = payload;

  // 프로젝트 카드 찾기
  const cardIndex = projectMapping[repo] || 1;
  const card = projectCards[cardIndex];

  if (!card) return;

  // 활동 텍스트 업데이트
  const activityText = card.querySelector('.activity-text');
  const prAction = action === 'opened' ? '열림' : action === 'merged' ? '머지됨' : action;
  activityText.textContent = `🔀 PR ${prAction}: ${title.substring(0, 30)}...`;

  // PR merged 시 반응 오버레이 표시 (3초)
  if (action === 'merged') {
    showReaction(cardIndex, '🎊', 3000);
  }
}

/**
 * VTuber 표정 변경 이벤트 처리
 */
function handleVTuberExpression(payload) {
  const { expression, trigger, metadata } = payload;

  console.log(`[OBS Overlay] VTuber expression: ${expression} (trigger: ${trigger})`);

  // VTuber 아바타 프레임에 표정 전달 (iframe postMessage)
  const vtuberIframe = document.querySelector('.vtuber-frame iframe');
  if (vtuberIframe && vtuberIframe.contentWindow) {
    vtuberIframe.contentWindow.postMessage({
      type: 'vtuber:expression',
      payload,
    }, '*');
  }

  // GitHub 이벤트 트리거 시 프로젝트 카드 반응
  if (trigger === 'commit' && metadata && metadata.repo) {
    const cardIndex = projectMapping[metadata.repo] || 1;
    showReaction(cardIndex, '🎉', 2000);
  } else if (trigger === 'pr_merged' && metadata && metadata.repo) {
    const cardIndex = projectMapping[metadata.repo] || 1;
    showReaction(cardIndex, '🎊', 3000);
  }
}

/**
 * 반응 오버레이 표시
 */
function showReaction(cardIndex, icon, duration = 2000) {
  const overlay = reactionOverlays[cardIndex];
  if (!overlay) return;

  // 아이콘 변경
  const reactionIcon = overlay.querySelector('.reaction-icon');
  reactionIcon.textContent = icon;

  // 오버레이 표시
  overlay.classList.add('active');

  // duration 후 숨김
  setTimeout(() => {
    overlay.classList.remove('active');
  }, duration);
}

/**
 * Active Projects 패널 업데이트
 */
function updateActiveProjects(projects) {
  // TODO: WebSocket으로 활성 프로젝트 목록 수신 시 업데이트
  // 현재는 정적 데이터 표시
}

/**
 * OBS 투명 모드 활성화 (URL 파라미터)
 */
function checkTransparentMode() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('transparent') === 'true') {
    document.body.classList.add('transparent-mode');
    console.log('[OBS Overlay] Transparent mode enabled');
  }
}

/**
 * 초기화
 */
function init() {
  console.log('[OBS Overlay] Initializing...');
  checkTransparentMode();
  connectWebSocket();
}

// 페이지 로드 시 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
