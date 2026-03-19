# -*- coding: utf-8 -*-
"""
SenseVoice STT POC 스크립트
목적: FunASR SenseVoice-Small 모델의 한국어 음성 인식 성능 독립 검증
사용법: python poc_sensevoice.py <오디오 파일 경로>
"""

import sys
import json
import time
import os
from pathlib import Path


def get_audio_duration(audio_path: str) -> float:
    """오디오 파일 길이(초) 반환"""
    try:
        import wave
        with wave.open(audio_path, 'r') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        # WAV가 아닌 경우 librosa 시도
        try:
            import librosa
            duration = librosa.get_duration(filename=audio_path)
            return duration
        except Exception:
            return 0.0


def get_memory_usage_gb() -> float:
    """현재 프로세스 CPU 메모리 사용량(GB) 반환"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_bytes = process.memory_info().rss
        return mem_bytes / (1024 ** 3)
    except ImportError:
        print("[경고] psutil 미설치 — 메모리 측정 불가 (pip install psutil)")
        return -1.0


def suggest_sample_tts():
    """샘플 TTS 생성 안내 메시지 출력"""
    print("\n[샘플 TTS 생성 옵션]")
    print("  아래 명령으로 테스트용 WAV 파일을 생성할 수 있습니다:")
    print()
    print("  Python TTS (gTTS 사용):")
    print("    pip install gtts")
    print("    python -c \"")
    print("    from gtts import gTTS")
    print("    tts = gTTS('오늘 회의 안건은 세 가지입니다. 첫째, 프로젝트 현황 보고입니다.', lang='ko')")
    print("    tts.save('test_sample.mp3')\"")
    print()
    print("  또는 audio_samples/ 폴더에 WAV/MP3 파일을 직접 배치 후 실행하세요.")
    print("  예: python poc_sensevoice.py poc/audio_samples/sample.wav")


def load_model():
    """SenseVoice-Small 모델 로드 및 로딩 시간 측정"""
    print("[1/4] FunASR AutoModel 임포트 중...")
    try:
        from funasr import AutoModel
    except ImportError as e:
        raise ImportError(
            "FunASR 미설치. 설치 명령: pip install funasr\n"
            f"원인: {e}"
        )

    print("[2/4] SenseVoice-Small 모델 로드 중 (초기 실행 시 다운로드 발생)...")
    t_start = time.time()
    try:
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            device="cpu",          # GPU는 LLM 전용으로 CPU 고정
            disable_update=True,   # 자동 업데이트 비활성화
        )
    except Exception as e:
        raise RuntimeError(
            f"모델 로드 실패. 네트워크 연결 및 HuggingFace 접근 가능 여부를 확인하세요.\n"
            f"원인: {e}"
        )
    load_time = time.time() - t_start
    return model, load_time


def run_inference(model, audio_path: str):
    """
    STT 추론 실행 및 추론 시간 측정
    반환: (인식 텍스트, 추론 소요 시간)
    """
    print("[3/4] STT 추론 실행 중...")
    t_start = time.time()
    try:
        res = model.generate(
            input=audio_path,
            language="ko",         # 한국어 고정
        )
    except Exception as e:
        # 오디오 포맷 오류 처리
        if "format" in str(e).lower() or "decode" in str(e).lower():
            raise ValueError(
                f"오디오 포맷 오류. WAV(16kHz, 16bit, mono) 형식을 권장합니다.\n"
                f"변환 명령: ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav\n"
                f"원인: {e}"
            )
        raise RuntimeError(f"추론 실패: {e}")

    infer_time = time.time() - t_start

    # FunASR 결과 파싱 (list of dict 형태)
    if isinstance(res, list) and len(res) > 0:
        text = res[0].get("text", "").strip()
    elif isinstance(res, dict):
        text = res.get("text", "").strip()
    else:
        text = str(res).strip()

    return text, infer_time


def print_results(audio_path: str, load_time: float, infer_time: float,
                  audio_duration: float, recognized_text: str, memory_gb: float,
                  output_json_path: str):
    """결과 콘솔 출력"""
    # RTF 계산 (Real-Time Factor: 추론시간 / 오디오 길이)
    if audio_duration > 0:
        rtf = infer_time / audio_duration
        realtime_ratio = audio_duration / infer_time if infer_time > 0 else 0
        rtf_str = f"{rtf:.2f} ({realtime_ratio:.1f}x 실시간)"
        duration_str = f"{audio_duration:.1f}초"
    else:
        rtf_str = "측정 불가 (오디오 길이 파악 실패)"
        duration_str = "알 수 없음"

    memory_str = f"{memory_gb:.2f}GB" if memory_gb >= 0 else "측정 불가"

    print()
    print("=" * 45)
    print("=== SenseVoice STT POC ===")
    print("=" * 45)
    print(f"모델: SenseVoice-Small (CPU)")
    print(f"오디오: {os.path.basename(audio_path)}")
    print("-" * 45)
    print(f"모델 로딩: {load_time:.1f}초")
    print(f"추론 시간: {infer_time:.1f}초")
    print(f"오디오 길이: {duration_str}")
    print(f"RTF: {rtf_str}")
    print(f"메모리: {memory_str}")
    print("-" * 45)
    print("인식 결과:")
    print(f'"{recognized_text}"')
    print("-" * 45)
    print(f"결과 저장: {output_json_path}")
    print("=" * 45)


def save_results_json(output_path: str, audio_path: str, load_time: float,
                      infer_time: float, audio_duration: float,
                      recognized_text: str, memory_gb: float):
    """결과를 JSON 파일로 저장"""
    print("[4/4] 결과 JSON 저장 중...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    rtf = infer_time / audio_duration if audio_duration > 0 else None
    realtime_ratio = audio_duration / infer_time if (audio_duration > 0 and infer_time > 0) else None

    result = {
        "model": "iic/SenseVoiceSmall",
        "device": "cpu",
        "audio_file": os.path.abspath(audio_path),
        "metrics": {
            "model_load_time_sec": round(load_time, 3),
            "inference_time_sec": round(infer_time, 3),
            "audio_duration_sec": round(audio_duration, 3) if audio_duration > 0 else None,
            "rtf": round(rtf, 4) if rtf is not None else None,
            "realtime_ratio": round(realtime_ratio, 2) if realtime_ratio is not None else None,
            "memory_gb": round(memory_gb, 3) if memory_gb >= 0 else None,
        },
        "recognized_text": recognized_text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    # 결과 저장 경로 (스크립트 위치 기준)
    script_dir = Path(__file__).parent
    output_json_path = str(script_dir / "results" / "sensevoice_result.json")

    # 인자 검증
    if len(sys.argv) < 2:
        print("[오류] 오디오 파일 경로를 인자로 제공하세요.")
        print("사용법: python poc_sensevoice.py <오디오 파일 경로>")
        print("예시:   python poc_sensevoice.py poc/audio_samples/meeting.wav")
        suggest_sample_tts()
        sys.exit(1)

    audio_path = sys.argv[1]

    # 파일 존재 확인
    if not os.path.isfile(audio_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {audio_path}")
        suggest_sample_tts()
        sys.exit(1)

    print(f"오디오 파일: {audio_path}")

    # 오디오 길이 측정 (추론 전 미리 측정)
    audio_duration = get_audio_duration(audio_path)

    # 메모리 기준점 (모델 로드 전)
    mem_before = get_memory_usage_gb()

    # 모델 로드
    try:
        model, load_time = load_model()
    except (ImportError, RuntimeError) as e:
        print(f"\n[치명적 오류] {e}")
        sys.exit(1)

    # 추론 실행
    try:
        recognized_text, infer_time = run_inference(model, audio_path)
    except (ValueError, RuntimeError) as e:
        print(f"\n[치명적 오류] {e}")
        sys.exit(1)

    # 메모리 사용량 (추론 후)
    memory_gb = get_memory_usage_gb()

    # 콘솔 출력
    print_results(
        audio_path=audio_path,
        load_time=load_time,
        infer_time=infer_time,
        audio_duration=audio_duration,
        recognized_text=recognized_text,
        memory_gb=memory_gb,
        output_json_path=output_json_path,
    )

    # JSON 저장
    save_results_json(
        output_path=output_json_path,
        audio_path=audio_path,
        load_time=load_time,
        infer_time=infer_time,
        audio_duration=audio_duration,
        recognized_text=recognized_text,
        memory_gb=memory_gb,
    )


if __name__ == "__main__":
    main()
