# -*- coding: utf-8 -*-
"""
Whisper 한국어 STT 비교 POC 스크립트
목적: faster-whisper 기반 한국어 STT 모델 3종 성능 비교
사용법:
  python poc_whisper_korean.py <오디오 파일 경로>                # 2분 샘플 비교 테스트
  python poc_whisper_korean.py <오디오 파일 경로> --full-test    # 최고 모델로 전체 오디오 처리
"""

import sys
import json
import time
import os
from pathlib import Path

# Windows cp949 콘솔에서 인코딩 불가 문자 제거
def _safe(text: str) -> str:
    """콘솔 인코딩에서 표현 불가한 문자를 ?로 대체"""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(enc, errors="replace").decode(enc, errors="replace")

# CUDA DLL 경로를 PATH에 추가 (pip nvidia-cublas-cu12 설치 시 필요)
_nvidia_path = Path(sys.prefix) / "Lib/site-packages/nvidia"
if _nvidia_path.exists():
    _dll_dirs = []
    for sub in ("cublas/bin", "cudnn/bin", "cuda_runtime/bin"):
        dll_dir = _nvidia_path / sub
        if dll_dir.exists():
            _dll_dirs.append(str(dll_dir))
            os.add_dll_directory(str(dll_dir))
    if _dll_dirs:
        os.environ["PATH"] = ";".join(_dll_dirs) + ";" + os.environ.get("PATH", "")


# ---------------------------------------------------------------------------
# 유틸리티
# ---------------------------------------------------------------------------

def get_memory_usage_gb() -> float:
    """현재 프로세스 CPU 메모리 사용량(GB) 반환"""
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss / (1024 ** 3)
    except ImportError:
        return -1.0


def get_gpu_vram_gb() -> float:
    """현재 GPU VRAM 사용량(GB) 반환 (CUDA only)"""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 ** 3)
    except ImportError:
        pass
    return -1.0


def get_audio_duration(audio_path: str) -> float:
    """오디오 파일 길이(초) 반환 -ffprobe 우선, 실패 시 wave 시도"""
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", audio_path],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        pass
    try:
        import wave
        with wave.open(audio_path, "r") as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# 모델 테스트 함수
# ---------------------------------------------------------------------------

TEST_CONFIGS = [
    {
        "id": "A",
        "name": "ghost613/faster-whisper-large-v3-turbo-korean (GPU fp16)",
        "model_id": "ghost613/faster-whisper-large-v3-turbo-korean",
        "device": "cuda",
        "compute_type": "float16",
        "description": "한국어 파인튜닝 turbo 모델 (GPU fp16)",
    },
    {
        "id": "B",
        "name": "openai/whisper-large-v3 (GPU fp16)",
        "model_id": "large-v3",
        "device": "cuda",
        "compute_type": "float16",
        "description": "OpenAI Whisper large-v3 원본 (GPU fp16)",
    },
    {
        "id": "C",
        "name": "ghost613/faster-whisper-large-v3-turbo-korean (CPU INT8)",
        "model_id": "ghost613/faster-whisper-large-v3-turbo-korean",
        "device": "cpu",
        "compute_type": "int8",
        "description": "한국어 파인튜닝 turbo 모델 (CPU INT8)",
    },
    {
        "id": "D",
        "name": "openai/whisper-large-v3 (CPU INT8)",
        "model_id": "large-v3",
        "device": "cpu",
        "compute_type": "int8",
        "description": "OpenAI Whisper large-v3 원본 (CPU INT8)",
    },
]

# --cpu-only 플래그로 GPU 테스트 스킵 가능
CPU_ONLY_CONFIGS = [c for c in TEST_CONFIGS if c["device"] == "cpu"]


def free_gpu_memory():
    """GPU 메모리를 해제하여 다음 모델 테스트 준비"""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass
    import gc
    gc.collect()


