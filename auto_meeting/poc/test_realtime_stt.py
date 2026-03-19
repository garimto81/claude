# -*- coding: utf-8 -*-
"""
poc_realtime_stt.py E2E 자동 검증 스크립트
Whisper 모델 로드 없이 서버 기동 + HTTP/WS 핵심 파이프라인 검증

사용법: python poc/test_realtime_stt.py
"""

import asyncio
import io
import json
import ssl
import sys
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

# 테스트 대상 모듈 경로
sys.path.insert(0, str(Path(__file__).parent))


# ---------------------------------------------------------------------------
# Test 1: SSL 인증서 생성 + 로드
# ---------------------------------------------------------------------------
def test_ssl_certs():
    """SSL 인증서 생성 → 로드 성공 확인"""
    from poc_realtime_stt import ensure_ssl_certs

    cert_path, key_path = ensure_ssl_certs()
    assert cert_path.exists(), f"cert.pem 없음: {cert_path}"
    assert key_path.exists(), f"key.pem 없음: {key_path}"

    # SSL context 로드 검증
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(cert_path), str(key_path))
    print("[PASS] Test 1: SSL 인증서 생성 + 로드 성공")


# ---------------------------------------------------------------------------
# Test 2: 모델명 qwen3.5:9b 확인
# ---------------------------------------------------------------------------
def test_model_name():
    """MODEL 상수가 qwen3.5:9b인지 확인"""
    from poc_realtime_stt import MODEL

    assert MODEL == "qwen3.5:9b", f"MODEL 불일치: {MODEL} (expected qwen3.5:9b)"
    print("[PASS] Test 2: 모델명 qwen3.5:9b 확인")


# ---------------------------------------------------------------------------
# Test 3: HTML에 Qwen 3.5 표시 확인
# ---------------------------------------------------------------------------
def test_html_model_display():
    """RECORDER_HTML에 'Qwen 3.5' 표기 확인"""
    from poc_realtime_stt import RECORDER_HTML

    assert "Qwen 3.5" in RECORDER_HTML, "RECORDER_HTML에 'Qwen 3.5' 없음"
    assert "Qwen 2.5" not in RECORDER_HTML, "RECORDER_HTML에 구버전 'Qwen 2.5' 잔존"
    print("[PASS] Test 3: HTML 모델명 표시 정상")


# ---------------------------------------------------------------------------
# Test 4: decode_webm_opus — 합성 오디오 디코딩
# ---------------------------------------------------------------------------
def test_decode_webm_opus():
    """합성 WebM/Opus 파일로 디코딩 함수 검증"""
    try:
        import av
    except ImportError:
        print("[SKIP] Test 4: PyAV 미설치, 디코딩 테스트 스킵")
        return

    from poc_realtime_stt import decode_webm_opus

    # 합성 WebM/Opus 생성 (1초 440Hz 사인파)
    sample_rate = 48000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    samples = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)

    buf = io.BytesIO()
    container = av.open(buf, mode="w", format="webm")
    stream = container.add_stream("libopus", rate=sample_rate)
    stream.layout = "mono"

    frame = av.AudioFrame.from_ndarray(
        samples.reshape(1, -1), format="flt", layout="mono"
    )
    frame.rate = sample_rate
    for packet in stream.encode(frame):
        container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
    container.close()

    webm_data = buf.getvalue()
    result = decode_webm_opus(webm_data)

    assert result is not None, "decode_webm_opus가 None 반환"
    assert len(result) > 0, "디코딩 결과가 비어있음"
    assert result.dtype == np.float32, f"dtype 불일치: {result.dtype}"
    print(f"[PASS] Test 4: WebM/Opus 디코딩 성공 ({len(result)} samples)")


# ---------------------------------------------------------------------------
# Test 5: CHUNK_SECONDS, MAX_RETRY 상수 확인
# ---------------------------------------------------------------------------
def test_accumulation_constants():
    """점진적 누적 관련 상수 확인"""
    from poc_realtime_stt import CHUNK_SECONDS, MAX_RETRY

    assert CHUNK_SECONDS == 15, f"CHUNK_SECONDS={CHUNK_SECONDS}, expected 15"
    assert MAX_RETRY == 3, f"MAX_RETRY={MAX_RETRY}, expected 3"
    print("[PASS] Test 5: 누적 상수 CHUNK_SECONDS=15, MAX_RETRY=3 확인")


# ---------------------------------------------------------------------------
# Test 6: MeetingServer 초기화 — pcm_buffer 필드 존재
# ---------------------------------------------------------------------------
def test_server_init_fields():
    """MeetingServer에 pcm_buffer, pcm_history, retry_count 필드 확인"""
    from poc_realtime_stt import MeetingServer

    mock_stt = MagicMock()
    server = MeetingServer(mock_stt)

    assert hasattr(server, "pcm_buffer"), "pcm_buffer 필드 없음"
    assert hasattr(server, "pcm_history"), "pcm_history 필드 없음"
    assert hasattr(server, "retry_count"), "retry_count 필드 없음"
    assert server.retry_count == 0, "retry_count 초기값이 0이 아님"
    print("[PASS] Test 6: MeetingServer 누적 버퍼 필드 확인")


