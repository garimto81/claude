#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GGM-CSVd v1.3 — Security Patched Version
- Hero/L (10x6) · Villain/R (10x6) 분리 기록
- /next : Google WebApp(op=nextfetch) 호출 → JSON의 csv가 dict 일 경우
         { "HeroX-Y":"<10x6 CSV>", "VillainA-B":"<10x6 CSV>" } 형식 지원
- 기존 단일 csv 문자열 응답도 호환(12열일 경우 자동 분할 시도)

Security Patches (v1.3):
- [HIGH] 슬롯명 정규식 검증 (경로 traversal 방지)
- [HIGH] Content-Length 제한 (10MB, DoS 방지)
- [MEDIUM] split_12_to_6_6 예외 로깅 개선
- [LOW] threading.Event() 사용으로 메모리 시각성 보장
"""

import http.server
import socketserver
import urllib.request
import json
import os
import threading
import queue
import time
import tempfile
import re
from pathlib import Path
from datetime import datetime

APP_NAME = "GGM-CSVd"
APP_VERSION = "1.3.0"

# Security: 슬롯명 검증 패턴 (영문, 숫자, 언더스코어, 하이픈만 허용)
SLOT_NAME_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')

# Security: 최대 요청 바디 크기 (10MB)
MAX_BODY_SIZE = 10 * 1024 * 1024

DEFAULTS = {
    "csv_dir": r"D:/CSV_Practice/CSV",
    "gs_url":  "",
    "rows": 10,
    "cols": 12,            # 단일 csv일 때의 열수(자동 분할 시 참조: 12→6/6)
    "port": 8787,
    "write_mode": "atomic",
    "process_duplicates": True,
    "dedup_window_ms": 0,
    "whitelist": []        # 비워두면 폴더 스캔(Hero*/Villain*)
}

CONF_LOCK = threading.Lock()
CONFIG = DEFAULTS.copy()
CONF_PATH = Path(__file__).with_name("config.json")


def validate_slot_name(name: str) -> bool:
    """
    Security: 슬롯명 검증 (경로 traversal 방지)
    허용: Hero1-1, Villain2_3, Hero_Position
    거부: ../etc/passwd, Hero/../../../tmp, Hero;rm -rf
    """
    if not name:
        return False
    if not SLOT_NAME_PATTERN.match(name):
        return False
    # 추가 검증: 최대 길이
    if len(name) > 64:
        return False
    return True


def load_config():
    global CONFIG
    with CONF_LOCK:
        cfg = DEFAULTS.copy()
        try:
            if CONF_PATH.exists():
                with open(CONF_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k in DEFAULTS.keys():
                        if k in data:
                            cfg[k] = data[k]
        except Exception as e:
            print(f"[WARN] config.json 읽기 실패: {e}", flush=True)
        CONFIG = cfg
        print(f"[CONFIG] {json.dumps(CONFIG, ensure_ascii=False)}", flush=True)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[{now()}] {msg}", flush=True)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, text: str):
    ensure_dir(path.parent)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    data = ("\ufeff" + (text or "")).encode("utf-8")
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass
    os.replace(tmp, str(path))


def blank_csv(rows=10, cols=6) -> str:
    line = ",".join([""] * cols)
    return "\r\n".join([line] * rows) + "\r\n"


def scan_slot_files(base_dir: Path):
    names = []
    if not base_dir.exists():
        return names
    for name in os.listdir(base_dir):
        p = base_dir / name
        if not p.is_file():
            continue
        low = name.lower()
        if not (low.endswith(".csv") or "." not in name):
            continue
        base = name[:-4] if low.endswith(".csv") else name
        # Security: 스캔된 파일명도 검증
        if validate_slot_name(base) and (base.startswith("Hero") or base.startswith("Villain")):
            names.append(base)
    return sorted(set(names))


def pick_target_path(base_dir: Path, slot: str) -> Path:
    # Security: 슬롯명 검증 후 경로 생성
    if not validate_slot_name(slot):
        raise ValueError(f"잘못된 슬롯명: {slot}")
    p_noext = base_dir / slot
    p_csv = base_dir / f"{slot}.csv"
    if p_noext.exists():
        return p_noext
    if p_csv.exists():
        return p_csv
    return p_csv


def fetch_next(gs_url: str, timeout=10.0) -> dict:
    log(f"웹앱 호출 시작...")  # Security: URL 노출 방지
    req = urllib.request.Request(gs_url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8", errors="replace")
    try:
        j = json.loads(data)
    except Exception as e:
        raise RuntimeError(f"웹앱 JSON 파싱 실패: {e}")
    if not isinstance(j, dict) or not j.get("ok"):
        raise RuntimeError("웹앱 응답 ok=false")
    return j


def get_slot_whitelist(csv_dir: Path, cfg: dict):
    wl = cfg.get("whitelist") or []
    if isinstance(wl, list) and wl:
        # Security: whitelist 항목도 검증
        return [str(x) for x in wl if validate_slot_name(str(x))]
    return scan_slot_files(csv_dir)


def split_12_to_6_6(csv_12: str, rows: int, cols12: int):
    """
    12열 CSV를 6+6으로 분할
    Security: 예외 발생 시 로깅 후 None 반환 (조용한 실패 방지)
    """
    if cols12 <= 0:
        log(f"[WARN] split_12_to_6_6: cols12={cols12} (0 이하)")
        return None, None
    if cols12 % 2 != 0:
        log(f"[WARN] split_12_to_6_6: cols12={cols12} (홀수)")
        return None, None

    try:
        lines = csv_12.strip("\r\n").splitlines()
        outL, outR = [], []
        for ln in lines[:rows]:
            cells = ln.split(",")
            if len(cells) < cols12:
                cells += [""] * (cols12 - len(cells))
            L = ",".join(cells[:cols12 // 2])
            R = ",".join(cells[cols12 // 2:cols12])
            outL.append(L)
            outR.append(R)
        return "\r\n".join(outL) + "\r\n", "\r\n".join(outR) + "\r\n"
    except Exception as e:
        log(f"[ERROR] split_12_to_6_6 실패: {e}")
        return None, None


def write_all(csv_dir: Path, rows: int, hero_slot: str, villain_slot: str,
              hero_text: str, villain_text: str, cfg: dict):
    # Security: 슬롯명 검증
    if not validate_slot_name(hero_slot):
        raise ValueError(f"잘못된 Hero 슬롯명: {hero_slot}")
    if not validate_slot_name(villain_slot):
        raise ValueError(f"잘못된 Villain 슬롯명: {villain_slot}")

    all_bases = get_slot_whitelist(csv_dir, cfg)
    if not all_bases:
        all_bases = [hero_slot, villain_slot]
    active = {hero_slot, villain_slot}
    wrote = blanked = 0
    for base in all_bases:
        # Security: 각 base도 재검증
        if not validate_slot_name(base):
            log(f"[WARN] 잘못된 슬롯명 스킵: {base}")
            continue
        path = pick_target_path(csv_dir, base)
        if base in active:
            text = hero_text if base == hero_slot else villain_text
            atomic_write_text(path, text or blank_csv(rows, 6))
            wrote += 1
        else:
            atomic_write_text(path, blank_csv(rows, 6))
            blanked += 1
    return {"wrote": wrote, "blanked": blanked, "hero": hero_slot, "villain": villain_slot}


STATE_LOCK = threading.Lock()
LAST_EXEC_MS = 0
LAST_RESULT = {"ok": False, "reason": "never"}
TASK_Q = queue.Queue(maxsize=0)

# Security: threading.Event()로 메모리 시각성 보장
WORKER_STOP_EVENT = threading.Event()


def perform_next():
    global LAST_RESULT, LAST_EXEC_MS
    with CONF_LOCK:
        cfg = CONFIG.copy()
    csv_dir = Path(cfg["csv_dir"])
    gs_url = cfg["gs_url"]
    rows = int(cfg["rows"])
    cols12 = int(cfg["cols"])

    if not gs_url:
        raise RuntimeError("gs_url 비어있음")
    if not csv_dir.exists():
        raise RuntimeError(f"CSV 폴더 없음: {csv_dir}")

    j = fetch_next(gs_url)
    hero_slot = (j.get("heroSlot") or j.get("hero") or "").strip()
    vill_slot = (j.get("villSlot") or j.get("villain") or "").strip()

    if not hero_slot or not vill_slot:
        raise RuntimeError("hero/villain 슬롯이 응답에 없음")

    # Security: WebApp 응답의 슬롯명도 검증
    if not validate_slot_name(hero_slot):
        raise RuntimeError(f"WebApp 응답의 잘못된 hero 슬롯명: {hero_slot}")
    if not validate_slot_name(vill_slot):
        raise RuntimeError(f"WebApp 응답의 잘못된 villain 슬롯명: {vill_slot}")

    hero_text = villain_text = ""
    payload = j.get("csv")
    if isinstance(payload, dict):
        hero_text = str(payload.get(hero_slot, ""))
        villain_text = str(payload.get(vill_slot, ""))
    else:
        csv_12 = str(payload or "")
        L, R = split_12_to_6_6(csv_12, rows, cols12)
        hero_text, villain_text = L or "", R or ""

    res = write_all(csv_dir, rows, hero_slot, vill_slot, hero_text, villain_text, cfg)
    with STATE_LOCK:
        LAST_RESULT = {"ok": True, **res}
        LAST_EXEC_MS = int(time.time() * 1000)
    log(f"CSV 갱신 → Hero={res['hero']} Villain={res['villain']} (채움 {res['wrote']}, 빈 {res['blanked']})")
    return LAST_RESULT


def worker_loop():
    while not WORKER_STOP_EVENT.is_set():
        try:
            task = TASK_Q.get(timeout=1.0)
        except queue.Empty:
            continue
        if task is None:
            break
        try:
            perform_next()
        except Exception as e:
            log(f"작업 실패: {e}")
        finally:
            TASK_Q.task_done()


WT = threading.Thread(target=worker_loop, daemon=True)
WT.start()


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = f"{APP_NAME}/{APP_VERSION}"

    def _send(self, code, obj, ct="application/json"):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/health"):
            with STATE_LOCK:
                last = LAST_RESULT.copy()
                last["last_ms"] = LAST_EXEC_MS
            with CONF_LOCK:
                cfg = CONFIG.copy()
            return self._send(200, {
                "ok": True,
                "version": APP_VERSION,
                "queue": TASK_Q.qsize(),
                "last": last,
                "config": cfg
            })
        if self.path.startswith("/reload"):
            load_config()
            return self._send(200, {"ok": True, "reloaded": True})
        if self.path.startswith("/next"):
            TASK_Q.put({"t": "next", "ts": time.time()})
            log("요청 수신: GET /next → 큐 등록")
            return self._send(200, {"ok": True, "queued": TASK_Q.qsize()})
        return self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        # Security: Content-Length 제한
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > MAX_BODY_SIZE:
            log(f"[SECURITY] Content-Length 초과: {length} > {MAX_BODY_SIZE}")
            return self._send(413, {"ok": False, "error": "Payload too large"})

        raw = self.rfile.read(length) if length > 0 else b""

        if self.path.startswith("/next"):
            TASK_Q.put({"t": "next", "ts": time.time()})
            log("요청 수신: POST /next → 큐 등록")
            return self._send(200, {"ok": True, "queued": TASK_Q.qsize()})

        if self.path.startswith("/force"):
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                body = {}

            with CONF_LOCK:
                cfg = CONFIG.copy()
            csv_dir = Path(cfg["csv_dir"])
            rows = int(cfg["rows"])

            hero = (body.get("hero") or body.get("heroSlot") or "").strip()
            vill = (body.get("villain") or body.get("villSlot") or "").strip()

            # Security: 슬롯명 검증
            if not hero or not vill:
                return self._send(400, {"ok": False, "error": "hero/villain 필수"})
            if not validate_slot_name(hero):
                log(f"[SECURITY] 잘못된 hero 슬롯명: {hero}")
                return self._send(400, {"ok": False, "error": f"잘못된 hero 슬롯명"})
            if not validate_slot_name(vill):
                log(f"[SECURITY] 잘못된 villain 슬롯명: {vill}")
                return self._send(400, {"ok": False, "error": f"잘못된 villain 슬롯명"})

            txtH = str(body.get("csvHero") or body.get("heroCsv") or body.get("csv") or "")
            txtV = str(body.get("csvVillain") or body.get("villainCsv") or body.get("csv") or "")

            try:
                res = write_all(csv_dir, rows, hero, vill, txtH, txtV, cfg)
                return self._send(200, {"ok": True, **res})
            except ValueError as e:
                return self._send(400, {"ok": False, "error": str(e)})
            except Exception as e:
                return self._send(500, {"ok": False, "error": str(e)})

        return self._send(404, {"ok": False, "error": "not found"})


def main():
    load_config()
    with CONF_LOCK:
        port = int(CONFIG["port"])
    addr = ("127.0.0.1", port)
    log(f"{APP_NAME} v{APP_VERSION} 시작: http://{addr[0]}:{addr[1]}")
    log(f"Security: 슬롯명 검증 활성화, Content-Length 제한 {MAX_BODY_SIZE // (1024*1024)}MB")

    with socketserver.ThreadingTCPServer(addr, Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            WORKER_STOP_EVENT.set()
            TASK_Q.put(None)
            log("종료합니다.")


if __name__ == "__main__":
    main()
