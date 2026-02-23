# 이미지 분석 규칙 — Tesseract OCR 자동 실행

**트리거**: 사용자가 "이미지 분석", "OCR", "텍스트 추출", "이미지에서 텍스트" 등 이미지 분석을 요청할 때

## 자동 실행 워크플로우

사용자가 이미지 분석을 요청하면 **반드시** 아래 순서로 실행:

### Step 1: 이미지 경로 확인
- 사용자가 이미지 경로를 제공했으면 해당 경로 사용
- 경로가 없으면 사용자에게 질문

### Step 2: Tesseract OCR 정밀 분석 실행
```bash
python -m lib.ocr extract "<이미지_경로>" --lang kor+eng
```

### Step 3: Claude Vision 맥락 분석
```
Read("<이미지_경로>")
```
Read 도구로 이미지를 직접 보고 시각적 맥락을 분석

### Step 4: 결과 통합 제시
OCR 텍스트 추출 결과와 Vision 분석을 결합하여 제시:
- OCR 추출 텍스트 (정밀)
- Vision 시각적 맥락 (의미 해석)
- 신뢰도 정보

## 옵션 처리

| 사용자 요청 | 추가 옵션 |
|------------|----------|
| "표 추출", "테이블" | `--table` 옵션 추가 |
| "문서 스캔" | `--preset document` |
| "스크린샷" | `--preset screenshot` |
| "손글씨" | `--preset handwriting` |
| "영수증", "명함" | `--preset photo` |
| "좌표 추출", "--coords" | `--mode coords` 옵션 추가 |
| "UI 분석", "--ui", "하이브리드" | `--mode ui` 옵션 추가 |
| "hybrid", "전체 분석" | `--mode full` 옵션 추가 |

## Tesseract 미설치 시

```bash
python -m lib.ocr check
```
미설치면 설치 안내 출력 후 Claude Vision만으로 분석 진행 (fallback).

## Hybrid Pipeline 모드 (신규)

| 모드 | 설명 | Vision 호출 |
|------|------|------------|
| `--mode coords` | Layer1(그래픽) + Layer2(텍스트) BBox 좌표만 | 없음 |
| `--mode ui` | coords + Layer3 SoM 시맨틱 분류 | 1회 |
| `--mode full` | ui + 어노테이션 이미지 저장 | 1회 |

## 금지 사항
- Read 도구만으로 이미지 분석하고 끝내기 금지 (OCR 반드시 병행)
- OCR 결과 없이 "분석 완료" 주장 금지
- Tesseract 미설치 시 조용히 스킵 금지 (설치 안내 필수)
