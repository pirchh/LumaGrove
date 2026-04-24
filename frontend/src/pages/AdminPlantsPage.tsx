import { FormEvent, useEffect, useState } from 'react';
import type { Asset, Plant } from '../api/content';
import { AssetUploader } from '../components/AssetUploader';
import { createAdminPlant, csvToSlugs, emptyToNull, listAdminPlants } from '../api/adminContent';

const inputClass = 'w-full rounded-2xl border border-cream/10 bg-black/20 px-4 py-3 text-sm outline-none transition focus:border-leaf/50';
const labelClass = 'mb-2 block text-xs uppercase tracking-[0.18em] text-cream/45';

const initialForm = {
  common_name: '',
  latin_name: '',
  slug: '',
  summary: '',
  origin_region: '',
  growth_zones: '',
  light_preference: '',
  water_preference: '',
  humidity_preference: '',
  temperature_range: '',
  soil_preference: '',
  growth_habit: '',
  notes: '',
  cover_image_url: '',
  growth_range_image_url: '',
  edible: false,
  indoor_friendly: true,
  flowering: false,
  is_public: true,
  categories: '',
  tags: '',
};

export function AdminPlantsPage() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [form, setForm] = useState(initialForm);
  const [coverAsset, setCoverAsset] = useState<Asset | null>(null);
  const [growthRangeAsset, setGrowthRangeAsset] = useState<Asset | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadPlants() {
    const items = await listAdminPlants();
    setPlants(items);
  }

  useEffect(() => {
    void loadPlants().catch(() => setError('Could not load plants from backend.'));
  }, []);

  function setField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      await createAdminPlant({
        common_name: form.common_name,
        latin_name: emptyToNull(form.latin_name),
        slug: emptyToNull(form.slug),
        summary: emptyToNull(form.summary),
        origin_region: emptyToNull(form.origin_region),
        growth_zones: emptyToNull(form.growth_zones),
        light_preference: emptyToNull(form.light_preference),
        water_preference: emptyToNull(form.water_preference),
        humidity_preference: emptyToNull(form.humidity_preference),
        temperature_range: emptyToNull(form.temperature_range),
        soil_preference: emptyToNull(form.soil_preference),
        growth_habit: emptyToNull(form.growth_habit),
        notes: emptyToNull(form.notes),
        cover_image_url: emptyToNull(form.cover_image_url),
        growth_range_image_url: emptyToNull(form.growth_range_image_url),
        cover_asset_id: coverAsset?.id ?? null,
        growth_range_asset_id: growthRangeAsset?.id ?? null,
        edible: form.edible,
        indoor_friendly: form.indoor_friendly,
        flowering: form.flowering,
        is_public: form.is_public,
        category_slugs: csvToSlugs(form.categories),
        tag_slugs: csvToSlugs(form.tags),
      });
      setMessage('Plant created. Public articles can now attach to it.');
      setForm(initialForm);
      setCoverAsset(null);
      setGrowthRangeAsset(null);
      await loadPlants();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Plant creation failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-moss">Plant encyclopedia</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">Plants</h1>
          <p className="mt-2 max-w-3xl text-cream/55">
            Create the structured plant records that power public overview panels: latin name, common name, growth ranges, care preferences, cover images, categories, and tags.
          </p>
        </div>
        <div className="rounded-2xl border border-cream/10 bg-cream/[0.045] px-4 py-3 text-sm text-cream/55">
          {plants.length} plant{plants.length === 1 ? '' : 's'} in backend
        </div>
      </div>

      <form onSubmit={onSubmit} className="rounded-[2rem] border border-cream/10 bg-cream/[0.045] p-6 shadow-2xl shadow-black/20">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.25em] text-moss">New plant</p>
          <h2 className="mt-2 text-2xl font-semibold">Generate new plant profile</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-1">
            <AssetUploader label="Cover image upload" asset={coverAsset} onUploaded={setCoverAsset} />
          </div>
          <div className="md:col-span-1">
            <AssetUploader label="Growth range image upload" asset={growthRangeAsset} onUploaded={setGrowthRangeAsset} />
          </div>
          <label><span className={labelClass}>Common name</span><input required value={form.common_name} onChange={(e) => setField('common_name', e.target.value)} className={inputClass} placeholder="Jalapeño / Cayenne Pepper" /></label>
          <label><span className={labelClass}>Latin name</span><input value={form.latin_name} onChange={(e) => setField('latin_name', e.target.value)} className={inputClass} placeholder="Capsicum annuum" /></label>
          <label><span className={labelClass}>Slug</span><input value={form.slug} onChange={(e) => setField('slug', e.target.value)} className={inputClass} placeholder="capsicum-annuum" /></label>
          <label><span className={labelClass}>Origin region</span><input value={form.origin_region} onChange={(e) => setField('origin_region', e.target.value)} className={inputClass} placeholder="Central and South America" /></label>
          <label><span className={labelClass}>Growth zones</span><input value={form.growth_zones} onChange={(e) => setField('growth_zones', e.target.value)} className={inputClass} placeholder="Annual in most climates; perennial in warm indoor conditions" /></label>
          <label><span className={labelClass}>Light preference</span><input value={form.light_preference} onChange={(e) => setField('light_preference', e.target.value)} className={inputClass} placeholder="High light; long photoperiod indoors" /></label>
          <label><span className={labelClass}>Water preference</span><input value={form.water_preference} onChange={(e) => setField('water_preference', e.target.value)} className={inputClass} placeholder="Even moisture while germinating" /></label>
          <label><span className={labelClass}>Humidity preference</span><input value={form.humidity_preference} onChange={(e) => setField('humidity_preference', e.target.value)} className={inputClass} placeholder="Moderate; avoid stagnant damp air" /></label>
          <label><span className={labelClass}>Temperature range</span><input value={form.temperature_range} onChange={(e) => setField('temperature_range', e.target.value)} className={inputClass} placeholder="70–85°F preferred" /></label>
          <label><span className={labelClass}>Soil preference</span><input value={form.soil_preference} onChange={(e) => setField('soil_preference', e.target.value)} className={inputClass} placeholder="Well-draining seed-starting mix" /></label>
          <label><span className={labelClass}>Growth habit</span><input value={form.growth_habit} onChange={(e) => setField('growth_habit', e.target.value)} className={inputClass} placeholder="Upright, branching pepper plant" /></label>
          <label><span className={labelClass}>Cover image URL</span><input value={form.cover_image_url} onChange={(e) => setField('cover_image_url', e.target.value)} className={inputClass} placeholder="https://..." /></label>
          <label><span className={labelClass}>Growth range image URL</span><input value={form.growth_range_image_url} onChange={(e) => setField('growth_range_image_url', e.target.value)} className={inputClass} placeholder="https://..." /></label>
          <label><span className={labelClass}>Categories</span><input value={form.categories} onChange={(e) => setField('categories', e.target.value)} className={inputClass} placeholder="vegetable, indoor" /></label>
          <label><span className={labelClass}>Tags</span><input value={form.tags} onChange={(e) => setField('tags', e.target.value)} className={inputClass} placeholder="jalapeno, cayenne, seed-starting" /></label>
        </div>

        <label className="mt-4 block"><span className={labelClass}>Summary</span><textarea value={form.summary} onChange={(e) => setField('summary', e.target.value)} className={`${inputClass} min-h-24`} placeholder="Short public overview for this plant." /></label>
        <label className="mt-4 block"><span className={labelClass}>Notes</span><textarea value={form.notes} onChange={(e) => setField('notes', e.target.value)} className={`${inputClass} min-h-28`} placeholder="Longer care or encyclopedia notes." /></label>

        <div className="mt-5 flex flex-wrap gap-4 text-sm text-cream/65">
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.edible} onChange={(e) => setField('edible', e.target.checked)} /> Edible</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.indoor_friendly} onChange={(e) => setField('indoor_friendly', e.target.checked)} /> Indoor friendly</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.flowering} onChange={(e) => setField('flowering', e.target.checked)} /> Flowering</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.is_public} onChange={(e) => setField('is_public', e.target.checked)} /> Public</label>
        </div>

        <div className="mt-6 flex items-center gap-4">
          <button disabled={loading} className="rounded-2xl bg-leaf px-5 py-3 text-sm font-semibold text-soil transition hover:brightness-110 disabled:opacity-50">
            {loading ? 'Saving...' : 'Create plant'}
          </button>
          {message ? <p className="text-sm text-leaf">{message}</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </div>
      </form>

      <div className="grid gap-4 md:grid-cols-2">
        {plants.map((plant) => (
          <div key={plant.id} className="rounded-3xl border border-cream/10 bg-cream/[0.045] p-5">
            <div className="mb-4 h-28 rounded-2xl border border-cream/8 bg-gradient-to-br from-leaf/20 to-black/20">
              {plant.cover_image_url ? <img src={plant.cover_image_url} alt={plant.common_name} className="h-full w-full rounded-2xl object-cover" /> : null}
            </div>
            <p className="text-xs uppercase tracking-[0.25em] text-moss">{plant.common_name}</p>
            <h2 className="mt-2 text-2xl font-semibold italic">{plant.latin_name ?? plant.common_name}</h2>
            <p className="mt-3 text-sm leading-6 text-cream/60">{plant.summary ?? 'No summary yet.'}</p>
            <div className="mt-4 grid gap-2 text-sm text-cream/55">
              <p><span className="text-cream/35">Zones:</span> {plant.growth_zones ?? 'not set'}</p>
              <p><span className="text-cream/35">Light:</span> {plant.light_preference ?? 'not set'}</p>
              <p><span className="text-cream/35">Water:</span> {plant.water_preference ?? 'not set'}</p>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {plant.categories.map((item) => <span key={item.slug} className="rounded-full border border-leaf/20 bg-leaf/10 px-3 py-1 text-xs text-leaf">{item.name}</span>)}
              {plant.tags.map((item) => <span key={item.slug} className="rounded-full border border-cream/10 px-3 py-1 text-xs text-cream/45">{item.name}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
