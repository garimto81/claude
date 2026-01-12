# PRD-0004 Part 8: Supabase Integration

**Part 8 of 9** | [← Migration Guide](./07-migration-guide.md) | [Import Pipeline →](./09-pokergfx-import-pipeline.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

**PRD Number**: PRD-0004
**Version**: 1.3
**Date**: 2026-01-08
**Status**: Draft
**Parent PRD**: PRD-0003, PRD-0001

---

## 8. Supabase Integration

### 8.1 스키마 네임스페이스 구조

프로젝트는 **스키마 분리 전략**을 사용하여 서로 다른 도메인을 명확히 구분합니다.

```
PostgreSQL Database
├── public schema       # Supabase 기본 (auth, storage 등)
│
├── aep schema         # After Effects 프로젝트 분석 (기존)
│   ├── aep_projects
│   ├── compositions
│   ├── layers
│   └── footage_assets
│
└── wsop schema        # WSOP Caption 시스템 (신규)
    ├── Core Reference (7개)
    │   ├── venues, events, tournaments
    │   ├── blind_levels, payouts
    │   └── commentators, schedules
    ├── Player System (4개)
    │   ├── players_master, player_instances
    │   ├── feature_tables, player_stats
    ├── Hand System (6개)
    │   ├── gfx_sessions, hands, hand_players
    │   └── hand_actions, hand_cards, chip_flow
    └── Broadcast System (4개)
        ├── graphics_queue, eliminations
        └── soft_contents, clip_markers, ai_results
```

### 8.2 AEP 스키마와의 공존

| 스키마 | 용도 | 테이블 수 | 접근 방식 |
|--------|------|----------|----------|
| `public` | Supabase 내장 (auth.users 등) | - | 자동 |
| `aep` (미래) | After Effects 프로젝트 분석 | 4 | `/rest/v1/aep_*` |
| `wsop` | WSOP Caption 시스템 | 21 | `/rest/v1/wsop.*` |

> **현재**: AEP 테이블은 `public` 스키마에 유지. 향후 `aep` 스키마로 이동 가능.

### 8.3 Supabase API 접근

#### PostgREST Endpoint

WSOP 스키마 테이블 접근을 위해 `accept-profile` 헤더 사용:

```typescript
// 기본 접근 (public schema)
const { data } = await supabase.from('aep_projects').select('*');

// wsop 스키마 접근 (헤더 설정 필요)
const { data } = await supabase
  .from('wsop.tournaments')  // 또는
  .select('*');

// 또는 RPC 함수 호출
const { data } = await supabase.rpc('wsop.get_or_create_player_master', {
  p_name: 'Phil Ivey',
  p_nationality: 'US'
});
```

#### API Settings 설정 (필수)

Supabase Dashboard > Settings > API에서:
1. **Additional schemas exposed**: `wsop` 추가
2. **Save** 후 API 재시작

### 8.4 RLS (Row Level Security) 정책

#### 기본 정책 구조

```sql
-- wsop 스키마 RLS 활성화
ALTER TABLE wsop.tournaments ENABLE ROW LEVEL SECURITY;

-- 읽기 권한 (모든 인증 사용자)
CREATE POLICY "Allow read for authenticated"
ON wsop.tournaments FOR SELECT
TO authenticated
USING (true);

-- 쓰기 권한 (service_role만)
CREATE POLICY "Allow write for service role"
ON wsop.tournaments FOR ALL
TO service_role
USING (true);
```

#### 권한 매트릭스

| Role | SELECT | INSERT | UPDATE | DELETE |
|------|--------|--------|--------|--------|
| `anon` | ✅ (일부) | ❌ | ❌ | ❌ |
| `authenticated` | ✅ | ⚠️ (제한적) | ⚠️ (제한적) | ❌ |
| `service_role` | ✅ | ✅ | ✅ | ✅ |

### 8.5 Realtime 구독

#### 활성화 테이블

```sql
-- Realtime 구독 활성화
ALTER PUBLICATION supabase_realtime ADD TABLE wsop.graphics_queue;
ALTER PUBLICATION supabase_realtime ADD TABLE wsop.player_instances;
ALTER PUBLICATION supabase_realtime ADD TABLE wsop.hands;
ALTER PUBLICATION supabase_realtime ADD TABLE wsop.eliminations;
```

#### 클라이언트 구독 예시

```typescript
// 그래픽 큐 변경 감지
supabase
  .channel('graphics-updates')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'wsop',
      table: 'graphics_queue',
      filter: 'status=eq.pending'
    },
    (payload) => {
      console.log('New graphic:', payload.new);
      renderGraphic(payload.new);
    }
  )
  .subscribe();

// 플레이어 칩 변동 감지
supabase
  .channel('chip-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'wsop',
      table: 'player_instances'
    },
    (payload) => {
      updateLeaderboard(payload.new);
    }
  )
  .subscribe();
```

### 8.6 Edge Functions (향후)

#### 계획된 Edge Functions

| Function | Trigger | 용도 |
|----------|---------|------|
| `import-gfx-json` | HTTP POST | pokerGFX JSON 파일 임포트 |
| `process-hand-completed` | DB Webhook | 핸드 완료 시 자막 생성 |
| `update-leaderboard` | Cron (5초) | 리더보드 실시간 갱신 |
| `generate-chip-flow` | DB Webhook | 칩 플로우 그래픽 데이터 생성 |

#### Edge Function 예시 구조

```typescript
// supabase/functions/import-gfx-json/index.ts
import { createClient } from '@supabase/supabase-js';

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  const gfxJson = await req.json();

  // GFX 세션 UPSERT
  const { data: session } = await supabase
    .from('wsop.gfx_sessions')
    .upsert({ gfx_id: gfxJson.ID, ... })
    .select()
    .single();

  // 핸드 처리...

  return new Response(JSON.stringify({ success: true }));
});
```

### 8.7 연결 정보

#### 환경 변수

```env
# Supabase Project
SUPABASE_URL=https://ohzdaflycmnbxkpvhxcu.supabase.co
SUPABASE_ANON_KEY=sb_publishable_iQ1PxRTtykgMhzsvWoGFeA_OfSBpeQ4

# Database Direct (Service Role용)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.ohzdaflycmnbxkpvhxcu.supabase.co:5432/postgres

# 스키마 설정
PGRST_DB_SCHEMAS=public,wsop
```

#### 연결 테스트

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

// 연결 테스트
const { data, error } = await supabase
  .from('wsop.venues')
  .select('count')
  .limit(1);

console.log(error ? 'Connection failed' : 'Connection successful');
```

---

**[다음: Part 9 - Import Pipeline →](./09-pokergfx-import-pipeline.md)**
