'use client';

import { useEffect, useState } from 'react';
import DeepLinkLauncher from '@/components/DeepLinkLauncher';
import { useTranslation } from 'react-i18next';
import { FaApple, FaFacebookF, FaGooglePlay, FaInstagram, FaTimes, FaWhatsapp } from 'react-icons/fa';

const APP_STORE_URL = 'https://apps.apple.com/us/app/mikiguiki/id6748412273';
const PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=com.ovalcampus.yuancity';
const HOME_DEEP_LINK = 'mikiguiki://home';
const WHATSAPP_NUMBER = '573116617105';
const WHATSAPP_MESSAGE = encodeURIComponent(
    'Descarga la app de Yuancity y ve contenido exclusivo https://yuancity.com',
);

type SocialPromoModalProps = {
    onClose: () => void;
};

export function SocialPromoModal({ onClose }: SocialPromoModalProps) {
    const { t } = useTranslation();
    const [autolaunch, setAutolaunch] = useState(false);

    useEffect(() => {
        const timer = window.setTimeout(() => setAutolaunch(true), 800);
        return () => window.clearTimeout(timer);
    }, []);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
                aria-hidden="true"
            />
            <div className="relative w-full max-w-md bg-background border-4 border-border shadow-brutal-3xl overflow-hidden rotate-1 hover:shadow-[20px_20px_0px_0px_var(--color-border)] transition-all">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center bg-black text-white border-2 border-border hover:bg-main hover:shadow-brutal transition-all z-10"
                    aria-label={t('socialPromo.close')}
                >
                    <FaTimes className="w-5 h-5" />
                </button>
                
                <div className="p-8 space-y-6 -rotate-1">
                    {/* Header */}
                    <div className="text-center space-y-4">
                        <div className="bg-main border-2 border-border shadow-brutal inline-block px-4 py-2 -rotate-1">
                            <p className="text-xs uppercase font-black text-white tracking-wider">
                                {t('socialPromo.subtitle')}
                            </p>
                        </div>
                        <h3 className="text-3xl md:text-4xl font-black text-foreground">{t('socialPromo.title')}</h3>
                        <p className="text-base font-semibold text-foreground/80">{t('socialPromo.storeCta')}</p>
                    </div>

                    {/* Deep Link Launcher */}
                    <div className="space-y-3">
                        <DeepLinkLauncher
                            deepLink={HOME_DEEP_LINK}
                            appStoreUrl={APP_STORE_URL}
                            playStoreUrl={PLAY_STORE_URL}
                            autolaunch={autolaunch}
                        />
                    </div>

                    {/* App Store Buttons */}
                    <div className="flex items-center gap-3">
                        <a
                            href={APP_STORE_URL}
                            target="_blank"
                            rel="noreferrer"
                            className="flex-1 flex items-center justify-center gap-2 bg-black text-white border-4 border-border py-3 font-black shadow-brutal hover:shadow-brutal-xl hover:bg-main transition-all rotate-1"
                        >
                            <FaApple className="w-5 h-5" />
                            App Store
                        </a>
                        <a
                            href={PLAY_STORE_URL}
                            target="_blank"
                            rel="noreferrer"
                            className="flex-1 flex items-center justify-center gap-2 bg-black text-white border-4 border-border py-3 font-black shadow-brutal hover:shadow-brutal-xl hover:bg-main transition-all -rotate-1"
                        >
                            <FaGooglePlay className="w-5 h-5" />
                            Google Play
                        </a>
                    </div>

                    {/* Social Media Section */}
                    <div className="bg-white border-4 border-border shadow-brutal-2xl p-6 -rotate-1 hover:shadow-[15px_15px_0px_0px_var(--color-border)] transition-all">
                        <div className="rotate-1">
                            <p className="text-center text-sm font-black text-foreground mb-4 uppercase tracking-wide">
                                {t('socialPromo.socialTitle')}
                            </p>
                            <div className="flex justify-center gap-4">
                                <a
                                    href="https://www.facebook.com/mikiguiki"
                                    target="_blank"
                                    rel="noreferrer"
                                    className="w-12 h-12 flex items-center justify-center bg-black text-white border-2 border-border shadow-brutal hover:shadow-brutal-lg hover:bg-main transition-all"
                                    aria-label="Facebook"
                                >
                                    <FaFacebookF className="w-5 h-5" />
                                </a>
                                <a
                                    href="https://www.instagram.com/mikiguiki/"
                                    target="_blank"
                                    rel="noreferrer"
                                    className="w-12 h-12 flex items-center justify-center bg-black text-white border-2 border-border shadow-brutal hover:shadow-brutal-lg hover:bg-main transition-all"
                                    aria-label="Instagram"
                                >
                                    <FaInstagram className="w-5 h-5" />
                                </a>
                                <a
                                    href={`https://wa.me/${WHATSAPP_NUMBER}?text=${WHATSAPP_MESSAGE}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="w-12 h-12 flex items-center justify-center bg-black text-white border-2 border-border shadow-brutal hover:shadow-brutal-lg hover:bg-main transition-all"
                                    aria-label="WhatsApp"
                                >
                                    <FaWhatsapp className="w-5 h-5" />
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* Close Button */}
                    <div className="flex justify-center">
                        <button
                            onClick={onClose}
                            className="px-6 py-3 bg-white border-2 border-border font-black text-foreground hover:bg-black hover:text-white shadow-brutal hover:shadow-brutal-lg transition-all"
                        >
                            {t('socialPromo.close')}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
