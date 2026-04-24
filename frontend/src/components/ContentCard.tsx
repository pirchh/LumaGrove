import { Link } from 'react-router-dom';
import { ArrowUpRight, Sprout } from 'lucide-react';
import { Badge } from './Badge';
import type { ContentCard as ContentCardType } from '../data/mockContent';

type Props = { item: ContentCardType };

const coverClasses: Record<ContentCardType['coverTone'], string> = {
  jade: 'from-emerald-300/25 via-lime-200/10 to-black/20',
  pepper: 'from-red-400/20 via-orange-200/10 to-black/25',
  amber: 'from-amber-300/25 via-yellow-100/10 to-black/25',
  violet: 'from-violet-300/20 via-cyan-200/10 to-black/25',
  pine: 'from-green-700/35 via-emerald-200/10 to-black/25',
  blue: 'from-sky-400/20 via-blue-200/10 to-black/25',
};

export function ContentCard({ item }: Props) {
  const href = item.type === 'plant' ? `/plant/${item.slug}` : `/article/${item.slug}`;

  return (
    <Link to={href} className="group block overflow-hidden rounded-3xl border border-cream/10 bg-cream/[0.055] shadow-2xl shadow-black/20 transition duration-300 hover:-translate-y-1 hover:border-leaf/45 hover:bg-cream/[0.075]">
      <div className={`relative h-52 overflow-hidden bg-gradient-to-br ${coverClasses[item.coverTone]} p-5`}>
        {item.coverImage ? <img src={item.coverImage} alt={item.coverAlt ?? item.title} className="absolute inset-0 h-full w-full object-cover opacity-75 transition duration-500 group-hover:scale-105" /> : null}
        <div className="absolute inset-0 bg-gradient-to-t from-soil via-soil/35 to-transparent" />
        <div className="absolute inset-0 opacity-30 [background-image:radial-gradient(circle_at_20%_20%,rgba(255,255,255,.22),transparent_18rem),radial-gradient(circle_at_80%_0%,rgba(183,200,139,.2),transparent_16rem)]" />
        <div className="relative flex items-start justify-between gap-4">
          <span className="rounded-full border border-cream/15 bg-soil/45 px-3 py-1 text-xs text-cream/80 backdrop-blur">{item.dateLabel}</span>
          <ArrowUpRight className="h-5 w-5 text-cream/55 transition group-hover:text-leaf" />
        </div>
        <div className="absolute bottom-5 left-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-cream/10 bg-black/20 text-leaf backdrop-blur">
          <Sprout className="h-6 w-6" />
        </div>
      </div>
      <div className="space-y-4 p-6">
        <div>
          <p className="mb-2 text-xs uppercase tracking-[0.22em] text-moss">{item.type}</p>
          <h2 className="text-2xl font-semibold tracking-tight text-cream">{item.title}</h2>
        </div>
        <p className="min-h-20 text-sm leading-6 text-cream/68">{item.summary}</p>
        <div className="flex flex-wrap gap-2">
          {item.categories.slice(0, 3).map((category) => <Badge key={category}>{category}</Badge>)}
        </div>
      </div>
    </Link>
  );
}
