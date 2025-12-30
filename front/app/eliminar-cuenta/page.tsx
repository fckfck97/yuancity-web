// app/cuenta/eliminar/page.tsx
"use client";

import React, { useState } from "react";
import { AlertTriangle, Mail, CheckCircle, XCircle, ShieldCheck } from "lucide-react";
import Navbar from "@/components/navigation/navbar";
import Footer from "@/components/navigation/footer";
import { useTranslation } from "react-i18next";

export default function DeleteAccountPage() {
  const { t } = useTranslation();
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
                {t('deleteAccount.header.title')}
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium">
              {t('deleteAccount.header.subtitle')}
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-main border-2 border-border text-white px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">{t('deleteAccount.header.lastUpdate')}</span>
            </div>
          </div>
        </section>

        {/* CARD 1: Descripción */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.description.number')}</span>
            {t('deleteAccount.sections.description.title')}
          </h2>
          <p className="text-white">
            {t('deleteAccount.sections.description.content')}
          </p>
        </section>

        {/* CARD 2: Advertencia */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.warning.number')}</span>
            {t('deleteAccount.sections.warning.title')}
          </h2>
          <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
            <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
            <div>
              <p className="font-semibold text-foreground">{t('deleteAccount.sections.warning.irreversible')}</p>
              <p className="text-foreground/90 mt-1">
                {t('deleteAccount.sections.warning.description')}
              </p>
            </div>
          </div>
        </section>

        {/* CARD 3: Verificación rápida (Formulario) */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.verification.number')}</span>
            {t('deleteAccount.sections.verification.title')}
          </h2>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="col-span-2 md:col-span-1">
              <label className="block text-sm font-black text-foreground mb-1">{t('deleteAccount.sections.verification.emailLabel')}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('deleteAccount.sections.verification.emailPlaceholder')}
                className="w-full bg-white border-2 border-border px-3 py-2 shadow-brutal focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-xs text-foreground/70 mt-1">{t('deleteAccount.sections.verification.emailHint')}</p>
            </div>

            <div className="col-span-2 md:col-span-1">
              <label className="block text-sm font-black text-foreground mb-1">{t('deleteAccount.sections.verification.otpLabel')}</label>
              <input
                type="text"
                inputMode="numeric"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder={t('deleteAccount.sections.verification.otpPlaceholder')}
                className="w-full bg-white border-2 border-border px-3 py-2 shadow-brutal focus:outline-none focus:ring-2 focus:ring-black"
              />
              <p className="text-xs text-foreground/70 mt-1">{t('deleteAccount.sections.verification.otpHint')}</p>
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-black text-foreground mb-1">{t('deleteAccount.sections.verification.reasonLabel')}</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                placeholder={t('deleteAccount.sections.verification.reasonPlaceholder')}
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
                {t('deleteAccount.sections.verification.deleteButton')}
              </button>
            </div>
          )}
        </section>

        {/* CARD 4: Contacto */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.contact.number')}</span>
            {t('deleteAccount.sections.contact.title')}
          </h2>
          <p className="text-white mb-3">{t('deleteAccount.sections.contact.description')}</p>
          <a
            href={`mailto:${t('deleteAccount.sections.contact.email')}`}
            className="text-white underline font-bold inline-flex items-center"
          >
            <Mail size={18} className="mr-2" />
            {t('deleteAccount.sections.contact.email')}
          </a>
        </section>

        {/* CARD 5: Qué se eliminará */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.whatWillBeDeleted.number')}</span>
            {t('deleteAccount.sections.whatWillBeDeleted.title')}
          </h2>
          <ul className="space-y-3 ml-1">
            {t('deleteAccount.sections.whatWillBeDeleted.items', { returnObjects: true }).map((item: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="text-white mr-3 mt-1">•</span>
                <span className="text-white">{item}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* CARD 6: Pasos para eliminar */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.steps.number')}</span>
            {t('deleteAccount.sections.steps.title')}
          </h2>

          <div className="grid gap-4 md:grid-cols-3">
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">{t('deleteAccount.sections.steps.fromApp.title')}</h3>
              <p className="text-foreground/90">
                {t('deleteAccount.sections.steps.fromApp.description')}
              </p>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">{t('deleteAccount.sections.steps.byEmail.title')}</h3>
              <p className="text-foreground/90">
                {t('deleteAccount.sections.steps.byEmail.description')}
              </p>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="font-black text-foreground mb-2">{t('deleteAccount.sections.steps.verification.title')}</h3>
              <p className="text-foreground/90">
                {t('deleteAccount.sections.steps.verification.description')}
              </p>
            </div>
          </div>
        </section>

        {/* CARD 7: Datos que pueden conservarse */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.dataRetention.number')}</span>
            {t('deleteAccount.sections.dataRetention.title')}
          </h2>

          <div className="bg-white border-2 border-border shadow-brutal overflow-x-auto">
            <table className="w-full border-collapse">
              <thead className="bg-secondary-background">
                <tr>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">{t('deleteAccount.sections.dataRetention.tableHeaders.type')}</th>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">{t('deleteAccount.sections.dataRetention.tableHeaders.reason')}</th>
                  <th className="border-2 border-border px-4 py-3 text-left font-black text-foreground">{t('deleteAccount.sections.dataRetention.tableHeaders.period')}</th>
                </tr>
              </thead>
              <tbody>
                {t('deleteAccount.sections.dataRetention.tableRows', { returnObjects: true }).map((row: string[], i: number) => (
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
            {t('deleteAccount.sections.dataRetention.note')}
          </p>
        </section>

        {/* CARD 8: Suscripciones y facturación */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('deleteAccount.sections.subscriptions.number')}</span>
            {t('deleteAccount.sections.subscriptions.title')}
          </h2>
          <div className="space-y-2">
            {t('deleteAccount.sections.subscriptions.items', { returnObjects: true }).map((item: any, index: number) => (
              <div key={index} className="bg-white border-2 border-border p-4 shadow-brutal">
                {item.label && <strong>{item.label}</strong>} {item.description}
              </div>
            ))}
          </div>
        </section>

        {/* CARD 9: Estado (success/error) */}
        {status === "success" && (
          <section className="bg-main border-4 border-border shadow-brutal-2xl p-6 -rotate-1">
            <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
              <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
              <p className="text-black font-bold">{t('deleteAccount.status.success')}</p>
            </div>
          </section>
        )}
        {status === "error" && (
          <section className="bg-main border-4 border-border shadow-brutal-2xl p-6 rotate-1">
            <div className="bg-white border-2 border-border p-4 shadow-brutal flex items-start gap-3">
              <XCircle className="text-red-600 flex-shrink-0" size={24} />
              <p className="text-black font-bold">{t('deleteAccount.status.error')}</p>
            </div>
          </section>
        )}

        {/* CARD 10: Pie/nota legal */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <p className="leading-relaxed">
            {t('deleteAccount.footer.content')}{" "}
            <a href={`mailto:${t('deleteAccount.footer.email')}`} className="underline text-white font-bold">{t('deleteAccount.footer.email')}</a>.
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
              <h3 className="text-xl font-black text-foreground">{t('deleteAccount.modal.title')}</h3>
            </div>
            <p className="text-foreground mb-6">
              {t('deleteAccount.modal.question')}
            </p>
            <div className="flex gap-4">
              <button
                onClick={confirmDelete}
                disabled={loading || !email}
                className="flex-1 bg-black text-white border-4 border-border px-4 py-2 font-black shadow-brutal hover:shadow-[12px_12px_0px_0px_var(--color-border)] disabled:opacity-50 transition-all"
              >
                {loading ? t('deleteAccount.modal.processing') : t('deleteAccount.modal.confirmButton')}
              </button>
              <button
                onClick={() => setShowConfirmation(false)}
                className="flex-1 bg-white text-foreground border-4 border-border px-4 py-2 font-black shadow-brutal hover:shadow-[12px_12px_0px_0px_var(--color-border)] transition-all"
              >
                {t('deleteAccount.modal.cancelButton')}
              </button>
            </div>
            <p className="text-xs text-foreground/70 mt-4">
              {t('deleteAccount.modal.note')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
