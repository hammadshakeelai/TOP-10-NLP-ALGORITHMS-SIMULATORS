export default function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4" role="status" aria-label="Loading page">
      <span className="relative inline-flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-fuchsia-500 to-sky-500 text-white font-extrabold shadow-glow animate-pulse">
        N
      </span>
      <span className="text-sm text-gray-500">Loading…</span>
    </div>
  );
}
