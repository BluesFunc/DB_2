'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/apiClient'
import { API_ENDPOINTS } from '@/lib/api'
import Link from 'next/link'

interface Booking {
  id: number
  user_id: number
  status: string
  created_at: string
  updated_at: string
  hold_expires_at?: string
  tickets?: Array<any>
  payments?: Array<any>
}

export default function ProfilePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [bookings, setBookings] = useState<Booking[]>([])
  const [userName, setUserName] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUserName = localStorage.getItem('user_name')

    if (!token) {
      router.push('/login')
      return
    }

    setUserName(storedUserName || '')
    fetchBookings()
  }, [router])

  const fetchBookings = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get(API_ENDPOINTS.LIST_BOOKINGS)
      // Backend returns raw array, not wrapped in { bookings: [...] }
      const bookingsData = Array.isArray(response.data) ? response.data : response.data.bookings || []
      setBookings(bookingsData)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load bookings'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="py-12">
        <div className="container-main text-center">
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="py-12">
      <div className="container-main">
        {/* Profile Header */}
        <div className="card mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
          <p className="text-gray-600">Welcome, {userName}</p>
        </div>

        {/* Tabs */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">My Trips</h2>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {bookings.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">You haven't booked any trips yet</p>
              <Link href="/">
                <button className="btn-primary">
                  Search for Trips
                </button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {bookings.map((booking) => (
                <div key={booking.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Booking ID</p>
                      <p className="font-mono text-gray-900">#{booking.id}</p>
                    </div>
                    <div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        booking.status === 'CONFIRMED'
                          ? 'bg-green-100 text-green-800'
                          : booking.status === 'TENTATIVE'
                          ? 'bg-yellow-100 text-yellow-800'
                          : booking.status === 'CANCELLED'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {booking.status}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-600">Tickets</p>
                      <p className="text-lg font-bold text-gray-900">
                        {booking.tickets?.length || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Booked on</p>
                      <p className="text-gray-900">
                        {new Date(booking.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {booking.hold_expires_at && (
                    <div className="mt-3 text-xs text-gray-500">
                      Hold expires: {new Date(booking.hold_expires_at).toLocaleString()}
                    </div>
                  )}

                  <Link href={`/booking/${booking.id}`}>
                    <button className="btn-outline text-sm mt-4 w-full">
                      View Details
                    </button>
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Passengers Section */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">My Passengers</h2>
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Manage passenger profiles for quick bookings</p>
            <button className="btn-primary">
              Add Passenger
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
