'use client';

import { FaApple, FaGooglePlay } from "react-icons/fa";
import { APP_NAME, APP_STORE_URL, PLAY_STORE_URL } from "@/lib/mobileApp";

type DownloadSectionProps = {
  deep?: boolean;
};

export function DownloadSection({ deep = false }: DownloadSectionProps) {
  const openLink = (url: string) => {
    if (typeof window === "undefined") return;
    window.open(url, "_blank");
  };

  const baseTextColor = deep ? "text-gray-800" : "text-gray-100";
  const subTextColor = deep ? "text-gray-600" : "text-gray-300";

  return (
    <section className={`py-16 px-4 md:px-12 ${deep ? "bg-white" : "bg-gradient-to-b from-gray-900 to-black"}`}>
      <div className="mx-auto max-w-5xl text-center">
        <h2 className={`text-3xl md:text-4xl font-bold ${baseTextColor}`}>Descarga {APP_NAME}</h2>
        <p className={`mt-4 text-lg md:text-xl ${subTextColor}`}>
          Compra, vende y sigue tus perfiles favoritos desde la aplicación oficial.
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-5 sm:flex-row">
          <button
            type="button"
            onClick={() => openLink(APP_STORE_URL)}
            className={`flex min-w-[220px] items-center justify-center gap-3 rounded-2xl border px-6 py-4 text-left transition hover:scale-[1.01] ${
              deep
                ? "border-gray-200 bg-white text-gray-900 hover:bg-gray-50"
                : "border-white/30 bg-white/10 text-white hover:bg-white/20"
            }`}
          >
            <FaApple className="text-2xl" />
            <div>
              <p className={`text-xs ${deep ? "text-gray-500" : "text-white/70"}`}>Descargar en</p>
              <p className="text-lg font-semibold">App Store</p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => openLink(PLAY_STORE_URL)}
            className="flex min-w-[220px] items-center justify-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-500/10 px-6 py-4 text-left text-emerald-900 transition hover:scale-[1.01] hover:bg-emerald-500/20"
          >
            <FaGooglePlay className="text-2xl" />
            <div>
              <p className="text-xs text-emerald-800/70">Disponible en</p>
              <p className="text-lg font-semibold text-emerald-900">Google Play</p>
            </div>
          </button>
        </div>

        <p className={`mt-8 text-sm ${subTextColor}`}>
          Funciona con enlaces profundos seguros y notificaciones en tiempo real.
        </p>
      </div>
    </section>
  );
}
