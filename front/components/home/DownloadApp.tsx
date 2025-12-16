// components/DownloadApp.tsx
"use client";

import Image from "next/image";
import { useEffect, useMemo, useRef, useState } from "react";
import { FaApple, FaGooglePlay } from "react-icons/fa";

function PhoneCarousel() {
  const slides = useMemo(
    () => Array.from({ length: 6 }, (_, i) => `/img/movil/${i + 1}.png`),
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
                alt={`Vista previa de la app GreenCloset ${i + 1}`}
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
  return (
    <section id="descargar-app" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Título */}
        <div>
          <div className="bg-chart-5 border-4 border-border shadow-brutal-colored p-4 inline-block mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
              DESCARGA LA APP
            </h2>
          </div>
        </div>

        {/* Fila superior: Descarga + Mockup (lado a lado) */}
        <div className="grid md:grid-cols-2 gap-8 items-start">
          {/* Texto + botones (compacto, sin estirar) */}
          <div className="lg:col-span-1">
            <div className="bg-black text-white border-4 border-border shadow-brutal-xl p-8">
              <div className="space-y-4">
                <h3 className="text-2xl font-bold">Compra y vende en GreenCloset</h3>
                <p className="text-white/90 font-medium">
                  Descubre moda de segunda mano, publica tus prendas y cobra con
                  seguridad. Todo desde tu celular.
                </p>
              </div>

              {/* Botones de tiendas (con íconos, manteniendo tus clases) */}
              <div className="mt-8 grid sm:grid-cols-2 gap-4">
                <a
                  href="https://play.google.com/store/apps/details?id=com.ovalcampus.greencloset" // TODO: reemplaza
                  target="_blank"
                  rel="noreferrer"
                  className="group bg-white text-black border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all flex items-center justify-center gap-3 px-6 py-3 font-bold"
                  aria-label="Descargar en Google Play"
                >
                  <span className="shrink-0 leading-none text-2xl md:text-3xl">
                    <FaGooglePlay />
                  </span>
                  <span>Google Play</span>
                </a>

                <a
                  href="https://apps.apple.com/app/idXXXXXXXXX" // TODO: reemplaza
                  target="_blank"
                  rel="noreferrer"
                  className="group bg-white text-black border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all flex items-center justify-center gap-3 px-6 py-3 font-bold"
                  aria-label="Descargar en App Store"
                >
                  <span className="shrink-0 leading-none text-2xl md:text-3xl">
                    <FaApple />
                  </span>
                  <span>App Store</span>
                </a>
              </div>

              {/* Aviso pequeño */}
              <p className="mt-6 text-sm text-white/70">
                ¿No encuentras tu tienda? Próximamente en más regiones.
              </p>
            </div>
          </div>


<div className="bg-secondary-background border-4 border-border shadow-brutal-l p-6 flex items-center justify-center">
            <PhoneCarousel />
          </div>
        </div>

        {/* Fila inferior: beneficios (ocupan todo el ancho) */}
        <div className="mt-12 grid md:grid-cols-3 gap-6">
          {[
            { title: "Publica rápido", desc: "Sube fotos, pon precio y listo." },
            { title: "Compra segura", desc: "Chatea y paga con confianza." },
            { title: "Cobra al entregar", desc: "Confirmamos y liberamos tu pago." },
          ].map((b, i) => (
            <div key={i} className="bg-black text-white border-4 border-border shadow-brutal p-6">
              <h5 className="text-lg font-bold mb-2">{b.title}</h5>
              <p className="text-white/90 font-medium">{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
