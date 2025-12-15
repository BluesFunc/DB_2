export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const API_ENDPOINTS = {
  // Auth
  REGISTER: '/v1/auth/register',
  LOGIN: '/v1/auth/login',
  REFRESH: '/v1/auth/refresh',
  GET_ME: '/v1/auth/me',
  
  // Bookings
  CREATE_BOOKING: '/v1/bookings',
  GET_BOOKING: (id: number) => `/v1/bookings/${id}`,
  LIST_BOOKINGS: '/v1/bookings',
  UPDATE_BOOKING: (id: number) => `/v1/bookings/${id}`,
  SEARCH_TRIPS: '/v1/bookings/search',
  
  // Trips
  GET_TRIP: (id: number) => `/v1/trips/${id}`,
  GET_TRIP_FARES: (id: number) => `/v1/trips/${id}/fares`,
  
  // Passengers
  CREATE_PASSENGER: '/v1/bookings/passengers',
  GET_PASSENGERS: '/v1/bookings/passengers',
  
  // Payments
  CREATE_PAYMENT: (bookingId: number) => `/v1/bookings/${bookingId}/payments`,
  CONFIRM_PAYMENT: (bookingId: number, paymentId: number) => `/v1/bookings/${bookingId}/payments/${paymentId}/confirm`,
  
  // Tickets
  CREATE_TICKET: (bookingId: number) => `/v1/bookings/${bookingId}/tickets`,
  GET_TICKETS: (bookingId: number) => `/v1/bookings/${bookingId}/tickets`,
}
