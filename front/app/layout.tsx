import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { I18nProvider } from '@/components/I18nProvider'
import { SITE_BASE_URL } from '@/lib/mobileApp'

const geist = Geist({ subsets: ['latin'], variable: '--font-geist' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
  metadataBase: new URL(SITE_BASE_URL),
  title: 'YuanCity - Venta de Productos de China',
  description: 'Publica y vende tus productos de China con YuanCity.',
  alternates: {
    canonical: '/',
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: { icon: '/logo.png' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={`${geist.variable} ${geistMono.variable} font-sans antialiased`}>
        <I18nProvider>
          {children}
        </I18nProvider>
      </body>
    </html>
  )
}
