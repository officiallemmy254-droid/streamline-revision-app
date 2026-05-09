import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type LearnerLevel = 'undergraduate' | 'postgraduate' | 'professional';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  token: string | null;
  login: (token: string, username: string) => void;
  logout: () => void;
  geminiApiKey: string;
  setGeminiApiKey: (key: string) => void;
  learnerLevel: LearnerLevel;
  setLearnerLevel: (level: LearnerLevel) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState<string | null>(localStorage.getItem('username'));
  const [geminiApiKey, setGeminiApiKeyState] = useState<string>(
    localStorage.getItem('gemini_api_key') || ''
  );
  const [learnerLevel, setLearnerLevelState] = useState<LearnerLevel>(
    (localStorage.getItem('learner_level') as LearnerLevel) || 'undergraduate'
  );

  const isAuthenticated = !!token;

  const login = (newToken: string, newUsername: string) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('username', newUsername);
    setToken(newToken);
    setUsername(newUsername);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setToken(null);
    setUsername(null);
  };

  const setGeminiApiKey = (key: string) => {
    localStorage.setItem('gemini_api_key', key);
    setGeminiApiKeyState(key);
  };

  const setLearnerLevel = (level: LearnerLevel) => {
    localStorage.setItem('learner_level', level);
    setLearnerLevelState(level);
  };

  useEffect(() => {
    // Sync state if localStorage changes in another tab
    const handleStorage = (e: StorageEvent) => {
      if (e.key === 'token') setToken(e.newValue);
      if (e.key === 'username') setUsername(e.newValue);
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        username,
        token,
        login,
        logout,
        geminiApiKey,
        setGeminiApiKey,
        learnerLevel,
        setLearnerLevel,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
