"""iconik CSV와 match.csv 매칭 분석 스크립트

두 파일의 title/filename 패턴을 분석하고 매칭 전략을 제안합니다.
"""

import csv
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List, Tuple

# 프로젝트 src 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False


def extract_file_key(filename: str) -> Dict[str, any]:
    """파일명에서 매칭 키 추출

    패턴: {번호}-wsop-{연도}-{타입}-ev-{이벤트번호}-{나머지}
    """
    result = {
        'prefix_number': None,
        'year': None,
        'event_number': None,
        'event_type': None,  # 'be' (bracelet event) or 'me' (main event)
        'game_type': None,
        'players': [],
        'raw': filename,
    }

    # 번호 접두사 추출 (예: "32-" -> 32)
    prefix_match = re.match(r'^(\d+)-', filename)
    if prefix_match:
        result['prefix_number'] = int(prefix_match.group(1))

    # 연도 추출
    year_match = re.search(r'(20\d{2})', filename)
    if year_match:
        result['year'] = int(year_match.group(1))

    # 이벤트 번호 추출 (ev-XX 또는 ev_XX)
    event_match = re.search(r'ev[-_]?(\d+)', filename.lower())
    if event_match:
        result['event_number'] = int(event_match.group(1))

    # 이벤트 타입 (be = bracelet event, me = main event)
    if '-be-' in filename.lower():
        result['event_type'] = 'be'
    elif '-me-' in filename.lower():
        result['event_type'] = 'me'

    # 게임 타입 추출
    game_types = ['nlh', 'plo', 'ppc', 'stud', 'omaha', '2-7', 'td']
    for gt in game_types:
        if gt in filename.lower():
            result['game_type'] = gt
            break

    # 선수 이름 추출 (대문자로 시작하는 단어들)
    # 주요 선수 목록
    known_players = [
        'negreanu', 'ivey', 'hellmuth', 'ausmus', 'yockey', 'bleznick',
        'bonomo', 'foxen', 'astedt', 'tamayo', 'griff', 'mateos',
        'seidel', 'deeb', 'kornuth', 'rast', 'serock', 'coelho'
    ]
    for player in known_players:
        if player in filename.lower():
            result['players'].append(player)

    return result


def load_iconik_csv(csv_path: str) -> List[Dict]:
    """iconik CSV 로드"""
    clips = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title', '').strip()
            if not title or 'test' in title.lower():
                continue

            clips.append({
                'iconik_id': row.get('id', ''),
                'title': title,
                'description': row.get('Description', ''),
                'project_name': row.get('ProjectName', ''),
                'episode_event': row.get('EpisodeEvent', ''),
                'players_tags': row.get('PlayersTags', ''),
                'hand_grade': row.get('HandGrade', ''),
                'key': extract_file_key(title),
            })
    return clips


def load_match_csv(csv_path: str) -> List[Dict]:
    """match.csv 로드"""
    matches = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            matched_filename = row.get('Matched Filename', '').strip()
            if not matched_filename:
                continue

            matches.append({
                'clip_id': row.get('Clip ID', ''),
                'file_no': row.get('File No', ''),
                'source_code': row.get('Source Code', ''),
                'year': row.get('Year', ''),
                'event_name': row.get('Event Name', ''),
                'players': row.get('Players', ''),
                'matched_filename': matched_filename,
                'matched_file_id': row.get('Matched File ID', ''),
                'match_level': row.get('Match Level', ''),
                'confidence': row.get('Confidence', ''),
                'key': extract_file_key(matched_filename),
            })
    return matches


def match_by_prefix_number(iconik_clips: List[Dict], match_records: List[Dict]) -> Dict[str, Dict]:
    """접두사 번호로 매칭"""
    # match.csv를 접두사 번호로 인덱싱
    match_by_prefix = defaultdict(list)
    for rec in match_records:
        prefix = rec['key']['prefix_number']
        if prefix:
            match_by_prefix[prefix].append(rec)

    results = {}
    for clip in iconik_clips:
        prefix = clip['key']['prefix_number']
        if prefix and prefix in match_by_prefix:
            candidates = match_by_prefix[prefix]
            # 연도도 같은지 확인
            for candidate in candidates:
                if candidate['key']['year'] == clip['key']['year']:
                    results[clip['iconik_id']] = {
                        'iconik_title': clip['title'],
                        'matched_filename': candidate['matched_filename'],
                        'matched_file_id': candidate['matched_file_id'],
                        'match_method': 'prefix_number',
                        'confidence': 0.95,
                    }
                    break

    return results


