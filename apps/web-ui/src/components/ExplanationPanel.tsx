import type { ReceiverMode, ReceiverModeExplanation, TeachingNotes } from "../types/api";

interface Props {
  mode: ReceiverMode;
  explanations: ReceiverModeExplanation[];
  researchContext?: string;
  teachingNotes?: TeachingNotes;
}

export default function ExplanationPanel({ mode, explanations, researchContext, teachingNotes }: Props) {
  const active = explanations?.find((e) => e.mode === mode);

  if (!active && !researchContext) return null;

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
      <h2 className="font-semibold text-lg">Explanation</h2>

      {active && (
        <div className="space-y-3">
          <p className="text-sm text-gray-200 leading-relaxed">{active.explanation}</p>

          {active.technical_detail && (
            <div className="bg-gray-800 rounded-lg px-4 py-3 text-xs text-gray-300 leading-relaxed">
              <span className="text-indigo-400 font-semibold mr-2">Technical detail:</span>
              {active.technical_detail}
            </div>
          )}

          {active.teaching_notes && mode === "instructor" && (
            <div className="bg-amber-950/40 border border-amber-900/50 rounded-lg px-4 py-3 text-xs text-amber-200 leading-relaxed">
              <span className="font-semibold mr-2">Teaching notes:</span>
              {active.teaching_notes}
            </div>
          )}
        </div>
      )}

      {researchContext && (
        <div className="text-xs text-gray-400 leading-relaxed border-t border-gray-800 pt-3">
          <span className="text-gray-300 font-semibold mr-2">Research context:</span>
          {researchContext}
        </div>
      )}

      {teachingNotes && mode === "instructor" && (
        <div className="border-t border-gray-800 pt-3 space-y-3">
          {teachingNotes.quiz_questions.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-amber-400 mb-2">Quiz Questions</div>
              <ul className="space-y-1">
                {teachingNotes.quiz_questions.map((q, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-amber-500">{i + 1}.</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {teachingNotes.common_misconceptions.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-rose-400 mb-2">Common Misconceptions</div>
              <ul className="space-y-1">
                {teachingNotes.common_misconceptions.map((m, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-rose-500">✗</span>
                    <span>{m}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
