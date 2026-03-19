# -*- coding: utf-8 -*-
"""
WebSocket 기반 실시간 회의 모니터 POC
목적: 브라우저 → WebSocket → 실시간 텍스트/요약 push 검증
사용법: python poc_websocket_server.py
접속: http://localhost:8765/
"""

import asyncio
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import websockets
except ImportError:
    print("[오류] websockets 패키지가 필요합니다: pip install websockets")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
PORT = 8765
OLLAMA_URL = "http://localhost:9000/v1/chat/completions"
MODEL = "qwen2.5:7b"
BUFFER_CHAR_THRESHOLD = 500
RESULTS_DIR = Path(__file__).parent / "results"

# 하드코딩 아젠다 (3개)
AGENDAS = [
    {"id": 1, "title": "분기 실적 리뷰", "target_minutes": 10},
    {"id": 2, "title": "신규 프로젝트 킥오프", "target_minutes": 15},
    {"id": 3, "title": "인력 충원 계획", "target_minutes": 10},
]

# 시뮬레이션용 회의 텍스트 청크 (3초 간격 전송)
SIMULATION_CHUNKS = [
    {"agenda_idx": 0, "speaker": "김부장",
     "text": "오늘 회의를 시작하겠습니다. 첫 번째 안건은 분기 실적 리뷰입니다. "
             "매출은 전분기 대비 12% 증가했고, 영업이익률은 8.5%를 기록했습니다."},
    {"agenda_idx": 0, "speaker": "이과장",
     "text": "마케팅 캠페인 효과가 컸습니다. 온라인 채널 매출이 35% 성장했는데, "
             "타겟 광고의 성과로 보입니다. 다만 오프라인 매장은 5% 감소했습니다."},
    {"agenda_idx": 0, "speaker": "박대리",
     "text": "고객 만족도 조사 결과 NPS가 72점으로 전분기 대비 8점 상승했습니다. "
             "배송 속도 개선에 대한 긍정적 피드백이 많았습니다."},
    {"agenda_idx": 1, "speaker": "김부장",
     "text": "두 번째 안건, 신규 프로젝트 킥오프입니다. "
             "AI 기반 고객 서비스 자동화 프로젝트를 다음 달부터 시작합니다."},
    {"agenda_idx": 1, "speaker": "이과장",
     "text": "기술 스택은 어떻게 구성할 예정인가요? 기존 시스템 연동도 고려해야 합니다. "
             "클라우드 인프라 비용 산정도 필요합니다."},
    {"agenda_idx": 1, "speaker": "박대리",
     "text": "현재 CRM 시스템이 레거시라서 API 연동에 시간이 걸릴 수 있습니다. "
             "최소 2주 사전 조사가 필요하고 벤더 미팅도 잡아야 합니다."},
    {"agenda_idx": 2, "speaker": "김부장",
     "text": "마지막 안건, 인력 충원 계획입니다. "
             "개발팀에서 2명, 디자인팀에서 1명 충원 요청이 있었습니다."},
    {"agenda_idx": 2, "speaker": "이과장",
     "text": "개발팀은 시니어 백엔드 1명, 주니어 프론트엔드 1명이 필요합니다. "
             "업무량 대비 인력 부족으로 야근이 잦습니다."},
    {"agenda_idx": 2, "speaker": "박대리",
     "text": "디자인팀도 UX 리서처 1명이 시급합니다. "
             "사용자 테스트를 못하고 있어 제품 품질에 영향이 있습니다."},
    {"agenda_idx": 2, "speaker": "김부장",
     "text": "인사팀에 채용 요청서를 이번 주 내로 제출하겠습니다. "
             "다른 의견 없으시면 오늘 회의를 마치겠습니다. 수고하셨습니다."},
]

