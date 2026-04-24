const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8003';

export function toAbsoluteMediaUrl(value?: string | null): string | undefined {
  if (!value) return undefined;
  if (value.startsWith('http://') || value.startsWith('https://')) return value;
  if (value.startsWith('/')) return `${API_BASE_URL}${value}`;
  return value;
}

export type Asset = {
  id: string;
  original_filename: string;
  stored_filename: string;
  storage_path: string;
  public_url: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  created_at_utc?: string | null;
  updated_at_utc?: string | null;
};

export type TaxonomyItem = {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
};

export type Plant = {
  id: string;
  common_name: string;
  latin_name?: string | null;
  slug: string;
  summary?: string | null;
  origin_region?: string | null;
  growth_zones?: string | null;
  light_preference?: string | null;
  water_preference?: string | null;
  humidity_preference?: string | null;
  temperature_range?: string | null;
  soil_preference?: string | null;
  growth_habit?: string | null;
  edible: boolean;
  indoor_friendly: boolean;
  flowering: boolean;
  notes?: string | null;
  cover_image_url?: string | null;
  growth_range_image_url?: string | null;
  cover_asset_id?: string | null;
  growth_range_asset_id?: string | null;
  cover_asset?: Asset | null;
  growth_range_asset?: Asset | null;
  is_public: boolean;
  categories: TaxonomyItem[];
  tags: TaxonomyItem[];
};

export type ArticleSection = {
  id: string;
  article_id: string;
  title: string;
  body: string;
  section_date?: string | null;
  sort_order: number;
  anchor_slug: string;
  image_url?: string | null;
  asset_id?: string | null;
  asset?: Asset | null;
};

export type Article = {
  id: string;
  plant_id?: string | null;
  title: string;
  slug: string;
  article_type: string;
  summary?: string | null;
  cover_image_url?: string | null;
  cover_asset_id?: string | null;
  cover_asset?: Asset | null;
  published_at_utc?: string | null;
  start_date?: string | null;
  is_public: boolean;
  plant?: Plant | null;
  categories: TaxonomyItem[];
  tags: TaxonomyItem[];
  sections: ArticleSection[];
};

export async function listPublicArticles(): Promise<Article[]> {
  const response = await fetch(`${API_BASE_URL}/public/articles`);
  if (!response.ok) throw new Error(`Failed to load public articles: ${response.status}`);
  const payload = await response.json();
  return payload.items ?? [];
}

export async function getPublicArticle(slug: string): Promise<Article> {
  const response = await fetch(`${API_BASE_URL}/public/articles/${slug}`);
  if (!response.ok) throw new Error(`Failed to load article: ${response.status}`);
  return response.json();
}
