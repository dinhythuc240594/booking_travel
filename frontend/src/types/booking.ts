import { BookingStatus, PaymentStatus } from "@/constants/enums";

export interface Booking {
  id: string;
  tourId: string;
  tourTitle: string;
  tourImage: string;
  userId: string;
  userName: string;
  departureDate: string;
  adults: number;
  children: number;
  totalPrice: number;
  status: BookingStatus;
  paymentStatus: PaymentStatus;
  createdAt: string;
}
