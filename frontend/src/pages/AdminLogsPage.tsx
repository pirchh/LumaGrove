import { useEffect, useState } from 'react';
import { authFetch } from '../api/auth';

type EventLog = {
  id: string;
  event_type: string;
  severity: string;
  message: string;
  created_at_utc: string;
};

export function AdminLogsPage() {
  const [logs, setLogs] = useState<EventLog[]>([]);

  useEffect(() => {
    void authFetch('/event-logs?limit=50').then(async (response) => {
      if (response.ok) {
        const data = await response.json();
        setLogs(data.items ?? []);
      }
    });
  }, []);

  return (
    <section>
      <p className="text-sm uppercase tracking-[0.25em] text-moss">System</p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">Event Logs</h1>
      <div className="mt-8 space-y-3">
        {logs.map((log) => (
          <div key={log.id} className="rounded-2xl border border-cream/10 bg-cream/[0.045] p-4">
            <div className="flex flex-col justify-between gap-2 md:flex-row md:items-center">
              <p className="font-medium">{log.event_type}</p>
              <p className="text-xs text-cream/40">{new Date(log.created_at_utc).toLocaleString()}</p>
            </div>
            <p className="mt-1 text-sm text-cream/55">{log.message}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
