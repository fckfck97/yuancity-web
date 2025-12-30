'use client';
// app/terminos-condiciones/page.tsx
import Footer from '@/components/navigation/footer';
import Navbar from '@/components/navigation/navbar';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';

export default function TerminosCondicionesPage() {
  const { t, i18n } = useTranslation();
  const withLanguage = (path: string) => {
    const separator = path.includes('?') ? '&' : '?';
    const language = i18n.language || i18n.resolvedLanguage || 'en';
    return `${path}${separator}lng=${encodeURIComponent(language)}`;
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
                {t('terms.header.title')}
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium">
              {t('terms.header.description')}
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-main border-2 border-border text-white px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">{t('terms.header.lastUpdate')}</span>
            </div>
          </div>
        </section>

        {/* 1. Introducción */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.introduction.number')}</span>
            {t('terms.sections.introduction.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.introduction.content').split('YuanCity')[0]}
            <strong className="text-main-foreground">{t('terms.sections.introduction.yuanCity')}</strong>
            {t('terms.sections.introduction.content').split('YuanCity')[1].split('Ovalcampus')[0]}
            <strong className="text-main-foreground">{t('terms.sections.introduction.ovalcampus')}</strong>
            {t('terms.sections.introduction.content').split('Ovalcampus')[1].split('EULA')[0]}
            <strong>{t('terms.sections.introduction.eula')}</strong>
            {t('terms.sections.introduction.content').split('EULA')[1]}
          </p>
        </section>

        {/* 2. Definiciones */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.definitions.number')}</span>
            {t('terms.sections.definitions.title')}
          </h2>
          <ul className="ml-12 space-y-3">
            {[
              [t('terms.sections.definitions.user'), t('terms.sections.definitions.userDefinition')],
              [t('terms.sections.definitions.provider'), t('terms.sections.definitions.providerDefinition')],
              [t('terms.sections.definitions.order'), t('terms.sections.definitions.orderDefinition')],
              [t('terms.sections.definitions.platform'), t('terms.sections.definitions.platformDefinition')],
              [t('terms.sections.definitions.services'), t('terms.sections.definitions.servicesDefinition')],
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
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.registration.number')}</span>
            {t('terms.sections.registration.title')}
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            {['🔐', '🔒', '👤', '⚠️'].map((emoji, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="mt-1.5">{emoji}</span>
                <span>{t(`terms.sections.registration.points.${index}`)}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* 4. Uso de la plataforma */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.platformUse.number')}</span>
            {t('terms.sections.platformUse.title')}
          </h2>
          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('terms.sections.platformUse.allowed.title')}</h3>
              <ul className="space-y-2 text-foreground/90 ml-1">
                {t('terms.sections.platformUse.allowed.points', { returnObjects: true }).map((point: string, i: number) => (
                  <li key={i}>• {point}</li>
                ))}
              </ul>
            </div>
            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('terms.sections.platformUse.prohibited.title')}</h3>
              <ul className="space-y-2 text-foreground/90 ml-1">
                {t('terms.sections.platformUse.prohibited.points', { returnObjects: true }).map((point: string, i: number) => (
                  <li key={i}>• {point}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* 5. Pedidos, precios y pagos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.orders.number')}</span>
            {t('terms.sections.orders.title')}
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            {['💰', '✅', '💳', '📄'].map((emoji, index) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">
                {emoji} {t(`terms.sections.orders.points.${index}`)}
              </li>
            ))}
          </ul>
        </section>

        {/* 6. Cancelaciones y reembolsos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.cancellations.number')}</span>
            {t('terms.sections.cancellations.title')}
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            {t('terms.sections.cancellations.points', { returnObjects: true }).map((point: string, i: number) => (
              <li key={i} className="bg-white border-2 border-border p-4 shadow-brutal">• {point}</li>
            ))}
          </ul>
        </section>

        {/* 7. Suscripciones e IAP */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.subscriptions.number')}</span>
            {t('terms.sections.subscriptions.title')}
          </h2>
          <div className="ml-12 space-y-4 text-foreground">
            <p className="leading-relaxed">
              {t('terms.sections.subscriptions.content')}
            </p>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              {t('terms.sections.subscriptions.appleEula')}{' '}
              <a
                href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
                target="_blank"
                rel="noreferrer"
                className="underline text-main-foreground font-bold"
              >
                {t('terms.sections.subscriptions.appleEulaLink')}
              </a>.
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <strong>{t('terms.sections.subscriptions.notResponsible')}</strong>
            </div>
          </div>
        </section>

        {/* 8. Calificaciones y contenido */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.reviews.number')}</span>
            {t('terms.sections.reviews.title')}
          </h2>
          <ul className="ml-12 space-y-3 text-foreground">
            {['⭐', '📝', '🛡️'].map((emoji, index) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">
                {emoji} {t(`terms.sections.reviews.points.${index}`)}
              </li>
            ))}
          </ul>
        </section>

        {/* 9. Propiedad intelectual */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.intellectualProperty.number')}</span>
            {t('terms.sections.intellectualProperty.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.intellectualProperty.content')}
          </p>
        </section>

        {/* 10. Dispositivos y servicios */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.devices.number')}</span>
            {t('terms.sections.devices.title')}
          </h2>
          <ul className="ml-12 space-y-3">
            {['📱', '🔗'].map((emoji, index) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">
                {emoji} {t(`terms.sections.devices.points.${index}`)}
              </li>
            ))}
          </ul>
        </section>

        {/* 11. Garantías y limitación */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.warranties.number')}</span>
            {t('terms.sections.warranties.title')}
          </h2>
          <ul className="ml-12 space-y-3">
            {['→', '→', '→'].map((arrow, index) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">
                {arrow} {t(`terms.sections.warranties.points.${index}`)}
              </li>
            ))}
          </ul>
        </section>

        {/* 12. Indemnidad */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.indemnity.number')}</span>
            {t('terms.sections.indemnity.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.indemnity.content')}
          </p>
        </section>

        {/* 13. Suspensión y terminación */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.suspension.number')}</span>
            {t('terms.sections.suspension.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.suspension.content')}
          </p>
        </section>

        {/* 14. Ley aplicable */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.law.number')}</span>
            {t('terms.sections.law.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.law.content')}
          </p>
        </section>

        {/* 15. Cambios */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.changes.number')}</span>
            {t('terms.sections.changes.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('terms.sections.changes.content')}
          </p>
        </section>

        {/* 16. Privacidad y docs */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('terms.sections.privacy.number')}</span>
            {t('terms.sections.privacy.title')}
          </h2>
          <div className="ml-12 space-y-3 text-foreground">
            <p>
              {t('terms.sections.privacy.content1')}{' '}
              <Link href={withLanguage('/politicas-privacidad')} className="text-main-foreground font-bold underline">
                {t('terms.sections.privacy.privacyPolicyLink')}
              </Link>.
            </p>
            <p>
              {t('terms.sections.privacy.content2')}{' '}
              <a
                href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
                target="_blank"
                rel="noreferrer"
                className="text-main-foreground font-bold underline"
              >
                {t('terms.sections.privacy.appleEulaLink')}
              </a>.
            </p>
          </div>
        </section>

        {/* 17. Contacto */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <h2 className="text-2xl md:text-3xl font-black mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-white text-black font-black text-xl border-2 border-border">{t('terms.sections.contact.number')}</span>
            {t('terms.sections.contact.title')}
          </h2>
          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-white/10 p-5 shadow-brutal border-2 border-white/20">
              <p className="font-bold mb-2 text-lg">📧 {t('terms.sections.contact.emailTitle')}</p>
              <a href={`mailto:${t('terms.sections.contact.email')}`} className="underline text-white">
                {t('terms.sections.contact.email')}
              </a>
            </div>
            <div className="bg-white/10 p-5 shadow-brutal border-2 border-white/20">
              <p className="font-bold mb-2 text-lg">📍 {t('terms.sections.contact.addressTitle')}</p>
              <p className="text-white/90 leading-relaxed whitespace-pre-line">
                {t('terms.sections.contact.address')}
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
