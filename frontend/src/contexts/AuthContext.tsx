import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { post, get } from "../services/api";

export interface UserOut {
  id: number;
  email: string;
}

interface AuthContextType {
  user: UserOut | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
      get<UserOut>("/auth/me")
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("access_token");
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const loginFn = useCallback(async (email: string, password: string) => {
    const data = await post<{ access_token: string; token_type: string }>("/auth/login", { email, password });
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
    const u = await get<UserOut>("/auth/me");
    setUser(u);
  }, []);

  const registerFn = useCallback(async (email: string, password: string) => {
    await post<UserOut>("/auth/register", { email, password });
    const data = await post<{ access_token: string; token_type: string }>("/auth/login", { email, password });
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
    const u = await get<UserOut>("/auth/me");
    setUser(u);
  }, []);

  const logoutFn = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }, []);

  const isAuthenticated = user !== null && token !== null;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated,
        login: loginFn,
        register: registerFn,
        logout: logoutFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
