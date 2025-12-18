/**
 * IPC Handlers
 *
 * Main ↔ Renderer 통신 핸들러
 */

import { ipcMain, BrowserWindow } from 'electron';
import type {
  DebateConfig,
  DebateProgress,
  DebateResponse,
  DebateResult,
  ElementScoreUpdate,
  LLMLoginStatus,
  LLMProvider,
} from '../../shared/types';
import { BrowserViewManager } from '../browser/browser-view-manager';
import { DebateController } from '../debate/debate-controller';
import { CycleDetector } from '../debate/cycle-detector';

let browserManager: BrowserViewManager | null = null;
let debateController: DebateController | null = null;

// Mock repository for now (will be replaced with actual DB)
const mockRepository = {
  create: async (data: unknown) => `debate-${Date.now()}`,
  createElements: async () => {},
  updateElementScore: async () => {},
  markElementComplete: async () => {},
  getLast3Versions: async () => [],
  getIncompleteElements: async () => [],
  updateIteration: async () => {},
  updateStatus: async () => {},
};

export function registerIpcHandlers(mainWindow: BrowserWindow) {
  // Initialize browser manager
  browserManager = new BrowserViewManager(mainWindow as unknown as {
    setBrowserView: (view: unknown) => void;
    getBounds: () => { x: number; y: number; width: number; height: number };
  });

  // Create event emitter that forwards to renderer
  const eventEmitter = {
    emit: (event: string, data: unknown) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send(event, data);
      }
    },
    on: () => {},
  };

  // Initialize cycle detector and debate controller
  const cycleDetector = new CycleDetector(browserManager);
  debateController = new DebateController(
    browserManager,
    mockRepository,
    cycleDetector,
    eventEmitter
  );

  // === Debate Handlers ===

  ipcMain.handle('debate:start', async (_event, config: DebateConfig) => {
    if (!debateController) {
      throw new Error('Debate controller not initialized');
    }

    // Create browser views for participants
    const providers: LLMProvider[] = [...config.participants, config.judgeProvider];
    for (const provider of new Set(providers)) {
      if (!browserManager?.getView(provider)) {
        browserManager?.createView(provider);
      }
    }

    // Start debate (runs in background)
    debateController.start(config).catch((error) => {
      eventEmitter.emit('debate:error', { error: String(error) });
    });

    return { success: true };
  });

  ipcMain.handle('debate:cancel', async (_event, sessionId: string) => {
    debateController?.cancel();
    return { success: true };
  });

  ipcMain.handle('debate:get-status', async () => {
    // Return current debate status
    return { status: 'idle' };
  });

  // === Login Handlers ===

  ipcMain.handle('login:check-status', async () => {
    if (!browserManager) {
      return {};
    }
    return browserManager.checkLoginStatus();
  });

  ipcMain.handle('login:open-window', async (_event, provider: LLMProvider) => {
    if (!browserManager) {
      throw new Error('Browser manager not initialized');
    }

    // Create view if not exists
    if (!browserManager.getView(provider)) {
      browserManager.createView(provider);
    }

    // Show the view for login
    const bounds = mainWindow.getBounds();
    browserManager.showView(provider, {
      x: 0,
      y: 50, // Leave space for header
      width: bounds.width,
      height: bounds.height - 50,
    });

    return { success: true };
  });
}

// Cleanup on app quit
export function cleanupIpcHandlers() {
  browserManager?.destroyAllViews();
  browserManager = null;
  debateController = null;
}
