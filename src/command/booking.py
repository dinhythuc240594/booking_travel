from command.component import DatabaseCommand
from database import (
    TourRejection,
    Setting,
    Bookings, 
    Payment, 
    BookingStatusEnum, 
    User, 
    PaymentStatusEnum,
    TourStatus,
    NewsletterSubscription,
    Tour)
from datetime import datetime, timedelta


class CreateBookingCommand(DatabaseCommand):

    """Lệnh tạo Booking (Hotel hoặc Tour) cho Khách hàng"""
    def __init__(self, user_id: int, booking_type, reference_id: int, total_price: float, check_in_date: datetime = None, check_out_date: datetime = None):
        self.user_id = user_id
        self.booking_type = booking_type
        self.reference_id = reference_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_price = total_price
        self.booking_record = None

    def execute(self, session) -> None:
        self.booking_record = Bookings(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            check_in_date=self.check_in_date,
            check_out_date=self.check_out_date,
            total_price=self.total_price,
            booking_status=BookingStatusEnum.pending
        )
        session.add(self.booking_record)
        session.flush()

    def undo(self, session) -> None:
        if self.booking_record:
            self.booking_record.booking_status = BookingStatusEnum.cancelled