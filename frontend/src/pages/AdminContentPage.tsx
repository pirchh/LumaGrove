import { FormEvent, useEffect, useMemo, useState } from 'react';
import type { Article, Asset, Plant } from '../api/content';
import { AssetUploader } from '../components/AssetUploader';
import {
  createAdminArticle,
  createAdminArticleSection,
  csvToSlugs,
  emptyToNull,
  listAdminArticles,
  listAdminPlants,
} from '../api/adminContent';

const inputClass = 'w-full rounded-2xl border border-cream/10 bg-black/20 px-4 py-3 text-sm outline-none transition focus:border-leaf/50';
const labelClass = 'mb-2 block text-xs uppercase tracking-[0.18em] text-cream/45';

const initialArticleForm = {
  plant_id: '',
  title: '',
  slug: '',
  article_type: 'article',
  summary: '',
  cover_image_url: '',
  start_date: '',
  is_public: true,
  categories: '',
  tags: '',
};

const initialSectionForm = {
  title: '',
  body: '',
  section_date: '',
  sort_order: 0,
  anchor_slug: '',
  image_url: '',
};

export function AdminContentPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [articleForm, setArticleForm] = useState(initialArticleForm);
  const [articleCoverAsset, setArticleCoverAsset] = useState<Asset | null>(null);
  const [sectionForm, setSectionForm] = useState(initialSectionForm);
  const [sectionAsset, setSectionAsset] = useState<Asset | null>(null);
  const [selectedArticleId, setSelectedArticleId] = useState('');
  const [loadingArticle, setLoadingArticle] = useState(false);
  const [loadingSection, setLoadingSection] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadContent() {
    const [articleItems, plantItems] = await Promise.all([listAdminArticles(), listAdminPlants()]);
    setArticles(articleItems);
    setPlants(plantItems);
    if (!selectedArticleId && articleItems.length > 0) setSelectedArticleId(articleItems[0].id);
  }

  useEffect(() => {
    void loadContent().catch(() => setError('Could not load content from backend.'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectedArticle = useMemo(() => articles.find((article) => article.id === selectedArticleId) ?? null, [articles, selectedArticleId]);

  function setArticleField<K extends keyof typeof articleForm>(key: K, value: (typeof articleForm)[K]) {
    setArticleForm((current) => ({ ...current, [key]: value }));
  }

  function setSectionField<K extends keyof typeof sectionForm>(key: K, value: (typeof sectionForm)[K]) {
    setSectionForm((current) => ({ ...current, [key]: value }));
  }

  async function onCreateArticle(event: FormEvent) {
    event.preventDefault();
    setLoadingArticle(true);
    setMessage(null);
    setError(null);

    try {
      const article = await createAdminArticle({
        plant_id: articleForm.plant_id || null,
        title: articleForm.title,
        slug: emptyToNull(articleForm.slug),
        article_type: articleForm.article_type,
        summary: emptyToNull(articleForm.summary),
        cover_image_url: emptyToNull(articleForm.cover_image_url),
        cover_asset_id: articleCoverAsset?.id ?? null,
        start_date: emptyToNull(articleForm.start_date),
        is_public: articleForm.is_public,
        category_slugs: csvToSlugs(articleForm.categories),
        tag_slugs: csvToSlugs(articleForm.tags),
        sections: [],
      });
      setMessage('Article created. Add timeline sections below.');
      setSelectedArticleId(article.id);
      setArticleForm(initialArticleForm);
      setArticleCoverAsset(null);
      await loadContent();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Article creation failed.');
    } finally {
      setLoadingArticle(false);
    }
  }

  async function onCreateSection(event: FormEvent) {
    event.preventDefault();
    if (!selectedArticleId) {
      setError('Select or create an article first.');
      return;
    }
    setLoadingSection(true);
    setMessage(null);
    setError(null);

    try {
      await createAdminArticleSection(selectedArticleId, {
        title: sectionForm.title,
        body: sectionForm.body,
        section_date: emptyToNull(sectionForm.section_date),
        sort_order: Number(sectionForm.sort_order) || 0,
        anchor_slug: emptyToNull(sectionForm.anchor_slug),
        image_url: emptyToNull(sectionForm.image_url),
        asset_id: sectionAsset?.id ?? null,
      });
      setMessage('Timeline section added. Public article page will render it automatically.');
      setSectionForm(initialSectionForm);
      setSectionAsset(null);
      await loadContent();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Section creation failed.');
    } finally {
      setLoadingSection(false);
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-moss">CMS lite</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">Content</h1>
          <p className="mt-2 max-w-3xl text-cream/55">
            Create article cards, attach them to plant encyclopedia records, and add dated timeline sections that render on the public site.
          </p>
        </div>
        <div className="rounded-2xl border border-cream/10 bg-cream/[0.045] px-4 py-3 text-sm text-cream/55">
          {articles.length} article{articles.length === 1 ? '' : 's'} · {plants.length} plant{plants.length === 1 ? '' : 's'}
        </div>
      </div>

      <form onSubmit={onCreateArticle} className="rounded-[2rem] border border-cream/10 bg-cream/[0.045] p-6 shadow-2xl shadow-black/20">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.25em] text-moss">New article</p>
          <h2 className="mt-2 text-2xl font-semibold">Create article card</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <AssetUploader label="Article cover / thumbnail upload" asset={articleCoverAsset} onUploaded={setArticleCoverAsset} />
          </div>
          <label><span className={labelClass}>Title</span><input required value={articleForm.title} onChange={(e) => setArticleField('title', e.target.value)} className={inputClass} placeholder="Pepper Seed Starting Notes" /></label>
          <label><span className={labelClass}>Slug</span><input value={articleForm.slug} onChange={(e) => setArticleField('slug', e.target.value)} className={inputClass} placeholder="pepper-seed-starting-notes" /></label>
          <label>
            <span className={labelClass}>Type</span>
            <select value={articleForm.article_type} onChange={(e) => setArticleField('article_type', e.target.value)} className={inputClass}>
              <option value="article">Article</option>
              <option value="plant">Plant</option>
              <option value="experiment">Experiment</option>
              <option value="hardware">Hardware</option>
            </select>
          </label>
          <label>
            <span className={labelClass}>Attached plant</span>
            <select value={articleForm.plant_id} onChange={(e) => setArticleField('plant_id', e.target.value)} className={inputClass}>
              <option value="">None</option>
              {plants.map((plant) => <option key={plant.id} value={plant.id}>{plant.common_name} {plant.latin_name ? `(${plant.latin_name})` : ''}</option>)}
            </select>
          </label>
          <label><span className={labelClass}>Start date</span><input type="date" value={articleForm.start_date} onChange={(e) => setArticleField('start_date', e.target.value)} className={inputClass} /></label>
          <label><span className={labelClass}>Cover / thumbnail URL</span><input value={articleForm.cover_image_url} onChange={(e) => setArticleField('cover_image_url', e.target.value)} className={inputClass} placeholder="https://..." /></label>
          <label><span className={labelClass}>Categories</span><input value={articleForm.categories} onChange={(e) => setArticleField('categories', e.target.value)} className={inputClass} placeholder="vegetable, indoor" /></label>
          <label><span className={labelClass}>Tags</span><input value={articleForm.tags} onChange={(e) => setArticleField('tags', e.target.value)} className={inputClass} placeholder="jalapeno, germination, moisture" /></label>
        </div>

        <label className="mt-4 block"><span className={labelClass}>Summary</span><textarea value={articleForm.summary} onChange={(e) => setArticleField('summary', e.target.value)} className={`${inputClass} min-h-24`} placeholder="Short card-level summary for the public homepage." /></label>

        <div className="mt-5 flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-cream/65"><input type="checkbox" checked={articleForm.is_public} onChange={(e) => setArticleField('is_public', e.target.checked)} /> Public</label>
          <button disabled={loadingArticle} className="rounded-2xl bg-leaf px-5 py-3 text-sm font-semibold text-soil transition hover:brightness-110 disabled:opacity-50">
            {loadingArticle ? 'Saving...' : 'Create article'}
          </button>
          {message ? <p className="text-sm text-leaf">{message}</p> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
        </div>
      </form>

      <section className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <div className="overflow-hidden rounded-3xl border border-cream/10 bg-cream/[0.045]">
          <div className="border-b border-cream/10 p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-moss">Backend articles</p>
            <h2 className="mt-2 text-2xl font-semibold">Current content</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-cream/10 text-cream/45">
                <tr>
                  <th className="px-5 py-4 font-medium">Title</th>
                  <th className="px-5 py-4 font-medium">Type</th>
                  <th className="px-5 py-4 font-medium">Plant</th>
                  <th className="px-5 py-4 font-medium">Public</th>
                  <th className="px-5 py-4 font-medium">Sections</th>
                </tr>
              </thead>
              <tbody>
                {articles.map((article) => (
                  <tr
                    key={article.id}
                    onClick={() => setSelectedArticleId(article.id)}
                    className={`cursor-pointer border-b border-cream/5 last:border-0 ${selectedArticleId === article.id ? 'bg-leaf/10' : 'hover:bg-cream/[0.035]'}`}
                  >
                    <td className="px-5 py-4 text-cream">{article.title}</td>
                    <td className="px-5 py-4 capitalize text-cream/65">{article.article_type}</td>
                    <td className="px-5 py-4 text-cream/65">{article.plant?.common_name ?? '—'}</td>
                    <td className="px-5 py-4 text-cream/65">{article.is_public ? 'Yes' : 'No'}</td>
                    <td className="px-5 py-4 text-cream/65">{article.sections.length}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <form onSubmit={onCreateSection} className="rounded-3xl border border-cream/10 bg-cream/[0.045] p-5">
          <p className="text-xs uppercase tracking-[0.25em] text-moss">Timeline section</p>
          <h2 className="mt-2 text-2xl font-semibold">Add dated section</h2>
          <p className="mt-2 text-sm text-cream/50">Selected: {selectedArticle?.title ?? 'none'}</p>

          <div className="mt-5 space-y-4">
            <label><span className={labelClass}>Article</span><select value={selectedArticleId} onChange={(e) => setSelectedArticleId(e.target.value)} className={inputClass}>{articles.map((article) => <option key={article.id} value={article.id}>{article.title}</option>)}</select></label>
            <label><span className={labelClass}>Section title</span><input required value={sectionForm.title} onChange={(e) => setSectionField('title', e.target.value)} className={inputClass} placeholder="Seeds started" /></label>
            <label><span className={labelClass}>Section date</span><input type="date" value={sectionForm.section_date} onChange={(e) => setSectionField('section_date', e.target.value)} className={inputClass} /></label>
            <label><span className={labelClass}>Sort order</span><input type="number" value={sectionForm.sort_order} onChange={(e) => setSectionField('sort_order', Number(e.target.value))} className={inputClass} /></label>
            <label><span className={labelClass}>Anchor slug</span><input value={sectionForm.anchor_slug} onChange={(e) => setSectionField('anchor_slug', e.target.value)} className={inputClass} placeholder="seeds-started" /></label>
            <AssetUploader label="Section image upload" asset={sectionAsset} onUploaded={setSectionAsset} />
            <label><span className={labelClass}>Image URL</span><input value={sectionForm.image_url} onChange={(e) => setSectionField('image_url', e.target.value)} className={inputClass} placeholder="https://..." /></label>
            <label><span className={labelClass}>Body</span><textarea required value={sectionForm.body} onChange={(e) => setSectionField('body', e.target.value)} className={`${inputClass} min-h-36`} placeholder="Write the dated update here." /></label>
          </div>

          <button disabled={loadingSection || !selectedArticleId} className="mt-5 rounded-2xl bg-leaf px-5 py-3 text-sm font-semibold text-soil transition hover:brightness-110 disabled:opacity-50">
            {loadingSection ? 'Saving...' : 'Add section'}
          </button>
        </form>
      </section>
    </div>
  );
}
