import { useState } from 'react';
import { uploadAdminAsset } from '../api/adminAssets';
import { toAbsoluteMediaUrl, type Asset } from '../api/content';

const labelClass = 'mb-2 block text-xs uppercase tracking-[0.18em] text-cream/45';

export function AssetUploader({ label, asset, onUploaded }: { label: string; asset?: Asset | null; onUploaded: (asset: Asset) => void }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File | null) {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const uploaded = await uploadAdminAsset(file);
      onUploaded(uploaded);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-cream/10 bg-black/10 p-4">
      <span className={labelClass}>{label}</span>
      {asset ? (
        <div className="mb-3 overflow-hidden rounded-2xl border border-cream/10 bg-black/20">
          <img src={toAbsoluteMediaUrl(asset.public_url)} alt={asset.original_filename} className="h-36 w-full object-cover" />
          <div className="p-3 text-xs text-cream/50">
            <p className="truncate text-cream/70">{asset.original_filename}</p>
            <p className="mt-1 font-mono">sha256: {asset.sha256.slice(0, 16)}…</p>
          </div>
        </div>
      ) : null}
      <input
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif"
        onChange={(event) => void handleFile(event.target.files?.[0] ?? null)}
        className="block w-full text-sm text-cream/65 file:mr-4 file:rounded-full file:border-0 file:bg-leaf file:px-4 file:py-2 file:text-sm file:font-semibold file:text-soil"
      />
      {uploading ? <p className="mt-2 text-xs text-moss">Uploading...</p> : null}
      {error ? <p className="mt-2 text-xs text-red-300">{error}</p> : null}
    </div>
  );
}
