"use client";

import type {
  ErrorBody,
  Garment,
  GarmentAnalysis,
  GarmentAttributes,
  Generation,
  Health,
  Inspiration,
  SampleInspiration,
  SavedLook,
  StylePreferences,
} from "./types";

const BASE = "/api";
const TOKEN_KEY = "rewear.token";

export class ApiError extends Error {
  code: string;
  status: number;
  retryable: boolean;

  constructor(status: number, body: ErrorBody) {
    super(body.message);
    this.status = status;
    this.code = body.code;
    this.retryable = body.retryable;
  }
}

/** Backend media paths ("/media/...") are served through the same-origin proxy. */
export function mediaUrl(path: string): string {
  return path.startsWith("/media/") ? `${BASE}${path}` : path;
}

function readToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

let tokenPromise: Promise<string> | null = null;

async function token(): Promise<string> {
  const existing = readToken();
  if (existing) return existing;
  tokenPromise ??= request<{ token: string }>("/session", { method: "POST" }, false).then((s) => {
    try {
      window.localStorage.setItem(TOKEN_KEY, s.token);
    } catch {
      /* private mode: token lives for this tab only */
    }
    return s.token;
  });
  return tokenPromise;
}

async function request<T>(path: string, init: RequestInit = {}, auth = true): Promise<T> {
  const headers = new Headers(init.headers);
  if (auth) headers.set("Authorization", `Bearer ${await token()}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { ...init, headers, cache: "no-store" });
  } catch {
    throw new ApiError(0, {
      code: "network_error",
      message: "Can't reach Rewear right now. Check your connection.",
      retryable: true,
    });
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    /* non-JSON error page */
  }
  if (!res.ok) {
    const body = (data as { error?: ErrorBody } | null)?.error ?? {
      code: "http_error",
      message:
        res.status >= 500 ? "Something went wrong on our side. Please try again." : `Request failed (${res.status}).`,
      retryable: res.status >= 500,
    };
    throw new ApiError(res.status, body);
  }
  return data as T;
}

const json = (body: unknown): RequestInit => ({ body: JSON.stringify(body) });

export const api = {
  health: () => request<Health>("/health", {}, false),

  listGarments: () => request<Garment[]>("/wardrobe/items"),
  analyzeGarment: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<GarmentAnalysis>("/wardrobe/items/analyze", { method: "POST", body: fd });
  },
  reanalyzeUpload: (uploadId: string) =>
    request<GarmentAnalysis>(`/wardrobe/uploads/${uploadId}/analyze`, { method: "POST" }),
  createGarment: (uploadId: string, attrs: GarmentAttributes) =>
    request<Garment>("/wardrobe/items", { method: "POST", ...json({ ...attrs, upload_id: uploadId }) }),
  updateGarment: (id: string, attrs: Partial<GarmentAttributes>) =>
    request<Garment>(`/wardrobe/items/${id}`, { method: "PATCH", ...json(attrs) }),
  deleteGarment: (id: string) => request<void>(`/wardrobe/items/${id}`, { method: "DELETE" }),

  loadSampleWardrobe: () => request<{ added: number; items: Garment[] }>("/demo/wardrobe", { method: "POST" }),
  removeSampleWardrobe: () => request<{ added: number; items: Garment[] }>("/demo/wardrobe", { method: "DELETE" }),
  sampleInspirations: () => request<SampleInspiration[]>("/demo/inspirations"),

  createInspiration: (input: { file: File } | { sampleId: string }) => {
    const fd = new FormData();
    if ("file" in input) fd.append("file", input.file);
    else fd.append("sample_id", input.sampleId);
    return request<Inspiration>("/inspirations", { method: "POST", body: fd });
  },

  generateLooks: (inspirationId: string, preferences: StylePreferences) =>
    request<Generation>("/looks/generate", {
      method: "POST",
      ...json({ inspiration_id: inspirationId, preferences }),
    }),
  refineLooks: (generationId: string, instruction: string, lookId?: string) =>
    request<Generation>("/looks/refine", {
      method: "POST",
      ...json({ generation_id: generationId, instruction, look_id: lookId }),
    }),
  swapItem: (generationId: string, lookId: string, oldGarmentId: string, newGarmentId: string) =>
    request<Generation>("/looks/swap", {
      method: "POST",
      ...json({
        generation_id: generationId,
        look_id: lookId,
        old_garment_id: oldGarmentId,
        new_garment_id: newGarmentId,
      }),
    }),

  listSaved: () => request<SavedLook[]>("/looks/saved"),
  saveLook: (generationId: string, lookId: string) =>
    request<SavedLook>("/looks/saved", {
      method: "POST",
      ...json({ generation_id: generationId, look_id: lookId }),
    }),
  deleteSaved: (id: string) => request<void>(`/looks/saved/${id}`, { method: "DELETE" }),
};

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  return "Something unexpected happened. Please try again.";
}