def extract_players_from_title(title: str) -> List[str]:
    """iconik title에서 선수 이름 추출

    패턴: ...Yerushlami-FH-ov-Rehmani... → ['yerushalmi', 'rehmani']
    """
    players = []
    title_lower = title.lower()

    # 알려진 선수 이름 목록 (확장)
    known_players = [
        'negreanu', 'ivey', 'hellmuth', 'ausmus', 'yockey', 'bleznick',
        'bonomo', 'foxen', 'astedt', 'tamayo', 'griff', 'mateos',
        'seidel', 'deeb', 'kornuth', 'rast', 'serock', 'coelho',
        'yerushalmi', 'yerushlami', 'rehmani', 'koury', 'cournut', 'ross',
        'morris', 'cho', 'waxman', 'henry', 'gortney', 'alcindor', 'loving',
        'little', 'witdoek', 'eichele', 'phan', 'hutter', 'bershadskiy',
        'vinczeffy', 'eisenberg', 'zinno', 'berry', 'bifarella', 'lowe',
        'bryant', 'hachem', 'coleman', 'fan', 'yea', 'gordon',
        'bechahed', 'hart', 'gheba', 'schutten', 'stafman', 'sepiol',
        'strelitz', 'winters', 'britton', 'li', 'patur', 'benton',
        'wong', 'mercier', 'seward', 'holskyi', 'galiana', 'guilbert',
        'margolin', 'hendrix', 'aido', 'hunichen', 'volpe', 'daly',
        'edengren', 'melson', 'yosifov', 'badziakouski', 'tollerne',
        'funaro', 'nakanishi', 'carey', 'spitale', 'checkwicz', 'kliper',
        'liao', 'okamoto', 'neves', 'johnson', 'adkins', 'nakache',
        'watson', 'krela', 'eldridge', 'conniff', 'tasyurek', 'jattin',
        'moulder', 'racener', 'anderson', 'sternheimer',
    ]

    for player in known_players:
        if player in title_lower:
            # 정규화된 이름 저장
            normalized = player.replace('yerushlami', 'yerushalmi')  # 스펠링 변형 처리
            players.append(normalized)

    return players


def extract_players_from_match(players_str: str) -> List[str]:
    """match.csv Players 컬럼에서 선수 이름 추출

    패턴: "YERUSHALMI vs REHMANI" → ['yerushalmi', 'rehmani']
    """
    if not players_str:
        return []

    # vs로 분리
    players = []
    for part in re.split(r'\s+vs\s+', players_str, flags=re.IGNORECASE):
        # 이름만 추출 (공백, 특수문자 제거)
        name = re.sub(r'[^a-zA-Z]', '', part).lower()
        if name and len(name) > 2:
            players.append(name)

    return players


def extract_day_number(text: str) -> Optional[str]:
    """Day 번호 추출

    예: "day1a", "Day 1A", "day-1-a" → "day1a"
    """
    text_lower = text.lower().replace(' ', '').replace('-', '').replace('_', '')

    # Main Event day 패턴
    day_match = re.search(r'day(\d+[a-d]?)', text_lower)
    if day_match:
        return f"day{day_match.group(1)}"

    # Final Table
    if 'finaltable' in text_lower or 'ft' in text_lower:
        ft_day = re.search(r'day(\d+)', text_lower)
        if ft_day:
            return f"ft-day{ft_day.group(1)}"
        return 'ft'

    return None


