# Supabase Self-Hosted LAN 배포 가이드

**Version**: 1.0.0
**대상**: WAN 없는 LAN 전용 환경

---

## 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAN Network                               │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────────────┐ │
│  │   NAS    │───▶│  Sync Agent  │───▶│  Supabase Self-Hosted  │ │
│  │ (JSON)   │    │  (Docker)    │    │  (LAN Server)          │ │
│  └──────────┘    └──────────────┘    └────────────────────────┘ │
│                                               │                  │
│                                               ▼                  │
│                                      ┌────────────────┐         │
│                                      │   Dashboard    │         │
│                                      │ (Next.js)      │         │
│                                      └────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Supabase Self-Hosted 설치 (LAN 서버)

### 1.1 요구 사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| RAM | 4GB | 8GB+ |
| Storage | 20GB | 50GB+ |
| Docker | v20.10+ | 최신 |
| Docker Compose | v2.0+ | 최신 |
| OS | Ubuntu 20.04+ / Windows Server | Linux 권장 |

### 1.2 설치 절차

```bash
# 1. Supabase 리포지토리 클론
git clone --depth 1 https://github.com/supabase/supabase
cd supabase/docker

# 2. 환경 변수 설정
cp .env.example .env

# 3. 보안 키 생성 (중요!)
# .env 파일에서 다음 값들을 변경:
# - POSTGRES_PASSWORD: 강력한 비밀번호
# - JWT_SECRET: 32자 이상 랜덤 문자열
# - ANON_KEY: JWT로 생성 (https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys)
# - SERVICE_ROLE_KEY: JWT로 생성

# 4. Supabase 시작
docker compose up -d
```

### 1.3 LAN IP 확인

```bash
# Linux
ip addr show | grep inet

# Windows
ipconfig
```

예: `192.168.1.100`

### 1.4 Supabase 접속 확인

| 서비스 | URL | 용도 |
|--------|-----|------|
| Studio (Dashboard) | `http://192.168.1.100:3000` | 관리 UI |
| API | `http://192.168.1.100:8000` | REST API |
| PostgreSQL | `192.168.1.100:5432` | DB 직접 연결 |

---

## 2. gfx_json Sync Agent 설정 변경

### 2.1 환경 변수 변경점

| 변수 | Cloud (기존) | LAN (변경) |
|------|-------------|-----------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | `http://192.168.1.100:8000` |
| `SUPABASE_SECRET_KEY` | Cloud Service Key | Self-Hosted SERVICE_ROLE_KEY |

### 2.2 .env 파일 예시

```env
# === LAN Supabase Self-Hosted ===
SUPABASE_URL=http://192.168.1.100:8000
SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # SERVICE_ROLE_KEY

# === NAS 설정 (변경 없음) ===
NAS_MOUNT_PATH=/volume1/pokergfx
POLL_INTERVAL=2.0
BATCH_SIZE=500
FLUSH_INTERVAL=5.0
LOG_LEVEL=INFO
```

### 2.3 코드 변경 불필요

기존 `src/sync_agent/` 코드는 **변경 없이 그대로 사용**:
- `supabase_client.py`: httpx 기반 REST 호출 → URL만 변경되면 동작
- `settings.py`: 환경 변수로 URL 주입

---

## 3. LAN 전용 Docker Compose

### 3.1 docker-compose.lan.yml

```yaml
# GFX Sync Agent - LAN 전용 구성
version: "3.8"

services:
  sync-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: gfx-sync-agent
    restart: unless-stopped
    # LAN 환경: 외부 DNS 불필요
    dns:
      - 192.168.1.1  # LAN 라우터/DNS
    volumes:
      - ${NAS_MOUNT_PATH}:/app/data:ro
      - sync_queue:/app/queue
    environment:
      # LAN Supabase Self-Hosted
      GFX_SYNC_SUPABASE_URL: ${SUPABASE_URL}
      GFX_SYNC_SUPABASE_SECRET_KEY: ${SUPABASE_SECRET_KEY}
      # NAS 경로
      GFX_SYNC_NAS_BASE_PATH: /app/data
      # 폴링/배치 설정
      GFX_SYNC_POLL_INTERVAL: ${POLL_INTERVAL:-2.0}
      GFX_SYNC_BATCH_SIZE: ${BATCH_SIZE:-500}
      GFX_SYNC_FLUSH_INTERVAL: ${FLUSH_INTERVAL:-5.0}
      # 헬스체크
      GFX_SYNC_HEALTH_PORT: "8080"
      GFX_SYNC_HEALTH_ENABLED: "true"
      GFX_SYNC_LOG_LEVEL: ${LOG_LEVEL:-INFO}
    ports:
      - "8081:8080"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    # LAN 네트워크 (Supabase와 동일 네트워크)
    networks:
      - lan_network

networks:
  lan_network:
    driver: bridge

volumes:
  sync_queue:
    name: gfx-sync-queue
```

