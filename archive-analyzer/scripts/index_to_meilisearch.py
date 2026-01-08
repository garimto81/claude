#!/usr/bin/env python
"""MeiliSearch 인덱싱 스크립트

archive.db 데이터를 MeiliSearch로 인덱싱합니다.

사용법:
    python scripts/index_to_meilisearch.py [--db-path PATH] [--clear]
"""

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archive_analyzer.search import SearchService, SearchConfig, MEILISEARCH_AVAILABLE


def main():
    parser = argparse.ArgumentParser(description="MeiliSearch 인덱싱")
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/output/archive.db",
        help="archive.db 경로 (기본: data/output/archive.db)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:7700",
        help="MeiliSearch 호스트 (기본: http://localhost:7700)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="archive-analyzer-dev-key",
        help="MeiliSearch API 키",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="기존 인덱스 초기화 후 재인덱싱",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="인덱스 통계만 조회",
    )

    args = parser.parse_args()

    if not MEILISEARCH_AVAILABLE:
        print("오류: meilisearch 패키지가 설치되지 않았습니다.")
        print("설치: pip install meilisearch")
        sys.exit(1)

    # DB 경로 확인
    db_path = Path(args.db_path)
    if not db_path.exists() and not args.stats:
        print(f"오류: DB 파일을 찾을 수 없습니다: {db_path}")
        sys.exit(1)

    # SearchService 초기화
    config = SearchConfig(host=args.host, api_key=args.api_key)

    try:
        service = SearchService(config)
    except Exception as e:
        print(f"오류: MeiliSearch 연결 실패: {e}")
        print(f"MeiliSearch가 {args.host}에서 실행 중인지 확인하세요.")
        print("Docker 시작: docker-compose up -d")
        sys.exit(1)

    # 헬스 체크
    if not service.health_check():
        print("오류: MeiliSearch 서버가 응답하지 않습니다.")
        sys.exit(1)

    print(f"MeiliSearch 연결 성공: {args.host}")

    # 통계 조회 모드
    if args.stats:
        print("\n=== 인덱스 통계 ===")
        stats = service.get_stats()
        for index_name, index_stats in stats.items():
            if "error" in index_stats:
                print(f"  {index_name}: 오류 - {index_stats['error']}")
            else:
                doc_count = index_stats.get("numberOfDocuments", 0)
                is_indexing = index_stats.get("isIndexing", False)
                status = "인덱싱 중" if is_indexing else "완료"
                print(f"  {index_name}: {doc_count}건 ({status})")
        return

    # 기존 인덱스 초기화
    if args.clear:
        print("\n기존 인덱스 초기화 중...")
        service.clear_all()
        print("초기화 완료")

    # 인덱싱 실행
    print(f"\n인덱싱 시작: {db_path}")
    try:
        results = service.index_from_db(str(db_path))
        print("\n=== 인덱싱 결과 ===")
        for table, count in results.items():
            print(f"  {table}: {count}건")
        print("\n인덱싱 완료!")
    except Exception as e:
        print(f"오류: 인덱싱 실패: {e}")
        sys.exit(1)

    # 최종 통계
    print("\n=== 최종 통계 ===")
    stats = service.get_stats()
    for index_name, index_stats in stats.items():
        if "error" not in index_stats:
            doc_count = index_stats.get("numberOfDocuments", 0)
            print(f"  {index_name}: {doc_count}건")


if __name__ == "__main__":
    main()
