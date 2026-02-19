import re
from pathlib import Path
from typing import Optional

# 토큰 임계값
THRESHOLD_CHUNK = 60_000       # 이 이상 → 청킹 필요
THRESHOLD_CHUNK_CONSERVATIVE = 40_000  # tiktoken 미설치 시 보수적 임계값
THRESHOLD_COMBO = 100_000      # 이 이상 → 조합 전략

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def estimate_tokens(text: str, encoding: str = "cl100k_base") -> int:
    if TIKTOKEN_AVAILABLE:
        enc = tiktoken.get_encoding(encoding)
        return len(enc.encode(text))
    else:
        # 간이 추정: 평균 3자 = 1토큰
        return len(text) // 3


def detect_prd_structure(text: str) -> dict:
    lines = text.split('\n')
    heading_count = sum(1 for l in lines if l.startswith('#'))
    h2_count = sum(1 for l in lines if l.startswith('## '))
    has_table = any('|---|' in l or '|:---|' in l or '|---:|' in l for l in lines)
    has_req_numbers = bool(re.search(r'\b(R\d+|NR\d+|SC\d+|C\d+)\b', text))
    table_line_count = sum(1 for l in lines if l.strip().startswith('|'))
    is_heavy_table = table_line_count > len(lines) * 0.2

    prd_score = 0
    if heading_count >= 3:    prd_score += 1
    if has_req_numbers:       prd_score += 2
    if has_table:             prd_score += 1
    if h2_count >= 2:         prd_score += 1

    return {
        "prd_score": prd_score,
        "heading_count": heading_count,
        "has_req_numbers": has_req_numbers,
        "has_table": has_table,
        "is_heavy_table": is_heavy_table,
        "h2_count": h2_count,
    }


def auto_select_strategy(file_path: str, text: Optional[str] = None) -> str:
    path = Path(file_path)
    if text is None:
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return "fixed"

    token_count = estimate_tokens(text)
    threshold = THRESHOLD_CHUNK if TIKTOKEN_AVAILABLE else THRESHOLD_CHUNK_CONSERVATIVE

    if token_count < threshold:
        return "none"

    info = detect_prd_structure(text)

    if info["prd_score"] >= 3 and token_count < THRESHOLD_COMBO:
        return "hierarchical"
    if info["is_heavy_table"] and info["prd_score"] < 3:
        return "semantic"
    if token_count >= THRESHOLD_COMBO:
        return "hierarchical+semantic"

    return "fixed"