### 3.2 실행

```bash
# LAN 구성으로 실행
docker compose -f docker-compose.lan.yml up -d
```

---

## 4. 데이터베이스 마이그레이션

### 4.1 Supabase Studio에서 테이블 생성

`http://192.168.1.100:3000` 접속 후 SQL Editor에서:

```sql
-- gfx_sessions 테이블 생성
CREATE TABLE IF NOT EXISTS gfx_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_hash TEXT UNIQUE NOT NULL,
    pc_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    session_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_pc_id ON gfx_sessions(pc_id);
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_created_at ON gfx_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_file_hash ON gfx_sessions(file_hash);

-- RLS 비활성화 (LAN 내부 전용이므로)
ALTER TABLE gfx_sessions DISABLE ROW LEVEL SECURITY;
```

### 4.2 기존 Cloud 데이터 마이그레이션 (선택)

```bash
# Cloud에서 데이터 내보내기
pg_dump "postgres://postgres:xxx@db.xxx.supabase.co:5432/postgres" \
  -t gfx_sessions --data-only > gfx_data.sql

# LAN Supabase로 가져오기
psql "postgres://postgres:your_password@192.168.1.100:5432/postgres" \
  < gfx_data.sql
```

---

## 5. Dashboard 설정 (선택)

### 5.1 환경 변수 변경

```env
# dashboard/.env.local
NEXT_PUBLIC_SUPABASE_URL=http://192.168.1.100:8000
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5.2 Dashboard 빌드 및 실행

```bash
cd dashboard
npm install
npm run build
npm run start
```

---

## 6. 검증 체크리스트

```markdown
- [ ] Supabase Studio 접속 확인 (http://LAN_IP:3000)
- [ ] API 엔드포인트 응답 확인 (http://LAN_IP:8000/rest/v1/)
- [ ] Sync Agent 헬스체크 (http://NAS_IP:8081/health)
- [ ] 테스트 JSON 파일 동기화 확인
- [ ] Dashboard 데이터 표시 확인
```

---

## 7. 트러블슈팅

### 7.1 연결 오류

```
Error: Connection refused to 192.168.1.100:8000
```

**해결**:
1. Supabase 컨테이너 상태 확인: `docker compose ps`
2. 방화벽 포트 열기: 3000, 5432, 8000

### 7.2 인증 오류

```
Error: Invalid API key
```

**해결**:
1. `.env`의 SERVICE_ROLE_KEY 확인
2. Supabase `.env`의 JWT_SECRET과 일치하는지 확인

### 7.3 DNS 해석 실패

```
Error: Name resolution failed for supabase
```

**해결**:
- IP 주소 직접 사용 (호스트네임 대신)
- `dns` 설정에 LAN DNS 서버 지정

---

## 8. 보안 고려사항

| 항목 | Cloud | LAN Self-Hosted |
|------|-------|-----------------|
| TLS/HTTPS | 자동 | 수동 설정 필요 (nginx 등) |
| API Key 관리 | Supabase Dashboard | 수동 관리 |
| 백업 | 자동 | 수동 스케줄링 필요 |
| 업데이트 | 자동 | 수동 (`docker compose pull`) |

### 8.1 HTTPS 설정 (권장)

```bash
# nginx reverse proxy with Let's Encrypt (LAN 내부 CA 사용)
# 또는 self-signed 인증서 사용
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-20 | 최초 작성 |
