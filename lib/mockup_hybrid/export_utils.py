"""
목업 내보내기 유틸리티

HTML 파일 저장, Playwright 스크린샷, PRD 연결 등을 처리합니다.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def save_html(
    content: str,
    output_path: Path,
    title: str = "Mockup",
    description: str = "",
) -> Path:
    """
    HTML 콘텐츠를 파일로 저장

    Args:
        content: HTML 콘텐츠
        output_path: 저장 경로
        title: 문서 제목
        description: 문서 설명

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 플레이스홀더 치환
    content = content.replace("{{title}}", title)
    content = content.replace("{{description}}", description)
    content = content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))

    # 파일 저장
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"HTML 저장: {output_path}")

    return output_path


def capture_screenshot(
    html_path: Path,
    image_path: Path,
    selector: Optional[str] = None,
    full_page: bool = False,
    width: int = 800,
    height: int = 600,
) -> Optional[Path]:
    """
    Playwright로 HTML 스크린샷 캡처

    Args:
        html_path: HTML 파일 경로
        image_path: 출력 이미지 경로
        selector: 캡처할 요소 선택자 (없으면 전체)
        full_page: 전체 페이지 캡처 여부
        width: 뷰포트 너비
        height: 뷰포트 높이

    Returns:
        캡처된 이미지 경로 (실패 시 None)
    """
    # 디렉토리 생성
    image_path.parent.mkdir(parents=True, exist_ok=True)

    # file:// URL로 변환
    file_url = html_path.resolve().as_uri()

    # Playwright 명령어 구성
    cmd = ["npx", "playwright", "screenshot"]

    if selector:
        cmd.extend(["--selector", selector])

    if full_page:
        cmd.append("--full-page")

    cmd.extend([
        "--viewport-size", f"{width},{height}",
        str(file_url),
        str(image_path),
    ])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            logger.info(f"스크린샷 캡처: {image_path}")
            return image_path
        else:
            logger.error(f"Playwright 오류: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("Playwright 타임아웃")
        return None
    except FileNotFoundError:
        logger.error("Playwright가 설치되지 않음. 'npx playwright install' 실행 필요")
        return None
    except Exception as e:
        logger.error(f"스크린샷 캡처 실패: {e}")
        return None


def generate_markdown_embed(
    image_path: Path,
    html_path: Path,
    alt_text: str,
    relative_to: Optional[Path] = None,
) -> str:
    """
    Markdown 문서에 삽입할 코드 생성

    Args:
        image_path: 이미지 경로
        html_path: HTML 파일 경로
        alt_text: 이미지 대체 텍스트
        relative_to: 상대 경로 기준 디렉토리

    Returns:
        Markdown 삽입 코드
    """
    if relative_to:
        try:
            img_rel = image_path.relative_to(relative_to)
            html_rel = html_path.relative_to(relative_to)
        except ValueError:
            img_rel = image_path
            html_rel = html_path
    else:
        img_rel = image_path
        html_rel = html_path

    # POSIX 경로 형식으로 변환
    img_rel_str = str(img_rel).replace("\\", "/")
    html_rel_str = str(html_rel).replace("\\", "/")

    return f"""![{alt_text}]({img_rel_str})
[HTML 원본]({html_rel_str})"""


def get_output_paths(
    name: str,
    prd: Optional[str] = None,
    suffix: str = "",
    mockup_dir: Path = Path("docs/mockups"),
    image_dir: Path = Path("docs/images/mockups"),
) -> tuple[Path, Path]:
    """
    출력 파일 경로 생성

    Args:
        name: 목업 이름
        prd: PRD 번호 (있으면 하위 폴더 사용)
        suffix: 파일명 접미사 (예: "-hifi")
        mockup_dir: 목업 기본 디렉토리
        image_dir: 이미지 기본 디렉토리

    Returns:
        (html_path, image_path) 튜플
    """
    # 파일명 생성 (공백을 하이픈으로)
    safe_name = name.lower().replace(" ", "-").replace("_", "-")

    # 한글 처리 (간단히 유지)
    import re
    safe_name = re.sub(r'[^\w\-]', '', safe_name, flags=re.UNICODE)

    filename = f"{safe_name}{suffix}"

    if prd:
        html_path = mockup_dir / prd / f"{filename}.html"
        image_path = image_dir / prd / f"{filename}.png"
    else:
        html_path = mockup_dir / f"{filename}.html"
        image_path = image_dir / f"{filename}.png"

    return html_path, image_path
