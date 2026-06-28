import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../utils/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('fw_jwt');
    if (token) {
      api.getMe()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('fw_jwt');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('fw_jwt', data.access_token);
    setUser(data.user);
    return data;
  };

  const signup = async (email, password) => {
    await api.signup(email, password);
    return login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('fw_jwt');
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
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
