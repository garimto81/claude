# -*- coding: utf-8 -*-
"""
실시간 STT POC — aiohttp + Whisper + Qwen 요약
목적: 스마트폰 마이크 → WebSocket → Whisper STT → 실시간 전사 + AI 요약
사용법: python poc_realtime_stt.py
스마트폰: https://<서버IP>:8765/recorder
모니터:   https://localhost:8765/
"""

import asyncio
import io
import ipaddress
import json
import ssl
import socket
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import av
except ImportError:
    print("[오류] PyAV 패키지가 필요합니다: pip install av")
    raise SystemExit(1)

try:
    from aiohttp import web
except ImportError:
    print("[오류] aiohttp 패키지가 필요합니다: pip install aiohttp")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
PORT = 8765
OLLAMA_URL = "http://localhost:9000/v1/chat/completions"
MODEL = "qwen3.5:9b"
BUFFER_CHAR_THRESHOLD = 500
CHUNK_SECONDS = 15          # 1차 STT 누적 단위 (초)
MAX_RETRY = 3               # NG 시 최대 재시도 (15→30→45초)
RESULTS_DIR = Path(__file__).parent / "results"
CERT_DIR = Path(__file__).parent / "certs"


# ---------------------------------------------------------------------------
# SSL 유틸리티
# ---------------------------------------------------------------------------
def ensure_ssl_certs():
    """자체 서명 SSL 인증서 생성 (없으면)"""
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    cert_path = CERT_DIR / "cert.pem"
    key_path = CERT_DIR / "key.pem"

    if cert_path.exists() and key_path.exists():
        print("[SSL] 기존 인증서 사용")
        return cert_path, key_path

    print("[SSL] 자체 서명 인증서 생성 중...")
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import datetime as _dt

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_dt.datetime.now(_dt.timezone.utc))
        .not_valid_after(_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    key_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    ))
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print("[SSL] 인증서 생성 완료")
    return cert_path, key_path


