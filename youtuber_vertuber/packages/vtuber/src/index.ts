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

// Phase 3 #107: Avatar Controller & Reaction Mapper
export { AvatarController, avatarController } from './avatar-controller.js';
export type { Expression, ExpressionTask, Priority } from './avatar-controller.js';

export { ReactionMapper } from './reaction-mapper.js';
export type { ExpressionMapping } from './reaction-mapper.js';
