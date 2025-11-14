import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import type { User } from "next-auth"
import { createClient } from '@supabase/supabase-js'
import { env } from "@/lib/env"

// Extended User type with role
interface ExtendedUser extends User {
  role?: string
}

// Supabase Admin Client (for auth operations)
function getSupabaseAdmin() {
  return createClient(
    env.NEXT_PUBLIC_SUPABASE_URL,
    env.SUPABASE_SERVICE_ROLE_KEY,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    }
  )
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: "Credentials",
      credentials: {
        email: {
          label: "이메일",
          type: "email",
          placeholder: "user@example.com"
        },
        password: {
          label: "비밀번호",
          type: "password"
        },
      },
      async authorize(credentials): Promise<ExtendedUser | null> {
        try {
          // 1. 입력 검증
          if (!credentials?.email || !credentials?.password) {
            return null
          }

          const email = credentials.email as string
          const password = credentials.password as string

          // 2. Supabase Auth로 로그인
          const supabase = getSupabaseAdmin()

          const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
            email,
            password,
          })

          if (authError || !authData.user) {
            console.error('[Auth] Login failed:', authError?.message)
            return null
          }

          // 3. profiles 테이블에서 role 가져오기
          const { data: profile, error: profileError } = await supabase
            .from('profiles')
            .select('role, display_name')
            .eq('id', authData.user.id)
            .single()

          if (profileError || !profile) {
            console.error('[Auth] Failed to fetch profile:', profileError?.message)
            return null
          }

          // 4. User 객체 반환
          return {
            id: authData.user.id,
            email: authData.user.email!,
            name: profile.display_name || authData.user.email!,
            role: profile.role,
          }

        } catch (error) {
          console.error('[Auth] Unexpected error:', error)
          return null
        }
      },
    }),
  ],

  callbacks: {
    // JWT 콜백: 토큰에 사용자 정보 추가
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = (user as ExtendedUser).role || "user"
      }
      return token
    },

    // Session 콜백: 클라이언트에 노출할 세션 데이터
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    },
  },

  pages: {
    signIn: "/login",
  },

  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours
  },

  // Development 환경에서 디버그 활성화
  debug: process.env.NODE_ENV === "development",
})
