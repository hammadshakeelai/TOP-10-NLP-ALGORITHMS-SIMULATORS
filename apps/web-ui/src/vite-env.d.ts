/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the FastAPI gateway. Ignored when VITE_STATIC_MODE is "true". */
  readonly VITE_API_URL?: string;
  /** "true" builds a backend-free static bundle served from src/mocks/. */
  readonly VITE_STATIC_MODE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
