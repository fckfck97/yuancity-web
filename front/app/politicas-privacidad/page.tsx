// app/legal/politica-privacidad/yuancity/page.tsx
import Footer from '@/components/navigation/footer';
import Navbar from '@/components/navigation/navbar';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: `Política de Privacidad - YuanCity`,
  description: 'Política de privacidad y tratamiento de datos personales de YuanCity (Ovalcampus).',
};

export default function PoliticaPrivacidadYuanCityPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 py-16 md:py-24 max-w-5xl space-y-10">
        {/* CARD: Header */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-10 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1">
            <div className="bg-main border-4 border-border shadow-brutal-colored-lg inline-block px-4 py-2 -rotate-1 mb-6">
              <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white">
                Política de Privacidad — YuanCity
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium">
              Tu privacidad es esencial para nosotros
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-main border-2 border-border text-white px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">Última actualización: 11 de noviembre de 2025</span>
            </div>
          </div>
        </section>

        {/* CARD: Intro */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4">INTRO</h2>
          <p className="text-lg leading-relaxed text-white">
            <strong className="text-white">YuanCity</strong>, producto de <strong className="text-white">Ovalcampus</strong>, es una plataforma para
            adquirir productos importados. Esta Política explica cómo recopilamos, usamos, compartimos, almacenamos y protegemos tus datos.
          </p>
          <p className="text-base leading-relaxed text-white mt-4">
            Operamos inicialmente en Colombia y cumplimos la <strong>Ley 1581 de 2012</strong> y el régimen de <strong>Habeas Data</strong>. Cuando corresponda, aplicamos principios del <strong>GDPR</strong> (UE) y <strong>CCPA</strong> (California).
          </p>
        </section>

        {/* CARD 1: Responsable */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">1</span>
            RESPONSABLE DEL TRATAMIENTO
          </h2>
          <div className="ml-12 space-y-3">
            <p className="text-white leading-relaxed">
              <strong>Ovalcampus / YuanCity</strong><br />
              <span className="text-white/80">1129 N Saint Lucas St, Allentown, PA 18104, Estados Unidos</span>
            </p>
            <p className="text-white">
              <strong>Contacto:</strong>{' '}
              <a href="mailto:contacto@yuancity.com" className="text-white font-semibold underline">
                contacto@yuancity.com
              </a>
            </p>
          </div>
        </section>

        {/* CARD 2: Información que Recopilamos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">2</span>
            INFORMACIÓN QUE RECOPILAMOS
          </h2>

          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-black text-white border-2 border-border p-6 shadow-brutal-2xl">
              <h3 className="text-xl font-black mb-3">2.1 Cuenta y perfil</h3>
              <ul className="space-y-2 text-white/90">
                <li>• Nombre, correo electrónico, número de teléfono.</li>
                <li>• Foto de perfil y preferencias.</li>
                <li>• Documento para facturación (cuando aplique).</li>
              </ul>
            </div>

            <div className="bg-black text-white border-2 border-border p-6 shadow-brutal-2xl">
              <h3 className="text-xl font-black mb-3">2.2 Publicaciones y transacciones</h3>
              <ul className="space-y-2 text-white/90">
                <li>• Fotos y descripciones de productos, precios, categorías y estado.</li>
                <li>• Mensajes/chats de soporte y consultas.</li>
                <li>• Pedidos, envíos y confirmaciones de entrega.</li>
                <li>• Pagos (no almacenamos números completos de tarjeta).</li>
              </ul>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">2.3 Datos técnicos y de uso</h3>
              <ul className="space-y-2 text-foreground/90">
                <li>• IP, dispositivo/navegador, SO, identificadores de app.</li>
                <li>• Métricas de rendimiento, eventos, fallos y seguridad.</li>
              </ul>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">2.4 Ubicación</h3>
              <ul className="space-y-2 text-foreground/90">
                <li>• Ubicación aproximada (con tu consentimiento).</li>
                <li>• Dirección de envío para completar transacciones.</li>
              </ul>
            </div>

            <div className="md:col-span-2 bg-black border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-white mb-2">2.5 Moderación y confianza</h3>
              <p className="text-white/90">
                Verificación de anuncios, evaluación de reportes y reglas automatizadas/manuales para prevenir fraude.
              </p>
            </div>
          </div>
        </section>

        {/* CARD 3: Finalidades (tu ejemplo exacto) */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">3</span>
            FINALIDADES DEL TRATAMIENTO
          </h2>
          <div className="ml-12 space-y-6">
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">3.1 Principales</h3>
              <ul className="space-y-2 ml-4">
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Crear/administrar tu cuenta.</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Explorar y gestionar pedidos de productos importados.</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Procesar pagos de forma segura y gestionar la logística de entrega.</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Brindar soporte, resolver incidencias y moderar contenidos.</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Prevenir fraude y seguridad de la plataforma.</span></li>
              </ul>
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">3.2 Adicionales</h3>
              <ul className="space-y-2 ml-4">
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Recomendaciones personalizadas (categorías, intereses, productos).</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Análisis de uso para mejorar experiencia y rendimiento.</span></li>
                <li className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>Marketing con tu consentimiento (opt-in) y posibilidad de retiro (opt-out).</span></li>
              </ul>
            </div>
          </div>
        </section>

        {/* CARD 4: Bases legales */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">4</span>
            BASES LEGALES / FUNDAMENTOS
          </h2>
          <ul className="ml-12 space-y-3">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Ejecución de contrato:</strong> compra-venta y pagos.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Consentimiento:</strong> ubicación, marketing, cookies no esenciales.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Interés legítimo:</strong> seguridad, antifraude, mejoras del servicio.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Obligación legal:</strong> contable, fiscal y atención de autoridades.</li>
          </ul>
        </section>

        {/* CARD 5: Cookies */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">5</span>
            COOKIES Y TECNOLOGÍAS SIMILARES
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Usamos cookies esenciales, de rendimiento y de preferencias. Las de marketing solo con tu consentimiento.
            Puedes gestionarlas en tu navegador y, cuando aplique, en nuestro banner.
          </p>
        </section>

        {/* CARD 6: Compartición */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">6</span>
            COMPARTICIÓN DE INFORMACIÓN
          </h2>
          <div className="ml-12 space-y-3">
            <div className="bg-white border-2 border-border p-4 shadow-brutal">• <strong>Pagos y logística</strong>: cobros, envíos y entregas.</div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">• <strong>Nube/analítica/mensajería</strong>: hosting, métricas, notificaciones.</div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">• <strong>Autoridades</strong>: cumplimiento legal y protección de derechos.</div>
          </div>
        </section>

        {/* CARD 7: Seguridad */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">7</span>
            SEGURIDAD DE LA INFORMACIÓN
          </h2>
          <ul className="ml-12 grid md:grid-cols-3 gap-4">
            <li className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">🔒 TLS en tránsito; buenas prácticas de almacenamiento.</li>
            <li className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">🔐 Controles de acceso, minimización y auditoría.</li>
            <li className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">🛡️ Monitoreo y pruebas periódicas.</li>
          </ul>
        </section>

        {/* CARD 8: Retención */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">8</span>
            RETENCIÓN DE DATOS
          </h2>
          <ul className="ml-12 space-y-3">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Cuenta</strong>: mientras esté activa o hasta su eliminación.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Transacciones/facturación</strong>: hasta 7 años (obligaciones legales).</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Registros técnicos</strong>: hasta 12 meses.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>Marketing</strong>: hasta revocar consentimiento.</li>
          </ul>
        </section>

        {/* CARD 9: Transferencias */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">9</span>
            TRANSFERENCIAS INTERNACIONALES
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Posibles transferencias a otros países (p. ej., EE. UU.) con salvaguardas adecuadas (SCC u otras medidas).
          </p>
        </section>

        {/* CARD 10: Menores */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">10</span>
            MENORES DE EDAD
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            No dirigida a menores de 18 años. Eliminaremos datos y cerraremos cuentas asociadas si se detectan.
          </p>
        </section>

        {/* CARD 11: Derechos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">11</span>
            TUS DERECHOS
          </h2>
          <div className="ml-12 space-y-4">
            <p className="text-foreground leading-relaxed">
              Acceso, actualización, rectificación, supresión; oposición o limitación; portabilidad; retiro del consentimiento.
            </p>
            <div className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">
              Escríbenos a{' '}
              <a href="mailto:contacto@yuancity.com" className="underline font-bold">
                contacto@yuancity.com
              </a>. Responderemos dentro de los plazos legales aplicables.
            </div>
          </div>
        </section>

        {/* CARD 12: Control de comunicaciones */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">12</span>
            CONTROL DE COMUNICACIONES
          </h2>
          <ul className="ml-12 grid md:grid-cols-3 gap-4">
            <li className="bg-white border-2 border-border p-4 shadow-brutal">📧 Desactiva emails promocionales desde el enlace del mensaje.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">📱 Gestiona notificaciones push en el dispositivo y la app.</li>
            <li className="bg-white border-2 border-border p-4 shadow-brutal">ℹ️ Los avisos transaccionales pueden continuar enviándose.</li>
          </ul>
        </section>

        {/* CARD 13: Cambios */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">13</span>
            CAMBIOS A ESTA POLÍTICA
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            Avisaremos cambios significativos en la app o por correo. Revisa la fecha de “Última actualización”.
          </p>
        </section>

        {/* CARD: Pie / Nota legal */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <p className="leading-relaxed mb-3">
            Al usar YuanCity confirmas que leíste y aceptas esta Política de Privacidad. Para ver Términos y Condiciones, visita su sección.
          </p>
          <p className="text-sm text-white/80">
            Usuarios Apple: revisa también los{' '}
            <a
              href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline text-white"
            >
              Términos de Servicio de Apple
            </a>.
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
}