def match_by_players_and_day(iconik_clips: List[Dict], match_records: List[Dict],
                             already_matched: set) -> Dict[str, Dict]:
    """선수 이름 + Day 번호로 Main Event 매칭"""

    # match.csv에서 Main Event 레코드 필터링 및 인덱싱
    main_event_records = []
    for rec in match_records:
        event_name = rec.get('event_name', '').lower()
        if 'main event' in event_name:
            rec['_players'] = extract_players_from_match(rec.get('players', ''))
            rec['_day'] = extract_day_number(event_name)
            main_event_records.append(rec)

    results = {}
    for clip in iconik_clips:
        if clip['iconik_id'] in already_matched:
            continue

        # Main Event 클립인지 확인
        if clip['key']['event_type'] != 'me':
            continue

        clip_players = extract_players_from_title(clip['title'])
        clip_day = extract_day_number(clip['title'])

        if not clip_players:
            continue

        # 매칭 후보 찾기
        best_candidate = None
        best_score = 0

        for rec in main_event_records:
            score = 0

            # 선수 이름 매칭 (가장 중요)
            rec_players = rec['_players']
            common_players = set(clip_players) & set(rec_players)
            if common_players:
                score += len(common_players) * 30

            # Day 매칭
            if clip_day and rec['_day']:
                if clip_day == rec['_day']:
                    score += 20
                elif clip_day[:4] == rec['_day'][:4]:  # day1 vs day1a
                    score += 10

            if score > best_score:
                best_score = score
                best_candidate = rec

        if best_candidate and best_score >= 30:  # 최소 1명의 선수 매칭 필요
            results[clip['iconik_id']] = {
                'iconik_title': clip['title'],
                'matched_filename': best_candidate['matched_filename'],
                'matched_file_id': best_candidate['matched_file_id'],
                'match_method': 'players_day',
                'confidence': min(0.90, 0.60 + best_score / 100),
            }

    return results


def match_by_event_number(iconik_clips: List[Dict], match_records: List[Dict],
                          already_matched: set) -> Dict[str, Dict]:
    """이벤트 번호 + 연도로 매칭"""
    # match.csv를 (연도, 이벤트번호)로 인덱싱
    match_by_event = defaultdict(list)
    for rec in match_records:
        year = rec['key']['year']
        event_num = rec['key']['event_number']
        if year and event_num:
            match_by_event[(year, event_num)].append(rec)

    results = {}
    for clip in iconik_clips:
        if clip['iconik_id'] in already_matched:
            continue

        year = clip['key']['year']
        event_num = clip['key']['event_number']

        if year and event_num and (year, event_num) in match_by_event:
            candidates = match_by_event[(year, event_num)]
            # 선수 이름으로 추가 필터링
            best_candidate = None
            best_score = 0

            for candidate in candidates:
                score = 0
                # 선수 이름 매칭
                clip_players = set(clip['key']['players'])
                cand_players = set(candidate['key']['players'])
                if clip_players & cand_players:
                    score += len(clip_players & cand_players) * 10

                # 게임 타입 매칭
                if clip['key']['game_type'] == candidate['key']['game_type']:
                    score += 5

                if score > best_score:
                    best_score = score
                    best_candidate = candidate

            if best_candidate:
                results[clip['iconik_id']] = {
                    'iconik_title': clip['title'],
                    'matched_filename': best_candidate['matched_filename'],
                    'matched_file_id': best_candidate['matched_file_id'],
                    'match_method': 'event_number',
                    'confidence': 0.85,
                }

    return results


def match_by_fuzzy(iconik_clips: List[Dict], match_records: List[Dict],
                   already_matched: set, threshold: int = 70) -> Dict[str, Dict]:
    """퍼지 매칭으로 나머지 매칭"""
    if not FUZZY_AVAILABLE:
        return {}

    # match.csv 파일명 목록
    match_filenames = [rec['matched_filename'] for rec in match_records]
    match_map = {rec['matched_filename']: rec for rec in match_records}

    results = {}
    for clip in iconik_clips:
        if clip['iconik_id'] in already_matched:
            continue

        # 퍼지 매칭
        match_result = process.extractOne(
            clip['title'],
            match_filenames,
            scorer=fuzz.token_set_ratio,
            score_cutoff=threshold
        )

        if match_result:
            matched_filename, score, _ = match_result
            rec = match_map[matched_filename]
            results[clip['iconik_id']] = {
                'iconik_title': clip['title'],
                'matched_filename': matched_filename,
                'matched_file_id': rec['matched_file_id'],
                'match_method': 'fuzzy',
                'confidence': score / 100.0,
            }

    return results


