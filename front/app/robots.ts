import type { MetadataRoute } from "next";
import { SITE_BASE_URL } from "@/lib/mobileApp";

const siteUrl = SITE_BASE_URL.replace(/\/$/, "");

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/dashboard", "/login", "/unsubscribe"],
      },
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
