# iconik ↔ media_metadata Path 기반 매칭 계획

## 1. Path 구조 분석

### 1.1 media_metadata.csv Path 구조
```
\\10.10.100.122\docker\GGPNAs\ARCHIVE\
├── WSOP (2,519개)
│   ├── WSOP ARCHIVE (PRE-2016) (1,295개)
│   │   ├── WSOP Archive (1973-2002) - 122개
│   │   ├── WSOP Archive (2003-2010) - 697개
│   │   └── WSOP Archive (2011-2016) - 476개
│   │
│   ├── WSOP-BR (1,132개) ─ Bracelet Events
│   │   ├── WSOP-PARADISE (656개)
│   │   │   ├── 2024 WSOP-PARADISE SUPER MAIN EVENT - 558개
│   │   │   └── 2023 WSOP-PARADISE - 98개
│   │   ├── WSOP-LAS VEGAS (318개)
│   │   │   ├── 2024 WSOP-LAS VEGAS (PokerGo Clip) - 196개
│   │   │   └── 2025 WSOP-LAS VEGAS - 122개
│   │   └── WSOP-EUROPE (158개)
│   │
│   ├── WSOP-C (80개) ─ Circuit
│   │   └── 2024 WSOP-C LA - 80개
│   │
│   └── WSOP-SC (12개) ─ Super Circuit
│       └── 2025 WSOP-SC (Cyprus) - 12개
│
├── HCL (250개) ─ Hustler Casino Live
│   ├── 2025 - 234개
│   └── HCL Poker Clip - 16개
│
├── PAD (88개) ─ Poker After Dark
│   ├── PAD S12 - 42개
│   └── PAD S13 - 46개
│
├── GGMillions (30개)
│
└── MPP (22개) ─ Mediterranean Poker Party
```

---

## 2. iconik ProjectName → Path 매핑 테이블

### 2.1 직접 매핑 가능 (1,617개 추정)

| iconik ProjectName | 수량 | → media_metadata Path |
|-------------------|------|----------------------|
| **WSOP PARADISE** | 209개 | `WSOP/WSOP-BR/WSOP-PARADISE` |
| **WSOP Paradise** | 66개 | `WSOP/WSOP-BR/WSOP-PARADISE` |
| **2024 WSOP PARADISE** | 21개 | `WSOP/WSOP-BR/WSOP-PARADISE/2024` |
| **2023 WSOP PARADISE** | 3개 | `WSOP/WSOP-BR/WSOP-PARADISE/2023` |
| **Hustler Casino Live** | 140개 | `HCL` |
| **PAD (POKER AFTER DARK) SEASON 13** | 40개 | `PAD/PAD S13` |
| **Poker After Dark S12** | 25개 | `PAD/PAD S12` |
| **Poker After Dark Seanson 13** | 23개 | `PAD/PAD S13` |
| **2024 WSOP Circuit Los Angeles** | 44개 | `WSOP/WSOP-C/2024 WSOP-C LA` |
| **WSOP** | 63개 | `WSOP/WSOP-BR/WSOP-LAS VEGAS` |
| **2024 WSOP** | 37개 | `WSOP/WSOP-BR/WSOP-LAS VEGAS/2024` |
| **WSOP 2025** | 4개 | `WSOP/WSOP-BR/WSOP-LAS VEGAS/2025` |
| **WSOPE** | 18개 | `WSOP/WSOP-BR/WSOP-EUROPE` |
| **2024 WSOPE** | 2개 | `WSOP/WSOP-BR/WSOP-EUROPE` |

### 2.2 PRE-2016 Archive 매핑 (약 900개)

