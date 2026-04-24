import { toAbsoluteMediaUrl, type Article } from '../api/content';
import type { ContentCard, ContentType } from './mockContent';

function articleTypeToContentType(value: string): ContentType {
  if (['article', 'plant', 'experiment', 'hardware'].includes(value)) return value as ContentType;
  return 'article';
}

export function articleToContentCard(article: Article): ContentCard {
  const coverImage = article.cover_asset?.public_url ?? article.cover_image_url ?? article.plant?.cover_asset?.public_url ?? article.plant?.cover_image_url;

  return {
    slug: article.slug,
    title: article.title,
    type: articleTypeToContentType(article.article_type),
    dateLabel: article.start_date ? article.start_date.slice(0, 7) : article.published_at_utc?.slice(0, 7) ?? 'Draft',
    summary: article.summary ?? '',
    categories: article.categories?.map((item) => item.name) ?? [],
    tags: article.tags?.map((item) => item.name) ?? [],
    coverImage: toAbsoluteMediaUrl(coverImage),
    coverAlt: article.title,
    coverTone: 'jade',
    metadata: article.plant
      ? {
          latinName: article.plant.latin_name ?? article.plant.common_name,
          commonName: article.plant.common_name,
          origin: article.plant.origin_region ?? 'Unknown',
          growthZones: article.plant.growth_zones ?? 'Not set',
          light: article.plant.light_preference ?? 'Not set',
          water: article.plant.water_preference ?? 'Not set',
          humidity: article.plant.humidity_preference ?? 'Not set',
          temperature: article.plant.temperature_range ?? 'Not set',
          difficulty: article.plant.growth_habit ?? 'Not set',
          rackStartDate: article.start_date ?? 'Not set',
          growthRangeImage: toAbsoluteMediaUrl(article.plant.growth_range_asset?.public_url ?? article.plant.growth_range_image_url),
        }
      : undefined,
    sections:
      article.sections?.map((section) => ({
        id: section.anchor_slug || section.id,
        title: section.title,
        date: section.section_date ?? '',
        body: section.body,
        imageUrl: toAbsoluteMediaUrl(section.asset?.public_url ?? section.image_url),
        mediaLabel: section.asset || section.image_url ? 'Attached image' : undefined,
      })) ?? [],
  };
}
