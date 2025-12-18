// components/Footer.tsx
"use client";
import { useState } from "react";
import Image from "next/image";
import { Facebook, Instagram, Twitter, Loader2 } from "lucide-react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error" | "">("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    setMessage("");
    setMessageType("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/blog/newsletter/subscribe`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage("¡Te has suscrito exitosamente a nuestro boletín!");
        setMessageType("success");
        setEmail("");
      } else {
        setMessage(data.error || "Error al suscribirse. Inténtalo de nuevo.");
        setMessageType("error");
      }
    } catch {
      setMessage("Error de conexión. Verifica tu conexión a internet.");
      setMessageType("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <footer className="bg-secondary-background border-t-4 border-border py-14">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* GRID 4 columnas en desktop */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Columna 1: Marca */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Image
                src="/logo.png"
                alt="Logo de YuanCity"
                width={32}
                height={32}
                className="h-8 w-8"
              />
              <span className="text-xl font-bold text-foreground">YuanCity</span>
            </div>
            <p className="text-foreground/90 font-medium mb-4 leading-relaxed">
              Información para descargar la app y unirte a nuestra comunidad.
            </p>
            <p className="text-foreground font-medium">
              <a
                href="mailto:contacto@yuancity.com"
                className="underline underline-offset-2 hover:text-main"
              >
                contacto@yuancity.com
              </a>
            </p>
          </div>

          {/* Columna 2: Navegación */}
          <div>
            <h3 className="text-lg font-bold text-foreground mb-4">NAVEGACIÓN</h3>
            <ul className="space-y-2 mb-8">
              <li>
            <a href="#about" className="text-black hover:text-main font-medium">
              Quienes Somos
            </a>
              </li>
              <li>
            <a href="#como-funciona" className="text-black hover:text-main font-medium">
              Como Funciona
            </a>
              </li>
              <li>
            <a href="#join" className="text-black hover:text-main font-medium">
              Únete
            </a>
              </li>

            </ul>
          </div>

          {/* Columna 3: Legal */}
          <div>
            <h3 className="text-lg font-bold text-foreground mb-4">LEGAL</h3>
            <ul className="space-y-2">
              <li>
                <a href="/politicas-privacidad" className="text-foreground hover:text-main font-medium">
                  Políticas de Privacidad
                </a>
              </li>
              <li>
                <a href="/terminos-condiciones" className="text-foreground hover:text-main font-medium">
                  Términos y Condiciones
                </a>
              </li>
              <li>
                <a href="/eliminar-cuenta" className="text-foreground hover:text-main font-medium">
                  Eliminar Cuenta
                </a>
              </li>
            </ul>
          </div>

          {/* Columna 4: Redes + Suscripción */}
          <div>
            <h3 className="text-lg font-bold text-foreground mb-4">SÍGUENOS</h3>
            <div className="flex items-center gap-4 mb-6">
              <a
                href="https://instagram.com/yuancity"
                aria-label="Instagram"
                target="_blank"
                rel="noreferrer"
              >
                <Instagram className="h-6 w-6 text-foreground hover:text-main transition-colors" />
              </a>
              <a
                href="https://facebook.com/yuancity"
                aria-label="Facebook"
                target="_blank"
                rel="noreferrer"
              >
                <Facebook className="h-6 w-6 text-foreground hover:text-main transition-colors" />
              </a>
              <a
                href="https://x.com/yuancity"
                aria-label="Twitter/X"
                target="_blank"
                rel="noreferrer"
              >
                <Twitter className="h-6 w-6 text-foreground hover:text-main transition-colors" />
              </a>
            </div>

            {/* Suscripción: alineada, altura consistente y sombra limpia */}
            <form onSubmit={handleSubmit} className="space-y-3" noValidate>
              <label htmlFor="footer-email" className="sr-only">
                Tu correo electrónico
              </label>
              <div className="flex flex-col sm:flex-row gap-2 w-full">
                <input
                  id="footer-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Tu correo"
                  aria-label="Tu correo electrónico"
                  className="flex-1 h-12 px-4 border-2 border-border bg-background text-foreground font-medium outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-black/20"
                  required
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className="h-12 bg-main text-main-foreground px-6 border-2 border-border shadow-[8px_8px_0px_0px_var(--color-border)] hover:shadow-[12px_12px_0px_0px_var(--color-border)] transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center whitespace-nowrap"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ENVIANDO...
                    </>
                  ) : (
                    "SUSCRIBIRME"
                  )}
                </button>
              </div>

              {message && (
                <p
                  role="status"
                  className={`text-sm font-medium ${
                    messageType === "success"
                      ? "text-green-600"
                      : messageType === "error"
                      ? "text-red-600"
                      : "text-foreground/80"
                  }`}
                >
                  {message}
                </p>
              )}
            </form>
          </div>
        </div>

        {/* Línea inferior opcional */}
        <div className="mt-10 pt-6 border-t-2 border-border/60 text-xs text-foreground/70 text-center">
          © {new Date().getFullYear()} YuanCity · Todos los derechos reservados
        </div>
      </div>
    </footer>
  );
}
