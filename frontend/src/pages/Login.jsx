import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.detail || 'Failed to login. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden scanline">
      {/* Background Decor */}
      <div className="absolute top-10 left-10 structural-text">01</div>
      
      <div className="glass p-10 w-full max-w-md relative z-10 flex flex-col gap-8">
        <div className="flex flex-col items-center gap-4 mb-2">
          <img src="/logo.png" alt="Lurien Matrix Logo" className="w-24 h-24 object-contain opacity-90" />
          <h1 className="text-2xl font-light tracking-widest text-white uppercase mt-2">Lurien Matrix</h1>
        </div>

        {error && (
          <div className="p-3 border border-red-900 bg-red-950/20 text-red-400 text-sm font-mono">
            [ERROR] {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-widest text-[#666666]">Identity (Email)</label>
            <input
              type="email"
              required
              className="bg-[#0A0A0A] border border-[#333333] p-3 text-white focus:outline-none focus:border-[#AAAAAA] transition-colors rounded-none"
              placeholder="operator@system.local"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-xs uppercase tracking-widest text-[#666666]">Passcode</label>
            <input
              type="password"
              required
              className="bg-[#0A0A0A] border border-[#333333] p-3 text-white focus:outline-none focus:border-[#AAAAAA] transition-colors rounded-none font-mono tracking-widest"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-4 inverted-chip w-full py-4 flex items-center justify-center gap-2 hover:bg-[#CCCCCC] transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'INITIALIZE SESSION'}
          </button>
        </form>

        <div className="text-center mt-4">
          <p className="text-[#666666] text-xs">
            NO CLEARANCE? <Link to="/signup" className="text-white border-b border-[#333333] hover:border-white transition-colors pb-1 ml-2">REQUEST ACCESS</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
