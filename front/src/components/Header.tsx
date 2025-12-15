'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function Header() {
  const router = useRouter()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userName, setUserName] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUserName = localStorage.getItem('user_name')
    setIsLoggedIn(!!token)
    setUserName(storedUserName || '')
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_id')
    setIsLoggedIn(false)
    router.push('/')
  }

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="container-main">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="text-2xl font-bold text-blue-600">VoyaGo</div>
            <span className="text-sm text-gray-600 hidden sm:inline">Travel Booking</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link
              href="/"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
            >
              Home
            </Link>

            {isLoggedIn && (
              <Link
                href="/profile"
                className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                My Trips
              </Link>
            )}

            {/* Auth Buttons */}
            <div className="flex items-center gap-3">
              {isLoggedIn ? (
                <>
                  <span className="text-gray-700 font-medium">{userName}</span>
                  <button
                    onClick={handleLogout}
                    className="btn-secondary text-sm"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login">
                    <button className="btn-secondary text-sm">
                      Sign In
                    </button>
                  </Link>
                  <Link href="/register">
                    <button className="btn-primary text-sm">
                      Sign Up
                    </button>
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  )
}
