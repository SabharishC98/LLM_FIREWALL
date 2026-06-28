import { AlertTriangle, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full space-y-6 animate-fade-in font-mono">
      <div className="w-24 h-24 border border-firewall-red bg-firewall-red/10 flex items-center justify-center">
        <AlertTriangle className="w-12 h-12 text-firewall-red" />
      </div>
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-light text-luma-FFF font-sans tracking-widest uppercase">
          404 <span className="font-bold text-accent-gold">ERROR</span>
        </h1>
        <h2 className="text-sm font-mono tracking-widest uppercase text-luma-500 mt-1">Page Not Found</h2>
        <p className="text-xs text-luma-500 max-w-md mx-auto uppercase tracking-widest mt-4">
          The page you are looking for does not exist or has been moved.
        </p>
      </div>
      <Link
        to="/"
        className="px-6 py-3 bg-accent-gold text-luma-000 border border-accent-gold text-sm font-bold uppercase tracking-widest flex items-center gap-2 hover:bg-accent-gold/80 transition-colors mt-6"
      >
        <Home className="w-4 h-4" />
        RETURN TO DASHBOARD
      </Link>
    </div>
  );
}
