// components/Navbar.tsx
'use client';

import Image from "next/image";
import LanguageSelector from "@/components/LanguageSelector";
import { useState } from "react";
import { HiMenu, HiX } from "react-icons/hi";
import { useTranslation } from 'react-i18next';

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { t } = useTranslation();
  return (
    <header className="sticky top-0 z-50 bg-white border-b-4 border-black shadow-brutal-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Marca */}
          <div className="flex items-center space-x-2">
            <Image
              src="/logo.png"
              alt={t('navbar.yuancity')}
              width={48}
              height={48}
              className="h-12 w-12"
              priority
            />
            <span className="text-xl font-bold text-black">
              {t('navbar.yuancity')}
            </span>
          </div>
          {/* Navegación Desktop */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#about" className="text-black hover:text-main font-medium">
              {t('navbar.whoWeAre')}
            </a>
            <a href="#como-funciona" className="text-black hover:text-main font-medium">
              {t('navbar.howItWorks')}
            </a>
            <a href="#join" className="text-black hover:text-main font-medium">
              {t('navbar.joinUs')}
            </a>

            {/* CTA descarga app */}
            <a
              href="#descargar-app"
              className="bg-main text-main-foreground px-6 py-2 border-2 border-black shadow-brutal hover:shadow-brutal-lg transition-all font-bold"
            >
              {t('navbar.downloadApp')}
            </a>

            {/* Selector de idioma */}
            <LanguageSelector />
          </nav>

          {/* Navegación Móvil */}
          <div className="flex md:hidden items-center space-x-4">
            <LanguageSelector />
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-black hover:text-main p-2"
              aria-label="Menú"
            >
              {isMobileMenuOpen ? <HiX className="h-6 w-6" /> : <HiMenu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Menú móvil desplegable */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t-2 border-black py-4">
            <nav className="flex flex-col space-y-4">
              <a
                href="#about"
                className="text-black hover:text-main font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {t('navbar.whoWeAre')}
              </a>
              <a
                href="#como-funciona"
                className="text-black hover:text-main font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {t('navbar.howItWorks')}
              </a>
              <a
                href="#join"
                className="text-black hover:text-main font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {t('navbar.joinUs')}
              </a>
              <a
                href="#descargar-app"
                className="bg-main text-main-foreground px-6 py-2 border-2 border-black shadow-brutal hover:shadow-brutal-lg transition-all font-bold text-center"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {t('navbar.downloadApp')}
              </a>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