# ---------------------------------------------------------------------------
# STT 서비스
# ---------------------------------------------------------------------------
class STTService:
    """faster-whisper 기반 STT 서비스"""

    def __init__(self):
        from faster_whisper import WhisperModel
        self.model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    def transcribe(self, audio_array: np.ndarray) -> str:
        """16kHz mono float32 오디오 배열 → 텍스트"""
        segments, _ = self.model.transcribe(
            audio_array,
            language="ko",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        parts = []
        for seg in segments:
            text = seg.text.strip()
            if text:
                parts.append(text)
        return " ".join(parts)


# ---------------------------------------------------------------------------
# 오디오 디코딩
# ---------------------------------------------------------------------------
def decode_webm_opus(data: bytes) -> np.ndarray | None:
    """WebM/Opus 바이너리 → 16kHz mono float32 numpy 배열"""
    try:
        container = av.open(io.BytesIO(data))
        resampler = av.AudioResampler(
            format="s16",
            layout="mono",
            rate=16000,
        )

        frames = []
        for frame in container.decode(audio=0):
            resampled = resampler.resample(frame)
            for rf in resampled:
                arr = rf.to_ndarray().flatten()
                frames.append(arr)
        container.close()

        if not frames:
            return None

        pcm = np.concatenate(frames)
        # s16 → float32 [-1.0, 1.0]
        audio_float = pcm.astype(np.float32) / 32768.0
        return audio_float

    except Exception as e:
        print(f"[디코딩] 오류: {e}")
        return None


# ---------------------------------------------------------------------------
# 레코더 HTML (스마트폰용)
# ---------------------------------------------------------------------------
RECORDER_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>실시간 STT (POC)</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', -apple-system, sans-serif;
    max-width: 600px; margin: 0 auto; padding: 16px;
    background: #fafafa; color: #333;
  }
  .header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
  }
  .header h1 { font-size: 1.2em; }
  #status {
    padding: 4px 12px; border-radius: 12px;
    font-size: 0.8em; display: inline-block;
  }
  .connected { background: #c8e6c9; color: #2e7d32; }
  .disconnected { background: #ffcdd2; color: #c62828; }
  .connecting { background: #fff9c4; color: #f57f17; }

  .controls {
    display: flex; gap: 12px; margin-bottom: 16px;
  }
  .controls button {
    flex: 1; padding: 16px; font-size: 1.1em;
    border: none; border-radius: 8px; cursor: pointer;
    font-weight: 600; transition: opacity 0.2s;
  }
  .controls button:disabled { opacity: 0.4; cursor: not-allowed; }
  #btnStart { background: #4caf50; color: white; }
  #btnStop { background: #f44336; color: white; }

  #statusText {
    text-align: center; font-size: 0.9em; color: #666;
    margin-bottom: 16px; min-height: 1.4em;
  }

  h2 { font-size: 1em; margin-bottom: 8px; color: #555; }

  #transcript {
    background: #f5f5f5; padding: 12px;
    min-height: 150px; max-height: 300px; overflow-y: auto;
    font-size: 0.88em; border-radius: 6px; line-height: 1.6;
    margin-bottom: 16px;
  }
  .line { margin-bottom: 4px; animation: fadeIn 0.3s; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  #summary {
    background: #e8f5e9; padding: 12px;
    min-height: 60px; border-radius: 6px;
    font-size: 0.88em; line-height: 1.6; white-space: pre-wrap;
  }
  .summary-hint {
    font-size: 0.75em; color: #999; margin-top: 4px;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>실시간 STT (POC)</h1>
    <span id="status" class="connecting">연결 중...</span>
  </div>

  <div class="controls">
    <button id="btnStart" disabled>🎤 녹음 시작</button>
    <button id="btnStop" disabled>⏹ 정지</button>
  </div>
  <div id="statusText">대기 중</div>

  <h2>■ 실시간 텍스트</h2>
  <div id="transcript"></div>

  <h2>■ AI 요약 (Qwen 3.5)</h2>
  <div id="summary">대기 중...</div>
  <div class="summary-hint">500자 축적 시 자동 갱신</div>

<script>
  const WS_URL = `wss://${location.host}/ws/audio`;
  let ws = null;
  let mediaRecorder = null;
  let stream = null;
  let chunkCount = 0;

  const statusEl = document.getElementById('status');
  const statusText = document.getElementById('statusText');
  const btnStart = document.getElementById('btnStart');
  const btnStop = document.getElementById('btnStop');
  const transcriptEl = document.getElementById('transcript');
  const summaryEl = document.getElementById('summary');

  function connect() {
    statusEl.textContent = '연결 중...';
    statusEl.className = 'connecting';

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      statusEl.textContent = '연결됨';
      statusEl.className = 'connected';
      btnStart.disabled = false;
      statusText.textContent = '대기 중 — 녹음 시작을 누르세요';
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'transcript') {
        const div = document.createElement('div');
        div.className = 'line';
        div.textContent = data.text;
        transcriptEl.appendChild(div);
        transcriptEl.scrollTop = transcriptEl.scrollHeight;
      }
      if (data.type === 'summary') {
        summaryEl.textContent = data.text;
      }
    };

    ws.onclose = () => {
      statusEl.textContent = '연결 끊김';
      statusEl.className = 'disconnected';
      btnStart.disabled = true;
      btnStop.disabled = true;
      statusText.textContent = '연결 끊김 — 3초 후 재연결';
      stopRecording();
      setTimeout(connect, 3000);
    };

    ws.onerror = () => { ws.close(); };
  }

  let recording = false;
  let sendInterval = null;

  async function startRecording() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunkCount = 0;
      recording = true;

      function createAndStart() {
        if (!recording || !stream) return;
        mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm;codecs=opus'
        });
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
            chunkCount++;
            ws.send(e.data);
            statusText.textContent = `녹음 중... (청크 #${chunkCount})`;
          }
        };
        mediaRecorder.start();
      }

      createAndStart();
      sendInterval = setInterval(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.onstop = () => { createAndStart(); };
          mediaRecorder.stop();
        }
      }, 3000);

      btnStart.disabled = true;
      btnStop.disabled = false;
      statusText.textContent = '녹음 중...';
    } catch (err) {
      statusText.textContent = '마이크 접근 실패: ' + err.message;
    }
  }

  function stopRecording() {
    recording = false;
    if (sendInterval) { clearInterval(sendInterval); sendInterval = null; }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.onstop = null;
      mediaRecorder.stop();
    }
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    mediaRecorder = null;
    btnStart.disabled = false;
    btnStop.disabled = true;
    statusText.textContent = '정지됨';
  }

  btnStart.addEventListener('click', startRecording);
  btnStop.addEventListener('click', stopRecording);

  connect();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# 모니터 HTML
