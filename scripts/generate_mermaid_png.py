# -*- coding: utf-8 -*-
"""Mermaid 다이어그램을 PNG로 변환하는 스크립트"""

import asyncio
import re
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright


async def mermaid_to_png(mermaid_code: str, output_path: Path, width: int = 1200):
    """Mermaid 코드를 PNG로 변환"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: white;
            font-family: Arial, sans-serif;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>
"""

    # 임시 HTML 파일 생성
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html_content)
        html_path = Path(f.name)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.set_viewport_size({"width": width, "height": 800})
            await page.goto(f"file:///{html_path}")

            # Mermaid 렌더링 대기
            await page.wait_for_selector(".mermaid svg", timeout=10000)
            await asyncio.sleep(1)  # 추가 렌더링 대기

            # SVG 요소 크기에 맞춰 스크린샷
            svg_element = await page.query_selector(".mermaid svg")
            if svg_element:
                box = await svg_element.bounding_box()
                if box:
                    # 여백 추가
                    await page.set_viewport_size(
                        {
                            "width": int(box["width"]) + 40,
                            "height": int(box["height"]) + 40,
                        }
                    )

            await page.screenshot(path=str(output_path), full_page=True)
            await browser.close()

        print(f"생성 완료: {output_path}")
        return output_path

    finally:
        html_path.unlink()


async def main():
    # 영문 PRD에서 Mermaid 코드 추출
    prd_path = Path(
        "C:/claude/WSOPTV/tasks/prds/_archive/PRD-0005-wsoptv-ott-rfp-en.md"
    )
    output_dir = Path("C:/claude/WSOPTV/docs/images/PRD-0005/en")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(prd_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Mermaid 코드 블록 추출
    mermaid_pattern = r"```mermaid\n(.*?)```"
    mermaid_blocks = re.findall(mermaid_pattern, content, re.DOTALL)

    # 다이어그램 이름 매핑
    names = ["system-architecture", "data-flow", "responsibility-matrix"]

    print(f"Mermaid 다이어그램 {len(mermaid_blocks)}개 발견")

    for i, (code, name) in enumerate(zip(mermaid_blocks, names)):
        output_path = output_dir / f"{name}.png"
        print(f"\n처리 중: {name}")
        await mermaid_to_png(code, output_path)


if __name__ == "__main__":
    asyncio.run(main())
