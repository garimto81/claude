# -*- coding: utf-8 -*-
"""
POC: Qwen 회의 요약 성능 검증 스크립트
로컬 Ollama/Qwen 3.5 (localhost:9000)의 회의 요약 성능을 3가지 시나리오로 검증합니다.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import time
from datetime import datetime
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:9000/v1"
MODEL = "qwen3.5:9b"
TEMPERATURE = 0.3
RESULTS_DIR = Path(__file__).parent / "results"

SYSTEM_PROMPT = (
    "당신은 회의 내용을 실시간으로 요약하는 AI 비서입니다.\n"
    "핵심 결정사항, Action Item, 다음 단계를 포함하여 간결하게 요약하세요."
)

# ---------------------------------------------------------------------------
# 샘플 회의 텍스트
# ---------------------------------------------------------------------------
SCENARIO_A = (
    "김팀장: 이번 분기 매출 목표 달성률이 85%입니다. "
    "박대리: 신규 거래처 3곳 확보했습니다. "
    "김팀장: 좋습니다. 다음 주까지 잔여 목표 달성 계획서 제출해주세요."
)

SCENARIO_B = (
    "김팀장: 오늘 회의 안건은 세 가지입니다. 첫째 분기 실적 리뷰, 둘째 신규 프로젝트 킥오프, "
    "셋째 인력 충원 계획입니다. "
    "박대리: 분기 매출은 전년 대비 12% 성장했고, 영업이익률은 8.5%입니다. "
    "이과장: 신규 프로젝트 A는 4월 1일 시작 예정이며, 프론트엔드 2명, 백엔드 3명이 필요합니다. "
    "최차장: HR에서 3월 중 채용 공고 올릴 예정입니다. 면접은 4월 둘째 주로 잡겠습니다. "
    "김팀장: 프로젝트 A 일정이 빠듯한데, 외주 인력도 검토해봅시다. "
    "다음 회의는 다음 주 화요일 같은 시간에 하겠습니다."
)

SCENARIO_C = (
    "김팀장: 오늘 회의 안건은 다섯 가지입니다. 분기 실적 리뷰, 신규 프로젝트 킥오프, "
    "인력 충원 계획, 예산 배분, 리스크 관리입니다. "
    "박대리: 분기 매출은 전년 대비 12% 성장했고, 영업이익률은 8.5%입니다. "
    "고객 만족도 점수는 4.2/5.0으로 전분기 대비 0.3점 상승했습니다. "
    "이과장: 신규 프로젝트 A는 4월 1일 시작 예정이며, 기술 스택은 React, FastAPI, PostgreSQL로 결정했습니다. "
    "프론트엔드 2명, 백엔드 3명, DevOps 1명이 필요합니다. "
    "마일스톤은 5월 MVP, 7월 베타, 9월 정식 출시입니다. "
    "최차장: HR에서 3월 중 채용 공고 올릴 예정입니다. 면접은 4월 둘째 주로 잡겠습니다. "
    "외주 인력 단가는 프리랜서 기준 월 600~800만 원이며, 3개월 계약을 검토 중입니다. "
    "정과장: 예산 배분안입니다. 개발 인건비 1.2억, 인프라 2천만, 마케팅 3천만, 예비비 1천만으로 총 1.8억입니다. "
    "CFO 보고는 내주 금요일 예정입니다. "
    "김팀장: 리스크 관리 측면에서 주요 우려사항을 짚어봅시다. "
    "첫째, 채용 지연 시 프로젝트 일정 영향. 둘째, 외주 인력 온보딩 리스크. "
    "셋째, 기술 스택 변경 가능성. 각 리스크별 플랜 B를 다음 주까지 문서화해주세요. "
    "이과장: 이해관계자 보고 일정은 월별 경영진 보고, 분기별 이사회 보고로 잡겠습니다. "
    "대시보드는 Notion과 Jira를 연동해 실시간 현황 공유하겠습니다. "
    "김팀장: 수고하셨습니다. Action Item 정리하겠습니다. "
    "박대리는 분기 실적 보고서 최종본 금주 내 제출, "
    "이과장은 기술 스택 아키텍처 문서 작성 및 리스크 플랜 B 다음 주 월요일까지, "
    "최차장은 채용 공고 3월 15일 오픈, "
    "정과장은 CFO 보고 자료 내주 수요일까지 준비. "
    "다음 회의는 다음 주 화요일 오전 10시 같은 장소에서 하겠습니다. "
    "한가지 추가 안건으로, 최근 고객사 A에서 요청한 커스터마이징 기능 일정도 조율이 필요합니다. "
    "이과장: 고객사 A 요청 기능은 총 5개이며, 난이도 상 2개, 중 2개, 하 1개입니다. "
    "기존 로드맵에 편입하면 베타 출시가 2주 지연될 수 있습니다. "
    "김팀장: 고객사 A는 연간 계약 규모가 커서 우선순위를 높여야 합니다. "
    "이과장과 박대리가 협력해 영향 범위 분석서를 목요일까지 제출해주세요. "
    "정과장: 고객사 A 커스터마이징 비용은 별도 청구 가능한지 계약서를 검토하겠습니다. "
    "결과는 다음 회의 전까지 공유하겠습니다."
)

SCENARIOS = [
    {"name": "A", "label": "짧은 회의", "text": SCENARIO_A},
    {"name": "B", "label": "중간 회의", "text": SCENARIO_B},
    {"name": "C", "label": "긴 회의",   "text": SCENARIO_C},
]


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------
def estimate_tokens(text: str) -> int:
    """한국어 포함 텍스트의 토큰 수 근사치 (글자 수 / 2)."""
    return max(1, len(text) // 2)


def check_ollama() -> bool:
    """Ollama 서버 연결 여부 확인."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/models", timeout=5)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def measure_ttft(meeting_text: str) -> float:
    """스트리밍 모드로 첫 토큰 지연시간(TTFT) 측정."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"다음 회의 내용을 요약해주세요:\n\n{meeting_text}"},
        ],
        "temperature": TEMPERATURE,
        "stream": True,
    }
    t0 = time.time()
    try:
        with requests.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            json=payload,
            stream=True,
            timeout=60,
        ) as resp:
            for chunk in resp.iter_lines():
                if chunk and chunk != b"data: [DONE]":
                    raw = chunk.decode("utf-8", errors="replace")
                    if raw.startswith("data: "):
                        raw = raw[6:]
                    try:
                        data = json.loads(raw)
                        delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            return round(time.time() - t0, 3)
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    return -1.0


def run_scenario(scenario: dict) -> dict:
    """단일 시나리오 실행 후 결과 반환."""
    name  = scenario["name"]
    label = scenario["label"]
    text  = scenario["text"]

    input_tokens = estimate_tokens(text)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"다음 회의 내용을 요약해주세요:\n\n{text}"},
        ],
        "temperature": TEMPERATURE,
        "stream": False,
    }

    t_start = time.time()
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            json=payload,
            timeout=120,
        )
        elapsed = round(time.time() - t_start, 2)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        print(f"\n[오류] Ollama 서버에 연결할 수 없습니다 ({OLLAMA_BASE_URL}).")
        print("       Ollama가 실행 중인지, 포트가 9000인지 확인하세요.")
        raise SystemExit(1)
    except requests.exceptions.Timeout:
        print(f"\n[오류] 시나리오 {name} 응답 타임아웃 (120초 초과).")
        raise SystemExit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[오류] HTTP 오류: {e}")
        raise SystemExit(1)

    summary = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    summary_tokens = estimate_tokens(summary)
    ratio = round(summary_tokens / input_tokens * 100, 1) if input_tokens else 0

    # TTFT (스트리밍)
    ttft = measure_ttft(text)

    result = {
        "scenario": name,
        "label": label,
        "input_length": len(text),
        "input_tokens_approx": input_tokens,
        "response_time_sec": elapsed,
        "ttft_sec": ttft,
        "summary_length": len(summary),
        "summary_tokens_approx": summary_tokens,
        "compression_ratio_pct": ratio,
        "summary": summary,
    }

    # 콘솔 출력
    print(f"\n[시나리오 {name}: {label}]")
    print(f"  입력: ~{input_tokens} 토큰 ({len(text)}자)")
    print(f"  응답 시간: {elapsed}초")
    print(f"  TTFT: {ttft if ttft >= 0 else 'N/A'}초")
    print(f"  요약 비율: {ratio}%")
    print(f"  요약:")
    print(f"    \"{summary}\"")
    print("-" * 60)

    return result


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("=== Qwen 회의 요약 POC ===")
    print(f"모델: {MODEL} ({OLLAMA_BASE_URL})")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not check_ollama():
        print("\n[오류] Ollama 서버에 연결할 수 없습니다.")
        print(f"       URL: {OLLAMA_BASE_URL}")
        print("       아래 사항을 확인하세요:")
        print("         1. Ollama가 실행 중인지: `ollama serve`")
        print("         2. 포트가 9000인지 (기본 11434 아님)")
        print(f"         3. 모델 설치 여부: `ollama pull {MODEL}`")
        raise SystemExit(1)

    print("\nOllama 서버 연결 확인.")

    results = []
    for scenario in SCENARIOS:
        result = run_scenario(scenario)
        results.append(result)

    # 결과 저장
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "qwen_summary_result.json"
    output = {
        "meta": {
            "model": MODEL,
            "base_url": OLLAMA_BASE_URL,
            "temperature": TEMPERATURE,
            "run_at": datetime.now().isoformat(),
        },
        "scenarios": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장 완료: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