def run_single_test(config: dict, audio_path: str) -> dict:
    """단일 모델 테스트 실행 -결과 dict 반환"""
    from faster_whisper import WhisperModel

    test_id = config["id"]
    print(f"\n{'='*60}")
    print(f"[테스트 {test_id}] {config['name']}")
    print(f"  디바이스: {config['device']}, 연산: {config['compute_type']}")
    print(f"{'='*60}")

    # 모델 로드
    print(f"  [1/3] 모델 로드 중...")
    mem_before = get_memory_usage_gb()
    vram_before = get_gpu_vram_gb()
    t_load = time.time()

    try:
        model = WhisperModel(
            config["model_id"],
            device=config["device"],
            compute_type=config["compute_type"],
        )
    except Exception as e:
        print(f"  [오류] 모델 로드 실패: {e}")
        return {"id": test_id, "error": str(e)}

    load_time = time.time() - t_load
    print(f"  모델 로드 완료: {load_time:.1f}초")

    # 추론
    print(f"  [2/3] STT 추론 중...")
    t_infer = time.time()
    try:
        segments, info = model.transcribe(
            audio_path,
            language="ko",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
    except (RuntimeError, OSError) as e:
        print(f"  [오류] 추론 실패: {e}")
        del model
        free_gpu_memory()
        return {"id": test_id, "error": str(e)}

    # 세그먼트 수집 (제너레이터이므로 순회 필요)
    segment_list = []
    full_text_parts = []
    try:
        for seg in segments:
            segment_list.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            })
            full_text_parts.append(seg.text.strip())
    except (RuntimeError, OSError) as e:
        print(f"  [오류] 세그먼트 처리 중 실패: {e}")
        del model
        free_gpu_memory()
        return {"id": test_id, "error": str(e)}

    infer_time = time.time() - t_infer
    full_text = " ".join(full_text_parts)

    # 메모리 측정
    mem_after = get_memory_usage_gb()
    vram_after = get_gpu_vram_gb()

    # 오디오 길이
    audio_duration = get_audio_duration(audio_path)
    rtf = infer_time / audio_duration if audio_duration > 0 else None

    # 결과 출력
    print(f"  [3/3] 결과:")
    print(f"  추론 시간: {infer_time:.1f}초")
    if audio_duration > 0:
        print(f"  오디오 길이: {audio_duration:.1f}초")
        print(f"  RTF: {rtf:.4f} ({audio_duration/infer_time:.1f}x 실시간)")
    if config["device"] == "cuda" and vram_after >= 0:
        print(f"  VRAM: {vram_after:.2f}GB (증가분: {vram_after - vram_before:.2f}GB)")
    if mem_after >= 0:
        print(f"  RAM: {mem_after:.2f}GB (증가분: {mem_after - mem_before:.2f}GB)")
    print(f"  세그먼트 수: {len(segment_list)}")
    print(f"  언어 확률: {info.language_probability:.2%}")
    print(f"\n  인식 결과:")
    # 긴 텍스트는 처음/마지막만 미리보기 (_safe로 인코딩 안전 보장)
    safe_text = _safe(full_text)
    if len(safe_text) > 300:
        print(f'  "{safe_text[:150]}..."')
        print(f'  "...{safe_text[-150:]}"')
    else:
        print(f'  "{safe_text}"')

    # 모델 해제
    del model
    free_gpu_memory()

    return {
        "id": test_id,
        "name": config["name"],
        "model_id": config["model_id"],
        "device": config["device"],
        "compute_type": config["compute_type"],
        "metrics": {
            "model_load_time_sec": round(load_time, 3),
            "inference_time_sec": round(infer_time, 3),
            "audio_duration_sec": round(audio_duration, 3) if audio_duration > 0 else None,
            "rtf": round(rtf, 4) if rtf is not None else None,
            "realtime_ratio": round(audio_duration / infer_time, 2) if (rtf and infer_time > 0) else None,
            "vram_gb": round(vram_after, 3) if vram_after >= 0 else None,
            "ram_gb": round(mem_after, 3) if mem_after >= 0 else None,
            "language_probability": round(info.language_probability, 4),
        },
        "segments_count": len(segment_list),
        "segments": segment_list,
        "full_text": full_text,
    }


# ---------------------------------------------------------------------------
# 비교 테스트 (Step 2)
# ---------------------------------------------------------------------------