def analyze_and_match(iconik_csv: str, match_csv: str) -> Dict[str, any]:
    """전체 매칭 분석 실행"""
    print("=" * 70)
    print("           iconik CSV ↔ match.csv 매칭 분석")
    print("=" * 70)

    # 데이터 로드
    print("\n[1] 데이터 로드 중...")
    iconik_clips = load_iconik_csv(iconik_csv)
    match_records = load_match_csv(match_csv)

    print(f"  - iconik CSV: {len(iconik_clips)} 클립")
    print(f"  - match.csv: {len(match_records)} 레코드")

    # 매칭 수행
    print("\n[2] 매칭 수행 중...")

    # 1단계: 접두사 번호 매칭 (Bracelet Events)
    prefix_matches = match_by_prefix_number(iconik_clips, match_records)
    print(f"  - 접두사 번호 매칭: {len(prefix_matches)}개")

    # 2단계: 선수 이름 + Day 매칭 (Main Event)
    matched_ids = set(prefix_matches.keys())
    players_day_matches = match_by_players_and_day(iconik_clips, match_records, matched_ids)
    print(f"  - 선수+Day 매칭 (ME): {len(players_day_matches)}개")

    # 3단계: 이벤트 번호 매칭
    matched_ids.update(players_day_matches.keys())
    event_matches = match_by_event_number(iconik_clips, match_records, matched_ids)
    print(f"  - 이벤트 번호 매칭: {len(event_matches)}개")

    # 4단계: 퍼지 매칭
    matched_ids.update(event_matches.keys())
    fuzzy_matches = match_by_fuzzy(iconik_clips, match_records, matched_ids)
    print(f"  - 퍼지 매칭: {len(fuzzy_matches)}개")

    # 결과 통합
    all_matches = {**prefix_matches, **players_day_matches, **event_matches, **fuzzy_matches}
    unmatched = [c for c in iconik_clips if c['iconik_id'] not in all_matches]

    # 통계
    print("\n[3] 매칭 결과")
    print("-" * 70)
    print(f"  총 클립: {len(iconik_clips)}개")
    print(f"  매칭 성공: {len(all_matches)}개 ({len(all_matches)/len(iconik_clips)*100:.1f}%)")
    print(f"  미매칭: {len(unmatched)}개")

    # 매칭 방법별 통계
    method_counts = defaultdict(int)
    for m in all_matches.values():
        method_counts[m['match_method']] += 1

    print("\n  [매칭 방법별]")
    for method, count in method_counts.items():
        print(f"    {method}: {count}개")

    # 미매칭 샘플 출력
    if unmatched:
        print("\n[4] 미매칭 샘플 (상위 10개)")
        print("-" * 70)
        for clip in unmatched[:10]:
            print(f"  - {clip['title'][:60]}...")
            print(f"    프로젝트: {clip['project_name']}, 이벤트: {clip['episode_event']}")

    # 매칭 샘플 출력
    print("\n[5] 매칭 샘플 (상위 10개)")
    print("-" * 70)
    for i, (iconik_id, match_info) in enumerate(list(all_matches.items())[:10]):
        print(f"  [{i+1}] {match_info['match_method']} (신뢰도: {match_info['confidence']:.2f})")
        print(f"      iconik: {match_info['iconik_title'][:50]}...")
        print(f"      match:  {match_info['matched_filename'][:50]}...")

    print("\n" + "=" * 70)

    return {
        'total_clips': len(iconik_clips),
        'matched': len(all_matches),
        'unmatched': len(unmatched),
        'matches': all_matches,
        'unmatched_clips': unmatched,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='iconik CSV와 match.csv 매칭 분석')
    parser.add_argument('--iconik', '-i', required=True, help='iconik CSV 파일 경로')
    parser.add_argument('--match', '-m', required=True, help='match.csv 파일 경로')
    parser.add_argument('--output', '-o', help='매칭 결과 출력 CSV 경로')

    args = parser.parse_args()

    result = analyze_and_match(args.iconik, args.match)

    # 결과 CSV 저장
    if args.output:
        with open(args.output, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'iconik_id', 'iconik_title', 'matched_filename',
                'matched_file_id', 'match_method', 'confidence'
            ])
            for iconik_id, match_info in result['matches'].items():
                writer.writerow([
                    iconik_id,
                    match_info['iconik_title'],
                    match_info['matched_filename'],
                    match_info['matched_file_id'],
                    match_info['match_method'],
                    match_info['confidence'],
                ])
        print(f"\n매칭 결과가 {args.output}에 저장되었습니다.")


if __name__ == "__main__":
    main()
