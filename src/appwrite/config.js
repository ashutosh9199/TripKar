export class Service {
    async createBooking(hotelId, userId, bookingDate) {
        try {
            const response = await fetch('http://localhost:5000/api/bookings/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hotelId, userId, bookingDate })
            });
            return await response.json();
        } catch(error) {
            console.log("Create Booking error: ", error)
        }
    }

    async deleteBooking(bookingId) {
        try {
            const response = await fetch(`http://localhost:5000/api/bookings/${bookingId}`, {
                method: 'DELETE'
            });
            return response.ok;
        } catch (error) {
            console.log("Delete Document Error ", error)
            return false
        }
    }

    async getBookings(queries) {
        try {
            // Simplified for microservice adaptation
            const user = JSON.parse(localStorage.getItem('userSession'));
            if (!user) return { documents: [] };
            
            const response = await fetch(`http://localhost:5000/api/bookings/my-bookings/${user.id}`);
            const data = await response.json();
            return { documents: data };
        } catch (error) {
            console.log("Get all Bookings error: ", error)
        }
    }

    async getHotels(queries) {
        try {
            const response = await fetch('http://localhost:5000/api/search/trips');
            const data = await response.json();
            // Appwrite expected format { documents: [...] }
            return { documents: data.map(t => ({ $id: t.id, name: t.destination, price: t.price })) };
        } catch(error) {
            console.log("Get hotels error", error)
        }
    }

    async getHotel(hotelId) {
        try {
            const response = await fetch('http://localhost:5000/api/search/trips');
            const data = await response.json();
            const hotel = data.find(t => t.id === hotelId);
            return hotel ? { $id: hotel.id, name: hotel.destination, price: hotel.price } : null;
        } catch(error) {
            console.log("Get hotel error", error)
        }
    }
}

const service = new Service();
export default service;