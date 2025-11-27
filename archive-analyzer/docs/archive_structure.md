# 아카이브 폴더 구조 다이어그램

> 생성일: 2025-11-27
> 총 용량: 18.03 TB | 총 파일: 1,418개

## 1. 전체 구조 (Mindmap)

```mermaid
mindmap
  root((ARCHIVE<br/>18.03 TB))
    WSOP
      WSOP ARCHIVE PRE-2016
        2003-2010
          2010 Masters<br/>2.85 TB
          2009 Masters<br/>2.78 TB
          2007<br/>1.56 TB
          2006<br/>411 GB
          2005<br/>1.19 TB
          2004<br/>841 GB
          2003<br/>267 GB
          2008<br/>194 GB
        2011-2016
          2015 Main Event<br/>748 GB
          2016 Main Event<br/>470 GB
          2011-2014<br/>538 GB
        1973-2002
          2002<br/>450 GB
          1995<br/>346 GB
          Others<br/>1.5 TB
      WSOP-BR
        EUROPE 2025<br/>1.3 TB
        PARADISE<br/>443 GB
        LAS VEGAS<br/>126 GB
      WSOP-C
        LA 2024<br/>100 GB
      WSOP-SC
        Cyprus 2025<br/>61 GB
    HCL
      2025<br/>596 GB
      Poker Clip<br/>2 GB
    PAD
      S13<br/>116 GB
      S12<br/>100 GB
    MPP
      Grand Final<br/>39 GB
      Main Event<br/>36 GB
      Mystery Bounty<br/>27 GB
    GGMillions<br/>18 GB
```

## 2. 용량 분포 (Pie Chart)

```mermaid
pie showData
    title 콘텐츠별 용량 분포
    "WSOP Archive (PRE-2016)" : 12500
    "WSOP-BR (현재)" : 2000
    "HCL" : 600
    "PAD" : 216
    "MPP" : 102
    "WSOP-C/SC" : 161
    "GGMillions" : 18
```

## 3. 파일 확장자 분포

```mermaid
pie showData
    title 파일 확장자별 용량 (GB)
    ".mov" : 10830
    ".mp4" : 4460
    ".mxf" : 2680
    ".webm" : 39
    ".mkv" : 18
    "기타" : 6
```

## 4. 상세 폴더 구조 (Flowchart)

```mermaid
flowchart TD
    subgraph ARCHIVE["📁 ARCHIVE (18.03 TB)"]
        subgraph WSOP["📁 WSOP (15.6 TB)"]
            subgraph PRE2016["📁 WSOP ARCHIVE PRE-2016 (12.5 TB)"]
                Y2003_2010["📁 2003-2010<br/>9.1 TB"]
                Y2011_2016["📁 2011-2016<br/>1.8 TB"]
                Y1973_2002["📁 1973-2002<br/>1.6 TB"]
            end
            subgraph WSOP_BR["📁 WSOP-BR (2.0 TB)"]
                EUROPE["🎬 EUROPE 2025<br/>1.3 TB"]
                PARADISE["🎬 PARADISE<br/>443 GB"]
                LASVEGAS["🎬 LAS VEGAS<br/>126 GB"]
            end
            WSOP_C["📁 WSOP-C (100 GB)"]
            WSOP_SC["📁 WSOP-SC (61 GB)"]
        end

        HCL["📁 HCL (598 GB)<br/>🎬 129 files"]
        PAD["📁 PAD (216 GB)<br/>🎬 44 files"]
        MPP["📁 MPP (102 GB)<br/>🎬 11 files"]
        GGMillions["📁 GGMillions (18 GB)<br/>🎬 15 files"]
    end

    style ARCHIVE fill:#1a1a2e
    style WSOP fill:#16213e
    style PRE2016 fill:#0f3460
    style WSOP_BR fill:#0f3460
    style HCL fill:#e94560
    style PAD fill:#533483
    style MPP fill:#0f3460
```

## 5. 연도별 콘텐츠 타임라인

```mermaid
timeline
    title WSOP 아카이브 연도별 분포
    section 1973-2002
        1983-1998 : 클래식 영상 1.2 TB
        2002 : 450 GB
    section 2003-2010
        2003 : 287 GB
        2004 : 841 GB
        2005 : 1.19 TB
        2006 : 411 GB
        2007 : 1.56 TB
        2008 : 194 GB
        2009 : 2.78 TB
        2010 : 2.85 TB
    section 2011-2016
        2011-2014 : 538 GB
        2015 : 748 GB
        2016 : 470 GB
    section 2024-2025
        2024 : WSOP-C LA, PARADISE
        2025 : EUROPE, Cyprus, HCL
```

## 6. 파일 유형별 상세

```mermaid
flowchart LR
    subgraph VIDEO["🎬 비디오 (15.34 TB)"]
        MOV[".mov<br/>256개 | 10.83 TB"]
        MP4[".mp4<br/>1,002개 | 4.46 TB"]
        WEBM[".webm<br/>8개 | 39 GB"]
        MKV[".mkv<br/>3개 | 18 GB"]
        AVI[".avi<br/>2개 | 1.4 GB"]
    end

    subgraph OTHER["📦 기타 (2.68 TB)"]
        MXF[".mxf<br/>126개 | 2.68 TB<br/>⚠️ 방송용 비디오"]
        PART[".part<br/>4개 | 3 GB"]
        ZIP[".zip<br/>1개 | 1.4 GB"]
        DB[".db<br/>13개"]
    end

    style VIDEO fill:#2d5a27
    style OTHER fill:#8b4513
    style MXF fill:#ff6b6b
```

## 7. 주요 폴더 용량 순위 (Top 10)

```mermaid
xychart-beta
    title "폴더별 용량 (TB)"
    x-axis ["2010 Masters", "2009 Masters", "2007", "2015 Main", "2005 MXFs", "HCL 2025", "2004 MXFs", "2002", "2006", "2016 MXFs"]
    y-axis "용량 (TB)" 0 --> 3
    bar [2.85, 2.78, 1.56, 0.73, 0.72, 0.58, 0.49, 0.44, 0.40, 0.39]
```

---

## 요약

| 항목 | 값 |
|------|-----|
| 총 파일 수 | 1,418개 |
| 총 용량 | 18.03 TB |
| 비디오 파일 | 1,271개 (15.34 TB) |
| 주요 확장자 | .mov (60%), .mp4 (25%), .mxf (15%) |
| 최대 폴더 | WSOP 2010 Masters (2.85 TB) |

> **참고**: .mxf 파일은 프로페셔널 방송용 비디오 포맷으로, video 유형으로 재분류 권장
