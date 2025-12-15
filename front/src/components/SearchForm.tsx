'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/apiClient'
import { API_ENDPOINTS } from '@/lib/api'

export default function SearchForm() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    departDate: '',
    returnDate: '',
    passengers: 1,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!formData.origin || !formData.destination || !formData.departDate) {
      setError('Please fill in all required fields')
      return
    }

    setLoading(true)

    try {
      // Store search params in localStorage for results page
      localStorage.setItem('lastSearch', JSON.stringify(formData))

      // Try to search via backend API
      try {
        const searchResponse = await apiClient.post(API_ENDPOINTS.SEARCH_TRIPS, {
          origin: formData.origin,
          destination: formData.destination,
          departure_date: formData.departDate,
          return_date: formData.returnDate || null,
          passengers: formData.passengers,
        })
        
        // Store results and navigate
        localStorage.setItem('searchResults', JSON.stringify(searchResponse.data))
      } catch (apiError) {
        console.warn('Search API call failed, using local navigation:', apiError)
        // Fallback to navigation with search params
      }

      // Navigate to search results page with params
      const params = new URLSearchParams({
        origin: formData.origin,
        destination: formData.destination,
        departDate: formData.departDate,
        ...(formData.returnDate && { returnDate: formData.returnDate }),
        passengers: formData.passengers.toString(),
      })

      router.push(`/search?${params.toString()}`)
    } catch (error) {
      console.error('Search error:', error)
      setError('An error occurred during search')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSearch} className="card max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Find Your Journey</h2>

      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        {/* Origin */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            From
          </label>
          <input
            type="text"
            name="origin"
            value={formData.origin}
            onChange={handleChange}
            placeholder="Departure city"
            className="input-field"
            required
          />
        </div>

        {/* Destination */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            To
          </label>
          <input
            type="text"
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            placeholder="Destination city"
            className="input-field"
            required
          />
        </div>

        {/* Depart Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Depart
          </label>
          <input
            type="date"
            name="departDate"
            value={formData.departDate}
            onChange={handleChange}
            className="input-field"
            required
          />
        </div>

        {/* Return Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Return
          </label>
          <input
            type="date"
            name="returnDate"
            value={formData.returnDate}
            onChange={handleChange}
            className="input-field"
          />
        </div>

        {/* Passengers */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Passengers
          </label>
          <select
            name="passengers"
            value={formData.passengers}
            onChange={handleChange}
            className="input-field"
          >
            {[1, 2, 3, 4, 5, 6].map(num => (
              <option key={num} value={num}>
                {num} {num === 1 ? 'Passenger' : 'Passengers'}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full btn-primary text-lg font-semibold disabled:opacity-50"
      >
        {loading ? 'Searching...' : 'Search Trips'}
      </button>
    </form>
  )
}
