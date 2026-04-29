import type { ReferenceEntry } from "../types/api";

interface Props {
  references: ReferenceEntry[];
}

export default function ReferencesPanel({ references }: Props) {
  if (!references?.length) return null;

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="font-semibold text-lg mb-4">Research References</h2>
      <div className="space-y-3">
        {references.map((ref, i) => {
          const href = ref.url ?? (ref.doi ? `https://doi.org/${ref.doi}` : null) ?? (ref.arxiv_id ? `https://arxiv.org/abs/${ref.arxiv_id}` : null);
          return (
            <div key={i} className="flex gap-3 bg-gray-800 rounded-lg p-4">
              <div className="text-gray-500 font-mono text-sm mt-0.5 min-w-[20px]">[{i + 1}]</div>
              <div className="space-y-1">
                {href ? (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-sm text-indigo-300 hover:text-indigo-200 underline"
                  >
                    {ref.title}
                  </a>
                ) : (
                  <div className="font-medium text-sm text-gray-200">{ref.title}</div>
                )}
                <div className="text-xs text-gray-400">
                  {ref.authors && <span>{ref.authors}</span>}
                  {ref.year && <span className="ml-2 text-gray-500">({ref.year})</span>}
                  {ref.doi && <span className="ml-2 text-gray-600">DOI: {ref.doi}</span>}
                  {ref.arxiv_id && <span className="ml-2 text-gray-600">arXiv: {ref.arxiv_id}</span>}
                </div>
                {ref.relevance && (
                  <div className="text-xs text-gray-400 italic">{ref.relevance}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
