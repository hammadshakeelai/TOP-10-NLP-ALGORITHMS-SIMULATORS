// Mirror of shared_schemas/models.py — keep in sync with backend Pydantic models.

export type AlgorithmID =
  | "tokenization"
  | "tfidf"
  | "word_embeddings"
  | "naive_bayes"
  | "svm"
  | "lstm"
  | "rake"
  | "textrank"
  | "fasttext"
  | "transformer_attention"
  | "bert"
  | "gpt"
  | "t5";

export type SimulatorMode = "learning" | "experiment" | "assessment" | "admin";
export type TraceLevel = "none" | "summary" | "full";
export type RunStatus = "queued" | "running" | "success" | "warning" | "failed";
export type ReceiverMode = "beginner" | "student" | "researcher" | "engineer" | "instructor";

export interface DocumentInput {
  id: string;
  text: string;
  label?: string;
}

export interface RunRequest {
  experiment_id?: string;
  algorithm_id: AlgorithmID;
  mode?: SimulatorMode;
  text?: string;
  documents?: DocumentInput[];
  labels?: string[];
  parameters?: Record<string, unknown>;
  trace_level?: TraceLevel;
  language?: string;
}

export interface WarningEntry {
  code: string;
  message: string;
  field?: string;
  suggestion?: string;
}

export interface MetricsOutput {
  runtime_ms: number;
  token_count?: number;
  memory_mb?: number;
  model_version?: string;
  extra?: Record<string, unknown>;
}

export interface VisualizationSpec {
  type: string;
  title: string;
  data: unknown;
  config?: Record<string, unknown>;
}

export interface FormulaCard {
  title: string;
  formula: string;
  explanation: string;
  variables: Record<string, string>;
  example?: string;
}

export interface StepExplanation {
  step_id: string;
  stage: string;
  title: string;
  description: string;
  formula?: string;
  input_preview?: unknown;
  output_preview?: unknown;
  why_it_matters?: string;
  visualization_type?: string;
}

export interface HoverAnnotation {
  target: string;
  definition: string;
  formula_meaning?: string;
  example?: string;
  common_mistake?: string;
  reference_label?: string;
}

export interface ReferenceEntry {
  title: string;
  authors?: string;
  year?: number;
  doi?: string;
  arxiv_id?: string;
  url?: string;
  relevance?: string;
}

export interface ReceiverModeExplanation {
  mode: ReceiverMode;
  explanation: string;
  technical_detail?: string;
  teaching_notes?: string;
}

export interface TeachingNotes {
  summary?: string;
  quiz_questions: string[];
  classroom_demo_tips: string[];
  common_misconceptions: string[];
}

export interface DemoMetadata {
  demo_input: Record<string, unknown>;
  auto_parameters: Record<string, unknown>;
  expected_output_preview: Record<string, unknown>;
  beginner_explanation?: string;
  advanced_explanation?: string;
  formula_cards: FormulaCard[];
  step_explanations: StepExplanation[];
  hover_annotations: HoverAnnotation[];
  references: ReferenceEntry[];
  receiver_mode_explanations: ReceiverModeExplanation[];
  research_context?: string;
  teaching_notes?: TeachingNotes;
}

export interface RunResponse {
  run_id: string;
  status: RunStatus;
  algorithm_id: AlgorithmID;
  algorithm_version: string;
  input_fingerprint: string;
  result: Record<string, unknown>;
  trace: Record<string, unknown> | unknown[];
  visualization_specs: VisualizationSpec[];
  metrics: MetricsOutput;
  warnings: WarningEntry[];
  export_links: unknown[];
  demo_input: Record<string, unknown>;
  auto_parameters: Record<string, unknown>;
  step_explanations: StepExplanation[];
  formula_cards: FormulaCard[];
  hover_annotations: HoverAnnotation[];
  references: ReferenceEntry[];
  receiver_mode_explanations: ReceiverModeExplanation[];
  research_context?: string;
  teaching_notes?: TeachingNotes;
}

export interface ParameterSchema {
  name: string;
  type: string;
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  options?: unknown[];
}

export interface AlgorithmEntry {
  id: AlgorithmID;
  name: string;
  family: string;
  description: string;
  use_cases: string[];
  input_types: string[];
  parameter_schema: ParameterSchema[];
  supported_modes: SimulatorMode[];
  complexity: string;
  requires_gpu: boolean;
  is_async: boolean;
}