# ---------------------------------------------------------------------------
# Test 7: _judge_quality — Qwen 판정 (Ollama 가용 시)
# ---------------------------------------------------------------------------
def test_judge_quality():
    """_judge_quality가 OK/NG를 반환하는지 확인"""
    from poc_realtime_stt import MeetingServer, OLLAMA_URL

    mock_stt = MagicMock()
    server = MeetingServer(mock_stt)

    # Ollama 가용 여부 확인
    try:
        req = urllib.request.Request(
            OLLAMA_URL.replace("/chat/completions", "/models"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=3)
        ollama_available = True
    except Exception:
        ollama_available = False

    if ollama_available:
        result = server._judge_quality("안녕하세요 오늘 회의를 시작하겠습니다")
        assert result in ("OK", "NG"), f"판정 결과 이상: {result}"
        print(f"[PASS] Test 7: Qwen 품질 판정 = {result} (Ollama 연결됨)")
    else:
        # Ollama 미가용 → 에러 시 기본값 OK 반환 확인
        result = server._judge_quality("테스트 텍스트")
        assert result == "OK", f"Ollama 미가용 시 기본값이 OK가 아님: {result}"
        print("[PASS] Test 7: Qwen 미가용 → 기본값 OK 확인")


# ---------------------------------------------------------------------------
# Test 8: aiohttp 서버 기동 + HTTP/WS 검증
# ---------------------------------------------------------------------------
async def test_server_http_ws():
    """aiohttp 서버 기동 → HTTP GET + WebSocket 연결 검증"""
    try:
        from aiohttp import web
        import aiohttp
    except ImportError:
        print("[SKIP] Test 8: aiohttp 미설치")
        return

    from poc_realtime_stt import MeetingServer, ensure_ssl_certs

    mock_stt = MagicMock()
    mock_stt.transcribe = MagicMock(return_value="테스트 텍스트")

    server = MeetingServer(mock_stt)
    server.start_time = 1000.0

    app = web.Application()
    app.router.add_get("/", server.handle_index)
    app.router.add_get("/recorder", server.handle_recorder)
    app.router.add_get("/ws/monitor", server.handle_ws_monitor)
    app.router.add_get("/ws/audio", server.handle_ws_audio)

    cert_path, key_path = ensure_ssl_certs()
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(str(cert_path), str(key_path))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0, ssl_context=ssl_ctx)
    await site.start()

    port = site._server.sockets[0].getsockname()[1]
    base_url = f"https://127.0.0.1:{port}"

    # 자체 서명 인증서 허용
    client_ssl = ssl.create_default_context()
    client_ssl.check_hostname = False
    client_ssl.verify_mode = ssl.CERT_NONE

    conn = aiohttp.TCPConnector(ssl=client_ssl)
    async with aiohttp.ClientSession(connector=conn) as session:
        # HTTP GET /
        async with session.get(f"{base_url}/") as resp:
            assert resp.status == 200, f"/ status={resp.status}"
            body = await resp.text()
            assert "실시간 STT 모니터" in body

        # HTTP GET /recorder
        async with session.get(f"{base_url}/recorder") as resp:
            assert resp.status == 200, f"/recorder status={resp.status}"
            body = await resp.text()
            assert "Qwen 3.5" in body

        # WebSocket /ws/monitor
        async with session.ws_connect(f"{base_url}/ws/monitor") as ws:
            msg = await asyncio.wait_for(ws.receive_json(), timeout=5)
            assert msg["type"] == "init", f"init 메시지 type 불일치: {msg}"
            await ws.close()

        # WebSocket /ws/audio — binary 전송 가능 확인
        async with session.ws_connect(f"{base_url}/ws/audio") as ws:
            await ws.send_bytes(b"\x00" * 100)
            await asyncio.sleep(0.5)
            await ws.close()

    await runner.cleanup()
    print(f"[PASS] Test 8: HTTP/WS 서버 검증 완료 (port {port})")


# ---------------------------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  poc_realtime_stt.py E2E 자동 검증")
    print("=" * 55)

    passed = 0
    failed = 0
    skipped = 0

    tests = [
        ("Test 1: SSL", test_ssl_certs),
        ("Test 2: 모델명", test_model_name),
        ("Test 3: HTML", test_html_model_display),
        ("Test 4: 디코딩", test_decode_webm_opus),
        ("Test 5: 누적 상수", test_accumulation_constants),
        ("Test 6: 서버 필드", test_server_init_fields),
        ("Test 7: Qwen 판정", test_judge_quality),
    ]

    for name, fn in tests:
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
        except Exception as e:
            if "SKIP" in str(e):
                skipped += 1
            else:
                print(f"[FAIL] {name}: {e}")
                failed += 1

    # async 테스트
    try:
        asyncio.run(test_server_http_ws())
        passed += 1
    except Exception as e:
        if "SKIP" in str(e):
            skipped += 1
        else:
            print(f"[FAIL] Test 8: {e}")
            failed += 1

    print(f"\n{'=' * 55}")
    print(f"  결과: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'=' * 55}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