def run_comparison_test(audio_path: str, configs: list[dict] | None = None) -> list[dict]:
    """모델 설정 목록으로 동일 오디오 순차 테스트"""
    configs = configs or TEST_CONFIGS
    print(f"\n{'#'*60}")
    print(f"# Whisper 한국어 STT 비교 POC ({len(configs)}종)")
    print(f"# 오디오: {os.path.basename(audio_path)}")
    print(f"{'#'*60}")

    results = []
    for config in configs:
        result = run_single_test(config, audio_path)
        results.append(result)

    return results


def print_comparison_summary(results: list[dict]):
    """비교 결과 요약 테이블 출력"""
    print(f"\n{'='*60}")
    print("비교 결과 요약")
    print(f"{'='*60}")
    print(f"{'테스트':<8} {'모델':<25} {'디바이스':<10} {'추론(초)':<10} {'RTF':<10} {'세그먼트':<8}")
    print("-" * 60)

    for r in results:
        if "error" in r:
            print(f"{r['id']:<8} {'오류':<25} {'-':<10} {'-':<10} {'-':<10} {'-':<8}")
            continue
        m = r["metrics"]
        rtf_str = f"{m['rtf']:.4f}" if m["rtf"] else "-"
        print(f"{r['id']:<8} {r['name'][:24]:<25} {r['device']:<10} {m['inference_time_sec']:<10.1f} {rtf_str:<10} {r['segments_count']:<8}")

    print(f"{'='*60}")

    # 최고 모델 선정 (RTF 기준 -오류 제외)
    valid = [r for r in results if "error" not in r and r["metrics"]["rtf"] is not None]
    if valid:
        best = min(valid, key=lambda r: r["metrics"]["rtf"])
        print(f"\n최고 성능: 테스트 {best['id']} -{best['name']}")
        print(f"  RTF: {best['metrics']['rtf']:.4f}, 추론: {best['metrics']['inference_time_sec']:.1f}초")


def select_best_model(results: list[dict]) -> dict | None:
    """비교 결과에서 최고 모델 설정 반환 (GPU 모델 우선, RTF 기준)"""
    valid = [r for r in results if "error" not in r and r["metrics"]["rtf"] is not None]
    if not valid:
        return None
    # GPU 모델 중 최고 RTF 선택 (GPU 없으면 전체에서)
    gpu_valid = [r for r in valid if r["device"] == "cuda"]
    pool = gpu_valid if gpu_valid else valid
    return min(pool, key=lambda r: r["metrics"]["rtf"])


# ---------------------------------------------------------------------------
# 전체 오디오 테스트 (Step 3)
# ---------------------------------------------------------------------------

