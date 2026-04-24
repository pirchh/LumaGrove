import { useEffect, useState } from 'react';
import { authFetch } from '../api/auth';

type Schedule = {
  id: string;
  name: string | null;
  desired_state: boolean;
  time_local: string;
  timezone: string;
  is_enabled: boolean;
  next_run_at_utc: string | null;
};

export function AdminSchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);

  async function loadSchedules() {
    const response = await authFetch('/schedules');
    if (response.ok) {
      const data = await response.json();
      setSchedules(data.items ?? []);
    }
  }

  useEffect(() => { void loadSchedules(); }, []);

  return (
    <section>
      <p className="text-sm uppercase tracking-[0.25em] text-moss">Automation</p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">Schedules</h1>
      <div className="mt-8 space-y-4">
        {schedules.map((schedule) => (
          <div key={schedule.id} className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-6">
            <p className="text-xl font-semibold">{schedule.name ?? 'Unnamed schedule'}</p>
            <p className="mt-2 text-sm text-cream/55">
              {schedule.desired_state ? 'On' : 'Off'} at {schedule.time_local} · {schedule.timezone}
            </p>
            <p className="mt-1 text-xs text-cream/35">Next UTC: {schedule.next_run_at_utc ?? 'not scheduled'}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
