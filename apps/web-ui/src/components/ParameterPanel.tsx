import { useAppDispatch } from "../store/hooks";
import { updateRequest } from "../store/simulationSlice";
import type { ParameterSchema } from "../types/api";

interface Props {
  schema: ParameterSchema[];
}

export default function ParameterPanel({ schema }: Props) {
  const dispatch = useAppDispatch();
  if (!schema?.length) return null;

  function handleChange(name: string, rawValue: string, type: string) {
    let value: unknown = rawValue;
    if (type === "int")   value = parseInt(rawValue, 10);
    if (type === "float") value = parseFloat(rawValue);
    if (type === "bool")  value = rawValue === "true";
    if (type === "array") {
      try { value = JSON.parse(rawValue); } catch { value = rawValue.split(",").map((s) => s.trim()); }
    }
    dispatch(updateRequest({ parameters: { [name]: value } }));
  }

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5" aria-label="Parameters">
      <h2 className="font-semibold mb-4">Parameters</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {schema.map((param) => {
          const inputId = `param-${param.name}`;
          return (
            <div key={param.name}>
              <label htmlFor={inputId} className="block text-xs text-gray-400 mb-1">
                {param.name}
              </label>
              {param.description && (
                <p id={`${inputId}-desc`} className="text-[11px] text-gray-500 mb-1 leading-snug">
                  {param.description}
                </p>
              )}
              {param.options ? (
                <select
                  id={inputId}
                  aria-describedby={param.description ? `${inputId}-desc` : undefined}
                  defaultValue={String(param.default)}
                  onChange={(e) => handleChange(param.name, e.target.value, param.type)}
                  className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus:border-indigo-500 outline-none focus-ring"
                >
                  {param.options.map((o) => (
                    <option key={String(o)} value={String(o)}>{String(o)}</option>
                  ))}
                </select>
              ) : param.type === "bool" ? (
                <select
                  id={inputId}
                  aria-describedby={param.description ? `${inputId}-desc` : undefined}
                  defaultValue={String(param.default)}
                  onChange={(e) => handleChange(param.name, e.target.value, "bool")}
                  className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus-ring"
                >
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              ) : (
                <input
                  id={inputId}
                  aria-describedby={param.description ? `${inputId}-desc` : undefined}
                  type={param.type === "int" || param.type === "float" ? "number" : "text"}
                  defaultValue={param.type === "array" ? JSON.stringify(param.default) : String(param.default ?? "")}
                  min={param.min !== undefined ? param.min : undefined}
                  max={param.max !== undefined ? param.max : undefined}
                  step={param.type === "float" ? 0.01 : undefined}
                  onChange={(e) => handleChange(param.name, e.target.value, param.type)}
                  className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm font-mono focus:border-indigo-500 outline-none focus-ring"
                />
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
