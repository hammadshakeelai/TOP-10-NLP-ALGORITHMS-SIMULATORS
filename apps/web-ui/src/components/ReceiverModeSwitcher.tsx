import type { ReceiverMode } from "../types/api";

interface Props {
  value: ReceiverMode;
  onChange: (mode: ReceiverMode) => void;
}

const MODES: { value: ReceiverMode; label: string; color: string }[] = [
  { value: "beginner",    label: "Beginner",    color: "bg-emerald-700 hover:bg-emerald-600" },
  { value: "student",     label: "Student",     color: "bg-blue-700 hover:bg-blue-600" },
  { value: "researcher",  label: "Researcher",  color: "bg-violet-700 hover:bg-violet-600" },
  { value: "engineer",    label: "Engineer",    color: "bg-amber-700 hover:bg-amber-600" },
  { value: "instructor",  label: "Instructor",  color: "bg-rose-700 hover:bg-rose-600" },
];

export default function ReceiverModeSwitcher({ value, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {MODES.map((m) => (
        <button
          key={m.value}
          onClick={() => onChange(m.value)}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
            value === m.value
              ? m.color + " text-white ring-2 ring-white/30"
              : "bg-gray-700 text-gray-300 hover:bg-gray-600"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
