// components/About.tsx
import Image from "next/image";

export default function About() {
  return (
    <section id="about" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Texto */}
          <div>
            <div className="bg-chart-1 border-4 border-border shadow-brutal-colored-lg p-4 inline-block mb-8 -rotate-1">
              <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
                QUIÉNES SOMOS
              </h2>
            </div>

            <div className="space-y-6">
              <p className="text-xl font-medium text-foreground">
                Somos <span className="font-bold">GreenCloset</span>: donde comprar y vender ropa de segunda mano nunca fue tan fácil.
              </p>

              <p className="text-lg font-medium text-foreground">
                Creamos un espacio bonito, organizado y seguro para que puedas dar una segunda vida a tus prendas,
                descubrir estilos únicos y ahorrar mientras reduces el impacto ambiental.
              </p>

              <p className="text-lg font-medium text-foreground">
                Nuestra misión: impulsar la moda circular con una experiencia simple, confiable y pensada para todos.
              </p>

              <div className="bg-chart-4 border-4 border-border shadow-brutal-xl p-6">
                <p className="text-main-foreground font-bold text-lg">
                  Compra y vende fácil • Ahorra dinero • Reduce residuos
                </p>
              </div>
            </div>
          </div>

          {/* Imagen */}
          <div className="relative">
            <div className="bg-black border-4 border-border shadow-brutal-3xl p-8 rotate-2 hover:shadow-[24px_24px_0px_0px_var(--color-border)] transition-all duration-300">
              <Image
                src="/img/about.jpg" // cambia por tu imagen real si usas otra
                alt="Comunidad GreenCloset comprando y vendiendo moda circular"
                width={500}
                height={400}
                className="border-2 border-border"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