# ---------------------------------------------------------------------------
MONITOR_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>실시간 STT 모니터 (POC)</title>
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

  #transcript {
    background: #f5f5f5; padding: 12px;
    min-height: 120px; max-height: 400px; overflow-y: auto;
    font-size: 0.88em; border-radius: 6px; line-height: 1.6;
  }
  .utterance { margin-bottom: 6px; animation: fadeIn 0.3s; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  #summary {
    background: #e8f5e9; padding: 12px;
    min-height: 60px; border-radius: 6px;
    font-size: 0.88em; line-height: 1.6; white-space: pre-wrap;
  }
  #metrics { margin-top: 16px; font-size: 0.78em; color: #888; }
</style>
</head>
<body>
  <h1>실시간 STT 모니터 (POC)</h1>
  <div id="status" class="connecting">연결 중...</div>

  <h2>실시간 텍스트</h2>
  <div id="transcript"></div>

  <h2>AI 요약</h2>
  <div id="summary">대기 중...</div>

  <div id="metrics"></div>

  <script>
    const WS_URL = `wss://${location.host}/ws/monitor`;
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
      if (data.type === 'transcript') {
        appendTranscript(data.text);
      }
      if (data.type === 'summary') {
        document.getElementById('summary').textContent = data.text;
      }
    }

    function appendTranscript(text) {
      const el = document.getElementById('transcript');
      const div = document.createElement('div');
      div.className = 'utterance';
      div.textContent = text;
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
# 서버 구현 (aiohttp 기반)
# ---------------------------------------------------------------------------
class MeetingServer:
    """실시간 STT aiohttp 서버"""

    def __init__(self, stt: STTService):
        self.stt = stt
        self.monitor_clients: set[web.WebSocketResponse] = set()
        self.audio_clients: set[web.WebSocketResponse] = set()
        self.text_buffer: list[str] = []
        self.buffer_char_count: int = 0
        self.transcript_log: list[str] = []
        self.summaries: list[str] = []
        self.msg_count: int = 0
        self.start_time: float = 0
        self.chunk_count: int = 0
        # STT 누적 버퍼 (점진적 누적 + Qwen 품질 판정)
        self.pcm_buffer = bytearray()       # 현재 누적 PCM (float32)
        self.pcm_history = bytearray()      # NG 시 유지할 이전 PCM
        self.retry_count: int = 0           # 현재 NG 재시도 횟수

    # --- HTTP 라우트 ---

    async def handle_index(self, request: web.Request) -> web.Response:
        return web.Response(text=MONITOR_HTML, content_type="text/html")

    async def handle_recorder(self, request: web.Request) -> web.Response:
        return web.Response(text=RECORDER_HTML, content_type="text/html")

    # --- WebSocket: 모니터 ---

    async def handle_ws_monitor(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.monitor_clients.add(ws)
        print(f"[모니터] 클라이언트 연결 (총 {len(self.monitor_clients)}명)")

        await ws.send_json({
            "type": "init",
            "transcript_count": len(self.transcript_log),
        })

        try:
            async for msg in ws:
                pass  # 모니터는 수신 전용
        finally:
            self.monitor_clients.discard(ws)
            print(f"[모니터] 클라이언트 해제 (총 {len(self.monitor_clients)}명)")

        return ws

    # --- WebSocket: 오디오 ---

    async def handle_ws_audio(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(max_msg_size=10 * 1024 * 1024)
        await ws.prepare(request)

        self.audio_clients.add(ws)
        print("[오디오] 클라이언트 연결")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.BINARY:
                    await self._process_audio_chunk(msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    print(f"[오디오] WebSocket 에러: {ws.exception()}")
        finally:
            self.audio_clients.discard(ws)
            print("[오디오] 클라이언트 해제")

            # 연결 종료 시 잔여 PCM 강제 STT
            remaining_pcm = bytes(self.pcm_history) + bytes(self.pcm_buffer)
            if len(remaining_pcm) > 4 * 16000:  # 최소 1초 이상
                print(f"[종료] 잔여 PCM {len(remaining_pcm)//4/16000:.1f}초 → 최종 STT")
                final_audio = np.frombuffer(remaining_pcm, dtype=np.float32)
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(None, self.stt.transcribe, final_audio)
                if text.strip():
                    await self.broadcast({"type": "transcript", "text": text})
                    self._add_to_buffer(text)
                self.pcm_buffer.clear()
                self.pcm_history.clear()
                self.retry_count = 0

            # 연결 종료 시 잔여 텍스트 버퍼 요약
            if self.text_buffer:
                print(f"[요약] 잔여 버퍼 {self.buffer_char_count}자 → 최종 요약")
                loop = asyncio.get_event_loop()
                summary = await loop.run_in_executor(None, self._summarize_sync)
                self.summaries.append(summary)
                await self.broadcast({"type": "summary", "text": summary})
                self.text_buffer.clear()
                self.buffer_char_count = 0

            self._save_results()

        return ws

    async def _process_audio_chunk(self, data: bytes):
        """오디오 청크 처리: 디코딩 → PCM 누적 → 15초 단위 STT → Qwen 품질 판정"""
        self.chunk_count += 1
        print(f"[오디오] 청크 #{self.chunk_count} 수신: {len(data)} bytes")

        # WebM/Opus 디코딩
        audio_array = decode_webm_opus(data)
        if audio_array is None:
            print(f"[오디오] 청크 #{self.chunk_count} 디코딩 실패, 스킵")
            return

        # PCM 누적 (float32 바이트)
        self.pcm_buffer.extend(audio_array.tobytes())
        samples = len(self.pcm_buffer) // 4  # float32 = 4 bytes
        accumulated_sec = samples / 16000
        print(f"[누적] {accumulated_sec:.1f}초 / {CHUNK_SECONDS}초 목표")

        if accumulated_sec < CHUNK_SECONDS:
            return  # 아직 충분히 누적되지 않음

        # 누적 완료 → history + buffer 결합하여 STT
        combined = bytes(self.pcm_history) + bytes(self.pcm_buffer)
        full_audio = np.frombuffer(combined, dtype=np.float32)
        total_sec = len(full_audio) / 16000
        print(f"[STT] 누적 {total_sec:.1f}초 오디오 추론 중... "
              f"(재시도 #{self.retry_count})")

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self.stt.transcribe, full_audio)

        if not text.strip():
            print(f"[STT] 텍스트 없음 (침묵), 버퍼 클리어")
            self.pcm_buffer.clear()
            self.pcm_history.clear()
            self.retry_count = 0
            return

        # Qwen 품질 판정
        verdict = await loop.run_in_executor(None, self._judge_quality, text)
        print(f"[품질] Qwen 판정: {verdict} | 텍스트: {text[:60]}...")

        if verdict == "OK" or self.retry_count >= MAX_RETRY:
            if self.retry_count >= MAX_RETRY and verdict != "OK":
                print(f"[품질] 최대 재시도 도달 ({MAX_RETRY}회), 강제 broadcast")
            # OK 또는 최대 재시도 → broadcast + 버퍼 클리어
            await self.broadcast({"type": "transcript", "text": text})
            self._add_to_buffer(text)
            self.pcm_buffer.clear()
            self.pcm_history.clear()
            self.retry_count = 0
        else:
            # NG → history에 누적, 다음 15초 추가 대기
            print(f"[품질] NG → history에 {len(self.pcm_buffer)}bytes 추가, "
                  f"다음 {CHUNK_SECONDS}초 대기")
            self.pcm_history.extend(self.pcm_buffer)
            self.pcm_buffer.clear()
            self.retry_count += 1

        # 500자 초과 시 요약
        if self.buffer_char_count >= BUFFER_CHAR_THRESHOLD:
            print(f"[요약] 버퍼 {self.buffer_char_count}자 → 요약 트리거")
            summary = await loop.run_in_executor(None, self._summarize_sync)
            self.summaries.append(summary)
            await self.broadcast({"type": "summary", "text": summary})
            self.text_buffer.clear()
            self.buffer_char_count = 0

    # --- 브로드캐스트 ---

    async def broadcast(self, data: dict):
        """모든 클라이언트 (모니터 + 오디오)에 메시지 push"""
        all_clients = self.monitor_clients | self.audio_clients
        if not all_clients:
            return
        disconnected = set()
        for client in all_clients:
            try:
                await client.send_json(data)
                self.msg_count += 1
            except (ConnectionResetError, ConnectionError):
                disconnected.add(client)
        self.monitor_clients -= disconnected
        self.audio_clients -= disconnected

    # --- Qwen 품질 판정 ---

    def _judge_quality(self, text: str) -> str:
        """Qwen에게 STT 결과 품질 판정 요청 — 'OK' 또는 'NG'"""
        prompt = (
            "다음 STT 결과가 의미 있는 한국어 문장인지 판단하세요.\n"
            "- 의미 있음: \"OK\"\n"
            "- 의미 없음 (깨진 텍스트, 의미 불명): \"NG\"\n"
            "한 단어로만 답하세요.\n\n"
            f"STT 결과: {text}"
        )
        try:
            payload = json.dumps({
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 5,
            }).encode("utf-8")

            req = urllib.request.Request(
                OLLAMA_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                answer = result["choices"][0]["message"]["content"].strip().upper()
                return "OK" if "OK" in answer else "NG"
        except Exception as e:
            print(f"[품질] Qwen 판정 오류 (OK 기본값): {e}")
            return "OK"  # Qwen 실패 시 통과 (STT 결과를 보여주는 게 안 보여주는 것보다 나음)

    # --- 버퍼 + 요약 ---

    def _add_to_buffer(self, text: str):
        """텍스트를 버퍼에 추가"""
        self.text_buffer.append(text)
        self.buffer_char_count += len(text)
        self.transcript_log.append(text)

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

    # --- 결과 저장 ---

    def _save_results(self):
        """세션 결과 JSON 저장"""
        if not self.transcript_log:
            print("[저장] 전사 기록 없음, 스킵")
            return

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result = {
            "run_at": datetime.now().isoformat(),
            "elapsed_sec": round(time.time() - self.start_time, 1),
            "chunk_count": self.chunk_count,
            "transcript": self.transcript_log,
            "summaries": self.summaries,
            "segments_count": len(self.transcript_log),
        }
        out_path = RESULTS_DIR / "realtime_session_result.json"
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[저장] {out_path}")


# ---------------------------------------------------------------------------
# 네트워크 유틸리티
# ---------------------------------------------------------------------------
def get_local_ip() -> str:
    """로컬 네트워크 IP 주소 반환"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------
def main():
    # SSL 인증서
    cert_path, key_path = ensure_ssl_certs()
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(str(cert_path), str(key_path))

    # Whisper 모델 로드
    print("Whisper Large-v3 모델 로드 중...")
    stt = STTService()
    print("Whisper 모델 로드 완료")

    # aiohttp 앱 구성
    server = MeetingServer(stt)
    server.start_time = time.time()

    app = web.Application()
    app.router.add_get("/", server.handle_index)
    app.router.add_get("/monitor", server.handle_index)
    app.router.add_get("/recorder", server.handle_recorder)
    app.router.add_get("/ws/audio", server.handle_ws_audio)
    app.router.add_get("/ws/monitor", server.handle_ws_monitor)

    local_ip = get_local_ip()
    print(f"\n{'='*55}")
    print(f"  실시간 STT POC 서버 (HTTPS)")
    print(f"{'='*55}")
    print(f"  모니터:    https://localhost:{PORT}/")
    print(f"  레코더:    https://{local_ip}:{PORT}/recorder")
    print(f"  Ollama:    {OLLAMA_URL} ({MODEL})")
    print(f"  종료:      Ctrl+C")
    print(f"{'='*55}\n")

    web.run_app(app, host="0.0.0.0", port=PORT, ssl_context=ssl_context,
                print=None)  # suppress default aiohttp startup message


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCtrl+C — 종료합니다.")
