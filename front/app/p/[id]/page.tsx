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
import Footer from "@/components/navigation/footer";
import Navbar from "@/components/navigation/navbar";

type Params = { id: string };

type ProductImage = {
  id?: string;
  image?: string;
  alt_text?: string | null;
};

type VendorDetail = {
  full_name?: string | null;
  email?: string | null;
  department?: string | null;
  city?: string | null;
};

interface ProductResponse {
  id: string;
  name: string;
  description?: string | null;
  price?: string | number;
  currency?: string | null;
  created_at?: string | null;
  first_image?: string | null;
  images?: ProductImage[];
  category_detail?: {
    name?: string | null;
  } | null;
  vendor_detail?: VendorDetail | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://yuancity.shop";
const SITE_ORIGIN = SITE_BASE_URL.replace(/\/$/, "");

async function fetchProductById(id: string): Promise<ProductResponse | null> {
  if (!id) return null;

  try {
    const res = await fetch(`${API_URL}/api/products/list/?id=${id}`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error("Error fetching product", error);
    return null;
  }
}

const currencyFormatter = (value?: number | string, currency = "COP") => {
  if (value === undefined || value === null || value === "") return null;
  const amount = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(amount)) return null;
  try {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: currency || "COP",
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `$${amount}`;
  }
};

const dateFormatter = (value?: string | null) => {
  if (!value) return null;
  try {
    return new Intl.DateTimeFormat("es-CO", {
      dateStyle: "long",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return null;
  }
};

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const product = await fetchProductById(params.id);
  if (!product) {
    return {
      title: "Producto no disponible | YuanCity",
    };
  }

  const canonicalUrl = `${SITE_ORIGIN}/p/${encodeURIComponent(params.id)}`;
  const deepLink = `${APP_SCHEME}://p/${encodeURIComponent(params.id)}`;
  const vendorName =
    product.vendor_detail?.full_name?.trim() || product.vendor_detail?.email;
  const title = `${product.name} | ${APP_NAME}`;
  const description =
    product.description?.trim() ??
    `Descubre esta prenda publicada por ${
      vendorName ?? "una vendedora de YuanCity"
    }.`;
  const ogImage =
    product.images?.[0]?.image ?? product.first_image ?? "/banner.png";

  return {
    title,
    description,
    alternates: {
      canonical: canonicalUrl,
    },
    openGraph: {
      title,
      description,
      images: [ogImage],
      type: "product",
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

export default async function ProductDeepLinkPage({
  params,
}: {
  params: Params;
}) {
  const product = await fetchProductById(params.id);
  if (!product) {
    notFound();
  }

  const deepLink = `${APP_SCHEME}://p/${encodeURIComponent(params.id)}`;
  const canonicalUrl = `${SITE_ORIGIN}/p/${encodeURIComponent(params.id)}`;
  const vendorName =
    product.vendor_detail?.full_name?.trim() ||
    product.vendor_detail?.email ||
    "Vendedora YuanCity";
  const vendorInitials =
    vendorName
      .split(" ")
      .filter(Boolean)
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "GC";
  const heroImage =
    product.images?.[0]?.image ?? product.first_image ?? "/banner.png";
  const formattedPrice = currencyFormatter(product.price, product.currency);
  const publishedAt = dateFormatter(product.created_at);

  return (
    <div className="min-h-screen bg-background px-4 py-16">
      <Navbar />
      <div className="mx-auto max-w-5xl">
        <div className="bg-chart-1 border-4 border-border shadow-brutal-3xl overflow-hidden rounded-3xl rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1 relative h-72 w-full bg-gradient-to-r from-gray-900 to-emerald-700 md:h-96">
            {heroImage && (
              <div className="absolute inset-0">
                <img
                  src={heroImage}
                  alt={product.name}
                  className="h-full w-full object-cover opacity-90"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
              </div>
            )}
            <div className="absolute bottom-6 left-6 right-6 text-white md:bottom-10 md:left-10 md:right-10">
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/80">
                Disponible en la app
              </p>
              <h1 className="mt-2 text-3xl font-bold md:text-4xl">
                {product.name}
              </h1>
              <p className="mt-2 max-w-3xl text-sm text-white/80">
                Publicado por {vendorName}. Descubre la historia completa,
                chatea y compra seguro en {APP_NAME}.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-8 px-6 py-10 md:px-10">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-2xl border-4 border-border bg-chart-4 p-5 rotate-1">
              <div className="-rotate-1">
                <p className="text-sm font-semibold uppercase tracking-widest text-foreground/90">
                  Precio
                </p>
                <p className="mt-2 text-3xl font-bold text-emerald-900">
                  {formattedPrice ?? "Consulta en la app"}
                </p>
              </div>
            </div>
            <div className="rounded-2xl border-4 border-border bg-chart-2 p-5 rotate-1">
              <div className="-rotate-1">
                <p className="text-sm font-semibold uppercase tracking-widest text-foreground/90">
                  Categoría
                </p>
                <p className="mt-2 text-2xl font-semibold text-foreground">
                  {product.category_detail?.name ?? "Moda circular"}
                </p>
              </div>
            </div>
            <div className="rounded-2xl border-4 border-border bg-chart-3 p-5 rotate-1">
              <div className="-rotate-1">
                <p className="text-sm font-semibold uppercase tracking-widest text-foreground/90">
                  Publicado
                </p>
                <p className="mt-2 text-xl font-semibold text-foreground">
                  {publishedAt ?? "Disponible recientemente"}
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 rounded-2xl border-4 border-border bg-chart-2 p-6 rotate-1 md:flex-row md:items-center md:gap-6">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-600/10 text-xl font-bold text-emerald-900">
                {vendorInitials}
              </div>
              <div>
                <p className="text-sm uppercase tracking-widest text-gray-500">
                  Vendedora
                </p>
                <p className="text-xl font-semibold text-gray-900">
                  {vendorName}
                </p>
                <p className="text-sm text-gray-600">
                  {product.vendor_detail?.city ??
                    product.vendor_detail?.department ??
                    "Colombia"}
                </p>
              </div>
            </div>
            <div className="flex-1 text-sm text-gray-600">
              Esta prenda solo puede adquirirse desde la app móvil. Conéctate
              con la vendedora, acuerda envío o entrega y paga seguro con la
              protección de {APP_NAME}.
            </div>
          </div>

          {product.description && (
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">
                Descripción
              </h2>
              <p className="mt-3 whitespace-pre-line text-base leading-relaxed text-gray-700">
                {product.description}
              </p>
            </div>
          )}

          <div className="bg-chart-2 border-4 border-border p-6 rounded-2xl shadow-brutal rotate-1">
            <div className="-rotate-1">
              <DeepLinkLauncher
                deepLink={deepLink}
                appStoreUrl={APP_STORE_URL}
                playStoreUrl={PLAY_STORE_URL}
                autolaunch
                label="Ver esta prenda en la app"
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

          <div className="border-t border-gray-100 pt-6 text-center text-sm text-gray-500">
            <p>Este enlace abre la experiencia completa en {APP_NAME}.</p>
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
