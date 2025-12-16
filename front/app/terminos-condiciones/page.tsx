// app/terminos-condiciones/page.tsx
import Footer from '@/components/navigation/footer';
import Navbar from '@/components/navigation/navbar';
import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: `Términos y Condiciones`,
  description: 'Términos y condiciones de uso de la plataforma GreenCloset Shop (Ovalcampus) y EULA.',
};

export default function TerminosCondicionesPage() {
  const ultimaActualizacion = '11 de noviembre de 2025';

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 py-16 md:py-24 max-w-5xl space-y-10">
        {/* CARD: Header */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-10 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1">
            <div className="bg-chart-1 border-4 border-border shadow-brutal-colored-lg inline-block px-4 py-2 -rotate-1 mb-6">
              <h1 className="text-3xl md:text-5xl font-black tracking-tight text-main-foreground">
                Términos y Condiciones de Uso
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium mb-2">
              Acuerdo de Licencia de Usuario Final (EULA)
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-chart-4 border-2 border-border text-main-foreground px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">Última actualización: {ultimaActualizacion}</span>
            </div>
          </div>
        </section>

        {/* 1. Introducción */}
        <section className="bg-chart-2 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">1</span>
            Introducción
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Bienvenido a <strong className="text-main-foreground">GreenCloset Shop</strong>, una plataforma de <strong className="text-main-foreground">Ovalcampus</strong> para
            explorar menús, realizar pedidos y pagar de forma segura a restaurantes asociados. Al usar nuestro sitio
            web o aplicación móvil, usted acepta estos Términos y Condiciones de Uso y el <strong>EULA</strong>. Si no está
            de acuerdo, no utilice GreenCloset Shop.
          </p>
        </section>

        {/* 2. Definiciones */}
        <section className="bg-chart-3 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">2</span>
            Definiciones
          </h2>
          <ul className="ml-12 space-y-3">
            {[
              ['Usuario/Cliente', 'Persona que crea una cuenta o utiliza GreenCloset Shop.'],
              ['Restaurante Socio', 'Establecimiento que recibe y gestiona pedidos vía GreenCloset Shop.'],
              ['Pedido', 'Solicitud de productos/servicios realizada por el Usuario al Restaurante Socio.'],
              ['Plataforma', 'Sitio web y app móvil de GreenCloset Shop.'],
              ['Servicios', 'Funcionalidades provistas por GreenCloset Shop (exploración de menús, pedidos, pagos, soporte, etc.).'],
            ].map(([term, desc], i) => (
              <li key={i} className="bg-white border-2 border-border p-4 shadow-brutal flex gap-3">
                <span className="font-bold text-main-foreground">→</span>
                <span className="text-foreground">
                  <strong className="text-foreground">{term}:</strong> {desc}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* 3. Registro y seguridad */}
        <section className="bg-chart-4 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">3</span>
            Registro y Seguridad de la Cuenta
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            <li className="flex items-start gap-3"><span className="mt-1.5">🔐</span><span>Debe proporcionar información veraz y mantenerla actualizada.</span></li>
            <li className="flex items-start gap-3"><span className="mt-1.5">🔒</span><span>Usted es responsable de sus credenciales y actividad.</span></li>
            <li className="flex items-start gap-3"><span className="mt-1.5">👤</span><span>Mayor de 18 años o autorización parental conforme a la ley.</span></li>
            <li className="flex items-start gap-3"><span className="mt-1.5">⚠️</span><span>Podemos suspender/cerrar cuentas por incumplimientos o fraude.</span></li>
          </ul>
        </section>

        {/* 4. Uso de la plataforma */}
        <section className="bg-chart-1 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">4</span>
            Uso de la Plataforma
          </h2>
          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">4.1 Uso permitido</h3>
              <ul className="space-y-2 text-foreground/90 ml-1">
                <li>• Consultar menús, disponibilidad y precios.</li>
                <li>• Realizar pedidos y pagos de forma segura.</li>
                <li>• Recibir actualizaciones del pedido y soporte.</li>
              </ul>
            </div>
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">4.2 Uso prohibido</h3>
              <ul className="space-y-2 text-foreground/90 ml-1">
                <li>• Pedidos fraudulentos o que perturben la operación.</li>
                <li>• Acceder/interferir con sistemas o datos no autorizados.</li>
                <li>• Publicar contenido ilegal, ofensivo o infractor.</li>
              </ul>
            </div>
          </div>
        </section>

        {/* 5. Pedidos, precios y pagos */}
        <section className="bg-chart-2 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">5</span>
            Pedidos, Precios y Pagos
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">💰 Los precios, disponibilidad y tiempos dependen del Restaurante Socio.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">✅ El pedido se confirma al ser aceptado; tiempos estimados.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">💳 Pagos con proveedores certificados; pueden aplicar impuestos/tasas/propinas.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">📄 Comprobantes/facturas según normativa aplicable.</li>
          </ul>
        </section>

        {/* 6. Cancelaciones y reembolsos */}
        <section className="bg-chart-3 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">6</span>
            Cancelaciones y Reembolsos
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">• Dependen del Restaurante Socio y de la ley aplicable.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">• Si el restaurante cancela, reembolso conforme al flujo del proveedor de pago.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">• Compras en App Store/Google Play se rigen por sus políticas.</li>
          </ul>
        </section>

        {/* 7. Suscripciones e IAP */}
        <section className="bg-chart-4 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">7</span>
            Suscripciones y Compras Dentro de la App (IAP)
          </h2>
          <div className="ml-12 space-y-4 text-foreground">
            <p className="leading-relaxed">
              Si GreenCloset Shop ofrece suscripciones o IAP, verás precios, beneficios y períodos antes del pago. Las suscripciones pueden
              ser <strong>auto-renovables</strong> a menos que se cancelen con 24h de antelación al final del período. Gestión/cancelación
              desde la tienda correspondiente. <em className="font-bold">Restaurar compras</em> estará disponible cuando aplique.
            </p>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              Para iOS, también aplica el{' '}
              <a
                href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
                target="_blank"
                rel="noreferrer"
                className="underline text-main-foreground font-bold"
              >
                Apple Standard EULA
              </a>.
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <strong>Apple y Google no son parte</strong> de este contrato entre usted y Ovalcampus respecto de GreenCloset Shop; no son responsables
              del soporte o mantenimiento del servicio.
            </div>
          </div>
        </section>

        {/* 8. Calificaciones y contenido */}
        <section className="bg-chart-1 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">8</span>
            Calificaciones, Reseñas y Contenido del Usuario
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">⭐ El contenido debe ser veraz, lícito y respetuoso.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">📝 Concedes a GreenCloset Shop licencia no exclusiva para usar/reproducir el contenido en la plataforma.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">🛡️ Podemos moderar o retirar contenido que incumpla estos términos.</li>
          </ul>
        </section>

        {/* 9. Propiedad intelectual */}
        <section className="bg-chart-2 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">9</span>
            Propiedad Intelectual y Licencia
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            GreenCloset Shop, su software, marcas, diseños y contenidos son propiedad de Ovalcampus o sus licenciantes. Recibes una licencia
            limitada, personal, no exclusiva e intransferible para usar la app con el único fin de interactuar con Restaurantes Socios
            conforme a estos términos.
          </p>
        </section>

        {/* 10. Dispositivos y servicios */}
        <section className="bg-chart-3 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">10</span>
            Dispositivos, Permisos y Servicios de Terceros
          </h2>
          <ul className="ml-12 space-y-3">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">📱 La app puede solicitar permisos (ubicación, cámara, notificaciones).</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">🔗 Integramos proveedores (pagos, mensajería, hosting, analítica) con sus propios términos.</li>
          </ul>
        </section>

        {/* 11. Garantías y limitación */}
        <section className="bg-chart-4 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">11</span>
            Garantías y Limitación de Responsabilidad
          </h2>
          <ul className="ml-12 space-y-3">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ Servicio “tal cual” y “según disponibilidad”.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ No respondemos por la calidad/disponibilidad/entrega de los Restaurantes Socios.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ La responsabilidad se limita al importe pagado en la transacción de la reclamación.</li>
          </ul>
        </section>

        {/* 12. Indemnidad */}
        <section className="bg-chart-1 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">12</span>
            Indemnidad
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Usted acepta mantener indemne a Ovalcampus/GreenCloset Shop frente a reclamaciones de terceros derivadas del uso indebido de la
            plataforma, incumplimientos de estos términos o violaciones de derechos de terceros.
          </p>
        </section>

        {/* 13. Suspensión y terminación */}
        <section className="bg-chart-2 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">13</span>
            Suspensión y Terminación
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Podemos suspender o terminar el acceso por incumplimientos graves, fraude, riesgos de seguridad o requerimientos legales.
            Usted puede dejar de usar el servicio en cualquier momento.
          </p>
        </section>

        {/* 14. Ley aplicable */}
        <section className="bg-chart-3 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">14</span>
            Ley Aplicable y Resolución de Disputas
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Estos términos se rigen por las leyes de <strong>Colombia</strong>. Las disputas se resolverán preferentemente por negociación; en su defecto,
            ante la jurisdicción competente.
          </p>
        </section>

        {/* 15. Cambios */}
        <section className="bg-chart-4 border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">15</span>
            Cambios a estos Términos/EULA
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Podemos actualizar estos Términos/EULA por cambios de servicio o exigencias legales. Notificaremos cambios sustanciales
            en la app o por correo. Revisa la fecha de “Última actualización”.
          </p>
        </section>

        {/* 16. Privacidad y docs */}
        <section className="bg-chart-1 border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-main-foreground mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">16</span>
            Privacidad y Documentos Relacionados
          </h2>
          <div className="ml-12 space-y-3 text-foreground">
            <p>
              El uso de la plataforma también se rige por nuestra{' '}
              <Link href="/politica-privacidad" className="text-main-foreground font-bold underline">
                Política de Privacidad
              </Link>.
            </p>
            <p>
              Para iOS, consulta el{' '}
              <a
                href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
                target="_blank"
                rel="noreferrer"
                className="text-main-foreground font-bold underline"
              >
                Apple Standard EULA
              </a>.
            </p>
          </div>
        </section>

        {/* 17. Contacto */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-white text-black font-black text-xl border-2 border-border">17</span>
            Contacto
          </h2>
          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-white/10 p-5 shadow-brutal border-2 border-white/20">
              <p className="font-bold mb-2 text-lg">📧 Email Legal</p>
              <a href="mailto:legal@GreenCloset Shop.com.co" className="underline text-white">
                legal@GreenCloset Shop.com.co
              </a>
            </div>
            <div className="bg-white/10 p-5 shadow-brutal border-2 border-white/20">
              <p className="font-bold mb-2 text-lg">📍 Dirección (Ovalcampus USA)</p>
              <p className="text-white/90 leading-relaxed">
                1129 N Saint Lucas St<br />Allentown, PA 18104<br />Estados Unidos
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
