# iconik ↔ media_metadata.csv 매칭 계획

## 1. 데이터셋 분석 결과

### 1.1 media_metadata.csv (아카이브 파일)
| 카테고리 | 파일 수 | 비고 |
|---------|--------|------|
| WSOP | 2,519개 | 메인 아카이브 |
| HCL | 250개 | Hustler Casino Live |
| PAD | 88개 | Poker After Dark |
| GGMillions | 30개 | GG Millions |
| MPP | 22개 | Mediterranean Poker Party |
| **총계** | **2,909개** | |

### 1.2 iconik 미매칭 클립
| 항목 | 수량 |
|------|------|
| 총 미매칭 | 2,102개 |
| 연도 확인 가능 | 1,409개 |
| 연도 불명 | 693개 |

### 1.3 연도별 매칭 가능성 분석

| 연도 | iconik | media_metadata | 매칭 가능성 |
|------|--------|----------------|-------------|
| 2003 | 47 | 9 | 낮음 |
| 2004 | 108 | 64 | 중간 |
| 2005 | 136 | 86 | 중간 |
| 2006 | 86 | 64 | 높음 |
| 2007 | 111 | 64 | 중간 |
| 2008 | 125 | 32 | 낮음 |
| 2009 | 101 | 64 | 중간 |
| 2010 | 18 | 68 | 높음 |
| 2011 | 93 | 64 | 높음 |
| 2012 | 55 | 56 | 높음 |
| 2013 | 49 | 56 | 높음 |
| 2014 | 57 | 56 | 높음 |
| 2015 | 64 | - | 불가 |
| 2016 | 65 | 500 | 매우 높음 |
| 2023 | 30 | 49 | 높음 |
| 2024 | 86 | 615 | 매우 높음 |
| 2025 | 86 | 203 | 매우 높음 |

---

## 2. 매칭 전략

### 2.1 Strategy 1: 연도 + 이벤트번호 매칭
**대상**: WSOP Bracelet Events, Main Event
**예상 매칭**: 400~600개

```
iconik title: "32-wsop-2024-be-ev-58-50k-ppc-day3-negreanu..."
                    ↓ 추출
            year=2024, event=58, type=bracelet

media_metadata: "WSOP 2024 Event #58 $50K PPC Day 3.mp4"
                    ↓ 추출
            year=2024, event=58
```

**매칭 키**:
- 연도 (year)
- 이벤트 번호 (event number)
- 이벤트 타입 (Main Event / Bracelet Event)
- Day 번호 (optional)

### 2.2 Strategy 2: 파일명 유사도 매칭
**대상**: 정형화된 파일명을 가진 클립
**예상 매칭**: 200~400개

```
iconik: "WSOP 2025 Main Event _ Day 8 (Part 2)"
media:  "WSOP 2025 Main Event _ Day 8 (Part 2).mp4"
        → 유사도: 95%+ (직접 매칭)
```

**방법**:
- 파일명 정규화 (확장자 제거, 특수문자 통일)
- rapidfuzz 토큰 기반 유사도 (threshold: 85%)

### 2.3 Strategy 3: 선수 이름 + 연도 매칭
**대상**: 선수 태그가 있는 클립
**예상 매칭**: 100~200개

```
iconik:
  title: "wsop-2001-me-nobug_subclip_Daniel Negreanu_Eliminated"
  players_tags: "Daniel Negreanu"
        ↓
media: "WSOP 2001 Main Event - Daniel Negreanu.mp4" 검색
```

**매칭 키**:
- 선수 이름 (정규화)
- 연도
- 이벤트 타입

### 2.4 Strategy 4: Subclip → 부모 파일 매칭
**대상**: "_subclip" 패턴이 있는 클립 (811개)
**예상 매칭**: 300~500개

```
iconik: "WSOP 2025 Bracelet Events _ Event #46_subclip_Alex Foxen"
        ↓ 부모 파일명 추출
parent: "WSOP 2025 Bracelet Events _ Event #46"
        ↓
media:  "WSOP 2025 Bracelet Events _ Event #46.mp4" 검색
```

### 2.5 Strategy 5: HCL (Hustler Casino Live) 전용 매칭
**대상**: Hustler Casino Live 클립 (140개)
**예상 매칭**: 80~120개

