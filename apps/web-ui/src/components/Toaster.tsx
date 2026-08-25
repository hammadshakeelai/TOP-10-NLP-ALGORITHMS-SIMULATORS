import { dismissToast, useToasts, type ToastKind } from "../lib/toasts";

const KIND_STYLES: Record<ToastKind, string> = {
  success: "border-emerald-500/40 bg-emerald-950/90 text-emerald-100",
  error: "border-red-500/40 bg-red-950/90 text-red-100",
  info: "border-indigo-500/40 bg-gray-900/95 text-gray-100",
};

const KIND_ICONS: Record<ToastKind, string> = {
  success: "✓",
  error: "✕",
  info: "ℹ",
};

export default function Toaster() {
  const toasts = useToasts();
  if (!toasts.length) return null;

  return (
    <div
      aria-live="polite"
      aria-atomic="false"
      className="fixed bottom-5 right-5 z-50 flex w-80 max-w-[calc(100vw-2.5rem)] flex-col gap-2"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`animate-toast-in pointer-events-auto flex items-start gap-2.5 rounded-lg border px-3.5 py-2.5 shadow-lg backdrop-blur ${KIND_STYLES[t.kind]}`}
        >
          <span aria-hidden className="mt-0.5 text-xs font-bold">
            {KIND_ICONS[t.kind]}
          </span>
          <p className="flex-1 text-sm leading-snug break-words">{t.message}</p>
          <button
            onClick={() => dismissToast(t.id)}
            aria-label="Dismiss notification"
            className="shrink-0 opacity-60 transition hover:opacity-100"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
