import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { Booking } from "@/types/booking";
import { BookingStatus, PaymentStatus } from "@/constants/enums";

interface BookingState {
  bookings: Booking[];
  addBooking: (booking: Booking) => void;
  cancelBooking: (bookingId: string) => void;
}

export const useBookingStore = create<BookingState>()(
  persist(
    (set) => ({
      bookings: [],
      
      addBooking: (newBooking) =>
        set((state) => ({
          bookings: [newBooking, ...state.bookings],
        })),

      cancelBooking: (bookingId) =>
        set((state) => ({
          bookings: state.bookings.map((booking) =>
            booking.id === bookingId
              ? { 
                  ...booking, 
                  status: BookingStatus.CANCELLED, 
                  paymentStatus: PaymentStatus.FAILED 
                }
              : booking
          ),
        })),
    }),
    {
      name: "booking-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
