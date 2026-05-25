import type { Metadata } from 'next'
import { Poppins } from 'next/font/google'
import './globals.css'

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-sans',
})

export const metadata: Metadata = {
  title: 'AutoGeo - Automatización Documental Geotécnica',
  description:
    'Plataforma SaaS para automatización de documentos geotécnicos con inteligencia artificial',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang='es'>
      <body className={poppins.variable}>
        {children}
      </body>
    </html>
  )
}
