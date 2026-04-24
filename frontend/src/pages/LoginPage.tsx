import { FormEvent, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { login } from '../api/auth';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
      const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/admin';
      navigate(from, { replace: true });
    } catch {
      setError('Login failed. Check the admin credentials in .env.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-[2rem] border border-cream/10 bg-cream/[0.06] p-8 shadow-2xl shadow-black/25">
        <p className="mb-2 text-sm uppercase tracking-[0.25em] text-moss">Private Admin</p>
        <h1 className="mb-6 text-4xl font-semibold tracking-tight">LumaGrove Login</h1>
        <label className="mb-4 block">
          <span className="mb-2 block text-sm text-cream/60">Username</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)} className="w-full rounded-2xl border border-cream/10 bg-black/20 px-4 py-3 outline-none focus:border-leaf/50" />
        </label>
        <label className="mb-6 block">
          <span className="mb-2 block text-sm text-cream/60">Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-2xl border border-cream/10 bg-black/20 px-4 py-3 outline-none focus:border-leaf/50" />
        </label>
        {error ? <p className="mb-4 text-sm text-red-300">{error}</p> : null}
        <button disabled={loading} className="w-full rounded-2xl bg-leaf px-4 py-3 font-semibold text-soil transition hover:brightness-110 disabled:opacity-60">
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </main>
  );
}
