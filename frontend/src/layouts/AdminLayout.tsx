import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { clearToken } from '../api/auth';

const navItems = [
  ['Dashboard', '/admin'],
  ['Content', '/admin/content'],
  ['Plants', '/admin/plants'],
  ['Themes', '/admin/themes'],
  ['Devices', '/admin/devices'],
  ['Schedules', '/admin/schedules'],
  ['Logs', '/admin/logs'],
] as const;

export function AdminLayout() {
  const navigate = useNavigate();

  function logout() {
    clearToken();
    navigate('/admin/login');
  }

  return (
    <div className="min-h-screen bg-[#11100d] text-cream">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-cream/10 bg-soil/90 p-6 lg:block">
        <div className="mb-10">
          <p className="text-xl font-semibold">LumaGrove Admin</p>
          <p className="mt-1 text-sm text-cream/45">private control plane</p>
        </div>
        <nav className="space-y-2">
          {navItems.map(([label, href]) => (
            <NavLink
              key={href}
              to={href}
              end={href === '/admin'}
              className={({ isActive }) => `block rounded-2xl px-4 py-3 text-sm transition ${isActive ? 'bg-leaf/15 text-leaf' : 'text-cream/65 hover:bg-cream/5 hover:text-cream'}`}
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <button onClick={logout} className="absolute bottom-6 left-6 right-6 rounded-2xl border border-cream/10 px-4 py-3 text-sm text-cream/60 hover:bg-cream/5 hover:text-cream">
          Logout
        </button>
      </aside>
      <main className="lg:pl-72">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
