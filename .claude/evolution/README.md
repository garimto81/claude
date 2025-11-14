# Agent Evolution System

Agent 사용 추적 및 피드백 기반 자동 개선 시스템

## 🚀 빠른 시작

```bash
# 1. Langfuse 시작
cd .claude/evolution
cp .env.example .env
vim .env  # 시크릿 및 admin 계정 설정
docker-compose up -d

# 2. 대시보드 접속
# http://localhost:3000
# API 키 발급: Settings → API Keys

# 3. Python 클라이언트 설치
pip install -r requirements.txt

# 4. Agent 추적 시작
python scripts/track_agent_usage.py  # 테스트 실행
```

## 📁 구조

```
.claude/evolution/
├── docker-compose.yml          # Langfuse self-hosted 설정
├── .env.example                # 환경 변수 템플릿
├── requirements.txt            # Python 의존성
├── README.md                   # 이 파일
│
├── scripts/
│   ├── track_agent_usage.py   # 메인 추적 시스템
│   └── collect_feedback.py    # 피드백 수집 CLI
│
├── config/                     # 설정 파일 (향후)
├── feedback/                   # 피드백 데이터 (로컬 백업)
└── data/                       # 분석 결과 (향후)
```

## 📖 사용법

### Python 코드 통합

```python
from .claude.evolution.scripts.track_agent_usage import get_tracker

tracker = get_tracker()

# Agent 실행 추적
with tracker.track("context7-engineer", phase="Phase 0", task="Verify docs"):
    result = agent.run()

# 피드백 수집
tracker.collect_feedback(
    agent="context7-engineer",
    rating=5,
    comment="Docs verified",
    effectiveness=0.9
)

tracker.flush()
```

### CLI 피드백 수집

```bash
# 대화형 모드
python scripts/collect_feedback.py context7-engineer --interactive

# 빠른 평점
python scripts/collect_feedback.py playwright-engineer --rating 5

# 완전한 피드백
python scripts/collect_feedback.py debugger \
    --rating 4 \
    --comment "Fixed bug correctly" \
    --effectiveness 8 \
    --suggestion "Add retry logic"
```

## 📊 대시보드

http://localhost:3000

- **Traces**: Agent 실행 로그
- **Scores**: 평점 및 피드백
- **Analytics**: 성능 분석

## 🔧 환경 변수

`.env` 파일 필수 항목:

```bash
# Auth Secrets (openssl rand -base64 32)
NEXTAUTH_SECRET=your-secret-here
SALT=your-salt-here

# Admin User
LANGFUSE_ADMIN_EMAIL=admin@localhost
LANGFUSE_ADMIN_PASSWORD=changeme

# API Keys (대시보드에서 발급)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

## 📚 문서

완전한 가이드: `../../docs/AGENT_EVOLUTION_GUIDE.md`

## 🐛 문제 해결

### Langfuse 연결 오류
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f langfuse-server

# 재시작
docker-compose restart
```

### API 키 오류
```bash
# .env 확인
cat .env | grep LANGFUSE_

# 대시보드에서 키 재발급
# Settings → API Keys → Create new
```

## 🔗 참고 링크

- **Langfuse 문서**: https://langfuse.com/docs
- **GitHub 이슈**: [#16](https://github.com/garimto81/claude-code-config/issues/16)
- **전체 가이드**: `docs/AGENT_EVOLUTION_GUIDE.md`

---

**Status**: Phase 1 (추적 시스템)
**Next**: Phase 2 (PromptAgent 자동 개선)