def run_full_audio_test(audio_path: str, best_result: dict) -> dict:
    """최고 모델로 전체 52분 오디오 처리"""
    from faster_whisper import WhisperModel

    print(f"\n{'#'*60}")
    print(f"# 전체 오디오 테스트 (Step 3)")
    print(f"# 모델: {best_result['name']}")
    print(f"# 오디오: {os.path.basename(audio_path)}")
    print(f"{'#'*60}")

    # 모델 로드
    print("[1/3] 모델 로드 중...")
    t_load = time.time()
    model = WhisperModel(
        best_result["model_id"],
        device=best_result["device"],
        compute_type=best_result["compute_type"],
    )
    load_time = time.time() - t_load
    print(f"  로드 완료: {load_time:.1f}초")

    # 추론 (VAD 활성화 -긴 오디오 필수)
    print("[2/3] 전체 오디오 STT 처리 중 (VAD 활성화)...")
    t_infer = time.time()
    segments, info = model.transcribe(
        audio_path,
        language="ko",
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    segment_list = []
    full_text_parts = []
    seg_count = 0
    for seg in segments:
        segment_list.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
        full_text_parts.append(seg.text.strip())
        seg_count += 1
        if seg_count % 50 == 0:
            print(f"  처리 중... {seg_count}개 세그먼트 ({seg.end:.0f}초 지점)")

    infer_time = time.time() - t_infer
    full_text = " ".join(full_text_parts)
    audio_duration = get_audio_duration(audio_path)
    rtf = infer_time / audio_duration if audio_duration > 0 else None

    # 결과 출력
    print(f"\n[3/3] 전체 오디오 처리 완료:")
    print(f"  추론 시간: {infer_time:.1f}초")
    if audio_duration > 0:
        print(f"  오디오 길이: {audio_duration:.1f}초 ({audio_duration/60:.1f}분)")
        print(f"  RTF: {rtf:.4f} ({audio_duration/infer_time:.1f}x 실시간)")
    print(f"  세그먼트 수: {len(segment_list)}")
    print(f"  총 글자 수: {len(full_text)}")
    print(f"\n  처음 300자:")
    print(f'  "{_safe(full_text[:300])}"')

    del model
    free_gpu_memory()

    return {
        "model": best_result["name"],
        "model_id": best_result["model_id"],
        "device": best_result["device"],
        "compute_type": best_result["compute_type"],
        "audio_file": os.path.abspath(audio_path),
        "metrics": {
            "model_load_time_sec": round(load_time, 3),
            "inference_time_sec": round(infer_time, 3),
            "audio_duration_sec": round(audio_duration, 3) if audio_duration > 0 else None,
            "rtf": round(rtf, 4) if rtf is not None else None,
            "realtime_ratio": round(audio_duration / infer_time, 2) if (rtf and infer_time > 0) else None,
        },
        "segments_count": len(segment_list),
        "segments": segment_list,
        "full_text": full_text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).parent
    output_dir = script_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) < 2:
        print("[오류] 오디오 파일 경로를 인자로 제공하세요.")
        print("사용법:")
        print("  python poc_whisper_korean.py <2분 샘플.wav>              # 3종 비교 테스트")
        print("  python poc_whisper_korean.py <전체 오디오.m4a> --full-test  # 최고 모델로 전체 처리")
        sys.exit(1)

    audio_path = sys.argv[1]
    full_test_mode = "--full-test" in sys.argv
    cpu_only_mode = "--cpu-only" in sys.argv

    if not os.path.isfile(audio_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {audio_path}")
        sys.exit(1)

    if full_test_mode:
        # --full-test: 비교 테스트 결과 large-v3가 최고 정확도
        # --model-id 인자가 있으면 해당 모델, 없으면 large-v3 CPU INT8
        model_override = None
        for i, arg in enumerate(sys.argv):
            if arg == "--model-id" and i + 1 < len(sys.argv):
                model_override = sys.argv[i + 1]
        if model_override:
            cfg = {"name": model_override, "model_id": model_override,
                   "device": "cpu", "compute_type": "int8"}
        else:
            # large-v3 CPU INT8 (비교 테스트 최고 정확도 모델)
            cfg = {"name": "openai/whisper-large-v3 (CPU INT8)",
                   "model_id": "large-v3", "device": "cpu", "compute_type": "int8"}
        best_config = {
            "name": cfg["name"],
            "model_id": cfg["model_id"],
            "device": cfg["device"],
            "compute_type": cfg["compute_type"],
        }
        full_result = run_full_audio_test(audio_path, best_config)

        # 결과 저장
        output_path = str(output_dir / "whisper_korean_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        print(f"\n결과 저장: {output_path}")

    else:
        # 비교 테스트 모드 (기본)
        configs = CPU_ONLY_CONFIGS if cpu_only_mode else TEST_CONFIGS
        results = run_comparison_test(audio_path, configs)
        print_comparison_summary(results)

        # 비교 결과 저장
        comparison_output = str(output_dir / "whisper_comparison_result.json")
        save_data = {
            "audio_file": os.path.abspath(audio_path),
            "tests": results,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(comparison_output, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"\n비교 결과 저장: {comparison_output}")

        # 최고 모델 안내
        best = select_best_model(results)
        if best:
            print(f"\n다음 단계: 최고 모델로 전체 52분 오디오 테스트")
            print(f'  python poc_whisper_korean.py "audio_samples/음성 260316_113405.m4a" --full-test')


if __name__ == "__main__":
    main()