# ---------------------------------------------------------------------------
# HTML 모니터 UI
# ---------------------------------------------------------------------------
MONITOR_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auto Meeting POC - Monitor</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', sans-serif;
    max-width: 800px; margin: 0 auto; padding: 20px;
    background: #fafafa; color: #333;
  }
  h1 { font-size: 1.4em; margin-bottom: 8px; }
  h2 { font-size: 1.05em; margin-top: 20px; margin-bottom: 8px; color: #555; }
  #status {
    padding: 4px 12px; border-radius: 12px;
    font-size: 0.85em; display: inline-block; margin-bottom: 12px;
  }
  .connected { background: #c8e6c9; color: #2e7d32; }
  .disconnected { background: #ffcdd2; color: #c62828; }
  .connecting { background: #fff9c4; color: #f57f17; }

  /* 아젠다 */
  .agenda-item {
    display: flex; align-items: center;
    padding: 8px 0; border-bottom: 1px solid #eee;
  }
  .agenda-num { font-weight: bold; width: 28px; color: #1976d2; }
  .agenda-title { flex: 1; }
  .agenda-time { font-size: 0.82em; color: #888; width: 90px; text-align: right; }
  .agenda-bar {
    width: 100px; height: 6px;
    background: #e0e0e0; border-radius: 3px; margin-left: 8px;
  }
  .agenda-bar-fill {
    height: 100%; background: #4caf50;
    border-radius: 3px; transition: width 0.5s;
  }
  .active .agenda-title { font-weight: bold; color: #1976d2; }
  .done .agenda-title { color: #999; text-decoration: line-through; }

  /* 전사 텍스트 */
  #transcript {
    background: #f5f5f5; padding: 12px;
    min-height: 120px; max-height: 300px; overflow-y: auto;
    font-size: 0.88em; border-radius: 6px; line-height: 1.6;
  }
  .utterance { margin-bottom: 6px; animation: fadeIn 0.3s; }
  .speaker { font-weight: 600; color: #1976d2; margin-right: 6px; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  /* 요약 */
  #summary {
    background: #e8f5e9; padding: 12px;
    min-height: 60px; border-radius: 6px;
    font-size: 0.88em; line-height: 1.6; white-space: pre-wrap;
  }
  #metrics { margin-top: 16px; font-size: 0.78em; color: #888; }
</style>
</head>
<body>
  <h1>회의 모니터 (POC)</h1>
  <div id="status" class="connecting">연결 중...</div>

  <h2>아젠다</h2>
  <div id="agenda"></div>

  <h2>실시간 텍스트</h2>
  <div id="transcript"></div>

  <h2>AI 요약</h2>
  <div id="summary">대기 중...</div>

  <div id="metrics"></div>

  <script>
    const WS_URL = `ws://${location.host}/ws/monitor`;
    let ws = null;
    let startTime = null;
    let msgCount = 0;
    let timerInterval = null;

    function formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
    }

    function connect() {
      const statusEl = document.getElementById('status');
      statusEl.textContent = '연결 중...';
      statusEl.className = 'connecting';

      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        statusEl.textContent = '연결됨';
        statusEl.className = 'connected';
        startTime = Date.now();
        timerInterval = setInterval(updateMetrics, 1000);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        msgCount++;
        handleMessage(data);
        updateMetrics();
      };

      ws.onclose = () => {
        statusEl.textContent = '연결 끊김 (3초 후 재연결)';
        statusEl.className = 'disconnected';
        clearInterval(timerInterval);
        setTimeout(connect, 3000);
      };

      ws.onerror = () => { ws.close(); };
    }

    function handleMessage(data) {
      if (data.type === 'init' || data.type === 'agenda_update') {
        renderAgenda(data.agendas, data.current_idx);
      }
      if (data.type === 'transcript') {
        appendTranscript(data.speaker, data.text);
      }
      if (data.type === 'summary') {
        document.getElementById('summary').textContent = data.text;
      }
      if (data.type === 'meeting_end') {
        const statusEl = document.getElementById('status');
        statusEl.textContent = '회의 종료';
        statusEl.className = 'disconnected';
      }
    }

    function renderAgenda(agendas, currentIdx) {
      const el = document.getElementById('agenda');
      el.innerHTML = agendas.map((a, i) => {
        let cls = '';
        if (i < currentIdx) cls = ' done';
        else if (i === currentIdx) cls = ' active';

        const elapsed = a.elapsed_sec || 0;
        const pct = Math.min(100, (elapsed / (a.target_minutes * 60)) * 100);
        const timeStr = formatTime(elapsed) + ' / ' + a.target_minutes + '분';

        return '<div class="agenda-item' + cls + '">' +
          '<span class="agenda-num">' + a.id + '.</span>' +
          '<span class="agenda-title">' + a.title + '</span>' +
          '<span class="agenda-time">' + timeStr + '</span>' +
          '<div class="agenda-bar"><div class="agenda-bar-fill" style="width:' + pct + '%"></div></div>' +
          '</div>';
      }).join('');
    }

    function appendTranscript(speaker, text) {
      const el = document.getElementById('transcript');
      const div = document.createElement('div');
      div.className = 'utterance';
      div.innerHTML = '<span class="speaker">' + speaker + '</span>' + text;
      el.appendChild(div);
      el.scrollTop = el.scrollHeight;
    }

    function updateMetrics() {
      const elapsed = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
      document.getElementById('metrics').textContent =
        'WebSocket 메시지: ' + msgCount + '건 | 경과: ' + formatTime(elapsed);
    }

    connect();
  </script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# 서버 구현
# ---------------------------------------------------------------------------
class MeetingServer:
    """WebSocket 회의 모니터 서버 (시뮬레이션 모드)"""

    def __init__(self):
        self.monitor_clients: set = set()
        self.audio_clients: set = set()
        self.text_buffer: list[str] = []
        self.buffer_char_count: int = 0
        self.agendas = [dict(a, elapsed_sec=0) for a in AGENDAS]
        self.current_agenda_idx: int = 0
        self.running: bool = False
        self.msg_count: int = 0
        self.start_time: float = 0
        self.transcript_log: list[str] = []

    # --- 연결 라우팅 ---

    async def handle_connection(self, websocket):
        """WebSocket 연결을 경로별로 라우팅"""
        path = getattr(websocket, 'path', '') or ''
        if hasattr(websocket, 'request') and hasattr(websocket.request, 'path'):
            path = websocket.request.path

        if "/ws/audio" in path:
            await self._handle_audio(websocket)
        else:
            await self._handle_monitor(websocket)

    async def _handle_monitor(self, websocket):
        """모니터 클라이언트: 실시간 텍스트/요약 수신"""
        self.monitor_clients.add(websocket)
        print(f"[모니터] 클라이언트 연결 (총 {len(self.monitor_clients)}명)")

        # 초기 아젠다 전송
        await websocket.send(json.dumps({
            "type": "init",
            "agendas": self.agendas,
            "current_idx": self.current_agenda_idx,
        }, ensure_ascii=False))

        try:
            async for _ in websocket:
                pass  # 모니터는 수신 전용
        except websockets.ConnectionClosed:
            pass
        finally:
            self.monitor_clients.discard(websocket)
            print(f"[모니터] 클라이언트 해제 (총 {len(self.monitor_clients)}명)")

    async def _handle_audio(self, websocket):
        """오디오 클라이언트: 향후 실시간 오디오 스트림 수신용"""
        self.audio_clients.add(websocket)
        print(f"[오디오] 클라이언트 연결")
        try:
            async for message in websocket:
                print(f"[오디오] 데이터 수신: {len(message)} bytes")
        except websockets.ConnectionClosed:
            pass
        finally:
            self.audio_clients.discard(websocket)
            print(f"[오디오] 클라이언트 해제")

    # --- 브로드캐스트 ---

    async def broadcast(self, data: dict):
        """모든 모니터 클라이언트에 메시지 push"""
        if not self.monitor_clients:
            return
        message = json.dumps(data, ensure_ascii=False)
        disconnected = set()
        for client in self.monitor_clients:
            try:
                await client.send(message)
                self.msg_count += 1
            except websockets.ConnectionClosed:
                disconnected.add(client)
        self.monitor_clients -= disconnected

    # --- 버퍼 + 요약 ---

    def _add_to_buffer(self, speaker: str, text: str):
        """텍스트를 버퍼에 추가"""
        entry = f"{speaker}: {text}"
        self.text_buffer.append(entry)
        self.buffer_char_count += len(entry)
        self.transcript_log.append(entry)

    def _summarize_sync(self) -> str:
        """Qwen 요약 호출 (동기 — executor에서 실행)"""
        full_text = "\n".join(self.text_buffer)
        print(f"[요약] Qwen 호출 ({self.buffer_char_count}자)...")
        t0 = time.time()

        try:
            payload = json.dumps({
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 회의 내용을 요약하는 전문가입니다. "
                                   "핵심 논의사항, 결정사항, 후속 조치를 간결하게 정리하세요.",
                    },
                    {
                        "role": "user",
                        "content": f"다음 회의 내용을 요약해주세요:\n\n{full_text}",
                    },
                ],
                "temperature": 0.3,
                "max_tokens": 512,
            }).encode("utf-8")

            req = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                summary = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            summary = f"[요약 실패] {e}"
            print(f"[요약] 오류: {e}")

        elapsed = time.time() - t0
        print(f"[요약] 완료 ({elapsed:.1f}초)")
        return summary

    # --- 시뮬레이션 ---

    async def run_simulation(self):
        """시뮬레이션 모드: 3초 간격으로 회의 텍스트 청크 전송"""
        await asyncio.sleep(2)  # 클라이언트 연결 대기
        print("[시뮬] 시뮬레이션 시작 (3초 간격)\n")

        agenda_start_times = {0: time.time()}
        prev_agenda_idx = 0

        for i, chunk in enumerate(SIMULATION_CHUNKS):
            if not self.running:
                break

            agenda_idx = chunk["agenda_idx"]
            speaker = chunk["speaker"]
            text = chunk["text"]

            # 아젠다 전환
            if agenda_idx != prev_agenda_idx:
                agenda_start_times[agenda_idx] = time.time()
                prev_agenda_idx = agenda_idx
                self.current_agenda_idx = agenda_idx
                await asyncio.sleep(1)  # 안건 전환 잠시 대기

            # 아젠다 경과 시간 업데이트
            for idx, start_t in agenda_start_times.items():
                if idx <= agenda_idx:
                    self.agendas[idx]["elapsed_sec"] = round(time.time() - start_t, 1)

            # 텍스트 전송
            print(f"[시뮬] [{i+1}/{len(SIMULATION_CHUNKS)}] {speaker}: {text[:40]}...")
            await self.broadcast({
                "type": "transcript",
                "speaker": speaker,
                "text": text,
            })

            # 아젠다 업데이트 전송
            await self.broadcast({
                "type": "agenda_update",
                "agendas": self.agendas,
                "current_idx": self.current_agenda_idx,
            })

            # 버퍼 축적
            self._add_to_buffer(speaker, text)

            # 500자 초과 시 요약
            if self.buffer_char_count >= BUFFER_CHAR_THRESHOLD:
                loop = asyncio.get_event_loop()
                summary = await loop.run_in_executor(None, self._summarize_sync)
                await self.broadcast({"type": "summary", "text": summary})
                self.text_buffer.clear()
                self.buffer_char_count = 0

            await asyncio.sleep(3)

        # 잔여 버퍼 요약
        if self.text_buffer and self.running:
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(None, self._summarize_sync)
            await self.broadcast({"type": "summary", "text": summary})

        # 회의 종료
        await self.broadcast({"type": "meeting_end"})

        # 결과 저장
        self._save_results()
        print("\n[시뮬] 시뮬레이션 완료. 서버는 계속 대기 중 (Ctrl+C 종료)")

    def _save_results(self):
        """세션 결과 JSON 저장"""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result = {
            "run_at": datetime.now().isoformat(),
            "elapsed_sec": round(time.time() - self.start_time, 1),
            "ws_messages_sent": self.msg_count,
            "monitor_connections": len(self.monitor_clients),
            "transcript": self.transcript_log,
            "agendas": [a["title"] for a in AGENDAS],
        }
        out_path = RESULTS_DIR / "websocket_session_result.json"
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[저장] {out_path}")


# ---------------------------------------------------------------------------
# HTTP 핸들러 (process_request 콜백)
# ---------------------------------------------------------------------------
async def handle_http(path, request_headers):
    """HTTP GET 요청 시 모니터 HTML 반환 (WebSocket이 아닌 요청)"""
    if path == "/" or path == "/index.html" or path == "/monitor":
        return (
            200,
            [("Content-Type", "text/html; charset=utf-8")],
            MONITOR_HTML.encode("utf-8"),
        )
    return None  # None → WebSocket 업그레이드 진행


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------
async def main():
    server = MeetingServer()
    server.running = True
    server.start_time = time.time()

    async with websockets.serve(
        server.handle_connection,
        "0.0.0.0",
        PORT,
        process_request=handle_http,
    ):
        print(f"\n{'='*55}")
        print(f"  회의 모니터 POC 서버")
        print(f"{'='*55}")
        print(f"  HTTP 모니터: http://localhost:{PORT}/")
        print(f"  WebSocket:   ws://localhost:{PORT}/ws/monitor")
        print(f"  오디오(예정): ws://localhost:{PORT}/ws/audio")
        print(f"  Ollama:      {OLLAMA_URL} ({MODEL})")
        print(f"  종료:        Ctrl+C")
        print(f"{'='*55}\n")

        sim_task = asyncio.create_task(server.run_simulation())

        try:
            await asyncio.Future()  # 무한 대기
        except asyncio.CancelledError:
            pass
        finally:
            server.running = False
            sim_task.cancel()
            try:
                await sim_task
            except asyncio.CancelledError:
                pass
            print("\n서버 종료")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCtrl+C — 종료합니다.")
