# Vercel 배포 가이드

이 문서는 NextAuth.js + Supabase SSO 애플리케이션을 Vercel에 배포하는 방법을 안내합니다.

## 사전 준비사항

- [x] Vercel 계정 (https://vercel.com)
- [x] GitHub 저장소에 코드 푸시 완료
- [x] Supabase 프로젝트 설정 완료

---

## 1. Vercel 프로젝트 생성

### 방법 A: Vercel Dashboard (웹)

1. https://vercel.com/dashboard 접속
2. "Add New" → "Project" 클릭
3. GitHub 저장소 연결
4. `sso-nextjs` 프로젝트 선택
5. "Import" 클릭

### 방법 B: Vercel CLI (터미널)

```bash
# Vercel CLI 설치 (처음 한 번만)
npm i -g vercel

# 프로젝트 배포
cd D:\AI\claude01\sso-nextjs
vercel

# 프로덕션 배포
vercel --prod
```

---

## 2. 환경 변수 설정

Vercel Dashboard → 프로젝트 → Settings → Environment Variables에서 다음 변수들을 추가합니다:

### Supabase 설정

```bash
NEXT_PUBLIC_SUPABASE_URL=https://dqkghhlnnskjfwntdtor.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxa2doaGxubnNramZ3bnRkdG9yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwMTI1NTcsImV4cCI6MjA3ODM3MjU1N30.0mSyA3pWnDx8XANJ4s6AKJB-TpCpZIFz6AM-J0bk_j4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxa2doaGxubnNramZ3bnRkdG9yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzAxMjU1NywiZXhwIjoyMDc4MzcyNTU3fQ.iVJUs3vDAw1Dh_ImcKQJnJT7Dyuj2PvwxtkevNBzUGk
```

### NextAuth.js 설정

```bash
# 중요: 프로덕션용 새 AUTH_SECRET 생성 필요!
# 생성 명령어: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

AUTH_SECRET=<새로_생성한_32자_이상_랜덤_문자열>

# AUTH_URL은 Vercel이 자동으로 설정하므로 생략 가능
# 수동 설정 시: https://your-project.vercel.app
AUTH_URL=https://your-project.vercel.app
```

### DATABASE_URL (선택사항)

마이그레이션 스크립트를 Vercel에서 실행하려면 추가:

```bash
DATABASE_URL=postgresql://postgres:skdltm16145%21%40@db.dqkghhlnnskjfwntdtor.supabase.co:5432/postgres?sslmode=require
```

⚠️ **주의**: 실제 프로덕션 환경에서는 비밀번호를 더 강력한 것으로 변경하세요!

---

## 3. 환경 변수 적용 범위

각 환경 변수에 대해 적용할 환경을 선택합니다:

- ✅ **Production** - 프로덕션 배포 (vercel --prod)
- ✅ **Preview** - PR 미리보기
- ✅ **Development** - 로컬 개발 (vercel dev)

일반적으로 모두 선택하되, `AUTH_SECRET`은 환경마다 다르게 설정하는 것이 좋습니다.

---

## 4. 배포 실행

### 자동 배포 (권장)

GitHub에 푸시하면 자동으로 배포됩니다:

```bash
git push origin feature/issue-16-agent-evolution
```

Vercel Dashboard에서 배포 진행 상황을 확인할 수 있습니다.

### 수동 배포

```bash
cd D:\AI\claude01\sso-nextjs
vercel --prod
```

---

## 5. 배포 후 확인사항

### ✅ 체크리스트

1. **로그인 페이지 접속**
   - URL: `https://your-project.vercel.app/login`
   - 정상적으로 로딩되는지 확인

2. **로그인 테스트**
   - test@test.com / qwer1234 (또는 설정한 계정)
   - 로그인 성공 후 홈페이지로 리다이렉트 확인

3. **Admin 페이지 접근**
   - URL: `https://your-project.vercel.app/admin`
   - Admin 사용자로 접근 가능한지 확인

4. **일반 사용자 테스트**
   - 일반 user 계정으로 로그인
   - `/admin` 접근 시 `/forbidden`으로 리다이렉트 확인

5. **로그아웃 테스트**
   - 로그아웃 후 `/login`으로 리다이렉트 확인

---

## 6. 도메인 설정 (선택사항)

### 커스텀 도메인 연결

1. Vercel Dashboard → 프로젝트 → Settings → Domains
2. "Add Domain" 클릭
3. 도메인 입력 (예: auth.yourdomain.com)
4. DNS 레코드 추가 안내에 따라 설정

### AUTH_URL 업데이트

커스텀 도메인 설정 후:

```bash
AUTH_URL=https://auth.yourdomain.com
```

---

## 7. 문제 해결

### 로그인 실패 시

**증상**: "이메일 또는 비밀번호가 올바르지 않습니다"

**해결책**:
1. Vercel Dashboard → Logs에서 에러 확인
2. 환경 변수가 올바르게 설정되었는지 확인
3. `SUPABASE_SERVICE_ROLE_KEY`가 정확한지 확인
4. Supabase RLS 정책 확인 (무한 재귀 이슈)

### CSRF 토큰 에러

**증상**: "CSRF token mismatch"

**해결책**:
1. `AUTH_SECRET`이 설정되었는지 확인
2. `AUTH_URL`이 실제 배포 URL과 일치하는지 확인
3. 브라우저 쿠키 설정 확인 (SameSite, Secure)

### 빌드 실패

**증상**: Vercel 빌드가 실패함

**해결책**:
1. 로컬에서 `npm run build` 테스트
2. TypeScript 에러 확인
3. ESLint 에러 확인
4. Vercel 로그에서 상세 에러 확인

---

## 8. 보안 체크리스트

배포 전 확인:

- [ ] `AUTH_SECRET` 프로덕션용 새로 생성
- [ ] `.env.local` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] Supabase Service Role Key가 환경 변수로만 관리되는지 확인
- [ ] 데이터베이스 비밀번호 강도 확인
- [ ] RLS 정책이 올바르게 설정되었는지 확인
- [ ] HTTPS 강제 적용 확인 (Vercel 기본값)

---

## 9. 모니터링

### Vercel Analytics

1. Vercel Dashboard → 프로젝트 → Analytics
2. 페이지 로드 시간, 방문자 수 확인

### Sentry (선택사항)

프로덕션 에러 추적을 위해 Sentry 통합:

```bash
npm install --save @sentry/nextjs
npx @sentry/wizard@latest -i nextjs
```

---

## 참고 자료

- [Vercel 공식 문서](https://vercel.com/docs)
- [NextAuth.js Deployment](https://next-auth.js.org/deployment)
- [Supabase Production Checklist](https://supabase.com/docs/guides/platform/going-into-prod)

---

## 배포 완료 후

배포 URL을 README.md에 추가하고 커밋:

```bash
echo "Deployed at: https://your-project.vercel.app" >> README.md
git add README.md
git commit -m "docs: Add deployment URL"
git push
```

축하합니다! 🎉 배포가 완료되었습니다.
