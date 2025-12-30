// app/legal/politica-privacidad/yuancity/page.tsx
'use client'
import Footer from '@/components/navigation/footer';
import Navbar from '@/components/navigation/navbar';

import { useTranslation } from 'react-i18next';


export default function PoliticaPrivacidadYuanCityPage() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 py-16 md:py-24 max-w-5xl space-y-10">
        {/* CARD: Header */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-10 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <div className="-rotate-1">
            <div className="bg-main border-4 border-border shadow-brutal-colored-lg inline-block px-4 py-2 -rotate-1 mb-6">
              <h1 className="text-3xl md:text-5xl font-black tracking-tight text-white">
                {t('privacyPolicy.title')}
              </h1>
            </div>
            <p className="text-lg md:text-xl text-white/90 font-medium">
                  {t('privacyPolicy.subtitle')}
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-main border-2 border-border text-white px-4 py-2 shadow-brutal">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-semibold">{t('privacyPolicy.lastUpdated')}</span>
            </div>
          </div>
        </section>

        {/* CARD: Intro */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-4">{t('privacyPolicy.intro.title')}</h2>
          <p className="text-lg leading-relaxed text-white">
            <strong className="text-white">YuanCity</strong>{t('privacyPolicy.intro.paragraph1')}<strong className="text-white">{t('privacyPolicy.intro.ovalcampus')}</strong>{t('privacyPolicy.intro.paragraph2')}
          </p>
          <p className="text-base leading-relaxed text-white mt-4">
            {t('privacyPolicy.intro.paragraph3')}<strong>{t('privacyPolicy.intro.law')}</strong>{t('privacyPolicy.intro.and')}<strong>{t('privacyPolicy.intro.habeasData')}</strong>{t('privacyPolicy.intro.regime')}<strong>{t('privacyPolicy.intro.gdpr')}</strong>{t('privacyPolicy.intro.eu')}<strong>{t('privacyPolicy.intro.ccpa')}</strong>{t('privacyPolicy.intro.california')}
          </p>
        </section>

        {/* CARD 1: Responsable */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.dataController.number')}</span>
            {t('privacyPolicy.sections.dataController.title')}
          </h2>
          <div className="ml-12 space-y-3">
            <p className="text-white leading-relaxed">
              <strong>{t('privacyPolicy.sections.dataController.name')}</strong><br />
              <span className="text-white/80">{t('privacyPolicy.sections.dataController.address')}</span>
            </p>
            <p className="text-white">
              <strong>{t('privacyPolicy.sections.dataController.contactLabel')}</strong>{' '}
              <a href={`mailto:${t('privacyPolicy.sections.dataController.email')}`} className="text-white font-semibold underline">
                {t('privacyPolicy.sections.dataController.email')}
              </a>
            </p>
          </div>
        </section>

        {/* CARD 2: Información que Recopilamos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.informationCollected.number')}</span>
            {t('privacyPolicy.sections.informationCollected.title')}
          </h2>

          <div className="ml-12 grid md:grid-cols-2 gap-6">
            <div className="bg-black text-white border-2 border-border p-6 shadow-brutal-2xl">
              <h3 className="text-xl font-black mb-3">{t('privacyPolicy.sections.informationCollected.accountProfile.title')}</h3>
              <ul className="space-y-2 text-white/90">
                {t('privacyPolicy.sections.informationCollected.accountProfile.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            </div>

            <div className="bg-black text-white border-2 border-border p-6 shadow-brutal-2xl">
              <h3 className="text-xl font-black mb-3">{t('privacyPolicy.sections.informationCollected.postsTransactions.title')}</h3>
              <ul className="space-y-2 text-white/90">
                {t('privacyPolicy.sections.informationCollected.postsTransactions.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('privacyPolicy.sections.informationCollected.technicalData.title')}</h3>
              <ul className="space-y-2 text-foreground/90">
                {t('privacyPolicy.sections.informationCollected.technicalData.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            </div>

            <div className="bg-white border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('privacyPolicy.sections.informationCollected.location.title')}</h3>
              <ul className="space-y-2 text-foreground/90">
                {t('privacyPolicy.sections.informationCollected.location.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            </div>

            <div className="md:col-span-2 bg-black border-2 border-border p-6 shadow-brutal">
              <h3 className="text-xl font-black text-white mb-2">{t('privacyPolicy.sections.informationCollected.moderation.title')}</h3>
              <p className="text-white/90">
                {t('privacyPolicy.sections.informationCollected.moderation.description')}
              </p>
            </div>
          </div>
        </section>

        {/* CARD 3: Finalidades (tu ejemplo exacto) */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.purposes.number')}</span>
            {t('privacyPolicy.sections.purposes.title')}
          </h2>
          <div className="ml-12 space-y-6">
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('privacyPolicy.sections.purposes.main.title')}</h3>
              <ul className="space-y-2 ml-4">
                {t('privacyPolicy.sections.purposes.main.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index} className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>{item}</span></li>
                ))}
              </ul>
            </div>
            <div className="bg-white border-2 border-border p-4 shadow-brutal">
              <h3 className="text-xl font-black text-foreground mb-3">{t('privacyPolicy.sections.purposes.additional.title')}</h3>
              <ul className="space-y-2 ml-4">
                {t('privacyPolicy.sections.purposes.additional.items', { returnObjects: true }).map((item: string, index: number) => (
                  <li key={index} className="flex items-start gap-2 font-medium"><span className="mt-1.5">•</span><span>{item}</span></li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        {/* CARD 4: Bases legales */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.legalBases.number')}</span>
            {t('privacyPolicy.sections.legalBases.title')}
          </h2>
          <ul className="ml-12 space-y-3">
            {t('privacyPolicy.sections.legalBases.items', { returnObjects: true }).map((item: any, index: number) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>{item.label}</strong> {item.description}</li>
            ))}
          </ul>
        </section>

        {/* CARD 5: Cookies */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.cookies.number')}</span>
            {t('privacyPolicy.sections.cookies.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('privacyPolicy.sections.cookies.description')}
          </p>
        </section>

        {/* CARD 6: Compartición */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.sharing.number')}</span>
            {t('privacyPolicy.sections.sharing.title')}
          </h2>
          <div className="ml-12 space-y-3">
            {t('privacyPolicy.sections.sharing.items', { returnObjects: true }).map((item: any, index: number) => (
              <div key={index} className="bg-white border-2 border-border p-4 shadow-brutal">• <strong>{item.label}</strong>{item.description}</div>
            ))}
          </div>
        </section>

        {/* CARD 7: Seguridad */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.security.number')}</span>
            {t('privacyPolicy.sections.security.title')}
          </h2>
          <ul className="ml-12 grid md:grid-cols-3 gap-4">
            {t('privacyPolicy.sections.security.items', { returnObjects: true }).map((item: string, index: number) => (
              <li key={index} className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">{item}</li>
            ))}
          </ul>
        </section>

        {/* CARD 8: Retención */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.retention.number')}</span>
            {t('privacyPolicy.sections.retention.title')}
          </h2>
          <ul className="ml-12 space-y-3">
            {t('privacyPolicy.sections.retention.items', { returnObjects: true }).map((item: any, index: number) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">→ <strong>{item.label}</strong>{item.description}</li>
            ))}
          </ul>
        </section>

        {/* CARD 9: Transferencias */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.transfers.number')}</span>
            {t('privacyPolicy.sections.transfers.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('privacyPolicy.sections.transfers.description')}
          </p>
        </section>

        {/* CARD 10: Menores */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.minors.number')}</span>
            {t('privacyPolicy.sections.minors.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('privacyPolicy.sections.minors.description')}
          </p>
        </section>

        {/* CARD 11: Derechos */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.rights.number')}</span>
            {t('privacyPolicy.sections.rights.title')}
          </h2>
          <div className="ml-12 space-y-4">
            <p className="text-foreground leading-relaxed">
              {t('privacyPolicy.sections.rights.description')}
            </p>
            <div className="bg-black text-white border-2 border-border p-4 shadow-brutal-2xl">
              {t('privacyPolicy.sections.rights.contact')}{' '}
              <a href={`mailto:${t('privacyPolicy.sections.rights.email')}`} className="underline font-bold">
                {t('privacyPolicy.sections.rights.email')}
              </a>{t('privacyPolicy.sections.rights.response')}
            </div>
          </div>
        </section>

        {/* CARD 12: Control de comunicaciones */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.communications.number')}</span>
            {t('privacyPolicy.sections.communications.title')}
          </h2>
          <ul className="ml-12 grid md:grid-cols-3 gap-4">
            {t('privacyPolicy.sections.communications.items', { returnObjects: true }).map((item: string, index: number) => (
              <li key={index} className="bg-white border-2 border-border p-4 shadow-brutal">{item}</li>
            ))}
          </ul>
        </section>

        {/* CARD 13: Cambios */}
        <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 -rotate-1">
          <h2 className="text-2xl md:text-3xl font-black text-white mb-6 flex items-center gap-3">
            <span className="flex items-center justify-center w-12 h-12 bg-black text-white font-black text-xl border-2 border-border">{t('privacyPolicy.sections.changes.number')}</span>
            {t('privacyPolicy.sections.changes.title')}
          </h2>
          <p className="ml-12 text-foreground leading-relaxed">
            {t('privacyPolicy.sections.changes.description')}
          </p>
        </section>

        {/* CARD: Pie / Nota legal */}
        <section className="bg-black text-white border-4 border-border shadow-brutal-3xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
          <p className="leading-relaxed mb-3">
            {t('privacyPolicy.footer.paragraph1')}
          </p>
          <p className="text-sm text-white/80">
            {t('privacyPolicy.footer.paragraph2')}{' '}
            <a
              href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline text-white"
            >
              {t('privacyPolicy.footer.appleTermsLink')}
            </a>{t('privacyPolicy.footer.period')}
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
}
