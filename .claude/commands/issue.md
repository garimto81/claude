# 이슈 등록 (/issue)

GitHub 이슈를 **생성**합니다.

> **역할 구분**:
> - `/issue` - 이슈 **등록** (Create)
> - `/issues` - 이슈 **조회** (Read)
> - `/issue-update` - 이슈 **업데이트** (Update)
> - `/fix-issue` - 이슈 **해결** (구현 → PR)

## Usage

```
/issue [제목]
/issue "로그인 타임아웃 버그"
```

## 입력 정보

다음 정보를 수집하여 이슈 생성:

1. **제목**: 간결한 이슈 제목
2. **유형**: bug | feature | docs | refactor
3. **설명**: 상세 설명 (재현 방법, 기대 동작 등)
4. **라벨**: 자동 추천 (유형 기반)

## 이슈 템플릿

### Bug Report
```markdown
## 버그 설명
[문제 상황]

## 재현 방법
1.
2.
3.

## 기대 동작
[예상되는 정상 동작]

## 실제 동작
[현재 발생하는 문제]

## 환경
- OS:
- Version:
```

### Feature Request
```markdown
## 기능 설명
[구현하고자 하는 기능]

## 배경/동기
[왜 이 기능이 필요한지]

## 제안 구현 방식
[구현 방법 아이디어]

## 대안
[고려한 다른 방법]
```

## 자동 라벨 매핑

| 유형 | 라벨 |
|------|------|
| bug | `bug`, `needs-triage` |
| feature | `enhancement`, `needs-discussion` |
| docs | `documentation` |
| refactor | `refactor`, `tech-debt` |

## 실행 명령

```bash
# 이슈 생성
gh issue create --title "[제목]" --body "[본문]" --label "[라벨]"

# 담당자 할당
gh issue create --title "[제목]" --body "[본문]" --assignee @me

# 마일스톤 지정
gh issue create --title "[제목]" --body "[본문]" --milestone "v1.0"
```

## 생성 후 워크플로우

이슈 생성 후 작업 시작하려면:
```
/fix-issue <생성된-이슈-번호>
```

## 관련 커맨드

| 커맨드 | 역할 |
|--------|------|
| `/issue` | 이슈 등록 (현재) |
| `/issues` | 이슈 목록 조회 |
| `/issue-update` | 실패 분석 및 업데이트 |
| `/fix-issue` | 이슈 해결 워크플로우 |
