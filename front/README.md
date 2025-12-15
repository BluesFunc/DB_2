# VoyaGo - Frontend

A modern React/Next.js application for booking travel tickets (flights, trains, buses).

## Features

- 🔐 User authentication (Sign up/Sign in)
- 🔍 Advanced search for trips
- 🎫 Booking management
- 👤 User profiles with trip history
- 💳 Payment integration
- 🎨 Modern UI with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4
- **HTTP Client**: Axios with token interceptors
- **Routing**: React Router DOM

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/              # Next.js App Router pages
│   ├── layout.tsx    # Root layout with Header
│   ├── page.tsx      # Home page
│   ├── login/        # Login page
│   ├── register/     # Registration page
│   └── profile/      # User profile page
├── components/       # Reusable components
│   ├── Header.tsx    # Navigation header
│   └── SearchForm.tsx # Trip search form
├── lib/
│   ├── api.ts        # API endpoint definitions
│   └── apiClient.ts  # Axios instance with interceptors
└── app/
    └── globals.css   # Global styles & Tailwind
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## API Integration

The frontend communicates with the VoyaGo backend API at `/api` endpoint.

### Authentication Flow

1. User registers or logs in
2. Backend returns JWT token and user info
3. Token stored in localStorage
4. Axios interceptor automatically adds Bearer token to requests
5. If token expires (401), client refreshes and retries

### Key Endpoints

- `POST /v1/auth/register` - User registration
- `POST /v1/auth/login` - User login
- `GET /v1/bookings` - List user bookings
- `POST /v1/bookings` - Create new booking
- `POST /v1/passengers` - Add passenger profile
- `POST /v1/payments` - Process payment

## Features Implementation

### Pages

- **Home** (`/`) - Search form with trip finder
- **Login** (`/login`) - User sign in
- **Register** (`/register`) - New user registration
- **Profile** (`/profile`) - User trips and passengers

### Components

- **Header** - Navigation with auth state
- **SearchForm** - Trip search with date picker

## Future Enhancements

- [ ] Search results page with trip cards
- [ ] Booking details and confirmation
- [ ] Payment processing page
- [ ] Passenger management
- [ ] Trip reviews and ratings
- [ ] Booking history and receipts
- [ ] Mobile app optimization

## Support

For issues or questions, please contact the development team.

## License

MIT
