// components/DownloadApp.tsx
"use client";

import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";
import { FaApple, FaGooglePlay } from "react-icons/fa";
import { ShoppingBag, Globe, ShieldCheck, Truck } from "lucide-react";
import { useTranslation } from 'react-i18next';
function PhoneCarousel() {
  const slides = useMemo(
    () => Array.from({ length: 4 }, (_, i) => `/img/movil/${i + 1}.png`),
    []
  );

  const [index, setIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const drag = useRef<{ active: boolean; startX: number; lastX: number }>({
    active: false,
    startX: 0,
    lastX: 0,
  });

  const goTo = (i: number) => setIndex((i + slides.length) % slides.length);

  // autoplay suave (opcional)
  useEffect(() => {
    if (isPaused) return;
    const t = setInterval(() => {
      setIndex((v) => (v + 1) % slides.length);
    }, 3500);
    return () => clearInterval(t);
  }, [isPaused, slides.length]);

  // swipe sin desmaquetar
  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    drag.current.active = true;
    drag.current.startX = e.clientX;
    drag.current.lastX = e.clientX;
    setIsPaused(true);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!drag.current.active) return;
    drag.current.lastX = e.clientX;
  };

  const onPointerUp = () => {
    if (!drag.current.active) return;
    drag.current.active = false;

    const dx = drag.current.lastX - drag.current.startX;
    const threshold = 40;

    if (dx > threshold) goTo(index - 1);
    else if (dx < -threshold) goTo(index + 1);

    window.setTimeout(() => setIsPaused(false), 1200);
  };

  return (
    <div
      className="w-full flex flex-col items-center justify-center"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Viewport con tamaño original */}
      <div
        className="relative overflow-hidden border-2 border-border rounded-2xl bg-black/5 touch-pan-y"
        style={{ width: 260, height: 520 }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        <div
          className="flex transition-transform duration-500 ease-out"
          style={{ transform: `translateX(-${index * 100}%)` }}
        >
          {slides.map((src, i) => (
            <div
              key={src}
              className="min-w-full flex items-center justify-center"
              style={{ width: 260, height: 520 }}
            >
              <Image
                src={src}
                alt={`Vista previa de la app YuanCity ${i + 1}`}
                width={260}
                height={520}
                className="rounded-2xl"
                priority={i === 0}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Dots (único control) */}
      <div className="mt-4 flex items-center justify-center gap-2">
        {slides.map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => {
              setIsPaused(true);
              goTo(i);
              window.setTimeout(() => setIsPaused(false), 1200);
            }}
            className={[
              "h-3 w-3 border-2 border-border shadow-brutal transition-all",
              i === index ? "bg-chart-5 scale-110" : "bg-white hover:scale-110",
            ].join(" ")}
            aria-label={`Ir a la imagen ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}

export default function DownloadApp() {
  const { t } = useTranslation();
  return (
    <section id="descargar-app" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Título */}
        <div>
          <div className="bg-chart-5 border-4 border-border shadow-brutal-colored p-4 inline-block mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
              {t('home.DownloadApp.title')}
            </h2>
          </div>
        </div>

        {/* Fila superior: Descarga + Mockup (lado a lado) */}
        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Texto + botones */}
          <div className="lg:col-span-1">
            <div className="bg-chart-2 border-4 border-border shadow-brutal-colored-xl p-8 -rotate-1">
              <div className="flex items-center gap-3 mb-4">
                <ShoppingBag className="h-10 w-10 text-white" />
                <h3 className="text-2xl font-bold text-white">{t('home.DownloadApp.purchaseInYuanCity')}</h3>
              </div>
              <p className="text-lg font-medium mb-6 text-white/95">
                {t('home.DownloadApp.purchaseDescription')}
              </p>
              {/* Botones de tiendas */}
              <div className="grid sm:grid-cols-2 gap-4">
                <a
                  href="https://play.google.com/store/apps/details?id=com.ovalcampus.yuancity"
                  target="_blank"
                  rel="noreferrer"
                  className="group bg-white text-black border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all flex items-center justify-center gap-3 px-6 py-3 font-bold"
                  aria-label="Descargar en Google Play"
                >
                  <span className="shrink-0 leading-none text-2xl md:text-3xl">
                    <FaGooglePlay />
                  </span>
                  <span>{t('home.DownloadApp.googlePlay')}</span>
                </a>

                <a
                  href="https://apps.apple.com/co/app/yuan-city/id6755722239?l=es"
                  target="_blank"
                  rel="noreferrer"
                  className="group bg-white text-black border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all flex items-center justify-center gap-3 px-6 py-3 font-bold"
                  aria-label="Descargar en App Store"
                >
                  <span className="shrink-0 leading-none text-2xl md:text-3xl">
                    <FaApple />
                  </span>
                  <span>{t('home.DownloadApp.appStore')}</span>
                </a>
              </div>
            </div>

            {/* Aviso pequeño */}
            <p className="mt-10 text-sm text-foreground/70">
              {t('home.DownloadApp.storeNotice')}
            </p>
          </div>

          {/* Carousel de celular */}
          <div className="bg-secondary-background border-4 border-border shadow-brutal-2xl p-6 flex items-center justify-center rotate-1">
            <PhoneCarousel />
          </div>
        </div>

        {/* Fila inferior: beneficios */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          {[
            {
              title: t('home.DownloadApp.globalCatalog'),
              desc: t('home.DownloadApp.globalCatalogDesc'),
              icon: Globe
            },
            {
              title: t('home.DownloadApp.securePurchase'),
              desc: t('home.DownloadApp.securePurchaseDesc'),
              icon: ShieldCheck
            },
            {
              title: t('home.DownloadApp.guaranteedShipping'),
              desc: t('home.DownloadApp.guaranteedShippingDesc'),
              icon: Truck
            },
          ].map((b, i) => (
            <div key={i} className="bg-black text-white border-4 border-border shadow-brutal p-6 hover:translate-y-[-4px] transition-transform">
              <div className="flex items-center gap-3 mb-3">
                <b.icon className="h-6 w-6 text-white" />
                <h5 className="text-xl font-bold">{b.title}</h5>
              </div>
              <p className="text-white/90 font-medium">{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
