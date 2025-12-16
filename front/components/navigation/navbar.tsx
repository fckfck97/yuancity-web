// components/Navbar.tsx
import Image from "next/image";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b-4 border-black shadow-brutal-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Marca */}
          <div className="flex items-center space-x-2">
            <Image
              src="/logo.png"
              alt="Logo de GreenCloset"
              width={48}
              height={48}
              className="h-12 w-12"
              priority
            />
            <span className="text-xl font-bold text-black">
              GreenCloset
            </span>
          </div>

          {/* Navegación */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#about" className="text-black hover:text-main font-medium">
              Quienes Somos
            </a>
            <a href="#como-funciona" className="text-black hover:text-main font-medium">
              Como Funciona
            </a>
            <a href="#join" className="text-black hover:text-main font-medium">
              Únete
            </a>

            {/* CTA descarga app */}
            <a
              href="#descargar-app" // ancla a tu sección de descarga
              className="bg-main text-main-foreground px-6 py-2 border-2 border-black shadow-brutal hover:shadow-brutal-lg transition-all font-bold"
            >
              DESCARGAR LA APP
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}
