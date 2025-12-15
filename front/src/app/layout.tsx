import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Header from '@/components/Header'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'VoyaGo - Book Your Journey',
  description: 'Discover and book your next travel adventure with VoyaGo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        <footer className="bg-gray-800 text-white py-8 mt-12">
          <div className="container-main text-center">
            <p>&copy; 2024 VoyaGo. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
