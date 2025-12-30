export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-[var(--color-background)]">
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-heading text-[var(--color-gold)]">
          GGP Heritage Mall
        </h1>
        <p className="text-xl text-[var(--color-text-secondary)]">
          VIP Exclusive Shopping Experience
        </p>
        <div className="mt-8 px-8 py-3 bg-[var(--color-surface)] rounded-lg border border-[var(--color-gold)]/20">
          <p className="text-sm text-[var(--color-text-muted)]">
            Access requires a valid invitation link
          </p>
        </div>
      </div>
    </main>
  );
}
