import { useEffect } from 'react';
import { useDebateStore } from './stores/debate-store';
import { useLoginStore } from './stores/login-store';
import { MainLayout } from './layouts/MainLayout';

function App() {
  const { initializeIPC } = useDebateStore();
  const { checkLoginStatus } = useLoginStore();

  useEffect(() => {
    // Initialize IPC listeners
    initializeIPC();
    // Check initial login status
    checkLoginStatus();
  }, [initializeIPC, checkLoginStatus]);

  return <MainLayout />;
}

export default App;
