import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Badge } from '../components/Badge';
import { PlantOverviewPanel } from '../components/PlantOverviewPanel';
import { getPublicArticle } from '../api/content';
import { articleToContentCard } from '../data/contentAdapter';
import { contentCards, getContentBySlug } from '../data/mockContent';
import type { ContentCard } from '../data/mockContent';

export function ArticlePage() {
  const { slug } = useParams();
  const fallbackItem = useMemo(() => getContentBySlug(slug ?? '') ?? contentCards[0], [slug]);
  const [item, setItem] = useState<ContentCard>(fallbackItem);
  const [sourceLabel, setSourceLabel] = useState('mock fallback');

  useEffect(() => {
    let cancelled = false;
    if (!slug) return;

    getPublicArticle(slug)
      .then((article) => {
        if (!cancelled) {
          setItem(articleToContentCard(article));
          setSourceLabel('backend');
        }
      })
      .catch(() => {
        if (!cancelled) {
          setItem(fallbackItem);
          setSourceLabel('mock fallback');
        }
      });

    return () => { cancelled = true; };
  }, [slug, fallbackItem]);

  return (
    <main className="mx-auto max-w-7xl px-6 py-12">
      <Link to="/" className="text-sm text-cream/55 hover:text-cream">← Back to journal</Link>
      <section className="mt-8 grid gap-10 xl:grid-cols-[260px_1fr_320px]">
        <aside className="space-y-5 xl:sticky xl:top-28 xl:h-fit">
          <div className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-5">
            <p className="mb-4 text-xs uppercase tracking-[0.25em] text-moss">Timeline</p>
            <div className="relative space-y-5 border-l border-leaf/30 pl-5">
              {item.sections.map((section) => (
                <a key={section.id} href={`#${section.id}`} className="group relative block">
                  <span className="absolute -left-[25px] mt-1 h-2.5 w-2.5 rounded-full bg-leaf transition group-hover:scale-125" />
                  <p className="text-xs text-cream/45">{section.date}</p>
                  <p className="text-sm text-cream/80 group-hover:text-leaf">{section.title}</p>
                </a>
              ))}
            </div>
          </div>
        </aside>

        <article>
          <div className="mb-8 overflow-hidden rounded-[2rem] border border-cream/10 bg-gradient-to-br from-cream/[0.08] to-leaf/[0.08] shadow-2xl shadow-black/20">
            {item.coverImage ? <img src={item.coverImage} alt={item.coverAlt ?? item.title} className="h-64 w-full object-cover" /> : <div className="h-64 bg-gradient-to-br from-leaf/25 via-moss/10 to-black/25" />}
            <div className="p-8">
              <div className="mb-3 flex items-center gap-3">
                <p className="text-sm uppercase tracking-[0.25em] text-moss">{item.type}</p>
                <span className="rounded-full border border-cream/10 px-2 py-0.5 text-[11px] text-cream/45">{sourceLabel}</span>
              </div>
              <h1 className="max-w-4xl text-5xl font-semibold tracking-tight md:text-6xl">{item.title}</h1>
              <p className="mt-5 max-w-3xl text-lg leading-8 text-cream/68">{item.summary}</p>
              <div className="mt-6 flex flex-wrap gap-2">
                {item.categories.map((category) => <Badge key={category}>{category}</Badge>)}
                {item.tags.map((tag) => <Badge key={tag} tone="outline">{tag}</Badge>)}
              </div>
            </div>
          </div>

          <div className="space-y-8">
            {item.sections.map((section) => (
              <section id={section.id} key={section.id} className="section-anchor overflow-hidden rounded-3xl border border-cream/10 bg-cream/[0.045]">
                {section.imageUrl ? <img src={section.imageUrl} alt={section.title} className="h-72 w-full object-cover" /> : null}
                <div className="p-7">
                  <p className="mb-2 text-sm text-moss">{section.date}</p>
                  <h2 className="mb-4 text-3xl font-semibold tracking-tight">{section.title}</h2>
                  <p className="whitespace-pre-wrap text-base leading-8 text-cream/70">{section.body}</p>
                </div>
              </section>
            ))}
          </div>
        </article>

        <aside className="xl:sticky xl:top-28 xl:h-fit">
          <PlantOverviewPanel item={item} />
        </aside>
      </section>
    </main>
  );
}
