'use client';

import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { IoGlobeOutline, IoChevronDown } from 'react-icons/io5';

const LanguageSelector = () => {
    const { i18n, t } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const languages = [
        { code: 'en', name: t('languages.english'), flag: '🇺🇸' },
        { code: 'es', name: t('languages.spanish'), flag: '🇪🇸' },
        { code: 'it', name: t('languages.italian'), flag: '🇮🇹' },
        { code: 'pt', name: t('languages.portuguese'), flag: '🇵🇹' },
        { code: 'zh', name: t('languages.chinese'), flag: '🇨🇳' },
    ];

    const currentLanguage = languages.find((lang) => lang.code === i18n.language) || languages[0];

    const changeLanguage = (langCode: string) => {
        i18n.changeLanguage(langCode);
        setIsOpen(false);
        // Dispatch custom event to notify other components about language change
        window.dispatchEvent(new Event('languageChanged'));
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-2 px-3 py-2 bg-white border-2 border-black shadow-brutal hover:shadow-brutal-lg transition-all text-black font-medium"
                aria-label={t('languages.selectLanguage')}
            >
                <IoGlobeOutline className="h-5 w-5" />
                <span className="hidden sm:inline text-sm">{currentLanguage.flag}</span>
                <span className="hidden md:inline text-sm">{currentLanguage.name}</span>
                <IoChevronDown
                    className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border-2 border-black shadow-brutal-lg z-50">
                    <div className="py-1">
                        {languages.map((language) => (
                            <button
                                key={language.code}
                                onClick={() => changeLanguage(language.code)}
                                className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors flex items-center space-x-3 ${
                                    i18n.language === language.code
                                        ? 'text-main font-bold bg-gray-50'
                                        : 'text-black font-medium'
                                }`}
                            >
                                <span className="text-lg">{language.flag}</span>
                                <span>{language.name}</span>
                                {i18n.language === language.code && (
                                    <span className="ml-auto text-main font-bold">✓</span>
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LanguageSelector;
