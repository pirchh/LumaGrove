import { Badge } from './Badge';
import type { ContentCard } from '../data/mockContent';

type Props = { item: ContentCard };

export function PlantOverviewPanel({ item }: Props) {
  const metadata = item.metadata;

  if (!metadata) {
    return (
      <div className="rounded-3xl border border-cream/10 bg-cream/[0.055] p-6">
        <p className="mb-3 text-xs uppercase tracking-[0.25em] text-moss">Overview</p>
        <p className="text-sm leading-6 text-cream/65">This entry is structured as a journal article. Plant encyclopedia metadata can be attached later from the admin content tools.</p>
      </div>
    );
  }

  const rows = [
    ['Common', metadata.commonName],
    ['Latin', metadata.latinName],
    ['Origin', metadata.origin],
    ['Zones', metadata.growthZones],
    ['Light', metadata.light],
    ['Water', metadata.water],
    ['Humidity', metadata.humidity],
    ['Temp', metadata.temperature],
    ['Difficulty', metadata.difficulty],
    ['Start', metadata.rackStartDate],
  ].filter(([, value]) => Boolean(value));

  return (
    <div className="space-y-4 rounded-3xl border border-cream/10 bg-cream/[0.055] p-6">
      <div>
        <p className="mb-2 text-xs uppercase tracking-[0.25em] text-moss">Plant overview</p>
        <h3 className="text-2xl font-semibold italic tracking-tight text-cream/95">{metadata.latinName}</h3>
      </div>
      {metadata.growthRangeImage ? (
        <img src={metadata.growthRangeImage} alt={`${metadata.latinName} range reference`} className="h-36 w-full rounded-2xl border border-cream/10 object-cover" />
      ) : null}
      <div className="grid gap-3">
        {rows.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-cream/8 bg-black/10 p-3">
            <p className="text-[0.65rem] uppercase tracking-[0.22em] text-cream/35">{label}</p>
            <p className="mt-1 text-sm leading-5 text-cream/78">{value}</p>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 pt-1">
        {item.tags.slice(0, 6).map((tag) => <Badge key={tag} tone="outline">{tag}</Badge>)}
      </div>
    </div>
  );
}
