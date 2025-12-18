/**
 * Login Store
 *
 * LLM 로그인 상태 관리 (Zustand)
 */

import { create } from 'zustand';
import type { LLMLoginStatus, LLMProvider } from '@shared/types';
import { ipc } from '../lib/ipc';

interface LoginState {
  // Login status for each provider
  status: Record<LLMProvider, LLMLoginStatus>;
  isChecking: boolean;

  // Actions
  checkLoginStatus: () => Promise<void>;
  openLoginWindow: (provider: LLMProvider) => Promise<void>;
  updateStatus: (provider: LLMProvider, isLoggedIn: boolean) => void;
}

const defaultStatus: Record<LLMProvider, LLMLoginStatus> = {
  chatgpt: {
    provider: 'chatgpt',
    isLoggedIn: false,
    lastChecked: '',
  },
  claude: {
    provider: 'claude',
    isLoggedIn: false,
    lastChecked: '',
  },
  gemini: {
    provider: 'gemini',
    isLoggedIn: false,
    lastChecked: '',
  },
};

export const useLoginStore = create<LoginState>((set, get) => ({
  status: defaultStatus,
  isChecking: false,

  checkLoginStatus: async () => {
    set({ isChecking: true });

    try {
      const status = await ipc.login.checkStatus();
      set({ status, isChecking: false });
    } catch (error) {
      console.error('Failed to check login status:', error);
      set({ isChecking: false });
    }
  },

  openLoginWindow: async (provider: LLMProvider) => {
    try {
      await ipc.login.openLoginWindow(provider);
    } catch (error) {
      console.error('Failed to open login window:', error);
    }
  },

  updateStatus: (provider: LLMProvider, isLoggedIn: boolean) => {
    set((state) => ({
      status: {
        ...state.status,
        [provider]: {
          ...state.status[provider],
          isLoggedIn,
          lastChecked: new Date().toISOString(),
        },
      },
    }));
  },
}));