| iconik ProjectName | 수량 | → media_metadata Path |
|-------------------|------|----------------------|
| **2004 World Series Of/of Poker** | 103개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2005 World Series Of/of Poker** | 129개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2006 World Series of Poker** | 73개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2007 World Series of Poker** | 109개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2008 World Series of Poker** | 89개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2009 World Series of Poker** | 89개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2010 World Series Of Poker** | 37개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2003-2010)` |
| **2011 World Series Of Poker** | 89개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |
| **2012 World Series Of Poker** | 52개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |
| **2013 World Series Of Poker** | 47개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |
| **2014 World Series Of Poker** | 57개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |
| **2015 World Series Of Poker** | 60개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |
| **2016 World Series Of Poker** | 62개 | `WSOP ARCHIVE (PRE-2016)/WSOP Archive (2011-2016)` |

### 2.3 매핑 불확실 (485개)

| iconik ProjectName | 수량 | 비고 |
|-------------------|------|------|
| **(없음)** | 257개 | 타이틀에서 추론 필요 |
| **World Series Of Poker** | 48개 | 연도 불명 → 타이틀 분석 |
| **World Series Of Poker Classic** | 43개 | 별도 카테고리 확인 필요 |
| **Game Of Gold** | 36개 | 아카이브에 없음 |
| **GGMillion$** | 13개 | `GGMillions` 폴더 매칭 |
| **Mediterranean Poker Party MPP** | 11개 | `MPP` 폴더 매칭 |
| **기타** | 77개 | 개별 분석 필요 |

---

## 3. Path 기반 매칭 전략

### Strategy 1: ProjectName → Path 직접 매핑
**대상**: 명확한 ProjectName이 있는 클립
**예상 매칭**: 1,200~1,400개

```python
# 매핑 테이블
PROJECT_TO_PATH = {
    'WSOP PARADISE': 'WSOP/WSOP-BR/WSOP-PARADISE',
    'WSOP Paradise': 'WSOP/WSOP-BR/WSOP-PARADISE',
    'Hustler Casino Live': 'HCL',
    'PAD (POKER AFTER DARK) SEASON 13': 'PAD/PAD S13',
    # ... 전체 매핑 테이블
}

# iconik project → 해당 Path의 파일들과 매칭
def match_by_project_path(iconik_clip, media_files):
    project = iconik_clip['project_name']
    target_path = PROJECT_TO_PATH.get(project)

    if target_path:
        candidates = [f for f in media_files if target_path in f['path']]
        return find_best_match(iconik_clip, candidates)
```

### Strategy 2: 연도 기반 Archive Path 매칭
**대상**: 2003-2016 WSOP 클립
**예상 매칭**: 600~800개

```python
# 연도별 Archive 경로
YEAR_TO_ARCHIVE = {
    range(1973, 2003): 'WSOP Archive (1973-2002)',
    range(2003, 2011): 'WSOP Archive (2003-2010)',
    range(2011, 2017): 'WSOP Archive (2011-2016)',
}

def match_by_year_archive(iconik_clip, media_files):
    year = extract_year(iconik_clip)
    archive_path = get_archive_path(year)

    candidates = [f for f in media_files if archive_path in f['path']]
    return find_best_match(iconik_clip, candidates)
```

### Strategy 3: Path 내 파일명 유사도 매칭
**대상**: Path 매핑 후 다수 후보가 있는 경우
**방법**: rapidfuzz를 사용한 파일명 매칭

```python
def find_best_match(iconik_clip, candidates):
    iconik_title = normalize(iconik_clip['title'])

    best_match = None
    best_score = 0

    for candidate in candidates:
        filename = normalize(candidate['filename'])
        score = fuzz.token_set_ratio(iconik_title, filename)

        if score > best_score:
            best_score = score
            best_match = candidate

    return best_match if best_score >= 70 else None
```

### Strategy 4: Subclip 부모 파일 Path 매칭
**대상**: "_subclip" 패턴 클립 (811개)
**예상 매칭**: 400~600개

```python
def match_subclip(iconik_clip, media_files):
    title = iconik_clip['title']

    # 부모 파일명 추출
    if '_subclip' in title:
        parent_name = title.split('_subclip')[0]

    # 해당 Path에서 부모 파일 검색
    project_path = PROJECT_TO_PATH.get(iconik_clip['project_name'])
    candidates = [f for f in media_files if project_path in f['path']]

    return fuzzy_match(parent_name, candidates)
