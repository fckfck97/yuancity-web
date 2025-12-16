import type { Metadata } from "next";
import { notFound } from "next/navigation";
import DeepLinkLauncher from "@/components/DeepLinkLauncher";
import { DownloadSection } from "@/components/home/DownloadSection";
import {
  APP_NAME,
  APP_SCHEME,
  APP_STORE_URL,
  PLAY_STORE_URL,
  SITE_BASE_URL,
  buildAppLinkMetadata,
} from "@/lib/mobileApp";
import Navbar from "@/components/navigation/navbar";
import Footer from "@/components/navigation/footer";

type Params = { id: string };

type SocialProduct = {
  id: string;
  name: string;
  price?: number | string | null;
  first_image?: string | null;
};

interface SocialProfile {
  id: string;
  email?: string | null;
  full_name?: string | null;
  bio?: string | null;
  city?: string | null;
  department?: string | null;
  followers_count?: number;
  following_count?: number;
  posts_count?: number;
  avatar_url?: string | null;
  cover_url?: string | null;
  products?: SocialProduct[] | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://greencloset.shop";
const SITE_ORIGIN = SITE_BASE_URL.replace(/\/$/, "");

async function fetchSocialProfile(
  identifier: string
): Promise<SocialProfile | null> {
  if (!identifier) return null;
  try {
    const res = await fetch(
      `${API_URL}/api/social/profile/${encodeURIComponent(identifier)}/`,
      {
        cache: "no-store",
        next: { revalidate: 0 },
      }
    );
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error("Error fetching profile", error);
    return null;
  }
}

const formatCompactNumber = (value?: number) => {
  if (value === undefined || value === null) return "0";
  try {
    return new Intl.NumberFormat("es-CO", {
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(value);
  } catch {
    return String(value);
  }
};

const currencyFormatter = (value?: number | string | null) => {
  if (value === undefined || value === null) return null;
  const amount = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(amount)) return null;
  try {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `$${amount}`;
  }
};

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const profile = await fetchSocialProfile(params.id);
  if (!profile) {
    return {
      title: "Perfil no disponible | GreenCloset",
    };
  }

  const canonicalUrl = `${SITE_ORIGIN}/u/${encodeURIComponent(params.id)}`;
  const deepLink = `${APP_SCHEME}://u/${encodeURIComponent(params.id)}`;
  const title = `${
    profile.full_name ?? profile.email ?? "Perfil"
  } | ${APP_NAME}`;
  const description =
    profile.bio?.trim() ??
    `Sigue a ${
      profile.full_name ?? profile.email ?? "esta vendedora"
    } y descubre sus prendas destacadas.`;
  const ogImage =
    profile.cover_url ||
    profile.avatar_url ||
    profile.products?.[0]?.first_image ||
    "/banner.png";

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      images: [ogImage],
      type: "profile",
      url: canonicalUrl,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [ogImage],
    },
    other: buildAppLinkMetadata(deepLink, canonicalUrl),
  };
}

