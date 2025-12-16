// components/Hero.tsx
import Image from "next/image";

export default function Hero() {
  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden" id="inicio">
      {/* Fondo con imagen */}
      <div className="absolute inset-0">
        <Image
          src="/img/hero.jpg"
          alt="Personas usando GreenCloset, comprando y vendiendo productos sostenibles"
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
              VÍSTETE VERDE.
            </h1>
            <h2 className="text-4xl md:text-6xl font-bold text-white leading-none">
              VIVE GREENCLOSET.
            </h2>
          </div>
        </div>

        <div>
          <div className="border-4 border-border shadow-brutal-2xl p-6 rotate-1">
            <p className="text-lg md:text-2xl text-white/95 font-medium mb-6">
              Para ver todo en <span className="font-bold">GreenCloset</span>
              descarga la app.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <a
                href="#descargar-app"
                className="bg-chart-2 text-white px-8 py-4 border-4 border-border shadow-brutal hover:shadow-brutal-lg transition-all font-bold text-lg"
              >
                DESCARGAR LA APP
              </a>
              <a
                href="#como-funciona"
                className="bg-white text-black px-8 py-4 border-4 border-black shadow-brutal hover:shadow-brutal-lg transition-all font-bold text-lg"
              >
                ¿CÓMO FUNCIONA?
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
