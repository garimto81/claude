/**
 * Debate Store
 *
 * 토론 상태 관리 (Zustand)
 */

import { create } from 'zustand';
import type {
  DebateConfig,
  DebateSession,
  DebateElement,
  DebateProgress,
  DebateResponse,
  DebateResult,
  ElementScoreUpdate,
  LLMProvider,
  StreamChunk,
} from '@shared/types';
import { ipc } from '../lib/ipc';

interface DebateState {
  // Current session
  session: DebateSession | null;
  isRunning: boolean;

  // Progress tracking
  currentProgress: DebateProgress | null;
  elements: DebateElement[];
  responses: DebateResponse[];

  // Streaming state (CL-002)
  streamingContent: Map<string, string>; // key: `${iteration}-${provider}`
  currentStreamKey: string | null;

  // Error state
  error: string | null;

  // Actions
  startDebate: (config: DebateConfig) => Promise<void>;
  cancelDebate: () => Promise<void>;
  resetDebate: () => void;

  // IPC event handlers
  initializeIPC: () => void;
  handleProgress: (progress: DebateProgress) => void;
  handleElementScore: (update: ElementScoreUpdate) => void;
  handleResponse: (response: DebateResponse) => void;
  handleStreamChunk: (chunk: StreamChunk) => void;
  handleCycleDetected: (data: { elementId: string; elementName: string }) => void;
  handleComplete: (result: DebateResult) => void;
  handleError: (error: { error: string }) => void;
}

export const useDebateStore = create<DebateState>((set, get) => ({
  // Initial state
  session: null,
  isRunning: false,
  currentProgress: null,
  elements: [],
  responses: [],
  streamingContent: new Map(),
  currentStreamKey: null,
  error: null,

  // Actions
  startDebate: async (config: DebateConfig) => {
    set({ error: null, isRunning: true });

    try {
      await ipc.debate.start(config);
      set({
        session: {
          id: `session-${Date.now()}`,
          config,
          status: 'running',
          currentIteration: 0,
          elements: [],
          createdAt: new Date().toISOString(),
        },
      });
    } catch (error) {
      set({ error: String(error), isRunning: false });
    }
  },

  cancelDebate: async () => {
    const { session } = get();
    if (session) {
      await ipc.debate.cancel(session.id);
      set({
        isRunning: false,
        session: session ? { ...session, status: 'cancelled' } : null,
      });
    }
  },

  resetDebate: () => {
    set({
      session: null,
      isRunning: false,
      currentProgress: null,
      elements: [],
      responses: [],
      streamingContent: new Map(),
      currentStreamKey: null,
      error: null,
    });
  },

  // IPC initialization
  initializeIPC: () => {
    const store = get();

    // Subscribe to IPC events
    ipc.onDebateProgress(store.handleProgress);
    ipc.onElementScore(store.handleElementScore);
    ipc.onDebateResponse(store.handleResponse);
    ipc.onStreamChunk(store.handleStreamChunk);
    ipc.onCycleDetected(store.handleCycleDetected);
    ipc.onDebateComplete(store.handleComplete);
    ipc.onDebateError(store.handleError);
  },

  // Event handlers
  handleProgress: (progress: DebateProgress) => {
    set((state) => ({
      currentProgress: progress,
      session: state.session
        ? { ...state.session, currentIteration: progress.iteration }
        : null,
    }));
  },

  handleElementScore: (update: ElementScoreUpdate) => {
    set((state) => {
      const elements = [...state.elements];
      const index = elements.findIndex((e) => e.id === update.elementId);

      if (index >= 0) {
        elements[index] = {
          ...elements[index],
          currentScore: update.score,
          scoreHistory: [...elements[index].scoreHistory, update.score],
        };
      } else {
        // New element
        elements.push({
          id: update.elementId,
          name: update.elementName,
          status: 'in_progress',
          currentScore: update.score,
          scoreHistory: [update.score],
          versionHistory: [],
        });
      }

      return { elements };
    });
  },

  handleResponse: (response: DebateResponse) => {
    set((state) => ({
      responses: [...state.responses, response],
    }));
  },

  handleStreamChunk: (chunk: StreamChunk) => {
    const streamKey = `${chunk.iteration}-${chunk.provider}`;

    set((state) => {
      const newStreamingContent = new Map(state.streamingContent);

      if (chunk.isComplete) {
        // Streaming complete for this iteration/provider
        newStreamingContent.delete(streamKey);
        return {
          streamingContent: newStreamingContent,
          currentStreamKey: null,
        };
      }

      // Append chunk to existing content
      const existingContent = newStreamingContent.get(streamKey) || '';
      newStreamingContent.set(streamKey, existingContent + chunk.chunk);

      return {
        streamingContent: newStreamingContent,
        currentStreamKey: streamKey,
      };
    });
  },

  handleCycleDetected: (data: { elementId: string; elementName: string }) => {
    set((state) => ({
      elements: state.elements.map((e) =>
        e.id === data.elementId
          ? { ...e, status: 'cycle_detected' as const, completionReason: 'cycle' as const }
          : e
      ),
    }));
  },

  handleComplete: (result: DebateResult) => {
    set((state) => ({
      isRunning: false,
      session: state.session
        ? {
            ...state.session,
            status: 'completed',
            completedAt: result.completedAt,
          }
        : null,
    }));
  },

  handleError: (error: { error: string }) => {
    set({
      error: error.error,
      isRunning: false,
    });
  },
}));
