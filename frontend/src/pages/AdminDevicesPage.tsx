import { useEffect, useState } from 'react';
import { authFetch } from '../api/auth';

type Device = {
  id: string;
  name: string;
  device_type: string;
  is_enabled: boolean;
  state_cache?: { status_json?: { output?: boolean; reachable?: boolean } } | null;
};

export function AdminDevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadDevices() {
    const response = await authFetch('/devices');
    if (!response.ok) {
      setError('Could not load devices.');
      return;
    }
    setDevices(await response.json());
  }

  async function setPower(deviceId: string, on: boolean) {
    const response = await authFetch(`/devices/${deviceId}/commands/power`, {
      method: 'POST',
      body: JSON.stringify({ on }),
    });
    if (!response.ok) {
      setError('Power command failed.');
      return;
    }
    await loadDevices();
  }

  useEffect(() => { void loadDevices(); }, []);

  return (
    <section>
      <p className="text-sm uppercase tracking-[0.25em] text-moss">Hardware</p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">Devices</h1>
      {error ? <p className="mt-4 text-red-300">{error}</p> : null}
      <div className="mt-8 space-y-4">
        {devices.map((device) => (
          <div key={device.id} className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-6">
            <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
              <div>
                <p className="text-xl font-semibold">{device.name}</p>
                <p className="mt-1 text-sm text-cream/50">{device.device_type} · {device.state_cache?.status_json?.reachable ? 'reachable' : 'unknown'}</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setPower(device.id, false)} className="rounded-2xl border border-cream/10 px-4 py-2 text-sm hover:bg-cream/5">Off</button>
                <button onClick={() => setPower(device.id, true)} className="rounded-2xl bg-leaf px-4 py-2 text-sm font-semibold text-soil hover:brightness-110">On</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
