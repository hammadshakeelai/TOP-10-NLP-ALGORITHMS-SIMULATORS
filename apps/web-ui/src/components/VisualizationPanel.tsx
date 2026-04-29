/**
 * VisualizationPanel — dispatches each VisualizationSpec to the correct chart component.
 *
 * Supported spec.type values: bar | heatmap | scatter | graph | table | timeline | diff | line | tree
 */
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, ScatterChart, Scatter, ZAxis,
} from "recharts";
import type { VisualizationSpec } from "../types/api";
import GraphCanvas from "./GraphCanvas";

interface Props {
  specs: VisualizationSpec[];
}

export default function VisualizationPanel({ specs }: Props) {
  if (!specs?.length) return null;
  return (
    <section className="space-y-6">
      <h2 className="font-semibold text-lg">Visualizations</h2>
      {specs.map((spec, i) => (
        <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h3 className="font-medium text-sm text-gray-300 mb-4">{spec.title}</h3>
          <SpecRenderer spec={spec} />
        </div>
      ))}
    </section>
  );
}

function SpecRenderer({ spec }: { spec: VisualizationSpec }) {
  const data = spec.data as any;
  const cfg  = spec.config as any ?? {};

  switch (spec.type) {
    case "bar":
      return <BarViz data={data} cfg={cfg} />;
    case "heatmap":
      return <HeatmapViz data={data} cfg={cfg} />;
    case "scatter":
      return <ScatterViz data={data} cfg={cfg} />;
    case "line":
      return <LineViz data={data} cfg={cfg} />;
    case "table":
      return <TableViz data={Array.isArray(data) ? data : []} />;
    case "diff":
      return <DiffViz data={data} />;
    case "graph":
      return <GraphCanvas data={data} />;
    case "timeline":
      return <TableViz data={Array.isArray(data) ? data : []} />;
    default:
      return <pre className="text-xs text-gray-400 overflow-auto">{JSON.stringify(data, null, 2)}</pre>;
  }
}

// ── Bar ─────────────────────────────────────────────────────────────────────

function BarViz({ data, cfg }: { data: any[]; cfg: any }) {
  if (!Array.isArray(data) || !data.length) return <Empty />;
  const xKey = cfg.x ?? Object.keys(data[0])[0];
  const yKey = cfg.y ?? Object.keys(data[0])[1];
  const color = cfg.color ?? "#6366f1";
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ left: 0, right: 16, top: 4, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey={xKey} tick={{ fill: "#9ca3af", fontSize: 11 }} angle={-30} textAnchor="end" interval={0} />
        <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }} />
        <Bar dataKey={yKey} fill={color} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

// ── Heatmap ─────────────────────────────────────────────────────────────────

function HeatmapViz({ data, cfg }: { data: any; cfg: any }) {
  // data: { labels: string[], matrix: number[][] }  OR  { terms: string[], rows: [{doc_id, values}] }
  if (!data) return <Empty />;

  let labels: string[] = [];
  let rowLabels: string[] = [];
  let matrix: number[][] = [];

  if (data.labels && data.matrix) {
    labels = data.labels;
    rowLabels = data.labels;
    matrix = data.matrix;
  } else if (data.terms && data.rows) {
    labels = data.terms;
    rowLabels = data.rows.map((r: any) => r.doc_id);
    matrix = data.rows.map((r: any) => r.values);
  } else {
    return <pre className="text-xs text-gray-400">{JSON.stringify(data, null, 2).slice(0, 500)}</pre>;
  }

  const allVals = matrix.flat();
  const maxVal = Math.max(...allVals, 0.001);

  return (
    <div className="overflow-auto">
      <table className="text-xs border-collapse">
        <thead>
          <tr>
            <th className="text-gray-500 pr-3 text-right font-normal" />
            {labels.map((l, i) => (
              <th key={i} className="text-gray-400 px-1 pb-1 font-normal max-w-[60px] truncate" title={l}>{l.slice(0, 8)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, ri) => (
            <tr key={ri}>
              <td className="text-gray-400 pr-3 text-right font-mono max-w-[80px] truncate">{rowLabels[ri]}</td>
              {row.map((val, ci) => {
                const intensity = Math.round((val / maxVal) * 200);
                return (
                  <td
                    key={ci}
                    title={`${rowLabels[ri]} × ${labels[ci]}: ${val.toFixed(4)}`}
                    className="w-8 h-7 text-center"
                    style={{ background: `rgba(99,102,241,${val / maxVal})` }}
                  />
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Scatter ──────────────────────────────────────────────────────────────────

function ScatterViz({ data, cfg }: { data: any[]; cfg: any }) {
  if (!Array.isArray(data) || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ScatterChart margin={{ left: 0, right: 16, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey="x" type="number" tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <YAxis dataKey="y" type="number" tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <ZAxis range={[60, 60]} />
        <Tooltip
          cursor={{ strokeDasharray: "3 3" }}
          contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }}
          labelFormatter={(_, payload) => payload?.[0]?.payload?.word ?? ""}
        />
        <Scatter data={data} fill="#6366f1" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

// ── Line ─────────────────────────────────────────────────────────────────────

function LineViz({ data, cfg }: { data: any[]; cfg: any }) {
  if (!Array.isArray(data) || !data.length) return <Empty />;
  const xKey = cfg.x ?? "iteration";
  const yKey = cfg.y ?? "max_delta";
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ left: 0, right: 16, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis dataKey={xKey} tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }} />
        {Array.isArray(yKey)
          ? yKey.map((k: string, i: number) => (
              <Line key={k} type="monotone" dataKey={k} stroke={["#6366f1", "#10b981"][i]} dot={false} />
            ))
          : <Line type="monotone" dataKey={yKey} stroke="#6366f1" dot={false} />}
      </LineChart>
    </ResponsiveContainer>
  );
}

// ── Table ─────────────────────────────────────────────────────────────────────

function TableViz({ data }: { data: Record<string, unknown>[] }) {
  if (!data?.length) return <Empty />;
  const keys = Object.keys(data[0]);
  return (
    <div className="overflow-auto max-h-64">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-800">
            {keys.map((k) => (
              <th key={k} className="text-left text-gray-400 font-medium pb-2 pr-4">{k}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 100).map((row, i) => (
            <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
              {keys.map((k) => (
                <td key={k} className="py-1.5 pr-4 font-mono text-gray-300 max-w-xs truncate">
                  {String(row[k] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Diff ─────────────────────────────────────────────────────────────────────

function DiffViz({ data }: { data: { original?: string; cleaned?: string; prompt?: string; completion?: string; source?: string; target?: string } }) {
  const left  = data?.original ?? data?.prompt ?? data?.source ?? "";
  const right = data?.cleaned  ?? data?.completion ?? data?.target ?? "";
  return (
    <div className="grid grid-cols-2 gap-4 text-xs font-mono">
      <div>
        <div className="text-gray-500 mb-1">Before / Source</div>
        <pre className="bg-gray-800 rounded p-3 whitespace-pre-wrap text-gray-300 max-h-40 overflow-auto">{left}</pre>
      </div>
      <div>
        <div className="text-gray-500 mb-1">After / Target</div>
        <pre className="bg-gray-800 rounded p-3 whitespace-pre-wrap text-green-300 max-h-40 overflow-auto">{right}</pre>
      </div>
    </div>
  );
}

function Empty() {
  return <div className="text-xs text-gray-600 italic">No data to display.</div>;
}