```

### Strategy 5: 선수 이름 + Path 매칭
**대상**: PlayersTags가 있는 클립
**예상 매칭**: 100~200개

```python
def match_by_players(iconik_clip, media_files):
    players = iconik_clip['players_tags'].split(',')
    project_path = get_project_path(iconik_clip)

    candidates = [f for f in media_files if project_path in f['path']]

    # 선수 이름이 파일명에 포함된 파일 찾기
    for candidate in candidates:
        filename = candidate['filename'].lower()
        for player in players:
            if player.lower().strip() in filename:
                return candidate
```

---

## 4. 구현 계획

### Phase 1: 데이터 준비
```sql
-- media_files 테이블 생성 (Path 정보 포함)
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY,
    filename TEXT,
    path TEXT,
    folder TEXT,
    -- Path 파싱 결과
    category TEXT,      -- 'WSOP', 'HCL', 'PAD', etc.
    sub_category TEXT,  -- 'WSOP-BR', 'WSOP ARCHIVE (PRE-2016)', etc.
    location TEXT,      -- 'PARADISE', 'LAS VEGAS', 'EUROPE'
    year_folder TEXT,   -- '2024', '2025', etc.
    normalized_name TEXT
);

-- 인덱스
CREATE INDEX idx_media_category ON media_files(category);
CREATE INDEX idx_media_sub_category ON media_files(sub_category);
CREATE INDEX idx_media_location ON media_files(location);
```

### Phase 2: 매칭 스크립트
```
scripts/match_by_path.py

1. load_and_parse_media_metadata()
   - media_metadata.csv 로드
   - Path 파싱하여 category, sub_category, location 추출
   - DB에 저장

2. build_project_path_mapping()
   - iconik ProjectName → Path 매핑 테이블 생성

3. match_clips()
   - Strategy 1-5 순차 실행
   - 매칭 결과 저장

4. export_results()
   - 매칭된 file_id 업데이트
   - CSV 재생성
```

### Phase 3: 실행 순서
```
1. Path 직접 매핑 (Strategy 1) - 가장 높은 신뢰도
2. 연도 Archive 매핑 (Strategy 2)
3. Subclip 매칭 (Strategy 4)
4. 파일명 유사도 (Strategy 3)
5. 선수 이름 매칭 (Strategy 5)
```

---

## 5. 예상 결과

| 전략 | 대상 | 예상 매칭 | 신뢰도 |
|------|------|----------|--------|
| Strategy 1 | ProjectName→Path | 400~600 | 95% |
| Strategy 2 | 연도 Archive | 600~800 | 90% |
| Strategy 3 | 파일명 유사도 | 200~300 | 85% |
| Strategy 4 | Subclip 부모 | 400~600 | 85% |
| Strategy 5 | 선수 이름 | 100~200 | 75% |
| **총계** | | **1,700~2,500** | |

### 최종 예상
| 항목 | 수량 | 비율 |
|------|------|------|
| 기존 매칭 | 346 | 14.1% |
| Path 기반 신규 매칭 | 1,400~1,800 | +57~74% |
| **총 매칭** | **1,746~2,146** | **71~88%** |
| 미매칭 예상 | 302~702 | 12~29% |

---

## 6. 매칭 불가 예상 항목

| 항목 | 수량 | 이유 |
|------|------|------|
| Game Of Gold | 36개 | 아카이브에 없음 |
| ProjectName 없음 + 타이틀 불명확 | ~150개 | 정보 부족 |
| 기타 외부 콘텐츠 | ~100개 | 아카이브 외부 |

---

## 7. 다음 단계

1. [ ] media_metadata를 DB에 로드 (Path 파싱 포함)
2. [ ] ProjectName → Path 매핑 테이블 완성
3. [ ] match_by_path.py 스크립트 구현
4. [ ] Strategy 1-5 순차 실행
5. [ ] 결과 검증 및 clip_metadata 업데이트
6. [ ] iconik_metadata_merged.csv 재생성
