"""Google Sheets 연동 상태 확인 스크립트"""
import os
import sys

def check_google_sheets():
    """Google Sheets 연동 확인"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        print(f"❌ Google API 라이브러리 없음: {e}")
        print("설치: pip install google-api-python-client google-auth")
        return

    SERVICE_ACCOUNT_FILE = r'D:\AI\claude01\json\service_account_key.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ 서비스 계정 파일 없음: {SERVICE_ACCOUNT_FILE}")
        return

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)

        # 1. 메인 동기화 시트
        print("=" * 60)
        print("=== 메인 동기화 시트 (pokervod.db) ===")
        print("=" * 60)
        MAIN_ID = '1TW2ON5CQyIrL8aGQNYJ4OWkbZMaGmY9DoDG9VFXU60I'

        try:
            meta = service.spreadsheets().get(spreadsheetId=MAIN_ID).execute()
            sheets = meta.get('sheets', [])
            print(f"스프레드시트: {meta.get('properties', {}).get('title')}")
            print(f"시트 수: {len(sheets)}")
            print("\n시트 목록:")
            for s in sheets[:10]:
                props = s.get('properties', {})
                rows = props.get('gridProperties', {}).get('rowCount', 0)
                print(f"  - {props.get('title')}: {rows}행")
        except Exception as e:
            print(f"❌ 메인 시트 접근 실패: {e}")

        # 2. Archive Team Hands 시트
        print("\n" + "=" * 60)
        print("=== Archive Team Hands 시트 ===")
        print("=" * 60)
        ARCHIVE_ID = '1_RN_W_ZQclSZA0Iez6XniCXVtjkkd5HNZwiT6l-z6d4'

        try:
            meta = service.spreadsheets().get(spreadsheetId=ARCHIVE_ID).execute()
            sheets = meta.get('sheets', [])
            print(f"스프레드시트: {meta.get('properties', {}).get('title')}")
            print(f"시트 수: {len(sheets)}")
            print("\n시트 목록:")
            for s in sheets[:10]:
                props = s.get('properties', {})
                rows = props.get('gridProperties', {}).get('rowCount', 0)
                print(f"  - {props.get('title')}: {rows}행")

            # 첫 시트 헤더 읽기
            if sheets:
                first_sheet = sheets[0].get('properties', {}).get('title')
                result = service.spreadsheets().values().get(
                    spreadsheetId=ARCHIVE_ID,
                    range=f"'{first_sheet}'!A1:Z3"
                ).execute()
                values = result.get('values', [])
                print(f"\n첫 3행 미리보기 ({first_sheet}):")
                for i, row in enumerate(values):
                    display = row[:6] if len(row) > 6 else row
                    print(f"  행{i+1}: {display}")
        except Exception as e:
            print(f"❌ Archive 시트 접근 실패: {e}")

    except Exception as e:
        print(f"❌ 인증 오류: {e}")


def check_local_db():
    """로컬 데이터베이스 확인"""
    import sqlite3

    print("\n" + "=" * 60)
    print("=== 로컬 데이터베이스 확인 ===")
    print("=" * 60)

    dbs = [
        ('archive.db', 'C:/claude/archive-analyzer/data/output/archive.db'),
        ('pokervod.db', 'D:/AI/claude01/shared-data/pokervod.db'),
    ]

    for name, path in dbs:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"\n✅ {name}: {size_mb:.2f} MB")

            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = cursor.fetchall()
                print(f"   테이블 ({len(tables)}개):")
                for t in tables[:8]:
                    cursor.execute(f"SELECT COUNT(*) FROM [{t[0]}]")
                    count = cursor.fetchone()[0]
                    print(f"     - {t[0]}: {count}행")
                if len(tables) > 8:
                    print(f"     ... 외 {len(tables) - 8}개")
                conn.close()
            except Exception as e:
                print(f"   DB 읽기 오류: {e}")
        else:
            print(f"\n❌ {name}: 파일 없음 ({path})")


if __name__ == '__main__':
    check_google_sheets()
    check_local_db()
