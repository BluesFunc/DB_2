import SearchForm from '@/components/SearchForm'

export default function Home() {
  return (
    <div className="py-12">
      <div className="container-main">
        {/* Hero Section */}
        <div className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Explore the World with <span className="text-blue-600">VoyaGo</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Book flights, trains, and buses in seconds. Get the best deals on your favorite routes.
          </p>
        </div>

        {/* Search Form */}
        <div className="mb-16">
          <SearchForm />
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          <div className="card text-center">
            <div className="text-4xl mb-4">✈️</div>
            <h3 className="text-xl font-bold mb-2">Multiple Transport Modes</h3>
            <p className="text-gray-600">
              Choose from flights, trains, buses, and more. All in one place.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">💳</div>
            <h3 className="text-xl font-bold mb-2">Secure Payments</h3>
            <p className="text-gray-600">
              Book with confidence. Your payment information is always secure.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-4">🎟️</div>
            <h3 className="text-xl font-bold mb-2">Instant Tickets</h3>
            <p className="text-gray-600">
              Get your tickets instantly. Save them on your phone or print them.
            </p>
          </div>
        </div>

        {/* Popular Routes */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold mb-8">Popular Routes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { from: 'New York', to: 'Boston' },
              { from: 'London', to: 'Paris' },
              { from: 'Tokyo', to: 'Osaka' },
              { from: 'Berlin', to: 'Munich' },
            ].map((route, idx) => (
              <div key={idx} className="card hover:shadow-lg transition-shadow">
                <p className="text-sm text-gray-600">Popular Route</p>
                <p className="text-lg font-bold text-gray-900">
                  {route.from} → {route.to}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
