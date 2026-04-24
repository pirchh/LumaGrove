import { authFetch } from './auth';
import type { Article, ArticleSection, Plant } from './content';

export type PlantCreatePayload = {
  common_name: string;
  latin_name?: string | null;
  slug?: string | null;
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
  is_public: boolean;
  category_slugs: string[];
  tag_slugs: string[];
};

export type ArticleCreatePayload = {
  plant_id?: string | null;
  title: string;
  slug?: string | null;
  article_type: string;
  summary?: string | null;
  cover_image_url?: string | null;
  cover_asset_id?: string | null;
  start_date?: string | null;
  is_public: boolean;
  category_slugs: string[];
  tag_slugs: string[];
  sections: ArticleSectionCreatePayload[];
};

export type ArticleSectionCreatePayload = {
  title: string;
  body: string;
  section_date?: string | null;
  sort_order: number;
  anchor_slug?: string | null;
  image_url?: string | null;
  asset_id?: string | null;
};

function normalizeResponseError(prefix: string, response: Response): Error {
  return new Error(`${prefix}: ${response.status}`);
}

export async function listAdminPlants(): Promise<Plant[]> {
  const response = await authFetch('/admin/content/plants');
  if (!response.ok) throw normalizeResponseError('Failed to load admin plants', response);
  const payload = await response.json();
  return payload.items ?? [];
}

export async function createAdminPlant(payload: PlantCreatePayload): Promise<Plant> {
  const response = await authFetch('/admin/content/plants', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw normalizeResponseError('Failed to create plant', response);
  return response.json();
}

export async function updateAdminPlant(plantId: string, payload: Partial<PlantCreatePayload>): Promise<Plant> {
  const response = await authFetch(`/admin/content/plants/${plantId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw normalizeResponseError('Failed to update plant', response);
  return response.json();
}

export async function listAdminArticles(): Promise<Article[]> {
  const response = await authFetch('/admin/content/articles');
  if (!response.ok) throw normalizeResponseError('Failed to load admin articles', response);
  const payload = await response.json();
  return payload.items ?? [];
}

export async function createAdminArticle(payload: ArticleCreatePayload): Promise<Article> {
  const response = await authFetch('/admin/content/articles', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw normalizeResponseError('Failed to create article', response);
  return response.json();
}

export async function updateAdminArticle(articleId: string, payload: Partial<ArticleCreatePayload>): Promise<Article> {
  const response = await authFetch(`/admin/content/articles/${articleId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw normalizeResponseError('Failed to update article', response);
  return response.json();
}

export async function createAdminArticleSection(articleId: string, payload: ArticleSectionCreatePayload): Promise<ArticleSection> {
  const response = await authFetch(`/admin/content/articles/${articleId}/sections`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw normalizeResponseError('Failed to create article section', response);
  return response.json();
}

export function csvToSlugs(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}
