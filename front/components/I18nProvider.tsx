'use client';

import { useEffect, useState } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../lib/i18n';

interface I18nProviderProps {
    children: React.ReactNode;
}

export const I18nProvider = ({ children }: I18nProviderProps) => {
    const [isInitialized, setIsInitialized] = useState(false);

    useEffect(() => {
        // Wait for i18n to be initialized
        if (i18n.isInitialized) {
            setIsInitialized(true);
        } else {
            i18n.on('initialized', () => {
                setIsInitialized(true);
            });
        }

        return () => {
            i18n.off('initialized');
        };
    }, []);

    if (!isInitialized) {
        return <div>Loading...</div>;
    }

    return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
};
