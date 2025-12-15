'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/apiClient'
import { API_ENDPOINTS } from '@/lib/api'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    setLoading(true)

    try {
      // Step 1: Register and get user data
      const registerResponse = await apiClient.post(API_ENDPOINTS.REGISTER, {
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
      })

      // After registration, user is created but not logged in
      // We need to log in to get tokens
      const loginResponse = await apiClient.post(API_ENDPOINTS.LOGIN, {
        email: formData.email,
        password: formData.password,
      })

      const { access_token, refresh_token } = loginResponse.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }

      // Step 2: Fetch user profile
      const userResponse = await apiClient.get(API_ENDPOINTS.GET_ME)
      const user = userResponse.data

      // Store user info
      localStorage.setItem('user_id', user.id)
      localStorage.setItem('user_name', user.full_name || user.email)
      localStorage.setItem('user_email', user.email)

      // Redirect to home
      router.push('/')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Registration failed. Please try again.'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="py-12">
      <div className="container-main max-w-md">
        <div className="card">
          <h1 className="text-3xl font-bold mb-2 text-gray-900">Create Account</h1>
          <p className="text-gray-600 mb-6">Join VoyaGo and start booking your trips</p>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="John Doe"
                className="input-field"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input-field"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="input-field"
                required
              />
              <p className="text-xs text-gray-500 mt-1">At least 8 characters</p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="input-field"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 mb-4"
            >
              {loading ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <p className="text-center text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
