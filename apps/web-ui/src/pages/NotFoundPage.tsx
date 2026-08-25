import { useEffect } from "react";
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  useEffect(() => {
    document.title = "Page not found · NLP Simulator";
  }, []);

  return (
    <div className="max-w-md mx-auto mt-24 text-center animate-fade-in">
      <p className="text-6xl font-extrabold gradient-text mb-4">404</p>
      <h1 className="text-xl font-semibold mb-2">This page doesn't exist</h1>
      <p className="text-sm text-gray-400 mb-8">
        The page you're looking for was moved, renamed, or never existed.
      </p>
      <Link
        to="/"
        className="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition focus-ring"
      >
        Back to catalog
      </Link>
    </div>
  );
}
