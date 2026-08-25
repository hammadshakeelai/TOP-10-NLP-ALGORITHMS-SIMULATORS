import { Background, Controls, MiniMap, ReactFlow, type Edge, type Node } from "@xyflow/react";

type GraphNode = {
  id: string;
  label?: string;
  score?: number;
};

type GraphEdge = {
  source: string;
  target: string;
  weight?: number;
};

interface Props {
  data: {
    nodes?: GraphNode[];
    edges?: GraphEdge[];
  };
}

export default function GraphCanvas({ data }: Props) {
  const rawNodes = data?.nodes ?? [];
  const rawEdges = data?.edges ?? [];

  if (!rawNodes.length) {
    return <div className="text-xs text-gray-600 italic">No graph nodes to display.</div>;
  }

  const radius = Math.max(120, Math.min(240, rawNodes.length * 16));
  const nodes: Node[] = rawNodes.map((node, index) => {
    const angle = (index / rawNodes.length) * Math.PI * 2;
    const score = typeof node.score === "number" ? node.score : 0;
    const size = Math.max(36, Math.min(72, 36 + score * 120));
    return {
      id: String(node.id),
      position: {
        x: radius + Math.cos(angle) * radius,
        y: radius + Math.sin(angle) * radius,
      },
      data: { label: node.label ?? node.id },
      style: {
        width: size,
        minHeight: 32,
        padding: 6,
        borderRadius: 8,
        border: "1px solid #334155",
        background: "#0f172a",
        color: "#e5e7eb",
        fontSize: 11,
        textAlign: "center",
      },
    };
  });

  const edges: Edge[] = rawEdges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,
    source: String(edge.source),
    target: String(edge.target),
    label: edge.weight == null ? undefined : String(edge.weight),
    style: {
      stroke: "#64748b",
      strokeWidth: Math.max(1, Math.min(5, Number(edge.weight ?? 1))),
    },
    labelStyle: { fill: "#cbd5e1", fontSize: 10 },
  }));

  return (
    <div
      className="h-[360px] overflow-hidden rounded-lg border border-gray-800 bg-gray-950"
      role="img"
      aria-label={`Graph with ${nodes.length} nodes and ${edges.length} edges`}
    >
      <ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.2} maxZoom={2} proOptions={{ hideAttribution: true }}>
        <Background color="#1f2937" gap={18} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable nodeColor="#1e293b" maskColor="rgba(3, 7, 18, 0.65)" />
      </ReactFlow>
    </div>
  );
}
