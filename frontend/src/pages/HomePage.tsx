import { useEffect, useMemo, useState } from 'react';
import { ContentCard } from '../components/ContentCard';
import { listPublicArticles } from '../api/content';
import { articleToContentCard } from '../data/contentAdapter';
import { categories as mockCategories, contentCards as mockContentCards } from '../data/mockContent';
import type { ContentCard as ContentCardType } from '../data/mockContent';

export function HomePage() {
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [cards, setCards] = useState<ContentCardType[]>(mockContentCards);
  const [sourceLabel, setSourceLabel] = useState('mock fallback');

  useEffect(() => {
    let cancelled = false;

    listPublicArticles()
      .then((articles) => {
        if (cancelled) return;
        if (articles.length > 0) {
          setCards(articles.map(articleToContentCard));
          setSourceLabel('backend');
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCards(mockContentCards);
          setSourceLabel('mock fallback');
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const categories = useMemo(() => Array.from(new Set(cards.flatMap((item) => item.categories))).sort(), [cards]);

  const filteredCards = useMemo(() => {
    if (activeCategory === 'All') return cards;
    return cards.filter((item) => item.categories.includes(activeCategory));
  }, [activeCategory, cards]);

  return (
    <main className="mx-auto max-w-7xl px-6 py-14">
      <section className="mb-12 grid gap-8 lg:grid-cols-[1fr_340px] lg:items-end">
        <div className="max-w-3xl">
          <p className="mb-4 text-sm uppercase tracking-[0.32em] text-moss">LumaGrove Journal</p>
          <h1 className="text-5xl font-semibold tracking-tight text-cream md:text-7xl">A living grow log with automation underneath.</h1>
          <p className="mt-6 text-lg leading-8 text-cream/68">
            Articles, plant timelines, rack experiments, and hardware notes in one place. The public side reads like a journal; the private side controls the actual grow setup.
          </p>
        </div>
        <div className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-5 shadow-2xl shadow-black/20">
          <p className="text-xs uppercase tracking-[0.25em] text-moss">Content source</p>
          <p className="mt-3 text-sm leading-6 text-cream/65">Rendering from {sourceLabel}. Backend content appears automatically once you create public articles.</p>
        </div>
      </section>

      <section className="mb-7 flex flex-wrap gap-2">
        {['All', ...categories].map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`rounded-full border px-4 py-2 text-sm transition ${activeCategory === category ? 'border-leaf bg-leaf/15 text-leaf' : 'border-cream/10 bg-cream/[0.045] text-cream/65 hover:border-cream/25 hover:text-cream'}`}
          >
            {category}
          </button>
        ))}
      </section>

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {filteredCards.map((item) => <ContentCard key={item.slug} item={item} />)}
      </section>
    </main>
  );
}
