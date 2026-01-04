/**
 * @youtuber/vtuber
 *
 * VMC Protocol 클라이언트 및 아바타 컨트롤러
 */

export const VERSION = '0.1.0';

// Phase 1 #77: VMC Protocol 클라이언트
export { VMCClient } from './vmc-client';
export type {
  BlendShapeData,
  VMCStatus,
  VMCClientOptions,
  BlendShapeUpdateCallback,
  ConnectionStatusCallback,
  ExpressionType,
} from './types';
export { VMC_BLENDSHAPE_NAMES } from './types';

// Avatar Controller는 Phase 3 #107에서 구현 예정
// Reaction Mapper는 Phase 3 #107에서 구현 예정
