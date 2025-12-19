/**
 * VIP Authentication & Session Management
 *
 * 이 모듈은 GGP Heritage Mall의 VIP 초대 토큰 인증 시스템을 제공합니다.
 *
 * @module lib/auth
 */

// 서버 컴포넌트용 세션 관리
export {
  getVipSession,
  hasVipTier,
  getVipOrderLimit,
  getVipCurrentOrderCount,
  canVipOrder,
  type VipSession,
} from "./vip-session";

// 클라이언트 컴포넌트용 훅은 직접 import 필요
// import { useVipSession, useVipOrderLimit } from "@/hooks/use-vip-session";
