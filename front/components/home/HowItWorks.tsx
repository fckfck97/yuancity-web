// components/HowItWorks.tsx
import { Search, ShoppingBag, CreditCard, Truck } from "lucide-react";

export default function HowItWorks() {
  const steps = [
    {
      title: "Explora y elige",
      desc: "Navega por miles de productos importados de China. Encuentra tecnología, hogar, moda y más.",
      Icon: Search,
    },
    {
      title: "Agrega al carrito",
      desc: "Selecciona tus artículos favoritos y agrégalos a tu carrito de compras de forma sencilla.",
      Icon: ShoppingBag,
    },
    {
      title: "Pago seguro",
      desc: "Realiza tu pago a través de nuestra plataforma protegida con múltiples métodos disponibles.",
      Icon: CreditCard,
    },
    {
      title: "Recibe en casa",
      desc: "Nos encargamos de la logística para que tus productos lleguen seguros a tu puerta. ¡Así de fácil!",
      Icon: Truck,
    },
  ] as const;

  return (
    <section id="como-funciona" className="py-20 bg-secondary-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Título */}
        <div>
          <div className="bg-chart-2 border-4 border-border shadow-brutal-colored-xl p-4 inline-block mb-12 rotate-1">
            <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
              ¿CÓMO FUNCIONA?
            </h2>
          </div>
        </div>

        {/* Pasos */}
        <div className="grid md:grid-cols-4 gap-8">
          {steps.map(({ title, desc, Icon }, i) => (
            <div key={i}>
              <div className="bg-black text-white border-4 border-border shadow-brutal-2xl hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 p-6 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <Icon className="h-6 w-6 text-white" />
                  <h3 className="text-2xl font-bold text-white">{title}</h3>
                </div>
                <p className="font-medium text-white/90">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-10 flex justify-center">
          <a
            href="#descargar-app"
            className="bg-main text-main-foreground px-8 py-3 border-2 border-border shadow-brutal hover:shadow-brutal-lg transition-all font-bold"
          >
            DESCARGAR LA APP
          </a>
        </div>
      </div>
    </section>
  );
}
