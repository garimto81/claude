#!/usr/bin/env python3
"""
Google Slides API를 사용하여 프레젠테이션 읽기
NBA TV 레퍼런스 스크린샷 분석용
"""

import os
import sys
from pathlib import Path

# Windows 콘솔 인코딩 문제 해결
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# OAuth 인증 관련
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 절대 경로 사용 (서브 레포에서도 동작)
CREDENTIALS_FILE = r'C:\claude\json\desktop_credentials.json'
TOKEN_FILE = r'C:\claude\json\token_slides.json'

# Slides API 읽기 권한 + Drive 다운로드 권한
SCOPES = [
    'https://www.googleapis.com/auth/presentations.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# 프레젠테이션 ID
PRESENTATION_ID = '12czNJ9OmJjzu-Nii1ZefIjNgov94I8gNIyXNVdBv9I4'

# 이미지 저장 경로
OUTPUT_DIR = Path(r'C:\claude\wsoptv_ott\docs\images\nbatv-reference')


def get_credentials():
    """OAuth 2.0 인증 수행"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ 인증 파일 없음: {CREDENTIALS_FILE}")
                print("   Google Cloud Console에서 OAuth 클라이언트 ID를 다운로드하세요.")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ 토큰 저장: {TOKEN_FILE}")

    return creds


def read_presentation(presentation_id: str):
    """프레젠테이션 내용 읽기"""
    creds = get_credentials()

    # Slides API 서비스 생성
    slides_service = build('slides', 'v1', credentials=creds)

    # 프레젠테이션 가져오기
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    title = presentation.get('title', 'Untitled')
    slides = presentation.get('slides', [])

    print(f"\n📊 프레젠테이션: {title}")
    print(f"   슬라이드 수: {len(slides)}")
    print("-" * 50)

    return presentation, slides


def extract_slide_content(slide, index: int):
    """슬라이드 내용 추출"""
    print(f"\n📄 슬라이드 {index + 1}")

    page_elements = slide.get('pageElements', [])

    texts = []
    images = []

    for element in page_elements:
        # 텍스트 추출
        if 'shape' in element:
            shape = element['shape']
            if 'text' in shape:
                text_content = shape['text']
                for text_element in text_content.get('textElements', []):
                    if 'textRun' in text_element:
                        content = text_element['textRun'].get('content', '').strip()
                        if content:
                            texts.append(content)

        # 이미지 추출
        if 'image' in element:
            image = element['image']
            content_url = image.get('contentUrl')
            source_url = image.get('sourceUrl')

            if content_url:
                images.append({
                    'type': 'content',
                    'url': content_url,
                    'element_id': element.get('objectId')
                })
            elif source_url:
                images.append({
                    'type': 'source',
                    'url': source_url,
                    'element_id': element.get('objectId')
                })

    if texts:
        print(f"   텍스트: {' | '.join(texts[:5])}")  # 최대 5개만 출력

    if images:
        print(f"   이미지: {len(images)}개")

    return {
        'index': index,
        'texts': texts,
        'images': images
    }


def download_image(url: str, output_path: Path, creds):
    """이미지 다운로드"""
    try:
        import requests

        # OAuth 토큰을 헤더에 추가
        headers = {
            'Authorization': f'Bearer {creds.token}'
        }

        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"   ❌ 다운로드 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 에러: {e}")
        return False


def export_slide_as_image(slides_service, presentation_id: str, slide_id: str,
                          output_path: Path, creds):
    """슬라이드를 이미지로 내보내기"""
    try:
        # 슬라이드 썸네일 가져오기
        thumbnail = slides_service.presentations().pages().getThumbnail(
            presentationId=presentation_id,
            pageObjectId=slide_id,
            thumbnailProperties_mimeType='PNG',
            thumbnailProperties_thumbnailSize='LARGE'
        ).execute()

        content_url = thumbnail.get('contentUrl')

        if content_url:
            return download_image(content_url, output_path, creds)

        return False
    except Exception as e:
        print(f"   ❌ 썸네일 내보내기 실패: {e}")
        return False


def main():
    """메인 실행"""
    print("=" * 50)
    print("Google Slides 읽기 - NBA TV 레퍼런스")
    print("=" * 50)

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # 프레젠테이션 읽기
        presentation, slides = read_presentation(PRESENTATION_ID)

        creds = get_credentials()
        slides_service = build('slides', 'v1', credentials=creds)

        # 각 슬라이드 처리
        slide_data = []
        for i, slide in enumerate(slides):
            content = extract_slide_content(slide, i)
            slide_data.append(content)

            # 슬라이드를 이미지로 내보내기
            slide_id = slide.get('objectId')
            output_path = OUTPUT_DIR / f"slide_{i+1:02d}.png"

            print(f"   📥 이미지 저장 중: {output_path.name}")
            success = export_slide_as_image(
                slides_service, PRESENTATION_ID, slide_id, output_path, creds
            )

            if success:
                print(f"   ✅ 저장 완료: {output_path}")

        print("\n" + "=" * 50)
        print(f"✅ 완료: {len(slides)}개 슬라이드 처리")
        print(f"   이미지 저장 위치: {OUTPUT_DIR}")
        print("=" * 50)

        # 요약 생성
        summary_path = OUTPUT_DIR / "README.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# NBA TV 레퍼런스 스크린샷\n\n")
            f.write(f"**소스**: [Google Slides]({PRESENTATION_ID})\n\n")
            f.write(f"**총 슬라이드**: {len(slides)}개\n\n")
            f.write("---\n\n")

            for data in slide_data:
                f.write(f"## 슬라이드 {data['index'] + 1}\n\n")
                if data['texts']:
                    f.write(f"**텍스트**: {' | '.join(data['texts'][:3])}\n\n")
                f.write(f"![Slide {data['index'] + 1}](slide_{data['index']+1:02d}.png)\n\n")

        print(f"📝 요약 파일: {summary_path}")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
