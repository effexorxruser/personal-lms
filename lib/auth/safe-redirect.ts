const DEFAULT_POST_LOGIN_PATH = "/dashboard";

/**
 * Allow only same-origin relative paths (no protocol-relative or external URLs).
 */
export function sanitizePostLoginPath(
  next: string | null | undefined,
  fallback = DEFAULT_POST_LOGIN_PATH,
): string {
  if (!next) {
    return fallback;
  }

  const trimmed = next.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) {
    return fallback;
  }

  if (trimmed.includes("://") || trimmed.includes("\\")) {
    return fallback;
  }

  try {
    const url = new URL(trimmed, "http://localhost");
    if (url.origin !== "http://localhost") {
      return fallback;
    }
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return fallback;
  }
}
