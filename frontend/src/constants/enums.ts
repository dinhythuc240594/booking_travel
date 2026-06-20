export enum UserRole {
  ADMIN = "admin",
  USER = "user",
  CUSTOMER = "customer",
}

export enum BookingStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
}

export enum PaymentStatus {
  PENDING = "pending",
  SUCCESSFUL = "successful",
  FAILED = "failed",
  REFUNDED = "refunded",
}
