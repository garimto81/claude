# Supabase CLI 스키마 확인 가이드

**Version**: 1.0.0 | **Last Updated**: 2026-01-16

이 문서는 Supabase 관련 코드 작성 시 **반드시 CLI로 실제 DB 스키마를 확인**하도록 하는 전역 지침입니다.

---

## 왜 CLI 확인이 필수인가?

### 문제 상황

| 잘못된 방식 | 문제점 | 결과 |
|------------|--------|------|
| TypeScript 타입만 확인 | 타입이 outdated일 수 있음 | 런타임 에러 |
| 마이그레이션 파일만 확인 | 원격에 미적용 상태일 수 있음 | 배포 실패 |
| 테이블 존재 가정 | 개발/운영 환경 차이 | 500 에러 |
| 컬럼명 추측 | snake_case vs camelCase 혼동 | 쿼리 실패 |

### 올바른 방식

```
요청 → CLI로 실제 스키마 확인 → 타입과 비교 → 코드 작성
```

---

## Supabase CLI 핵심 명령어

### 1. 연결 상태 확인

```powershell
# 프로젝트 디렉토리에서 실행
supabase status
```

**출력 예시:**
```
         API URL: https://xxx.supabase.co
     GraphQL URL: https://xxx.supabase.co/graphql/v1
          DB URL: postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres
      Studio URL: https://supabase.com/dashboard/project/xxx
    Inbucket URL: http://127.0.0.1:54324
      JWT secret: xxx
        anon key: xxx
service_role key: xxx
```

### 2. 전체 스키마 덤프 (가장 중요)

```powershell
# 전체 public 스키마
supabase db dump --schema public

# 특정 테이블만
supabase db dump --schema public -t users
supabase db dump --schema public -t users,posts,comments
```

**출력 예시:**
```sql
CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
);
```

### 3. 테이블 목록 및 크기

```powershell
supabase inspect db table-sizes
```

**출력 예시:**
```
 schema |    name    | size
--------+------------+--------
 public | users      | 16 kB
 public | posts      | 8192 bytes
 public | comments   | 8192 bytes
```

### 4. RLS 정책 확인

```powershell
supabase inspect db policies
```

**출력 예시:**
```
 table_name | name                | action | roles
------------+---------------------+--------+---------------
 users      | Users can view own  | SELECT | authenticated
 users      | Users can update    | UPDATE | authenticated
 posts      | Anyone can read     | SELECT | public
```

### 5. 인덱스 확인

```powershell
supabase inspect db index-sizes
```

### 6. 로컬 vs 원격 차이

```powershell
# 마이그레이션 적용 여부 확인
supabase db diff

# 특정 마이그레이션 상태
supabase migration list
```

---

## 작업 시나리오별 체크리스트

### 시나리오 1: 새 테이블 조회 코드 작성

```markdown
- [ ] `supabase db dump --schema public -t [테이블명]` 실행
- [ ] 컬럼명 정확히 확인 (snake_case 주의)
- [ ] nullable 여부 확인
- [ ] 기본값 확인
- [ ] TypeScript 타입과 일치 여부 확인
```

**예시:**
```powershell
# users 테이블 구조 확인
supabase db dump --schema public -t users
```

```typescript
// 확인된 스키마 기반 코드 작성
const { data, error } = await supabase
  .from('users')
  .select('id, email, created_at, metadata')  // 실제 컬럼명 사용
  .eq('id', userId);
```

### 시나리오 2: 새 테이블 생성

```markdown
- [ ] `supabase inspect db table-sizes` 로 동일 이름 존재 여부 확인
- [ ] 참조할 테이블 존재 여부 확인
- [ ] `supabase migration new [name]` 으로 마이그레이션 생성
- [ ] `supabase db push` 전 `supabase db diff` 로 변경 사항 확인
```

**예시:**
```powershell
# 기존 테이블 확인
supabase inspect db table-sizes

# 마이그레이션 생성
supabase migration new create_comments_table

# 적용 전 검토
supabase db diff
```

### 시나리오 3: RLS 정책 추가

```markdown
- [ ] `supabase inspect db policies` 로 기존 정책 확인
- [ ] 정책 이름 충돌 여부 확인
- [ ] 테이블에 RLS 활성화 여부 확인
```

### 시나리오 4: 컬럼 추가/수정

```markdown
- [ ] `supabase db dump --schema public -t [테이블명]` 으로 현재 구조 확인
- [ ] 기존 데이터 영향도 분석
- [ ] NOT NULL 추가 시 기본값 설정 필요 여부 확인
- [ ] 마이그레이션 작성 후 `supabase db diff` 검토
```

---

## 자주 발생하는 실수와 해결

### 실수 1: 컬럼명 오타

**문제:**
```typescript
// TypeScript 타입: createdAt (camelCase)
// 실제 DB: created_at (snake_case)
.select('id, createdAt')  // ❌ 에러
```

**해결:**
```powershell
supabase db dump --schema public -t users
# 출력: created_at timestamp with time zone
```

```typescript
.select('id, created_at')  // ✅ 정확한 컬럼명
```

### 실수 2: nullable 미확인

**문제:**
```typescript
// DB에서 nullable인데 필수로 가정
const userName: string = data.name;  // ❌ null일 수 있음
```

**해결:**
```powershell
supabase db dump --schema public -t users
# 출력: name text  (NOT NULL 없음 = nullable)
```

```typescript
const userName: string | null = data.name;  // ✅
```

### 실수 3: 존재하지 않는 테이블

**문제:**
```typescript
// 마이그레이션은 있지만 원격에 미적용
await supabase.from('new_feature_table').select('*');  // ❌ 테이블 없음
```

**해결:**
```powershell
supabase inspect db table-sizes
# new_feature_table 이 목록에 없음 → 적용 필요

supabase db push  # 마이그레이션 적용
```

---

## 환경별 설정

### 로컬 개발 환경

```powershell
# supabase/config.toml 에서 로컬 DB 설정 확인
supabase start
supabase status  # 로컬 URL 확인
```

### 원격 환경 (Production)

```powershell
# 프로젝트 연결
supabase link --project-ref [project-id]

# 원격 스키마 확인
supabase db dump --schema public --linked
```

---

## TypeScript 타입 자동 생성

스키마 확인 후 타입을 자동 생성하여 동기화:

```powershell
# 타입 생성
supabase gen types typescript --linked > types/supabase.ts

# 또는 로컬 DB 기준
supabase gen types typescript --local > types/supabase.ts
```

**생성된 타입 예시:**
```typescript
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string;
          created_at: string;
          metadata: Json | null;
        };
        Insert: { ... };
        Update: { ... };
      };
    };
  };
}
```

---

## Quick Reference

| 상황 | 명령어 |
|------|--------|
| 전체 스키마 확인 | `supabase db dump --schema public` |
| 특정 테이블 확인 | `supabase db dump --schema public -t [table]` |
| 테이블 목록 | `supabase inspect db table-sizes` |
| RLS 정책 | `supabase inspect db policies` |
| 인덱스 목록 | `supabase inspect db index-sizes` |
| 마이그레이션 차이 | `supabase db diff` |
| 타입 생성 | `supabase gen types typescript --linked` |
| 연결 상태 | `supabase status` |

---

## 관련 문서

- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [Database Migrations](https://supabase.com/docs/guides/cli/local-development#database-migrations)
- [Type Generation](https://supabase.com/docs/guides/api/rest/generating-types)
