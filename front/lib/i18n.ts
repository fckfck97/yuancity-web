import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import en from '../locales/en.json';
import es from '../locales/es.json';
import it from '../locales/it.json';
import pt from '../locales/pt.json';
import zh from '../locales/zh.json';
const resources = {
  en: { translation: en },
  es: { translation: es },
  it: { translation: it },
  pt: { translation: pt },
  zh: { translation: zh  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    detection: {
      // Allow the mobile app to force a language using ?lng=es on deep links
      order: ['querystring', 'localStorage', 'navigator', 'htmlTag'],
      lookupQuerystring: 'lng',
      caches: ['localStorage'],
    },
  });

export default i18n;
