// app/cuenta/eliminar/page.tsx
"use client";

import React, { useState } from "react";
import { AlertTriangle, Mail, CheckCircle, XCircle, ShieldCheck } from "lucide-react";
import Navbar from "@/components/navigation/navbar";
import Footer from "@/components/navigation/footer";

export default function DeleteAccountPage() {
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [status, setStatus] = useState<"success" | "error" | null>(null);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState(""); // correo registrado
  const [otp, setOtp] = useState(""); // OTP opcional
  const [reason, setReason] = useState(""); // motivo opcional

  const handleDeleteRequest = () => setShowConfirmation(true);

  const confirmDelete = async () => {
    try {
      setLoading(true);
      const res = await fetch("/api/account/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp: otp || null, reason: reason || null }),
      });

      if (!res.ok) throw new Error("Request failed");
      setStatus("success");
      setShowConfirmation(false);
    } catch {
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 py-16 md:py-24 max-w-5xl space-y-10">
        {/* CARD 0: Header */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-10 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1">
            <div className="bg-main border-4 border-border shadow-brutal-colored-lg inline-block px-4 py-2 -rotate-1 mb-6">
              <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white">
                Eliminar tu cuenta
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium">
              Elimina permanentemente tu cuenta de YuanCity
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-main border-2 border-border text-white px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">Última actualización: 11 de noviembre de 2025</span>
            </div>
          </div>
        </section>

        {/* CARD 1: Descripción */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">1</span>
            ¿Qué significa eliminar tu cuenta?
          </h2>
          <p className="text-white">
            Al eliminar tu cuenta, tus datos personales, historial de pedidos y preferencias se eliminarán de nuestros
            sistemas, salvo ciertos datos mínimos que debamos conservar por motivos legales o de seguridad. Esta acción
            no se puede deshacer.
          </p>
        </section>

        {/* CARD 2: Advertencia */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">2</span>
            Advertencia
          </h2>
          <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
            <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
            <div>
              <p className="font-semibold text-foreground">Esta acción es irreversible.</p>
              <p className="text-foreground/90 mt-1">
                Una vez completado el proceso, tu cuenta y datos eliminables no podrán recuperarse.
              </p>
            </div>
          </div>
        </section>

        {/* CARD 3: Verificación rápida (Formulario) */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">3</span>
            Verificación rápida
          </h2>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="col-span-2 md:col-span-1">
              <label className="block text-sm font-black text-foreground mb-1">Correo de tu cuenta</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu-correo@YuanCity.com"
                className="w-full bg-white border-2 border-border px-3 py-2 shadow-brutal focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-xs text-foreground/70 mt-1">Debe coincidir con el correo registrado en YuanCity.</p>
            </div>

            <div className="col-span-2 md:col-span-1">
              <label className="block text-sm font-black text-foreground mb-1">Código OTP (si requerido)</label>
              <input
                type="text"
                inputMode="numeric"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="Ingresa tu código de verificación"
                className="w-full bg-white border-2 border-border px-3 py-2 shadow-brutal focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-xs text-foreground/70 mt-1">Te lo enviamos por correo/SMS/WhatsApp si tu cuenta lo requiere.</p>
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-black text-foreground mb-1">Motivo (opcional)</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                placeholder="Cuéntanos brevemente el motivo (opcional)"
                className="w-full bg-white border-2 border-border px-3 py-2 shadow-brutal focus:outline-none focus:ring-2 focus:ring-black"
              />
            </div>
          </div>

          {/* Botón principal */}
          {!status && (
            <div className="text-center mt-6">
              <button
                onClick={handleDeleteRequest}
                className="bg-black text-white border-4 border-border px-8 py-3 font-black shadow-brutal hover:shadow-[14px_14px_0px_0px_var(--color-border)] transition-all"
              >
                Eliminar mi cuenta
              </button>
            </div>
          )}
        </section>

        {/* CARD 4: Contacto */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">4</span>
            Contáctanos
          </h2>
          <p className="text-white mb-3">¿Dudas antes de eliminar tu cuenta? Escríbenos:</p>
          <a
            href="mailto:contacto@yuancity.com"
            className="text-white underline font-bold inline-flex items-center"
          >
            <Mail size={18} className="mr-2" />
            contacto@yuancity.com
          </a>
        </section>

        {/* CARD 5: Qué se eliminará */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">5</span>
            Qué se eliminará
          </h2>
          <ul className="space-y-3 ml-1">
            <li className="flex items-start">
              <span className="text-foreground mr-3 mt-1">•</span>
              <span className="text-foreground">Perfil e información personal (nombre, correo, teléfono).</span>
            </li>
            <li className="flex items-start">
              <span className="text-foreground mr-3 mt-1">•</span>
              <span className="text-foreground">Historial de pedidos, pagos y preferencias.</span>
            </li>
            <li className="flex items-start">
              <span className="text-foreground mr-3 mt-1">•</span>
              <span className="text-white">Artículos favoritos y listas guardadas.</span>
            </li>
            <li className="flex items-start">
              <span className="text-foreground mr-3 mt-1">•</span>
              <span className="text-foreground">
                Datos de suscripción administrados por YuanCity (las suscripciones externas deben cancelarse por separado).
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-foreground mr-3 mt-1">•</span>
              <span className="text-foreground">Mensajes y comunicaciones vinculadas a tu cuenta dentro del servicio.</span>
            </li>
          </ul>
        </section>

        {/* CARD 6: Pasos para eliminar */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">6</span>
            Pasos para eliminar tu cuenta
          </h2>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">Desde la app</h3>
              <p className="text-foreground/90">
                Abre YuanCity → Configuración → Cuenta → Eliminar cuenta y sigue los pasos. Confirma tu identidad (PIN/biometría/OTP).
              </p>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">Por correo</h3>
              <p className="text-foreground/90">
                Envía a <strong>contact@YuanCity.com</strong> el asunto «Eliminar mi cuenta» con tu correo registrado y país.
              </p>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">Verificación y tiempos</h3>
              <p className="text-foreground/90">
                Podemos solicitar verificación adicional. Procesamos en hasta 30 días. Backups pueden tardar hasta 90 días en purgarse.
              </p>
            </div>
          </div>
        </section>

        {/* CARD 7: Datos que pueden conservarse */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">7</span>
            Datos que pueden conservarse
          </h2>

          <div className="bg-white border-2 border-border shadow-brutal overflow-x-auto">
            <table className="w-full border-collapse">
              <thead className="bg-secondary-background">
                <tr>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">Tipo de dato</th>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">Motivo</th>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">Periodo</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Registros de seguridad/antifraude", "Prevención, investigación y seguridad", "Hasta 12 meses"],
                  ["Comprobantes contables/fiscales", "Obligaciones legales", "Hasta 7 años (según país)"],
                  ["Tickets de soporte y correos", "Atención, defensa de reclamaciones", "Hasta 24 meses"],
                  ["Copias de seguridad", "Integridad y recuperación ante desastres", "Hasta 90 días"],
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-secondary-background/60">
                    <td className="border-2 border-border px-4 py-3 text-foreground">{row[0]}</td>
                    <td className="border-2 border-border px-4 py-3 text-foreground">{row[1]}</td>
                    <td className="border-2 border-border px-4 py-3 text-foreground">{row[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="text-foreground/80 text-sm mt-4 italic">
            El resto se elimina o anonimiza de forma segura.
          </p>
        </section>

        {/* CARD 8: Suscripciones y facturación */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">8</span>
            Suscripciones y facturación
          </h2>
          <div className="space-y-2">
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <strong>Importante:</strong> Eliminar tu cuenta no cancela automáticamente suscripciones compradas en App Store o Google Play.
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              Cancélalas directamente desde tu cuenta de la tienda correspondiente.
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              No almacenamos datos completos de tarjetas en nuestros sistemas.
            </div>
          </div>
        </section>

        {/* CARD 9: Estado (success/error) */}
        {status === "success" && (
          <section className="bg-main border-4 border-border shadow-brutal-2xl p-6 -rotate-1">
            <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
              <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
              <p className="text-black font-bold">Tu cuenta ha sido eliminada correctamente.</p>
            </div>
          </section>
        )}
        {status === "error" && (
          <section className="bg-main border-4 border-border shadow-brutal-2xl p-6 rotate-1">
            <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
              <XCircle className="text-red-600 flex-shrink-0" size={24} />
              <p className="text-black font-bold">Hubo un error al eliminar tu cuenta. Inténtalo de nuevo.</p>
            </div>
          </section>
        )}

        {/* CARD 10: Pie/nota legal */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <p className="leading-relaxed">
            Para tu seguridad, podemos solicitar verificación adicional en algunos casos. Si necesitas ayuda, escribe a{" "}
            <a href="mailto:contact@YuanCity.com" className="underline text-white font-bold">contact@YuanCity.com</a>.
          </p>
        </section>
      </main>

      <Footer />

      {/* Modal de confirmación (brutalista) */}
      {showConfirmation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white border-4 border-border shadow-brutal-3xl max-w-md w-full p-6 -rotate-1">
            <div className="flex items-center mb-4">
              <ShieldCheck className="text-black mr-3" size={28} />
              <h3 className="text-xl font-black text-foreground">Confirmación requerida</h3>
            </div>
            <p className="text-foreground mb-6">
              ¿Seguro que deseas eliminar tu cuenta de forma permanente?
            </p>
            <div className="flex gap-4">
              <button
                onClick={confirmDelete}
                disabled={loading || !email}
                className="flex-1 bg-black text-white border-4 border-border px-4 py-2 font-black shadow-brutal hover:shadow-[12px_12px_0px_0px_var(--color-border)] disabled:opacity-50 transition-all"
              >
                {loading ? "Procesando..." : "Sí, eliminar mi cuenta"}
              </button>
              <button
                onClick={() => setShowConfirmation(false)}
                className="flex-1 bg-white text-foreground border-4 border-border px-4 py-2 font-black shadow-brutal hover:shadow-[12px_12px_0px_0px_var(--color-border)] transition-all"
              >
                Cancelar
              </button>
            </div>
            <p className="text-xs text-foreground/70 mt-4">
              Podemos solicitar verificación adicional para proteger tu cuenta.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
