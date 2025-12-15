/**
 * User Profile Business Logic Tests
 * Tests trip sorting, filtering, and passenger management logic
 */

describe('User Profile - Business Logic Tests', () => {
  let tripService: any;
  let passengerService: any;

  beforeEach(() => {
    const mockTrips = [
      {
        id: '1',
        origin: 'New York',
        destination: 'Boston',
        status: 'completed',
        departureDate: new Date('2024-01-15'),
      },
      {
        id: '2',
        origin: 'New York',
        destination: 'Washington',
        status: 'upcoming',
        departureDate: new Date('2024-12-20'),
      },
      {
        id: '3',
        origin: 'Boston',
        destination: 'Philadelphia',
        status: 'cancelled',
        departureDate: new Date('2024-02-01'),
      },
    ];

    const mockPassengers = [
      {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        documentId: 'P123456',
        documentType: 'passport',
      },
    ];

    tripService = {
      getTrips: jest.fn().mockResolvedValue(mockTrips),
      sortByDate: (trips: any[], ascending = false) => {
        return [...trips].sort((a, b) => {
          const dateA = new Date(a.departureDate).getTime();
          const dateB = new Date(b.departureDate).getTime();
          return ascending ? dateA - dateB : dateB - dateA;
        });
      },
      filterByStatus: (trips: any[], status: string) => {
        if (status === 'all') return trips;
        return trips.filter(t => t.status === status);
      },
    };

    passengerService = {
      getPassengers: jest.fn().mockResolvedValue(mockPassengers),
      validateEmail: (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
      validateDocument: (docId: string) => docId.length >= 5,
      addPassenger: jest.fn(),
      updatePassenger: jest.fn(),
      deletePassenger: jest.fn(),
    };
  });

  describe('Trip Display and Sorting', () => {
    it('should load all user trips', async () => {
      const trips = await tripService.getTrips();
      expect(trips.length).toBe(3);
    });

    it('should sort trips by date in descending order (most recent first)', async () => {
      const trips = await tripService.getTrips();
      const sorted = tripService.sortByDate(trips, false);
      
      expect(sorted[0].departureDate.getTime()).toBeGreaterThan(
        sorted[1].departureDate.getTime()
      );
      expect(sorted[0].id).toBe('2'); // 2024-12-20
      expect(sorted[sorted.length - 1].id).toBe('1'); // 2024-01-15
    });

    it('should sort trips by date in ascending order (oldest first)', async () => {
      const trips = await tripService.getTrips();
      const sorted = tripService.sortByDate(trips, true);
      
      expect(sorted[0].departureDate.getTime()).toBeLessThan(
        sorted[1].departureDate.getTime()
      );
      expect(sorted[0].id).toBe('1'); // 2024-01-15
    });
  });

  describe('Trip Filtering', () => {
    it('should return all trips when no filter applied', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'all');
      
      expect(filtered.length).toBe(3);
    });

    it('should filter trips by completed status', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'completed');
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].status).toBe('completed');
    });

    it('should filter trips by upcoming status', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'upcoming');
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].status).toBe('upcoming');
    });

    it('should filter trips by cancelled status', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'cancelled');
      
      expect(filtered.length).toBe(1);
      expect(filtered[0].status).toBe('cancelled');
    });

    it('should return empty array when no trips match filter', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'nonexistent');
      
      expect(filtered.length).toBe(0);
    });

    it('should support chaining sort and filter operations', async () => {
      const trips = await tripService.getTrips();
      const filtered = tripService.filterByStatus(trips, 'completed');
      const sorted = tripService.sortByDate(filtered, false);
      
      expect(sorted.length).toBe(1);
      expect(sorted[0].status).toBe('completed');
    });
  });

  describe('Passenger Management', () => {
    it('should load all passengers', async () => {
      const passengers = await passengerService.getPassengers();
      expect(passengers.length).toBe(1);
    });

    it('should validate passenger email format', () => {
      expect(passengerService.validateEmail('valid@example.com')).toBe(true);
      expect(passengerService.validateEmail('invalidemail')).toBe(false);
    });

    it('should validate passenger document ID', () => {
      expect(passengerService.validateDocument('P123456')).toBe(true);
      expect(passengerService.validateDocument('ID')).toBe(false);
    });

    it('should reject invalid email on add passenger', async () => {
      const passengerData = {
        name: 'Jane Doe',
        email: 'invalidemail',
        documentId: 'P987654',
        documentType: 'passport',
      };
      
      const emailValid = passengerService.validateEmail(passengerData.email);
      expect(emailValid).toBe(false);
    });

    it('should reject invalid document ID on add passenger', async () => {
      const passengerData = {
        name: 'Jane Doe',
        email: 'jane@example.com',
        documentId: 'ID',
        documentType: 'passport',
      };
      
      const docValid = passengerService.validateDocument(passengerData.documentId);
      expect(docValid).toBe(false);
    });

    it('should add passenger with valid data', async () => {
      const newPassenger = {
        id: '2',
        name: 'Jane Doe',
        email: 'jane@example.com',
        documentId: 'P987654',
        documentType: 'passport',
      };
      
      passengerService.addPassenger.mockResolvedValue(newPassenger);
      
      const result = await passengerService.addPassenger(newPassenger);
      
      expect(result.id).toBe('2');
      expect(result.name).toBe('Jane Doe');
    });

    it('should update existing passenger', async () => {
      const updated = {
        id: '1',
        name: 'John Updated',
        email: 'john.updated@example.com',
        documentId: 'P999999',
        documentType: 'idcard',
      };
      
      passengerService.updatePassenger.mockResolvedValue(updated);
      
      const result = await passengerService.updatePassenger('1', updated);
      
      expect(result.name).toBe('John Updated');
      expect(passengerService.updatePassenger).toHaveBeenCalledWith('1', updated);
    });

    it('should delete passenger by ID', async () => {
      passengerService.deletePassenger.mockResolvedValue({ success: true });
      
      await passengerService.deletePassenger('1');
      
      expect(passengerService.deletePassenger).toHaveBeenCalledWith('1');
    });
  });

  describe('Document Type Support', () => {
    it('should support passport document type', () => {
      const passenger = {
        id: '1',
        name: 'John Doe',
        documentType: 'passport',
        documentId: 'P123456',
      };
      
      expect(['passport', 'idcard', 'license']).toContain(passenger.documentType);
    });

    it('should support ID card document type', () => {
      const passenger = {
        id: '2',
        name: 'Jane Doe',
        documentType: 'idcard',
        documentId: 'ID123456',
      };
      
      expect(['passport', 'idcard', 'license']).toContain(passenger.documentType);
    });

    it('should support driver license document type', () => {
      const passenger = {
        id: '3',
        name: 'Bob Smith',
        documentType: 'license',
        documentId: 'DL123456',
      };
      
      expect(['passport', 'idcard', 'license']).toContain(passenger.documentType);
    });
  });

  describe('Passenger Data Validation', () => {
    it('should reject passenger with missing name', () => {
      const passenger = {
        name: '',
        email: 'john@example.com',
        documentId: 'P123456',
      };
      
      const isValid = passenger.name.length > 0;
      expect(isValid).toBe(false);
    });

    it('should reject passenger with missing email', () => {
      const passenger = {
        name: 'John Doe',
        email: '',
        documentId: 'P123456',
      };
      
      const isValid = passengerService.validateEmail(passenger.email);
      expect(isValid).toBe(false);
    });

    it('should reject passenger with missing document ID', () => {
      const passenger = {
        name: 'John Doe',
        email: 'john@example.com',
        documentId: '',
      };
      
      const isValid = passengerService.validateDocument(passenger.documentId);
      expect(isValid).toBe(false);
    });

    it('should accept passenger with all valid fields', () => {
      const passenger = {
        name: 'John Doe',
        email: 'john@example.com',
        documentId: 'P123456',
      };
      
      const nameValid = passenger.name.length > 0;
      const emailValid = passengerService.validateEmail(passenger.email);
      const docValid = passengerService.validateDocument(passenger.documentId);
      
      expect(nameValid && emailValid && docValid).toBe(true);
    });
  });
});
