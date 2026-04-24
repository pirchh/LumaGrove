const themes = [
  { name: 'Soil Dark', description: 'Current warm dark journal theme.' },
  { name: 'Greenhouse Light', description: 'Future bright public theme with soft cream cards.' },
  { name: 'Night Rack', description: 'Future high-contrast admin/control theme.' },
];

export function AdminThemesPage() {
  return (
    <div>
      <p className="text-sm uppercase tracking-[0.25em] text-moss">Site settings mock</p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">Themes</h1>
      <p className="mt-3 max-w-2xl text-cream/55">Eventually this page should save one global public theme for everyone. For now it documents the direction without adding another backend table.</p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {themes.map((theme, index) => (
          <div key={theme.name} className={`rounded-3xl border p-5 ${index === 0 ? 'border-leaf/40 bg-leaf/10' : 'border-cream/10 bg-cream/[0.045]'}`}>
            <p className="text-xl font-semibold">{theme.name}</p>
            <p className="mt-3 text-sm leading-6 text-cream/58">{theme.description}</p>
            <button className="mt-6 rounded-2xl border border-cream/10 px-4 py-2 text-sm text-cream/70">{index === 0 ? 'Active' : 'Preview'}</button>
          </div>
        ))}
      </div>
    </div>
  );
}
