import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Electron IPC
vi.mock('../lib/ipc', () => ({
  ipc: {
    send: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    invoke: vi.fn(),
  },
}));

// Mock window.electronAPI
Object.defineProperty(window, 'electronAPI', {
  value: {
    send: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    invoke: vi.fn(),
  },
  writable: true,
});
