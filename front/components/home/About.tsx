// components/About.tsx
'use client';
import Image from "next/image";
import { useTranslation } from 'react-i18next';
export default function About() {
  const { t } = useTranslation();
  return (
    <section id="about" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Texto */}
          <div>
            <div className="bg-chart-1 border-4 border-border shadow-brutal-colored-lg p-4 inline-block mb-8 -rotate-1">
              <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
                {t('home.about.title')}
              </h2>
            </div>

            <div className="space-y-6">
              <p className="text-xl font-medium text-foreground">
                {t('home.about.weAreYuanCity')} <span className="font-bold">{t('home.about.yuanCity')}</span>{t('home.about.description1')}
              </p>

              <p className="text-lg font-medium text-foreground">
                {t('home.about.description2')}
              </p>

              <p className="text-lg font-medium text-foreground">
                {t('home.about.description3')}
              </p>

              <div className="bg-chart-4 border-4 border-border shadow-brutal-xl p-6">
                <p className="text-main-foreground font-bold text-lg">
                  {t('home.about.qualityBadge')}
                </p>
              </div>
            </div>
          </div>

          {/* Imagen */}
          <div className="relative">
            <div className="bg-black border-4 border-border shadow-brutal-3xl p-8 rotate-2 hover:shadow-[24px_24px_0px_0px_var(--color-border)] transition-all duration-300">
              <Image
                src="/img/about.jpg"
                alt={t('home.about.imageAlt')}
                width={500}
                height={400}
                className="border-2 border-border"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
