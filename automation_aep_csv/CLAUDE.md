# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**GGM-CSVd (GGM CSV Daemon)** - Google Apps Script WebApp과 연동하여 포커 그래픽 시스템용 CSV 파일을 실시간으로 갱신하는 로컬 HTTP 서버입니다.

- Hero/Villain 슬롯 데이터를 10x6 CSV 형식으로 분리 저장
- Google Sheets → WebApp → 로컬 CSV 파일 동기화

## 아키텍처

```
Google Sheets ──▶ Apps Script WebApp ──▶ GGM-CSVd (localhost:8787) ──▶ CSV 파일
                     (nextfetch)              HTTP Server              (Hero/Villain)
```

### 핵심 컴포넌트

| 컴포넌트 | 파일 | 역할 |
|----------|------|------|
| HTTP 서버 | `ggm_csvd.py` | `/next`, `/health`, `/force`, `/reload` 엔드포인트 |
| 설정 | `config.json` | csv_dir, gs_url, port 등 |
| 실행 스크립트 | `run_ggm_csvd.bat` | Python unbuffered 모드 실행 |

### API 엔드포인트

| 메서드 | 경로 | 동작 |
|--------|------|------|
| GET/POST | `/next` | WebApp 호출 → CSV 갱신 (큐 등록) |
| GET | `/health` | 상태/설정/마지막 결과 조회 |
| GET | `/reload` | config.json 리로드 |
| POST | `/force` | 강제 CSV 덮어쓰기 |

## 빌드 및 실행

```powershell
# 서버 실행
python -u ggm_csvd.py

# 또는 배치 파일 사용
run_ggm_csvd.bat
```

## 설정 (config.json)

```json
{
  "csv_dir": "C:/path/to/CSV",
  "gs_url": "https://script.google.com/macros/s/.../exec?op=nextfetch",
  "rows": 10,
  "cols": 12,
  "port": 8787,
  "write_mode": "atomic",
  "whitelist": []
}
```

| 키 | 설명 |
|----|------|
| `csv_dir` | CSV 파일 저장 디렉토리 |
| `gs_url` | Google Apps Script WebApp URL |
| `rows` | CSV 행 수 (기본 10) |
| `cols` | 단일 CSV 열 수 (12 → 6/6 자동 분할) |
| `whitelist` | 대상 슬롯 목록 (비어있으면 Hero*/Villain* 스캔) |

## CSV 파일 구조

- **슬롯 명명**: `Hero{N}-{M}.csv`, `Villain{N}-{M}.csv` (N: 테이블, M: 좌석)
- **형식**: 10행 x 6열, UTF-8 with BOM
- **위치 파일**: `Hero_Position.csv`, `Villain_Position.csv`

## 테스트

```powershell
# 서버 상태 확인
curl http://localhost:8787/health

# CSV 갱신 트리거
curl http://localhost:8787/next

# 강제 CSV 작성
curl -X POST http://localhost:8787/force -d '{"hero":"Hero1-1","villain":"Villain1-1","csvHero":"...","csvVillain":"..."}'
```

## 의존성

- Python 3.x (표준 라이브러리만 사용)
- 외부 패키지 없음
