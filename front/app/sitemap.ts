import type { MetadataRoute } from "next";
import { SITE_BASE_URL } from "@/lib/mobileApp";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://yuancity.shop";
const siteUrl = SITE_BASE_URL.replace(/\/$/, "");

type ProductListItem = {
  id?: string | number | null;
  updated_at?: string | null;
  modified_at?: string | null;
  created_at?: string | null;
};

function toAbsolute(path: string) {
  return `${siteUrl}${path}`;
}

function toDate(value?: string | null) {
  if (!value) return undefined;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

function parseProductList(payload: unknown): ProductListItem[] {
  if (Array.isArray(payload)) return payload as ProductListItem[];
  if (payload && typeof payload === "object") {
    const maybeResults = (payload as { results?: unknown }).results;
    if (Array.isArray(maybeResults)) return maybeResults as ProductListItem[];
  }
  return [];
}

async function getPublicProductUrls(): Promise<MetadataRoute.Sitemap> {
  try {
    const res = await fetch(`${API_URL}/api/products/list/`, {
      next: { revalidate: 3600 },
    });

    if (!res.ok) return [];
    const data = parseProductList(await res.json());

    const entries: MetadataRoute.Sitemap = [];

    for (const item of data) {
      const id = String(item.id ?? "").trim();
      if (!id) continue;

      entries.push({
        url: toAbsolute(`/p/${encodeURIComponent(id)}`),
        lastModified:
          toDate(item.updated_at) ??
          toDate(item.modified_at) ??
          toDate(item.created_at),
        changeFrequency: "daily",
        priority: 0.7,
      });
    }

    return entries;
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();

  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: toAbsolute("/"),
      lastModified: now,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: toAbsolute("/politicas-privacidad"),
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: toAbsolute("/terminos-condiciones"),
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: toAbsolute("/eliminar-cuenta"),
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.7,
    },
  ];

  const productRoutes = await getPublicProductUrls();

  return [...staticRoutes, ...productRoutes];
}
