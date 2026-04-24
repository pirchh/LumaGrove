import { Link, Outlet } from 'react-router-dom';

export function PublicLayout() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-cream/10 bg-soil/75 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-2xl bg-leaf/80 shadow-lg shadow-leaf/20" />
            <div>
              <p className="text-lg font-semibold tracking-tight">LumaGrove</p>
              <p className="text-xs text-cream/45">grow notes · automation · experiments</p>
            </div>
          </Link>
          <nav className="flex items-center gap-5 text-sm text-cream/65">
            <Link to="/" className="hover:text-cream">Journal</Link>
            <Link to="/admin" className="hover:text-cream">Admin</Link>
          </nav>
        </div>
      </header>
      <Outlet />
    </div>
  );
}
