import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-screen items-center justify-center bg-luma-000 p-6 font-mono">
          <div className="max-w-md w-full bg-luma-000 border border-firewall-red p-6 text-center space-y-4">
            <AlertTriangle className="w-12 h-12 text-firewall-red mx-auto" />
            <h1 className="text-2xl font-light text-luma-FFF font-sans tracking-widest uppercase">
              SYSTEM <span className="font-bold text-accent-gold">FAULT</span>
            </h1>
            <p className="text-xs text-luma-500 uppercase tracking-widest">
              The application encountered an unexpected error.
            </p>
            {this.state.error && (
              <div className="bg-luma-100 p-4 border border-luma-300 overflow-x-auto text-left mt-4">
                <code className="text-xs text-firewall-red font-mono uppercase tracking-widest">
                  {this.state.error.toString()}
                </code>
              </div>
            )}
            <button
              onClick={() => window.location.reload()}
              className="w-full mt-6 px-6 py-3 border border-luma-300 bg-luma-000 text-luma-700 text-sm font-bold uppercase tracking-widest hover:text-luma-FFF hover:bg-luma-100 transition-colors"
            >
              RELOAD APPLICATION
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
