/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Optional full backend URL for production. Dev uses the Vite proxy. */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
