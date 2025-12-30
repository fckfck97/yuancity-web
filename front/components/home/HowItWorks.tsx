// components/HowItWorks.tsx
"use client";
import { Search, ShoppingBag, CreditCard, Truck } from "lucide-react";
import { useTranslation } from 'react-i18next';
export default function HowItWorks() {
  const { t } = useTranslation();
  const steps = [
    {
      title: t('home.HowItWorks.step1Title'),
      desc: t('home.HowItWorks.step1Desc'),
      Icon: Search,
    },
    {
      title: t('home.HowItWorks.step2Title'),
      desc: t('home.HowItWorks.step2Desc'),
      Icon: ShoppingBag,
    },
    {
      title: t('home.HowItWorks.step3Title'),
      desc: t('home.HowItWorks.step3Desc'),
      Icon: CreditCard,
    },
    {
      title: t('home.HowItWorks.step4Title'),
      desc: t('home.HowItWorks.step4Desc'),
      Icon: Truck,
    },
  ] as const;

  return (
    <section id="como-funciona" className="py-20 bg-secondary-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Título */}
        <div>
          <div className="bg-chart-2 border-4 border-border shadow-brutal-colored-xl p-4 inline-block mb-12 rotate-1">
            <h2 className="text-4xl md:text-5xl font-bold text-main-foreground">
              {t('home.HowItWorks.title')}
            </h2>
          </div>
        </div>

        {/* Pasos */}
        <div className="grid md:grid-cols-4 gap-8">
          {steps.map(({ title, desc, Icon }, i) => (
            <div key={i}>
              <div className="bg-black text-white border-4 border-border shadow-brutal-2xl hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all duration-300 p-6 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <Icon className="h-6 w-6 text-white" />
                  <h3 className="text-2xl font-bold text-white">{title}</h3>
                </div>
                <p className="font-medium text-white/90">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-10 flex justify-center">
          <a
            href="#descargar-app"
            className="bg-main text-main-foreground px-8 py-3 border-2 border-border shadow-brutal hover:shadow-brutal-lg transition-all font-bold"
          >
            {t('home.HowItWorks.downloadApp')}
          </a>
        </div>
      </div>
    </section>
  );
}
