# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
SenseVoice STT + Qwen 요약 통합 파이프라인 POC
목적: 오디오 → STT → 텍스트 버퍼 → LLM 요약 end-to-end 파이프라인 검증
사용법:
  python poc_pipeline.py <오디오 파일 경로>   # 오디오 모드
  python poc_pipeline.py                      # 텍스트 직접 입력 모드
"""

import sys
import json
import time
import os
from pathlib import Path

# 내장 샘플 회의 텍스트 (텍스트 직접 입력 모드용)
SAMPLE_MEETING_TEXT = """
김부장: 그러면 오늘 회의를 시작하겠습니다. 첫 번째 안건은 이번 분기 실적 리뷰입니다.
매출은 전분기 대비 12% 증가했고, 영업이익률은 8.5%를 기록했습니다.

이과장: 마케팅 캠페인 효과가 컸습니다. 특히 온라인 채널 매출이 35% 성장했는데,
이는 지난달 진행한 타겟 광고의 성과로 보입니다. 다만 오프라인 매장은 5% 감소했습니다.

박대리: 고객 만족도 조사 결과도 공유드리면, NPS가 72점으로 전분기 대비 8점 상승했습니다.
특히 배송 속도 개선에 대한 긍정적 피드백이 많았습니다.

김부장: 좋은 성과네요. 두 번째 안건으로 넘어가서, 신규 프로젝트 킥오프 건입니다.
AI 기반 고객 서비스 자동화 프로젝트를 다음 달부터 시작하려고 합니다.

이과장: 기술 스택은 어떻게 구성할 예정인가요? 기존 시스템과의 연동도 고려해야 합니다.

박대리: 현재 CRM 시스템이 레거시라서 API 연동에 시간이 걸릴 수 있습니다.
최소 2주 정도 사전 조사가 필요할 것 같습니다.

김부장: 알겠습니다. 사전 조사 기간을 포함해서 전체 일정을 다시 수립합시다.
마지막 안건은 인력 충원 계획입니다. 개발팀에서 2명, 디자인팀에서 1명 충원 요청이 있었습니다.

이과장: 개발팀은 시니어 백엔드 1명, 주니어 프론트엔드 1명이 필요합니다.
현재 업무량 대비 인력이 부족해서 야근이 잦은 상황입니다.

박대리: 디자인팀도 UX 리서처 1명이 시급합니다. 사용자 테스트를 제대로 못하고 있어서
제품 품질에 영향을 주고 있습니다.

김부장: 인사팀에 채용 요청서를 이번 주 내로 제출하겠습니다. 다른 의견 없으시면 회의를 마치겠습니다.
""".strip()

# 버퍼 임계치
BUFFER_CHAR_THRESHOLD = 500


def get_memory_usage_gb() -> float:
    """현재 프로세스 CPU 메모리 사용량(GB) 반환"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 ** 3)
    except ImportError:
        return -1.0