```
iconik project: "Hustler Casino Live"
iconik title:   "HCL Season 5 Episode 12..."
        ↓
media (HCL 폴더): "HCL S5 E12.mp4" 검색
```

**매칭 키**:
- 시즌 번호
- 에피소드 번호
- 날짜 (있는 경우)

### 2.6 Strategy 6: PAD (Poker After Dark) 전용 매칭
**대상**: Poker After Dark 클립 (64개)
**예상 매칭**: 40~60개

```
iconik project: "PAD (POKER AFTER DARK) SEASON 13"
        ↓
media (PAD 폴더): 시즌 + 에피소드 매칭
```

---

## 3. 구현 계획

### 3.1 Phase 1: 데이터 준비
```python
# 1. media_metadata를 DB에 로드
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    path TEXT,
    folder TEXT,
    year INTEGER,
    event_number INTEGER,
    event_type TEXT,  -- 'main_event', 'bracelet', 'other'
    category TEXT,    -- 'WSOP', 'HCL', 'PAD', etc.
    normalized_name TEXT
);

# 2. 인덱스 생성
CREATE INDEX idx_media_year ON media_files(year);
CREATE INDEX idx_media_category ON media_files(category);
CREATE INDEX idx_media_normalized ON media_files(normalized_name);
```

### 3.2 Phase 2: 매칭 스크립트 구현
```
scripts/match_iconik_to_media.py

함수:
- load_media_metadata(): DB에 media 파일 로드
- normalize_filename(): 파일명 정규화
- extract_event_info(): 연도, 이벤트 번호 추출
- match_by_event(): Strategy 1 실행
- match_by_similarity(): Strategy 2 실행
- match_by_players(): Strategy 3 실행
- match_subclips(): Strategy 4 실행
- match_hcl(): Strategy 5 실행
- match_pad(): Strategy 6 실행
```

### 3.3 Phase 3: 매칭 실행
```
실행 순서:
1. Strategy 2 (직접 유사도) - 가장 신뢰도 높음
2. Strategy 1 (연도+이벤트) - 구조화된 매칭
3. Strategy 4 (Subclip) - 부모 파일 매칭
4. Strategy 5 (HCL) - 카테고리 전용
5. Strategy 6 (PAD) - 카테고리 전용
6. Strategy 3 (선수 이름) - 보조 매칭
```

### 3.4 Phase 4: 검증 및 정제
```
- 신뢰도 95%+: 자동 승인
- 신뢰도 80-95%: 샘플 검토
- 신뢰도 <80%: 수동 검토 목록 생성
```

---

## 4. 예상 결과

| 전략 | 대상 | 예상 매칭 | 신뢰도 |
|------|------|----------|--------|
| Strategy 1 | 이벤트 기반 | 400~600 | 90% |
| Strategy 2 | 파일명 유사도 | 200~400 | 95% |
| Strategy 3 | 선수 이름 | 100~200 | 75% |
| Strategy 4 | Subclip | 300~500 | 85% |
| Strategy 5 | HCL | 80~120 | 90% |
| Strategy 6 | PAD | 40~60 | 90% |
| **총계** | | **1,120~1,880** | |

### 최종 예상
| 항목 | 수량 | 비율 |
|------|------|------|
| 기존 매칭 | 346 | 14.1% |
| 신규 매칭 (예상) | 1,120~1,880 | 46~77% |
| **총 매칭** | **1,466~2,226** | **60~91%** |
| 미매칭 (예상) | 222~982 | 9~40% |

---

## 5. 매칭 불가 예상 항목

| 항목 | 수량 | 이유 |
|------|------|------|
| WSOP Paradise | ~275개 | media_metadata에 없음 |
| 2015 WSOP | ~60개 | media_metadata에 없음 |
| 기타 외부 콘텐츠 | ~100개 | 아카이브 외부 소스 |

---

## 6. 다음 단계

1. [ ] media_metadata를 DB에 로드하는 스크립트 생성
2. [ ] match_iconik_to_media.py 구현
3. [ ] Phase 1-2-3 순차 실행
4. [ ] 결과 검증 및 CSV 업데이트
5. [ ] 수동 검토 목록 생성
