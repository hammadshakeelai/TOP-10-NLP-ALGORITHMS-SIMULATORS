import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled UI error:", error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="max-w-xl mx-auto mt-20 panel p-8 text-center animate-fade-in">
        <div className="text-4xl mb-3" aria-hidden>⚠️</div>
        <h1 className="text-lg font-semibold text-gray-100 mb-2">Something went wrong</h1>
        <p className="text-sm text-gray-400 mb-1">
          An unexpected error interrupted the page. Your data in this session may be lost.
        </p>
        <pre className="mt-3 mb-5 max-h-32 overflow-auto rounded-lg bg-gray-950/70 p-3 text-left text-xs font-mono text-red-300">
          {this.state.error.message}
        </pre>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => this.setState({ error: null })}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition focus-ring"
          >
            Try again
          </button>
          <a
            href="/"
            className="px-4 py-2 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition focus-ring"
          >
            Go home
          </a>
        </div>
      </div>
    );
  }
}
