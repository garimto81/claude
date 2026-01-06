#!/usr/bin/env python
"""클립 트래커 CSV와 아카이브 파일 매칭 시스템

다양한 매칭 전략을 사용하여 CSV 클립 정보를 아카이브 파일과 연결합니다.

매칭 전략:
1. 정확한 경로 매칭 (Nas Folder Link 필드 사용)
2. Event 번호 + 연도 기반 매칭
3. Main Event 전용 매칭
4. RapidFuzz 기반 다중 후보 매칭

신뢰도 등급:
- HIGH (0.85+): 단일 정확 매칭
- MEDIUM (0.6-0.85): 높은 신뢰도 복수 후보
- LOW (0.4-0.6): 검토 필요
- REVIEW (<0.4): 수동 검토 필수
"""

import sys
import os
import re
import csv
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher
from collections import defaultdict
from enum import Enum

# RapidFuzz import
try:
    from rapidfuzz import fuzz, process
    from rapidfuzz.distance import Levenshtein
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("Warning: RapidFuzz not installed. Using fallback matching.")

# UTF-8 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


class ConfidenceLevel(Enum):
    """매칭 신뢰도 등급"""
    HIGH = "high"        # 0.85+: 단일 정확 매칭, 자동 승인
    MEDIUM = "medium"    # 0.6-0.85: 높은 신뢰도, 선택적 검토
    LOW = "low"          # 0.4-0.6: 검토 필요
    REVIEW = "review"    # <0.4: 수동 검토 필수
    UNMATCHED = "unmatched"


@dataclass
class MatchCandidate:
    """매칭 후보"""
    file_id: int
    filename: str
    path: str
    score: float
    scorer_name: str  # 사용된 스코어러 (token_set_ratio, partial_ratio 등)

    def __repr__(self):
        return f"Candidate({self.file_id}, {self.score:.2f}, {self.scorer_name})"


# Source CSV 코드 매핑
SOURCE_CODES = {
    "WSOP HAND SELECTION -  2024 WSOP Clip Tracker.csv": "24W",
    "WSOP HAND SELECTION - 2025 WSOP Clip Tracker.csv": "25W",
    "WSOP HAND SELECTION - 2025 WSOP Cyprus SC Clip Tracker.csv": "25C",
    "WSOP HAND SELECTION - 2025 WSOP Europe Clip Tracker.csv": "25E",
}


