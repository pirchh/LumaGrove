export function AdminDashboardPage() {
  return (
    <section>
      <p className="text-sm uppercase tracking-[0.25em] text-moss">Control Plane</p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">Admin Dashboard</h1>
      <div className="mt-8 grid gap-5 md:grid-cols-3">
        {['Devices', 'Schedules', 'Event Logs'].map((title) => (
          <div key={title} className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-6">
            <p className="text-xl font-semibold">{title}</p>
            <p className="mt-2 text-sm leading-6 text-cream/55">Phase 7A shell. Live API wiring comes next.</p>
          </div>
        ))}
      </div>
    </section>
  );
}
