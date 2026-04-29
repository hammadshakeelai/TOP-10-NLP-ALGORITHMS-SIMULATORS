import { useState } from "react";
import type { StepExplanation } from "../types/api";

const STAGE_COLORS: Record<string, string> = {
  input_validation: "bg-blue-500",
  preprocessing:    "bg-teal-500",
  computation:      "bg-violet-500",
  training:         "bg-amber-500",
  forward_pass:     "bg-orange-500",
  prediction:       "bg-rose-500",
  output:           "bg-emerald-500",
  graph_construction: "bg-cyan-500",
  generation_loop:  "bg-pink-500",
  encoder_forward:  "bg-indigo-500",
  decoder_generation: "bg-purple-500",
};

function stageColor(stage: string) {
  return STAGE_COLORS[stage] ?? "bg-gray-500";
}

interface Props {
  steps: StepExplanation[];
}

export default function StepTimeline({ steps }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!steps?.length) return null;

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="font-semibold text-lg mb-4">Pipeline Steps</h2>
      <div className="relative">
        {/* vertical line */}
        <div className="absolute left-3.5 top-4 bottom-4 w-px bg-gray-700" />

        <div className="space-y-3">
          {steps.map((step, i) => {
            const isOpen = expanded === step.step_id;
            return (
              <div key={step.step_id} className="relative pl-10">
                {/* dot */}
                <div
                  className={`absolute left-0 top-1 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white ${stageColor(step.stage)}`}
                >
                  {i + 1}
                </div>

                <button
                  onClick={() => setExpanded(isOpen ? null : step.step_id)}
                  className="w-full text-left bg-gray-800 hover:bg-gray-750 rounded-lg px-4 py-3 transition"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs text-gray-400 uppercase tracking-wide">{step.stage.replace(/_/g, " ")}</span>
                      <div className="font-medium text-sm mt-0.5">{step.title}</div>
                    </div>
                    <span className="text-gray-500 text-xs">{isOpen ? "▲" : "▼"}</span>
                  </div>
                </button>

                {isOpen && (
                  <div className="mt-2 ml-0 bg-gray-800/50 rounded-lg px-4 py-3 text-sm space-y-3">
                    <p className="text-gray-300">{step.description}</p>

                    {step.formula && (
                      <div className="bg-gray-900 rounded px-3 py-2 font-mono text-indigo-300 text-xs">
                        {step.formula}
                      </div>
                    )}

                    {step.why_it_matters && (
                      <div className="flex gap-2 text-xs text-amber-300">
                        <span>💡</span>
                        <span>{step.why_it_matters}</span>
                      </div>
                    )}

                    {!!(step.input_preview || step.output_preview) && (
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        {!!step.input_preview && (
                          <div>
                            <div className="text-gray-500 mb-1">Input</div>
                            <pre className="bg-gray-900 rounded p-2 text-gray-300 overflow-auto max-h-24 whitespace-pre-wrap">
                              {JSON.stringify(step.input_preview, null, 2)}
                            </pre>
                          </div>
                        )}
                        {!!step.output_preview && (
                          <div>
                            <div className="text-gray-500 mb-1">Output</div>
                            <pre className="bg-gray-900 rounded p-2 text-green-300 overflow-auto max-h-24 whitespace-pre-wrap">
                              {JSON.stringify(step.output_preview, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
