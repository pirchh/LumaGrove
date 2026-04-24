export type ContentType = 'article' | 'plant' | 'experiment' | 'hardware';

export type PlantMetadata = {
  commonName: string;
  latinName: string;
  origin?: string;
  growthZones?: string;
  light?: string;
  water?: string;
  humidity?: string;
  temperature?: string;
  difficulty?: string;
  rackStartDate?: string;
  growthRangeImage?: string;
};

export type ContentCard = {
  slug: string;
  type: ContentType;
  title: string;
  summary: string;
  dateLabel: string;
  categories: string[];
  tags: string[];
  coverImage?: string;
  coverAlt?: string;
  coverTone: 'jade' | 'pepper' | 'amber' | 'violet' | 'pine' | 'blue';
  metadata?: PlantMetadata;
  sections: ContentSection[];
};

export type ContentSection = {
  id: string;
  title: string;
  date: string;
  body: string;
  mediaLabel?: string;
  imageUrl?: string;
};

export const contentCards: ContentCard[] = [
  {
    slug: 'portulacaria-afra-indoor-rack',
    type: 'plant',
    title: 'Portulacaria Afra on the Indoor Rack',
    summary: 'Tracking light response, watering cadence, trunk development, and whether the rack can support long-term bonsai growth.',
    dateLabel: 'Apr 2026',
    categories: ['Bonsai', 'Succulent', 'Indoor'],
    tags: ['low humidity tolerant', 'grow light', 'trunk thickening', 'beginner friendly'],
    coverTone: 'jade',
    metadata: {
      commonName: 'Elephant Bush / Dwarf Jade',
      latinName: 'Portulacaria afra',
      origin: 'Southern Africa',
      growthZones: 'USDA 9–11 outdoors; indoor-friendly under bright light',
      light: 'Bright indirect to strong grow light',
      water: 'Let dry between waterings',
      humidity: 'Tolerates 30–50% indoor humidity',
      temperature: '65–85°F preferred',
      difficulty: 'Beginner-friendly',
      rackStartDate: '2026-04-24',
    },
    sections: [
      {
        id: 'setup',
        title: 'Initial rack setup',
        date: '2026-04-24',
        body: 'The first baseline is simple: stable light, controlled watering, and enough airflow to avoid stagnant humidity while still keeping the plant from drying too fast.',
        mediaLabel: 'Rack photo placeholder',
      },
      {
        id: 'light-window',
        title: 'Light window and timing',
        date: '2026-04-25',
        body: 'The lights are treated as a scheduled device group. LumaGrove will eventually handle the on/off window while the journal captures observed response over time.',
      },
      {
        id: 'first-prune',
        title: 'First structure pass',
        date: '2026-05-10',
        body: 'The first pruning pass should focus on direction and branching, not perfection. The goal is a compact structure with enough growth left to thicken naturally.',
      },
    ],
  },
  {
    slug: 'pepper-seed-starting-notes',
    type: 'plant',
    title: 'Pepper Seed Starting Notes',
    summary: 'A grow log for jalapeño and cayenne germination, moisture control, and early light exposure under the rack.',
    dateLabel: 'Apr 2026',
    categories: ['Vegetable', 'Indoor'],
    tags: ['seed starting', 'jalapeño', 'cayenne', 'moisture'],
    coverTone: 'pepper',
    metadata: {
      commonName: 'Jalapeño / Cayenne Pepper',
      latinName: 'Capsicum annuum',
      origin: 'Central and South America',
      growthZones: 'Annual in most climates; perennial with warm indoor conditions',
      light: 'High light; long photoperiod indoors',
      water: 'Even moisture during germination, moderate after establishment',
      humidity: 'Average indoor humidity is acceptable',
      temperature: '70–85°F for germination',
      difficulty: 'Moderate indoors',
      rackStartDate: '2026-04-23',
    },
    sections: [
      {
        id: 'sowing',
        title: 'Seeds started',
        date: '2026-04-23',
        body: 'Seeds were started in small cells and misted from the top. The first watch item is keeping the medium evenly damp without turning it soggy.',
      },
      {
        id: 'watering',
        title: 'Moisture rhythm',
        date: '2026-04-24',
        body: 'The goal is a repeatable light-watering rhythm. The medium should not fully crust over during germination, but pooling water is worse than needing a second misting.',
      },
    ],
  },
  {
    slug: 'lumagrove-control-plane',
    type: 'hardware',
    title: 'Building the LumaGrove Control Plane',
    summary: 'How the project moved from a local FastAPI scaffold to real scheduled control of a Shelly smart plug.',
    dateLabel: 'Apr 2026',
    categories: ['Automation', 'Infrastructure'],
    tags: ['Shelly', 'FastAPI', 'scheduler', 'UTC'],
    coverTone: 'blue',
    sections: [
      {
        id: 'backend-slice',
        title: 'Backend vertical slice',
        date: '2026-04-24',
        body: 'The first slice proved the important loop: register hardware, test connectivity, save it, control it, log it, and schedule it.',
      },
      {
        id: 'scheduler',
        title: 'Scheduler comes online',
        date: '2026-04-24',
        body: 'Recurring local-time schedule intent is converted into UTC execution times. The app-integrated poller now processes due schedules from the database.',
      },
    ],
  },
  {
    slug: 'rack-humidity-baseline',
    type: 'experiment',
    title: 'Rack Humidity Baseline',
    summary: 'A running experiment to understand how the open rack behaves with indoor airflow, AC movement, and no enclosed tent.',
    dateLabel: 'May 2026',
    categories: ['Experiment', 'Indoor'],
    tags: ['humidity', 'airflow', 'sensor', 'rack'],
    coverTone: 'violet',
    sections: [
      {
        id: 'baseline',
        title: 'Baseline range',
        date: '2026-05-01',
        body: 'The initial expected indoor range sits around 30–50%. This log tracks whether plant placement, trays, or partial enclosure materially changes that range.',
      },
    ],
  },
  {
    slug: 'micro-tomato-candidate-list',
    type: 'article',
    title: 'Micro Tomato Candidate List',
    summary: 'Notes on compact tomato varieties that could fit the rack while still producing fruit under indoor lights.',
    dateLabel: 'May 2026',
    categories: ['Vegetable', 'Fruit', 'Indoor'],
    tags: ['micro tomato', 'edible', 'grow light', 'compact'],
    coverTone: 'amber',
    sections: [
      {
        id: 'candidate-traits',
        title: 'Candidate traits',
        date: '2026-05-03',
        body: 'The right candidates stay compact, produce quickly, and do not require a large trellis. The rack can support experimentation, but height and light intensity are the limiting constraints.',
      },
    ],
  },
  {
    slug: 'brush-cherry-bonsai-notes',
    type: 'plant',
    title: 'Brush Cherry Bonsai Notes',
    summary: 'A future candidate profile for indoor flowering bonsai potential, humidity tolerance, and trunk development.',
    dateLabel: 'May 2026',
    categories: ['Bonsai', 'Flowering', 'Indoor'],
    tags: ['brush cherry', 'flowering', 'humidity', 'candidate'],
    coverTone: 'pine',
    metadata: {
      commonName: 'Brush Cherry',
      latinName: 'Syzygium paniculatum',
      origin: 'Australia',
      growthZones: 'USDA 10–11 outdoors; indoor bonsai candidate',
      light: 'Bright light',
      water: 'Even moisture, avoid full dry-down',
      humidity: 'Prefers moderate humidity',
      temperature: '65–80°F preferred',
      difficulty: 'Intermediate',
      rackStartDate: 'Candidate only',
    },
    sections: [
      {
        id: 'candidate',
        title: 'Candidate profile',
        date: '2026-05-05',
        body: 'Brush cherry is being tracked as a possible flowering bonsai candidate. The main concern is whether the open rack humidity and airflow are too dry long term.',
      },
    ],
  },
];

export const categories = Array.from(new Set(contentCards.flatMap((item) => item.categories))).sort();

export function getContentBySlug(slug: string): ContentCard | undefined {
  return contentCards.find((item) => item.slug === slug);
}
