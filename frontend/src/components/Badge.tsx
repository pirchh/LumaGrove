type BadgeProps = {
  children: React.ReactNode;
  tone?: 'soft' | 'outline';
};

export function Badge({ children, tone = 'soft' }: BadgeProps) {
  const classes = tone === 'soft'
    ? 'bg-leaf/15 text-leaf border-leaf/20'
    : 'bg-transparent text-cream/70 border-cream/15';

  return <span className={`rounded-full border px-3 py-1 text-xs ${classes}`}>{children}</span>;
}