def parse_timecode(timecode: str) -> tuple:
    """Timecode를 start_at, end_at으로 분리

    지원 패턴:
    - "1:01:46 - 1:06:21" (공백-대시-공백, H:MM:SS)
    - "3:23:20-3:26:30" (대시만, H:MM:SS)
    - "37:35-40:44" (MM:SS-MM:SS 형식)
    - "11:01-11:08" (M:SS-M:SS 형식)

    Returns:
        tuple: (start_at, end_at) - 원본 형식 그대로 유지
    """
    if not timecode or not timecode.strip():
        return "", ""

    tc = timecode.strip()

    # 공백-대시-공백 패턴 우선 (가장 명확한 구분자)
    if ' - ' in tc:
        parts = tc.split(' - ', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

    # 대시만 있는 패턴
    if '-' in tc:
        # 시간 형식 패턴:
        # H:MM:SS-H:MM:SS (예: 3:23:20-3:26:30)
        # MM:SS-MM:SS (예: 37:35-40:44)
        # M:SS-M:SS (예: 11:01-11:08)
        # 0H:MM:SS-0H:MM:SS (예: 04:49:06-4:59:24)
        match = re.match(
            r'^(\d{1,2}:\d{2}:\d{2})\s*-\s*(\d{1,2}:\d{2}:\d{2})$',  # H:MM:SS-H:MM:SS
            tc
        )
        if match:
            return match.group(1), match.group(2)

        match = re.match(
            r'^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$',  # MM:SS-MM:SS or M:SS-M:SS
            tc
        )
        if match:
            return match.group(1), match.group(2)

        # 혼합 패턴: H:MM:SS-MM:SS 또는 MM:SS-H:MM:SS
        match = re.match(
            r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(\d{1,2}:\d{2}(?::\d{2})?)$',
            tc
        )
        if match:
            return match.group(1), match.group(2)

        # 매칭 실패시 단순 분리 (첫 번째 대시 기준)
        parts = tc.split('-', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

    # 대시 없음 - 시작 시간만 있는 경우
    return tc, ""


@dataclass
class ClipInfo:
    """CSV 클립 정보"""
    clip_id: str = ""  # 고유 식별자: {SourceCode}-R{RowNum} (예: 24W-R1, 25W-R15)
    row_num: int = 0   # 원본 CSV 내 행 번호 (헤더 다음부터 1)
    file_no: str = ""
    event_number: str = ""
    event_name: str = ""
    nas_folder_link: str = ""
    players: str = ""
    hands: str = ""
    timecode: str = ""
    timecode_start: str = ""
    timecode_end: str = ""
    caption: str = ""
    key_point: str = ""
    youtube_title: str = ""
    is_shorts: bool = False
    edit_status: str = ""
    assignee: str = ""
    source_csv: str = ""
    source_year: str = ""
    source_code: str = ""  # 소스 코드: 24W, 25W, 25C, 25E
    # 단일 매칭 결과 (기존 호환)
    matched_file_id: Optional[int] = None
    match_confidence: float = 0.0
    match_method: str = ""
    # 다중 후보 매칭 결과 (신규)
    candidates: List['MatchCandidate'] = field(default_factory=list)
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNMATCHED
    needs_review: bool = False


@dataclass
class FileInfo:
    """DB 파일 정보"""
    id: int
    filename: str
    path: str
    parent_folder: str
    # 검색용 정규화 필드
    normalized_name: str = ""
    tokens: List[str] = field(default_factory=list)
    year: str = ""
    event_number: str = ""
    day: str = ""


class ClipMatcher:
    """클립-파일 매칭 엔진"""

    def __init__(self, db_path: str = "archive.db"):
        self.db_path = db_path
        self.files: Dict[int, FileInfo] = {}
        self.clips: List[ClipInfo] = []

        # 인덱스
        self.by_event_number: Dict[str, List[int]] = defaultdict(list)
        self.by_year: Dict[str, List[int]] = defaultdict(list)
        self.by_token: Dict[str, List[int]] = defaultdict(list)

        self._load_files()

    def _normalize_text(self, text: str) -> str:
        """텍스트 정규화 (검색용)"""
        if not text:
            return ""
        # 소문자 변환
        text = text.lower()
        # 특수문자 제거/정규화
        text = re.sub(r'[_\-\.]+', ' ', text)
        text = re.sub(r'\$', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        # 다중 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_tokens(self, text: str) -> List[str]:
        """텍스트에서 검색 토큰 추출"""
        normalized = self._normalize_text(text)
        tokens = normalized.split()
        # 불용어 제거
        stopwords = {'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'on', 'at'}
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _extract_event_number(self, text: str) -> str:
        """이벤트 번호 추출 (Event #58, ev-01, #13 등)"""
        patterns = [
            r'event\s*#?\s*(\d+)',
            r'ev[ent]*[\-_\s]*(\d+)',
            r'#(\d+)',
            r'bracelet\s*event\s*#?\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).lstrip('0') or '0'
        return ""

    def _extract_year(self, text: str) -> str:
        """연도 추출 (2024, 2025 등)"""
        match = re.search(r'20(2[0-9])', text)
        if match:
            return f"20{match.group(1)}"
        return ""

    def _extract_day(self, text: str) -> str:
        """Day 정보 추출"""
        match = re.search(r'day\s*(\d+[a-d]?)', text.lower())
        if match:
            return match.group(1)
        if 'final' in text.lower():
            return 'final'
        return ""

    def _load_files(self):
        """DB에서 파일 정보 로드 및 인덱싱"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, filename, path, parent_folder
            FROM files
            WHERE file_type = 'video'
        ''')

        for row in cursor.fetchall():
            file_id, filename, path, parent_folder = row

            # 정규화 및 토큰 추출
            full_text = f"{filename} {path}"
            normalized = self._normalize_text(full_text)
            tokens = self._extract_tokens(full_text)
            year = self._extract_year(full_text)
            event_num = self._extract_event_number(full_text)
            day = self._extract_day(full_text)

            file_info = FileInfo(
                id=file_id,
                filename=filename,
                path=path,
                parent_folder=parent_folder,
                normalized_name=normalized,
                tokens=tokens,
                year=year,
                event_number=event_num,
                day=day
            )

            self.files[file_id] = file_info

            # 인덱스 구축
            if event_num:
                self.by_event_number[event_num].append(file_id)
            if year:
                self.by_year[year].append(file_id)
            for token in tokens:
                self.by_token[token].append(file_id)

        conn.close()
        print(f"Loaded {len(self.files)} video files")
        print(f"Indexed {len(self.by_event_number)} event numbers")

    def _match_by_path(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """경로 기반 정확 매칭"""
        if not clip.nas_folder_link:
            return None

        # 경로 정규화
        search_path = clip.nas_folder_link.replace('/', '\\').lower()

        for file_id, file_info in self.files.items():
            file_path = file_info.path.replace('/', '\\').lower()
            if search_path in file_path or file_path in search_path:
                return (file_id, 1.0)

        return None

    def _match_2024_pattern(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """2024 PokerGo 클립 파일명 패턴 매칭

        2024 파일명 형식: wsop-2024-be-ev-{num}-{buyin}-{event}-...
        예: 32-wsop-2024-be-ev-58-50k-ppc-day3-negreanu-misreads-hand
        """
        if clip.source_year != "2024":
            return None

        # 이벤트 번호 추출
        event_num = self._extract_event_number(clip.event_number + " " + clip.event_name)
        if not event_num:
            return None

        # Day 정보 추출
        day = self._extract_day(clip.event_name)

        # 선수명 추출
        player_names = []
        if clip.players:
            player_names = [p.strip().lower() for p in re.split(r'\s+vs\s+', clip.players, flags=re.IGNORECASE)]

        # 2024 파일 패턴으로 검색
        candidates = []
        for file_id, file_info in self.files.items():
            fname_lower = file_info.filename.lower()

            # wsop-2024 패턴 확인
            if 'wsop-2024' not in fname_lower and '2024' not in file_info.path.lower():
                continue

            # 이벤트 번호 패턴 매칭 (ev-58, ev58 등)
            ev_patterns = [f'ev-{event_num}', f'ev{event_num}', f'-{event_num}-']
            if not any(p in fname_lower for p in ev_patterns):
                continue

            candidates.append(file_id)

        if not candidates:
            return None

        # Day 필터링
        if day:
            day_filtered = []
            for fid in candidates:
                fname = self.files[fid].filename.lower()
                if f'day{day}' in fname or f'day-{day}' in fname or f'day{day[0]}' in fname:
                    day_filtered.append(fid)
            if day_filtered:
                candidates = day_filtered

        # 선수명으로 점수 계산
        if player_names and candidates:
            scored = []
            for fid in candidates:
                fname = self.files[fid].filename.lower()
                matches = sum(1 for p in player_names if p in fname)
                scored.append((fid, matches))
            scored.sort(key=lambda x: -x[1])
            if scored[0][1] > 0:
                return (scored[0][0], 0.9 + scored[0][1] * 0.02)

        if len(candidates) == 1:
            return (candidates[0], 0.85)
        elif candidates:
            return (candidates[0], 0.7)

        return None

    def _match_by_players(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """선수명 기반 매칭 (fallback)"""
        if not clip.players:
            return None

        # 선수명 추출
        player_names = [p.strip().lower() for p in re.split(r'\s+vs\s+', clip.players, flags=re.IGNORECASE)]
        if not player_names or len(player_names[0]) < 3:
            return None

        # 연도 필터
        year = clip.source_year or self._extract_year(clip.event_name)

        candidates = []
        for file_id, file_info in self.files.items():
            fname_lower = file_info.filename.lower()

            # 연도 필터링
            if year and year not in file_info.path:
                continue

            # 선수명 매칭 점수
            matches = sum(1 for p in player_names if p in fname_lower)
            if matches > 0:
                candidates.append((file_id, matches))

        if not candidates:
            return None

        candidates.sort(key=lambda x: -x[1])

        # 매칭된 선수 수에 따른 신뢰도
        best_fid, best_count = candidates[0]
        confidence = 0.5 + (best_count / len(player_names)) * 0.3

        return (best_fid, confidence)

    def _is_main_event(self, text: str) -> bool:
        """Main Event 여부 확인"""
        lower = text.lower()
        return 'main event' in lower or 'me day' in lower or 'me-day' in lower

    def _match_main_event(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """Main Event 전용 매칭"""
        if not self._is_main_event(clip.event_name):
            return None

        year = clip.source_year or self._extract_year(clip.event_name)
        day = self._extract_day(clip.event_name)

        # Part 정보 추출
        part = ""
        part_match = re.search(r'part\s*(\d+)', clip.event_name.lower())
        if part_match:
            part = part_match.group(1)

        # Main Event 파일 후보 검색
        candidates = []
        for file_id, file_info in self.files.items():
            if self._is_main_event(file_info.filename) or self._is_main_event(file_info.path):
                candidates.append(file_id)

        if not candidates:
            return None

        # 연도 필터링
        if year:
            year_filtered = [fid for fid in candidates if self.files[fid].year == year]
            if year_filtered:
                candidates = year_filtered

        # Day 필터링
        if day:
            day_filtered = []
            for fid in candidates:
                file_day = self._extract_day(self.files[fid].filename)
                # Day 1A, 1B 등의 경우
                if day.lower() == file_day.lower():
                    day_filtered.append(fid)
                # Day 숫자만 일치하는 경우
                elif day.rstrip('abcd') == file_day.rstrip('abcd'):
                    day_filtered.append(fid)
            if day_filtered:
                candidates = day_filtered

        # Part 필터링
        if part:
            part_filtered = []
            for fid in candidates:
                file_part = ""
                file_part_match = re.search(r'part\s*(\d+)', self.files[fid].filename.lower())
                if file_part_match:
                    file_part = file_part_match.group(1)
                if file_part == part:
                    part_filtered.append(fid)
            if part_filtered:
                candidates = part_filtered

        if len(candidates) == 1:
            return (candidates[0], 0.85)
        elif candidates:
            # 토큰 유사도로 최적 선택
            best_match = None
            best_score = 0
            clip_tokens = set(self._extract_tokens(clip.event_name))

            for fid in candidates:
                file_tokens = set(self.files[fid].tokens)
                if clip_tokens and file_tokens:
                    score = len(clip_tokens & file_tokens) / len(clip_tokens | file_tokens)
                    if score > best_score:
                        best_score = score
                        best_match = fid

            if best_match:
                return (best_match, 0.6 + best_score * 0.25)

        return None

    def _match_by_event(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """이벤트 번호 + 연도 기반 매칭"""
        event_num = self._extract_event_number(clip.event_number + " " + clip.event_name)
        year = clip.source_year or self._extract_year(clip.event_name)
        day = self._extract_day(clip.event_name)

        if not event_num:
            return None

        candidates = self.by_event_number.get(event_num, [])

        if not candidates:
            return None

        # 연도 필터링
        if year:
            year_filtered = [fid for fid in candidates if self.files[fid].year == year]
            if year_filtered:
                candidates = year_filtered

        # Day 필터링
        if day:
            day_filtered = [fid for fid in candidates if self.files[fid].day == day]
            if day_filtered:
                candidates = day_filtered

        if len(candidates) == 1:
            return (candidates[0], 0.9)
        elif candidates:
            # 여러 후보 중 가장 적합한 것 선택 (토큰 유사도)
            best_match = None
            best_score = 0
            clip_tokens = set(self._extract_tokens(clip.event_name))

            for fid in candidates:
                file_tokens = set(self.files[fid].tokens)
                if clip_tokens and file_tokens:
                    score = len(clip_tokens & file_tokens) / len(clip_tokens | file_tokens)
                    if score > best_score:
                        best_score = score
                        best_match = fid

            if best_match:
                return (best_match, 0.7 + best_score * 0.2)

        return None

    def _match_by_fuzzy(self, clip: ClipInfo) -> Optional[Tuple[int, float]]:
        """Fuzzy 토큰 매칭"""
        search_text = f"{clip.event_name} {clip.event_number}"
        clip_tokens = set(self._extract_tokens(search_text))

        if not clip_tokens:
            return None

        # 토큰 인덱스로 후보 수집
        candidate_scores: Dict[int, int] = defaultdict(int)
        for token in clip_tokens:
            for file_id in self.by_token.get(token, []):
                candidate_scores[file_id] += 1

        if not candidate_scores:
            return None

        # 상위 후보들에 대해 상세 유사도 계산
        top_candidates = sorted(candidate_scores.items(), key=lambda x: -x[1])[:20]

        best_match = None
        best_score = 0.0

        for file_id, token_hits in top_candidates:
            file_info = self.files[file_id]

            # Jaccard 유사도
            file_tokens = set(file_info.tokens)
            jaccard = len(clip_tokens & file_tokens) / len(clip_tokens | file_tokens) if (clip_tokens | file_tokens) else 0

            # SequenceMatcher 유사도
            seq_score = SequenceMatcher(None,
                self._normalize_text(search_text),
                file_info.normalized_name[:200]
            ).ratio()

            # 종합 점수
            combined = jaccard * 0.6 + seq_score * 0.4

            if combined > best_score:
                best_score = combined
                best_match = file_id

        if best_match and best_score > 0.3:
            return (best_match, best_score)

        return None

    def _get_confidence_level(self, score: float, num_candidates: int) -> ConfidenceLevel:
        """점수와 후보 수로 신뢰도 등급 결정"""
        if score >= 0.85 and num_candidates == 1:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.REVIEW

    def match_with_candidates(self, clip: ClipInfo, max_candidates: int = 5,
                               score_cutoff: float = 40.0) -> ClipInfo:
        """RapidFuzz 기반 다중 후보 매칭

        Args:
            clip: 매칭할 클립 정보
            max_candidates: 최대 후보 수 (기본 5개)
            score_cutoff: 최소 점수 (0-100, 기본 40)

        Returns:
            후보 목록이 포함된 ClipInfo
        """
        if not RAPIDFUZZ_AVAILABLE:
            # Fallback to original matching
            return self.match_clip(clip)

        # 1. 정확한 경로 매칭 시도 (최우선)
        result = self._match_by_path(clip)
        if result:
            file_info = self.files[result[0]]
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "path"
            clip.confidence_level = ConfidenceLevel.HIGH
            clip.candidates = [MatchCandidate(
                file_id=result[0],
                filename=file_info.filename,
                path=file_info.path,
                score=100.0,
                scorer_name="exact_path"
            )]
            return clip

        # 1.5. 2024 PokerGo 클립 패턴 매칭
        result = self._match_2024_pattern(clip)
        if result:
            file_info = self.files[result[0]]
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "2024_pattern"
            clip.confidence_level = ConfidenceLevel.HIGH if result[1] >= 0.85 else ConfidenceLevel.MEDIUM
            clip.candidates = [MatchCandidate(
                file_id=result[0],
                filename=file_info.filename,
                path=file_info.path,
                score=result[1] * 100,
                scorer_name="2024_pattern"
            )]
            return clip

        # 2. 검색 쿼리 구성
        search_parts = []
        if clip.event_name:
            search_parts.append(clip.event_name)
        if clip.event_number:
            search_parts.append(f"Event {clip.event_number}")
        if clip.players:
            search_parts.append(clip.players)

        search_query = " ".join(search_parts)
        if not search_query.strip():
            clip.confidence_level = ConfidenceLevel.UNMATCHED
            return clip

        # 3. 연도/이벤트 기반 사전 필터링으로 검색 범위 축소
        year = clip.source_year or self._extract_year(clip.event_name)
        event_num = self._extract_event_number(clip.event_number + " " + clip.event_name)

        # 후보 풀 구성
        candidate_pool = set()

        # 이벤트 번호로 필터링
        if event_num and event_num in self.by_event_number:
            candidate_pool.update(self.by_event_number[event_num])

        # Main Event의 경우 특별 처리
        if self._is_main_event(clip.event_name):
            for fid, finfo in self.files.items():
                if self._is_main_event(finfo.filename) or self._is_main_event(finfo.path):
                    candidate_pool.add(fid)

        # 연도로 필터링 (후보 풀이 비어있으면 연도 기준으로 시작)
        if not candidate_pool and year:
            candidate_pool.update(self.by_year.get(year, []))

        # 여전히 비어있으면 토큰 기반 후보 추가
        if not candidate_pool:
            query_tokens = self._extract_tokens(search_query)
            for token in query_tokens[:5]:  # 상위 5개 토큰만
                candidate_pool.update(self.by_token.get(token, [])[:100])

        # 후보 풀이 너무 작으면 전체 검색
        if len(candidate_pool) < 10:
            candidate_pool = set(self.files.keys())

        # 4. RapidFuzz로 다중 후보 검색
        choices = {}
        for fid in candidate_pool:
            if fid in self.files:
                finfo = self.files[fid]
                # 파일명 + 상위 폴더를 검색 대상으로
                choices[fid] = f"{finfo.filename} {finfo.parent_folder}"

        if not choices:
            clip.confidence_level = ConfidenceLevel.UNMATCHED
            return clip

        # 여러 스코어러로 매칭
        all_matches = []

        # Token Set Ratio: 단어 순서 무관, 부분 집합 매칭에 강함
        matches = process.extract(
            search_query,
            choices,
            scorer=fuzz.token_set_ratio,
            limit=max_candidates * 2,
            score_cutoff=score_cutoff
        )
        for choice, score, key in matches:
            all_matches.append((key, score, "token_set_ratio"))

        # Token Sort Ratio: 단어 순서 정규화 후 비교
        matches = process.extract(
            search_query,
            choices,
            scorer=fuzz.token_sort_ratio,
            limit=max_candidates,
            score_cutoff=score_cutoff
        )
        for choice, score, key in matches:
            all_matches.append((key, score, "token_sort_ratio"))

        # Partial Ratio: 부분 문자열 매칭
        matches = process.extract(
            search_query,
            choices,
            scorer=fuzz.partial_ratio,
            limit=max_candidates,
            score_cutoff=score_cutoff
        )
        for choice, score, key in matches:
            all_matches.append((key, score, "partial_ratio"))

        # 5. 후보 통합 및 정렬
        candidate_scores: Dict[int, List[Tuple[float, str]]] = defaultdict(list)
        for fid, score, scorer in all_matches:
            candidate_scores[fid].append((score, scorer))

        # 각 후보의 최고 점수와 스코어러 선택
        final_candidates = []
        for fid, scores in candidate_scores.items():
            best_score, best_scorer = max(scores, key=lambda x: x[0])
            avg_score = sum(s[0] for s in scores) / len(scores)
            # 종합 점수: 최고 점수 70% + 평균 30%
            combined_score = best_score * 0.7 + avg_score * 0.3

            finfo = self.files[fid]
            final_candidates.append(MatchCandidate(
                file_id=fid,
                filename=finfo.filename,
                path=finfo.path,
                score=combined_score,
                scorer_name=best_scorer
            ))

        # 점수순 정렬 후 상위 N개
        final_candidates.sort(key=lambda x: -x.score)
        clip.candidates = final_candidates[:max_candidates]

        # 6. 신뢰도 등급 결정 및 최종 매칭
        if clip.candidates:
            top_score = clip.candidates[0].score / 100.0  # 0-1 범위로 변환
            clip.match_confidence = top_score
            clip.matched_file_id = clip.candidates[0].file_id
            clip.match_method = f"rapidfuzz_{clip.candidates[0].scorer_name}"

            # 상위 2개 점수 차이로 확신도 판단
            if len(clip.candidates) >= 2:
                score_gap = clip.candidates[0].score - clip.candidates[1].score
                if score_gap < 5:  # 상위 2개가 5점 이내로 가까우면 검토 필요
                    clip.needs_review = True

            clip.confidence_level = self._get_confidence_level(
                top_score,
                len([c for c in clip.candidates if c.score >= score_cutoff])
            )
        else:
            # 7. Fallback: 선수명 기반 매칭 시도
            result = self._match_by_players(clip)
            if result:
                file_info = self.files[result[0]]
                clip.matched_file_id = result[0]
                clip.match_confidence = result[1]
                clip.match_method = "players"
                clip.confidence_level = ConfidenceLevel.LOW
                clip.candidates = [MatchCandidate(
                    file_id=result[0],
                    filename=file_info.filename,
                    path=file_info.path,
                    score=result[1] * 100,
                    scorer_name="players"
                )]
                clip.needs_review = True  # 선수명 매칭은 항상 검토 필요
            else:
                clip.confidence_level = ConfidenceLevel.UNMATCHED
                clip.match_method = "unmatched"

        return clip

    def match_clip(self, clip: ClipInfo) -> ClipInfo:
        """단일 클립 매칭 (여러 전략 순차 적용)"""

        # 1. 경로 기반 매칭 (가장 정확)
        result = self._match_by_path(clip)
        if result:
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "path"
            return clip

        # 2. Main Event 전용 매칭
        result = self._match_main_event(clip)
        if result:
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "main_event"
            return clip

        # 3. 이벤트 번호 기반 매칭
        result = self._match_by_event(clip)
        if result:
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "event"
            return clip

        # 4. Fuzzy 매칭
        result = self._match_by_fuzzy(clip)
        if result:
            clip.matched_file_id = result[0]
            clip.match_confidence = result[1]
            clip.match_method = "fuzzy"
            return clip

        # 매칭 실패
        clip.match_method = "unmatched"
        return clip

    def load_csv(self, csv_path: str, source_year: str = "") -> List[ClipInfo]:
        """CSV 파일 로드"""
        clips = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 헤더 찾기 (File No. 컬럼)
        header_row = None
        for i, row in enumerate(rows):
            if any('File No' in str(cell) for cell in row):
                header_row = i
                break

        if header_row is None:
            print(f"Warning: Could not find header in {csv_path}")
            return clips

        # 컬럼 인덱스 찾기
        header = rows[header_row]
        col_idx = {}
        for i, col in enumerate(header):
            col_lower = col.lower().strip()
            if 'file no' in col_lower:
                col_idx['file_no'] = i
            elif 'event' in col_lower and 'name' in col_lower:
                col_idx['event_name'] = i
            elif col_lower == 'event':
                col_idx['event_number'] = i
            elif 'nas folder' in col_lower or 'folder link' in col_lower:
                col_idx['nas_folder'] = i
            elif 'player' in col_lower:
                col_idx['players'] = i
            elif 'hand' in col_lower:
                col_idx['hands'] = i
            elif 'timecode' in col_lower:
                col_idx['timecode'] = i
            elif 'short' in col_lower:
                col_idx['shorts'] = i
            elif 'caption' in col_lower:
                col_idx['caption'] = i
            elif 'key point' in col_lower or 'key_point' in col_lower:
                col_idx['key_point'] = i
            elif 'youtube' in col_lower and 'title' in col_lower:
                col_idx['youtube_title'] = i

        # 데이터 파싱
        row_num = 0  # CSV 내 고유 행 번호 (헤더 다음부터 1)
        for row in rows[header_row + 1:]:
            row_num += 1
            if len(row) < 3:
                continue

            # 빈 행 스킵
            file_no = row[col_idx.get('file_no', 0)] if col_idx.get('file_no') is not None else ""
            event_name = row[col_idx.get('event_name', 1)] if col_idx.get('event_name') is not None else ""

            if not file_no and not event_name:
                continue

            # Source code 및 Clip ID 생성 (row_num 기반으로 고유성 보장)
            csv_name = Path(csv_path).name
            source_code = SOURCE_CODES.get(csv_name, "UNK")
            clip_id = f"{source_code}-R{row_num}"  # R = Row number로 고유성 보장

            clip = ClipInfo(
                clip_id=clip_id,
                row_num=row_num,
                file_no=file_no,
                event_number=row[col_idx.get('event_number', 0)] if col_idx.get('event_number') is not None and len(row) > col_idx.get('event_number', 0) else "",
                event_name=event_name,
                nas_folder_link=row[col_idx.get('nas_folder', 0)] if col_idx.get('nas_folder') is not None and len(row) > col_idx.get('nas_folder', 0) else "",
                players=row[col_idx.get('players', 0)] if col_idx.get('players') is not None and len(row) > col_idx.get('players', 0) else "",
                hands=row[col_idx.get('hands', 0)] if col_idx.get('hands') is not None and len(row) > col_idx.get('hands', 0) else "",
                timecode=row[col_idx.get('timecode', 0)] if col_idx.get('timecode') is not None and len(row) > col_idx.get('timecode', 0) else "",
                caption=row[col_idx.get('caption', 0)] if col_idx.get('caption') is not None and len(row) > col_idx.get('caption', 0) else "",
                key_point=row[col_idx.get('key_point', 0)] if col_idx.get('key_point') is not None and len(row) > col_idx.get('key_point', 0) else "",
                youtube_title=row[col_idx.get('youtube_title', 0)] if col_idx.get('youtube_title') is not None and len(row) > col_idx.get('youtube_title', 0) else "",
                is_shorts='TRUE' in str(row[col_idx.get('shorts', 0)]).upper() if col_idx.get('shorts') is not None and len(row) > col_idx.get('shorts', 0) else False,
                source_csv=csv_name,
                source_year=source_year,
                source_code=source_code
            )

            # 타임코드 파싱
            if clip.timecode and '-' in clip.timecode:
                parts = clip.timecode.split('-')
                clip.timecode_start = parts[0].strip()
                clip.timecode_end = parts[1].strip() if len(parts) > 1 else ""

            # 빈 행 필터링 (Event Name과 Players 둘 다 비어있으면 스킵)
            if not clip.event_name.strip() and not clip.players.strip():
                continue

            clips.append(clip)

        return clips

    def match_all(self, clips: List[ClipInfo], use_rapidfuzz: bool = True) -> Dict[str, int]:
        """모든 클립 매칭 및 통계 반환

        Args:
            clips: 매칭할 클립 목록
            use_rapidfuzz: True면 다중 후보 매칭, False면 기존 단일 매칭

        Returns:
            매칭 방법별 통계
        """
        stats = defaultdict(int)

        for i, clip in enumerate(clips):
            if use_rapidfuzz and RAPIDFUZZ_AVAILABLE:
                self.match_with_candidates(clip)
            else:
                self.match_clip(clip)
            stats[clip.match_method] = stats.get(clip.match_method, 0) + 1

            # 진행률 출력 (100개마다)
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(clips)} clips...")

        return dict(stats)

    def match_all_with_review(self, clips: List[ClipInfo]) -> Dict[str, List[ClipInfo]]:
        """모든 클립을 매칭하고 신뢰도 등급별로 분류

        Returns:
            신뢰도 등급별 클립 목록:
            - 'high': 자동 승인 가능
            - 'medium': 높은 신뢰도 (선택적 검토)
            - 'low': 검토 필요
            - 'review': 수동 검토 필수
            - 'unmatched': 매칭 실패
        """
        result = {
            'high': [],
            'medium': [],
            'low': [],
            'review': [],
            'unmatched': []
        }

        for clip in clips:
            self.match_with_candidates(clip)
            result[clip.confidence_level.value].append(clip)

        return result

    def print_results(self, clips: List[ClipInfo], show_unmatched: bool = True):
        """매칭 결과 출력"""
        print("\n" + "=" * 70)
        print("MATCHING RESULTS")
        print("=" * 70)

        matched = [c for c in clips if c.matched_file_id]
        unmatched = [c for c in clips if not c.matched_file_id]

        print(f"\nTotal clips: {len(clips)}")
        print(f"Matched: {len(matched)} ({len(matched)/len(clips)*100:.1f}%)")
        print(f"Unmatched: {len(unmatched)} ({len(unmatched)/len(clips)*100:.1f}%)")

        # 매칭 방법별 통계
        methods = defaultdict(int)
        for c in clips:
            methods[c.match_method] += 1

        print("\nBy method:")
        for method, count in sorted(methods.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")

        # 매칭된 샘플 출력
        print("\n--- Matched Samples ---")
        for clip in matched[:5]:
            file_info = self.files.get(clip.matched_file_id)
            print(f"\nCSV: {clip.event_name[:50]}...")
            print(f"  -> {file_info.filename[:50]}..." if file_info else "  -> ???")
            print(f"     Confidence: {clip.match_confidence:.2f} ({clip.match_method})")

        # 매칭 안 된 샘플 출력
        if show_unmatched and unmatched:
            print("\n--- Unmatched Samples ---")
            for clip in unmatched[:10]:
                print(f"  - {clip.event_number} {clip.event_name[:40]}...")


    def export_unmatched_report(self, clips: List[ClipInfo], output_path: str = "unmatched_clips.csv"):
        """미매칭 클립 리포트 CSV 출력"""
        unmatched = [c for c in clips if not c.matched_file_id]

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Source CSV', 'Year', 'File No', 'Event Number', 'Event Name',
                'Players', 'Timecode', 'Key Point', 'Suggested Files'
            ])

            for clip in unmatched:
                # 유사 파일 후보 추천
                search_text = f"{clip.event_name} {clip.event_number}"
                clip_tokens = set(self._extract_tokens(search_text))

                candidate_scores = defaultdict(int)
                for token in clip_tokens:
                    for file_id in self.by_token.get(token, [])[:50]:
                        candidate_scores[file_id] += 1

                top_files = sorted(candidate_scores.items(), key=lambda x: -x[1])[:3]
                suggestions = []
                for fid, score in top_files:
                    if fid in self.files:
                        suggestions.append(f"{self.files[fid].filename[:40]}... (score:{score})")

                writer.writerow([
                    clip.source_csv,
                    clip.source_year,
                    clip.file_no,
                    clip.event_number,
                    clip.event_name[:60],
                    clip.players[:30] if clip.players else "",
                    clip.timecode,
                    clip.key_point[:40] if clip.key_point else "",
                    " | ".join(suggestions) if suggestions else "No suggestions"
                ])

        print(f"\nExported unmatched report: {output_path} ({len(unmatched)} clips)")
        return output_path

    def export_matched_report(self, clips: List[ClipInfo], output_path: str = "matched_clips.csv"):
        """매칭된 클립 리포트 CSV 출력"""
        matched = [c for c in clips if c.matched_file_id]

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Source CSV', 'Year', 'File No', 'Event Name', 'Players', 'Timecode',
                'Match Method', 'Confidence', 'Matched File ID', 'Matched Filename', 'Matched Path'
            ])

            for clip in matched:
                file_info = self.files.get(clip.matched_file_id)
                writer.writerow([
                    clip.source_csv,
                    clip.source_year,
                    clip.file_no,
                    clip.event_name[:50],
                    clip.players[:30] if clip.players else "",
                    clip.timecode,
                    clip.match_method,
                    f"{clip.match_confidence:.2f}",
                    clip.matched_file_id,
                    file_info.filename if file_info else "",
                    file_info.path[:80] if file_info else ""
                ])

        print(f"\nExported matched report: {output_path} ({len(matched)} clips)")
        return output_path

    def suggest_files(self, search_query: str, limit: int = 10) -> List[Tuple[int, str, float]]:
        """검색어로 파일 후보 추천 (수동 매칭 지원)"""
        tokens = set(self._extract_tokens(search_query))
        if not tokens:
            return []

        candidate_scores = defaultdict(int)
        for token in tokens:
            for file_id in self.by_token.get(token, []):
                candidate_scores[file_id] += 1

        top_candidates = sorted(candidate_scores.items(), key=lambda x: -x[1])[:limit * 2]

        results = []
        for file_id, token_hits in top_candidates:
            file_info = self.files[file_id]
            # 상세 유사도
            file_tokens = set(file_info.tokens)
            jaccard = len(tokens & file_tokens) / len(tokens | file_tokens) if (tokens | file_tokens) else 0
            results.append((file_id, file_info.filename, jaccard))

        results.sort(key=lambda x: -x[2])
        return results[:limit]

    def export_review_report(self, clips: List[ClipInfo], output_path: str = "review_report.csv"):
        """수동 검토용 상세 리포트 (다중 후보 포함)

        복수 후보가 있는 클립들을 검토할 수 있는 상세 리포트 생성.
        각 클립에 대해 최대 5개의 후보 파일과 점수를 표시.
        """
        # 검토 필요한 클립만 필터링 (needs_review 또는 LOW/REVIEW 등급)
        review_clips = [c for c in clips if
                        c.needs_review or
                        c.confidence_level in (ConfidenceLevel.LOW, ConfidenceLevel.REVIEW) or
                        (c.candidates and len(c.candidates) > 1)]

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            # 헤더
            writer.writerow([
                'Clip ID', 'Source CSV', 'Year', 'Event Name', 'Players',
                'Confidence Level', 'Needs Review', 'Top Score',
                'Candidate 1 (ID|Filename|Score)',
                'Candidate 2 (ID|Filename|Score)',
                'Candidate 3 (ID|Filename|Score)',
                'Candidate 4 (ID|Filename|Score)',
                'Candidate 5 (ID|Filename|Score)',
            ])

            for i, clip in enumerate(review_clips, 1):
                # 후보 정보 포맷팅
                candidates_info = []
                for cand in clip.candidates[:5]:
                    candidates_info.append(f"{cand.file_id}|{cand.filename[:40]}|{cand.score:.1f}")
                # 빈 칸 채우기
                while len(candidates_info) < 5:
                    candidates_info.append("")

                writer.writerow([
                    clip.file_no or f"clip_{i}",
                    clip.source_csv,
                    clip.source_year,
                    clip.event_name[:60],
                    clip.players[:30] if clip.players else "",
                    clip.confidence_level.value,
                    "YES" if clip.needs_review else "",
                    f"{clip.match_confidence:.2f}" if clip.match_confidence else "",
                    *candidates_info
                ])

        print(f"\nExported review report: {output_path} ({len(review_clips)} clips need review)")
        return output_path

    def export_single_report(self, clips: List[ClipInfo], output_path: str = "data/output/match.csv"):
        """단일 통합 리포트 생성 (match.csv)

        모든 클립을 하나의 CSV 파일로 출력.
        Match Level 컬럼으로 신뢰도 등급 표시 (high/medium/low/unmatched).
        Clip ID는 {SourceCode}-R{RowNum} 형식으로 고유성 보장.
        Timecode를 Start At, End At으로 분리하여 출력.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Clip ID', 'File No', 'Source Code', 'Source CSV', 'Year',
                'Event Name', 'Players', 'Timecode', 'Start At', 'End At',
                'Match Level', 'Match Method', 'Confidence', 'Needs Review',
                'Matched File ID', 'Matched Filename',
                'Alt Candidate 1', 'Alt Candidate 2'
            ])

            for clip in clips:
                file_info = self.files.get(clip.matched_file_id) if clip.matched_file_id else None

                # Match Level 결정 (high/medium/low/unmatched)
                if clip.confidence_level:
                    match_level = clip.confidence_level.value.lower()
                    # review 등급은 low로 통합
                    if match_level == 'review':
                        match_level = 'low'
                else:
                    match_level = 'unmatched'

                # 대안 후보들
                alt_candidates = []
                for cand in clip.candidates[1:3]:  # 2-3위 후보
                    alt_candidates.append(f"{cand.filename[:30]}({cand.score:.0f})")
                while len(alt_candidates) < 2:
                    alt_candidates.append("")

                # 줄바꿈 문자를 공백으로 치환 (CSV 일관성 유지)
                clean_event_name = clip.event_name.replace('\n', ' ').replace('\r', ' ')[:50]
                clean_players = (clip.players.replace('\n', ' ').replace('\r', ' ')[:30]
                                if clip.players else "")
                clean_timecode = (clip.timecode.replace('\n', ' ').replace('\r', ' ')
                                 if clip.timecode else "")

                # Timecode 분리 (Start At, End At)
                # 작은따옴표 접두사 추가 - 구글 시트에서 텍스트로 인식되도록
                start_at, end_at = parse_timecode(clean_timecode)
                start_at = f"'{start_at}" if start_at else ""
                end_at = f"'{end_at}" if end_at else ""

                writer.writerow([
                    clip.clip_id,
                    clip.file_no,
                    clip.source_code,
                    clip.source_csv,
                    clip.source_year,
                    clean_event_name,
                    clean_players,
                    clean_timecode,
                    start_at,
                    end_at,
                    match_level,
                    clip.match_method,
                    f"{clip.match_confidence:.2f}" if clip.match_confidence else "",
                    "YES" if clip.needs_review else "",
                    clip.matched_file_id or "",
                    file_info.filename[:50] if file_info else "",
                    *alt_candidates
                ])

        print(f"\nExported: {output_path} ({len(clips)} clips)")

        # Match Level별 통계
        stats = {}
        for clip in clips:
            if clip.confidence_level:
                level = clip.confidence_level.value.lower()
                if level == 'review':
                    level = 'low'
            else:
                level = 'unmatched'
            stats[level] = stats.get(level, 0) + 1

        print("Match Level별 통계:")
        for level in ['high', 'medium', 'low', 'unmatched']:
            if level in stats:
                print(f"  {level}: {stats[level]}")

        return output_path

    def export_full_report(self, clips: List[ClipInfo], output_dir: str = "data/output") -> Dict[str, Path]:
        """신뢰도 등급별 분리 리포트 생성

        Args:
            clips: 매칭된 클립 목록
            output_dir: 출력 디렉토리

        Returns:
            등급별 출력 파일 경로
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 등급별 분류
        by_level = {
            'high': [],
            'medium': [],
            'low': [],
            'review': [],
            'unmatched': []
        }

        for clip in clips:
            level = clip.confidence_level.value if clip.confidence_level else 'unmatched'
            by_level[level].append(clip)

        output_paths = {}

        for level, level_clips in by_level.items():
            if not level_clips:
                continue

            output_path = output_dir / f"match_{level}.csv"

            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'File No', 'Source CSV', 'Year', 'Event Name', 'Players', 'Timecode',
                    'Match Method', 'Confidence', 'Needs Review',
                    'Matched File ID', 'Matched Filename',
                    'Alt Candidate 1', 'Alt Candidate 2'
                ])

                for clip in level_clips:
                    file_info = self.files.get(clip.matched_file_id) if clip.matched_file_id else None

                    # 대안 후보들
                    alt_candidates = []
                    for cand in clip.candidates[1:3]:
                        alt_candidates.append(f"{cand.filename[:30]}({cand.score:.0f})")
                    while len(alt_candidates) < 2:
                        alt_candidates.append("")

                    # 줄바꿈 문자를 공백으로 치환 (CSV 일관성 유지)
                    clean_event_name = clip.event_name.replace('\n', ' ').replace('\r', ' ')[:50]
                    clean_players = (clip.players.replace('\n', ' ').replace('\r', ' ')[:30]
                                    if clip.players else "")
                    clean_timecode = (clip.timecode.replace('\n', ' ').replace('\r', ' ')
                                     if clip.timecode else "")

                    writer.writerow([
                        clip.file_no,
                        clip.source_csv,
                        clip.source_year,
                        clean_event_name,
                        clean_players,
                        clean_timecode,
                        clip.match_method,
                        f"{clip.match_confidence:.2f}" if clip.match_confidence else "",
                        "YES" if clip.needs_review else "",
                        clip.matched_file_id or "",
                        file_info.filename[:50] if file_info else "",
                        *alt_candidates
                    ])

            output_paths[level] = output_path
            print(f"Exported: {output_path} ({len(level_clips)} clips)")

        return output_paths

    def print_results_extended(self, clips: List[ClipInfo]):
        """확장된 매칭 결과 출력 (신뢰도 등급 포함)"""
        print("\n" + "=" * 70)
        print("MATCHING RESULTS (Extended)")
        print("=" * 70)

        # 기본 통계
        matched = [c for c in clips if c.matched_file_id]
        unmatched = [c for c in clips if not c.matched_file_id]

        print(f"\nTotal clips: {len(clips)}")
        print(f"Matched: {len(matched)} ({len(matched)/len(clips)*100:.1f}%)")
        print(f"Unmatched: {len(unmatched)} ({len(unmatched)/len(clips)*100:.1f}%)")

        # 신뢰도 등급별 통계
        print("\n신뢰도 등급별:")
        level_counts = defaultdict(int)
        for c in clips:
            level_counts[c.confidence_level.value] += 1

        for level in ['high', 'medium', 'low', 'review', 'unmatched']:
            count = level_counts.get(level, 0)
            pct = count / len(clips) * 100
            indicator = "✓" if level == 'high' else "○" if level == 'medium' else "△" if level == 'low' else "✗"
            print(f"  {indicator} {level.upper():10}: {count:4} ({pct:5.1f}%)")

        # 검토 필요 통계
        needs_review = [c for c in clips if c.needs_review]
        print(f"\n복수 후보 검토 필요: {len(needs_review)}")

        # 매칭 방법별 통계
        print("\n매칭 방법별:")
        methods = defaultdict(int)
        for c in clips:
            methods[c.match_method] += 1
        for method, count in sorted(methods.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")

        # 샘플 출력 (검토 필요한 항목)
        if needs_review:
            print("\n--- 검토 필요 샘플 (상위 2개 후보 점수 유사) ---")
            for clip in needs_review[:5]:
                print(f"\n  CSV: {clip.event_name[:50]}...")
                for i, cand in enumerate(clip.candidates[:3], 1):
                    marker = "→" if i == 1 else " "
                    print(f"    {marker} [{cand.file_id}] {cand.filename[:40]}... (score: {cand.score:.1f})")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Clip Matcher - CSV to Archive File Matching (with RapidFuzz)")
    parser.add_argument('--export', action='store_true', help="Export matched/unmatched reports")
    parser.add_argument('--full-report', action='store_true', help="Export full reports by confidence level (분리된 파일)")
    parser.add_argument('--unified', action='store_true', help="Export unified match.csv with Match Level column (통합 파일)")
    parser.add_argument('--output', type=str, default="data/output/match.csv", help="Output path for unified report")
    parser.add_argument('--review-report', action='store_true', help="Export review report for ambiguous matches")
    parser.add_argument('--search', type=str, help="Search for files matching query")
    parser.add_argument('--legacy', action='store_true', help="Use legacy matching (without RapidFuzz)")
    parser.add_argument('--max-candidates', type=int, default=5, help="Max candidates per clip (default: 5)")
    parser.add_argument('--score-cutoff', type=float, default=40.0, help="Min score cutoff 0-100 (default: 40)")
    args = parser.parse_args()

    print("=" * 70)
    print("Clip Matcher - CSV to Archive File Matching")
    print(f"RapidFuzz: {'Available' if RAPIDFUZZ_AVAILABLE else 'Not Available'}")
    print("=" * 70)

    matcher = ClipMatcher("archive.db")

    # 검색 모드
    if args.search:
        print(f"\nSearching for: {args.search}")
        results = matcher.suggest_files(args.search, limit=15)
        print(f"\nTop {len(results)} matches:")
        for i, (fid, fname, score) in enumerate(results, 1):
            print(f"  {i}. [{fid}] {fname[:60]}... (score: {score:.2f})")
        return None, matcher

    # CSV 파일들 로드 (data/input/ 폴더에서)
    csv_files = [
        ("data/input/WSOP HAND SELECTION -  2024 WSOP Clip Tracker.csv", "2024"),
        ("data/input/WSOP HAND SELECTION - 2025 WSOP Clip Tracker.csv", "2025"),
        ("data/input/WSOP HAND SELECTION - 2025 WSOP Cyprus SC Clip Tracker.csv", "2025"),
        ("data/input/WSOP HAND SELECTION - 2025 WSOP Europe Clip Tracker.csv", "2025"),
    ]

    all_clips = []

    for csv_path, year in csv_files:
        if Path(csv_path).exists():
            print(f"\nLoading: {csv_path}")
            clips = matcher.load_csv(csv_path, year)
            print(f"  Loaded {len(clips)} clips")
            all_clips.extend(clips)

    print(f"\nTotal clips loaded: {len(all_clips)}")

    # 매칭 실행
    if args.legacy or not RAPIDFUZZ_AVAILABLE:
        print("\nMatching clips (legacy mode)...")
        stats = matcher.match_all(all_clips, use_rapidfuzz=False)
        matcher.print_results(all_clips)
    else:
        print(f"\nMatching clips (RapidFuzz, max_candidates={args.max_candidates}, cutoff={args.score_cutoff})...")
        for clip in all_clips:
            matcher.match_with_candidates(clip, max_candidates=args.max_candidates, score_cutoff=args.score_cutoff)
        matcher.print_results_extended(all_clips)

    # 리포트 내보내기
    if args.export:
        matcher.export_matched_report(all_clips, "matched_clips.csv")
        matcher.export_unmatched_report(all_clips, "unmatched_clips.csv")

    if args.review_report:
        matcher.export_review_report(all_clips, "review_report.csv")

    if args.full_report:
        print("\nGenerating full reports by confidence level (분리된 파일)...")
        matcher.export_full_report(all_clips, "data/output")

    if args.unified:
        print("\nGenerating unified report with Match Level column (통합 파일)...")
        matcher.export_single_report(all_clips, args.output)

    return all_clips, matcher


if __name__ == "__main__":
    clips, matcher = main()
