// app/not-found.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';
import Navbar from '@/components/navigation/navbar';
import Footer from '@/components/navigation/footer';
import { Home, Search, AlertTriangle } from 'lucide-react';

export default function NotFound() {
  const { t, i18n } = useTranslation();
  const withLanguage = (path: string) => {
    const separator = path.includes('?') ? '&' : '?';
    const language = i18n.language || i18n.resolvedLanguage || 'en';
    return `${path}${separator}lng=${encodeURIComponent(language)}`;
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />

      <main className="flex-1 container mx-auto px-4 py-16 md:py-24 max-w-4xl flex items-center justify-center">
        <div className="w-full space-y-8">
          {/* CARD: 404 Giant Number */}
          <section className="bg-main border-4 border-border shadow-brutal-3xl p-10 rotate-2 hover:shadow-[25px_25px_0px_0px_var(--color-border)] transition-all duration-300">
            <div className="-rotate-2 text-center">
              <div className="relative inline-block">
                <h1 className="text-[150px] md:text-[220px] font-black tracking-tighter text-white leading-none relative z-10">
                  404
                </h1>
                <div className="absolute inset-0 text-[150px] md:text-[220px] font-black tracking-tighter text-black opacity-20 blur-sm transform translate-x-2 translate-y-2">
                  404
                </div>
              </div>
            </div>
          </section>

          {/* CARD: Error Message */}
          <section className="bg-black text-white border-4 border-border shadow-brutal-2xl p-8 -rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300">
            <div className="rotate-1 flex items-start gap-4">
              <AlertTriangle className="text-main flex-shrink-0 mt-1" size={32} />
              <div>
                <h2 className="text-3xl md:text-4xl font-black mb-4 text-white">
                  {t('notFound.title')}
                </h2>
                <p className="text-lg md:text-xl text-white/90 font-medium">
                  {t('notFound.description')}
                </p>
              </div>
            </div>
          </section>

          {/* CARD: Actions */}
          <section className="bg-main border-4 border-border shadow-brutal-2xl p-8 rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300">
            <div className="-rotate-1">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Search size={24} />
                {t('notFound.whatCanYouDo')}
              </h3>
              
              <div className="grid md:grid-cols-2 gap-4">
                {/* Botón Home */}
                <Link 
                  href="/"
                  className="group bg-black text-white border-4 border-border p-6 shadow-brutal hover:shadow-[14px_14px_0px_0px_var(--color-border)] transition-all duration-300 flex flex-col items-center gap-3"
                >
                  <Home size={32} className="group-hover:scale-110 transition-transform" />
                  <span className="font-black text-xl">{t('notFound.backToHome')}</span>
                </Link>

                {/* Botón Explorar */}
                <Link 
                  href="/"
                  className="group bg-white text-foreground border-4 border-border p-6 shadow-brutal hover:shadow-[14px_14px_0px_0px_var(--color-border)] transition-all duration-300 flex flex-col items-center gap-3"
                >
                  <Search size={32} className="group-hover:scale-110 transition-transform" />
                  <span className="font-black text-xl">{t('notFound.exploreProducts')}</span>
                </Link>
              </div>
            </div>
          </section>

          {/* CARD: Help Links */}
          <section className="bg-white border-4 border-border shadow-brutal-2xl p-6 -rotate-1 hover:shadow-[15px_15px_0px_0px_var(--color-border)] transition-all duration-300">
            <div className="rotate-1">
              <p className="text-foreground text-center font-semibold">
                {t('notFound.needHelp')}{' '}
                <Link href={withLanguage('/politicas-privacidad')} className="text-main underline font-black hover:text-main/80">
                  {t('notFound.privacyPolicy')}
                </Link>
                {' '}{t('notFound.or')}{' '}
                <Link href={withLanguage('/terminos-condiciones')} className="text-main underline font-black hover:text-main/80">
                  {t('notFound.termsAndConditions')}
                </Link>
                {' '}{t('notFound.pages')}
              </p>
            </div>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
