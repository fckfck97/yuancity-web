// components/Hero.tsx
'use client';

import Image from "next/image";
import { useTranslation } from 'react-i18next';
export default function Hero() {
  const { t } = useTranslation();
  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden" id="inicio">
      {/* Fondo con imagen */}
      <div className="absolute inset-0">
        <Image
          src="/img/hero.jpg"
          alt={t('home.hero.altText')}
          fill
          className="object-cover"
          priority
        />
        {/* Capa oscura suave */}
        <div className="absolute inset-0 bg-black/40" />
        {/* Gradiente para lectura del texto */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        {/* Mini “máscara” sutil sobre la imagen */}
        <div
          className="absolute inset-0 pointer-events-none opacity-20"
          style={{
            backgroundImage:
              "radial-gradient(rgba(255,255,255,0.08) 1px, transparent 1px)",
            backgroundSize: "12px 12px",
          }}
        />
      </div>

      {/* Contenido */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <div className="border-4 border-border shadow-brutal-3xl p-8 -rotate-1">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-4 leading-none">
              {t('home.hero.discoverInYuanCity')}
            </h1>
            <h2 className="text-4xl md:text-6xl font-bold text-white leading-none">
              {t('home.hero.closeToYou')}
            </h2>
          </div>
        </div>

        <div>
          <div className="border-4 border-border shadow-brutal-2xl p-6 rotate-1">
            <p className="text-lg md:text-2xl text-white/95 font-medium mb-6">
              {t('home.hero.discoverThousandsOfExclusiveProducts')} <span className="font-bold">{t('home.hero.yuanCity')}</span>.
              {t('home.hero.qualityAndVarietyAtYourFingertips')}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <a
                href="#descargar-app"
                className="bg-chart-2 text-white px-8 py-4 border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all font-bold text-lg"
              >
                {t('home.hero.downloadApp')}
              </a>
              <a
                href="#como-funciona"
                className="bg-white text-black px-8 py-4 border-4 border-black shadow-brutal hover:shadow-brutal-lg transition-all font-bold text-lg"
              >
                {t('home.hero.howItWorks')}
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