export default async function PublicProfileFallback({
  params,
}: {
  params: Params;
}) {
  const profile = await fetchSocialProfile(params.id);
  if (!profile) {
    notFound();
  }

  const deepLink = `${APP_SCHEME}://u/${encodeURIComponent(params.id)}`;
  const canonicalUrl = `${SITE_ORIGIN}/u/${encodeURIComponent(params.id)}`;
  const displayName =
    profile.full_name?.trim() || profile.email || "Vendedora GreenCloset";
  const emailDisplay = profile.email || "";
  const location = profile.city || profile.department;

  return (
    <div className="min-h-screen bg-background px-4 py-16">
      <Navbar />
      <div className="mx-auto max-w-5xl">
        <div className="bg-chart-1 border-4 border-border shadow-brutal-3xl overflow-hidden rounded-3xl rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1 relative h-72 md:h-80 bg-gradient-to-r from-gray-900 to-emerald-700">
            {profile.cover_url && (
              <div className="absolute inset-0">
                <img
                  src={profile.cover_url}
                  alt={`Portada de ${displayName}`}
                  className="h-full w-full object-cover opacity-80"
                />
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
            <div className="absolute bottom-6 left-6 flex items-end gap-4 text-white md:bottom-10 md:left-10">
              <div className="h-24 w-24 overflow-hidden rounded-full border-4 border-white/40 bg-white/20">
                {profile.avatar_url ? (
                  <img
                    src={profile.avatar_url}
                    alt={displayName}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-3xl font-bold text-white">
                    {displayName
                      .split(" ")
                      .filter(Boolean)
                      .map((part) => part[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </div>
                )}
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/60">
                  Perfil en la app
                </p>
                <h1 className="mt-2 text-3xl font-bold md:text-4xl">
                  {displayName}
                </h1>
                {emailDisplay && <p className="text-white/80">{emailDisplay}</p>}
                {location && (
                  <p className="text-sm text-white/80">{location}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8 px-6 py-10 md:px-10">
          <div className="grid gap-4 rounded-2xl border-4 border-border bg-chart-3 p-6 text-center md:grid-cols-3 rotate-1">
            <div className="-rotate-1 grid grid-cols-3 gap-4">
              <div className="p-2">
                <p className="text-sm font-semibold uppercase tracking-widest text-gray-500">
                  Seguidores
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatCompactNumber(profile.followers_count)}
                </p>
              </div>
              <div className="p-2">
                <p className="text-sm font-semibold uppercase tracking-widest text-gray-500">
                  Siguiendo
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatCompactNumber(profile.following_count)}
                </p>
              </div>
              <div className="p-2">
                <p className="text-sm font-semibold uppercase tracking-widest text-gray-500">
                  Prendas
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {formatCompactNumber(profile.posts_count)}
                </p>
              </div>
            </div>
          </div>

          {profile.bio && (
            <div className="bg-chart-2 border-4 border-border shadow-brutal-2xl p-6 rotate-1">
              <div className="-rotate-1">
                <h2 className="text-2xl font-semibold text-main-foreground">
                  Descripción
                </h2>
                <p className="mt-3 whitespace-pre-line text-base leading-relaxed text-foreground">
                  {profile.bio}
                </p>
              </div>
            </div>
          )}

          {Array.isArray(profile.products) && profile.products.length > 0 && (
            <div className="bg-chart-4 border-4 border-border shadow-brutal-2xl p-6 rotate-1">
              <div className="-rotate-1">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold text-main-foreground">
                    Prendas destacadas
                  </h2>
                  <p className="text-sm text-foreground/70">
                    Solo disponibles dentro de la app
                  </p>
                </div>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {(profile.products ?? []).slice(0, 6).map((product) => (
                    <div
                      key={product.id}
                      className="overflow-hidden rounded-2xl border-2 border-border bg-white shadow-sm"
                    >
                      {product.first_image && (
                        <div className="h-40 w-full bg-gray-100">
                          <img
                            src={product.first_image}
                            alt={product.name}
                            className="h-full w-full object-cover"
                          />
                        </div>
                      )}
                      <div className="p-4">
                        <p className="font-semibold text-gray-900">
                          {product.name}
                        </p>
                        <p className="text-sm text-emerald-600">
                          {currencyFormatter(product.price) ?? "Consultar"}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="bg-chart-2 border-4 border-border p-6 rounded-2xl shadow-brutal rotate-1">
            <div className="-rotate-1">
              <DeepLinkLauncher
                deepLink={deepLink}
                appStoreUrl={APP_STORE_URL}
                playStoreUrl={PLAY_STORE_URL}
                autolaunch
                label="Abrir este perfil en la app"
              />
            </div>
          </div>

          <div className="relative text-center">
            <div className="absolute inset-x-0 top-1/2 border-t border-gray-200" />
            <span className="relative bg-white px-4 text-sm font-medium text-gray-500">
              ¿No tienes la app?
            </span>
          </div>

          <DownloadSection deep />

          <div className="border-t border-gray-100 pt-6 text-center text-sm text-foreground/80">
            <p>
              Explora la experiencia completa desde la aplicación móvil de{" "}
              {APP_NAME}.
            </p>
            <a href={canonicalUrl} className="text-emerald-600 hover:underline">
              {canonicalUrl}
            </a>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
