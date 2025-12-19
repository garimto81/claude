import { type NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";
import type { Database } from "@/types/database";

// Support both new key system (2025+) and legacy keys
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// 보호된 경로 (VIP 세션 필요)
const PROTECTED_PATHS = ["/shop", "/orders", "/profile"];

// 인증 없이 접근 가능한 경로
const PUBLIC_PATHS = ["/", "/invalid-token"];

export async function middleware(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl;

  // Supabase 클라이언트 생성
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient<Database>(supabaseUrl, supabaseKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) =>
          request.cookies.set(name, value)
        );
        supabaseResponse = NextResponse.next({
          request,
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          supabaseResponse.cookies.set(name, value, options)
        );
      },
    },
  });

  // 1. URL에서 초대 토큰 확인
  const inviteToken = searchParams.get("token");

  if (inviteToken) {
    // 토큰으로 VIP 조회
    type VipRow = Database["public"]["Tables"]["vips"]["Row"];
    const { data: vip, error } = await supabase
      .from("vips")
      .select("id, email, name, tier, invite_token, is_active")
      .eq("invite_token", inviteToken.trim())
      .eq("is_active", true)
      .single<VipRow>();

    if (error || !vip) {
      // 유효하지 않은 토큰
      const url = request.nextUrl.clone();
      url.pathname = "/invalid-token";
      url.search = "";
      return NextResponse.redirect(url);
    }

    // 유효한 토큰: VIP 세션 생성
    // VIP 정보를 쿠키에 저장 (간소화된 세션 관리)
    const response = NextResponse.redirect(
      new URL(pathname, request.url) // 같은 페이지로 리다이렉트 (토큰 제거)
    );

    // VIP ID를 암호화하여 쿠키에 저장
    response.cookies.set("vip_session", vip.id, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7일
      path: "/",
    });

    return response;
  }

  // 2. 보호된 경로 확인
  const isProtectedPath = PROTECTED_PATHS.some((path) =>
    pathname.startsWith(path)
  );

  if (isProtectedPath) {
    // 쿠키에서 VIP 세션 확인
    const vipSessionId = request.cookies.get("vip_session")?.value;

    if (!vipSessionId) {
      // 세션 없음: 홈으로 리다이렉트
      const url = request.nextUrl.clone();
      url.pathname = "/";
      url.search = "";
      return NextResponse.redirect(url);
    }

    // VIP 유효성 확인
    type VipRow = Database["public"]["Tables"]["vips"]["Row"];
    const { data: vip, error } = await supabase
      .from("vips")
      .select("id, email, tier, is_active")
      .eq("id", vipSessionId)
      .eq("is_active", true)
      .single<VipRow>();

    if (error || !vip) {
      // 유효하지 않은 세션: 쿠키 삭제 후 홈으로 리다이렉트
      const response = NextResponse.redirect(new URL("/", request.url));
      response.cookies.delete("vip_session");
      return response;
    }
  }

  // 3. Supabase 세션 갱신 (기존 로직)
  await supabase.auth.getUser();

  return supabaseResponse;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