def get_cpu_percent() -> float:
    """현재 프로세스 CPU 사용률(%) 반환"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.cpu_percent(interval=0.1)
    except ImportError:
        return -1.0


class MeetingPipeline:
    """STT → 텍스트 버퍼 → Qwen 요약 통합 파이프라인"""

    def __init__(self):
        self.stt_model = None  # lazy load
        self.text_buffer = []
        self.buffer_char_count = 0
        self.summaries = []
        self.ollama_url = "http://localhost:9000/v1/chat/completions"
        self.metrics = {
            "stt_time_sec": 0.0,
            "summarize_times_sec": [],
            "total_time_sec": 0.0,
            "memory_before_gb": -1.0,
            "memory_after_gb": -1.0,
            "cpu_percent": -1.0,
        }

    def load_stt(self):
        """SenseVoice-Small 모델 로드 (CPU)"""
        print("[STT] FunASR SenseVoice-Small 모델 로드 중...")
        try:
            from funasr import AutoModel
            self.stt_model = AutoModel(
                model="iic/SenseVoiceSmall",
                device="cpu",
                disable_update=True,
            )
            print("[STT] 모델 로드 완료")
        except ImportError:
            raise ImportError("FunASR 미설치. 설치: pip install funasr")

    def transcribe(self, audio_path: str) -> str:
        """오디오 파일 → STT → 텍스트 반환 + 버퍼에 추가"""
        if self.stt_model is None:
            self.load_stt()

        print(f"[STT] 추론 실행: {os.path.basename(audio_path)}")
        t_start = time.time()

        try:
            res = self.stt_model.generate(input=audio_path, language="ko")
        except Exception as e:
            raise RuntimeError(f"STT 추론 실패: {e}")

        stt_time = time.time() - t_start
        self.metrics["stt_time_sec"] = round(stt_time, 3)

        # FunASR 결과 파싱
        if isinstance(res, list) and len(res) > 0:
            text = res[0].get("text", "").strip()
        elif isinstance(res, dict):
            text = res.get("text", "").strip()
        else:
            text = str(res).strip()

        print(f"[STT] 완료 ({stt_time:.1f}초), 인식 텍스트 {len(text)}자")

        # 버퍼에 추가
        self._add_to_buffer(text)
        return text

    def _add_to_buffer(self, text: str):
        """텍스트를 버퍼에 추가"""
        self.text_buffer.append(text)
        self.buffer_char_count += len(text)
        print(f"[버퍼] 현재 {self.buffer_char_count}자 축적")

    def should_summarize(self) -> bool:
        """버퍼 임계치 초과 여부"""
        return self.buffer_char_count >= BUFFER_CHAR_THRESHOLD

    def summarize(self) -> str:
        """버퍼의 텍스트를 Qwen으로 요약"""
        if not self.text_buffer:
            return ""

        full_text = "\n".join(self.text_buffer)
        print(f"[요약] Qwen 요약 호출 중 ({len(full_text)}자)...")

        t_start = time.time()

        try:
            import urllib.request
            payload = json.dumps({
                "model": "qwen3.5:9b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "당신은 회의 내용을 요약하는 전문가입니다. "
                            "핵심 논의사항, 결정사항, 후속 조치를 간결하게 정리하세요."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"다음 회의 내용을 요약해주세요:\n\n{full_text}",
                    },
                ],
                "temperature": 0.3,
            }).encode("utf-8")

            req = urllib.request.Request(
                self.ollama_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                summary = result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            summary = f"[요약 실패] Ollama 서버 연결 오류: {e}"
            print(f"[요약] 오류 발생: {e}")

        summarize_time = time.time() - t_start
        self.metrics["summarize_times_sec"].append(round(summarize_time, 3))
        print(f"[요약] 완료 ({summarize_time:.1f}초)")

        self.summaries.append(summary)

        # 버퍼 초기화
        self.text_buffer.clear()
        self.buffer_char_count = 0

        return summary

    def run(self, audio_path: str = None):
        """전체 파이프라인 실행"""
        t_total_start = time.time()
        self.metrics["memory_before_gb"] = get_memory_usage_gb()

        if audio_path:
            # 오디오 모드: STT → 버퍼 → 요약
            print(f"\n{'='*50}")
            print("  STT + 요약 파이프라인 (오디오 모드)")
            print(f"{'='*50}")
            print(f"입력: {audio_path}\n")

            # Step 1: STT
            self.transcribe(audio_path)

            # Step 2-3: 버퍼 확인 + 요약
            if self.should_summarize():
                self.summarize()
            else:
                print(f"[버퍼] 임계치 미달 ({self.buffer_char_count}/{BUFFER_CHAR_THRESHOLD}), 강제 요약 실행")
                self.summarize()
        else:
            # 텍스트 직접 입력 모드
            print(f"\n{'='*50}")
            print("  STT + 요약 파이프라인 (텍스트 모드)")
            print(f"{'='*50}")
            print("오디오 파일 없이 텍스트 모드로 실행합니다\n")

            # 텍스트를 청크로 분할하여 버퍼 시뮬레이션
            lines = SAMPLE_MEETING_TEXT.split("\n")
            chunk = []
            for line in lines:
                chunk.append(line)
                chunk_text = "\n".join(chunk)
                if len(chunk_text) >= BUFFER_CHAR_THRESHOLD:
                    self._add_to_buffer(chunk_text)
                    chunk = []
                    if self.should_summarize():
                        self.summarize()

            # 잔여 텍스트 처리
            if chunk:
                remaining = "\n".join(chunk)
                self._add_to_buffer(remaining)
            if self.text_buffer:
                print(f"[버퍼] 잔여 텍스트 강제 요약 실행")
                self.summarize()

        # 측정 완료
        self.metrics["total_time_sec"] = round(time.time() - t_total_start, 3)
        self.metrics["memory_after_gb"] = get_memory_usage_gb()
        self.metrics["cpu_percent"] = get_cpu_percent()

        # 결과 출력
        self._print_results()

        # JSON 저장
        self._save_results(audio_path)

    def _print_results(self):
        """결과 콘솔 출력"""
        print(f"\n{'='*50}")
        print("  파이프라인 결과")
        print(f"{'='*50}")

        if self.metrics["stt_time_sec"] > 0:
            print(f"STT 처리 시간: {self.metrics['stt_time_sec']:.1f}초")

        for i, t in enumerate(self.metrics["summarize_times_sec"]):
            print(f"요약 #{i+1} 처리 시간: {t:.1f}초")

        print(f"전체 지연시간: {self.metrics['total_time_sec']:.1f}초")

        mem_before = self.metrics["memory_before_gb"]
        mem_after = self.metrics["memory_after_gb"]
        if mem_before >= 0 and mem_after >= 0:
            print(f"메모리: {mem_before:.2f}GB → {mem_after:.2f}GB (+{mem_after - mem_before:.2f}GB)")
        cpu = self.metrics["cpu_percent"]
        if cpu >= 0:
            print(f"CPU 사용률: {cpu:.1f}%")

        print(f"\n요약 횟수: {len(self.summaries)}건")
        for i, s in enumerate(self.summaries):
            print(f"\n--- 요약 #{i+1} ---")
            print(s)

        print(f"{'='*50}")

    def _save_results(self, audio_path: str = None):
        """결과 JSON 저장"""
        script_dir = Path(__file__).parent
        output_path = str(script_dir / "results" / "pipeline_result.json")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        result = {
            "mode": "audio" if audio_path else "text",
            "audio_file": os.path.abspath(audio_path) if audio_path else None,
            "metrics": self.metrics,
            "summaries": self.summaries,
            "summary_count": len(self.summaries),
            "buffer_threshold_chars": BUFFER_CHAR_THRESHOLD,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"결과 저장: {output_path}")


def main():
    audio_path = sys.argv[1] if len(sys.argv) >= 2 else None

    if audio_path and not os.path.isfile(audio_path):
        print(f"[오류] 파일을 찾을 수 없습니다: {audio_path}")
        sys.exit(1)

    pipeline = MeetingPipeline()
    pipeline.run(audio_path)


if __name__ == "__main__":
    main()
