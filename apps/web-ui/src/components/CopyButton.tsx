import { useState } from "react";
import { toast } from "../lib/toasts";

interface Props {
  value: string | (() => string);
  label?: string;
  className?: string;
}

function fallbackCopy(text: string): boolean {
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

export default function CopyButton({ value, label = "Copy", className }: Props) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    const text = typeof value === "function" ? value() : value;
    let ok = false;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        ok = true;
      }
    } catch {
      ok = false;
    }
    if (!ok) ok = fallbackCopy(text);
    if (ok) {
      setCopied(true);
      toast("Copied to clipboard.", "success", 2000);
      setTimeout(() => setCopied(false), 1600);
    } else {
      toast("Could not access the clipboard.", "error");
    }
  }

  return (
    <button
      onClick={handleCopy}
      className={
        className ??
        "text-xs text-gray-500 hover:text-gray-300 transition focus-ring rounded px-1"
      }
    >
      {copied ? "Copied ✓" : label}
    </button>
  );
}
