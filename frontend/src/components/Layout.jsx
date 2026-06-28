import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-luma-000 relative">
      {/* Structural Watermark */}
      <div className="absolute top-0 left-64 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="structural-text absolute -left-40 top-40 -rotate-90 origin-left">
          LURIEN
        </div>
        <div className="structural-text absolute right-[-100px] bottom-[-40px] opacity-20 text-[250px]">
          SYSTEM
        </div>
      </div>

      <Sidebar />
      <main className="flex-1 overflow-y-auto relative z-10 scanline">
        <div className="p-6 max-w-[1600px] mx-auto min-h-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
