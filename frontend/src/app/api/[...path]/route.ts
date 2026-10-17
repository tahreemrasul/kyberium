// Same-origin proxy to the Rewear API.
// API_URL is read at runtime, so one frontend image works in every environment and
// no backend URL or credential is ever shipped to the browser.
// When the API runs as a private Cloud Run service, set API_AUDIENCE to its URL: the
// proxy then attaches a Google-signed ID token in X-Serverless-Authorization, leaving
// the user's own Authorization (session) header untouched.

import type { NextRequest } from "next/server";

const FORWARD_REQUEST_HEADERS = ["authorization", "content-type", "accept"];
const FORWARD_RESPONSE_HEADERS = ["content-type", "cache-control", "x-content-type-options", "content-security-policy"];
const TIMEOUT_MS = 170_000;

let idToken: { value: string; expires: number } | null = null;

async function serviceIdToken(audience: string): Promise<string | null> {
  if (idToken && idToken.expires > Date.now()) return idToken.value;
  try {
    const res = await fetch(
      `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=${encodeURIComponent(audience)}`,
      { headers: { "Metadata-Flavor": "Google" }, cache: "no-store" },
    );
    if (!res.ok) return null;
    const value = await res.text();
    idToken = { value, expires: Date.now() + 45 * 60 * 1000 };
    return value;
  } catch {
    return null;
  }
}

function errorResponse(status: number, code: string, message: string) {
  return Response.json({ error: { code, message, retryable: true, details: null } }, { status });
}

async function proxy(req: NextRequest, ctx: RouteContext<"/api/[...path]">) {
  const { path } = await ctx.params;
  const base = (process.env.API_URL ?? "http://localhost:8000").replace(/\/+$/, "");
  const target = `${base}/${path.map(encodeURIComponent).join("/")}${req.nextUrl.search}`;

  const headers = new Headers();
  for (const name of FORWARD_REQUEST_HEADERS) {
    const value = req.headers.get(name);
    if (value) headers.set(name, value);
  }
  const audience = process.env.API_AUDIENCE;
  if (audience) {
    const token = await serviceIdToken(audience);
    if (token) headers.set("X-Serverless-Authorization", `Bearer ${token}`);
  }

  const hasBody = !["GET", "HEAD"].includes(req.method);
  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: req.method,
      headers,
      body: hasBody ? await req.arrayBuffer() : undefined,
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (err) {
    const timedOut = err instanceof Error && err.name === "TimeoutError";
    return timedOut
      ? errorResponse(504, "upstream_timeout", "The stylist took too long to answer. Please try again.")
      : errorResponse(502, "upstream_unavailable", "Rewear's API is unreachable right now. Please try again.");
  }

  const out = new Headers();
  for (const name of FORWARD_RESPONSE_HEADERS) {
    const value = upstream.headers.get(name);
    if (value) out.set(name, value);
  }
  return new Response(upstream.status === 204 ? null : upstream.body, { status: upstream.status, headers: out });
}

export { proxy as DELETE, proxy as GET, proxy as PATCH, proxy as POST };
