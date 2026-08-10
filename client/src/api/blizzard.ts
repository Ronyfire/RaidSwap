import { apiFetch, ApiError } from "./client";
import { getToken } from "./authToken";

const API_URL = import.meta.env.VITE_API_URL;

// Optional integration (#93) — a raid leader without Blizzard credentials
// configured gets a 503 from the backend; callers here get null instead of
// a thrown error, so a missing icon degrades to "no icon" rather than
// breaking the raid plan render.
export async function getClassIcon(classId: number): Promise<string | null> {
  try {
    const { icon_url } = await apiFetch<{ icon_url: string }>(`/api/blizzard/class-icon/${classId}`);
    return icon_url;
  } catch (err) {
    if (err instanceof ApiError) return null;
    throw err;
  }
}

// For the canvas export only (RaidPlanOverlay/raidplanExport) — the live
// overlay uses getClassIcon's plain URL directly, a normal <img src> works
// fine cross-origin. Canvas export doesn't: it needs to read the pixels
// back out, and Blizzard's icon CDN sends no CORS header, so this fetches
// the bytes through our own origin (which does send one) instead.
export async function getClassIconBlobUrl(classId: number): Promise<string | null> {
  const token = getToken();
  const response = await fetch(`${API_URL}/api/blizzard/class-icon/${classId}/image`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) return null;
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}
